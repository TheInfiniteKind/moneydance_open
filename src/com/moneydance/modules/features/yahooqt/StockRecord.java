/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

/**
 * Stores a single entry for a historical price entry (snapshot) for a security.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class StockRecord implements Comparable<StockRecord> {
  int date = 0;
  long volume = 0;
  double highRate = -1.0;
  double lowRate = -1.0;
  double open = -1.0;
  double closeRate = -1.0;
  String priceDisplay = "";

  @Override
  public String toString() {
    return "close="+ closeRate +"; volume="+volume+"; high="+ highRate +"; low="+ lowRate +"; date="+date;
  }

  public int compareTo(StockRecord o) {
    // sort by date
    return date - o.date;
  }
}
