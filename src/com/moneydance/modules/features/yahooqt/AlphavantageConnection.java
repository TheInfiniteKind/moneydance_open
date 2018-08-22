package com.moneydance.modules.features.yahooqt;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;
import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.*;
import com.moneydance.awt.*;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.net.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
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
  private int connectionThrottleCounter = 0;
  
  
  /**
   * Alphavantage connections should be throttled to approximately one every 1.1 seconds
   */
  public long getPerConnectionThrottleTime() {
    connectionThrottleCounter++;
    return 30000;
//    if(connectionThrottleCounter%4 == 0) {
//      return 20000; // every Nth connection, delay for 15 seconds
//    } else {
//      return 10000; // pause for 1.5 seconds after each connection
//    }
  }
  
  
  static synchronized String getAPIKey(final StockQuotesModel model, final boolean evenIfAlreadySet) {
    if(!evenIfAlreadySet && cachedAPIKey!=null) return cachedAPIKey;
    
    if(model==null) return null;
    
    AccountBook book = model.getBook();
    if(book==null) return null;
    
    final Account root = book.getRootAccount();
    String apiKey = root.getParameter("alphavantage.apikey", 
                                      model.getPreferences().getSetting("alphavantage_apikey", null));
    if(!evenIfAlreadySet && !com.infinitekind.util.StringUtils.isBlank(apiKey)) {
      return apiKey;
    }
    
    if(!evenIfAlreadySet && suppressAPIKeyRequestUntilTime > System.currentTimeMillis()) { // further requests for the key have been suppressed
      return null;
    }
    
    final String existingAPIKey = apiKey;
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
        String defaultAPIKey = existingAPIKey != null ? existingAPIKey : "";
        signupAction.putValue(Action.NAME, model.getResources().getString("alphavantage.apikey_action"));
        JLinkLabel linkButton = new JLinkLabel(signupAction);
        p.add(new JTextPanel(model.getResources().getString("alphavantage.apikey_msg")), 
              GridC.getc(0,0).wxy(1,1));
        p.add(linkButton, 
              GridC.getc(0,1).center().insets(12,16,0,16));
        while(true) {
          String inputString = JOptionPane.showInputDialog(null, p, defaultAPIKey);
          if(inputString==null) { // the user canceled the prompt, so let's not ask again for 5 minutes unless this prompt was forced
            if(!evenIfAlreadySet) {
              suppressAPIKeyRequestUntilTime = System.currentTimeMillis() + 1000 * 60 * 5;
            }
            return;
          }
          
          if(!SQUtil.isEmpty(inputString) && !inputString.equals(JOptionPane.UNINITIALIZED_VALUE)) {
            root.setParameter("alphavantage.apikey", inputString);
            model.getPreferences().setSetting("alphavantage_apikey", inputString);
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
      if(marketID.contains("-")) {
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
   * Retrieve the current exchange rates for the given currency and base
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
    
    String apiKey = getAPIKey(getModel(), false);
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
    JsonReader jsonReader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(bout.toByteArray()), StandardCharsets.UTF_8));
    Gson gson = new Gson();
    Map gsonData = gson.fromJson(jsonReader, Map.class);
    ExchangeRate downloadedRate = null;
    
    Object rateInfoObj = gsonData.get("Realtime Currency Exchange Rate");
    if(rateInfoObj != null && rateInfoObj instanceof Map) {
      Map rateInfo = (Map) rateInfoObj;
      Object rateObj = rateInfo.get("5. Exchange Rate");
      if (rateObj != null) {
        double rate = StringUtils.parseDouble(String.valueOf(rateObj), -1.0, '.');
        if (rate > 0) {
          downloadedRate = new ExchangeRate(1 / rate);
        }
      }
    }
    
    if(downloadedRate==null) {
      downloadedRate = new ExchangeRate(-1.0);
    }
    try {
      downloadedRate.setTestMessage(new String(bout.toByteArray(), "UTF8"));
    } catch (Throwable t){} 
    
    return downloadedRate;
  }
  
  protected String getCurrentPriceHeader() {
    return "date,open,high,low,close,adjusted_close,volume,dividend_amount,splitdividendevents";
    //return "date,open,high,low,close,volume";
  }

  protected boolean allowAutodetect() {return false;}
  
  public String getId() { return PREFS_KEY; }
  

  @Override
  public String getHistoryURL(String fullTickerSymbol, DateRange dateRange) {
    String apiKey = getAPIKey(getModel(), false);
    return apiKey==null ? null :
           "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+SQUtil.urlEncode(fullTickerSymbol)+"&apikey="+SQUtil.urlEncode(apiKey)+"&datatype=csv";
  }

  /**
   * Test method.
   * @param args Program arguments.
   * @throws Exception If an error occurs.
   */
  public static void main(String[] args) throws Exception {
    if(args.length < 2) {
      System.err.println("usage: <thiscommand> <alphavantage-apikey> [-x] <symbol>...");
      System.err.println(" -x : symbols are three digit currency codes instead of security/ticker symbols");
      System.exit(-1);
    }
    int argIdx = 0;
    cachedAPIKey = args[argIdx++];
    
    StockQuotesModel model = new StockQuotesModel(null);
    AccountBook book = AccountBook.fakeAccountBook();
    book.performPostLoadVerification();
    // setup a basic account structure
    Account rootAcct = book.getRootAccount();
    Account bankAcct = Account.makeAccount(book, Account.AccountType.BANK, rootAcct);
    bankAcct.setAccountName("Banking");
    bankAcct.syncItem();
    Account incAcct = Account.makeAccount(book, Account.AccountType.INCOME, rootAcct);
    incAcct.setAccountName("Misc Income");
    incAcct.syncItem();
    Account expAcct = Account.makeAccount(book, Account.AccountType.EXPENSE, rootAcct);
    expAcct.setAccountName("Misc Expense");
    expAcct.syncItem();
    
    CurrencyTable currencies = book.getCurrencies();
    model.setData(book);
    AlphavantageConnection conn = new AlphavantageConnection(model);
    if(args[argIdx].equals("-x")) {
      argIdx++;
      for(; argIdx < args.length; argIdx++) {
        String symbol = args[argIdx];
        BaseConnection.ExchangeRate currentRate = conn.getCurrentRate(symbol, currencies.getBaseType().getIDString());
        System.out.println(" retrieved rate is for " + symbol + " is " + currentRate.getRate());
      }
    } else {
      DateRange dateRange = new DateRange(DateUtil.incrementDate(DateUtil.getStrippedDateInt(), 0, -2, 0),
                                          DateUtil.getStrippedDateInt());
      for(; argIdx < args.length; argIdx++) {
        String symbol = args[argIdx];
        CurrencyType security = currencies.getCurrencyByTickerSymbol(symbol);
        if(security==null) {
          security = new CurrencyType(currencies);
          security.setTickerSymbol(symbol);
          security.setName(symbol);
          security.setIDString("^"+symbol);
          security.setCurrencyType(CurrencyType.Type.SECURITY);
          security.setDecimalPlaces(4);
          currencies.addCurrencyType(security);
        }
        StockHistory history = conn.getHistory(security, dateRange, true);
        System.err.println(" retrieved history for ticker '"+symbol+"' with "+history.getRecordCount()+" records and "+history.getErrorCount()+" errors");
        for(int i=0; i<history.getRecordCount(); i++) {
          System.err.println(String.valueOf(history.getRecord(i)));
        }
      }
    }
  }

}
