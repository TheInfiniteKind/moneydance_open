package com.moneydance.modules.features.yahooqt;

import com.google.gson.stream.JsonReader;
import com.infinitekind.moneydance.model.*;
import com.moneydance.util.*;
import java.net.*;
import java.io.*;


/**
 * Created by sreilly -  02/11/2017 21:38
 */
public class AlphavantageConnection extends BaseConnection {

  public static final String PREFS_KEY = "alphavantage";
  private static final String API_KEY = "O8AQ";
  
  public AlphavantageConnection(StockQuotesModel model) {
    super(model, BaseConnection.HISTORY_SUPPORT | BaseConnection.EXCHANGE_RATES_SUPPORT);
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
      if(marketID.indexOf("-")>=0) {
        // the currency ID was encoded along with the market ID
        return StringUtils.fieldIndex(marketID, '-', 1);
      }
    }
    return exchange.getCurrencyCode();
  }
  
  public String toString() {
    StockQuotesModel model = getModel();
    return model==null ? "" : model.getResources().getString("alphavantage");
  }
  
  /**
   * Retrieve the current information for the given stock ticker symbol.
   * @param currencyID      The string identifier of the currency to start with ('from').
   * @param baseCurrencyID  The string identifier of the currency to end with ('to').
   * @return The downloaded exchange rate definition.
   * @throws Exception If an error occurs during download.
   */
  public ExchangeRate getCurrentRate(String currencyID, String baseCurrencyID)
    throws Exception
  {
    currencyID = currencyID.toUpperCase().trim();
    baseCurrencyID = baseCurrencyID.toUpperCase().trim();
    if (currencyID.length() != 3 || baseCurrencyID.length() != 3)
      return null;

    String urlStr = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"+
                    "&from_currency="+ SQUtil.urlEncode(currencyID) +
                    "&to_currency=" + SQUtil.urlEncode(baseCurrencyID) +
                    "&apikey="+SQUtil.urlEncode(API_KEY);
    
    /*
     {
     "Realtime Currency Exchange Rate": {
         "1. From_Currency Code": "USD",
         "2. From_Currency Name": "United States Dollar",
         "3. To_Currency Code": "EUR",
         "4. To_Currency Name": "Euro",
         "5. Exchange Rate": "0.86488300",
         "6. Last Refreshed": "2017-11-07 11:46:52",
         "7. Time Zone": "UTC"
      }
    }
    */
    
    URL url = new URL(urlStr);
    Reader rdr = new InputStreamReader(url.openConnection().getInputStream(), "UTF8");

    double rate = -1;
    JsonReader jsonReader = new JsonReader(rdr);
    jsonReader.beginObject();
    if(jsonReader.hasNext()) {
      String wrapperName = jsonReader.nextName(); // should be Realtime Currency Exchange Rate
      jsonReader.beginObject();
      while (jsonReader.hasNext()) {
        String objName = jsonReader.nextName();
        String objVal = jsonReader.nextString();
        if(objName!=null && objName.equals("5. Exchange Rate")) {
          rate = com.infinitekind.util.StringUtils.parseDouble(objVal, -1.0,'.');
          if(rate > 0 ) {
            rate = 1/rate;
          }
        }
      }
      jsonReader.endObject();
      jsonReader.endObject();
    }
    
    return new ExchangeRate(rate);
  }

  
  protected String getCurrentPriceHeader() {
    return "date,open,high,low,close,volume";
  }

  public String getId() { return PREFS_KEY; }
  

  @Override
  public String getHistoryURL(String fullTickerSymbol, DateRange dateRange) {
    return getCurrentPriceURL(fullTickerSymbol);
  }

  @Override
  public String getCurrentPriceURL(String fullTickerSymbol) {
    return "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+SQUtil.urlEncode(fullTickerSymbol)+"&apikey="+SQUtil.urlEncode(API_KEY)+"&datatype=csv";
  }

  /**
   * Test method.
   * @param args Program arguments.
   * @throws Exception If an error occurs.
   */
  public static void main(String[] args) throws Exception {
    AlphavantageConnection conn = new AlphavantageConnection(null);
    BaseConnection.ExchangeRate currentRate = conn.getCurrentRate("USD", "EUR");
    System.out.println("rate is " + currentRate.getRate());
  }

}
