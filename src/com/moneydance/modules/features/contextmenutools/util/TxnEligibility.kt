package com.moneydance.modules.features.contextmenutools.util

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.Reminder
import com.moneydance.modules.features.contextmenutools.Main

/**
 * Extension-specific (contextmenutools-only) shared transaction-eligibility helpers - unlike
 * Util.kt (common across StuWareSoftSystems extensions), this file holds logic specific to how
 * THIS extension defines "protected" and "unreconciled" for its own split-editing actions.
 */

/**
 * "Has ol data" = wasDownloaded() is true on the split itself (not the parent). Presence alone
 * is disqualifying, regardless of isNew()/matchType - a split carrying its own download/match
 * data means a separate action was taken on ANOTHER account that specifically targets this
 * split (e.g. a bank transfer's other side confirming a match against it). Parent-level ol.*
 * data is deliberately ignored - it's just import/match metadata about the transaction as a
 * whole, not a per-split cross-account dependency.
 */
fun hasAnyProtectedSplit(txn:ParentTxn):Boolean =
  txn.allSplits.any { it.wasDownloaded() }

/** True if the transaction and every one of its splits are Unreconciled. */
fun isAllUnreconciled(txn:ParentTxn):Boolean =
  txn.clearedStatus == AbstractTxn.ClearedStatus.UNRECONCILED &&
  txn.allSplits.all { it.clearedStatus == AbstractTxn.ClearedStatus.UNRECONCILED }

/**
 * True if this reminder is inactive/expired - either deliberately (lastDateInt set before
 * initialDateInt, a known convention for marking a reminder permanently inert) or because it
 * genuinely has no future occurrences left (per Moneydance's real calculation, not a
 * re-derivation of the date rules).
 */
fun Reminder.isInactiveOrExpired():Boolean {
  // deliberate inert marker
  if (lastDateInt != 0 && lastDateInt < initialDateInt) return true
  
  // real check: any occurrences within the relevant window?
  val searchWindow = if (lastDateInt > 0) lastDateInt else 20991231
  
  return getNextOccurrences(searchWindow).isEmpty()
}

/**
 * True if txn's own ID matches Moneydance's auto-commit convention for this reminder
 * ("{reminderUUID}.{txn's date}" - see ReminderSet.autoCommitReminder). Identity match, not a
 * heuristic - only confirmed for auto-committed occurrences.
 */
fun isUUIDDateMatch(txn:ParentTxn, reminder:Reminder):Boolean =
  txn.UUID == "${reminder.UUID}.${txn.dateInt}"

/**
 * Our own fallback identity link, written by this extension whenever it applies a Splits
 * Template (single or batch) to a transaction - separate from, and a fallback for, Moneydance's
 * own uuid.date auto-commit convention above, which only ever exists for AUTO-committed
 * occurrences. Since Apply Splits Template is applied manually by the user, transactions it
 * touches would otherwise never carry any link back to their source reminder at all. Prefixed
 * with Main.EXTN_ID, matching every other preference/parameter key this extension writes, to
 * avoid colliding with Moneydance's own fields or another extension's.
 *
 * NOTE: the write side (SyncableItem.setParameter) is confirmed real - it's the exact mechanism
 * Moneydance's own ReminderSet.autoCommitReminder uses for the uuid.date convention itself. The
 * read side (getParameter) is inferred by symmetry, not independently confirmed - worth a quick
 * check that this compiles/behaves as expected before relying on it.
 */
private val REM_ID_PARAM_KEY = "${Main.EXTN_ID}.rem_id"

fun isRemIdMarkerMatch(txn:ParentTxn, reminder:Reminder):Boolean =
  txn.getParameter(REM_ID_PARAM_KEY, null) == reminder.UUID

fun writeRemIdMarker(txn:ParentTxn, reminderUUID:String) {
  txn.setParameter(REM_ID_PARAM_KEY, reminderUUID)
}