package com.moneydance.modules.features.yahooqt;

/**
* Created by IntelliJ IDEA.
* User: Kevin
* Date: Jun 13, 2010
* Time: 10:58:05 AM
* To change this template use File | Settings | File Templates.
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
