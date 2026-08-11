package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.*
import com.moneydance.apps.md.controller.MDActionContext
import com.infinitekind.moneydance.model.UndoableChange
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.apps.md.view.gui.OKButtonWindow
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.Util
import com.moneydance.awt.GridC
import com.moneydance.modules.features.contextmenutools.Main.Companion.extensionContext
import com.moneydance.modules.features.contextmenutools.util.downloadMatchTypeCompat
import com.moneydance.modules.features.contextmenutools.util.noMatchConstantCompat
import com.moneydance.modules.features.contextmenutools.util.setNameCompat
import java.awt.Dimension
import java.awt.GridBagLayout
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.awt.event.ActionListener
import java.awt.event.WindowAdapter
import java.awt.event.WindowEvent
import javax.swing.Action
import javax.swing.ButtonGroup
import javax.swing.JPanel
import javax.swing.JRadioButton
import javax.swing.border.EmptyBorder
import kotlin.math.abs
import kotlin.math.max

@Suppress("DuplicatedCode", "PrivatePropertyName", "DestructuringDeclaration")

/**
 * Adds "Copy Splits" / "Paste Splits" context-menu actions to the transaction register, letting
 * the user copy the split lines from one transaction and apply them to another - primarily to
 * bring multi-split detail (e.g. from a Reminder or manually-entered transaction) onto a
 * downloaded/imported transaction, without retyping every split by hand.
 *
 * ELIGIBILITY - Copy:
 * - Source account must be BANK or CREDIT_CARD.
 * - Source transaction must have at least one split.
 * - All splits must share the source account's currency (no cross-currency splits).
 * - Source transaction's own cleared/reconciled status is not checked - any status may be copied.
 *
 * ELIGIBILITY - Paste:
 * - Target cannot be the same transaction that was copied from.
 * - Target account must be BANK or CREDIT_CARD.
 * - Target transaction and all of its existing splits must be UNRECONCILED.
 * - Target account's currency must match the copied source's currency.
 * - Target account must have a default category set, or the paste is blocked with a message.
 *
 * If either set of conditions fails, the corresponding menu action is simply not shown - no
 * error is surfaced (see canCopySplits / canPasteSplits).
 *
 * WHAT GETS COPIED per split: category (account), amount, description, keywords/tags, check
 * number. Attachment key names are recorded (for warning purposes only - see below) but the
 * actual attached files are never copied. VAT-related split data is not yet handled (open TODO).
 * Online-download/match data (blue-dot state, match type, FI/transaction IDs) is deliberately
 * NEVER copied onto pasted splits - this is enforced, not just omitted.
 *
 * OVERWRITE PROTECTION: if the paste target's existing splits include one that is downloaded and
 * either matched/merged or already confirmed (see splitHoldsProtectedOnlineData), the user is
 * warned before their data is overwritten. Pasting onto a single blank ($0) placeholder split
 * skips this and other overwrite prompts, unless that split itself holds protected online data.
 *
 * AMOUNT MISMATCH HANDLING: if the target's current total differs from the copied splits' total,
 * the user is asked to choose one of:
 *   - Overwrite total: paste the copied amounts exactly, changing the target's overall total.
 *   - Exact amounts, remainder on a new split: keep copied amounts unchanged, put the difference
 *     on an additional new split (using the target account's default category).
 *   - Allocate by % (Hamilton's method): rescale every split to its original percentage share of
 *     the new total, distributing any rounding remainder across splits (largest-remainder method)
 *     so no single split absorbs more than a whole unit of rounding error.
 *
 * ATTACHMENTS: never pasted under any circumstance. If any copied split had attachments, an
 * informational popup fires after paste, but only when the extension's debug-messages preference is enabled.
 *
 * All paste operations replace the target's entire split set (remove-all, then re-add) and are
 * recorded as a single undoable change.
 */
class CopyPasteSplits:ContextMenuAction {
  
  private val string_copy_splits = "Copy Splits"
  private val string_paste_splits = "Paste Splits"
  private val string_paste_overwrite_confirm = "This will overwrite the existing splits on the selected transaction. Continue?"
  private val string_paste_splits_remainder_title = "Paste Splits - Allocation Method"
  private val string_undo_redo_paste_splits = "Paste Splits"
  
  private val string_opt_overwrite_total = "Change/Overwrite total to {total} (paste exact copied amounts)"
  private val string_opt_exact_new = "Exact amounts, remainder on a new split"
  private val string_opt_pct_hamilton = "Allocate by % (Hamilton's method)"
  private val string_paste_blocked_no_default_category = "Paste blocked. Please set the default category for account: {acct}"
  private val string_paste_overwrite_confirm_online = "This will overwrite existing splits on the selected transaction, including data linked to a downloaded or matched online transaction. Continue?"
  private val string_warn_copy_splits_had_attachments = "One or more copied splits had attachments which were not pasted"

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
  
  // ------------------------------------------------------------------------------------------
  // menu construction
  // ------------------------------------------------------------------------------------------
  
  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    val actions = mutableListOf<Action>()
    
    // selected item must always be exactly one Parent txn - no resolving from a split row
    if (listTxns.size != 1) return actions
    val txn = listTxns.first() as? ParentTxn ?: return actions
    
    if (canCopySplits(txn)) {
      actions += addAction(label = string_copy_splits, cmd = "copy_splits") { copySplits(txn) }
    }
    
    val copy = Main.copiedSplits
    if (copy != null && canPasteSplits(txn, copy)) {
      actions += addAction(label = string_paste_splits, cmd = "paste_splits") { pasteSplits(menuContext, txn) }
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
  
  private fun isAllUnreconciled(txn:ParentTxn):Boolean =
    txn.clearedStatus == AbstractTxn.ClearedStatus.UNRECONCILED &&
    txn.allSplits.all { it.clearedStatus == AbstractTxn.ClearedStatus.UNRECONCILED }
  
  private fun canCopySplits(txn:ParentTxn):Boolean {
    // NOTE: copy source can be in any cleared state - unreconciled check applies to paste target only
    if (!isEligibleAccountType(txn.account)) return false
    val splits = txn.allSplits
    if (splits.isEmpty()) return false
    val parentCurr = txn.account.currencyType
    if (splits.any { it.account.currencyType != parentCurr }) return false
    return true
  }
  
  private fun canPasteSplits(txn:ParentTxn, copy:CopiedSplitsSnapshot):Boolean {
    if (txn.UUID == copy.sourceParentUUID) return false     // block paste into copy source
    if (!isEligibleAccountType(txn.account)) return false
    if (!isAllUnreconciled(txn)) return false
    if (txn.account.currencyType != copy.sourceCurrency) return false
    return true
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
    require(total == splits.sumOf { it.parentAmount }) { "Parent total must equal sum of its splits" }
    
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
      splits = copiedLines
    )
    
    copySyncInfoToClipboard(txn)
    
    Util.logConsole(true, "CopyPasteSplits: copied ${copiedLines.size} split(s) from parent txn '${txn.UUID}'")
  }
  
  /** Also copy the raw syncInfo of the selected txn to the system clipboard, for diagnostics. */
  private fun copySyncInfoToClipboard(txn:ParentTxn) {
    try {
      val info = txn.syncInfo
      val strVal = info.toMultilineHumanReadableString()
      Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(strVal), null)
    } catch (e:Exception) {
      Util.logConsole("Failed to copy text to clipboard: $e")
    }
  }
  
  // ------------------------------------------------------------------------------------------
  // paste
  // ------------------------------------------------------------------------------------------
  
  private fun pasteSplits(menuContext:MDActionContext, txn:ParentTxn) {
    val copy = Main.copiedSplits ?: return
    if (!canPasteSplits(txn, copy)) return   // re-validate at click time
    
    if (txn.account.defaultCategory == null) {
      mdGUI.showInfoMessage(string_paste_blocked_no_default_category.replace("{acct}", txn.account.getAccountName()))
      return
    }
    
    val existingSplits = txn.allSplits
    val targetTotal = txn.value
    require(targetTotal == existingSplits.sumOf { it.parentAmount }) { "Target parent total must equal sum of its splits" }
    
    val hasProtectedOnlineData = pasteTargetHasProtectedSplits(txn)
    val isBlankPlaceholderTarget = existingSplits.size == 1 && targetTotal == 0L && !hasProtectedOnlineData
    
    if (!isBlankPlaceholderTarget && (existingSplits.size > 1 || hasProtectedOnlineData)) {
      val msg = if (hasProtectedOnlineData) string_paste_overwrite_confirm_online else string_paste_overwrite_confirm
      if (!mdGUI.askQuestion(msg)) return
    }
    
    val newLines:List<CopiedSplitLine> =
      if (isBlankPlaceholderTarget || targetTotal == copy.parentTotal) {
        copy.splits
      } else {

        when (askPasteMismatchOption(menuContext, copy) ?: return) {
          is PasteMismatchOption.OverwriteTargetTotal -> copy.splits
          is PasteMismatchOption.ExactNewLine -> allocateExactRemainderOnNewLine(copy.splits, targetTotal, txn)
          is PasteMismatchOption.PercentHamilton -> allocatePercentHamilton(copy.splits, targetTotal)
        }
      }
    
    val change = UndoableChange()
    change.beginModification(txn)   // snapshot "before" state - target already exists/synced
    
    applyPastedSplits(txn, newLines)
    
    pasteSplitsRecordChange(change, txn)
    
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
  // applying the pasted splits
  // ------------------------------------------------------------------------------------------
  
  private fun applyPastedSplits(target:ParentTxn, lines:List<CopiedSplitLine>) {
    // remove existing splits first (confirmed API: ParentTxn.removeSplit(SplitTxn?): Boolean)
    val existing = target.allSplits.toList()
    for (split in existing) {
      target.removeSplit(split)
    }
    
    // confirmed API: SplitTxn.makeSplitTxn(parentTxn, parentAmount, splitAmount, rate, account,
    // description, txnId, status) then ParentTxn.addSplit(newSplit). Same-currency splits only
    // (enforced at copy/paste eligibility), so parentAmount == splitAmount in magnitude.
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
  
  private fun pasteSplitsRecordChange(change:UndoableChange, target:ParentTxn) {
    change.setNameCompat(string_undo_redo_paste_splits)
    change.finishModification(modifiedItem = target)
    mdGUI.undoManager?.recordChange(change)
  }
  
  /**
   * Returns true if pasting/overwriting this split's data would destroy real online-txn
   * download/match state (as opposed to a plain, untouched blue-dot split).
   */
  private fun splitHoldsProtectedOnlineData(split:SplitTxn):Boolean {
    return split.wasDownloaded() &&
           (split.downloadMatchTypeCompat() != noMatchConstantCompat || !split.isNew)
  }
  
  /**
   * Checks all existing splits on the paste target. Returns true if any of them
   * would need a confirmation prompt before being overwritten.
   */
  private fun pasteTargetHasProtectedSplits(target:ParentTxn):Boolean {
    for (i in 0 until target.splitCount) {
      val split = target.getSplit(i) ?: continue
      if (splitHoldsProtectedOnlineData(split)) return true
    }
    return false
  }
  
  // ------------------------------------------------------------------------------------------
  // remainder-option popup
  // ------------------------------------------------------------------------------------------
  
  private fun askPasteMismatchOption(menuContext:MDActionContext, copy:CopiedSplitsSnapshot):PasteMismatchOption? {
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
      panel.add(rb, GridC.getc().xy(0, y++).west())
      option to rb
    }
    radios.first().second.isSelected = true   // default: overwrite target total
    
    val win = OKButtonWindow(mdGUI, menuContext.component, string_paste_splits_remainder_title, null, OKButtonPanel.QUESTION_OK_CANCEL)
    win.setEscapeKeyCancels(true)
    
    win.window.addWindowListener(object:WindowAdapter() {
      override fun windowOpened(e:WindowEvent) {
        win.pack()
        val preferredWidth = max(360, win.preferredSize.width)
        val preferredHeight = max(290, win.preferredSize.height)
        mdGUI.adjustWindow(win, Util.getComponentDialog(win), Dimension(preferredWidth, preferredHeight), null, null)
      }
    })
    
    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return null
    
    return radios.firstOrNull { it.second.isSelected }?.first
  }
  
}