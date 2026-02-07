package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.*
import com.infinitekind.util.StringUtils
import com.infinitekind.util.labelify
import com.infinitekind.util.nullIfBlank
import com.moneydance.apps.md.controller.ActionContextType
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.controller.UserPreferences
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.modules.features.contextmenutools.util.StatusPopupDialog
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.awt.event.ActionListener
import javax.swing.Action
import javax.swing.JOptionPane
import javax.swing.SwingUtilities
import kotlin.math.roundToLong

@Suppress("DuplicatedCode", "PrivatePropertyName", "LocalVariableName", "SameParameterValue")

class ValueSelectedTxns: ContextMenuAction {
  
  private val string_value_selected_txns = "Show value of selected transactions"
  
  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    val actions = mutableListOf<Action>()
    
    // quick do-nothing exit if there are no items/accounts to process...
    if (listTxns.isEmpty() && listAccts.isEmpty()) return actions
    
    // build menu options for allowed types
    when (menuContext.type) {
      ActionContextType.register, ActionContextType.home_search -> {
        
        if (listTxns.size > 1) {
          
          listTxns.firstOrNull()?.account?.let {
            val duplicateTxnSameDateAction = addAction(label = string_value_selected_txns, cmd = "total_selected_txns")
            { valueSelectedTxns(menuContext = menuContext, txns = listTxns) }
            
            actions.add(duplicateTxnSameDateAction)
          }
        }
      }
      
      else -> {}
    }
    return actions
  }
  
  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }
  
  private fun valueSelectedTxns(menuContext:MDActionContext, txns:List<AbstractTxn>) {
    
    val prefs = Main.mdMain?.preferences ?: return
    val book = txns.first().account.book
    val dec = prefs.decimalChar
    val strings = Main.mdGUI.strings()

    var base = book.currencies.baseType
    val originalBase = base
    
    val MULTI_STR = strings.bal_popup_selection_multi
    
    val userPrefCurrID = prefs.getSetting(UserPreferences.GUI_POPUP_USER_CURR_ID_OVERRIDE, null)
    
    userPrefCurrID.nullIfBlank?.let {
      book.currencies.getCurrencyByIDString(userPrefCurrID)?.also { newBase ->
        if (newBase != base && newBase.currencyType == CurrencyType.Type.CURRENCY) {
          base = newBase
        }
      }
    }
    
    val totalsByTxnCurrency = mutableMapOf<CurrencyType, Long>()

    var primaryAccount:Account? = null
    var primaryAcctCurr:CurrencyType? = null
    var multiAccounts = false
    var multiAccountTypes = false
    var multiCurrency = false
    var investments = false
    var numShares = 0.0
    var feesInAcctCurr = 0.0
    var amountsInAcctCurr = 0.0
    var feesInBaseCurr = 0.0
    var amountsInBaseCurr = 0.0
    var buys = 0L
    var sells = 0L
    val fields = InvestFields()
    
    for (txn in txns) {
      val txnAcct = txn.account
      val txnAcctCurr = txnAcct.currencyType

      when {
        primaryAccount == null -> {
          primaryAccount = txnAcct
          primaryAcctCurr = txnAcctCurr
        }
        
        primaryAccount != txnAcct -> {
          multiAccounts = true
          if (primaryAccount.getAccountType() != txnAcct.getAccountType()) multiAccountTypes = true
          if (primaryAcctCurr != txnAcctCurr) multiCurrency = true
        }
      }

      if (txnAcct.getAccountType() == Account.AccountType.INVESTMENT) {

        investments = true
        fields.setFieldStatus(txn)

        val mult = if (fields.negateSecurity) -1.0 else 1.0

        if (fields.hasShares) {
          if (!fields.negateSecurity) buys++ else sells++
          fields.secCurr?.let {
            numShares += it.getDoubleValue(fields.shares) * mult
          }
        }
        if (fields.hasFee) {
          fields.curr?.let {
            feesInAcctCurr += it.getDoubleValue(fields.fee)
            feesInBaseCurr += base.getDoubleValue(CurrencyUtil.convertValue(value = fields.fee, fromCurrency = txnAcctCurr, toCurrency = base))
          }
        }
        if (fields.hasAmount) {
          fields.curr?.let {
            amountsInAcctCurr += it.getDoubleValue(fields.amount) * mult
            amountsInBaseCurr += base.getDoubleValue(CurrencyUtil.convertValue(value = fields.amount, fromCurrency = txnAcctCurr, toCurrency = base)) * mult
          }
        }
      }
      totalsByTxnCurrency[txnAcctCurr] = totalsByTxnCurrency.getOrPut(txnAcctCurr) { 0L } + txn.value

    }
    if (totalsByTxnCurrency.isEmpty()) return

    val totalInBaseCurrency = totalsByTxnCurrency.entries.sumOf {
      (txnCurr, amt) -> CurrencyUtil.convertValue(value = amt, fromCurrency = txnCurr, toCurrency = base)
    }
    
    val primary = primaryAccount ?: return
    val primaryCurr = primaryAcctCurr ?: return
    val isCat = (!multiAccountTypes && primaryAccount.getAccountType().isCategory)
    var acctTypeLbl = pad(strings.bal_popup_selection_account.labelify, 18)
    if (isCat) acctTypeLbl = pad(strings.bal_popup_selection_category.labelify, 18)
    val sumAcctCurr = totalsByTxnCurrency.values.sum()
    val count = txns.size

    val averageValueTxt =
      if (count > 0) {
        if (multiCurrency)
          base.formatFancy((totalInBaseCurrency.toDouble() / count.toDouble()).roundToLong(), dec)
          else primaryCurr.formatFancy((sumAcctCurr.toDouble() / count.toDouble()).roundToLong(), dec)
      } else ""

    val fxLine =
      if (primaryCurr != base || multiCurrency) "${pad(strings.bal_popup_selection_base_value.labelify, 18)}" +
                                                "${base.formatFancy(totalInBaseCurrency, dec)}\n"
      else ""
    
    val investLine = if (investments) {
      if (multiCurrency) "${pad(strings.bal_popup_selection_shares.labelify, 18)}${StringUtils.formatRate(numShares, dec, 4)} (${strings.bal_popup_selection_buys.labelify} $buys, ${strings.bal_popup_selection_sells.labelify} $sells)\n" +
                         "${pad(strings.bal_popup_selection_amounts_base.labelify, 18)}${StringUtils.formatRate(amountsInBaseCurr, dec, 2, true)}\n" +
                         "${pad(strings.bal_popup_selection_fees_base.labelify, 18)}${StringUtils.formatRate(feesInBaseCurr, dec, 2, true)}\n"

                    else "${pad(strings.bal_popup_selection_shares.labelify, 18)}${StringUtils.formatRate(numShares, dec, 4)} (${strings.bal_popup_selection_buys.labelify} $buys, ${strings.bal_popup_selection_sells.labelify} $sells)\n" +
                         "${pad(strings.bal_popup_selection_amounts_local.labelify, 18)}${StringUtils.formatRate(amountsInAcctCurr, dec, 2, true)}\n" +
                         "${pad(strings.bal_popup_selection_fees_local.labelify, 18)}${StringUtils.formatRate(feesInAcctCurr, dec, 2, true)}\n"
    } else ""

    val extraPreviewTxt = ""
    //val extraPreviewTxt =
    //  if (Main.PREVIEW_BUILD) "\n<PREVIEW BUILD: ${Main.mdMain!!.build}>"
    //  else ""

    val cashValueTxt =
      if (multiCurrency) base.formatFancy(totalInBaseCurrency, dec)
      else primaryCurr.formatFancy(sumAcctCurr, dec)

    val baseCurrTxt =
      if (base != originalBase) "(${strings.base_currency.labelify} '${base.idString}' >> ${strings.bal_popup_selection_original_base.labelify}'${originalBase.idString}')\n"
      else ""

    val headerLine =
      "${strings.bal_popup_selection_cash_value.labelify} " +
      "$cashValueTxt (${strings.bal_popup_selection_count.labelify} " +
      "$count, ${strings.bal_popup_selection_average.labelify} " +
      "$averageValueTxt)${if (multiCurrency) " (${strings.bal_popup_selection_multi_currency_converted_to_base})"
      else ""}"
    
    val detailMsg = buildString {
      append(acctTypeLbl).append(if (multiAccounts) MULTI_STR else primary.getAccountName()).append('\n')
      append(fxLine)
      append(investLine)
      append(pad(strings.bal_popup_selection_account_type.labelify, 18)).append(if (multiAccountTypes) MULTI_STR else primary.getAccountType()).append('\n')
      append(pad(strings.bal_popup_selection_currency.labelify, 18)).append(if (multiCurrency) MULTI_STR else "${primaryCurr.getName()} (${primaryCurr.idString})").append('\n')
      append(baseCurrTxt)
      append(extraPreviewTxt)
    }

    StatusPopupDialog(mdGUI = Main.mdGUI,
                      parent = SwingUtilities.windowForComponent(menuContext.component),
                      title = string_value_selected_txns,
                      status = headerLine,
                      message = detailMsg,
                      messageType = JOptionPane.INFORMATION_MESSAGE,
                      modal = false,
                      dlgName = Main.EXTN_ID)
      .showDialog()
    
    try { Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(cashValueTxt), null)} catch (_:Exception) {
    }
  }
  
  private fun pad(s:String, len:Int):String = if (s.length >= len) s else s.padEnd(len, ' ')
}