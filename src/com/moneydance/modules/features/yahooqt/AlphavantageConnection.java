package com.moneydance.modules.features.yahooqt;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;
import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.*;
import com.moneydance.awt.*;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.lang.reflect.InvocationTargetException;
import java.net.*;
import java.io.*;
import java.util.Map;


/**
 * Created by sreilly -  02/11/2017 21:38
 */
public class AlphavantageConnection extends BaseConnection {
  
  public static final String PREFS_KEY = "alphavantage";
  
  public AlphavantageConnection(StockQuotesModel model) {
    super(model, BaseConnection.HISTORY_SUPPORT | BaseConnection.EXCHANGE_RATES_SUPPORT);
  }
  
  private static String cachedAPIKey = null;
  private static long suppressAPIKeyRequestUntilTime = 0;
  
  private static synchronized String getAPIKey(final StockQuotesModel model) {
    if(cachedAPIKey!=null) return cachedAPIKey;
    
    if(model==null) return null;
    
    AccountBook book = model.getBook();
    if(book==null) return null;
    
    final Account root = book.getRootAccount();
    String apiKey = root.getParameter("alphavantage.apikey", null);
    if( ! com.infinitekind.util.StringUtils.isBlank(apiKey)) {
      return apiKey;
    }
    
    if(suppressAPIKeyRequestUntilTime > System.currentTimeMillis()) { // further requests for the key have been suppressed
      return null;
    }
    
    final String inputString = null;
    Runnable uiActions = new Runnable() {
      @Override
      public void run() {
        JPanel p = new JPanel(new GridBagLayout());
        AbstractAction signupAction = new AbstractAction() {
          @Override
          public void actionPerformed(ActionEvent e) {
            model.showURL("https://infinitekind.com/alphavantage");
          }
        };
        signupAction.putValue(Action.NAME, model.getResources().getString("alphavantage.apikey_action"));
        JLinkLabel linkButton = new JLinkLabel(signupAction);
        p.add(new JTextPanel(model.getResources().getString("alphavantage.apikey_msg")), 
              GridC.getc(0,0).wxy(1,1));
        p.add(linkButton, 
              GridC.getc(0,1).center().insets(12,16,0,16));
        while(true) {
          String inputString = JOptionPane.showInputDialog(null, p, "title", JOptionPane.QUESTION_MESSAGE);
          if(inputString==null) { // the user canceled the API key request, so let's not ask again for 5 minutes
            suppressAPIKeyRequestUntilTime = System.currentTimeMillis() + 1000 * 60 * 5;
            return;
          }
          
          if(!SQUtil.isEmpty(inputString) && !inputString.equals(JOptionPane.UNINITIALIZED_VALUE)) {
            root.setParameter("alphavantage.apikey", inputString);
            root.syncItem();
            cachedAPIKey = inputString;
            return;
          } else {
            // the user left the field blank or entered an invalid key
            model.getGUI().beep();
          }
        }
      }
    };
    
    if(SwingUtilities.isEventDispatchThread()) {
      uiActions.run();
    } else {
      try {
        SwingUtilities.invokeAndWait(uiActions);
      } catch (Exception e) {
        e.printStackTrace();
      }
    }
    return cachedAPIKey;
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
    
    String apiKey = getAPIKey(getModel());
    if(apiKey==null) return null;
    
    String urlStr = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"+
                    "&from_currency="+ SQUtil.urlEncode(currencyID) +
                    "&to_currency=" + SQUtil.urlEncode(baseCurrencyID) +
                    "&apikey="+SQUtil.urlEncode(apiKey);
    
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
    ByteArrayOutputStream bout = new ByteArrayOutputStream();
    IOUtils.copyStream(url.openConnection().getInputStream(), bout);
    JsonReader jsonReader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(bout.toByteArray()), "UTF8"));
    Gson gson = new Gson();
    Map gsonData = gson.fromJson(jsonReader, Map.class);
    
    Object rateInfoObj = gsonData.get("Realtime Currency Exchange Rate");
    if(rateInfoObj != null && rateInfoObj instanceof Map) {
      Map rateInfo = (Map) rateInfoObj;
      Object rateObj = rateInfo.get("5. Exchange Rate");
      if (rateObj != null) {
        double rate = StringUtils.parseDouble(String.valueOf(rateObj), -1.0, '.');
        if (rate > 0) {
          return new ExchangeRate(1 / rate);
        }
      }
    }
    
    return new ExchangeRate(-1.0);
  }
  
  protected String getCurrentPriceHeader() {
    return "date,open,high,low,close,volume";
  }

  protected boolean allowAutodetect() {return false;}
  
  public String getId() { return PREFS_KEY; }
  

  @Override
  public String getHistoryURL(String fullTickerSymbol, DateRange dateRange) {
    return getCurrentPriceURL(fullTickerSymbol);
  }

  @Override
  public String getCurrentPriceURL(String fullTickerSymbol) {
    String apiKey = getAPIKey(getModel());
    return apiKey==null ? null : 
           "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+SQUtil.urlEncode(fullTickerSymbol)+"&apikey="+SQUtil.urlEncode(apiKey)+"&datatype=csv";
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
