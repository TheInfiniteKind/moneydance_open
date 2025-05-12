/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.moneydance.model.DateRange
import com.infinitekind.util.DateUtil
import kotlin.math.max

/**
 * Date range specific to a security to fill in the needed number of days of history.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
object HistoryDateRange {
  private const val NEW_DOWNLOAD_DAYS = 365
  private const val MINIMUM_DAYS = 5
  
  fun getRangeForSecurity(secCurrency: CurrencyType, numDays: Int): DateRange {
    var lastDate = 0
    for (snap in secCurrency.snapshots) {
      lastDate = max(lastDate, snap.dateInt)
    }
    // determine how many days of history to download
    var days: Int
    val today: Int = DateUtil.strippedDateInt
    if (lastDate == 0) {
      days = max(numDays, NEW_DOWNLOAD_DAYS) // no history exists for that security/currency
    } else {
      days = DateUtil.calculateDaysBetween(lastDate, today)
      days = max(days, numDays)
      days = max(days, MINIMUM_DAYS)
    }
    
    return DateRange(DateUtil.incrementDate(today, 0, 0, -(days + 1)), today)
  }
}
