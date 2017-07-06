/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.Util;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.Calendar;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Base class for a download connection to the Yahoo! Finance service.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public abstract class YahooConnection extends BaseConnection {
  /**
   * The format to be returned. These are the complete format symbols, which seem to work but are
   * not documented on the Yahoo website. These meanings come from here on May 17, 2010:
   * http://search.cpan.org/~edd/Finance-YahooQuote-0.22/YahooQuote.pm
   * <br/>
   * and 'ohgv' info here: http://www.practicalpc.co.uk/computing/how/webexcel2.htm
   *
   * <ul>
   * <li>Symbol = s</li>
   * <li>Name = n</li>
   * <li>Last Trade (With Time) = l</li>
   * <li>Last Trade (Price Only) = l1</li>
   * <li>Last Trade Date = d1</li>
   * <li>Last Trade Time = t1</li>
   * <li>Last Trade Size = k3</li>
   * <li>Change and Percent Change = c</li>
   * <li>Change = c1</li>
   * <li>Change in Percent = p2</li>
   * <li>Ticker Trend = t7</li>
   * <li>Volume = v</li>
   * <li>Average Daily Volume = a2</li>
   * <li>More Info = i</li>
   * <li>Trade Links = t6</li>
   * <li>Bid = b</li>
   * <li>Bid Size = b6</li>
   * <li>Ask = a</li>
   * <li>Ask Size = a5</li>
   * <li>Previous Close = p</li>
   * <li>Open = o</li>
   * <li>High (Daily)= h</li>
   * <li>Low (Daily) = g</li>
   * <li>Day's Range = m</li>
   * <li>52-week Range = w</li>
   * <li>Change From 52-wk Low = j5</li>
   * <li>Pct Chg From 52-wk Low = j6</li>
   * <li>Change From 52-wk High = k4</li>
   * <li>Pct Chg From 52-wk High = k5</li>
   * <li>Earnings/Share = e</li>
   * <li>P/E Ratio = r</li>
   * <li>Short Ratio = s7</li>
   * <li>Dividend Pay Date = r1</li>
   * <li>Ex-Dividend Date = q</li>
   * <li>Dividend/Share = d</li>
   * <li>Dividend Yield = y</li>
   * <li>Float Shares = f6</li>
   * <li>Market Capitalization = j1</li>
   * <li>1yr Target Price = t8</li>
   * <li>EPS Est. Current Yr = e7</li>
   * <li>EPS Est. Next Year = e8</li>
   * <li>EPS Est. Next Quarter = e9</li>
   * <li>Price/EPS Est. Current Yr = r6</li>
   * <li>Price/EPS Est. Next Yr = r7</li>
   * <li>PEG Ratio = r5</li>
   * <li>Book Value = b4</li>
   * <li>Price/Book = p6</li>
   * <li>Price/Sales = p5</li>
   * <li>EBITDA = j4</li>
   * <li>50-day Moving Avg = m3</li>
   * <li>Change From 50-day Moving Avg = m7</li>
   * <li>Pct Chg From 50-day Moving Avg = m8</li>
   * <li>200-day Moving Avg = m4</li>
   * <li>Change From 200-day Moving Avg = m5</li>
   * <li>Pct Chg From 200-day Moving Avg = m6</li>
   * <li>Shares Owned = s1</li>
   * <li>Price Paid = p1</li>
   * <li>Commission = c3</li>
   * <li>Holdings Value = v1</li>
   * <li>Day's Value Change = w1,</li>
   * <li>Holdings Gain Percent = g1</li>
   * <li>Holdings Gain = g4</li>
   * <li>Trade Date = d2</li>
   * <li>Annualized Gain = g3</li>
   * <li>High Limit = l2</li>
   * <li>Low Limit = l3</li>
   * <li>Notes = n4</li>
   * <li>Last Trade (Real-time) with Time = k1</li>
   * <li>Bid (Real-time) = b3</li>
   * <li>Ask (Real-time) = b2</li>
   * <li>Change Percent (Real-time) = k2</li>
   * <li>Change (Real-time) = c6</li>
   * <li>Holdings Value (Real-time) = v7</li>
   * <li>Day's Value Change (Real-time) = w4</li>
   * <li>Holdings Gain Pct (Real-time) = g5</li>
   * <li>Holdings Gain (Real-time) = g6</li>
   * <li>Day's Range (Real-time) = m2</li>
   * <li>Market Cap (Real-time) = j3</li>
   * <li>P/E (Real-time) = r2</li>
   * <li>After Hours Change (Real-time) = c8</li>
   * <li>Order Book (Real-time) = i5</li>
   * <li>Stock Exchange = x</li>
   * </ul>
   *
   * So the selected format (column order of returned data) is:<br/>
   * {Symbol}{Last Trade (Close)}{Last Trade Date}{Last Trade Time}{Change}{Open}{High}{Low}{Volume}
   *
   * Updated 7/2017:
   * Previous URLs no longer work. But https://stackoverflow.com/questions/44044263/yahoo-finance-historical-data-downloader-url-is-not-working
   * has a workaround that uses the standard Yahoo historical data interface. Used his Python code as a model
   * for (minor)changes to yahooqt.
   */
  protected static final String CURRENT_PRICE_FORMAT = "sl1d1t1c1ohgv";

  // Codes necessary to retrieve historical data.
  private String cookie = null;
  private String crumble = null;

  public YahooConnection(StockQuotesModel model) {
    super(model, BaseConnection.HISTORY_SUPPORT | BaseConnection.CURRENT_PRICE_SUPPORT);
  }

  public String getFullTickerSymbol(SymbolData parsedSymbol, StockExchange exchange)
  {
    if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) return null;
    // check if the exchange was already added on, which will override the selected exchange
    if (!SQUtil.isBlank(parsedSymbol.suffix)) {
      return parsedSymbol.symbol + parsedSymbol.suffix;
    }
    // Check if the selected exchange has a Yahoo suffix or not. If it does, add it.
    String suffix = exchange.getSymbolYahoo();
    if (SQUtil.isBlank(suffix)) return parsedSymbol.symbol;
    return parsedSymbol.symbol + suffix;
  }

  public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange)
  {
    if (SQUtil.isBlank(rawTickerSymbol)) return null;
    // check if this symbol overrides the exchange and the currency code
    int periodIdx = rawTickerSymbol.lastIndexOf('.');
    if(periodIdx>0) {
      String marketID = rawTickerSymbol.substring(periodIdx+1);
      if(marketID.indexOf("-")>=0) {
        // the currency ID was encoded along with the market ID
        return StringUtils.fieldIndex(marketID, '-', 1);
      }
    }
    return exchange.getCurrencyCode();
  }
  
  protected abstract String getHistoryBaseUrl();

  @Override
  public String getHistoryURL(String fullTickerSymbol, DateRange dateRange) {
    setCookieAndCrumble(fullTickerSymbol);
    StringBuilder result = new StringBuilder(getHistoryBaseUrl());
    Calendar cal = Calendar.getInstance();
    cal.setTime(Util.convertIntDateToLong(dateRange.getEndDateInt()));
    long endTimeInEpoch = cal.getTimeInMillis() / 1000;
    cal.add(Calendar.DATE, -dateRange.getNumDays());
    long startTimeInEpoch = cal.getTimeInMillis() / 1000;

    String encTicker;
    try {
      encTicker = URLEncoder.encode(fullTickerSymbol, N12EStockQuotes.URL_ENC);
    } catch (UnsupportedEncodingException ignore) {
      // should never happen, as the US-ASCII character set is one that is required to be
      // supported by every Java implementation
      encTicker = fullTickerSymbol;
    }

    // add the parameters
    result.append(encTicker);       // symbol
    result.append("?period1=");     // start date
    result.append(startTimeInEpoch);
    result.append("&period2=");     // end date
    result.append(endTimeInEpoch);
    result.append("&interval=1d");  // interval
    result.append("&events=history"); // history
    result.append("&crumb=");       // crumble
    result.append(crumble);
    return result.toString();
  }

  protected abstract String getCurrentPriceBaseUrl();

  public String getCurrentPriceURL(String fullTickerSymbol) {
    StringBuilder result = new StringBuilder(getCurrentPriceBaseUrl());
    String encTicker;
    try {
      encTicker = URLEncoder.encode(fullTickerSymbol, N12EStockQuotes.URL_ENC);
    } catch (UnsupportedEncodingException ignore) {
      // should never happen, as the US-ASCII character set is one that is required to be
      // supported by every Java implementation
      encTicker = fullTickerSymbol;
    }
    // add the parameters
    result.append("?s=");                // symbol
    result.append(encTicker);
    result.append("&f=");                // format of each line
    result.append(getCurrentPriceFormat());
    result.append("&e=.csv");            // response format
    return result.toString();
  }

  private final String crumbleLink = "https://finance.yahoo.com/quote/%1$s/history?p=%1$s";
  private final String crumbleRegEx = ".*\"CrumbStore\":[{]\"crumb\":\"(.*?)\"}.*";

  private void setCookieAndCrumble(String fullTickerSymbol) {
    cookie = null;
    crumble = null;
    try {
      String urlString = String.format(crumbleLink, fullTickerSymbol);
      URL url = new URL(urlString);
      HttpURLConnection urlConn = (HttpURLConnection)url.openConnection();
      int respCode = urlConn.getResponseCode();
      if (respCode < 200 | respCode >= 300) {
        return;
      }

      for (int i = 0; ; i++) {
        String key = urlConn.getHeaderFieldKey(i);
        String value = urlConn.getHeaderField(i);
        if (key == null && value == null) {
          return;
        }
        if (key != null && key.equals("Set-Cookie")) {
          cookie = value.substring(0, value.indexOf(";"));
          break;
        }
      }

      Pattern p = Pattern.compile(crumbleRegEx);
      BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(urlConn.getInputStream()));
      String line = null;
      while ((line = bufferedReader.readLine()) != null) {
        Matcher m = p.matcher(line);
        if (m.matches()) {
          crumble = m.group(1);
          break;
        }
      }
    } catch (Exception e) {
      return;  // If anything goes wrong, there will be no cookie
    }
  }

  protected String getCookie() { return cookie; }

  protected String getCurrentPriceFormat() {
    return CURRENT_PRICE_FORMAT;
  }

  @Override
  protected String getCurrentPriceHeader() {
    // this is the format it is *supposed* to return, see CURRENT_PRICE_FORMAT
    return "Symbol,Close,Date,Time,Change,Open,High,Low,Volume";
  }
}
