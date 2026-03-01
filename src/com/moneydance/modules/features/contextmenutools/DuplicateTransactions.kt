package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.InvestFields
import com.infinitekind.moneydance.model.InvestTxnType
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.SplitTxn
import com.infinitekind.moneydance.model.TxnUtil.getCorrespondingDuplicate
import com.infinitekind.moneydance.model.UndoableChange
import kotlin.math.abs
import com.infinitekind.util.DateUtil.incrementDate
import com.infinitekind.util.DateUtil.strippedDateInt
import com.infinitekind.util.labelify
import com.moneydance.apps.md.controller.*
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.apps.md.view.gui.OKButtonWindow
import com.moneydance.apps.md.view.gui.txnreg.TxnRegister
import com.moneydance.awt.GridC
import com.moneydance.awt.JDateField
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.Util
import com.moneydance.awt.JCurrencyField
import java.awt.Dimension
import java.awt.GridBagLayout
import java.awt.event.ActionListener
import java.awt.event.FocusAdapter
import java.awt.event.FocusEvent
import java.awt.event.WindowAdapter
import java.awt.event.WindowEvent
import java.util.LinkedHashSet
import java.util.Locale
import javax.swing.Action
import javax.swing.Box
import javax.swing.JLabel
import javax.swing.JPanel
import javax.swing.JSpinner
import javax.swing.SpinnerNumberModel
import javax.swing.border.EmptyBorder
import javax.swing.event.DocumentEvent
import javax.swing.event.DocumentListener
import kotlin.math.max

@Suppress("DuplicatedCode", "PrivatePropertyName", "AssignedValueIsNeverRead")

class DuplicateTransactions: ContextMenuAction {

    private val string_duplicate = "Duplicate transactions"
    private val string_duplicate_same_date = "With the same date(s)"
    private val string_duplicate_adjust_date = "Adjust duplicated date(s)"
    private val string_duplicate_adjust_date_one_month = "Adjust duplicated date(s) by one month"
    private val string_duplicate_adjust_date_tip = "Existing tax dates will also be adjusted..."
    private val string_duplicate_enter_date = "Enter new date"
    private val string_duplicate_enter_tax_date = "Enter new tax date"
    private val string_duplicate_enter_value = "New value"
    private val string_duplicate_enter_value_tooltip = "All transactions have the same value. Enter a new value for all duplicated txns (the sign / debit/credit direction of each will be preserved)."
    private val string_duplicate_are_you_sure = "Are you sure you want to duplicate {num} transactions?"
    private val string_undo_redo_dup_txns = "Duplicate {num} Transaction(s)"
    private val string_days = "Days"
    private val string_months = "Months"
    private val string_years  ="Years"
    
    override fun getActions(menuContext: MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>): List<Action> {
      val actions = mutableListOf<Action>()
      
      // quick do-nothing exit if there are no items/accounts to process...
      if (listTxns.isEmpty() && listAccts.isEmpty()) return actions
      
      if (listTxns.isNotEmpty()) {
        
        // check that all accounts are the same - otherwise, suspect running from home screen search, and reject
        // we only need this check for versions prior to MD2026(5500)
        listTxns.firstOrNull()?.account?.let { firstAcct ->
          
          // don't allow the duplicate options when called from an income/expense register (or other strange places)
          val acctType = firstAcct.getAccountType()
          if (!firstAcct.getAccountType().isCategory && acctType != Account.AccountType.ROOT && acctType != Account.AccountType.SECURITY) {
            val allSameAccount = listTxns.size == 1 || listTxns.all { it.account == firstAcct }
            if (allSameAccount) {
              
              if (listTxns.size > 1) {
                val duplicateTxnSameDateAction = addAction(label = "$string_duplicate - $string_duplicate_same_date", cmd = "duplicate_same_date")
                { duplicateTxns(adjustOption = DuplicateTxnDateOption.SAME, menuContext = menuContext, txns = listTxns) }
                val duplicateTxnEnterDateAction = addAction(label = "$string_duplicate - $string_duplicate_enter_date", cmd = "duplicate_enter_date")
                { duplicateTxns(adjustOption = DuplicateTxnDateOption.ENTER, menuContext = menuContext, txns = listTxns) }
                val duplicateTxnAdjustDateAction = addAction(label = "$string_duplicate - $string_duplicate_adjust_date", cmd = "duplicate_adjust_date")
                { duplicateTxns(adjustOption = DuplicateTxnDateOption.ADJUST, menuContext = menuContext, txns = listTxns) }
                actions.add(duplicateTxnSameDateAction)
                actions.add(duplicateTxnEnterDateAction)
                actions.add(duplicateTxnAdjustDateAction)
              }
              
              // always add this option
              val duplicateTxnAdjustOneMonthAction = addAction(label = "$string_duplicate - $string_duplicate_adjust_date_one_month", cmd = "duplicate_adjust_date_one_month")
              { duplicateTxns(adjustOption = DuplicateTxnDateOption.ADJUST_ONE_MONTH, menuContext = menuContext, txns = listTxns) }
              actions.add(duplicateTxnAdjustOneMonthAction)
            }
          }
        }
      }
      
      return actions
    }
  
  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }


  private enum class DuplicateTxnDateOption { SAME, ENTER, ADJUST, ADJUST_ONE_MONTH }
  @JvmRecord private data class DateAdjustments(val years: Int, val months: Int, val days: Int, val newValue: Long? = null)
  @JvmRecord private data class DateIntPair(val firstDateInt: Int, val secondDateInt: Int, val newValue: Long? = null)
  
  private fun duplicateTxns(adjustOption: DuplicateTxnDateOption, menuContext:MDActionContext, txns:List<AbstractTxn>) {
    val txnRegister = (menuContext.component as? TxnRegister) ?: return

    val showTaxDate = mdGUI.preferences.getBoolSetting(UserPreferences.GEN_SEPARATE_TAX_DATE, false)
    
    if (txns.size > 20 && !mdGUI.askQuestion(string_duplicate_are_you_sure.replace("{num}", "${txns.size}"))) return
    
    var newDates: DateIntPair? = null
    var dateAdjustments: DateAdjustments? = null
    
    // determine whether the (edit) value field should appear
    val showValueField = (adjustOption == DuplicateTxnDateOption.ADJUST || adjustOption == DuplicateTxnDateOption.ENTER) && canEditValue(txns)
    val valueField = if (showValueField) makeValueField(txns) else null
    
    when (adjustOption) {

      DuplicateTxnDateOption.SAME -> {}

      DuplicateTxnDateOption.ADJUST -> {                                  // user wants to adjust by years/months/days
        if (txns.size < 2) return
        dateAdjustments = duplicateTxnsAdjustDate(showTaxDate = showTaxDate, valueField = valueField, menuContext = menuContext) ?: return
      }

      DuplicateTxnDateOption.ADJUST_ONE_MONTH -> {
        if (txns.isEmpty()) return
        dateAdjustments = DateAdjustments(years = 0, months = 1, days = 0)
      }
      
      DuplicateTxnDateOption.ENTER -> {
        // user wants to enter a new date for all txns being duplicated
        // we can in special conditions, allow a new value to be entered too...
        if (txns.size < 2) return
        var existingDate = -1
        var existingTaxDate = -1
        for (txn in txns) {
          existingDate = max(existingDate, txn.dateInt)
          existingTaxDate = max(existingTaxDate, txn.taxDateInt)
        }
        newDates = duplicateTxnsEnterDate(existingDate = existingDate, existingTaxDate = existingTaxDate, showTaxDate = showTaxDate, valueField = valueField, menuContext = menuContext) ?: return
        if (newDates.firstDateInt <= 0) return
      }
    }
    
    // now duplicate the txns (same for all adjustment types)
    val duplicatedTxnPairs = mutableListOf<Pair<AbstractTxn, AbstractTxn>>()
    // note: Pair.first  holds the duplicated parent txn
    //       Pair.second holds the corresponding duplicated parent or split - depending on what was selected in the register
    for (originalTxn in txns) {
      val duplicatedParentTxn = originalTxn.parentTxn.duplicateAsNew()
      duplicatedParentTxn.clearedStatus = AbstractTxn.ClearedStatus.UNRECONCILED
      for (dupSplit in duplicatedParentTxn.allSplits) {
        dupSplit.clearedStatus = AbstractTxn.ClearedStatus.UNRECONCILED
      }
      val txnToEdit = getCorrespondingDuplicate(duplicatedParentTxn, originalTxn)
      duplicatedTxnPairs.add(duplicatedParentTxn to txnToEdit)
    }
    
    if (adjustOption == DuplicateTxnDateOption.ENTER || adjustOption == DuplicateTxnDateOption.ADJUST || adjustOption == DuplicateTxnDateOption.ADJUST_ONE_MONTH) {
      for ((txn, _) in duplicatedTxnPairs) {
        val parent = txn as ParentTxn // this is the duplicated txn (parent)
        val txnDate = parent.dateInt
        val taxDate = parent.taxDateInt
        val changeTaxDate = (taxDate != 0)
        if (adjustOption == DuplicateTxnDateOption.ADJUST || adjustOption == DuplicateTxnDateOption.ADJUST_ONE_MONTH) {
          dateAdjustments!!
          val newTxnDate = incrementDate(txnDate, dateAdjustments.years, dateAdjustments.months, dateAdjustments.days)
          parent.dateInt = newTxnDate
          parent.taxDateInt = newTxnDate        // by default just make the tax date the same
          if (showTaxDate && changeTaxDate) {   // we will adjust the tax date by the same number of days/months/years (if it was set before and if tax dates are enabled)
            val newTaxDate = incrementDate(taxDate, dateAdjustments.years, dateAdjustments.months, dateAdjustments.days)
            parent.taxDateInt = newTaxDate
          }
          
          if (adjustOption == DuplicateTxnDateOption.ADJUST) {
            // apply new value if user changed it (preserving original sign on each txn)
            dateAdjustments.newValue?.let { absNewValue ->
              applyNewValue(parent, absNewValue)
            }
          }

        } else {
          // we are entering a fixed date (and possibly editing the value)
          check(adjustOption == DuplicateTxnDateOption.ENTER)
          newDates!!
          parent.dateInt = newDates.firstDateInt
          val newTaxDate = if (showTaxDate && newDates.secondDateInt > 0) newDates.secondDateInt else newDates.firstDateInt
          parent.taxDateInt = newTaxDate
          
          // apply new value if user changed it (preserving original sign on each txn)
          newDates.newValue?.let { absNewValue ->
            applyNewValue(parent, absNewValue)
          }
        }
      }
    }
    
    if (duplicatedTxnPairs.size == 1) {
      txnRegister.beginEditing(duplicatedTxnPairs.first().second, true)
      return
    }

    duplicateTxnsRecordChanges(duplicatedTxnPairs.map { it.first })  // save the duplicated txns
    
    val selected = duplicatedTxnPairs.map { it.second }.toTypedArray()
    txnRegister.setSelectedTransactions(selected)
    
    val first = selected.first()
    val last = selected.last()
    val visibleTxn = if (first.dateInt >= last.dateInt) first else last
    txnRegister.ensureTxnIsVisible(visibleTxn)

  }
  
  /**
   * Determines whether the "edit value" field should be shown in the duplicate date dialog.
   *
   * All of the following conditions must be met (any failure 'poisons' the whole batch and prevents the edit value box from appearing):
   * - More than one transaction selected
   * - All transactions have exactly one split
   * - Both sides (parent and split) of every transaction have the same currency
   * - All transactions have the same absolute value
   * - The split value must be the negation of the parent value (simple 1:1 same-currency txn)
   * - Neither side of any transaction is a ROOT or SECURITY account
   * - If either side is an INVESTMENT account, the transaction must be a simple BANK transfer type with a transfer account
   */
  private fun canEditValue(txns: List<AbstractTxn>): Boolean {
    if (txns.size < 2) return false
    val investFields = InvestFields()
    val firstAbsValue = abs(txns.first().parentTxn.value)
    val firstCurrency = txns.first().parentTxn.account.currencyType
    for (txn in txns) {
      val parent = txn.parentTxn
      if (parent.splitCount != 1) return false                                      // more than 1 split - poison
      val split = parent.getOtherTxn(0)                             // safe as we know that split count is 1 so other(0) must be the only split
      val splitAcct = split.account
      val splitAcctType = splitAcct.getAccountType()
      val splitValue = split.value
      val parentAcct = parent.account
      val parentAcctType = parentAcct.getAccountType()
      val parentValue = parent.value
      val acctTypes = setOf(parentAcctType, splitAcctType)
      if (-splitValue != parentValue) return false                                  // values must match
      if (parentAcct.currencyType != firstCurrency) return false                    // different parent currency - poison
      if (splitAcct.currencyType != firstCurrency) return false                     // different split currency - poison
      if (abs(parentValue) != firstAbsValue) return false                       // not all same abs value - poison
      if (acctTypes.any { it == Account.AccountType.ROOT                            // should never happen - poison
                          || it == Account.AccountType.SECURITY }) return false
      if (acctTypes.any { it == Account.AccountType.INVESTMENT }) {
        investFields.setFieldStatus(parent)
        if (!investFields.hasXfrAcct) return false                                  // doesn't have transfer account - poison
        if (investFields.txnType != InvestTxnType.BANK) return false                // not a simple BANK (transfer) type invest txn - poison
        investFields.xfrAcct ?: return false                                        // no transfer account - poison
      }
    }
    return true
  }
  
  private fun duplicateTxnsEnterDate(existingDate: Int, existingTaxDate: Int, showTaxDate: Boolean, valueField: JCurrencyField?, menuContext:MDActionContext): DateIntPair? {
    val duplicateDatePnl = JPanel(GridBagLayout())
    duplicateDatePnl.border = EmptyBorder(16, 16, 16, 16)
    
    val shortDateFormat = mdGUI.preferences.shortDateFormatter
    
    val dupFixedDateField = JDateField(shortDateFormat)
    dupFixedDateField.dateInt = if (existingDate > 0) existingDate else strippedDateInt
    
    val dupFixedTaxDateField = JDateField(shortDateFormat)
    dupFixedTaxDateField.dateInt = if (showTaxDate && existingTaxDate > 0) existingTaxDate else dupFixedDateField.dateInt
    
    var x = 0
    var y = 0
    duplicateDatePnl.add(JLabel(string_duplicate_enter_date.labelify), GridC.getc().xy(x++, y).label())
    duplicateDatePnl.add(dupFixedDateField, GridC.getc().xy(x, y++).field())
    
    if (showTaxDate) {
      x = 0
      duplicateDatePnl.add(JLabel(string_duplicate_enter_tax_date.labelify), GridC.getc().xy(x, y).label().topInset(8))
      duplicateDatePnl.add(dupFixedTaxDateField, GridC.getc().xy(1, y++).field())
      
      dupFixedDateField.addFocusListener(object : FocusAdapter() {
        override fun focusLost(e: FocusEvent) {
          val thisField = e.source as JDateField
          if (!e.isTemporary) dupFixedTaxDateField.dateInt = thisField.dateInt
        }
      })
      
      // Add document listener to update tax field as user types
      dupFixedDateField.document.addDocumentListener(object : DocumentListener {
        fun update() {
          try {
            val newDate = dupFixedDateField.parseDateInt() // safe parse
            dupFixedTaxDateField.dateInt = newDate
          } catch (_: Exception) {}
        }
        override fun insertUpdate(e: DocumentEvent?) { update() }
        override fun removeUpdate(e: DocumentEvent?) { update() }
        override fun changedUpdate(e: DocumentEvent?) { update() }
      })
    } else {
      dupFixedTaxDateField.isEnabled = false
    }
    
    // edit txn's value field setup (only if eligible)
    val showValueField = valueField != null
    val existingAbsValue = valueField?.value
    valueField?.let {
      x = 0
      duplicateDatePnl.add(JLabel(string_duplicate_enter_value.labelify), GridC.getc().xy(x, y).label().topInset(8))
      duplicateDatePnl.add(it, GridC.getc().xy(1, y++).field())
    }

    val win = OKButtonWindow(mdGUI, menuContext.component, string_duplicate_enter_date, null, OKButtonPanel.QUESTION_OK_CANCEL)
    win.setEscapeKeyCancels(true)
    
    win.window.addWindowListener(object : WindowAdapter() {
      override fun windowOpened(e: WindowEvent) {
        win.pack()
        val preferredWidth = max(250, win.preferredSize.width)
        val preferredHeight = max(125 + (if (showTaxDate) 50 else 0) + (if (showValueField) 50 else 0), win.preferredSize.height)
        mdGUI.adjustWindow(win, Util.getComponentDialog(win), Dimension(preferredWidth, preferredHeight), null, null)
        dupFixedDateField.requestFocusInWindow()
      }
    })
    
    val result = win.showDialog(duplicateDatePnl)
    
    val newDateInt = dupFixedDateField.dateInt
    var newTaxDateInt = -1
    if (result == OKButtonPanel.ANSWER_OK && newDateInt > 0) {
      if (showTaxDate) {
        newTaxDateInt = dupFixedTaxDateField.dateInt
      }
      var newValue: Long? = null                                                         // capture new value if field was shown and value changed
      valueField?.let {
        val enteredLong = it.value
        if (enteredLong != existingAbsValue) newValue = enteredLong
      }
      return DateIntPair(newDateInt, newTaxDateInt, newValue)
    }
    return null
  }
  
  private fun makeValueField(txns:List<AbstractTxn>):JCurrencyField {
    val book = txns.first().account.book
    val currencyType = txns.first().account.currencyType
    val prefs = mdGUI.preferences
    return JCurrencyField(currencyType, book.currencies, prefs.decimalChar, prefs.thousandsSeparator).also {
      it.value = abs(txns.first().parentTxn.value)
      it.toolTipText = string_duplicate_enter_value_tooltip
    }
  }
  
  // popup a dialog for the use to enter date adjustments to the txns being duplicated
  private fun duplicateTxnsAdjustDate(showTaxDate: Boolean, valueField: JCurrencyField?, menuContext: MDActionContext): DateAdjustments? {
    val shortDateFormat = mdGUI.preferences.shortDateFormat.lowercase(Locale.ROOT)
    
    val yearSpinner = JSpinner(SpinnerNumberModel(0, -60, 60, 1))
    val monthSpinner = JSpinner(SpinnerNumberModel(1, -12, 12, 1))
    val daySpinner = JSpinner(SpinnerNumberModel(0, -31, 31, 1))
    
    val spinnerMap = mapOf('d' to daySpinner, 'm' to monthSpinner, 'y' to yearSpinner)
    
    val labelMap = mapOf(
      'd' to string_days.labelify,
      'm' to string_months.labelify,
      'y' to string_years.labelify
    )

    // Determine the order of components by parsing the format
    val seen: MutableSet<Char> = LinkedHashSet()
    for (c in shortDateFormat.toCharArray()) {
      if (c == 'd' || c == 'm' || c == 'y') {
        seen.add(c)
      }
    }
    val adjControlsOrder = seen.toList()
    
    val dateAdjustmentPnl = JPanel(GridBagLayout())
    dateAdjustmentPnl.border = EmptyBorder(16, 16, 16, 16)
    
    val win = OKButtonWindow(mdGUI, menuContext.component, string_duplicate_adjust_date, null, OKButtonPanel.QUESTION_OK_CANCEL)
    win.setEscapeKeyCancels(true)
    
    var x = 0
    var y = 0
    for (adjControl in adjControlsOrder) {
      dateAdjustmentPnl.add(JLabel(labelMap[adjControl]), GridC.getc().xy(x, y).label())
      dateAdjustmentPnl.add(spinnerMap[adjControl]!!, GridC.getc().xy(x + 1, y++).field().wx(0f).fillnone())
    }
    
    if (showTaxDate) {
      y++
      val infoLbl = JLabel(string_duplicate_adjust_date_tip, JLabel.CENTER)
      dateAdjustmentPnl.add(infoLbl, GridC.getc().xy(x, y++).wx(0f).center().topInset(20).colspan(2))
    }
    
    for (spinner in arrayOf(yearSpinner, monthSpinner, daySpinner)) {
      val editor = spinner.editor
      if (editor is JSpinner.DefaultEditor) {
        val tf = editor.textField
        tf.columns = 4
      }
    }

    // edit txn's value field setup (only if eligible)
    val showValueField = valueField != null
    val existingAbsValue = valueField?.value
    valueField?.let {
      x = 0
      dateAdjustmentPnl.add(JLabel(string_duplicate_enter_value.labelify), GridC.getc().xy(x, y).label().topInset(8))
      dateAdjustmentPnl.add(it, GridC.getc().xy(1, y++).field().wx(0f).fillnone())
    }
    
    win.window.addWindowListener(object : WindowAdapter() {
      override fun windowOpened(e: WindowEvent) {
        win.pack()
        val preferredWidth = max(300, win.preferredSize.width)
        val preferredHeight = max(200 + (if (showTaxDate) 25 else 0) + (if (showValueField) 50 else 0), win.preferredSize.height)
        mdGUI.adjustWindow(win, Util.getComponentDialog(win), Dimension(preferredWidth, preferredHeight), null, null)
      }
    })
    
    val result = win.showDialog(dateAdjustmentPnl)
    
    if (result == OKButtonPanel.ANSWER_OK) {
      val years = yearSpinner.value as Int
      val months = monthSpinner.value as Int
      val days = daySpinner.value as Int
      if (years != 0 || months != 0 || days != 0) {
        val newValue = if (valueField != null && valueField.value != existingAbsValue) valueField.value else null
        return DateAdjustments(years, months, days, newValue)
      }
    }
    return null
  }

  private fun applyNewValue(txn:AbstractTxn, newAbsValue:Long) {
    val parent = txn.parentTxn
    val split = parent.getOtherTxn(0) as SplitTxn
    val newSplitValue = if (split.value < 0) -newAbsValue else newAbsValue
    split.setAmount(newSplitValue, newSplitValue)
  }
  
  private fun duplicateTxnsRecordChanges(duplicatedTxns: List<AbstractTxn>) {
    val change = UndoableChange()

    val undoName = string_undo_redo_dup_txns.replace("{num}", "${duplicatedTxns.size}")

    val clazz = change.javaClass
    val setOk = runCatching {
      val m = clazz.getMethod("setName", String::class.java)
      m.invoke(change, undoName)
    }.isSuccess
    
    if (!setOk) {
      runCatching {
        val f = clazz.getDeclaredField("name")
        f.isAccessible = true
        f.set(change, undoName)
      }
    }
    
    duplicatedTxns.forEach { dup -> change.finishModification(modifiedItem = dup) }
    mdGUI.undoManager?.recordChange(change)
  }
  
}