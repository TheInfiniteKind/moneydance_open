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
  protected final StockQuotesModel model;
  private final SimpleDateFormat DEFAULT_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
  
  private BaseConnection() {
    model = null;
    _capabilities = 0;
    this.connectionID = "test";
  }
  
  public BaseConnection(String connectionID, StockQuotesModel model, final int capabilities) {
    this.connectionID = connectionID;
    this.model = model;
    this._capabilities = capabilities;
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
  public abstract String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange);


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
                                    100.0f / (float)currenciesToUpdate.size();
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
        message = downloadInfo.buildRateDisplayText(model);
        logMessage = downloadInfo.buildRateLogText(model);
      }
      model.showProgress(progressPercent, message);
      if(Main.DEBUG_YAHOOQT) System.err.println(logMessage);
      didUpdateItem(downloadInfo);
    }
    
    return true;
  }
  
  public boolean updateSecurities(List<DownloadInfo> securitiesToUpdate) {
    ResourceProvider res = model.getResources();
    float progressPercent = 0.0f;
    final float progressIncrement = securitiesToUpdate.isEmpty() ? 1.0f :
                                    100.0f / (float)securitiesToUpdate.size();
    boolean success = true;
    for (DownloadInfo downloadInfo : securitiesToUpdate) {
      System.err.println("updating currency: "+downloadInfo.security+" ("+downloadInfo.fullTickerSymbol+")");
      updateSecurity(downloadInfo);
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
        message = downloadInfo.buildRateDisplayText(model);
        logMessage = downloadInfo.buildRateLogText(model);
      }
      model.showProgress(progressPercent, message);
      if(Main.DEBUG_YAHOOQT) System.err.println(logMessage);
      //        } catch (Exception error) {
      //          downloadException = error;
      //          String message = MessageFormat.format(
      //            resources.getString(L10NStockQuotes.ERROR_DOWNLOADING_FMT),
      //            resources.getString(L10NStockQuotes.RATES),
      //            error.getLocalizedMessage());
      //          model.showProgress(0f, message);
      //          if(Main.DEBUG_YAHOOQT) System.err.println(MessageFormat.format("Error while downloading Currency Exchange Rates: {0}",
      //                                                                         error.getMessage()));
      //          error.printStackTrace();
      //          success = false;
      //        }

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
    final Account root = model.getRootAccount();
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

  /**
   * Return the currency appropriate for the price quotes for the given security. For example a
   * U.S. stock is quoted in U.S. Dollars but a Brazilian stock could be quoted in Brazilian reals.
   * @param securityCurrency The security to query.
   * @return The currency that price quotes should use, or <code>null</code> if it cannot be
   * determined.
   */
  public CurrencyType getPriceCurrency(CurrencyType securityCurrency) {
    // first check for a currency override in the symbol
    SymbolData parsedSymbol = SQUtil.parseTickerSymbol(securityCurrency);
    if (parsedSymbol == null) return null;
    CurrencyTable cTable = model.getRootAccount() == null ? null : model.getRootAccount().getBook().getCurrencies();
    if (cTable == null) return null;
    if (!SQUtil.isBlank(parsedSymbol.currencyCode)) {
      // see if the override currency exists in the file
      CurrencyType override = cTable.getCurrencyByIDString(parsedSymbol.currencyCode);
      if (override != null) return override;
    }
    StockExchange exchange = getExchangeForSecurity(parsedSymbol, securityCurrency);
    String fullTickerSymbol = getFullTickerSymbol(parsedSymbol, exchange);
    if (fullTickerSymbol == null) return null;
    String priceCurrencyId = getCurrencyCodeForQuote(securityCurrency.getTickerSymbol(), exchange);
    // get the currency that the prices are specified in
    return cTable.getCurrencyByIDString(priceCurrencyId);
  }

  /**
   * Obtain the associated stock exchange for a particular security. This method first checks if
   * the user has put any overrides in the security symbol. An override can be a Google prefix
   * (such as 'LON:') or a Yahoo suffix (such as '.L'). If an override exists and maps to an
   * exchange, then that exchange is returned. Otherwise the exchange listed in the symbol map
   * for the security is used.
   * @param symbol           The parsed symbol along with any overrides entered by the user.
   * @param securityCurrency The security currency.
   * @return The appropriate stock exchange definition to use for the given security.
   */
  protected StockExchange getExchangeForSecurity(SymbolData symbol, CurrencyType securityCurrency) {
    if (!SQUtil.isBlank(symbol.prefix)) {
      // check for a Google prefix override
      StockExchange result = model.getExchangeList().findByGooglePrefix(symbol.prefix);
      if (result != null) return result;
    }
    if (!SQUtil.isBlank(symbol.suffix)) {
      // check for a Yahoo exchange suffix override
      StockExchange result = model.getExchangeList().findByYahooSuffix(symbol.suffix);
      if (result != null) return result;
    }
    // go with the exchange the user assigned to the security
    return model.getSymbolMap().getExchangeForCurrency(securityCurrency);
  }
  
  protected String getTimeZoneID() {
    // the default time zone is EDT in the U.S.
    return "America/New_York";  // could possibly also use 'US/Eastern'
  }

  protected SimpleDateFormat getExpectedDateFormat(boolean getFullHistory) {
    CustomDateFormat userDateFormat = model.getPreferences().getShortDateFormatter();
    if (userDateFormat == null) return DEFAULT_DATE_FORMAT;
    return new SimpleDateFormat(userDateFormat.getPattern());
  }

  protected StockQuotesModel getModel() { return model; }

  protected String getCookie() { return null; }
  
  
  //////////////////////////////////////////////////////////////////////////////////////////////


  protected DownloadException buildDownloadException(DownloadInfo securityCurrency, int result) {
    String message;
    final ResourceProvider resources = model.getResources();
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
  


  
  

}