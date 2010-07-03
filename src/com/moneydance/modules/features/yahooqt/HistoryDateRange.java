package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.DateRange;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.util.Constants;

/**
 * Created by IntelliJ IDEA.
 * User: Kevin
 * Date: Jun 7, 2010
 * Time: 6:16:09 AM
 * To change this template use File | Settings | File Templates.
 */
public class HistoryDateRange {
  private static final int DOWNLOAD_DAYS = 60;
  private static final int MINIMUM_DAYS = 5;

  public static DateRange getRangeForSecurity(CurrencyType secCurrency) {
    int lastDate = 0;
    for (int snapIndex = 0; snapIndex < secCurrency.getSnapshotCount(); snapIndex++) {
      CurrencyType.Snapshot snap = secCurrency.getSnapshot(snapIndex);
      lastDate = Math.max(lastDate, snap.getDateInt());
    }

    int days;
    final int today = Util.getStrippedDateInt();
    if (lastDate == 0) {
      days = DOWNLOAD_DAYS; // no history exists for that security/currency
    } else {
      days = Util.calculateDaysBetween(lastDate, today);
      days = Math.max(days, MINIMUM_DAYS);
    }

    return new DateRange(Util.incrementDate(today, 0, 0, -(days + 1)), today);
  }
}
