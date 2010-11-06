/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.RootAccount;

import java.text.SimpleDateFormat;


/**
 * Obtains quotes from a U.K.-based Yahoo! server, which works better for many European securities.
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

  /**
   * Define the default currency, which is the price currency that is to be used for the downloaded
   * quotes when the Default stock exchange is assigned to a security. The implementation for the
   * UK connection is to specify the Great Britain Pound, and if that doesn't exist, the Euro. If
   * the Euro doesn't exist, then do nothing.
   */
  public void setDefaultCurrency() {
    final RootAccount root = getModel().getRootAccount();
    if (root == null) return;
    // assume the London exchange
    CurrencyType currency = root.getCurrencyTable().getCurrencyByIDString("GBP");
    // assume some other European exchange is in use
    if (currency == null) currency = root.getCurrencyTable().getCurrencyByIDString("EUR");
    if (currency == null) return;
    StockExchange.DEFAULT.setCurrency(currency);
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