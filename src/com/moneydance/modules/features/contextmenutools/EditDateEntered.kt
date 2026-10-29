package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.UndoableChange
import com.infinitekind.util.labelify
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import com.moneydance.awt.JDateField
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.SizedOKButtonWindow
import com.moneydance.modules.features.contextmenutools.util.setNameCompat
import java.awt.GridBagLayout
import java.awt.event.ActionListener
import java.util.Calendar
import java.util.Date
import javax.swing.Action
import javax.swing.JLabel
import javax.swing.JPanel
import javax.swing.JSpinner
import javax.swing.SpinnerDateModel
import javax.swing.border.EmptyBorder

@Suppress("PrivatePropertyName")

/**
 * Adds a context-menu action to edit the "date entered" of the selected transaction - always the
 * parent's, since Moneydance holds date entered only on the parent (splits read the parent's).
 *
 * Date entered is a full date and time in milliseconds, local time zone. Moneydance uses it to
 * order transactions that share the same date, and keeps it unique for that reason.
 *
 * Rules:
 * - offered only when exactly one transaction is selected;
 * - any date may be entered, but never a date/time later than now: pressing OK with one, or with
 *   a date or time that cannot be read, shows an info message that nothing was saved, and ends;
 * - the time is entered as 24-hour HH:mm:ss in a spinner (the arrows change the part under the
 *   cursor: hours, minutes or seconds); the old value's milliseconds are kept on save, so
 *   the value stays unique;
 * - OK with no change saves nothing and records no undo step;
 * - a change is saved straight away as one undo/redo step.
 *
 * @author Stuart Beesley - October 2026
 */
class EditDateEntered:ContextMenuAction {

  private val dialog_edit_date_entered_size = ".gui.edit_date_entered.size"
  private val dialog_edit_date_entered_locn = ".gui.edit_date_entered.loc"

  private val string_edit_date_entered = "Edit date entered"
  private val string_edit_date_entered_title = "Edit date entered"
  private val string_undo_redo_edit_date_entered = "Edit Date Entered"
  private val string_account_label = "Account"
  private val string_desc_label = "Description"
  private val string_value_label = "Amount"
  private val string_date_label = "Date"
  private val string_tax_date_label = "Tax date"
  private val string_date_entered_label = "Date entered"
  private val string_time_entered_label = "Time entered (HH:mm:ss)"
  private val string_future_not_saved = "Date entered cannot be later than now - NOT saved."
  private val string_bad_date_time_not_saved = "Date or time entered is not valid (time must be HH:mm:ss, 24-hour) - NOT saved."

  private val TIME_PATTERN = "HH:mm:ss"

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (listTxns.size != 1) return emptyList()
    val txn = listTxns.first().parentTxn

    val action = addAction(label = string_edit_date_entered, cmd = "edit_date_entered")
    { editDateEntered(menuContext, txn) }
    return listOf(action)
  }

  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }

  private fun editDateEntered(menuContext:MDActionContext, txn:ParentTxn) {
    val oldMillis = txn.dateEntered
    val millisPart = Calendar.getInstance().apply { timeInMillis = oldMillis }.get(Calendar.MILLISECOND)

    val dateFmt = mdGUI.preferences.shortDateFormatter
    val dec = mdGUI.preferences.decimalChar
    val dateField = JDateField(dateFmt)
    val timeSpinner = JSpinner(SpinnerDateModel()).apply {
      editor = JSpinner.DateEditor(this, TIME_PATTERN)
    }

    val oldCal = Calendar.getInstance().apply { timeInMillis = oldMillis }
    dateField.dateInt = oldCal.get(Calendar.YEAR) * 10000 + (oldCal.get(Calendar.MONTH) + 1) * 100 + oldCal.get(Calendar.DAY_OF_MONTH)
    timeSpinner.value = Date(oldMillis)

    val valueStr = txn.account.currencyType.formatFancy(txn.value, dec)

    val panel = JPanel(GridBagLayout()).also {
      it.border = EmptyBorder(16, 16, 16, 16)
      var y = 0
      it.add(JLabel(string_account_label.labelify), GridC.getc().xy(0, y).label())
      it.add(JLabel(txn.account.fullAccountName), GridC.getc().xy(1, y++).west())
      it.add(JLabel(string_desc_label.labelify), GridC.getc().xy(0, y).label())
      it.add(JLabel(txn.description), GridC.getc().xy(1, y++).west())
      it.add(JLabel(string_value_label.labelify), GridC.getc().xy(0, y).label())
      it.add(JLabel(valueStr), GridC.getc().xy(1, y++).west())
      it.add(JLabel(string_date_label.labelify), GridC.getc().xy(0, y).label())
      it.add(JLabel(dateFmt.format(txn.dateInt)), GridC.getc().xy(1, y++).west())
      it.add(JLabel(string_tax_date_label.labelify), GridC.getc().xy(0, y).label())
      it.add(JLabel(dateFmt.format(txn.taxDateInt)), GridC.getc().xy(1, y++).west())
      it.add(JLabel(string_date_entered_label.labelify), GridC.getc().xy(0, y).label())
      it.add(dateField, GridC.getc().xy(1, y++).field())
      it.add(JLabel(string_time_entered_label.labelify), GridC.getc().xy(0, y).label())
      it.add(timeSpinner, GridC.getc().xy(1, y).field())
    }

    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, string_edit_date_entered_title, OKButtonPanel.QUESTION_OK_CANCEL,
      focusComponent = dateField,
      sizeKey = Main.EXTN_ID + dialog_edit_date_entered_size,
      locationKey = Main.EXTN_ID + dialog_edit_date_entered_locn
    )
    win.setEscapeKeyCancels(true)

    if (win.showDialog(panel) != OKButtonPanel.ANSWER_OK) return

    val dateInt = dateField.dateInt
    // text typed into the spinner is only taken once committed; text that is not a valid time fails here
    val time = try { timeSpinner.commitEdit(); timeSpinner.value as? Date } catch (e:Exception) { null }
    if (dateInt <= 0 || time == null) {
      mdGUI.showInfoMessage(string_bad_date_time_not_saved)
      return
    }

    val timeCal = Calendar.getInstance().apply { this.time = time }
    val newMillis = Calendar.getInstance().apply {
      clear()
      set(dateInt / 10000, dateInt / 100 % 100 - 1, dateInt % 100,
          timeCal.get(Calendar.HOUR_OF_DAY), timeCal.get(Calendar.MINUTE), timeCal.get(Calendar.SECOND))
      set(Calendar.MILLISECOND, millisPart)
    }.timeInMillis

    if (newMillis > System.currentTimeMillis()) {
      mdGUI.showInfoMessage(string_future_not_saved)
      return
    }

    if (newMillis == oldMillis) return

    val change = UndoableChange()
    change.beginModification(txn)
    txn.dateEntered = newMillis
    change.finishModification(txn)
    change.setNameCompat(string_undo_redo_edit_date_entered)
    mdGUI.undoManager?.recordChange(change)
  }
}
