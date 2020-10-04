/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.CustomDateFormat;

import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Constructor;
import java.text.MessageFormat;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * Base class for importing stock and currency prices. Derived classes provide specific
 * exchange rate and/or security price implementations.
 */
public abstract class BaseConnection {
  static final int HISTORY_SUPPORT = 1;
  static final int EXCHANGE_RATES_SUPPORT = 4;
  static final int ALL_SUPPORT = HISTORY_SUPPORT | EXCHANGE_RATES_SUPPORT;
  static final int FOREX_HISTORY_INTERVAL = 7; // snapshot minimum frequency, in days

  private final String connectionID;
  private final int _capabilities;
  protected final DownloadModel model;
  
  public BaseConnection(String connectionID, StockQuotesModel model, final int capabilities) {
    this.connectionID = connectionID;
    this._capabilities = capabilities;
    this.model = new DownloadModel(model, this);
  }

  public final String getConnectionID() {
    return this.connectionID;
  }
  
  /**
   * Given a raw ticker symbol, convert it to a full symbol by adding prefix or suffix appropriate
   * for the stock exchange.
   *
   * @param parsedSymbol    The raw ticker symbol, parsed into its various parts.
   * @param exchange        The selected stock exchange to use.
   * @return The full ticker symbol appropriate for the selected stock exchange.
   */
  public abstract String getFullTickerSymbol(SymbolData parsedSymbol, StockExchange exchange);

  /**
   * Given a ticker symbol, which could have an embedded currency (typically after the '-' symbol),
   * and return the currency code for the currency that should be used to interpret prices.
   * @param rawTickerSymbol The ticker symbol, potentially with an embedded currency.
   * @param exchange        The selected stock exchange to use.
   * @return the currency code from the ticker symbol, or if no embedded currency, the currency code
   * as specified by the given stock exchange.
   */
  public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange) {
    return null;
  }


  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  public abstract void updateExchangeRate(DownloadInfo downloadInfo);
  
  
//  /**
//   * Download price history for a security.
//   * @param securityInfo The information about the security to download, including symbol, date range, status, results, etc
//   * applying (for testing).
//   * @return The security price history that was downloaded.
//   * @throws DownloadException if an error occurs.
//   */
//  public abstract DownloadResult getHistory(DownloadResult securityInfo);
  
  
  /** Update the currencies in the given list */
  public boolean updateExchangeRates(List<DownloadInfo> currenciesToUpdate) {
    ResourceProvider res = model.getResources();
    float progressPercent = 0.0f;
    final float progressIncrement = currenciesToUpdate.isEmpty() ? 1.0f :
                                    1.0f / (float)currenciesToUpdate.size();
    for (DownloadInfo downloadInfo : currenciesToUpdate) {
      System.err.println("updating currency: "+downloadInfo.security+" ("+downloadInfo.fullTickerSymbol+")");
      updateExchangeRate(downloadInfo);
      double rate = downloadInfo.getRate();
      progressPercent += progressIncrement;
      final String message, logMessage;
      if (rate <= 0.0) {
        message = MessageFormat.format( res.getString(L10NStockQuotes.ERROR_EXCHANGE_RATE_FMT),
                                        downloadInfo.security.getIDString(),
                                        downloadInfo.relativeCurrency.getIDString());
        logMessage = MessageFormat.format("Unable to get rate from {0} to {1}",
                                          downloadInfo.security.getIDString(),
                                          downloadInfo.relativeCurrency.getIDString());
      } else {
        message = downloadInfo.buildRateDisplayText(model.getQuotesModel());
        logMessage = downloadInfo.buildRateLogText(model.getQuotesModel());
      }
      model.getQuotesModel().showProgress(progressPercent, message);
      if(Main.DEBUG_YAHOOQT) System.err.println(logMessage);
      didUpdateItem(downloadInfo);
    }
    
    return true;
  }
  
  public boolean updateSecurities(List<DownloadInfo> securitiesToUpdate) {
    ResourceProvider res = model.getQuotesModel().getResources();
    float progressPercent = 0.0f;
    final float progressIncrement = securitiesToUpdate.isEmpty() ? 1.0f :
                                    1.0f / (float)securitiesToUpdate.size();
    boolean success = true;
    for (DownloadInfo downloadInfo : securitiesToUpdate) {
      System.err.println("updating security: "+downloadInfo.security+" ("+downloadInfo.fullTickerSymbol+")");
      updateSecurity(downloadInfo);
      progressPercent += progressIncrement;
      final String message, logMessage;
      if (!downloadInfo.wasSuccess()) {
        message = MessageFormat.format( res.getString(L10NStockQuotes.ERROR_EXCHANGE_RATE_FMT),
                                        downloadInfo.security.getIDString(),
                                        downloadInfo.relativeCurrency.getIDString());
        logMessage = MessageFormat.format("Unable to get rate from {0} to {1}",
                                          downloadInfo.security.getIDString(),
                                          downloadInfo.relativeCurrency.getIDString());
      } else {
        message = downloadInfo.buildPriceDisplayText(model.getQuotesModel());
        logMessage = downloadInfo.buildPriceLogText(model.getQuotesModel());
      }
      model.getQuotesModel().showProgress(progressPercent, message);
      if(Main.DEBUG_YAHOOQT) System.err.println(logMessage);
      
      didUpdateItem(downloadInfo);
    }
    return Boolean.TRUE;
  }


  protected abstract void updateSecurity(DownloadInfo downloadInfo);
  
  
  /**
   * Define the default currency, which is the price currency that is to be used for the downloaded
   * quotes when the Default stock exchange is assigned to a security. The default implementation
   * specifies the U.S. Dollar as the default currency. If the default currency is not defined in
   * the current data file, the method does nothing.
   */
  public void setDefaultCurrency() {
    final Account root = model.getQuotesModel().getRootAccount();
    if (root == null) return;
    CurrencyType currency = root.getBook().getCurrencies().getCurrencyByIDString("USD");
    if (currency == null) return;
    StockExchange.DEFAULT.setCurrency(currency);
  }
  
  public boolean canGetHistory() {
    return ((_capabilities & HISTORY_SUPPORT) != 0);
  }

  public boolean canGetRates() {
    return ((_capabilities & EXCHANGE_RATES_SUPPORT) != 0);
  }
  
  /**
   * Return the number of milliseconds by which the connection should be throttled.
   * The default is zero.
   */
  public long getPerConnectionThrottleTime() {
    return 0;
  }
  
  
  /** 
   * This is called after an item is updated.  If the error parameter is non-null then it
   * means there was a problem performing the update.  The default implementation checks
   * for a per-connection/item throttling time and if it is a positive number will
   * sleep/wait for the appropriate number of milliseconds.
   */
  public void didUpdateItem(DownloadInfo downloadInfo) {
    long delay = getPerConnectionThrottleTime();
    if (delay > 0) {
      try {
        Thread.sleep(delay);
      } catch (InterruptedException e) {
        System.err.println(
          "Unexpected error while sleeping throttled connection: " + e);
      }
    }
  }

//  /**
//   * Return the currency appropriate for the price quotes for the given security. For example a
//   * U.S. stock is quoted in U.S. Dollars but a Brazilian stock could be quoted in Brazilian reals.
//   * @param securityCurrency The security to query.
//   * @return The currency that price quotes should use, or <code>null</code> if it cannot be
//   * determined.
//   */
//  public CurrencyType getPriceCurrency(CurrencyType securityCurrency) {
//    // first check for a currency override in the symbol
//    SymbolData parsedSymbol = SQUtil.parseTickerSymbol(securityCurrency);
//    if (parsedSymbol == null) return null;
//    CurrencyTable cTable = model.getRootAccount() == null ? null : model.getRootAccount().getBook().getCurrencies();
//    if (cTable == null) return null;
//    if (!SQUtil.isBlank(parsedSymbol.currencyCode)) {
//      // see if the override currency exists in the file
//      CurrencyType override = cTable.getCurrencyByIDString(parsedSymbol.currencyCode);
//      if (override != null) return override;
//    }
//    StockExchange exchange = downloadInfo.getExchangeForSecurity(parsedSymbol, securityCurrency);
//    String fullTickerSymbol = getFullTickerSymbol(parsedSymbol, exchange);
//    if (fullTickerSymbol == null) return null;
//    String priceCurrencyId = getCurrencyCodeForQuote(securityCurrency.getTickerSymbol(), exchange);
//    // get the currency that the prices are specified in
//    return cTable.getCurrencyByIDString(priceCurrencyId);
//  }
  
  protected String getTimeZoneID() {
    // the default time zone is EDT in the U.S.
    return "America/New_York";  // could possibly also use 'US/Eastern'
  }

  protected DownloadModel getModel() { return model; }

  protected String getCookie() { return null; }
  
  
  //////////////////////////////////////////////////////////////////////////////////////////////


  protected DownloadException buildDownloadException(DownloadInfo securityCurrency, int result) {
    String message;
    final ResourceProvider resources = model.getQuotesModel().getResources();
    switch (result) {
      case SnapshotImporter.ERROR_NO_INPUT_STREAM:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_INPUT_STREAM);
        break;
      case SnapshotImporter.ERROR_READ_INPUT:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_READ_INPUT);
        break;
      case SnapshotImporter.ERROR_NO_DATA:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_DATA);
        break;
      case SnapshotImporter.ERROR_READING_DATA:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_READING_DATA);
        break;
      case SnapshotImporter.ERROR_NO_VALID_DATA:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_VALID_DATA);
        break;
      case SnapshotImporter.ERROR_NOT_TEXT_DATA:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_NOT_TEXT_DATA);
        break;
      case SnapshotImporter.ERROR_NO_COLUMNS:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_COLUMNS);
        break;
      case SnapshotImporter.ERROR_MALFORMED_TEXT:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_MALFORMED_TEXT);
        break;
      case SnapshotImporter.ERROR_NO_HEADER:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_HEADER);
        break;
      case SnapshotImporter.ERROR_OTHER:
      default:
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_OTHER);
        break;
    }
    
    return new DownloadException(securityCurrency, message);
  }
  

  protected void buildMessageAndThrow(DownloadInfo securityCurrency, int result)
    throws DownloadException
  {
    DownloadException exception = buildDownloadException(securityCurrency, result);
    if(exception!=null) {
      throw exception;
    }
  }
  

  static StockQuotesModel createEmptyTestModel() {
    StockQuotesModel model = new StockQuotesModel(null);
    AccountBook book = AccountBook.fakeAccountBook();
    CurrencyUtil.createDefaultTable(book, "USD");
    for(CurrencyType curr : book.getCurrencies()) {
      curr.setCurrencyType(CurrencyType.Type.CURRENCY);
      curr.setDecimalPlaces(2);
      curr.setTickerSymbol("");
    }
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
    
    model.setData(book);

    InputStream englishInputStream = BaseConnection.class.getResourceAsStream(N12EStockQuotes.ENGLISH_PROPERTIES_FILE);
    try {
      final XmlResourceBundle englishBundle = new XmlResourceBundle(englishInputStream);
      model.setResources(new ResourceProvider() {
        @Override
        public String getString(String key) {
          return englishBundle.getString(key);
        }
      });
    } catch (IOException e) {
      e.printStackTrace();
      model.setResources(new ResourceProvider() {
        @Override
        public String getString(String key) {
          return "<<"+key+">>";
        }
      });
    }
    
    return model;
  }
  
  public static void runTests(BaseConnection currencyConnection, 
                              BaseConnection securityConnection,
                              String args[])
  {
    
    List<String> currencySymbols = new ArrayList<>();
    List<String> securitySymbols = new ArrayList<>();
    
    boolean exchangeRatesMode = false;
    for (String arg : args) {
      if (arg.equals("-x")) {
        exchangeRatesMode = true;
      } else {
        if(exchangeRatesMode) {
          currencySymbols.add(arg);
        } else {
          securitySymbols.add(arg);
        }
      }
    }

    if(currencySymbols.size()<=0 && securitySymbols.size()<=0) {
      currencySymbols.addAll(
        Arrays.asList("ADP","AED","AFA","ALL","ANG","AOK","ARA","ATS","AUD","AWG","BBD","BDT",
                      "BEF","BGL","BHD","BIF","BMD","BND","BOB","BRC","BSD","BTN","BUK","BWP",
                      "BZD","CAD","CHF","CLF","CLP","CNY","COP","CRC","CSK","CUP","CVE","CYP",
                      "DDM","DEM","DJF","DKK","DOP","DZD","ECS","EGP","ESP","ETB","FIM","FJD",
                      "FKP","FRF","GBP","GHC","GIP","GMD","GNF","GRD","GTQ","GWP","GYD","HKD",
                      "HNL","HTG","HUF","IDR","IEP","ILS","INR","IQD","IRR","ISK","ITL","JMD",
                      "JOD","JPY","KES","KHR","KMF","KPW","KRW","KWD","KYD","LAK","LBP","LKR",
                      "LRD","LSL","LUF","LYD","MAD","MGF","MNT","MOP","MRO","MTL","MUR","MVR",
                      "MWK","MXP","MYR","MZM","NGN","NIC","NLG","NOK","NPR","NZD","OMR","PAB",
                      "PEI","PGK","PHP","PKR","PLZ","PTE","PYG","QAR","ROL","RWF","SAR","SBD",
                      "SCR","SDP","SEK","SGD","SHP","SLL","SOS","SRG","STD","SUR","SVC","SYP",
                      "SZL","THB","TND","TOP","TPE","TRL","TTD","TWD","TZS","UGS","USD","UYP",
                      "VEB","VND","VUV","WST","YDD","YER","YUD","ZAR","ZMK","ZRZ","ZWD"));
      
      securitySymbols.addAll(
        Arrays.asList("DPL", "DTE", "DAI", "DCX", "DAN", "DHR", "DAC", "DRI", "DAR", "DVA", "DPM", "DCT",
                      "DF", "DE", "DLM", "DK", "DFY", "DFG", "DFP", "DAL", "DEL", "DLX", "DNR", "DFS", "HXM",
                      "DB", "DTK", "DT", "WMW", "DDR", "DVN", "DV", "DEX", "DEO", "DL", "DO", "DRH", "DSX",
                      "DHX", "DKS", "DBD", "DLR", "DDS", "DIN", "DYS", "DBX", "DLB", "DTG", "DM", "D", "DCP",
                      "DOM", "DPZ", "UFS", "DCI", "DRL", "DHT", "DEI", "DOV", "DDE", "DVD", "DPO", "DOW",
                      "DHI", "DPS", "RDY", "DWA", "DRC", "DW", "DRQ", "DST", "DSW", "DD", "DMH", "DCO",
                      "DUF", "DUK", "DRE", "DEP", "DFT", "DHG", "DRP", "DY", "DYN", "DX", "EME", "EJ", "UBC",
                      "UBG", "FUD", "UBM", "USV", "UBN", "PTD", "EXP", "NGT", "EGP", "EMN", "EK", "EV",
                      "ETJ", "ECL", "EIX", "EDR", "EW", "EFD", "EP", "EE", "EPB", "ELN", "ELU", "EQ", "AKO.A",
                      "AKO.B", "ERJ", "EMC", "EMS", "EBS", "ESC", "EMR", "EDE", "EIG", "EOC", "EDN", "ICA",
                      "ERI", "ELX", "ENB", "EEQ", "EEP", "ECA", "EAC", "ENP", "ENH", "EGN", "ENR", "EPL",
                      "ETP", "ETE", "ES", "ENI", "ENS", "EC", "E", "EBF", "NPO", "ESV", "ETM", "ETR", "EHB",
                      "EHA", "EHL", "EMQ", "EMO", "EPE", "EPD", "EPR", "EVC", "ENZ", "EOG", "EPC", "ENT",
                      "EFX", "EQT", "ELS", "EQY", "EQR", "RET", "ESE", "ESS", "EL", "ESL", "DEG", "ETH",
                      "EVR", "RE", "EBI", "EEE", "XCO", "EXM", "EXC", "XJT", "EXH", "EXR", "XOM", "FMC",
                      "FNB", "FPL", "HCE", "FDS", "FIC", "FA", "FCS", "FFH", "FRP", "FDO", "FNM", "FFG",
                      "AGM.A", "AGM", "FNA", "FRT", "FSS", "FII", "FDX", "FCH", "FMX", "FGP", "FOE", "FNF",
                      "FSC", "FIF", "FSF", "FSE", "FAC", "FAF", "FBP", "FCF", "FHN", "FR", "FMD", "FMR",
                      "FPO", "FEO", "FE", "FED", "FBC", "FSR", "FLE", "FTK", "FLO", "FLS", "FLR", "FTI",
                      "FL", "F", "FCJ", "FCZ", "FCE.B", "FCE.A", "FCY", "FRX", "FST", "FOR", "FIG", "FO",
                      "FCL", "FGC", "FTE", "BEN", "FC", "FT", "FRE", "FCX", "FMS", "FDP", "FBR", "FTR",
                      "FTO", "FRO", "FCN", "FUL", "FRM", "FBN", "GMT", "GFA", "AJG", "GBL", "GME", "GRS",
                      "GCI", "GPS", "GDI", "IT", "GET", "GEP", "BGC", "GD", "GE", "GIS", "GOM", "GNK", "GY",
                      "DNA", "GEC", "GEJ", "GGP", "GMR", "XGM", "RGM", "HGM", "GMS", "GRM", "GXM", "GBM",
                      "GPM", "GMA", "GSI", "GCO", "GWR", "GLS", "GED", "GEA", "GKM", "BGM", "G", "GPC", "GNW",
                      "GEO", "GGC", "GAR", "GAT", "GPW", "GPU", "GAH", "GPD", "GPJ", "GRB", "GGB", "GNA",
                      "GTY", "GA", "GIL", "GLG", "GLT", "GSK", "GLG.U", "GLG.UN", "GRT", "GCA", "GLP", "GPN",
                      "GEG", "GSL.UN", "GSL.U", "GSL", "GM", "GMW", "GJM", "GFI", "GG", "GOL", "GR", "GDP",
                      "GT", "IRE", "GPX", "GGG", "GTI", "GKK", "GVA", "GPK", "GTN.A", "GTN", "GAJ", "GAP",
                      "GNI", "GXP", "GB", "GBX", "GHL", "GEF.B", "GEF", "GFF", "GPI", "GBE", "GMK", "ASR",
                      "SAB", "CEL", "RC", "TMM", "GS", "GSC", "GNV", "GSH", "GFG", "GES", "GUQ", "GUL", "GUI",
                      "GLF", "GU"));
    }
    
    List<DownloadInfo> currencies = new ArrayList<>();
    List<DownloadInfo> securities = new ArrayList<>();

    if(securityConnection!=null) {
      CurrencyTable ctable = securityConnection.getModel().getBook().getCurrencies();
      for(String symbol : securitySymbols) {
        CurrencyType security = ctable.getCurrencyByTickerSymbol(symbol);
        if (security == null) {
          security = new CurrencyType(ctable);
          security.setCurrencyType(CurrencyType.Type.SECURITY);
          security.setTickerSymbol(symbol);
          security.setName(symbol);
          security.setIDString("^" + symbol);
          security.setDecimalPlaces(4);
          ctable.addCurrencyType(security);
        }
        securities.add(new DownloadInfo(security, securityConnection.getModel()));
      }
    }
    
    if(currencyConnection!=null) {
      CurrencyTable ctable = currencyConnection.getModel().getBook().getCurrencies();
      for (String symbol : currencySymbols) {
        CurrencyType currency = ctable.getCurrencyByIDString(symbol);
        if (currency == null) {
          currency = new CurrencyType(ctable);
          currency.setCurrencyType(CurrencyType.Type.CURRENCY);
          currency.setName(symbol);
          currency.setIDString(symbol);
          currency.setDecimalPlaces(2);
          ctable.addCurrencyType(currency);
        }
        currencies.add(new DownloadInfo(currency, currencyConnection.getModel()));
      }
    }
    
    if(currencyConnection!=null) currencyConnection.updateExchangeRates(currencies);
    if(securityConnection!=null) securityConnection.updateSecurities(securities);
  }
  
}
