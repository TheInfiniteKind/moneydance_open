/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.util.DateUtil;
import com.infinitekind.util.StringUtils;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.List;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Class for downloading security prices from Yahoo
 */
public class YahooConnection extends BaseConnection {
  
  private static final SimpleDateFormat SNAPSHOT_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
  private static final String crumbleLink = "https://finance.yahoo.com/quote/%1$s/history?p=%1$s";
  
  private static enum YahooConnectionType {
    DEFAULT, UK, CURRENCIES;

    public String preferencesKey() {
      switch (this) {
        case UK: return "yahooUK";
        case CURRENCIES: return "yahooRates";
        case DEFAULT: 
        default: return "yahooUSA";
      }
    }

    public boolean isUK() {
      return this==UK;
    }
    
    public int updateTypes() {
      switch(this) {
        case CURRENCIES:
          return BaseConnection.EXCHANGE_RATES_SUPPORT;
        case UK:
        case DEFAULT:
        default:
          return BaseConnection.HISTORY_SUPPORT;
      }
    }
  }
  
//  private static final String HISTORY_URL_BASE_UK =       "https://ichart.yahoo.com/table.csv";
//  private static final String CURRENT_PRICE_URL_BASE_UK = "https://uk.old.finance.yahoo.com/d/quotes.csv";
//  private static final String HISTORY_URL_BASE_USA =       "https://query1.finance.yahoo.com/v7/finance/download/";
//  private static final String CURRENT_PRICE_URL_BASE_USA = "https://download.finance.yahoo.com/d/quotes.csv";
  
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
  private static final String CURRENT_PRICE_FORMAT = "sl1d1t1c1ohgv";

  // Codes necessary to retrieve historical data.
  private String cookie = null;
  private String crumble = null;
  private final YahooConnectionType connectionType;
  
  private YahooConnection(StockQuotesModel model, YahooConnectionType connectionType) {
    super(connectionType.preferencesKey(), model, connectionType.updateTypes());
    this.connectionType = connectionType;
  }
  
  public static YahooConnection getDefaultConnection(StockQuotesModel model) {
    return new YahooConnection(model, YahooConnectionType.DEFAULT);
  }
  
  public static YahooConnection getUKConnection(StockQuotesModel model) {
    return new YahooConnection(model, YahooConnectionType.UK);
  }
  
  public static YahooConnection getCurrenciesConnection(StockQuotesModel model) {
    return new YahooConnection(model, YahooConnectionType.CURRENCIES);
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
  
  /**
   * Update the exchange rate for the given currency using Yahoo's CURR1CURR2=X ticker symbol lookup
   * 
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  @Override
  public void updateExchangeRate(DownloadInfo downloadInfo) {
    String baseCurrencyID = downloadInfo.relativeCurrency.getIDString().toUpperCase();
    if(!downloadInfo.isValidForDownload) return;

    // only update the cookie and crumble if we don't already have them
    if(cookie==null || crumble==null) {
      if(!setCookieAndCrumble(downloadInfo.fullTickerSymbol)) {
        downloadInfo.recordError("Unable to get cookie or crumbs from Yahoo");
        return;
      }
    }
    
    StringBuilder urlStr = new StringBuilder("https://download.finance.yahoo.com/d/quotes.csv");
    urlStr.append('?');
    urlStr.append("s=");
    urlStr.append(SQUtil.urlEncode(baseCurrencyID + downloadInfo.fullTickerSymbol)); // symbol
    urlStr.append("=X");
    urlStr.append("&f=sl1d1t1c1ohgv"); // format of each line
    urlStr.append("&e=.csv");          // response format
    urlStr.append("&crumb=");       // crumble
    urlStr.append(crumble);
    
    boolean foundRate = false;
    Exception error = null;
    try {
      URL url = new URL(urlStr.toString());
      HttpURLConnection conn = (HttpURLConnection) url.openConnection();
      //conn.addRequestProperty("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.73.11 (KHTML, like Gecko) Version/7.0.1 Safari/537.73.11");
      BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF8"));
      // read the message...
      while (true) {
        String line = in.readLine();
        if (line == null)
          break;
        line = line.trim();

        String rateStr = StringUtils.fieldIndex(line, ',', 1).trim();

        if (rateStr.length() > 0) {
          double parsedRate = StringUtils.parseRate(rateStr, 0.0, '.');
          if (parsedRate != 0) {
            downloadInfo.setRate(parsedRate, System.currentTimeMillis());
            foundRate = true;
          }
        }
      }
    } catch (Exception e) {
      error = e;
      System.err.println("exchange rate update error for "+downloadInfo);
      e.printStackTrace();
    }
    
    if(!foundRate) {
      if(error!=null) {
        downloadInfo.recordError("No rate information was retrieved");
      } else {
        
      }
    }
  }
  
  
  @Override
  public boolean updateSecurities(List<DownloadInfo> securitiesToUpdate) {
    
    // TODO: if there's any initialisation step, that goes here before updateSecurity() is invoked for each individual security
    
    return super.updateSecurities(securitiesToUpdate);
  }
  
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  @Override
  public void updateSecurity(DownloadInfo downloadInfo) {
    System.err.println("yahoo: updating security: "+downloadInfo.fullTickerSymbol);
    int today = DateUtil.getStrippedDateInt();
    List<CurrencySnapshot> history = downloadInfo.security.getSnapshots();
    int firstDate = DateUtil.incrementDate(today, 0, -6, -0);
    if(history!=null && history.size()>0) {
      firstDate = Math.max(history.get(history.size()-1).getDateInt(), firstDate);
    }

    if (!setCookieAndCrumble(downloadInfo.fullTickerSymbol)) {
      downloadInfo.recordError("Unable to get cookie or crumbs from Yahoo");
      return;
    }
    
    String urlStr = getHistoryURL(downloadInfo.fullTickerSymbol, new DateRange(firstDate, today));

    char decimal = model.getPreferences().getDecimalChar();
    SnapshotImporterFromURL importer =
      new SnapshotImporterFromURL(urlStr, cookie, model.getResources(),
                                  downloadInfo, SNAPSHOT_DATE_FORMAT,
                                  TimeZone.getTimeZone(getTimeZoneID()), decimal);
    importer.setColumnsFromHeader("Date,Open,High,Low,Close,Adj Close,Volume");
    importer.setPriceMultiplier(downloadInfo.priceMultiplier);
    
    // the return value is negative for general errors, 0 for success with no error, or a positive
    // value for overall success but one or more errors
    int errorResult = importer.importData();
    if (errorResult < 0) {
      Exception error = importer.getLastException();
      downloadInfo.errors.add(new DownloadException(downloadInfo, error.getMessage(), error));
      return;
    }
    List<StockRecord> recordList = importer.getImportedRecords();
    if (recordList.isEmpty()) {
      DownloadException de = buildDownloadException(downloadInfo, SnapshotImporter.ERROR_NO_DATA);
      downloadInfo.errors.add(de);
      return;
    }
    
    downloadInfo.addHistoryRecords(recordList);
  }

  public String getHistoryURL(String fullTickerSymbol, DateRange dateRange) {
    //  private static final String CURRENT_PRICE_URL_BASE_UK = "https://uk.old.finance.yahoo.com/d/quotes.csv";
    //  private static final String HISTORY_URL_BASE_UK =       "https://ichart.yahoo.com/table.csv";
    
    String baseURL = connectionType.isUK() ? "https://ichart.yahoo.com/table.csv" : "https://query1.finance.yahoo.com/v7/finance/download/";
    StringBuilder result = new StringBuilder(baseURL);
    Calendar cal = Calendar.getInstance();
    cal.setTime(DateUtil.convertIntDateToLong(dateRange.getEndDateInt()));
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
  
  
  public String toString() {
    DownloadModel model = getModel();
    return model==null ? "??" : model.getResources().getString(getConnectionID());
  }
  
  
  private boolean setCookieAndCrumble(String fullTickerSymbol) {
    long startTime = System.currentTimeMillis();
    try {
      String urlString = String.format(crumbleLink, fullTickerSymbol);
      URL url = new URL(urlString);
      HttpURLConnection urlConn = (HttpURLConnection)url.openConnection();
      //urlConn.setRequestProperty("User-Agent", "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11");

      int respCode = urlConn.getResponseCode();
      if (respCode < 200 | respCode >= 300) {
        System.err.println("non-success response for cookie/crumble request; code="+respCode+" msg="+urlConn.getResponseMessage());
        return false;
      }
      
      String cookieValue = urlConn.getHeaderField("set-cookie");
      if(cookieValue!=null) {
        int endIdx = cookieValue.indexOf(";");
        cookie = endIdx >= 0 ? cookieValue.substring(0, endIdx) : cookieValue.trim();
      }

      /*
       We need to find the tdv2Crumb, as in the following:
                    "RequestPlugin": {
                        "user": {
                            "crumb": ".asdfasdfasdf.4",
                            "firstName": null,
                            "tdv2Crumb": "VabcdabcdIb6X"
                        }
                    },
       */
      Pattern p = Pattern.compile(".*\"tdv2Crumb\": *\"(.*?)\".*");
      BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(urlConn.getInputStream()));
      String line = null;
      while ((line = bufferedReader.readLine()) != null) {
        // the matcher is slow, so try a quick string comparison first...
        if(!line.contains("\"crumb\"")) continue;
        
        Matcher m = p.matcher(line);
        if (m.matches()) {
          crumble = m.group(1);
          break;
        }
      }
    } catch (Throwable e) {
      e.printStackTrace();
    } finally {
      System.err.println("yahoo: set/updated cookie and/or crumble in " + ((System.currentTimeMillis()-startTime)/1000.0) + " seconds");
    }
    
    return crumble!=null;
  }

}
