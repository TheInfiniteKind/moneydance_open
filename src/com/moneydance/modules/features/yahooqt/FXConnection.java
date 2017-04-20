/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.DateRange;
import com.moneydance.util.StringUtils;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;


/**
 * Class used to download currency histories via HTTP using the same spreadsheet format as at
 * finance.yahoo.com.
 *
 * @author Sean Reilly - The Infinite Kind, LLC
 */
public class FXConnection extends BaseConnection {
  private static final String CURRENT_BASE_URL = "https://download.finance.yahoo.com/d/quotes.csv";
  // the rest of it: ?s=USDEUR=X&f=sl1d1t1c1ohgv&e=.csv"
  private final String _displayName;
  static final String PREFS_KEY = "yahooRates";

  /**
   * Create a connection object that can retrieve exchange rates.
   * @param model       The main data model for the extension.
   * @param displayName Name to display to the user for selection.
   */
  public FXConnection(StockQuotesModel model, String displayName) {
    super(model, BaseConnection.EXCHANGE_RATES_SUPPORT);
    _displayName = displayName;
  }

  /**
   * Retrieve the current information for the given stock ticker symbol.
   * @param currencyID      The string identifier of the currency to start with ('from').
   * @param baseCurrencyID  The string identifier of the currency to end with ('to').
   * @return The downloaded exchange rate definition.
   * @throws Exception If an error occurs during download.
   */
  public ExchangeRate getCurrentRate(String currencyID, String baseCurrencyID)
      throws Exception {
    currencyID = currencyID.toUpperCase().trim();
    baseCurrencyID = baseCurrencyID.toUpperCase().trim();
    if (currencyID.length() != 3 || baseCurrencyID.length() != 3)
      return null;

    StringBuilder urlStr = new StringBuilder(CURRENT_BASE_URL);
    urlStr.append('?');
    urlStr.append("s=");
    urlStr.append(URLEncoder.encode(baseCurrencyID + currencyID, N12EStockQuotes.URL_ENC)); // symbol
    urlStr.append("=X");
    urlStr.append("&f=sl1d1t1c1ohgv"); // format of each line
    urlStr.append("&e=.csv");          // response format
    System.err.println("downloading from: "+urlStr);
    URL url = new URL(urlStr.toString());
    HttpURLConnection conn = (HttpURLConnection)url.openConnection();
    conn.addRequestProperty("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.73.11 (KHTML, like Gecko) Version/7.0.1 Safari/537.73.11");
    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF8"));
    // read the message...
    double rate = -1;
    while (true) {
      String line = in.readLine();
      if (line == null)
        break;
      line = line.trim();

      String rateStr = StringUtils.fieldIndex(line, ',', 1).trim();

      if (rateStr.length() > 0)
        rate = StringUtils.parseRate(rateStr, '.');
    }
    return new ExchangeRate(rate);
  }

  @Override
  public String getFullTickerSymbol(SymbolData parsedSymbol, StockExchange exchange) {
    return null;  // not used
  }

  @Override
  public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange) {
    return null;  // not used
  }

  @Override
  public String getHistoryURL(String fullTickerSymbol, DateRange dateRange) {
    return null;  // not used
  }

  @Override
  public String getCurrentPriceURL(String fullTickerSymbol) {
    return null;  // not used
  }

  @Override
  protected String getCurrentPriceHeader() {
    return null;  // not used
  }

  @Override
  public String getId() { return PREFS_KEY;  }

  @Override
  public String toString() {
    return _displayName;
  }

  public class ExchangeRate {
    private final double rate;

    ExchangeRate(double rate) {
      this.rate = rate;
    }

    public double getRate() {
      return this.rate;
    }
  }

  /**
   * Test method.
   * @param args Program arguments.
   * @throws Exception If an error occurs.
   */
  public static void main(String[] args) throws Exception {
    FXConnection fxConnection = new FXConnection(null, "Test Rates");
    FXConnection.ExchangeRate currentRate = fxConnection.getCurrentRate("USD", "EUR");
    System.out.println("rate is " + currentRate.getRate());
  }
}