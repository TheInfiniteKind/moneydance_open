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
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;


/**
 * Created by sreilly -  02/11/2017 21:38
 */
public class AlphavantageConnection extends BaseConnection {
  
  public static final String PREFS_KEY = "alphavantage";
  
  public AlphavantageConnection(StockQuotesModel model) {
    super(PREFS_KEY, model, BaseConnection.HISTORY_SUPPORT | BaseConnection.EXCHANGE_RATES_SUPPORT);
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
   * Retrieve the current exchange rate for the given currency relative to the base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  @Override
  public void updateExchangeRate(DownloadInfo downloadInfo) {
    String baseCurrencyID = downloadInfo.relativeCurrency.getIDString().toUpperCase();
    if(!downloadInfo.isValidForDownload) return;
    
    String apiKey = getAPIKey(getModel(), false);
    if(apiKey==null) {
      downloadInfo.recordError(getModel(), "No Alphavantage API Key Provided");
      return;
    }
    
    String urlStr = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"+
                    "&from_currency="+ SQUtil.urlEncode(downloadInfo.fullTickerSymbol) +
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
    
    try {
      URL url = new URL(urlStr);
      ByteArrayOutputStream bout = new ByteArrayOutputStream();
      IOUtils.copyStream(url.openConnection().getInputStream(), bout);
      JsonReader jsonReader = new JsonReader(new InputStreamReader(new ByteArrayInputStream(bout.toByteArray()), StandardCharsets.UTF_8));
      Gson gson = new Gson();
      Map gsonData = gson.fromJson(jsonReader, Map.class);
      
      Object rateInfoObj = gsonData.get("Realtime Currency Exchange Rate");
      if (rateInfoObj instanceof Map) {
        Map rateInfo = (Map) rateInfoObj;
        Object rateObj = rateInfo.get("5. Exchange Rate");
        if (rateObj != null) {
          double rate = StringUtils.parseDouble(String.valueOf(rateObj), -1.0, '.');
          if (rate > 0) {
            downloadInfo.setRate(1 / rate);
          }
        }
      }
      try {
        downloadInfo.setTestMessage(new String(bout.toByteArray(), "UTF8"));
      } catch (Throwable t){}
    } catch (Exception connEx) {
      downloadInfo.recordError(getModel(), "Connection Error: "+connEx);
    }
  }
  
  protected String getCurrentPriceHeader() {
    return "date,open,high,low,close,adjusted_close,volume,dividend_amount,splitdividendevents";
    //return "date,open,high,low,close,volume";
  }

  public String getHistoryURL(String fullTickerSymbol) {
    String apiKey = getAPIKey(getModel(), false);
    return apiKey==null ? null :
           "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+SQUtil.urlEncode(fullTickerSymbol)+"&apikey="+SQUtil.urlEncode(apiKey)+"&datatype=csv";
  }



  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  @Override
  public void updateSecurity(DownloadInfo downloadInfo) {
    System.err.println("alphavantage: getting history for "+downloadInfo.fullTickerSymbol);
    String urlStr = getHistoryURL(downloadInfo.fullTickerSymbol);
    if (urlStr == null) {
      // this basically means that an API key wasn't available
      downloadInfo.recordError(model, "No API Key Available");
      return;
    }
    
    SimpleDateFormat defaultDateFormat = getExpectedDateFormat(true);
    char decimal = model.getPreferences().getDecimalChar();
    SnapshotImporterFromURL importer = 
      new SnapshotImporterFromURL(urlStr, getCookie(), model.getResources(),
                                  downloadInfo, defaultDateFormat, 
                                  TimeZone.getTimeZone(getTimeZoneID()), decimal);
    importer.setColumnsFromHeader(getCurrentPriceHeader());
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
    
    if(downloadInfo.fullTickerSymbol.endsWith(".L") && recordList.size() > 1) {
      // special case when Alphavantage provides the first (aka current date) price in pence instead of GBP for some LSE securities
      StockRecord first = recordList.get(0);
      StockRecord second = recordList.get(1);
      if(first.closeRate > (second.closeRate/100)*0.9 && first.closeRate < (second.closeRate/100)*1.1) {
        for(int i=recordList.size()-1; i>=1; i--) { // adjust all but the first entry
          StockRecord record = recordList.get(i);
          record.closeRate /= 100;
          record.highRate /= 100;
          record.lowRate /= 100;
          record.open /= 100;
        }
      }
    }
    downloadInfo.addHistoryRecords(recordList);
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
    
    CurrencyTable ctable = book.getCurrencies();
    CurrencyType usd = new CurrencyType(ctable);
    usd.setCurrencyType(CurrencyType.Type.CURRENCY);
    usd.setIDString("USD");
    ctable.setBaseType(usd);
    
    model.setData(book);
    AlphavantageConnection conn = new AlphavantageConnection(model);

    List<DownloadInfo> currencies = new ArrayList<>();
    List<DownloadInfo> securities = new ArrayList<>();
    
    if(args[argIdx].equals("-x")) {
      argIdx++;
      for(; argIdx < args.length; argIdx++) {
        String symbol = args[argIdx];
        CurrencyType currency = ctable.getCurrencyByIDString(symbol);
        if(currency==null) {
          currency = new CurrencyType(ctable);
          currency.setCurrencyType(CurrencyType.Type.CURRENCY);
          currency.setIDString(symbol);
          ctable.addCurrencyType(currency);
        }
        currencies.add(new DownloadInfo(currency, conn));
      }
    } else {
      for(; argIdx < args.length; argIdx++) {
        String symbol = args[argIdx];
        CurrencyType security = ctable.getCurrencyByTickerSymbol(symbol);
        if(security==null) {
          security = new CurrencyType(ctable);
          security.setCurrencyType(CurrencyType.Type.SECURITY);
          security.setTickerSymbol(symbol);
          security.setName(symbol);
          security.setIDString("^"+symbol);
          security.setDecimalPlaces(4);
          ctable.addCurrencyType(security);
        }
        securities.add(new DownloadInfo(security, conn));
      }
    }
    
    conn.updateExchangeRates(currencies);
    conn.updateSecurities(securities);
  }

}
