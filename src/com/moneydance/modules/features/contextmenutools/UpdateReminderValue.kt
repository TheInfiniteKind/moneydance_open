package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.Reminder
import com.infinitekind.moneydance.model.UndoableChange
import com.infinitekind.util.labelify
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import com.moneydance.awt.JCurrencyField
import com.moneydance.modules.features.contextmenutools.Main.Companion.DEBUG
import com.moneydance.modules.features.contextmenutools.Main.Companion.extensionContext
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.*
import java.awt.GridBagLayout
import java.awt.Insets
import java.awt.event.ActionListener
import javax.swing.Action
import javax.swing.JButton
import javax.swing.JCheckBox
import javax.swing.JLabel
import javax.swing.JPanel
import javax.swing.border.EmptyBorder

@Suppress("DuplicatedCode", "PrivatePropertyName")

/**
 * Adds two mutually-exclusive context-menu actions for correcting a Reminder's own stored
 * transaction value/structure against a real register transaction:
 *
 * - "Update Reminder and transaction's value" (Scenario A) - offered when exactly one eligible
 *   reminder's single-split value exactly matches the selected transaction's single-split value.
 *   Opens a value-edit dialog that can optionally also update the selected transaction's own
 *   split to the same new value, in the same undo/redo batch.
 *
 * - "Update Reminder from selected transaction" (Scenario B) - offered otherwise, whenever at
 *   least one structurally-eligible reminder exists in the same account. Opens a picker over
 *   every eligible reminder; the chosen reminder's entire transaction is wholesale-replaced with
 *   a duplicate of the selected transaction. One-way only (txn -> reminder), no value-edit step.
 *
 * WHY TWO SCENARIOS: a Reminder's auto-recorded transaction and an unmatched downloaded bank
 * transaction can end up sitting side by side in the register with different values, because the
 * download didn't auto-merge (values differed). The auto-recorded entry is a like-for-like copy
 * of the reminder (same desc/account/split/value) - Scenario A. The downloaded entry carries the
 * bank's own description/categorization, which often won't resemble the reminder's own fields at
 * all - Scenario B's picker exists because automated matching can't be trusted there.
 *
 * ELIGIBILITY: both scenarios require the selected transaction's account, and every candidate
 * reminder's own account, to be BANK or CREDIT_CARD, and require the reminder to be unexpired
 * and share the exact same account as the selected transaction. Scenario A additionally requires
 * both sides to have exactly one split, with that split's currency matching its own account's
 * currency. Scenario B has no split-count or per-split-currency restriction on either side -
 * duplicateAsNew() copies whatever structure the selected transaction actually has.
 *
 * REMINDER MODEL NOTE: Reminder.transaction is not a separately-persisted object - it's a live
 * view constructed from the Reminder's own internal record, cached in a private field.
 * The Reminder itself is the real MoneydanceSyncableItem being persisted - UndoableChange's
 * beginModification/finishModification are called on the Reminder, never on reminder.transaction.
 * setEditingMode() is what stops a template transaction being saved later as a real, separate
 * register transaction - it's called explicitly on BOTH the Reminder and the fetched/replaced
 * ParentTxn wherever this class touches either, since the getter's fresh-construction path does
 * NOT call it itself (only the transaction SETTER does).
 */
class UpdateReminderValue:ContextMenuAction {

  private val LOG_SOURCE = "UpdateReminderValue"

  private val string_update_reminder_and_txn = "Update Reminder and transaction's value"
  private val string_update_reminder_from_txn = "Update Reminder from selected transaction"

  private val string_undo_redo_update_reminder_only = "Update Reminder Value"
  private val string_undo_redo_update_both = "Update Reminder and Transaction Value"
  private val string_undo_redo_update_reminder_from_txn = "Update Reminder from Transaction"

  private val string_disambiguate_title = "Select the Reminder to Update"
  private val string_full_picker_title = "Select a Reminder to Update from this Transaction"
  private val string_edit_value_title = "Update Reminder Value"
  private val string_confirm_replace_title = "Confirm Update Reminder from Transaction"

  private val string_from_label = "Current Value"
  private val string_new_value_label = "New Value"
  private val string_also_update_txn = "Also update this transaction"
  private val string_reminder_label = "Reminder"
  private val string_account_label = "Account"
  private val string_category_label = "Category"
  private val string_memo_label = "Memo"
  private val string_next_scheduled_label = "Upcoming reminder dates..."
  private val string_current_txn_heading = "Current Transaction"
  private val string_replacement_txn_heading = "Will be replaced with"
  private val string_description_label = "Description"
  private val string_total_label = "Total"
  private val string_splits_label = "Splits"

  private val string_reset_tooltip = "Reset to the selected transaction's value"
  private val string_rewind_tooltip = "Rewind to the reminder's current value"

  // real Moneydance-bundled icons - same resource paths already confirmed working elsewhere in
  // this extension (CopyPasteSplits.kt's askRebalanceChoice/askPasteAlwaysConfirmChoice)
  private val ICON_RESET_PATH = "com/moneydance/apps/md/view/gui/glyphs/reset.png"
  private val ICON_REWIND_PATH = "com/moneydance/apps/md/view/gui/glyphs/horizontal-left.png"

  private val dialog_disambiguate_size = ".gui.update_reminder.disambiguate.size"
  private val dialog_disambiguate_locn = ".gui.update_reminder.disambiguate.loc"
  private val dialog_full_picker_size = ".gui.update_reminder.picker.size"
  private val dialog_full_picker_locn = ".gui.update_reminder.picker.loc"
  private val dialog_edit_value_size = ".gui.update_reminder.edit_value.size"
  private val dialog_edit_value_locn = ".gui.update_reminder.edit_value.loc"
  private val dialog_confirm_replace_size = ".gui.update_reminder.confirm_replace.size"
  private val dialog_confirm_replace_locn = ".gui.update_reminder.confirm_replace.loc"

  // ------------------------------------------------------------------------------------------
  // eligibility - evaluated both at menu-build time and again at click time
  // ------------------------------------------------------------------------------------------

  private fun isEligibleAccountType(acct:Account):Boolean =
    acct.getAccountType() == Account.AccountType.BANK || acct.getAccountType() == Account.AccountType.CREDIT_CARD

  /**
   * Base candidate pool: unexpired, same account as the selected txn (which also enforces
   * BANK/CREDIT_CARD on the reminder side, since it's the same account). No split-count or
   * per-split-currency restriction here - those are applied narrower, only for the Scenario A
   * exact-match subset below.
   */
  private fun findCandidateReminders(txn:ParentTxn):List<Reminder> {
    if (!isEligibleAccountType(txn.account)) return emptyList()
    val book = txn.account.book

    return book.reminders.allReminders.filter { reminder ->
      reminder.getReminderType() == Reminder.Type.TRANSACTION &&
      !reminder.isInactiveOrExpired() &&
      reminder.transaction.account == txn.account
    }
  }

  /**
   * Scenario A candidate subset of the given pool: both sides single-split, both sides' single
   * split currency matches its own account's currency, and the values match exactly (raw,
   * signed). Empty immediately if the selected txn itself is multi-split - Scenario A is never
   * attempted for a multi-split selection.
   */
  /**
   * Structural prerequisite for BOTH Scenario A match tiers (UUID.date and exact value): both
   * sides must have exactly 1 split, with that split's currency matching its own account's
   * currency. Multi-split selections never enter Scenario A - both tiers below return empty for
   * an ineligible pool, and getActions/updateReminderAndTxnFlow fall straight through to
   * Scenario B as a result.
   */
  private fun singleSplitEligiblePool(txn:ParentTxn, pool:List<Reminder>):List<Reminder> {
    if (txn.allSplits.size != 1) return emptyList()
    val txnSplit = txn.allSplits.first()
    if (txnSplit.account.currencyType != txn.account.currencyType) return emptyList()

    return pool.filter { reminder ->
      val rTxn = reminder.transaction
      if (rTxn.allSplits.size != 1) return@filter false
      val rSplit = rTxn.allSplits.first()
      rSplit.account.currencyType == rTxn.account.currencyType
    }
  }

  /**
   * Identity match, not a heuristic: txn's own UUID equals "{reminderUUID}.{txn's date}" -
   * Moneydance's own auto-commit convention (ReminderSet.autoCommitReminder sets a committed
   * transaction's ID to exactly this). Only confirmed for auto-committed occurrences - a
   * manually-entered transaction may not follow this convention, in which case it simply won't
   * match here and falls through to the value tier below.
   */
  private fun uuidDateMatchCandidates(txn:ParentTxn, eligiblePool:List<Reminder>):List<Reminder> =
    eligiblePool.filter { reminder -> txn.UUID == "${reminder.UUID}.${txn.dateInt}" }

  /** Exact value match (raw, signed) within the structurally-eligible pool. */
  private fun valueMatchCandidates(txn:ParentTxn, eligiblePool:List<Reminder>):List<Reminder> {
    val txnSplit = txn.allSplits.first()
    return eligiblePool.filter { reminder -> reminder.transaction.allSplits.first().value == txnSplit.value }
  }

  /** Trimmed, case-insensitive equality between the selected txn's description and the
   *  candidate reminder's own transaction description. */
  private fun descriptionMatches(txn:ParentTxn, reminder:Reminder):Boolean =
    txn.description.trim().equals(reminder.transaction.description.trim(), ignoreCase = true)

  // ------------------------------------------------------------------------------------------
  // menu
  // ------------------------------------------------------------------------------------------

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (listTxns.size != 1) return emptyList()
    val txn = listTxns.first() as? ParentTxn ?: return emptyList()
    if (!isEligibleAccountType(txn.account)) {
      logBlockedIfDebug(LOG_SOURCE, "Account type not eligible for account '${txn.account.fullAccountName}' (${txn.account.getAccountType()})")
      return emptyList()
    }

    val pool = findCandidateReminders(txn)
    if (pool.isEmpty()) {
      logBlockedIfDebug(LOG_SOURCE, "No eligible reminders found for account '${txn.account.fullAccountName}'")
      return emptyList()
    }

    val eligiblePool = singleSplitEligiblePool(txn, pool)
    val hasMatch = uuidDateMatchCandidates(txn, eligiblePool).isNotEmpty() ||
                   valueMatchCandidates(txn, eligiblePool).isNotEmpty()

    return if (hasMatch) {
      listOf(addAction(label = string_update_reminder_and_txn, cmd = "update_reminder_and_txn")
      { updateReminderAndTxnFlow(menuContext, txn) })
    } else {
      listOf(addAction(label = string_update_reminder_from_txn, cmd = "update_reminder_from_txn")
      { updateReminderFromTxnFlow(menuContext, txn) })
    }
  }

  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }

  // ------------------------------------------------------------------------------------------
  // Scenario A - Update Reminder and transaction's value
  // ------------------------------------------------------------------------------------------

  private fun updateReminderAndTxnFlow(menuContext:MDActionContext, txn:ParentTxn) {
    // re-validate at click time
    val pool = findCandidateReminders(txn)
    val eligiblePool = singleSplitEligiblePool(txn, pool)

    val uuidMatches = uuidDateMatchCandidates(txn, eligiblePool)
    if (uuidMatches.size == 1) {
      // identity match, not a heuristic - no desc confirmation needed
      showEditValueDialog(menuContext, txn, uuidMatches.first())
      return
    }

    val valueMatches = valueMatchCandidates(txn, eligiblePool)
    if (uuidMatches.isEmpty() && valueMatches.isEmpty()) {
      logBlockedIfDebug(LOG_SOURCE, "No matching reminders remained at click time for '${txn.description}' (${txn.dateInt}) - data changed since the menu was built")
      return
    }

    val descMatches = valueMatches.filter { descriptionMatches(txn, it) }

    val chosen =
      if (descMatches.size == 1) {
        descMatches.first()
      } else {
        // 0 or 2+ description matches on the value tier - always make the user confirm
        // explicitly. Picker shows every UUID-match and value-match candidate together
        // (deduplicated) - UUID matches (if any) sort to the top via pickReminder's own tiering.
        val disambiguationSet = (uuidMatches + valueMatches).distinct()
        pickReminder(
          mdGUI, menuContext.component, string_disambiguate_title, disambiguationSet,
          sizeKey = Main.EXTN_ID + dialog_disambiguate_size,
          locationKey = Main.EXTN_ID + dialog_disambiguate_locn,
          showSplitPercentages = false,
          referenceTxn = txn
        ) ?: return
      }

    showEditValueDialog(menuContext, txn, chosen)
  }

  private fun showEditValueDialog(menuContext:MDActionContext, txn:ParentTxn, reminder:Reminder) {
    val reminderTxn = reminder.transaction
    val rSplit = reminderTxn.allSplits.first()
    val fromValue = reminderTxn.value
    val suggestedValue = txn.value
    val currency = reminderTxn.account.currencyType
    val currencyTable = reminderTxn.account.book.currencies
    val dec = mdGUI.preferences.decimalChar
    val com = if (dec == ',') '.' else ','

    val fromValueStr = currency.formatFancy(fromValue, dec)

    val newValueField = JCurrencyField(currency, currencyTable, dec, com).also {
      it.value = suggestedValue
    }
    val resetButton = buildUseValueButton(string_reset_tooltip, ICON_RESET_PATH, "\u21ba", newValueField, suggestedValue)
    val rewindButton = buildUseValueButton(string_rewind_tooltip, ICON_REWIND_PATH, "\u2190", newValueField, fromValue)

    val canAlsoUpdate = isAllUnreconciled(txn) && !hasAnyProtectedSplit(txn)
    val alsoUpdateTxnCheckbox = JCheckBox(string_also_update_txn).apply {
      isEnabled = canAlsoUpdate
      isSelected = canAlsoUpdate   // default ticked whenever eligible, per author's instruction
    }

    val fieldRow = JPanel(GridBagLayout())
    fieldRow.add(newValueField, GridC.getc().xy(0, 0))
    fieldRow.add(resetButton, GridC.getc().xy(1, 0).insets(0, 4, 0, 0))
    fieldRow.add(rewindButton, GridC.getc().xy(2, 0).insets(0, 4, 0, 0))

    val panel = JPanel(GridBagLayout())
    panel.border = EmptyBorder(16, 16, 16, 16)
    var y = 0
    panel.add(JLabel("$string_reminder_label: ${reminder.description}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_account_label: ${reminderTxn.account.fullAccountName}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_description_label: ${reminderTxn.description}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_category_label: ${rSplit.account.fullAccountName}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    reminder.memo?.trim()?.takeIf { it.isNotEmpty() }?.let {
      panel.add(JLabel("$string_memo_label: $it"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    }
    panel.add(JLabel("$string_from_label: $fromValueStr"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_next_scheduled_label: ${upcomingDatesStr(mdGUI, reminder)}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 12, 0))

    panel.add(JLabel(string_new_value_label.labelify), GridC.getc().xy(0, y).label())
    panel.add(fieldRow, GridC.getc().xy(1, y++).wx(1f).field())

    panel.add(alsoUpdateTxnCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(10, 0, 0, 0))

    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, string_edit_value_title, OKButtonPanel.QUESTION_OK_CANCEL,
      focusComponent = newValueField,
      sizeKey = Main.EXTN_ID + dialog_edit_value_size,
      locationKey = Main.EXTN_ID + dialog_edit_value_locn
    )
    win.setEscapeKeyCancels(true)

    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return

    val newValue = newValueField.value
    applyReminderAndTxnUpdate(reminder, txn, newValue, alsoUpdateTxnCheckbox.isSelected && canAlsoUpdate)
  }

  /** Same "small button that sets a JCurrencyField to a given value on click" pattern as
   *  CopyPasteSplits.kt's buildUseValueButton - not shared (this class doesn't import that
   *  private helper), duplicated here since it's a tiny, self-contained few lines. */
  private fun buildUseValueButton(tooltip:String, iconPath:String, fallbackText:String, field:JCurrencyField, value:Long):JButton {
    val icon = Util.loadIcon(iconPath)
    val btn = if (icon != null) JButton(icon) else JButton(fallbackText)
    btn.toolTipText = tooltip
    btn.margin = Insets(1, 4, 1, 4)
    btn.addActionListener { field.value = value }
    return btn
  }

  private fun applyReminderAndTxnUpdate(reminder:Reminder, txn:ParentTxn, newValue:Long, alsoUpdateTxn:Boolean) {
    // newValue is parent-convention (matches reminderTxn.value/txn.value - what's displayed and
    // typed in the dialog). SplitTxn.setAmount expects split-convention (samt), which for a
    // single-split transaction is the exact negation of parent-convention (pamt) - confirmed
    // against DuplicateTransactions.applyNewValue()'s own working precedent, which computes its
    // split value in split.value's own sign and passes the same number to both setAmount args.
    val splitConventionValue = -newValue

    val change = UndoableChange()

    change.beginModification(reminder)
    reminder.setEditingMode()
    reminder.transaction.setEditingMode()   // getter's fresh-construction path doesn't set this itself
    reminder.transaction.allSplits.first().setAmount(splitConventionValue, splitConventionValue)
    change.finishModification(reminder)

    if (alsoUpdateTxn) {
      change.beginModification(txn)
      txn.allSplits.first().setAmount(splitConventionValue, splitConventionValue)
      change.finishModification(txn)
    }

    change.setNameCompat(if (alsoUpdateTxn) string_undo_redo_update_both else string_undo_redo_update_reminder_only)
    mdGUI.undoManager?.recordChange(change)

    if (extensionContext?.debugMenuEnabled == true || DEBUG) {
      Util.logConsole(
        "UpdateReminderValue: updated reminder '${reminder.description}' to $newValue" +
        (if (alsoUpdateTxn) ", also updated txn '${txn.description}' (${txn.dateInt})" else "")
      )
    }
  }

  // ------------------------------------------------------------------------------------------
  // Scenario B - Update Reminder from selected transaction
  // ------------------------------------------------------------------------------------------

  private fun updateReminderFromTxnFlow(menuContext:MDActionContext, txn:ParentTxn) {
    // re-validate at click time
    val revalidatedPool = findCandidateReminders(txn)
    if (revalidatedPool.isEmpty()) {
      logBlockedIfDebug(LOG_SOURCE, "No eligible reminders remained at click time for '${txn.description}' (${txn.dateInt}) - data changed since the menu was built")
      return
    }

    val chosen = pickReminder(
      mdGUI, menuContext.component, string_full_picker_title, revalidatedPool,
      sizeKey = Main.EXTN_ID + dialog_full_picker_size,
      locationKey = Main.EXTN_ID + dialog_full_picker_locn,
      showSplitPercentages = false,
      referenceTxn = txn
    ) ?: return

    if (!showConfirmReplaceDialog(menuContext, chosen, txn)) return

    applyReminderFromTxnUpdate(chosen, txn)
  }

  /**
   * Read-only review before committing the wholesale replace - nothing here is editable.
   * Reminder name, account, and next-scheduled dates are shown once (none of them change).
   * The current reminder transaction and the transaction it will be replaced with are shown
   * stacked, since those are the two things that actually differ.
   */
  private fun showConfirmReplaceDialog(menuContext:MDActionContext, reminder:Reminder, txn:ParentTxn):Boolean {
    val reminderTxn = reminder.transaction
    val currency = reminderTxn.account.currencyType
    val dec = mdGUI.preferences.decimalChar

    val panel = JPanel(GridBagLayout())
    panel.border = EmptyBorder(16, 16, 16, 16)
    var y = 0
    panel.add(JLabel("$string_reminder_label: ${reminder.description}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_account_label: ${reminderTxn.account.fullAccountName}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_next_scheduled_label: ${upcomingDatesStr(mdGUI, reminder)}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 12, 0))

    panel.add(buildTxnSummaryBlock(string_current_txn_heading, reminderTxn, currency, dec), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 10, 0))
    panel.add(buildTxnSummaryBlock(string_replacement_txn_heading, txn, currency, dec), GridC.getc().xy(0, y++).colspan(2).wx(1f).west())

    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, string_confirm_replace_title, OKButtonPanel.QUESTION_OK_CANCEL,
      sizeKey = Main.EXTN_ID + dialog_confirm_replace_size,
      locationKey = Main.EXTN_ID + dialog_confirm_replace_locn
    )
    win.setEscapeKeyCancels(true)

    return win.showDialog(panel) == OKButtonPanel.ANSWER_OK
  }

  private fun buildTxnSummaryBlock(heading:String, blockTxn:ParentTxn, currency:CurrencyType, dec:Char):JPanel {
    val panel = JPanel(GridBagLayout())
    var y = 0
    panel.add(JLabel(heading).also { it.font = it.font.deriveFont(java.awt.Font.BOLD) }, GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_description_label: ${blockTxn.description}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 2, 0))
    panel.add(JLabel("$string_total_label: ${currency.formatFancy(blockTxn.value, dec)}"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 2, 0))
    val splitsStr = blockTxn.allSplits.joinToString(", ") { it.account.getAccountName() }
    panel.add(JLabel("$string_splits_label: ${blockTxn.allSplits.size} ($splitsStr)"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    return panel
  }

  private fun applyReminderFromTxnUpdate(reminder:Reminder, txn:ParentTxn) {
    // duplicateAsNew() does NOT itself reset status - force parent + every split to unreconciled,
    // same pattern as TxnRegister's own memorizeAction (real Moneydance source, not guessed).
    val duplicate = txn.duplicateAsNew()
    duplicate.clearedStatus = AbstractTxn.ClearedStatus.UNRECONCILED
    for (i in duplicate.splitCount - 1 downTo 0) {
      duplicate.getSplit(i)!!.clearedStatus = AbstractTxn.ClearedStatus.UNRECONCILED
    }

    val change = UndoableChange()
    change.beginModification(reminder)
    reminder.setEditingMode()
    reminder.transaction = duplicate   // setter also calls duplicate.setEditingMode() internally
    change.finishModification(reminder)

    change.setNameCompat(string_undo_redo_update_reminder_from_txn)
    mdGUI.undoManager?.recordChange(change)

    if (extensionContext?.debugMenuEnabled == true || DEBUG) {
      Util.logConsole(
        "UpdateReminderValue: replaced reminder '${reminder.description}' transaction from '${txn.description}' (${txn.dateInt})"
      )
    }
  }
}