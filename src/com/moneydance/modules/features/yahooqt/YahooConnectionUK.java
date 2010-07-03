package com.moneydance.modules.features.yahooqt;

import com.moneydance.util.CustomDateFormat;

import java.text.SimpleDateFormat;


/**
 * Obtains quotes from a U.S.-based Yahoo server.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class YahooConnectionUK extends YahooConnection {

  private static final String HISTORY_URL_BASE =       "http://ichart.yahoo.com/table.csv";
  private static final String CURRENT_PRICE_URL_BASE = "http://uk.old.finance.yahoo.com/d/quotes.csv";
  private final String _displayName;
  static final String PREFS_KEY = "yahooUK";

  public YahooConnectionUK(StockQuotesModel model, String displayName) {
    super(model);
    _displayName = displayName;
  }

  protected final String getHistoryBaseUrl() { return HISTORY_URL_BASE; }
  protected final String getCurrentPriceBaseUrl() { return CURRENT_PRICE_URL_BASE; }

  @Override
  protected String getCurrentPriceFormat() {
    return "slt1hgv";
  }

  @Override
  protected String getCurrentPriceHeader() {
    // for whatever reason, the UK version flips the date and time columns, despite being told
    // what order to return them in - looks like 'd1' is ignored and 't1' returns time,date
    return "Symbol,Close,Time,Date,High,Low,Volume";
  }

  @Override
  protected SimpleDateFormat getExpectedDateFormat(boolean getFullHistory) {
    // for some reason history is in 'yyyy-MM-dd' but current price is in 'MM/dd/yyyy'
    if (getFullHistory) return new SimpleDateFormat("yyyy-MM-dd");
    return new SimpleDateFormat("MM/dd/yyyy");
  }

  public String getId() { return PREFS_KEY; }

  @Override
  public String toString() {
    return _displayName;
  }
}