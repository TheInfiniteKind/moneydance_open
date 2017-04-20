/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import java.text.SimpleDateFormat;


/**
 * Obtains quotes from a U.S.-based Yahoo! server.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class YahooConnectionUSA extends YahooConnection {

  private static final String HISTORY_URL_BASE =       "https://ichart.finance.yahoo.com/table.csv";
//  private static final String CURRENT_PRICE_URL_BASE = "https://finance.yahoo.com/d/quotes.csv";
  private static final String CURRENT_PRICE_URL_BASE = "https://download.finance.yahoo.com/d/quotes.csv";
  private final String _displayName;
  static final String PREFS_KEY = "yahooUSA";

  public YahooConnectionUSA(StockQuotesModel model, String displayName) {
    super(model);
    _displayName = displayName;
  }

  protected final String getHistoryBaseUrl() { return HISTORY_URL_BASE; }
  protected final String getCurrentPriceBaseUrl() { return CURRENT_PRICE_URL_BASE; }

  @Override
  protected SimpleDateFormat getExpectedDateFormat(boolean getFullHistory) {
    // for some reason history is in 'yyyy-MM-dd' but current price is in 'M/d/yyyy' (no leading
    // zeroes, unlike the UK version of Yahoo)
    if (getFullHistory) return new SimpleDateFormat("yyyy-MM-dd");
    return new SimpleDateFormat("M/d/yyyy");
  }

  public String getId() { return PREFS_KEY; }
  
  @Override
  public String toString() {
    return _displayName;
  }
}
