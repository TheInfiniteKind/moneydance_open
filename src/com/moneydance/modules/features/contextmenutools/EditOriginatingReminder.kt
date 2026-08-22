package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.Reminder
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.EditRemindersWindow
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.awt.AwtUtil
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.isUUIDDateMatch
import java.awt.event.ActionListener
import javax.swing.Action

@Suppress("PrivatePropertyName")

/**
 * Adds a context-menu action to open the reminder editor directly on whichever Reminder
 * auto-committed the selected transaction, identified via Moneydance's own auto-commit ID
 * convention ("{reminderUUID}.{txn's date}" - see ReminderSet.autoCommitReminder).
 *
 * Only offered when exactly 1 match is found. No other eligibility rules currently - the search
 * itself is same-account, transaction-type reminders, no expiry filter (unlike
 * UpdateReminderValue's candidate search, which needs usable-for-future-edits reminders; this is
 * an identity lookup for a transaction that already happened, so an expired or since-modified
 * reminder should still be found if it's the one that actually created this transaction).
 *
 * TODO: placeholder for additional narrowing rules if the plain UUID.date search ever proves too
 * broad in practice.
 */
class EditOriginatingReminder:ContextMenuAction {

  private val string_edit_originating_reminder = "Edit Originating Reminder"

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (listTxns.size != 1) return emptyList()
    val txn = listTxns.first().parentTxn

    val match = findOriginatingReminder(txn) ?: return emptyList()

    val action = addAction(label = string_edit_originating_reminder, cmd = "edit_originating_reminder")
    { editReminder(menuContext, txn) }
    return listOf(action)
  }

  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }

  /** Same-account, transaction-type reminders only, no expiry filter - see class kdoc. */
  private fun findOriginatingReminder(txn:ParentTxn):Reminder? {
    val book = txn.account.book
    return book.reminders.allReminders.firstOrNull { reminder ->
      reminder.getReminderType() == Reminder.Type.TRANSACTION &&
      reminder.transaction.account == txn.account &&
      isUUIDDateMatch(txn, reminder)
    }
  }

  private fun editReminder(menuContext:MDActionContext, txn:ParentTxn) {
    // re-validate at click time
    val reminder = findOriginatingReminder(txn) ?: return
    EditRemindersWindow.editReminder(AwtUtil.getFrame(menuContext.component), mdGUI, reminder)
  }
}