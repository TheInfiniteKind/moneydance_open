package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.AcctFilter
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.UndoableChange
import com.infinitekind.moneydance.online.OnlineTxnMerger
import com.infinitekind.tiksync.SyncRecord
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import com.moneydance.modules.features.contextmenutools.Main.Companion.DEBUG
import com.moneydance.modules.features.contextmenutools.Main.Companion.extensionContext
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.SizedOKButtonWindow
import com.moneydance.modules.features.contextmenutools.util.Util.logConsole
import com.moneydance.modules.features.contextmenutools.util.logBlockedIfDebug
import com.moneydance.modules.features.contextmenutools.util.setNameCompat
import java.awt.GridBagLayout
import java.awt.event.ActionListener
import javax.swing.Action
import javax.swing.JCheckBox
import javax.swing.JLabel
import javax.swing.JPanel
import javax.swing.border.EmptyBorder

@Suppress("PrivatePropertyName")

/**
 * Ported from the standalone Toolbox "Zap md+/ofx/qif (default) memo fields" script, scoped down
 * to the user's own selection instead of a whole-account date-range sweep. Cleans junk/redundant
 * Memo fields on downloaded transactions - zapping them outright, or swapping them into a blank
 * Description first.
 *
 * Menu-build gate is deliberately TYPE- and SETTING-AGNOSTIC and purely STRUCTURAL - it never
 * reads any of the 11 persisted toggles (see ZapSettings below), and never inspects any
 * transaction's memo/description/download-type either. It only checks: 1-100 selected items,
 * every one a ParentTxn (non-parents are silently excluded from consideration, never block),
 * all sharing one account, that account Active and Bank/Credit Card/Investment. If those hold,
 * the menu item appears - full stop. All content-based logic (which download types to include,
 * reconciled/confirmed-only, subset zap/swap, edit-protection bypass, description-compare
 * bypass, and the actual Stage 1/Stage 2 decision) only ever runs after the item is clicked, via
 * the settings popup and the apply pass - never at build time.
 *
 * NOTE on API surface: this ports several Moneydance fields never previously used elsewhere in
 * this codebase (txn.getFIID(), AbstractTxn.ORIG_TXN_TAG, AbstractTxn.TAG_IS_NEW_TXN via
 * getBooleanParameter, account-active check, OnlineTxnMerger.ORIG_MEMO_TAG). Each real, confirmed
 * call is taken directly from the original script's own working Jython source - but several of
 * the exact Kotlin accessor forms (property vs explicit getter) are inferred, not independently
 * compiled/tested. Flagged inline at each specific call.
 */
class ZapCleanMemo:ContextMenuAction {
  private val ORIG_TXN_TAG = "ol.orig-txn"  // copies AbstractTxn.ORIG_TXN_TAG (which is private)
  
  private val string_zap_clean_memo = "Zap/Clean Memo"
  private val string_zap_settings_title = "Zap/Clean Memo - Settings"
  private val string_zap_large_selection_confirm = "You have selected {count} transactions. This may take a moment and cannot easily be reviewed item-by-item before applying - continue?"
  private val string_zap_info_line = "{count} of the {total} selected transactions currently look like candidates, based on your settings below."
  private val string_zap_summary = "Zapped/swapped the memo on {applied} of {total} selected transactions."
  private val string_undo_redo_zap_clean_memo = "Zap/Clean Memo"
  
  private val LARGE_SELECTION_THRESHOLD = 30
  private val MAX_SELECTION = 100
  
  private val dialog_zap_settings_size = ".gui.zap_clean_memo.size"
  private val dialog_zap_settings_locn = ".gui.zap_clean_memo.loc"
  
  private val LOG_SOURCE = "ZapCleanMemo"
  
  // ------------------------------------------------------------------------------------------
  // type detection
  
  private enum class DownloadType { MDP, OFX, IMPORTED_OFX, DOWNLOADED_QIF, NON_DOWNLOADED_QIF }
  
  private val QIF_NON_DOWNLOADED_IMPORT_KEY = "qif.orig-txn"
  private val OFX_IMPORT_TAG_MARKER = "<STMTTRN>"
  
  /**
   * Mirrors the script's own detection exactly: downloaded transactions are typed via their FIID
   * (Financial Institution ID) prefix; non-downloaded transactions are only ever QIF- (manually
   * imported), detected via a specific stored parameter. A transaction matching none of these
   * returns null (never processed).
   *
   * UNVERIFIED: txn.getFIID() - never used elsewhere in this codebase. Confirmed real in the
   * original script's own working source, exact Kotlin call form (property vs explicit getter)
   * not independently checked here.
   */
  private fun detectType(txn:ParentTxn):DownloadType? {
    val fiid = try {
      txn.fIID ?: ""
    } catch (_:Exception) {
      ""
    }
    
    if (!txn.wasDownloaded()) {
      if (fiid.isNotEmpty()) return null   // script treats this combination as a logic error - just don't detect a type
      // QIF- is fundamentally less certain than the other four types. Those are detected from a
      // literal prefix in real online-banking data (mdplus:/ofx:/qif), a solid fact about the
      // transaction. QIF- transactions were never downloaded at all - there's no such prefix, no
      // Confirm/Merge step, none of Moneydance's normal online-banking metadata (see readme). The
      // best available signal is just whether this one stored parameter happens to be present -
      // a weaker, more ambiguous hint than the other four types get.
      //
      // The original script reflects this uncertainty by bundling the include-toggle INTO
      // detection itself: a transaction only ever becomes "QIF-" at all if the toggle is on,
      // right at this line. We split that into two steps instead - detect purely from the
      // signal here, check the toggle separately afterward (includeToggleFor) - same end result
      // for every real case (skipped either way when the toggle's off), just structured
      // differently. Noted here since it's the one real structural difference from the script
      // found during audit, not because it changes behavior.
      val isNonDownloadedQif = (txn.getParameter(QIF_NON_DOWNLOADED_IMPORT_KEY, "") ?: "").isNotBlank()
      return if (isNonDownloadedQif) DownloadType.NON_DOWNLOADED_QIF else null
    }
    
    val fiidLower = fiid.lowercase()
    return when {
      "mdplus:" in fiidLower -> DownloadType.MDP
      "ofx:" in fiidLower -> DownloadType.OFX
      "qif" in fiidLower || "script:" in fiidLower -> DownloadType.DOWNLOADED_QIF
      else -> {
        // UNVERIFIED: AbstractTxn.ORIG_TXN_TAG - the original script reflects this field
        // (getFieldByReflection(AbstractTxn, "ORIG_TXN_TAG")), suggesting it may not have been
        // directly compile-time accessible in its own older devkit. Trying the direct reference
        // first, given this codebase's MD2024.4 devkit may expose it normally now - flagged for
        // a compile check.
        val origTxnData = try {
          txn.getParameter(ORIG_TXN_TAG, "")
        } catch (_:Exception) {
          ""
        }
        if ((origTxnData ?: "").uppercase().contains(OFX_IMPORT_TAG_MARKER)) DownloadType.IMPORTED_OFX else null
      }
    }
  }
  
  private fun includeToggleFor(type:DownloadType, settings:ZapSettings):Boolean = when (type) {
    DownloadType.MDP -> settings.includeMdp
    DownloadType.OFX -> settings.includeOfx
    DownloadType.IMPORTED_OFX -> settings.includeImportedOfx
    DownloadType.DOWNLOADED_QIF -> settings.includeDownloadedQif
    DownloadType.NON_DOWNLOADED_QIF -> settings.includeNonDownloadedQif
  }
  
  // ------------------------------------------------------------------------------------------
  // ------------------------------------------------------------------------------------------
  
  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (listTxns.size !in 1..MAX_SELECTION) return emptyList()
    
    val parentTxns = listTxns.filterIsInstance<ParentTxn>()   // non-parents silently excluded, never block
    if (parentTxns.isEmpty()) {
      logBlockedIfDebug(LOG_SOURCE, "No Parent transactions in the selection")
      return emptyList()
    }
    
    val sharedAccount = parentTxns.first().account
    if (parentTxns.any { it.account != sharedAccount }) {
      logBlockedIfDebug(LOG_SOURCE, "Selected transactions are not all in the same account")
      return emptyList()
    }
    
    if (sharedAccount.getAccountType() !in listOf(Account.AccountType.BANK, Account.AccountType.CREDIT_CARD, Account.AccountType.INVESTMENT)) {
      logBlockedIfDebug(LOG_SOURCE, "Account type not eligible (Bank/Credit Card/Investment)")
      return emptyList()
    }
    
    if (!AcctFilter.ACTIVE_ACCOUNTS_FILTER.matches(sharedAccount)) {
      logBlockedIfDebug(LOG_SOURCE, "Account is not Active")
      return emptyList()
    }
    
    // menu-build stops here - basic structural checks only. Every content-based rule (memo/
    // description comparison, download type, edit-status, all 11 toggles) is deliberately left
    // to the settings popup and the actual apply pass, not evaluated at build time at all.
    
    val action = addAction(label = string_zap_clean_memo, cmd = "zap_clean_memo")
    { runZapFlow(menuContext, parentTxns, sharedAccount) }
    return listOf(action)
  }
  
  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }
  
  // ------------------------------------------------------------------------------------------
  // settings - persisted in AccountBook.localStorage (NOT user preferences - deliberate, tied
  // to the data file, matching the original script's own choice), one subset group holding every
  // sub-key, each sub-key further suffixed with the account's own UUID (per-account, same
  // scheme the script uses).
  
  private data class ZapSettings(
    val includeMdp:Boolean,
    val includeOfx:Boolean,
    val includeImportedOfx:Boolean,
    val includeDownloadedQif:Boolean,
    val includeNonDownloadedQif:Boolean,
    val reconciledOnly:Boolean,
    val confirmedOnly:Boolean,
    val zapWhenSubsetDesc:Boolean,
    val swapWhenSubsetDesc:Boolean,
    val dontCheckOriginalMemo:Boolean,
    val dontCompareWithDesc:Boolean
  )
  
  private fun groupKey():String = "${Main.EXTN_ID}.zap_memo"
  
  // UNVERIFIED: AccountBook.localStorage - inferred from this codebase's own Java-getter-to-
  // Kotlin-property convention (book.reminders, book.currencies), and confirmed as a real,
  // nullable var property from AccountBook.kt's own source. Null-safe throughout - falls back
  // to script defaults if unavailable.
  private fun loadSettings(account:Account):ZapSettings {
    val ls = account.book.localStorage
    val subset:SyncRecord? = try {
      ls?.getSubset(groupKey())
    } catch (_:Exception) {
      null
    }
    val uuid = account.UUID
    fun b(name:String, default:Boolean):Boolean = subset?.getBoolean("$name.$uuid", default) ?: default
    return ZapSettings(
      includeMdp = b("include_mdp", false),
      includeOfx = b("include_ofx", false),
      includeImportedOfx = b("include_imported_ofx", false),
      includeDownloadedQif = b("include_downloaded_qif", false),
      includeNonDownloadedQif = b("include_non_downloaded_qif", false),
      reconciledOnly = b("reconciled_only", true),
      confirmedOnly = b("confirmed_only", true),
      zapWhenSubsetDesc = b("zap_when_subset_desc", false),
      swapWhenSubsetDesc = b("swap_when_subset_desc", false),
      dontCheckOriginalMemo = b("dont_check_original_memo", false),
      dontCompareWithDesc = b("dont_compare_with_desc", false)
    )
  }
  
  private fun saveSettings(account:Account, settings:ZapSettings) {
    val ls = account.book.localStorage ?: return
    val subset = try {
      ls.getSubset(groupKey())
    } catch (_:Exception) {
      SyncRecord()
    }
    val uuid = account.UUID
    fun put(name:String, value:Boolean) {
      subset.put("$name.$uuid", value)
    }
    put("include_mdp", settings.includeMdp)
    put("include_ofx", settings.includeOfx)
    put("include_imported_ofx", settings.includeImportedOfx)
    put("include_downloaded_qif", settings.includeDownloadedQif)
    put("include_non_downloaded_qif", settings.includeNonDownloadedQif)
    put("reconciled_only", settings.reconciledOnly)
    put("confirmed_only", settings.confirmedOnly)
    put("zap_when_subset_desc", settings.zapWhenSubsetDesc)
    put("swap_when_subset_desc", settings.swapWhenSubsetDesc)
    put("dont_check_original_memo", settings.dontCheckOriginalMemo)
    put("dont_compare_with_desc", settings.dontCompareWithDesc)
    ls.put(groupKey(), subset)
    // no explicit save() - Moneydance manages the flush/save cycle itself, matching the
    // original script's own behavior (it never calls .save() here either).
  }
  
  // ------------------------------------------------------------------------------------------
  // full, toggle-aware decision logic - apply-time only
  
  private data class ZapAction(val zapMemo:Boolean, val swapIntoDescription:Boolean)
  
  /**
   * Full Stage 1 (edit-protection) + Stage 2 (zap/swap decision) logic, exactly matching the
   * original script's own branching, including the "blank description always swaps+zaps
   * regardless of the swap toggle" behavior (that toggle only affected the script's own report
   * marker, which we don't reproduce - it's fully unconditional here).
   */
  private fun decideZapAction(txn:ParentTxn, type:DownloadType, settings:ZapSettings, logReason:Boolean = false):ZapAction? {
    val debug = logReason && (extensionContext?.debugMenuEnabled == true || DEBUG)
    fun skip(reason:String):ZapAction? {
      if (debug) logConsole("Zap/Clean Memo: skipped '${txn.description}' (${txn.dateInt}) [$type] - $reason")
      return null
    }
    
    val txnMemo = txn.memo.trim()
    if (txnMemo.isEmpty()) return skip("memo is blank")
    
    // reconciled-only applies to EVERY type, including QIF- - no exemption in the real script.
    // confirmed-only is the one that's exempted for QIF- - "confirmed" here means Moneydance's
    // own online-match status, and QIF- transactions never went through online banking at all
    // (no Confirm/Merge step - see readme), so the concept doesn't apply to them; there's nothing
    // to check, not a deliberate leniency.
    if (settings.reconciledOnly && txn.clearedStatus != AbstractTxn.ClearedStatus.CLEARED) return skip("not reconciled (reconciled-only is on)")
    if (type != DownloadType.NON_DOWNLOADED_QIF) {
      // UNVERIFIED: AbstractTxn.TAG_IS_NEW_TXN via getBooleanParameter - confirmed real constant
      // and real method shape from the original script; exact Kotlin call form not independently
      // checked here.
      if (settings.confirmedOnly && txn.getBooleanParameter(AbstractTxn.TAG_IS_NEW_TXN, false)) return skip("not confirmed (confirmed-only is on)")
    }
    
    // Stage 1 - edit-protection
    // Stage 1 - edit-protection. QIF- is exempt here too, for the same underlying reason as the
    // confirmed-only exemption above: this check compares the current memo against Moneydance's
    // own record of what was originally downloaded, and QIF- was never downloaded - there's no
    // original to compare against, so the protection can't be applied, not because it's been
    // deliberately waived.
    val mustCheckOriginal = type != DownloadType.NON_DOWNLOADED_QIF && !settings.dontCheckOriginalMemo
    if (mustCheckOriginal) {
      val olMemo = try {
        (txn.getParameter(OnlineTxnMerger.ORIG_MEMO_TAG, "") ?: "").trim()
      } catch (_:Exception) {
        ""
      }
      if (olMemo.isEmpty()) return skip("no original downloaded memo found (ol.orig-memo blank/unreadable)")
      if (!txnMemo.equals(olMemo, ignoreCase = true)) return skip("memo differs from original downloaded memo (edited since download) - current='$txnMemo' original='$olMemo'")
    }
    
    // Stage 2 - zap/swap decision
    var zapMemo = false
    var swapIntoDescription = false
    
    if (type == DownloadType.MDP) {
      zapMemo = true
    } else {
      if (settings.dontCompareWithDesc) zapMemo = true
      
      val txnDesc = txn.description.trim()
      if (txnDesc.isNotEmpty() && txnDesc.equals(txnMemo, ignoreCase = true)) {
        zapMemo = true
      } else if (txnDesc.isEmpty() && txnMemo.isNotEmpty()) {
        // always swaps+zaps regardless of the swap toggle - matches the script exactly
        swapIntoDescription = true
        zapMemo = true
      } else if (txnDesc.contains(txnMemo, ignoreCase = true) && txnMemo.length < txnDesc.length) {
        if (settings.zapWhenSubsetDesc) zapMemo = true
      } else if (txnMemo.contains(txnDesc, ignoreCase = true) && txnDesc.length < txnMemo.length) {
        if (settings.swapWhenSubsetDesc) {
          swapIntoDescription = true
          zapMemo = true
        }
      }
    }
    
    if (zapMemo) {
      if (debug) logConsole("Zap/Clean Memo: matched '${txn.description}' (${txn.dateInt}) [$type] - zap=$zapMemo swap=$swapIntoDescription")
      return ZapAction(zapMemo, swapIntoDescription)
    }
    return skip("desc='${txn.description.trim()}' memo='$txnMemo' - no zap/swap rule matched (check subset/blank-description toggles)")
  }
  
  // ------------------------------------------------------------------------------------------
  // the flow: >30 confirm -> settings popup -> apply -> summary
  
  private fun runZapFlow(menuContext:MDActionContext, txns:List<ParentTxn>, account:Account) {
    if (txns.size > LARGE_SELECTION_THRESHOLD) {
      val msg = string_zap_large_selection_confirm.replace("{count}", txns.size.toString())
      if (!mdGUI.askQuestion(msg)) return
    }
    
    val settings = askZapSettings(menuContext, txns, account) ?: return
    val debug = extensionContext?.debugMenuEnabled == true || DEBUG
    
    val change = UndoableChange()
    var appliedCount = 0
    
    for (txn in txns) {
      if (txn.memo.isBlank()) {
        if (debug) logConsole("Zap/Clean Memo: skipped '${txn.description}' (${txn.dateInt}) - memo is blank")
        continue
      }
      val type = detectType(txn)
      if (type == null) {
        if (debug) logConsole("Zap/Clean Memo: skipped '${txn.description}' (${txn.dateInt}) - no download type detected (FIID and <STMTTRN> fallback both came up empty)")
        continue
      }
      if (!includeToggleFor(type, settings)) {
        if (debug) logConsole("Zap/Clean Memo: skipped '${txn.description}' (${txn.dateInt}) [$type] - this type isn't ticked in settings")
        continue
      }
      val action = decideZapAction(txn, type, settings, logReason = true) ?: continue
      
      change.beginModification(txn)
      if (action.swapIntoDescription) txn.description = txn.memo
      if (action.zapMemo) txn.memo = ""
      change.finishModification(txn)
      appliedCount++
    }
    
    if (appliedCount > 0) {
      change.setNameCompat(string_undo_redo_zap_clean_memo)
      mdGUI.undoManager?.recordChange(change)
    }
    
    val summary = string_zap_summary
      .replace("{applied}", appliedCount.toString())
      .replace("{total}", txns.size.toString())
    mdGUI.showInfoMessage(summary)
  }
  
  private fun askZapSettings(menuContext:MDActionContext, txns:List<ParentTxn>, account:Account):ZapSettings? {
    val current = loadSettings(account)

    val typeCounts = DownloadType.entries.associateWith { wanted -> txns.count { detectType(it) == wanted } }

    val includeMdpCheckbox = JCheckBox("MD+ downloads (Moneydance, via Plaid) - ${typeCounts[DownloadType.MDP]} in selection", current.includeMdp)
    val includeOfxCheckbox = JCheckBox("OFX Direct Connect downloads (OFX+) - ${typeCounts[DownloadType.OFX]} in selection", current.includeOfx)
    val includeImportedOfxCheckbox = JCheckBox("Manually imported .ofx/.qfx files (OFX-) - ${typeCounts[DownloadType.IMPORTED_OFX]} in selection", current.includeImportedOfx)
    val includeDownloadedQifCheckbox = JCheckBox("Downloaded .qif files (QIF+) - ${typeCounts[DownloadType.DOWNLOADED_QIF]} in selection", current.includeDownloadedQif)
    val includeNonDownloadedQifCheckbox = JCheckBox("Manually imported .qif files, non-downloaded (QIF-) - ${typeCounts[DownloadType.NON_DOWNLOADED_QIF]} in selection", current.includeNonDownloadedQif)
    includeMdpCheckbox.toolTipText = "Always zaps unedited memos unconditionally - only the memo, nothing else, and every other rule below is ignored."

    // disabled (not hidden) when that type isn't present at all in this selection - ticking it
    // would have zero effect either way. Checkbox state itself is left exactly as persisted,
    // never modified just because it's disabled this time.
    includeMdpCheckbox.isEnabled = (typeCounts[DownloadType.MDP] ?: 0) > 0
    includeOfxCheckbox.isEnabled = (typeCounts[DownloadType.OFX] ?: 0) > 0
    includeImportedOfxCheckbox.isEnabled = (typeCounts[DownloadType.IMPORTED_OFX] ?: 0) > 0
    includeDownloadedQifCheckbox.isEnabled = (typeCounts[DownloadType.DOWNLOADED_QIF] ?: 0) > 0
    includeNonDownloadedQifCheckbox.isEnabled = (typeCounts[DownloadType.NON_DOWNLOADED_QIF] ?: 0) > 0

    val reconciledOnlyCheckbox = JCheckBox("Only reconciled transactions", current.reconciledOnly)
    val confirmedOnlyCheckbox = JCheckBox("Only confirmed transactions (bypassed on QIF-)", current.confirmedOnly)
    val zapWhenSubsetDescCheckbox = JCheckBox("Zap unchanged memo when it's already contained in a longer description", current.zapWhenSubsetDesc)
    val swapWhenSubsetDescCheckbox = JCheckBox("Swap memo into description when description is the same text, just shorter than the memo", current.swapWhenSubsetDesc)
    val dontCheckOriginalMemoCheckbox = JCheckBox("Don't check the original downloaded memo first", current.dontCheckOriginalMemo)
    val dontCompareWithDescCheckbox = JCheckBox("Don't compare memo to description - just zap", current.dontCompareWithDesc)
    swapWhenSubsetDescCheckbox.toolTipText = "Only when the description matches exactly within the memo, not just any shorter description."
    dontCheckOriginalMemoCheckbox.toolTipText = "Zaps the memo regardless of edits made to it. QIF- is never protected either way, ticked or not."
    dontCompareWithDescCheckbox.toolTipText = "Reconciled-only, confirmed-only, and the memo edit-protection check above still apply on top of this."
    
    // Reads the CURRENT, live checkbox states - not the persisted 'current' loaded at dialog-
    // open time. Used both to recompute the candidate count as the user toggles things, and to
    // build the final settings written out on OK - one source of truth for both, rather than
    // two separate places that could drift apart.
    fun liveSettingsFromCheckboxes():ZapSettings = ZapSettings(
      includeMdp = includeMdpCheckbox.isSelected,
      includeOfx = includeOfxCheckbox.isSelected,
      includeImportedOfx = includeImportedOfxCheckbox.isSelected,
      includeDownloadedQif = includeDownloadedQifCheckbox.isSelected,
      includeNonDownloadedQif = includeNonDownloadedQifCheckbox.isSelected,
      reconciledOnly = reconciledOnlyCheckbox.isSelected,
      confirmedOnly = confirmedOnlyCheckbox.isSelected,
      zapWhenSubsetDesc = zapWhenSubsetDescCheckbox.isSelected,
      swapWhenSubsetDesc = swapWhenSubsetDescCheckbox.isSelected,
      dontCheckOriginalMemo = dontCheckOriginalMemoCheckbox.isSelected,
      dontCompareWithDesc = dontCompareWithDescCheckbox.isSelected
    )
    
    val infoLabel = JLabel()
    
    fun refreshInfoLabel() {
      val liveSettings = liveSettingsFromCheckboxes()
      val candidateCount = txns.count { txn ->
        val type = detectType(txn)
        type != null && includeToggleFor(type, liveSettings) && decideZapAction(txn, type, liveSettings) != null
      }
      infoLabel.text = string_zap_info_line.replace("{count}", candidateCount.toString()).replace("{total}", txns.size.toString())
    }
    
    for (checkbox in listOf(
      includeMdpCheckbox, includeOfxCheckbox, includeImportedOfxCheckbox, includeDownloadedQifCheckbox, includeNonDownloadedQifCheckbox,
      reconciledOnlyCheckbox, confirmedOnlyCheckbox, zapWhenSubsetDescCheckbox, swapWhenSubsetDescCheckbox, dontCheckOriginalMemoCheckbox, dontCompareWithDescCheckbox
    )) {
      checkbox.addActionListener { refreshInfoLabel() }
    }
    refreshInfoLabel()
    
    val panel = JPanel(GridBagLayout())
    panel.border = EmptyBorder(16, 16, 16, 16)
    var y = 0
    
    panel.add(
      infoLabel,
      GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 12, 0)
    )
    
    panel.add(JLabel("Which download types to include:"), GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 4, 0))
    panel.add(includeMdpCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(includeOfxCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(includeImportedOfxCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(includeDownloadedQifCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(includeNonDownloadedQifCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 12, 0))
    
    panel.add(reconciledOnlyCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(confirmedOnlyCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west().insets(0, 0, 12, 0))
    
    panel.add(zapWhenSubsetDescCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(swapWhenSubsetDescCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(dontCheckOriginalMemoCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    panel.add(dontCompareWithDescCheckbox, GridC.getc().xy(0, y++).colspan(2).wx(1f).west())
    
    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, string_zap_settings_title, OKButtonPanel.QUESTION_OK_CANCEL,
      sizeKey = Main.EXTN_ID + dialog_zap_settings_size,
      locationKey = Main.EXTN_ID + dialog_zap_settings_locn
    )
    win.setEscapeKeyCancels(true)
    
    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return null
    
    val chosen = liveSettingsFromCheckboxes()
    saveSettings(account, chosen)
    return chosen
  }
}