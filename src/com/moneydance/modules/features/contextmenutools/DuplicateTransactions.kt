package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.TxnUtil.getCorrespondingDuplicate
import com.infinitekind.moneydance.model.UndoableChange
import com.infinitekind.util.DateUtil.incrementDate
import com.infinitekind.util.DateUtil.strippedDateInt
import com.infinitekind.util.labelify
import com.moneydance.apps.md.controller.*
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.apps.md.view.gui.OKButtonWindow
import com.moneydance.apps.md.view.gui.moneyforesight.txnPredicate
import com.moneydance.apps.md.view.gui.txnreg.TxnRegister
import com.moneydance.awt.AwtUtil.getDialog
import com.moneydance.awt.GridC
import com.moneydance.awt.JDateField
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
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
    private val string_duplicate_adjust_date_tip = "Existing tax dates will also be adjusted..."
    private val string_duplicate_enter_date = "Enter new date"
    private val string_duplicate_enter_tax_date = "Enter new tax date"
    private val string_duplicate_are_you_sure = "Are you sure you want to duplicate {num} transactions?"
    private val string_undo_redo_dup_txns = "Duplicate {num} Transaction(s)"
    private val string_days = "Days"
    private val string_months = "Months"
    private val string_years  ="Years"
    
    override fun getActions(menuContext: MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>): List<Action> {
      val actions = mutableListOf<Action>()
      
      // quick do-nothing exit if there are no items/accounts to process...
      if (listTxns.isEmpty() && listAccts.isEmpty()) return actions
      
      // build menu options for allowed types
      when (menuContext.type) {
        ActionContextType.register -> {

          val txnRegister = (menuContext.component as? TxnRegister)

          if (listTxns.size > 1) {
            
            // check that all accounts are the same - otherwise, suspect running from home screen search, and reject
            listTxns.firstOrNull()?.account?.let { firstAcct ->
              val allSameAccount = listTxns.all { it.account == firstAcct }
              if (allSameAccount) {

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


  private enum class DuplicateTxnDateOption { SAME, ENTER, ADJUST }
  @JvmRecord data class DateAdjustments(val years: Int, val months: Int, val days: Int)
  @JvmRecord private data class DateIntPair(val firstDateInt: Int, val secondDateInt: Int)
  
  private fun duplicateTxns(adjustOption: DuplicateTxnDateOption, menuContext:MDActionContext, txns:List<AbstractTxn>) {
    val txnRegister = (menuContext.component as? TxnRegister) ?: return

    val showTaxDate = mdGUI.preferences.getBoolSetting(UserPreferences.GEN_SEPARATE_TAX_DATE, false)
    
    if (txns.size > 20 && !mdGUI.askQuestion(string_duplicate_are_you_sure.replace("{num}", "$txns.size"))) return
    
    var newDates: DateIntPair? = null
    var dateAdjustments: DateAdjustments? = null
    
    when (adjustOption) {
      DuplicateTxnDateOption.SAME -> {}
      DuplicateTxnDateOption.ADJUST -> {                                  // user wants to adjust by years/months/days
        if (txns.size < 2) return
        dateAdjustments = duplicateTxnsAdjustDate(showTaxDate, menuContext) ?: return
      }
      
      DuplicateTxnDateOption.ENTER -> {                                   // user wants to enter a new date for all txns being duplicated
        if (txns.size < 2) return
        var existingDate = -1
        var existingTaxDate = -1
        for (txn in txns) {
          existingDate = max(existingDate, txn.dateInt)
          existingTaxDate = max(existingTaxDate, txn.taxDateInt)
        }
        newDates = duplicateTxnsEnterDate(existingDate = existingDate, existingTaxDate = existingTaxDate, showTaxDate = showTaxDate, menuContext = menuContext) ?: return
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
    
    if (adjustOption == DuplicateTxnDateOption.ENTER || adjustOption == DuplicateTxnDateOption.ADJUST) {
      for ((txn, _) in duplicatedTxnPairs) {
        val parent = txn as ParentTxn // this is the duplicated txn (parent)
        val txnDate = parent.dateInt
        val taxDate = parent.taxDateInt
        val changeTaxDate = (taxDate != 0)
        if (adjustOption == DuplicateTxnDateOption.ADJUST) {
          dateAdjustments!!
          val newTxnDate = incrementDate(txnDate, dateAdjustments.years, dateAdjustments.months, dateAdjustments.days)
          parent.dateInt = newTxnDate
          parent.taxDateInt = newTxnDate        // by default just make the tax date the same
          if (showTaxDate && changeTaxDate) {   // we will adjust the tax date by the same amount of days/months/years (if it was set before and if tax dates are enabled)
            val newTaxDate = incrementDate(taxDate, dateAdjustments.years, dateAdjustments.months, dateAdjustments.days)
            parent.taxDateInt = newTaxDate
          }
        } else {                                // we are entering a fixed date
          newDates!!
          parent.dateInt = newDates.firstDateInt
          val taxDate = if (showTaxDate && newDates.secondDateInt > 0) newDates.secondDateInt else newDates.firstDateInt
          parent.taxDateInt = taxDate

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
  
  private fun duplicateTxnsEnterDate(existingDate: Int, existingTaxDate: Int, showTaxDate: Boolean, menuContext:MDActionContext): DateIntPair? {
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
      duplicateDatePnl.add(JLabel(string_duplicate_enter_tax_date.labelify), GridC.getc().xy(x, y).label())
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
    val win = OKButtonWindow(mdGUI, menuContext.component, string_duplicate_enter_date, null, OKButtonPanel.QUESTION_OK_CANCEL)
    win.setEscapeKeyCancels(true)
    
    win.window.addWindowListener(object : WindowAdapter() {
      override fun windowOpened(e: WindowEvent) {
        mdGUI.adjustWindow(win, getDialog(win), Dimension(250, 125 + (if (showTaxDate) 50 else 0)), null, null)
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
      return DateIntPair(newDateInt, newTaxDateInt)
    }
    return null
  }
  
  // popup a dialog for the use to enter date adjustments to the txns being duplicated
  private fun duplicateTxnsAdjustDate(showTaxDate: Boolean, menuContext:MDActionContext): DateAdjustments? {
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
    
    val x = 0
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
    
    win.window.addWindowListener(object : WindowAdapter() {
      override fun windowOpened(e: WindowEvent) {
        mdGUI.adjustWindow(win, getDialog(win), Dimension(300, 200 + (if (showTaxDate) 25 else 0)), null, null)
      }
    })
    
    val result = win.showDialog(dateAdjustmentPnl)
    
    if (result == OKButtonPanel.ANSWER_OK) {
      val years = yearSpinner.value as Int
      val months = monthSpinner.value as Int
      val days = daySpinner.value as Int
      if (years != 0 || months != 0 || days != 0) {
        return DateAdjustments(years, months, days)
      }
    }
    return null
  }
  
  private fun duplicateTxnsRecordChanges(duplicatedTxns: List<AbstractTxn>) {
    val change = UndoableChange()

    // attempt to set the undo menu name
    runCatching {
      change.javaClass
        .getMethod("setName", String::class.java)
        .invoke(change, string_undo_redo_dup_txns.replace("{num}", "${duplicatedTxns.size}"))
    }.recover {
      val f = change.javaClass.getDeclaredField("name")
      f.isAccessible = true
      f.set(change, string_undo_redo_dup_txns.replace("{num}", "${duplicatedTxns.size}"))
    }.getOrNull()
    
    duplicatedTxns.forEach { dup -> change.finishModification(modifiedItem = dup) }
    mdGUI.undoManager?.recordChange(change)
  }
  
}
