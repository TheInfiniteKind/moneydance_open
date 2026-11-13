package com.moneydance.modules.features.contextmenutools.util

import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.Reminder
import com.moneydance.modules.features.contextmenutools.Main
import java.lang.reflect.Method

/**
 * Reminder one-off instances (deferred occurrences), MD2027(5512) onwards. These methods are not in
 * lib/moneydance-private.jar, so they are reached by reflection, and every call falls back to the
 * pre-5512 behaviour when they are missing.
 *
 * @author Stuart Beesley - November 2026
 */
object RemUtility {
  private val getDeferredDatesMethod:Method? by lazy {
    runCatching { Reminder::class.java.getMethod("getDeferredDates") }.getOrNull()
  }
  private val getDeferredTxnInfoMethod:Method? by lazy {
    runCatching { Reminder::class.java.getMethod("getDeferredTxnInfo", Int::class.javaPrimitiveType) }.getOrNull()
  }
  private val setDeferredTxnInfoMethod:Method? by lazy {
    runCatching { Reminder::class.java.getMethod("setDeferredTxnInfo", Int::class.javaPrimitiveType, ParentTxn::class.java) }.getOrNull()
  }

  val isDeferredRemindersBuild:Boolean by lazy {
    (Main.mdMain?.build ?: 0) >= Main.REMINDERS_ONE_OFF_INSTANCES_BUILD &&
      getDeferredDatesMethod != null && getDeferredTxnInfoMethod != null && setDeferredTxnInfoMethod != null
  }

  /** Every scheduled date with a stored one-off record, complete or not; empty before 5512. */
  fun storedDeferredDates(rem:Reminder):List<Int> {
    if (!isDeferredRemindersBuild) return emptyList()
    @Suppress("UNCHECKED_CAST")
    return runCatching { getDeferredDatesMethod!!.invoke(rem) as List<Int> }.getOrNull() ?: emptyList()
  }

  /** Scheduled dates that have a usable one-off instance; empty before 5512. */
  fun deferredDates(rem:Reminder):List<Int> = storedDeferredDates(rem).filter { deferredTxn(rem, it) != null }

  /** The one-off instance for a scheduled date, or null. */
  fun deferredTxn(rem:Reminder, scheduledDate:Int):ParentTxn? {
    if (!isDeferredRemindersBuild) return null
    return runCatching { getDeferredTxnInfoMethod!!.invoke(rem, scheduledDate) as ParentTxn? }.getOrNull()
  }

  fun hasOneOffs(rem:Reminder):Boolean = deferredDates(rem).isNotEmpty()

  /** Stores the one-off instance for a scheduled date; null removes it.
   *  The caller wraps it in an UndoableChange on the reminder. */
  fun setDeferredTxn(rem:Reminder, scheduledDate:Int, txn:ParentTxn?) {
    if (!isDeferredRemindersBuild) return
    runCatching { setDeferredTxnInfoMethod!!.invoke(rem, scheduledDate, txn) }
  }

  /** Removes every one-off instance, as MD's Edit Reminder does when the master changes.
   *  The caller wraps it in an UndoableChange on the reminder, together with the master edit
   *  when there is one. */
  fun clearAllOneOffs(rem:Reminder) {
    if (!isDeferredRemindersBuild) return
    for (date in storedDeferredDates(rem)) runCatching { setDeferredTxnInfoMethod!!.invoke(rem, date, null) }
  }

  /** Upcoming occurrences as the user sees them: (date, isOneOff), by moved date
   *  (Reminder Details' look-forward). */
  fun upcomingOccurrences(rem:Reminder, maximumDate:Int):List<Pair<Int, Boolean>> {
    val movedDates = deferredDates(rem).associateWith { deferredTxn(rem, it)!!.dateInt }
    return (rem.getNextOccurrences(maximumDate) + movedDates.keys).distinct()
      .map { scheduled -> movedDates[scheduled]?.let { it to true } ?: (scheduled to false) }
      .filter { it.first in 1..maximumDate }
      .sortedBy { it.first }
  }

  /** True if Moneydance committed this txn from this reminder. The id holds the scheduled date, which
   *  differs from the txn's date when the occurrence was deferred or its date was changed on Record. */
  fun isFromReminder(txn:ParentTxn, rem:Reminder):Boolean = txn.UUID.startsWith("${rem.UUID}.")
}
