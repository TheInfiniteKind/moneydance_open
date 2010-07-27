/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.DateRange;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.model.CurrencyType;

/**
 * Date range specific to a security to fill in the needed number of days of history.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class HistoryDateRange {
  private static final int DOWNLOAD_DAYS = 60;
  private static final int MINIMUM_DAYS = 5;

  public static DateRange getRangeForSecurity(CurrencyType secCurrency, int numDays) {
    int lastDate = 0;
    for (int snapIndex = 0; snapIndex < secCurrency.getSnapshotCount(); snapIndex++) {
      CurrencyType.Snapshot snap = secCurrency.getSnapshot(snapIndex);
      lastDate = Math.max(lastDate, snap.getDateInt());
    }
    // determine how many days of history to download
    int days;
    final int today = Util.getStrippedDateInt();
    if (lastDate == 0) {
      days = Math.max(numDays, DOWNLOAD_DAYS); // no history exists for that security/currency
    } else {
      days = Util.calculateDaysBetween(lastDate, today);
      days = Math.max(days, numDays);
      days = Math.max(days, MINIMUM_DAYS);
    }

    return new DateRange(Util.incrementDate(today, 0, 0, -(days + 1)), today);
  }
}
