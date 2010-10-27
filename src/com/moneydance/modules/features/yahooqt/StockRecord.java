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
  /** The integer date of the quote. */
  int date = 0;
  /** The exact date of the quote, which can have the time of day set as well. */
  long dateTime = 0;
  /** Number of shares traded. */
  long volume = 0;
  /** The high price in terms of the price currency (gets converted to base currency). */
  double highRate = -1.0;
  /** The low price in terms of the price currency (gets converted to base currency). */
  double lowRate = -1.0;
  /** The open price in terms of the price currency. Currently not used. */
  double open = -1.0;
  /** The close price in terms of the price currency (gets converted to base currency). */
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
