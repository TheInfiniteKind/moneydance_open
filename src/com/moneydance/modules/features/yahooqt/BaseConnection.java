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
import java.util.List;
import java.util.TimeZone;

/**
 * Base class for importing stock and currency prices. Derived classes provide specific
 * implementation.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public abstract class BaseConnection {
  static final int HISTORY_SUPPORT = 1;
  static final int EXCHANGE_RATES_SUPPORT = 4;
  static final int ALL_SUPPORT = HISTORY_SUPPORT | EXCHANGE_RATES_SUPPORT;
  
  private final int _capabilities;
  private final StockQuotesModel _model;
  private final TimeZone _timeZone;
  private final SimpleDateFormat DEFAULT_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
  
  public BaseConnection(StockQuotesModel model, final int capabilities) {
    _model = model;
    _capabilities = capabilities;
    _timeZone = TimeZone.getTimeZone(getTimeZoneID());
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
   * Given a ticker symbol, return the URL to obtain historical prices for a security.
   * @param fullTickerSymbol The ticker symbol to use.
   * @param dateRange        The date range to obtain history for.
   * @return The URL to use to obtain historical quotes from.
   */
  public abstract String getHistoryURL(String fullTickerSymbol, DateRange dateRange);

  /**
   * Define the default currency, which is the price currency that is to be used for the downloaded
   * quotes when the Default stock exchange is assigned to a security. The default implementation
   * specifies the U.S. Dollar as the default currency. If the default currency is not defined in
   * the current data file, the method does nothing.
   */
  public void setDefaultCurrency() {
    final Account root = _model.getRootAccount();
    if (root == null) return;
    CurrencyType currency = root.getBook().getCurrencies().getCurrencyByIDString("USD");
    if (currency == null) return;
    StockExchange.DEFAULT.setCurrency(currency);
  }

  /**
   * Download price history for a security.
   * @param securityCurrency The currency of the security to be updated.
   * @param dateRange The date range to obtain history for.
   * @param apply True to apply the downloaded history to the currency, false to download without
   * applying (for testing).
   * @return The security price history that was downloaded.
   * @throws DownloadException if an error occurs.
   */
  public StockHistory getHistory(CurrencyType securityCurrency, DateRange dateRange, boolean apply)
    throws DownloadException
  {
    return importData(securityCurrency, dateRange, apply);
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
    throw new Exception("Exchange rate retrieval not implemented in "+this);
  }


  public abstract String getId();
  
  public boolean canGetHistory() {
    return ((_capabilities & HISTORY_SUPPORT) != 0);
  }

  public boolean canGetRates() {
    return ((_capabilities & EXCHANGE_RATES_SUPPORT) != 0);
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
    CurrencyTable cTable = _model.getRootAccount() == null ? null : _model.getRootAccount().getBook().getCurrencies();
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
  private StockExchange getExchangeForSecurity(SymbolData symbol, CurrencyType securityCurrency) {
    if (!SQUtil.isBlank(symbol.prefix)) {
      // check for a Google prefix override
      StockExchange result = _model.getExchangeList().findByGooglePrefix(symbol.prefix);
      if (result != null) return result;
    }
    if (!SQUtil.isBlank(symbol.suffix)) {
      // check for a Yahoo exchange suffix override
      StockExchange result = _model.getExchangeList().findByYahooSuffix(symbol.suffix);
      if (result != null) return result;
    }
    // go with the exchange the user assigned to the security
    return _model.getSymbolMap().getExchangeForCurrency(securityCurrency);
  }
  
  protected boolean allowAutodetect() {return true;}
  
  protected abstract String getCurrentPriceHeader();

  protected String getTimeZoneID() {
    // the default time zone is EDT in the U.S.
    return "America/New_York";  // could possibly also use 'US/Eastern'
  }

  protected SimpleDateFormat getExpectedDateFormat(boolean getFullHistory) {
    CustomDateFormat userDateFormat = _model.getPreferences().getShortDateFormatter();
    if (userDateFormat == null) return DEFAULT_DATE_FORMAT;
    return new SimpleDateFormat(userDateFormat.getPattern());
  }

  protected StockQuotesModel getModel() { return _model; }

  protected String getCookie() { return null; }
  
  
  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Private Methods
  //////////////////////////////////////////////////////////////////////////////////////////////

  private StockHistory importData(CurrencyType securityCurrency, DateRange dateRange, boolean apply)
    throws DownloadException
  {
    SymbolData parsedSymbol = SQUtil.parseTickerSymbol(securityCurrency);
    if (parsedSymbol == null) return null;
    StockExchange exchange = getExchangeForSecurity(parsedSymbol, securityCurrency);
    String fullTickerSymbol = getFullTickerSymbol(parsedSymbol, exchange);
    if (fullTickerSymbol == null) return null;
    String priceCurrencyId = getCurrencyCodeForQuote(securityCurrency.getTickerSymbol(), exchange);
    // get the currency that the prices are specified in
    CurrencyType priceCurrency = getPriceCurrency(securityCurrency);
    if (priceCurrency == null) {
      String message = MessageFormat.format(
              _model.getResources().getString(L10NStockQuotes.ERROR_PRICE_CURRENCY_FMT),
              priceCurrencyId);
      throw new DownloadException(securityCurrency, message);
    }
    double priceMultiplier = exchange.getPriceMultiplier();
    final String urlStr = getHistoryURL(fullTickerSymbol, dateRange);
    System.err.println("getting history using url: "+ urlStr);
    
    if (urlStr == null) {
      // mode is not supported by this connection
      String message = _model.getResources().getString(L10NStockQuotes.ERROR_HISTORY_NOT_SUPPORTED);
      throw new DownloadException(securityCurrency, message);
    }

    SimpleDateFormat defaultDateFormat = getExpectedDateFormat(true);
    char decimal = _model.getPreferences().getDecimalChar();
    SnapshotImporterFromURL importer = new SnapshotImporterFromURL(urlStr, getCookie(), _model.getResources(),
                                                                   securityCurrency, defaultDateFormat, _timeZone, decimal);
    if (allowAutodetect()) {
      importer.setAutodetectFormat(true);
    } else {
      importer.setColumnsFromHeader(getCurrentPriceHeader());
    }
    importer.setPriceMultiplier(priceMultiplier);
    
    // the return value is negative for general errors, 0 for success with no error, or a positive
    // value for overall success but one or more errors
    int errorResult = importer.importData();
    if (errorResult < 0) {
      Exception error = importer.getLastException();
      if (error != null) throw new DownloadException(securityCurrency, error.getMessage(), error);
      buildMessageAndThrow(securityCurrency, errorResult);
    }
    List<StockRecord> recordList = importer.getImportedRecords();
    if (recordList.isEmpty())  buildMessageAndThrow(securityCurrency, SnapshotImporter.ERROR_NO_DATA);
    
    if(this instanceof AlphavantageConnection && fullTickerSymbol.endsWith(".L") && recordList.size() > 1) {
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
    
    buildPriceDisplayText(recordList, priceCurrency, _model.getPreferences().getDecimalChar());
    if (apply) {
      importer.apply(priceCurrency);
    }
    return new StockHistory(priceCurrencyId, recordList, errorResult);
  }

  private void buildPriceDisplayText(List<StockRecord> recordList, CurrencyType priceCurrency,
                                     char decimal) {
    for (StockRecord record : recordList) {
      long amount = (record.closeRate == 0.0) ? 0 : priceCurrency.getLongValue(1.0 / record.closeRate);
      record.priceDisplay = priceCurrency.formatFancy(amount, decimal);
    }
  }

  private void buildMessageAndThrow(CurrencyType securityCurrency, int result)
      throws DownloadException
  {
    String message = null;
    final ResourceProvider resources = _model.getResources();
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
        message = resources.getString(L10NStockQuotes.IMPORT_ERROR_OTHER);
        break;
    }
    if (message != null) {
      throw new DownloadException(securityCurrency, message);
    }
  }


  public class ExchangeRate {
    private final double rate;

    ExchangeRate(double rate) {
      this.rate = rate;
    }

    public double getRate() {
      return this.rate;
    }
  }


}