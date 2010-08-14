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
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.util.CustomDateFormat;

import java.text.MessageFormat;
import java.util.Enumeration;
import java.util.concurrent.Callable;

/**
 * Downloads price history and current price for securities.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class DownloadQuotesTask implements Callable<Boolean> {
  static final String NAME = "Download_Security_Quotes";  // not translatable
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private final CustomDateFormat _dateFormat;

  private float _progressPercent = 0.0f;

  DownloadQuotesTask(final StockQuotesModel model, final ResourceProvider resources) {
    _model = model;
    _resources = resources;
    _dateFormat = _model.getPreferences().getShortDateFormatter();
  }

  @Override
  public String toString() { return NAME; }

  public Boolean call() throws Exception {
    final String taskDisplayName = _resources.getString(L10NStockQuotes.QUOTES);
    // this is a Moneydance string that says 'Downloading {acctname}'
    String format = _model.getGUI().getStr("downloading_acct_x");
    _model.showProgress(0.0f, SQUtil.replaceAll(format, "{acctname}", taskDisplayName));

    RootAccount root = _model.getRootAccount();
    if (root == null) {
      System.err.println("Skipping security prices download, no root account");
      return Boolean.FALSE;
    }
    CurrencyTable ctable = root.getCurrencyTable();
    final int numDays = _model.getHistoryDays();

    boolean success = false;
    int skippedCount = 0, errorCount = 0, successCount = 0;
    try {
      int totalValues = (int) ctable.getCurrencyCount();
      int currIdx = 0;
      for (Enumeration cen = ctable.getAllValues(); cen.hasMoreElements();) {
        CurrencyType currencyType = (CurrencyType) cen.nextElement();
        _progressPercent = currIdx / (float) totalValues;
        if (_progressPercent == 0.0f) {
          _progressPercent = 0.01f;
        }

        if (currencyType.getCurrencyType() == CurrencyType.CURRTYPE_SECURITY) {
          DownloadResult result = updateSecurity(currencyType, numDays);
          if (result.skipped) {
            ++skippedCount;
          } else {
            if (result.currentError || (result.historyErrorCount > 0)) {
              ++errorCount;
            }
            if (!result.currentError || (result.historyRecordCount > 0)) {
              ++successCount;
            }
            // log any messages for those that weren't skipped
            if (!SQUtil.isBlank(result.logMessage)) System.err.println(result.logMessage);
          }
        }
        currIdx++;
      }
      success = true;
    } catch (Exception error) {
      String message = MessageFormat.format(
              _resources.getString(L10NStockQuotes.ERROR_DOWNLOADING_FMT),
              _resources.getString(L10NStockQuotes.QUOTES),
              error.getLocalizedMessage());
      _model.showProgress(0f, message);
      System.err.println(MessageFormat.format("Error while downloading Security Price Quotes: {0}",
              error.getMessage()));
      success = false;
    } finally {
      _progressPercent = 0f;
      ctable.fireCurrencyTableModified();
    }

    if (success) {
      SQUtil.pauseTwoSeconds(); // wait a bit so user can read the last price update
      if ((skippedCount == 0) && (errorCount == 0) && (successCount == 0)) {
        String message = MessageFormat.format(
                _resources.getString(L10NStockQuotes.FINISHED_DOWNLOADING_FMT),
                _resources.getString(L10NStockQuotes.QUOTES));
        _model.showProgress(0f, message);
        System.err.println("Finished downloading Security Price Quotes");
      } else {
        String message = MessageFormat.format(
                _resources.getString(L10NStockQuotes.QUOTES_DONE_FMT),
                Integer.toString(skippedCount), Integer.toString(errorCount),
                Integer.toString(successCount));
        _model.showProgress(0f, message);
        System.err.println(MessageFormat.format(
                "Security price update complete with {0} skipped, {1} errors and {2} quotes obtained",
                Integer.toString(skippedCount), Integer.toString(errorCount),
                Integer.toString(successCount)));
      }
    }
    return Boolean.TRUE;
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private DownloadResult updateSecurity(CurrencyType currType, int numDays) {
    DateRange dateRange = HistoryDateRange.getRangeForSecurity(currType, numDays);

    // check if the user is skipping this one but leaving the symbol intact
    DownloadResult result = new DownloadResult();
    result.displayName = currType.getName();
    if (!_model.getSymbolMap().getIsCurrencyUsed(currType)) {
      result.skipped = true;
      return result;
    }

    BaseConnection connection = _model.getSelectedHistoryConnection();
    if (connection == null) {
      final String message = _resources.getString(L10NStockQuotes.ERROR_NO_CONNECTION);
      _model.showProgress(_progressPercent, message);
      result.historyErrorCount = 1;
      result.historyResult = message;
      result.currentError = true;
      result.currentResult = message;
      result.logMessage = "No connection established";
      return result;
    }

    boolean foundPrice = false;
    double latestRate = 0.0;
    int latestPriceDate = Util.getStrippedDateInt();
    if (connection.canGetHistory()) {
      try {
        final StockHistory history = connection.getHistory(currType, dateRange, true);
        if (history == null) {
          result.skipped = true;
          result.logMessage = "No history obtained for security " + currType.getName();
          return result;
        }
        // we're just counting the number of successful symbols
        if (history.getErrorCount() > 0) result.historyErrorCount = 1;
        if (history.getRecordCount() > 0) {
          result.historyRecordCount = 1;
          result.historyResult = "Success";  // currently not shown to the user
          StockRecord latest = history.findMostRecentValidRecord();
          if (latest != null) {
            foundPrice = true;
            latestRate = latest.closeRate;
            latestPriceDate = latest.date;
          }
        } else {
          result.historyResult = "Error";   // currently not shown to the user
          result.logMessage = "No history records returned for security " + currType.getName();
        }
      } catch (DownloadException e) {
        final CurrencyType currency = (e.getCurrency() != null) ? e.getCurrency() : currType;
        String message = MessageFormat.format(
                _resources.getString(L10NStockQuotes.ERROR_HISTORY_FMT),
                currency.getName(), e.getLocalizedMessage());
        _model.showProgress(_progressPercent, message);
        result.historyErrorCount = 1;
        result.historyResult = e.getMessage();
        if (SQUtil.isBlank(result.logMessage)) {
          result.logMessage = MessageFormat.format("Error downloading historical prices for {0}: {1}",
                  currency.getName(), e.getMessage());
        }
      }
    } // if getting price history
    if (connection.canGetCurrentPrice()) {
      try {
        final StockRecord record = connection.getCurrentPrice(currType);
        if (record == null) {
          result.skipped = true;
          result.logMessage = "No current price obtained for security " + currType.getName();
          return result;
        }
        result.currentError = (record.closeRate == 0.0);
        result.currentResult = record.priceDisplay;
        if (!result.currentError) {
          foundPrice = true;
          latestRate = record.closeRate;
          latestPriceDate = record.date;
        }
      } catch (DownloadException e) {
        final CurrencyType currency = (e.getCurrency() != null) ? e.getCurrency() : currType;
        String message = MessageFormat.format(
                _resources.getString(L10NStockQuotes.ERROR_CURRENT_FMT),
                currency.getName(), e.getLocalizedMessage());
        _model.showProgress(_progressPercent, message);
        result.currentError = true;
        result.currentResult = e.getMessage();
        if (SQUtil.isBlank(result.logMessage)) {
          result.logMessage = MessageFormat.format("Error downloading current price for {0}: {1}",
                  currency.getName(), e.getMessage());
        }
      }
    } // if getting the current price
    // update the current price if possible, the last price date is stored as a long
    final long longLatestDate = Util.convertIntDateToLong(latestPriceDate).getTime();
    if (foundPrice && ((currType.getTag("price_date")==null) ||
        (Long.parseLong(currType.getTag("price_date")) < longLatestDate))) {
      currType.setUserRate(latestRate);
      currType.setTag("price_date", String.valueOf(longLatestDate));
    }
    if (foundPrice) {
      _model.showProgress(_progressPercent,
                          buildPriceDisplayText(connection, currType, result.displayName,
                                                latestRate, latestPriceDate));
      if (SQUtil.isBlank(result.logMessage)) {
        result.logMessage = buildPriceLogText(connection, currType, result.displayName, latestRate,
                latestPriceDate);
      }
    }
    return result;
  }

  private String buildPriceDisplayText(BaseConnection connection, CurrencyType securityCurrency,
                                       String name, double rate, int date) {
    String format = _resources.getString(L10NStockQuotes.SECURITY_PRICE_DISPLAY_FMT);
    // get the currency that the prices are specified in
    CurrencyType priceCurrency = connection.getPriceCurrency(securityCurrency);
    long amount = (rate == 0.0) ? 0 : priceCurrency.getLongValue(1.0 / rate);
    final char decimal = _model.getPreferences().getDecimalChar();
    String priceDisplay = priceCurrency.formatFancy(amount, decimal);
    String asofDate =_dateFormat.format(date);
    return MessageFormat.format(format, name, asofDate, priceDisplay);
  }

  private String buildPriceLogText(BaseConnection connection, CurrencyType securityCurrency,
                                   String name, double rate, int date) {
    String format = "Price for {0} as of {1}: {2}";
    // get the currency that the prices are specified in
    CurrencyType priceCurrency = connection.getPriceCurrency(securityCurrency);
    long amount = (rate == 0.0) ? 0 : priceCurrency.getLongValue(1.0 / rate);
    String priceDisplay = priceCurrency.formatFancy(amount, '.');
    String asofDate = _dateFormat.format(date);
    return MessageFormat.format(format, name, asofDate, priceDisplay);
  }

}