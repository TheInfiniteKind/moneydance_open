package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.*
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import com.moneydance.awt.JCurrencyField
import com.moneydance.modules.features.contextmenutools.Main.Companion.DEBUG
import com.moneydance.modules.features.contextmenutools.Main.Companion.extensionContext
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.*
import java.awt.Cursor
import java.awt.GridBagLayout
import java.awt.Insets
import java.awt.event.ActionListener
import java.awt.event.MouseAdapter
import java.awt.event.MouseEvent
import javax.swing.*
import javax.swing.border.EmptyBorder
import kotlin.math.abs

@Suppress("DuplicatedCode", "PrivatePropertyName", "DestructuringDeclaration")

/**
 * Adds "Copy Splits" / "Paste Splits" / "Apply Splits Template" context-menu actions to the
 * transaction register, letting the user copy the split lines from one transaction (or a
 * Reminder acting as a reusable template) and apply them to another - primarily to bring
 * multi-split detail onto a downloaded/imported transaction, without retyping every split by hand.
 *
 * ELIGIBILITY - Copy ([canCopySplits], self-applied to the copy source):
 * - Source account must be BANK or CREDIT_CARD.
 * - Source transaction must have at least one split.
 * - All splits must share the source account's currency (no cross-currency splits).
 * - Source transaction's own cleared/reconciled status is not checked - any status may be copied.
 *
 * ELIGIBILITY - target-side ([isTargetEligible] - shared by Paste and Apply Splits Template):
 * - Target account must be BANK or CREDIT_CARD.
 * - Target transaction and all of its existing splits must be UNRECONCILED.
 * - All of the target's existing splits must share the target account's currency (internal
 *   consistency check, independent of any copy source - same shape as the Copy-side check).
 * - NONE of the target's existing splits may hold protected online/downloaded-match data (see
 *   [hasAnyProtectedSplit] - true if any split itself has an FI transaction ID, i.e.
 *   split.wasDownloaded(), regardless of isNew()/matchType; parent-level online/match data is
 *   deliberately NOT checked - see that function's doc comment for the reasoning) - this is a
 *   hard block, checked FIRST, before anything else, with no override. A transaction with any
 *   such split simply never offers Paste, Apply Splits Template, or Rebalance Splits at all -
 *   not a confirmation, an outright non-appearance.
 *
 * ELIGIBILITY - Paste ([canPasteSplits]): `isTargetEligible(txn)` PLUS:
 * - Target cannot be the same transaction that was copied from.
 * - Target account's currency must match the copied source's currency.
 * - Target account must have a default category set, or the paste is blocked with a message
 *   (checked inside [runPasteFlow], since it's a property of the eventual write, not eligibility).
 *
 * ELIGIBILITY - Apply Splits Template: identical ruleset to Paste, in full - `isTargetEligible(txn)`
 * PLUS currency match against whichever candidate reminder is chosen. The menu item's visibility
 * now requires `isTargetEligible(txn)` AND at least one candidate reminder whose currency matches;
 * candidates are every [Reminder] whose transaction passes [canCopySplits], searched/filtered fresh
 * each time the menu action is invoked (not cached at menu-build time).
 *
 * If any of the above conditions fails, the corresponding menu action is simply not shown - no
 * error is surfaced (see [canCopySplits] / [isTargetEligible] / [canPasteSplits] / [getActions]).
 *
 * WHAT GETS COPIED per split: category (account), amount, description, keywords/tags, check
 * number. Attachment key names are recorded (for warning purposes only - see below) but the
 * actual attached files are never copied. VAT-related split data is not yet handled (open TODO).
 * Online-download/match data (blue-dot state, match type, FI/transaction IDs) is deliberately
 * NEVER copied onto pasted splits - this is enforced, not just omitted.
 *
 * OVERWRITE CONFIRMATION: the only remaining pre-action popup (besides the allocation-mismatch
 * popup below) is a plain Yes/No "this will overwrite existing splits, continue?" prompt, shown
 * only when the target currently has more than one split. It no longer has an "online data"
 * variant - protected-split targets are excluded entirely before this point is ever reached (see
 * [isTargetEligible] above). Pasting onto a single blank ($0) placeholder split skips this prompt.
 *
 * AMOUNT MISMATCH HANDLING: if the target's current total differs from the copied splits' total,
 * the user is asked to choose one of:
 *   - Overwrite total: paste the copied amounts exactly, changing the target's overall total.
 *   - Exact amounts, remainder on a new split: keep copied amounts unchanged, put the difference
 *     on an additional new split (using the target account's default category).
 *   - Allocate by % (Hamilton's method): rescale every split to its original percentage share of
 *     the new total, distributing any rounding remainder across splits (largest-remainder method)
 *     so no single split absorbs more than a whole unit of rounding error.
 * The same mismatch handling applies identically whether the source is an ad-hoc copy or a
 * chosen Splits Template - both funnel into the same paste execution (see runPasteFlow).
 *
 * ATTACHMENTS: never pasted under any circumstance. If any copied split had attachments, an
 * informational popup fires after paste, but only when the extension's debug-messages preference is enabled.
 *
 * All paste operations replace the target's entire split set (remove-all, then re-add) and are
 * recorded as a single undoable change.
 *
 * REBALANCE SPLITS: a third, self-contained action - the source and target are the same
 * transaction. Requires isTargetEligible(txn) (same rules as Paste/Template) PLUS more than one
 * existing split. Prompts for a new total (defaulting to the current total) and an allocation
 * mode (keep each split's existing ratio, or split equally across all lines), then recomputes
 * each existing split's amount IN PLACE - unlike Paste/Template, no splits are removed or
 * created; category, description, keywords, check number, and attachments are untouched.
 * Rounding uses the same Hamilton's-method largest-remainder distribution as Paste's % option.
 * Exactly one dialog on success; no separate overwrite-confirm or mismatch popup, since there is
 * no external source to reconcile against.
 *
 * @param copyPasteEnabled Whether the "Copy Splits" / "Paste Splits" menu actions should be
 * offered. Read once by the caller (Main.getActionsForContext) from user preferences, alongside
 * every other menu-enabled flag - this class does not read preferences itself.
 * @param templateEnabled Whether the "Apply Splits Template" menu action should be offered.
 * Same sourcing as copyPasteEnabled.
 * @param templateMatchAccount Whether a candidate reminder's own account must exactly match the
 * target account. Same sourcing as copyPasteEnabled - Main.kt reads SETTING_TEMPLATE_MATCH_ACCOUNT
 * and always passes it explicitly. NOTE: this constructor parameter's default (true) does NOT
 * match Main.kt's actual wired-up default (false) - the default here only applies to
 * standalone/testing construction that skips Main.kt's wiring, same convention documented on
 * CopyRawDetailsToClipboard's copyEnabled/showEnabled parameters.
 * @param rebalanceEnabled Whether the "Rebalance Splits" menu action should be offered.
 * Same sourcing as copyPasteEnabled.
 */
class CopyPasteSplits(
  private val copyPasteEnabled:Boolean = true,
  private val templateEnabled:Boolean = true,
  private val includeSingleSplitReminders:Boolean = false,
  private val templateNameFilter:String = "",
  private val templateMatchAccount:Boolean = true,
  private val excludeExpiredReminders:Boolean = false,
  private val rebalanceEnabled:Boolean = true,
  private val alwaysConfirmTotal:Boolean = false
):ContextMenuAction {
  
  private val dialog_apply_tmplt_size = ".gui.apply_template.size"
  private val dialog_apply_tmplt_locn = ".gui.apply_template.loc"
  private val dialog_paste_mismatch_size = ".gui.paste_mismatch.size"
  private val dialog_paste_mismatch_locn =  ".gui.paste_mismatch.loc"
  private val dialog_paste_always_confirm_size = ".gui.paste_always_confirm.size"
  private val dialog_paste_always_confirm_locn = ".gui.paste_always_confirm.loc"
  
  private val string_copy_splits = "Copy Splits"
  private val string_paste_splits = "Paste Splits"
  private val string_paste_overwrite_confirm = "This will overwrite the existing splits on the selected transaction. Continue?"
  private val string_allocation_method_title_template = "{action} - Allocation Method"
  private val string_undo_redo_paste_splits = "Paste Splits"
  private val string_undo_redo_apply_template = "Apply Splits Template"
  
  private val string_opt_overwrite_total = "Change/Overwrite total to {total} (paste exact copied amounts)"
  private val string_opt_exact_new = "Exact amounts, remainder on a new split"
  private val string_opt_pct_hamilton = "Allocate by % (Hamilton's method)"
  private val string_blocked_no_default_category_template = "{action} blocked. Please set the default category for account: {acct}"
  private val string_warn_copy_splits_had_attachments = "One or more copied splits had attachments which were not pasted"
  
  private val string_source_label = "Source"
  private val string_transaction_label = "Transaction"
  private val string_source_splits_label = "Splits"
  private val string_source_total_label = "Source total"
  private val string_target_total_label = "Target total"
  private val string_current_total_label = "Current total"
  private val string_new_total_label = "New total"
  
  private val string_source_splits_heading = "Source splits"
  private val string_current_splits_heading = "Current splits"
  
  private val string_use_source_total_tooltip = "Use source total"
  private val string_reset_target_total_tooltip = "Reset to target's original total"
  private val string_reset_current_total_tooltip = "Reset to original total"
  
  private val string_hamilton_link_tooltip = "About the largest-remainder (Hamilton's) method"
  private val HAMILTON_WIKI_URL = "https://en.wikipedia.org/wiki/Largest_remainder_method"
  private val ICON_RESET_PATH = "com/moneydance/apps/md/view/gui/glyphs/reset.png"
  private val ICON_USE_VALUE_PATH = "com/moneydance/apps/md/view/gui/glyphs/horizontal-left.png"
  
  private val string_apply_splits_template = "Apply Splits Template (from Reminders)"
  private val string_apply_template_title = "Choose a Splits Template (from Reminders)"
  private val string_apply_template_no_candidates = "No suitable reminder templates were found for this transaction's account/currency."
  
  private val string_reason_not_parent = "Not a parent transaction (target cannot be a split)"
  private val string_reason_account_type = "Account type not eligible (Bank/Credit Card)"
  private val string_reason_no_splits = "No splits"
  private val string_reason_inconsistent_currency = "Inconsistent currencies between parent and splits"
  private val string_reason_protected_online_data = "Protected online bank downloaded data"
  private val string_reason_reconciled = "Reconciled/Reconciling (target must be unreconciled)"
  private val string_reason_same_as_source = "Same as copy source (cannot paste over itself)"
  private val string_reason_currency_mismatch_source = "Currency does not match copied source"
  private val string_reason_no_templates = "No matching reminder templates found"
  private val string_reason_needs_multiple_splits = "Requires more than one split"
  
  private val string_rebalance_splits = "Rebalance Splits - update total and/or ratio"
  private val string_rebalance_title = "Rebalance Splits"
  private val string_rebalance_new_total_label = "New total"
  private val string_rebalance_mode_keep_ratio = "Keep existing ratio per split"
  private val string_rebalance_mode_equal_split = "Equal split per line"
  private val string_rebalance_hamilton_note = "Rounding uses the largest-remainder method"
  private val string_undo_redo_rebalance_splits = "Rebalance Splits"
  private val dialog_rebalance_size = ".gui.rebalance_splits.size"
  private val dialog_rebalance_locn = ".gui.rebalance_splits.loc"

  // ------------------------------------------------------------------------------------------
  // stored copy snapshot - held by Main until cleared on file open/close events
  // ------------------------------------------------------------------------------------------
  
  data class CopiedSplitLine(
    val category:Account,
    val amount:Long,
    val percent:Double,
    val description:String?,
    val keywords:List<String>,
    val checkNumber:String,
    val attachmentKeys:List<String>
    //TODO (placeholder): VAT-related split data (possibly: TAG_SPLIT_CALC / TAG_SPLIT_AMOUNT / TAG_SPLIT_PAIR)
  )
  
  data class CopiedSplitsSnapshot(
    val sourceParentUUID:String,
    val sourceCurrency:CurrencyType,
    val parentTotal:Long,
    val splits:List<CopiedSplitLine>,
    val sourceDescription:String,
    val copiedAtMillis:Long = System.currentTimeMillis()
  )
  
  companion object {
    const val COPY_EXPIRY_MILLIS = 10 * 60 * 1000L
  }
  
  private sealed class PasteMismatchOption {
    object OverwriteTargetTotal:PasteMismatchOption()
    object ExactNewLine:PasteMismatchOption()
    object PercentHamilton:PasteMismatchOption()
  }
  
  /** Used only by the always-confirm popup (askPasteAlwaysConfirmChoice) - no "overwrite total"
   *  option there, since the free-text total field replaces it entirely. */
  private sealed class AllocationMode {
    object ExactNewLine:AllocationMode()
    object PercentHamilton:AllocationMode()
  }
  
  private data class PasteConfirmChoice(val newTotal:Long, val mode:AllocationMode)
  
  private sealed class RebalanceMode {
    object KeepRatio:RebalanceMode()
    object EqualSplit:RebalanceMode()
  }
  
  private data class RebalanceChoice(val newTotal:Long, val mode:RebalanceMode)
  
  // ------------------------------------------------------------------------------------------
  // menu construction
  // ------------------------------------------------------------------------------------------
  
  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    val actions = mutableListOf<Action>()
    
    // selected item must always be exactly one Parent txn - no resolving from a split row
    if (listTxns.size != 1) return actions
    val txn = listTxns.first() as? ParentTxn
    if (txn == null) {
      logBlockedIfDebug(string_copy_splits, null, string_reason_not_parent)
      return actions
    }
    
    if (copyPasteEnabled) {
      val copyReason = copyEligibilityReason(txn)
      if (copyReason == null) {
        actions += addAction(label = string_copy_splits, cmd = "copy_splits") { copySplits(txn) }
      } else {
        logBlockedIfDebug(string_copy_splits, txn, copyReason)
      }
      
      val copy = Main.copiedSplits
      if (copy != null) {
        val pasteReason = pasteEligibilityReason(txn, copy)
        if (pasteReason == null) {
          actions += addAction(label = string_paste_splits, cmd = "paste_splits") { pasteSplits(menuContext, txn) }
        } else {
          logBlockedIfDebug(string_paste_splits, txn, pasteReason)
        }
      }
    }
    
    // Apply Splits Template: full target-side eligibility (isTargetEligible), same as Paste,
    // independent of whether an ad-hoc copy is currently held. The menu item only appears if at
    // least one candidate reminder currency-matches this target. Candidates are re-searched at
    // click time regardless.
    if (templateEnabled) {
      val targetReason = targetEligibilityReason(txn)
      if (targetReason == null) {
        if (findTemplateCandidates(txn.account).isNotEmpty()) {
          actions += addAction(label = string_apply_splits_template, cmd = "apply_splits_template") {
            applySplitsTemplate(menuContext, txn)
          }
        } else {
          logBlockedIfDebug(string_apply_splits_template, txn, string_reason_no_templates)
        }
      } else {
        logBlockedIfDebug(string_apply_splits_template, txn, targetReason)
      }
    }
    
    // Rebalance Splits: same target-side eligibility as Paste/Template (isTargetEligible), self-
    // applied - the txn is both source and target. Additionally requires more than one split;
    // single-split txns never show this option.
    if (rebalanceEnabled) {
      val targetReason = targetEligibilityReason(txn)
      if (targetReason == null) {
        if (txn.allSplits.size > 1) {
          actions += addAction(label = string_rebalance_splits, cmd = "rebalance_splits") {
            rebalanceSplits(menuContext, txn)
          }
        } else {
          logBlockedIfDebug(string_rebalance_splits, txn, string_reason_needs_multiple_splits)
        }
      } else {
        logBlockedIfDebug(string_rebalance_splits, txn, targetReason)
      }
    }
    
    return actions
  }
  
  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }
  
  // ------------------------------------------------------------------------------------------
  // eligibility rules - evaluated both at menu-build time and again at click time
  // ------------------------------------------------------------------------------------------

  private fun isEligibleAccountType(acct:Account):Boolean =
    acct.getAccountType() == Account.AccountType.BANK || acct.getAccountType() == Account.AccountType.CREDIT_CARD
  
  /** Every existing split's currency matches the parent account's currency - same shape as the
   *  copy-source consistency check in canCopySplits, applied here to a paste/template TARGET. */
  private fun hasCurrencyConsistentSplits(txn:ParentTxn):Boolean {
    val parentCurr = txn.account.currencyType
    return txn.allSplits.all { it.account.currencyType == parentCurr }
  }
  
  private fun copyEligibilityReason(txn:ParentTxn):String? {
    // NOTE: copy source can be in any cleared state - unreconciled check applies to paste target only
    if (!isEligibleAccountType(txn.account)) return string_reason_account_type
    val splits = txn.allSplits
    if (splits.isEmpty()) return string_reason_no_splits
    val parentCurr = txn.account.currencyType
    if (splits.any { it.account.currencyType != parentCurr }) return string_reason_inconsistent_currency
    return null
  }
  
  private fun canCopySplits(txn:ParentTxn):Boolean = copyEligibilityReason(txn) == null
  
  /**
   * Shared target-side eligibility for Paste, Apply Splits Template, and Rebalance Splits (which
   * applies it to itself, being both source and target). Protected-split check is evaluated
   * FIRST and unconditionally - a transaction with any protected split never qualifies as a
   * target for any of these three actions, full stop, no override.
   */
  private fun targetEligibilityReason(txn:ParentTxn):String? {
    if (hasAnyProtectedSplit(txn)) return string_reason_protected_online_data
    if (!isEligibleAccountType(txn.account)) return string_reason_account_type
    if (!isAllUnreconciled(txn)) return string_reason_reconciled
    if (!hasCurrencyConsistentSplits(txn)) return string_reason_inconsistent_currency
    return null
  }
  
  private fun isTargetEligible(txn:ParentTxn):Boolean = targetEligibilityReason(txn) == null
  
  private fun pasteEligibilityReason(txn:ParentTxn, copy:CopiedSplitsSnapshot):String? {
    if (txn.UUID == copy.sourceParentUUID) return string_reason_same_as_source     // block paste into copy source
    targetEligibilityReason(txn)?.let { return it }
    if (txn.account.currencyType != copy.sourceCurrency) return string_reason_currency_mismatch_source
    return null
  }
  
  private fun canPasteSplits(txn:ParentTxn, copy:CopiedSplitsSnapshot):Boolean = pasteEligibilityReason(txn, copy) == null
  
  /** Logs why a menu action was NOT offered, gated by the extension's own "Enable debug
   *  messages" config checkbox (debugMenuEnabled) - NOT Util.logConsole's Main.DEBUG launch-flag
   *  gate, which is a different, unrelated debug switch. txn may be null for the "not a parent
   *  transaction" case, where no transaction details are available yet to describe. */
  private fun logBlockedIfDebug(actionLabel:String, txn:ParentTxn?, reason:String) {
    if (extensionContext?.debugMenuEnabled != true) return
    val desc = if (txn != null) {
      val dec = mdGUI.preferences.decimalChar
      val totalStr = txn.account.currencyType.formatFancy(txn.value, dec)
      " for '${txn.description}' (${txn.dateInt}, $totalStr, ${txn.allSplits.size} splits)"
    } else ""
    Util.logConsole(false, "$actionLabel blocked$desc: $reason")
  }
  
  // ------------------------------------------------------------------------------------------
  // copy
  // ------------------------------------------------------------------------------------------
  
  private fun copySplits(txn:ParentTxn) {
    if (!canCopySplits(txn)) return   // re-validate at click time
    
    val parentCurr = txn.account.currencyType
    val splits = txn.allSplits
    val total = txn.value
    
    // NOTE: it's split.parentAmount (not split.value, not split.amount) that sums to the parent
    // total. split.value is the split's own actual value; store that for reconstruction.
    //require(total == splits.sumOf { it.parentAmount }) { "Parent total must equal sum of its splits" }
    
    val copiedLines = splits.map { split ->
      val pct = if (total != 0L) -split.value.toDouble() / total.toDouble() else 0.0
      CopiedSplitLine(
        category = split.account,
        amount = split.value,
        percent = pct,
        description = split.description,
        keywords = split.keywords,
        checkNumber = split.checkNumber,
        attachmentKeys = split.attachmentKeys
      )
      //TODO (placeholder): check for other data worth copying per split - e.g. VAT, Online Download data
    }
    
    Main.copiedSplits = CopiedSplitsSnapshot(
      sourceParentUUID = txn.UUID,
      sourceCurrency = parentCurr,
      parentTotal = total,
      splits = copiedLines,
      sourceDescription = txn.description
    )
    if (extensionContext?.debugMenuEnabled == true || DEBUG) {
      val dec = mdGUI.preferences.decimalChar
      val totalStr = parentCurr.formatFancy(total, dec)
      Util.logConsole(
        "CopyPasteSplits: Copy Splits from '${txn.description}' (${txn.dateInt}) on parent txn '${txn.UUID}': " +
        "total $totalStr, splits ${copiedLines.size}"
      )
    }
  }
  
  // ------------------------------------------------------------------------------------------
  // apply splits template (reminder-as-preset)
  // ------------------------------------------------------------------------------------------
  
  /**
   * Search all reminders and filter to those whose transaction is a valid copy source (same
   * rules as canCopySplits) and whose currency matches the paste target. Also applies three
   * user-configurable filters: same-account matching (default ON - reminder's own account must
   * be the exact same account as the target, not just same currency), single-split reminders can
   * be excluded (default excluded), and an optional name filter restricts by reminder description
   * (case-insensitive, substring match).
   */
  private fun findTemplateCandidates(targetAccount:Account):List<Reminder> {
    val book = Main.mdMain?.currentAccountBook ?: return emptyList()
    val nameFilter = templateNameFilter.trim()
    val targetCurrency = targetAccount.currencyType
    
    return book.reminders.allReminders.filter { reminder ->
      val templateTxn = reminder.transaction
      reminder.getReminderType() == Reminder.Type.TRANSACTION &&
      canCopySplits(templateTxn) &&
      templateTxn.account.currencyType == targetCurrency &&
      (!templateMatchAccount || templateTxn.account == targetAccount) &&
      templateTxn.value == templateTxn.allSplits.sumOf { it.parentAmount } &&
      (includeSingleSplitReminders || templateTxn.allSplits.size > 1) &&
      (!excludeExpiredReminders || !reminder.isInactiveOrExpired()) &&
      (nameFilter.isEmpty() || reminder.description.trim().contains(nameFilter, ignoreCase = true))
    }
  }
  
  
  /**
   * Same derivation as copySplits(), but fails soft (returns null) instead of crashing, so one
   * malformed reminder can't take down the template picker for every other candidate.
   */
  private fun buildSnapshotFromTemplate(txn:ParentTxn, reminderDescription:String):CopiedSplitsSnapshot? {
    if (!canCopySplits(txn)) return null
    val parentCurr = txn.account.currencyType
    val splits = txn.allSplits
    val total = txn.value
    if (total != splits.sumOf { it.parentAmount }) return null
    
    val copiedLines = splits.map { split ->
      val pct = if (total != 0L) -split.value.toDouble() / total.toDouble() else 0.0
      CopiedSplitLine(
        category = split.account,
        amount = split.value,
        percent = pct,
        description = split.description,
        keywords = split.keywords,
        checkNumber = split.checkNumber,
        attachmentKeys = split.attachmentKeys
      )
    }
    
    return CopiedSplitsSnapshot(
      sourceParentUUID = txn.UUID,
      sourceCurrency = parentCurr,
      parentTotal = total,
      splits = copiedLines,
      sourceDescription = reminderDescription
    )
  }
  
  private fun applySplitsTemplate(menuContext:MDActionContext, txn:ParentTxn) {
    val candidates = findTemplateCandidates(txn.account)
    if (candidates.isEmpty()) {
      mdGUI.showInfoMessage(string_apply_template_no_candidates)
      return
    }
    
    val chosen = pickReminder(
      mdGUI, menuContext.component, string_apply_template_title, candidates,
      sizeKey = Main.EXTN_ID + dialog_apply_tmplt_size,
      locationKey = Main.EXTN_ID + dialog_apply_tmplt_locn,
      showSplitPercentages = true
    ) ?: return
    val copy = buildSnapshotFromTemplate(chosen.transaction, chosen.description) ?: return
    if (!canPasteSplits(txn, copy)) return   // re-validate at click time
    
    runPasteFlow(menuContext, txn, copy, string_undo_redo_apply_template)
  }
  
  // ------------------------------------------------------------------------------------------
  // paste
  // ------------------------------------------------------------------------------------------
  
  private fun pasteSplits(menuContext:MDActionContext, txn:ParentTxn) {
    val copy = Main.copiedSplits ?: return
    if (!canPasteSplits(txn, copy)) return   // re-validate at click time
    runPasteFlow(menuContext, txn, copy, string_undo_redo_paste_splits)
  }
  
  /**
   * Shared paste execution, used by both the ad-hoc Paste Splits action and Apply Splits
   * Template. Caller must have already validated canPasteSplits(txn, copy) - which includes
   * isTargetEligible(txn), so by this point the target is guaranteed to hold no protected splits.
   */
  private fun runPasteFlow(menuContext:MDActionContext, txn:ParentTxn, copy:CopiedSplitsSnapshot, undoName:String) {
    val existingSplits = txn.allSplits
    val targetTotal = txn.value
    //require(targetTotal == existingSplits.sumOf { it.parentAmount }) { "Target parent total must equal sum of its splits" }
    
    val isBlankPlaceholderTarget = existingSplits.size == 1 && targetTotal == 0L
    
    // the only remaining pre-action popup: plain overwrite confirm when target has >1 split.
    // No "protected data" variant needed anymore - protected targets are excluded entirely by
    // isTargetEligible() before this function is ever reached.
    if (!isBlankPlaceholderTarget && existingSplits.size > 1) {
      if (!mdGUI.askQuestion(string_paste_overwrite_confirm)) return
    }
    
    // default-category check only happens here, right where it's actually needed - the ONLY
    // allocation path that creates a new remainder split (and therefore needs a default
    // category to assign it to). Every other path (fast path, Overwrite total, % Hamilton) never
    // touches defaultCategory, so they must not be blocked by its absence.
    fun requireDefaultCategoryOrBlock():Boolean {
      if (txn.account.defaultCategory != null) return true
      mdGUI.showInfoMessage(
        string_blocked_no_default_category_template
          .replace("{action}", undoName)
          .replace("{acct}", txn.account.getAccountName())
      )
      return false
    }
    
    // dialog title reflects whichever action actually triggered this flow (Paste Splits or
    // Apply Splits Template), rather than always saying "Paste Splits"
    val allocationDialogTitle = string_allocation_method_title_template.replace("{action}", undoName)
    
    val newLines:List<CopiedSplitLine> =
      if (alwaysConfirmTotal) {
        // no fast path when this setting is on - always show the popup, regardless of whether
        // totals happen to match. Overwrite-confirm above still only fires when existingSplits.size > 1.
        val choice = askPasteAlwaysConfirmChoice(menuContext, txn, copy, targetTotal, allocationDialogTitle) ?: return
        if (choice.newTotal == copy.parentTotal) {
          copy.splits
        } else {
          when (choice.mode) {
            is AllocationMode.ExactNewLine -> {
              if (!requireDefaultCategoryOrBlock()) return
              allocateExactRemainderOnNewLine(copy.splits, choice.newTotal, txn)
            }
            is AllocationMode.PercentHamilton -> allocatePercentHamilton(copy.splits, choice.newTotal)
          }
        }
      } else if (isBlankPlaceholderTarget || targetTotal == copy.parentTotal) {
        copy.splits
      } else {

        when (askPasteMismatchOption(menuContext, copy, targetTotal, allocationDialogTitle) ?: return) {
          is PasteMismatchOption.OverwriteTargetTotal -> copy.splits
          is PasteMismatchOption.ExactNewLine -> {
            if (!requireDefaultCategoryOrBlock()) return
            allocateExactRemainderOnNewLine(copy.splits, targetTotal, txn)
          }
          is PasteMismatchOption.PercentHamilton -> allocatePercentHamilton(copy.splits, targetTotal)
        }
      }
    
    val change = UndoableChange()
    change.beginModification(txn)   // snapshot "before" state - target already exists/synced
    
    applyPastedSplits(txn, newLines)
    
    pasteSplitsRecordChange(change, txn, undoName)

    if (extensionContext?.debugMenuEnabled == true || DEBUG) {
      val dec = mdGUI.preferences.decimalChar
      val currency = copy.sourceCurrency
      val sourceTotalStr = currency.formatFancy(copy.parentTotal, dec)
      val newTotalStr = currency.formatFancy(newLines.sumOf { -it.amount }, dec)
      Util.logConsole(
        "CopyPasteSplits: $undoName from '${copy.sourceDescription}' onto '${txn.description}' (${txn.dateInt}) on parent txn '${txn.UUID}': " +
        "source total $sourceTotalStr, source splits ${copy.splits.size} -> new total $newTotalStr, new splits ${newLines.size}"
      )
    }
    
    val droppedAttachments = newLines.any { it.attachmentKeys.isNotEmpty() }
    if (droppedAttachments && extensionContext?.debugMenuEnabled == true) {
      mdGUI.showInfoMessage(string_warn_copy_splits_had_attachments)
    }
  }
  
  // ------------------------------------------------------------------------------------------
  // allocation when target total != copy source total
  // ------------------------------------------------------------------------------------------
  
  private fun preserveSign(originalAmount:Long, computedAmount:Long):Long =
    if (originalAmount < 0) -abs(computedAmount) else abs(computedAmount)
  
  private fun allocateExactRemainderOnNewLine(
    sourceLines:List<CopiedSplitLine>,
    targetTotal:Long,
    target:ParentTxn
  ):List<CopiedSplitLine> {
    if (sourceLines.size == 1) {
      val only = sourceLines.first()
      return listOf(only.copy(amount = preserveSign(only.amount, targetTotal), percent = 1.0))
    }
    
    val remainder = -targetTotal - sourceLines.sumOf { it.amount }
    val extraPct = if (targetTotal != 0L) -remainder.toDouble() / targetTotal.toDouble() else 0.0

    val newLines = sourceLines.map { line ->
      val pct = if (targetTotal != 0L) -line.amount.toDouble() / targetTotal.toDouble() else 0.0
      line.copy(percent = pct)
    }.toMutableList()
    
    newLines += CopiedSplitLine(
      category = target.account.defaultCategory!!,  // null defaultCategory condition already checked / blocked earlier
      amount = remainder,
      percent = extraPct,
      description = null,
      keywords = emptyList(),
      checkNumber = "",
      attachmentKeys = emptyList()
    )
    return newLines
  }
  
  private fun allocatePercentHamilton(
    sourceLines:List<CopiedSplitLine>,
    targetTotal:Long
  ):List<CopiedSplitLine> {
    if (sourceLines.size == 1) {
      val only = sourceLines.first()
      return listOf(only.copy(amount = preserveSign(only.amount, targetTotal), percent = 1.0))
    }
    
    val exact = sourceLines.map { -it.percent * targetTotal }
    val floored = exact.map { truncateTowardZero(it) }
    var shortfall = -targetTotal - floored.sum()
    
    val order = exact.indices.sortedByDescending { abs(exact[it] - floored[it]) }
    val finalAmounts = floored.toMutableList()
    val step = if (shortfall > 0) 1L else -1L
    var i = 0
    while (shortfall != 0L && i < order.size) {
      finalAmounts[order[i]] += step
      shortfall -= step
      i++
    }
    
    return sourceLines.zip(finalAmounts) { line, amt ->
      val pct = if (targetTotal != 0L) -amt.toDouble() / targetTotal.toDouble() else 0.0
      line.copy(amount = amt, percent = pct)
    }
  }
  
  private fun truncateTowardZero(d:Double):Long =
    if (d < 0) kotlin.math.ceil(d).toLong() else kotlin.math.floor(d).toLong()
  
  // ------------------------------------------------------------------------------------------
  // reusable split-summary display (used by Rebalance, Paste mismatch/always-confirm popups)
  // ------------------------------------------------------------------------------------------
  
  /**
   * "Category Name: £amount (nn.n%)" per line. percent is used as-stored (already the natural
   * share of the total, confirmed to sum to 100% across all lines by the same sign algebra used
   * throughout this class) - no additional sign flip needed. Individual percentages can exceed
   * 100% or be negative when splits have mixed signs (e.g. a gross income split partly offset by
   * expense-side splits) - this is mathematically correct, not a display bug.
   */
  private fun formatSplitSummaryLine(categoryName:String, amount:Long, percent:Double, currency:CurrencyType, dec:Char):String {
    val amtStr = currency.formatFancy(amount, dec)
    val pctStr = String.format("%.1f", percent * 100.0)
    return "$categoryName: $amtStr ($pctStr%)"
  }
  
  private fun splitSummaryLinesFromCopied(lines:List<CopiedSplitLine>, currency:CurrencyType, dec:Char):List<String> =
    lines.map { formatSplitSummaryLine(it.category.getAccountName(), it.amount, it.percent, currency, dec) }
  
  private fun splitSummaryLinesFromExisting(splits:List<SplitTxn>, total:Long, currency:CurrencyType, dec:Char):List<String> =
    splits.map { split ->
      val pct = if (total != 0L) -split.value.toDouble() / total.toDouble() else 0.0
      formatSplitSummaryLine(split.account.getAccountName(), split.value, pct, currency, dec)
    }
  
  /** Read-only, scrollable, height-constrained list of split summary lines - shows up to 6 rows
   *  before scrolling, so a long split list can't blow out the popup's size. */
  private fun buildSplitSummaryList(summaryLines:List<String>):JScrollPane {
    val listModel = DefaultListModel<String>()
    summaryLines.forEach { listModel.addElement(it) }
    val list = JList(listModel)
    list.isFocusable = false
    list.selectionModel.selectionMode = ListSelectionModel.SINGLE_SELECTION
    list.visibleRowCount = minOf(summaryLines.size, 6).coerceAtLeast(1)
    return JScrollPane(list, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_NEVER)
  }
  
  /**
   * Builds the bottom-of-dialog info block: a separator, an intro label, the source/current
   * description + split count + total, and the scrollable split summary list. Used at the
   * bottom of all three popups (askPasteMismatchOption, askPasteAlwaysConfirmChoice,
   * askRebalanceChoice) - options/fields come first in each dialog, this block comes last.
   *
   * @param extraLine Optional additional "Label: value" line shown after the total (e.g. the
   * target's total on the mismatch popup, which has two distinct totals to show).
   */
  private fun buildBottomInfoBlock(
    heading:String,
    descriptionLabel:String,
    description:String,
    splitCount:Int,
    totalLabel:String,
    total:Long,
    currency:CurrencyType,
    summaryLines:List<String>,
    extraLine:Pair<String, Long>? = null
  ):JPanel {
    val dec = mdGUI.preferences.decimalChar
    val totalStr = currency.formatFancy(total, dec)
    
    val panel = JPanel(GridBagLayout())
    var y = 0
    panel.add(JSeparator(), GridC.getc().xy(0, y++).colspan(2).wx(1f).fillboth().insets(10, 0, 10, 0))
    panel.add(
      JLabel(heading).also { it.font = it.font.deriveFont(java.awt.Font.BOLD) },
      GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 8, 0)
    )
    panel.add(JLabel("$descriptionLabel: $description"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(JLabel("$string_source_splits_label: $splitCount"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    val totalBottomInset = if (extraLine != null) 4 else 8
    panel.add(JLabel("$totalLabel: $totalStr"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, totalBottomInset, 0))
    if (extraLine != null) {
      val extraStr = currency.formatFancy(extraLine.second, dec)
      panel.add(JLabel("${extraLine.first}: $extraStr"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 8, 0))
    }
    panel.add(buildSplitSummaryList(summaryLines), GridC.getc().xy(0, y++).colspan(2).wx(1f).fillboth())
    return panel
  }
  
  /** Small button that sets a JCurrencyField to a given value on click - real Moneydance-bundled
   *  icon (confirmed resource paths, see ICON_RESET_PATH/ICON_USE_VALUE_PATH), falling back to
   *  a plain text glyph if the icon can't be loaded for any reason. */
  private fun buildUseValueButton(tooltip:String, iconPath:String, fallbackText:String, field:JCurrencyField, value:Long):JButton {
    val icon = Util.loadIcon(iconPath)
    val btn = if (icon != null) JButton(icon) else JButton(fallbackText)
    btn.toolTipText = tooltip
    btn.margin = Insets(1, 4, 1, 4)
    btn.addActionListener { field.value = value }
    return btn
  }
  
  /** Small clickable "(?)" label that opens the Hamilton's-method Wikipedia page. */
  private fun buildHamiltonHelpLink():JLabel {
    val link = JLabel("(?)")
    link.foreground = Util.blue
    link.cursor = Cursor(Cursor.HAND_CURSOR)
    link.toolTipText = string_hamilton_link_tooltip
    link.addMouseListener(object:MouseAdapter() {
      override fun mouseClicked(e:MouseEvent) {
        mdGUI.showInternetURL(HAMILTON_WIKI_URL)
      }
    })
    return link
  }
  
  
  
  // ------------------------------------------------------------------------------------------
  // applying the pasted splits
  // ------------------------------------------------------------------------------------------
  
  private fun applyPastedSplits(target:ParentTxn, lines:List<CopiedSplitLine>) {
    // remove existing splits first
    val existing = target.allSplits.toList()
    for (split in existing) {
      target.removeSplit(split)
    }
    
    for (line in lines) {
      // makeSplitTxn(parentTxn, parentAmount, splitAmount, rate, ...) internally sets
      // splitAmount field = splitAmount_param, parentAmount field = -parentAmount_param.
      // For same-currency splits, original.parentAmount == -original.value, so both args here
      // equal line.amount (== original split.value) to reconstruct both fields correctly.
      val newSplit = SplitTxn.makeSplitTxn(
        target, line.amount, line.amount, 1.0, line.category, line.description, -1,
        AbstractTxn.ClearedStatus.UNRECONCILED.code
      )
      if (line.keywords.isNotEmpty()) {
        newSplit.keywords = line.keywords
      }
      if (line.checkNumber.isNotEmpty()) {
        newSplit.checkNumber = line.checkNumber
      }
      //TODO - placeholder for attachmentKeys (not pasting at this time)
      target.addSplit(newSplit)
    }
  }
  
  private fun pasteSplitsRecordChange(change:UndoableChange, target:ParentTxn, undoName:String) {
    change.setNameCompat(undoName)
    change.finishModification(modifiedItem = target)
    mdGUI.undoManager?.recordChange(change)
  }
  
  // ------------------------------------------------------------------------------------------
  // rebalance splits (self-source: recompute existing splits' amounts, in place, no import)
  // ------------------------------------------------------------------------------------------
  
  /**
   * Recomputes the amount of every existing split on txn, in place - no splits are removed or
   * created (unlike Paste/Apply Template, which always remove-all/recreate). Category,
   * description, keywords, check number, and attachments on each split are left untouched.
   *
   * Re-validates isTargetEligible(txn) && txn.allSplits.size > 1 at click time, same "check
   * again before acting" pattern used by pasteSplits()/applySplitsTemplate().
   */
  private fun rebalanceSplits(menuContext:MDActionContext, txn:ParentTxn) {
    if (!isTargetEligible(txn) || txn.allSplits.size <= 1) return   // re-validate at click time
    
    val existingSplits = txn.allSplits
    val currentTotal = txn.value
    //require(currentTotal == existingSplits.sumOf { it.parentAmount }) { "Parent total must equal sum of its splits" }
    
    val choice = askRebalanceChoice(menuContext, txn, currentTotal) ?: return
    
    // percent uses the SAME sign convention as copySplits()/buildSnapshotFromTemplate(): pct = -value/total.
    // KeepRatio's percent naturally carries each split's original sign through, so ratio and sign
    // preservation both fall out of this automatically - no separate sign-preservation step needed.
    val percents:List<Double> = when (choice.mode) {
      is RebalanceMode.KeepRatio ->
        existingSplits.map { split -> if (currentTotal != 0L) -split.value.toDouble() / currentTotal.toDouble() else 0.0 }
      is RebalanceMode.EqualSplit ->
        // NOTE (flagged, not silently decided): equal CONTRIBUTION per line, not equal magnitude
        // with sign preserved - those two are mathematically incompatible whenever the existing
        // splits have mixed signs (e.g. one income-side split alongside one expense-side split,
        // as in the Gem Lettings example that surfaced this). Every line gets the SAME sign here;
        // a split whose original sign differs from the others can flip. Confirm this is the
        // intended meaning of "Equal split" before relying on it for mixed-sign transactions.
        List(existingSplits.size) { 1.0 / existingSplits.size }
    }
    
    val newAmounts = allocatePercentHamiltonValues(percents, choice.newTotal)
    
    val change = UndoableChange()
    change.beginModification(txn)   // snapshot "before" state - target already exists/synced
    
    for ((split, newAmount) in existingSplits.zip(newAmounts)) {
      // update in place - amount only, category/description/keywords/checkNumber/attachments untouched
      split.setAmount(newAmount, newAmount)
    }
    
    change.setNameCompat(string_undo_redo_rebalance_splits)
    change.finishModification(modifiedItem = txn)
    mdGUI.undoManager?.recordChange(change)
    
    if (extensionContext?.debugMenuEnabled == true || DEBUG) {
      val dec = mdGUI.preferences.decimalChar
      val currency = txn.account.currencyType
      val sourceTotalStr = currency.formatFancy(currentTotal, dec)
      val newTotalStr = currency.formatFancy(choice.newTotal, dec)
      // NOTE: "new splits" count always equals "source splits" count - Rebalance updates amounts
      // in place and never adds/removes splits. Logged anyway for symmetry/clarity.
      Util.logConsole(
        "CopyPasteSplits: Rebalance Splits for '${txn.description}' (${txn.dateInt}) on parent txn '${txn.UUID}': " +
        "source total $sourceTotalStr, source splits ${existingSplits.size} -> new total $newTotalStr, new splits ${newAmounts.size}, mode=${choice.mode}"
      )
    }

  }
  
  /**
   * Generalized Hamilton's-method largest-remainder allocation, same math as
   * allocatePercentHamilton() (including its -percent*targetTotal negation, required by the
   * split.parentAmount == -split.value sign relation), just decoupled from CopiedSplitLine so it
   * can be reused for Rebalance's raw percent list. Returns split.value-convention amounts whose
   * sum is guaranteed to be -targetTotal, so that split.setAmount(v, v) on each produces a
   * parentAmount-field sum of exactly targetTotal.
   */
  private fun allocatePercentHamiltonValues(percents:List<Double>, targetTotal:Long):List<Long> {
    if (percents.size == 1) return listOf(-targetTotal)
    
    val exact = percents.map { -it * targetTotal }
    val floored = exact.map { truncateTowardZero(it) }
    var shortfall = -targetTotal - floored.sum()
    
    val order = exact.indices.sortedByDescending { abs(exact[it] - floored[it]) }
    val finalAmounts = floored.toMutableList()
    val step = if (shortfall > 0) 1L else -1L
    var i = 0
    while (shortfall != 0L && i < order.size) {
      finalAmounts[order[i]] += step
      shortfall -= step
      i++
    }
    return finalAmounts
  }
  
  
  private fun askRebalanceChoice(menuContext:MDActionContext, txn:ParentTxn, currentTotal:Long):RebalanceChoice? {
    val dec = mdGUI.preferences.decimalChar
    val com = if (dec == ',') '.' else ','
    val currency = txn.account.currencyType
    val currencyTable = txn.account.book.currencies
    
    val newTotalField = JCurrencyField(currency, currencyTable, dec, com).also {
      it.value = currentTotal
    }
    val resetButton = buildUseValueButton(string_reset_current_total_tooltip, ICON_RESET_PATH, "\u21ba", newTotalField, currentTotal)
    
    val keepRatioRadio = JRadioButton(string_rebalance_mode_keep_ratio)
    val equalSplitRadio = JRadioButton(string_rebalance_mode_equal_split)
    val group = ButtonGroup()
    group.add(keepRatioRadio)
    group.add(equalSplitRadio)
    keepRatioRadio.isSelected = true   // default: keep existing ratio
    
    val fieldRow = JPanel(GridBagLayout())
    fieldRow.add(newTotalField, GridC.getc().xy(0, 0))
    fieldRow.add(resetButton, GridC.getc().xy(1, 0).insets(0, 4, 0, 0))
    
    val panel = JPanel(GridBagLayout())
    panel.border = EmptyBorder(16, 16, 16, 16)
    
    var y = 0
    panel.add(JLabel(string_rebalance_new_total_label), GridC.getc().xy(0, y).label())
    panel.add(fieldRow, GridC.getc().xy(1, y++).wx(1f).field())
    panel.add(keepRatioRadio, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(equalSplitRadio, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    
    val hamiltonNote = JPanel(GridBagLayout())
    hamiltonNote.add(JLabel(string_rebalance_hamilton_note), GridC.getc().xy(0, 0).west())
    hamiltonNote.add(buildHamiltonHelpLink(), GridC.getc().xy(1, 0).insets(0, 4, 0, 0))
    panel.add(hamiltonNote, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    
    panel.add(
      buildBottomInfoBlock(
        heading = string_current_splits_heading,
        descriptionLabel = string_transaction_label,
        description = txn.description,
        splitCount = txn.allSplits.size,
        totalLabel = string_current_total_label,
        total = currentTotal,
        currency = currency,
        summaryLines = splitSummaryLinesFromExisting(txn.allSplits, currentTotal, currency, dec)
      ),
      GridC.getc().xy(0, y++).colspan(2).wx(1f).fillboth()
    )
    
    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, string_rebalance_title, OKButtonPanel.QUESTION_OK_CANCEL,
      focusComponent = newTotalField,
      sizeKey = Main.EXTN_ID + dialog_rebalance_size,
      locationKey = Main.EXTN_ID + dialog_rebalance_locn
    )
    win.setEscapeKeyCancels(true)
    
    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return null
    
    val newTotal = newTotalField.value
    val mode:RebalanceMode = if (equalSplitRadio.isSelected) RebalanceMode.EqualSplit else RebalanceMode.KeepRatio
    return RebalanceChoice(newTotal = newTotal, mode = mode)
  }
  
  // ------------------------------------------------------------------------------------------
  // remainder-option popup
  // ------------------------------------------------------------------------------------------
  
  private fun askPasteMismatchOption(menuContext:MDActionContext, copy:CopiedSplitsSnapshot, targetTotal:Long, dialogTitle:String):PasteMismatchOption? {
    val dec = mdGUI.preferences.decimalChar
    val formattedTotal = copy.sourceCurrency.formatFancy(copy.parentTotal, dec)
    
    val options:List<Pair<PasteMismatchOption, String>> = listOf(
      PasteMismatchOption.OverwriteTargetTotal to string_opt_overwrite_total.replace("{total}", formattedTotal),
      PasteMismatchOption.ExactNewLine to string_opt_exact_new,
      PasteMismatchOption.PercentHamilton to string_opt_pct_hamilton
    )
    
    val group = ButtonGroup()
    val panel = JPanel(GridBagLayout())
    panel.border = EmptyBorder(16, 16, 16, 16)
    
    var y = 0
    val radios = options.map { (option, label) ->
      val rb = JRadioButton(label)
      group.add(rb)
      if (option is PasteMismatchOption.PercentHamilton) {
        val row = JPanel(GridBagLayout())
        row.add(rb, GridC.getc().xy(0, 0))
        row.add(buildHamiltonHelpLink(), GridC.getc().xy(1, 0).insets(0, 4, 0, 0))
        panel.add(row, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
      } else {
        panel.add(rb, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
      }
      option to rb
    }
    radios.first().second.isSelected = true   // default: overwrite target total
    
    panel.add(
      buildBottomInfoBlock(
        heading = string_source_splits_heading,
        descriptionLabel = string_source_label,
        description = copy.sourceDescription,
        splitCount = copy.splits.size,
        totalLabel = string_source_total_label,
        total = copy.parentTotal,
        currency = copy.sourceCurrency,
        summaryLines = splitSummaryLinesFromCopied(copy.splits, copy.sourceCurrency, dec),
        extraLine = string_target_total_label to targetTotal
      ),
      GridC.getc().xy(0, y++).colspan(2).wx(1f).fillboth()
    )
    
    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, dialogTitle, OKButtonPanel.QUESTION_OK_CANCEL,
      sizeKey = Main.EXTN_ID + dialog_paste_mismatch_size,
      locationKey = Main.EXTN_ID + dialog_paste_mismatch_locn
    )
    win.setEscapeKeyCancels(true)

    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return null
    
    return radios.firstOrNull { it.second.isSelected }?.first
  }
  
  /**
   * Shown instead of askPasteMismatchOption() when the "always confirm total when pasting
   * splits" preference is on. No fast path - this fires every time, even when totals already
   * match. First field is the target's CURRENT total, pre-filled but editable to any value.
   * No "overwrite total" option here - typing the copy's total into the field IS that option.
   */
  private fun askPasteAlwaysConfirmChoice(menuContext:MDActionContext, txn:ParentTxn, copy:CopiedSplitsSnapshot, targetCurrentTotal:Long, dialogTitle:String):PasteConfirmChoice? {
    val dec = mdGUI.preferences.decimalChar
    val currency = copy.sourceCurrency
    val com = if (dec == ',') '.' else ','
    val currencyTable = txn.account.book.currencies
    
    val newTotalField = JCurrencyField(currency, currencyTable, dec, com).also {
      it.value = targetCurrentTotal
    }
    val useSourceButton = buildUseValueButton(string_use_source_total_tooltip, ICON_USE_VALUE_PATH, "\u2190", newTotalField, copy.parentTotal)
    val resetButton = buildUseValueButton(string_reset_target_total_tooltip, ICON_RESET_PATH, "\u21ba", newTotalField, targetCurrentTotal)
    
    val exactRadio = JRadioButton(string_opt_exact_new)
    val hamiltonRadio = JRadioButton(string_opt_pct_hamilton)
    val group = ButtonGroup()
    group.add(exactRadio)
    group.add(hamiltonRadio)
    exactRadio.isSelected = true
    
    val fieldRow = JPanel(GridBagLayout())
    fieldRow.add(newTotalField, GridC.getc().xy(0, 0))
    fieldRow.add(useSourceButton, GridC.getc().xy(1, 0).insets(0, 4, 0, 0))
    fieldRow.add(resetButton, GridC.getc().xy(2, 0).insets(0, 4, 0, 0))
    
    val hamiltonRow = JPanel(GridBagLayout())
    hamiltonRow.add(hamiltonRadio, GridC.getc().xy(0, 0))
    hamiltonRow.add(buildHamiltonHelpLink(), GridC.getc().xy(1, 0).insets(0, 4, 0, 0))
    
    val panel = JPanel(GridBagLayout())
    panel.border = EmptyBorder(16, 16, 16, 16)
    
    var y = 0
    panel.add(JLabel(string_new_total_label), GridC.getc().xy(0, y).label())
    panel.add(fieldRow, GridC.getc().xy(1, y++).wx(1f).field())
    panel.add(exactRadio, GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(8, 0, 0, 0))
    panel.add(hamiltonRow, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    
    panel.add(
      buildBottomInfoBlock(
        heading = string_source_splits_heading,
        descriptionLabel = string_source_label,
        description = copy.sourceDescription,
        splitCount = copy.splits.size,
        totalLabel = string_source_total_label,
        total = copy.parentTotal,
        currency = copy.sourceCurrency,
        summaryLines = splitSummaryLinesFromCopied(copy.splits, copy.sourceCurrency, dec),
        extraLine = string_target_total_label to targetCurrentTotal
      ),
      GridC.getc().xy(0, y++).colspan(2).wx(1f).fillboth()
    )
    
    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, dialogTitle, OKButtonPanel.QUESTION_OK_CANCEL,
      focusComponent = newTotalField,
      sizeKey = Main.EXTN_ID + dialog_paste_always_confirm_size,
      locationKey = Main.EXTN_ID + dialog_paste_always_confirm_locn
    )
    win.setEscapeKeyCancels(true)
    
    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return null
    
    val newTotal = newTotalField.value
    val mode:AllocationMode = if (hamiltonRadio.isSelected) AllocationMode.PercentHamilton else AllocationMode.ExactNewLine
    return PasteConfirmChoice(newTotal = newTotal, mode = mode)
  }

}