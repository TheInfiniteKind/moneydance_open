/*************************************************************************\
* Copyright (C) 2025 The Infinite Kind, LLC
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.google.gson.*;
import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.util.AppDebug;
import com.infinitekind.util.DateUtil;
import com.infinitekind.util.StringUtils;
import com.moneydance.modules.features.yahooqt.tdameritrade.Candle;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.HttpClient;
import org.apache.http.client.config.CookieSpecs;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicHeader;
import org.apache.http.util.EntityUtils;


import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;

/**
 * Class for downloading security prices from Yahoo
 */
public class YahooConnection extends BaseConnection {
  
  private enum YahooConnectionType {
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

  private RequestConfig requestConfig = RequestConfig.custom().setCookieSpec(CookieSpecs.STANDARD).build();
  private HttpClient httpClient = 
    HttpClients.custom().setDefaultRequestConfig(requestConfig)
               .setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15")
               .setDefaultHeaders(List.of(new BasicHeader("Accept-Language", "en-US,en;q=0.9")))
               .build();
  
  private YahooConnection(StockQuotesModel model, YahooConnectionType connectionType) {
    super(connectionType.preferencesKey(), model, connectionType.updateTypes());
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

  @Override
  public void updateExchangeRate(DownloadInfo downloadInfo) {
    downloadInfo.recordError("Implementation error: YahooConnection does not currently support exchange rate downloads");
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
    if(history!=null && !history.isEmpty()) {
      firstDate = Math.max(history.getLast().getDateInt(), firstDate);
    }
    
    String urlStr = getHistoryURL(downloadInfo.fullTickerSymbol, new DateRange(firstDate, today));
    HttpGet httpGet = new HttpGet(urlStr);
    
    try {
      HttpResponse response = httpClient.execute(httpGet);
      if (response.getStatusLine().getStatusCode() != HttpStatus.SC_OK) {
        String errMessage = "Error retrieving quote from " + urlStr + " : " + response.getStatusLine();
        AppDebug.DEBUG.log(errMessage);
        downloadInfo.recordError(errMessage);
        return;
      }
      
      String json = EntityUtils.toString(response.getEntity());
      JsonObject jsonData = JsonParser.parseString(json).getAsJsonObject();
      
      extractHistoryFromJSON(downloadInfo, jsonData);
    } catch (Exception e) {
      downloadInfo.recordError("Error retrieving quote from "+urlStr+" : "+e.getMessage());
      AppDebug.DEBUG.log("Error retrieving quote for "+downloadInfo.fullTickerSymbol+" from "+urlStr, e);
    }
  }
  
  private void extractHistoryFromJSON(DownloadInfo downloadInfo, JsonObject jsonData) {
    JsonObject chart = jsonData.getAsJsonObject("chart");
    String error = chart.get("error").isJsonNull() ? null : chart.get("error").getAsString();
    if(!StringUtils.isBlank(error)) {
      downloadInfo.recordError(error);
      return;
    }
    
    JsonObject result = chart.getAsJsonArray("result").getAsJsonArray().get(0).getAsJsonObject();
    // map a list of the timestamps to long objects
    JsonArray timestampArray = result.getAsJsonArray("timestamp");
    if(timestampArray==null || timestampArray.isEmpty()) {
      downloadInfo.recordError("No timestamped results received");
      return;
    }
    long[] timestamps = timestampArray.asList().stream().mapToLong(JsonElement::getAsLong).toArray();
    JsonObject indicators = result.getAsJsonObject("indicators");
    JsonArray quoteArray = indicators.getAsJsonArray("quote");
    if(quoteArray==null || quoteArray.isEmpty()) {
      downloadInfo.recordError("Response had missing or empty quote indicator");
      return;
    }
    JsonObject quoteInfo = quoteArray.get(0).getAsJsonObject();
    if(quoteInfo==null || quoteInfo.isJsonNull()) {
      downloadInfo.recordError("Response had empty quote indicator");
      return;
    }
    
    JsonArray closeValues = quoteInfo.getAsJsonArray("close");
    JsonArray volumeValues = quoteInfo.getAsJsonArray("volume");
    JsonArray highValues = quoteInfo.getAsJsonArray("high");
    JsonArray openValues = quoteInfo.getAsJsonArray("open");
    JsonArray lowValues = quoteInfo.getAsJsonArray("low");
    ArrayList<StockRecord> records = new ArrayList<>();
    for(int i=0; i<timestamps.length; i++) {
      Candle candle = new Candle();
      candle.datetime = timestamps[i] * 1000;
      if(volumeValues.size() > i) { candle.volume = volumeValues.get(i).getAsLong(); }
      if(openValues.size() > i) { candle.open = openValues.get(i).getAsDouble(); }
      if(lowValues.size() > i) { candle.low = lowValues.get(i).getAsDouble(); }
      if(highValues.size() > i) { candle.high = highValues.get(i).getAsDouble(); }
      if(closeValues.size() > i) { candle.close = closeValues.get(i).getAsDouble(); }
    
      records.add(new StockRecord(candle, downloadInfo.priceMultiplier));
    }
    records.sort((rec1, rec2) -> rec2.date - rec1.date);
    
    downloadInfo.addHistoryRecords(records);
  }

  private String getHistoryURL(String fullTickerSymbol, DateRange dateRange) {
    //  private static final String CURRENT_PRICE_URL_BASE_UK = "https://uk.old.finance.yahoo.com/d/quotes.csv";
    //  private static final String HISTORY_URL_BASE_UK =       "https://ichart.yahoo.com/table.csv";

    String encodedTicker = SQUtil.urlEncode(fullTickerSymbol);
    
    long startTime = DateUtil.convertIntDateToLong(dateRange.getStartDateInt()).getTime()/1000;
    long endTime = DateUtil.convertIntDateToLong(dateRange.getEndDateInt()).getTime()/1000;
    String queryURL = "https://query1.finance.yahoo.com/v8/finance/chart/" + encodedTicker + 
                      "?period1=" + startTime +
                      "&period2=" + endTime + 
                      "&interval=1d" +
                      "&includePrePost=true" +
                      "&events=div%7Csplit%7Cearn" + // possibly "events=history" 
                      "&lang=en-US" +
                      "&region=US";
    return queryURL;
  }
  
  
  public String toString() {
    DownloadModel model = getModel();
    return model==null ? "??" : model.getResources().getString(getConnectionID());
  }
  
  
}
