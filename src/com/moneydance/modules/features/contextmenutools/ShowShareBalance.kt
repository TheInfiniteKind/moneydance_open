package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.AccountBook
import com.infinitekind.moneydance.model.AccountUtil
import com.infinitekind.moneydance.model.AcctFilter
import com.infinitekind.moneydance.model.CurrencySplit
import com.infinitekind.moneydance.model.InvestFields
import com.infinitekind.moneydance.model.NetWorthCalculator
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.ReportSpec
import com.infinitekind.moneydance.model.TotalAmount
import com.infinitekind.util.DateUtil
import com.infinitekind.util.labelify
import com.infinitekind.util.nullIfBlank
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.reporttool.CellStyle
import com.moneydance.apps.md.view.gui.reporttool.Report2
import com.moneydance.apps.md.view.gui.reporttool.ShowReportWindow
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.TextViewerDialog
import com.moneydance.util.UiUtil
import java.awt.event.ActionListener
import java.math.BigDecimal
import javax.swing.Action

@Suppress("PrivatePropertyName")

/**
 * Adds a context-menu action that shows the share balance of the selected investment transaction's security.
 *
 * Rules:
 * - offered only when exactly one transaction is selected and it has a security (investment and security registers);
 * - building the menu only reads the security account's current balance (held in memory); the balances are worked out only when the menu item is clicked;
 * - the balances come from ONE call to NetWorthCalculator.computeAccountBalancesByAsOfDates (MD2027, by reflection, as the compile
 *   jar predates it); older builds use AccountUtil.getBalancesAsOfDates once per holding account;
 * - the report window is used when ShowReportWindow can show a report with no report type; older builds get the text popup;
 * - the balance calculation runs on its own thread; the windows are built and shown back on the EDT;
 * - balances are end of day, in the shares of that date; "in today's terms" applies only the later splits;
 * - a stock split dated on the transaction's day counts as already applied (Moneydance's own rule) and is listed above the figures;
 * - opening = the balance at the end of the day before; closing = the balance at the end of the transaction's day;
 * - "other transactions" (that day) is closing less opening less this transaction, shown only when not zero;
 * - the all-accounts block has the same rows, totalled across the accounts, and is shown only when more than one account holds the security.
 *
 * @author Stuart Beesley - October 2026
 */
class ShowShareBalance:ContextMenuAction {

  private val dialog_share_balance_size = ".gui.share_balance.size"
  private val dialog_share_balance_locn = ".gui.share_balance.loc"
  private val dialog_share_balance_rpt_size = ".gui.share_balance_rpt.size"
  private val dialog_share_balance_rpt_locn = ".gui.share_balance_rpt.loc"

  private val string_menu = "Show Share Balance: {name} - {held} held in this account today"
  private val string_menu_with_ticker = "Show Share Balance: {name} ({ticker}) - {held} held in this account today"
  private val string_title = "Share balance"
  private val string_title_security = "Share balance - {name}"
  private val string_title_security_with_ticker = "Share balance - {name} ({ticker})"
  private val string_transaction = "Transaction {date}  {desc}"
  private val string_this_account = "THIS ACCOUNT ({account})"
  private val string_all_accounts = "ALL ACCOUNTS HOLDING {name}"
  private val string_on = "On {date}"
  private val string_in_todays_shares = "In today's terms"
  private val string_opening = "Opening {date}"
  private val string_this_txn = "This transaction ({type})"
  private val string_other_txns = "Other transactions"
  private val string_closing = "Closing {date}"
  private val string_today = "Today"
  private val string_splits_since = "Splits since {date}"
  private val string_splits_since_none = "Splits since {date}: none"
  private val string_splits_on = "Splits on {date} (already included in the figures below)"
  private val string_ratio = "shares x {ratio}"
  private val string_split_line = "  {date}   {ratio}"
  private val string_failed = "Share balance could not be worked out: {error}."

  private val LABEL_WIDTH = 32
  private val VALUE_WIDTH = 20

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (listTxns.size != 1) return emptyList()
    val registerAcctType = listTxns.first().account.getAccountType()
    if (registerAcctType != Account.AccountType.INVESTMENT && registerAcctType != Account.AccountType.SECURITY) return emptyList()
    val ptxn = listTxns.first().parentTxn
    val fields = InvestFields()
    fields.setFieldStatus(ptxn)
    if (!fields.hasSecurity) return emptyList()
    val security = fields.security ?: return emptyList()

    val secCurr = security.currencyType
    val ticker = secCurr.getTickerSymbol().nullIfBlank?.takeIf { it != secCurr.getName() }
    val heldToday = secCurr.formatSemiFancy(security.currentBalance, mdGUI.preferences.decimalChar)
    val label = (if (ticker != null) string_menu_with_ticker.replace("{ticker}", ticker) else string_menu)
      .replace("{name}", secCurr.getName()).replace("{held}", heldToday)
    val action = addAction(label = label, cmd = "show_share_balance")
    { showShareBalance(menuContext, ptxn, security) }
    return listOf(action)
  }

  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }

  private fun showShareBalance(menuContext:MDActionContext, ptxn:ParentTxn, security:Account) {
    val book = ptxn.account.book
    val secCurr = security.currencyType
    val txnDate = ptxn.dateInt
    val dayBefore = DateUtil.incrementDate(txnDate, 0, 0, -1)
    val today = DateUtil.strippedDateInt

    val holdingAccts = AccountUtil.allMatchesForSearch(book, object:AcctFilter() {
      override fun matches(acct:Account?):Boolean = acct?.getAccountType() == Account.AccountType.SECURITY && acct.currencyType == secCurr
      override fun format(acct:Account):String = acct.fullAccountName
    })

    Thread({
      val balanceOf = try {
        balancesByAsOfDates(book, holdingAccts.toSet(), intArrayOf(dayBefore, txnDate, today))
      } catch (e:Exception) {
        UiUtil.runOnUIThread { mdGUI.showErrorMessage(string_failed.replace("{error}", e.toString())) }
        return@Thread
      }
      UiUtil.runOnUIThread { showWindows(menuContext, ptxn, security, holdingAccts, today, balanceOf) }
    }, "contextmenutools: share balance").start()
  }

  private fun showWindows(menuContext:MDActionContext, ptxn:ParentTxn, security:Account, holdingAccts:List<Account>,
                          today:Int, balanceOf:(Account, Int) -> Long) {
    val book = ptxn.account.book
    val secCurr = security.currencyType
    val dateFmt = mdGUI.preferences.shortDateFormatter
    val dec = mdGUI.preferences.decimalChar
    val txnDate = ptxn.dateInt
    val dayBefore = DateUtil.incrementDate(txnDate, 0, 0, -1)

    val thisTxn = (0 until ptxn.splitCount).mapNotNull { ptxn.getSplit(it) }.filter { it.account == security }.sumOf { it.value }
    val thisTxnLabel = string_this_txn.replace("{type}", mdGUI.resources.getString(InvestFields().also { it.setFieldStatus(ptxn) }.txnType, true))
    val onDateHeading = string_on.replace("{date}", dateFmt.format(txnDate))

    val rpt = Report2()
    rpt.addColumn()
    rpt.addColumn().defaultAlignment(CellStyle.Alignment.RIGHT)
    rpt.addColumn().defaultAlignment(CellStyle.Alignment.RIGHT)
    fun fmt(value:Long) = secCurr.formatSemiFancy(value, dec).padStart(VALUE_WIDTH)
    fun inToday(value:Long) = secCurr.adjustValueForSplitsInt(txnDate, value, today)
    fun row(label:String, onDate:Long?, todays:Long) =
      label.padEnd(LABEL_WIDTH) + (onDate?.let { fmt(it) } ?: "".padStart(VALUE_WIDTH)) + fmt(todays)
    fun ratio(split:CurrencySplit) = BigDecimal.valueOf(split.getSplitRatio()).stripTrailingZeros().toPlainString()

    // a label too long for the label column goes on its own line, so the column headings stay over their figures
    fun StringBuilder.appendHeading(label:String) {
      if (label.length >= LABEL_WIDTH) appendLine(label)
      appendLine((if (label.length >= LABEL_WIDTH) "" else label).padEnd(LABEL_WIDTH)
                 + onDateHeading.padStart(VALUE_WIDTH) + string_in_todays_shares.padStart(VALUE_WIDTH))
      rpt.addRow().apply { listOf(label, onDateHeading, string_in_todays_shares).forEach { addCell(it).styleBold() } }
    }

    fun StringBuilder.appendRow(label:String, onDate:Long?, todays:Long) {
      appendLine(row(label, onDate, todays))
      rpt.addRow().labels(listOf(label, onDate?.let { fmt(it).trim() } ?: "", fmt(todays).trim()))
    }

    fun StringBuilder.appendBlock(label:String, accts:List<Account>) {
      val startOfDay = secCurr.adjustValueForSplitsInt(dayBefore, accts.sumOf { balanceOf(it, dayBefore) }, txnDate)
      val endOfDay = accts.sumOf { balanceOf(it, txnDate) }
      val otherTxns = endOfDay - startOfDay - thisTxn
      appendHeading(label)
      appendRow(string_opening.replace("{date}", dateFmt.format(txnDate)), startOfDay, inToday(startOfDay))
      appendRow(thisTxnLabel, thisTxn, inToday(thisTxn))
      if (otherTxns != 0L) appendRow(string_other_txns, otherTxns, inToday(otherTxns))
      appendRow(string_closing.replace("{date}", dateFmt.format(txnDate)), endOfDay, inToday(endOfDay))
      appendRow(string_today, null, accts.sumOf { balanceOf(it, today) })
    }

    fun StringBuilder.appendBlank() { appendLine(); rpt.addSeparatorRow() }

    fun StringBuilder.appendText(line:String, splitRatio:String? = null) {
      appendLine(if (splitRatio == null) line else string_split_line.replace("{date}", line).replace("{ratio}", splitRatio))
      rpt.addRow().labels(listOfNotNull(line, splitRatio))
    }

    val ticker = secCurr.getTickerSymbol().nullIfBlank
    val titleTicker = ticker?.takeIf { it != secCurr.getName() }
    val title = (if (titleTicker != null) string_title_security_with_ticker.replace("{ticker}", titleTicker) else string_title_security)
      .replace("{name}", secCurr.getName())
    val txnLine = string_transaction.replace("{date}", dateFmt.format(txnDate)).replace("{desc}", ptxn.description)
    rpt.title(title).subTitle(txnLine)
    val text = buildString {
      appendLine(title)
      appendLine(txnLine)
      appendBlank()

      val sameDaySplits = secCurr.getSplits().filter { it.dateInt == txnDate }
      if (sameDaySplits.isNotEmpty()) {
        appendText(string_splits_on.replace("{date}", dateFmt.format(txnDate)).labelify)
        sameDaySplits.forEach { appendText(dateFmt.format(it.dateInt), string_ratio.replace("{ratio}", ratio(it))) }
        appendBlank()
      }

      appendBlock(string_this_account.replace("{account}", security.getParentAccount()?.fullAccountName ?: ""), listOf(security))

      if (holdingAccts.size > 1) {
        appendBlank()
        appendBlock(string_all_accounts.replace("{name}", ticker ?: secCurr.getName()), holdingAccts)
      }

      val splits = secCurr.getSplits().filter { it.dateInt in (txnDate + 1)..today }
      appendBlank()
      val sinceDate = dateFmt.format(txnDate)
      appendText(if (splits.isEmpty()) string_splits_since_none.replace("{date}", sinceDate) else string_splits_since.replace("{date}", sinceDate).labelify)
      splits.forEach { appendText(dateFmt.format(it.dateInt), string_ratio.replace("{ratio}", ratio(it))) }
    }

    val setKeys = try { ShowReportWindow::class.java.getMethod("setRememberSizeLocationKeys", String::class.java, String::class.java) } catch (_:NoSuchMethodException) { null }
    if (setKeys != null) {
      val rptWin = ShowReportWindow(mdGUI, null, ReportSpec(book), rpt)
      rptWin.name = Main.EXTN_ID
      setKeys.invoke(rptWin, Main.EXTN_ID + dialog_share_balance_rpt_size, Main.EXTN_ID + dialog_share_balance_rpt_locn)
      rptWin.isVisible = true
    } else {
      TextViewerDialog(
        mdGUI, menuContext.component, string_title, text, Main.STRING_COPY_TO_CLIPBOARD,
        sizeKey = Main.EXTN_ID + dialog_share_balance_size,
        locationKey = Main.EXTN_ID + dialog_share_balance_locn
      ).isVisible = true
    }
  }

  private fun balancesByAsOfDates(book:AccountBook, accounts:Set<Account>, asOfDates:IntArray):(Account, Int) -> Long {
    val compute = try {
      NetWorthCalculator::class.java.getMethod("computeAccountBalancesByAsOfDates", AccountBook::class.java, Set::class.java, IntArray::class.java)
    } catch (_:NoSuchMethodException) {
      val byAcct = accounts.associateWith { AccountUtil.getBalancesAsOfDates(book, it, asOfDates) }
      return { acct, asOfDate -> byAcct[acct]?.getOrNull(asOfDates.indexOf(asOfDate)) ?: 0L }
    }
    val result = compute.invoke(null, book, accounts, asOfDates)
    val getBalance = result.javaClass.getMethod("getBalance", Account::class.java, Int::class.javaObjectType)
    return { acct, asOfDate -> (getBalance.invoke(result, acct, asOfDate) as? TotalAmount)?.amount ?: 0L }
  }
}
