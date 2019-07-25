package com.moneydance.modules.features.yahooqt;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.infinitekind.util.DateUtil;
import com.infinitekind.util.StringUtils;

import java.io.InputStreamReader;
import java.io.Reader;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


/**
 * Created by sreilly -  02/11/2017 21:38
 */
public class IEXConnection extends BaseConnection {
  
  public static final String PREFS_KEY = "iex";

  private DateFormat dateFormat;
  
  //Get API token from - https://iexcloud.io/cloud-login#/register/
  public static final String API_TOKEN = "Tpk_************************";
  
  public IEXConnection(StockQuotesModel model) {
    super(PREFS_KEY, model, HISTORY_SUPPORT);
    dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    dateFormat.setLenient(true);
  }
  
  /**
   * Alphavantage connections should be throttled to approximately one every 1.1 seconds
   */
  public long getPerConnectionThrottleTime() {
    return 100; // throttle only so we dont exceed 10 requests per second
  }
  
  @Override
  public String getFullTickerSymbol(SymbolData parsedSymbol, StockExchange exchange) {
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
  public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange) {
    if (SQUtil.isBlank(rawTickerSymbol)) return null;
    // check if this symbol overrides the exchange and the currency code
    int periodIdx = rawTickerSymbol.lastIndexOf('.');
    if(periodIdx>0) {
      String marketID = rawTickerSymbol.substring(periodIdx+1);
      if(marketID.contains("-")) {
        // the currency ID was encoded along with the market ID
        return StringUtils.fieldIndex(marketID, '-', 1);
      }
    }
    return exchange.getCurrencyCode();
  }
  
  public String toString() {
    return model==null ? "" : model.getResources().getString("iextrading");
  }


  /** Update the currencies in the given list */
  @Override
  public boolean updateExchangeRates(List<DownloadInfo> currenciesToUpdate) {
    for(DownloadInfo downloadInfo : currenciesToUpdate) {
      downloadInfo.recordError("Implementation error: IEXTrading does not provide exchange rates");
    }
    return false;
  }

  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  public void updateExchangeRate(DownloadInfo downloadInfo) {
    downloadInfo.recordError("Implementation error: IEXTrading does not provide exchange rates");
  }
  
  protected void updateSecurity(DownloadInfo downloadInfo) {
    downloadInfo.recordError("Implementation error: IEXTrading connection should batch requests");
  }
  
  /**
   * Download price history for a security.
   * @param securityCurrencies The list of securities to be updated
   * applying (for testing).
   * @return The security price history that was downloaded.
   */
  @Override 
  public boolean updateSecurities(List<DownloadInfo> securityCurrencies) {
    // if we have more than 200 securities in the list, split this into multiple updates...
    boolean success = false;
    int startIdx = 0;
    while (startIdx < securityCurrencies.size()) {
      success = updateLimitedSecurities(securityCurrencies.subList(startIdx, Math.min(startIdx+100, securityCurrencies.size())));
      startIdx += 100;
    }
    return success;
  }
  
    
  private boolean updateLimitedSecurities(List<DownloadInfo> securityCurrencies) {  
    char decimal = model.getDecimalDisplayChar();
    StringBuilder symbolList = new StringBuilder();
    
    Map<String, DownloadInfo> results = new HashMap<>();
    // build the symbol list for all valid securities and a SecurityDownloadInfo list to hold the symbols and results
    for(DownloadInfo secInfo : securityCurrencies) {
      if(symbolList.length()>0) symbolList.append(",");
      symbolList.append(SQUtil.urlEncode(secInfo.fullTickerSymbol));
      results.put(secInfo.fullTickerSymbol.toLowerCase(), secInfo);
    }
    
    String urlStr = "https://cloud.iexapis.com/stable/stock/market/batch?symbols="
                    + symbolList.toString()
                    + "&types=chart&range=1m"
                    + "&token=" + API_TOKEN;
    System.err.println("getting history using url: "+ urlStr);

    Map<String,Map<String,List<Map<String,Object>>>> info;
    try {
      URL url = new URL(urlStr);
      Reader reader = new InputStreamReader(url.openConnection().getInputStream(),
                                            StandardCharsets.UTF_8);
      //JsonReader jsonReader = new JsonReader(reader);
      Gson gson = new Gson();
      //Map gsonData = gson.fromJson(jsonReader, Map.class);
      info = gson.fromJson(reader, new TypeToken<Map<String, Map<String, List<Map<String, Object>>>>>() {
      }.getType());
    } catch (Exception e) {
      
      return false;
    }
    
    for(String tickerStr : info.keySet()) {
      DownloadInfo downloadInfo = results.get(tickerStr.toLowerCase());
      if(downloadInfo==null) {
        System.err.println("iextrading: received result for unrecognized security '"+tickerStr+"'");
        continue;
      }
      if(!downloadInfo.isValidForDownload) {
        System.err.println("iextrading: received result for invalid security '"+tickerStr+"'. That shouldn't happen.");
        continue;
      }
      List<Map<String,Object>> chartInfo = info.get(tickerStr).get("chart");
      if(chartInfo==null) {
        System.err.println("iextrading: response for symbol "+tickerStr+" doesn't include 'chart' data: "+info.get(tickerStr).keySet());
        continue;
      }
      
      List<StockRecord> snaps = new ArrayList<>();
      for(Map<String,Object> historyInfo : chartInfo) {
        try {
          
        /* parse the JSON dictionary for one snapshot
        {
        "date": "2018-09-14",
        "open": 225.75,
        "high": 226.84,
        "low": 222.522,
        "close": 223.84,
        "volume": 31999289,
        "unadjustedVolume": 31999289,
        "change": -2.57,
        "changePercent": -1.135,
        "vwap": 224.319,
        "label": "Sep 14",
        "changeOverTime": 0.038893530121600274
        }
        */
          
          StockRecord snap = new StockRecord();
          String dateStr = String.valueOf(historyInfo.getOrDefault("date", "0000-00-00"));
          snap.date = DateUtil.convertDateToInt(dateFormat.parse(dateStr));
          snap.dateTimeGMT = DateUtil.lastMinuteInDay(DateUtil.convertIntDateToLong(snap.date)).getTime();
          snap.volume = Math.round(Double.parseDouble(String.valueOf(historyInfo.getOrDefault("volume", "0"))));
          
          snap.lowRate = safeInversion(Double.parseDouble(String.valueOf(historyInfo.getOrDefault("low", "0"))));
          snap.highRate = safeInversion(Double.parseDouble(String.valueOf(historyInfo.getOrDefault("high", "0"))));
          snap.closeRate = safeInversion(Double.parseDouble(String.valueOf(historyInfo.getOrDefault("close", "0"))));
          snap.open =  safeInversion(Double.parseDouble(String.valueOf(historyInfo.getOrDefault("open", "0"))));
          
          long amount = (snap.closeRate == 0.0) ? 0 : downloadInfo.relativeCurrency.getLongValue(1.0 / snap.closeRate);
          snap.priceDisplay = downloadInfo.relativeCurrency.formatFancy(amount, decimal);
          snaps.add(snap);
        } catch (Exception e) {
          System.err.println("iextrading: error reading record: "+historyInfo);
          e.printStackTrace(System.err);
          downloadInfo.errors.add(new DownloadException(downloadInfo, "Error reading record", e));
        }
      }
      downloadInfo.addHistoryRecords(snaps);
      downloadInfo.buildPriceDisplay(downloadInfo.relativeCurrency, decimal);
    }
    
    // now scan the securities and mark any for which we didn't get data with the appropriate errors/messages
    for(DownloadInfo downloadInfo : securityCurrencies) {
      if(downloadInfo.errors.size()<=0 && !downloadInfo.wasSuccess()) {
        downloadInfo.recordError("No data received");
      }
    }
    return true;
  }
  
  
  private static double safeInversion(double rate) {
    return rate==0.0 ? 0.0 : 1/rate;
  }
  
  
  public static void main(String[] args) throws Exception {
    IEXConnection iexConn = new IEXConnection(createEmptyTestModel());
    BaseConnection.runTests(null, iexConn, args);
  }
  
}
