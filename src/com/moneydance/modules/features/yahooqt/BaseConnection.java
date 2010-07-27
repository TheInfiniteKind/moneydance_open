/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.DateRange;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.util.CustomDateFormat;

import java.text.MessageFormat;
import java.text.SimpleDateFormat;
import java.util.Vector;

/**
 * Base class for importing stock and currency prices. Derived classes provide specific
 * implementation.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public abstract class BaseConnection {
  static final int HISTORY_SUPPORT = 1;
  static final int CURRENT_PRICE_SUPPORT = 2;
  static final int EXCHANGE_RATES_SUPPORT = 4;
  static final int ALL_SUPPORT = HISTORY_SUPPORT | CURRENT_PRICE_SUPPORT | EXCHANGE_RATES_SUPPORT;
  
  private final int _capabilities;
  private final StockQuotesModel _model;

  private final SimpleDateFormat DEFAULT_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");

  public BaseConnection(StockQuotesModel model, final int capabilities) {
    _model = model;
    _capabilities = capabilities;
  }

  /**
   * Given a raw ticker symbol, convert it to a full symbol by adding prefix or suffix appropriate
   * for the stock exchange.
   *
   * @param rawTickerSymbol The raw ticker symbol.
   * @param exchange        The selected stock exchange to use.
   * @return The full ticker symbol appropriate for the selected stock exchange.
   */
  public abstract String getFullTickerSymbol(String rawTickerSymbol, StockExchange exchange);

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
   * Given a ticker symbol, return the URL to obtain current security price.
   * @param fullTickerSymbol The ticker symbol to use.
   * @return The URL to use to obtain a current price quote from.
   */
  public abstract String getCurrentPriceURL(String fullTickerSymbol);

  /** Retrieve the history for the given stock ticker.  The history
    * ends on the given date and includes the previous numDays days. */

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
    return importData(securityCurrency, true, dateRange, apply);
  }

  /**
   * Retrieve the current information for the given stock ticker symbol.
   * @param securityCurrency The currency for the security we're downloading the current price for.
   * @return The current price record for the given currency.
   * @throws DownloadException if an error occurs.
   */
  public StockRecord getCurrentPrice(CurrencyType securityCurrency)
    throws DownloadException
  {
    int today = Util.getStrippedDateInt();
    DateRange dateRange = new DateRange(today, today);
    // the current price does not add a history entry, so we do not 'apply' the download
    final boolean apply = false;
    StockHistory history = importData(securityCurrency, false, dateRange, apply);
    if (history == null) return null;
    return history.getRecord(0);
  }

  public abstract String getId();

  public boolean canGetHistory() {
    return ((_capabilities & HISTORY_SUPPORT) != 0);
  }

  public boolean canGetCurrentPrice() {
    return ((_capabilities & CURRENT_PRICE_SUPPORT) != 0);
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
    StockExchange exchange = _model.getSymbolMap().getExchangeForCurrency(securityCurrency);
    String fullTickerSymbol = getFullTickerSymbol(securityCurrency.getTickerSymbol(), exchange);
    if (fullTickerSymbol == null) return null;
    String priceCurrencyId = getCurrencyCodeForQuote(securityCurrency.getTickerSymbol(), exchange);
    // get the currency that the prices are specified in
    return _model.getRootAccount().getCurrencyTable().getCurrencyByIDString(priceCurrencyId);
  }

  protected abstract String getCurrentPriceHeader();

  protected SimpleDateFormat getExpectedDateFormat(boolean getFullHistory) {
    CustomDateFormat userDateFormat = _model.getPreferences().getShortDateFormatter();
    if (userDateFormat == null) return DEFAULT_DATE_FORMAT;
    return new SimpleDateFormat(userDateFormat.getPattern());
  }


  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Private Methods
  //////////////////////////////////////////////////////////////////////////////////////////////

  private StockHistory importData(CurrencyType securityCurrency, boolean getFullHistory,
                                         DateRange dateRange, boolean apply)
    throws DownloadException
  {
    StockExchange exchange = _model.getSymbolMap().getExchangeForCurrency(securityCurrency);
    String fullTickerSymbol = getFullTickerSymbol(securityCurrency.getTickerSymbol(), exchange);
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
    final String urlStr;
    if (getFullHistory) {
      urlStr = getHistoryURL(fullTickerSymbol, dateRange);
    } else {
      urlStr = getCurrentPriceURL(fullTickerSymbol);
    }

    if (urlStr == null) {
      // mode is not supported by this connection
      String message = getFullHistory ?
              _model.getResources().getString(L10NStockQuotes.ERROR_HISTORY_NOT_SUPPORTED) :
              _model.getResources().getString(L10NStockQuotes.ERROR_CURRENT_NOT_SUPPORTED);
      throw new DownloadException(securityCurrency, message);
    }

    SimpleDateFormat defaultDateFormat = getExpectedDateFormat(getFullHistory);
    char decimal = _model.getPreferences().getDecimalChar();
    SnapshotImporterFromURL importer = new SnapshotImporterFromURL(urlStr, _model.getResources(),
            securityCurrency, defaultDateFormat, decimal);
    if (getFullHistory) {
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
    Vector<StockRecord> recordList = importer.getImportedRecords();
    if (recordList.isEmpty())  buildMessageAndThrow(securityCurrency, SnapshotImporter.ERROR_NO_DATA);
    buildPriceDisplayText(recordList, priceCurrency, _model.getPreferences().getDecimalChar());
    if (apply) {
      importer.apply(priceCurrency);
    }
    return new StockHistory(priceCurrencyId, recordList, errorResult);
  }

  private void buildPriceDisplayText(Vector<StockRecord> recordList, CurrencyType priceCurrency,
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

}