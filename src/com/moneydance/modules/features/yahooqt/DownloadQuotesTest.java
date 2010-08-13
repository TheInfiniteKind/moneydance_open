/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.DateRange;
import com.moneydance.util.CustomDateFormat;
import com.moneydance.util.StringUtils;

import java.text.MessageFormat;
import java.util.concurrent.Callable;

/**
 * Performs a test to see if quotes/prices can be downloaded without error.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class DownloadQuotesTest implements Callable<Boolean> {
  static final String NAME = DownloadQuotesTask.NAME;
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private final CustomDateFormat _dateFormat;

  DownloadQuotesTest(final StockQuotesModel model, final ResourceProvider resources) {
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
    _model.showProgress(0.0f, StockUtil.replaceAll(format, "{acctname}", taskDisplayName));

    final SecuritySymbolTableModel tableModel = _model.getTableModel();
    final int rowCount = tableModel.getRowCount();

    // initial setup
    for (int index = 0; index < rowCount; index++) {
      final SecuritySymbolTableModel.SecurityEntry entry = tableModel.getEntry(index);
      if (entry.use) {
        entry.testResult = _resources.getString(L10NStockQuotes.TEST_NOTSTARTED);
      } else {
        entry.testResult = _resources.getString(L10NStockQuotes.TEST_EXCLUDED);
      }
    }
    tableModel.refreshRow(-1);

    // download each one
    final BaseConnection connection = _model.getSelectedHistoryConnection();
    final String setupError = _resources.getString(L10NStockQuotes.TEST_ERR_SETUP);
    final String skipped = _resources.getString(L10NStockQuotes.TEST_EXCLUDED);
    for (int index = 0; index < rowCount; index++) {
      final SecuritySymbolTableModel.SecurityEntry entry = tableModel.getEntry(index);
      if (entry.use) {
        final TestResult testResult = testEntry(entry, connection);
        entry.testResult = (connection == null) ? setupError : testResult._testResult;
        entry.toolTip = testResult._toolTip;
      } else {
        entry.testResult = skipped;
        entry.toolTip = skipped;
      }
      tableModel.refreshRow(index);
    }

    return Boolean.TRUE;
  }

  private TestResult testEntry(SecuritySymbolTableModel.SecurityEntry entry, BaseConnection connection) {
    DateRange dateRange = HistoryDateRange.getRangeForSecurity(entry.currency, _model.getHistoryDays());
    final DownloadResult historyResult = getHistoryTest(entry, connection, dateRange);
    final DownloadResult quoteResult = getQuoteTest(entry, connection);
    TestResult testResult = new TestResult(historyResult, quoteResult);
    // create a verbose tooltip
    StringBuilder sb = new StringBuilder(N12EStockQuotes.HTML_BEGIN);
    if (connection.canGetHistory()) {
      sb.append(N12EStockQuotes.PARA_BEGIN);
      sb.append(SQUtil.getLabelText(_resources, L10NStockQuotes.HISTORY));
      sb.append(testResult._historyResult);
    }
    if (connection.canGetCurrentPrice()) {
      sb.append(N12EStockQuotes.PARA_BEGIN);
      sb.append(SQUtil.getLabelText(_resources, L10NStockQuotes.QUOTE));
      sb.append(testResult._quoteResult);
    }
    sb.append(N12EStockQuotes.HTML_END);
    testResult._toolTip = sb.toString();
    // create a succinct summary test result
    sb.setLength(0);
    sb.append(N12EStockQuotes.HTML_BEGIN);
    if (connection.canGetHistory()) {
      sb.append(getSuccessIcon(testResult._historySuccess));
      sb.append(N12EStockQuotes.SPACE);
      sb.append(_resources.getString(L10NStockQuotes.HISTORY));
    }
    if (connection.canGetCurrentPrice()) {
      if (connection.canGetHistory()) sb.append(N12EStockQuotes.COMMA_SEPARATOR);
      sb.append(getSuccessIcon(testResult._quoteSuccess));
      sb.append(N12EStockQuotes.SPACE);
      sb.append(SQUtil.getLabelText(_resources, L10NStockQuotes.QUOTE));
      if (testResult._quoteSuccess) {
        sb.append(testResult._price);
      } else {
        sb.append(N12EStockQuotes.ERROR);
      }
    }
    sb.append(N12EStockQuotes.HTML_END);
    testResult._testResult = sb.toString();
    return testResult;
  }

  private String getSuccessIcon(boolean success) {
    if (success) {
      return N12EStockQuotes.GREEN_FONT_BEGIN + "&#x2714;" + N12EStockQuotes.FONT_END;
    }
    return N12EStockQuotes.RED_FONT_BEGIN + "&#x2716;" + N12EStockQuotes.FONT_END;
  }

  private DownloadResult getHistoryTest(SecuritySymbolTableModel.SecurityEntry entry,
                                        BaseConnection connection, DateRange dateRange) {
    try {
      final StockHistory history = connection.getHistory(entry.currency, dateRange, false);
      if (history == null) {
        return new DownloadResult(_resources.getString(L10NStockQuotes.ERROR_NO_SYMBOL), 1);
      }
      int errors = history.getErrorCount();
      int records = history.getRecordCount();
      if (errors > 0) {
        if (records > 0) {
          final String message = MessageFormat.format(
                  _resources.getString(L10NStockQuotes.TEST_SOME_SUCCESS_FMT),
                  Integer.toString(records), Integer.toString(errors));
          final DownloadResult result = new DownloadResult(message, errors);
          result.historyRecordCount = records;
        }
        final String message = MessageFormat.format(
                _resources.getString(L10NStockQuotes.TEST_ERROR_FMT),
                Integer.toString(errors));
        final DownloadResult result = new DownloadResult(message, errors);
        result.historyRecordCount = 0;
        return result;
      }
      if (records == 0) {
        return new DownloadResult(_resources.getString(L10NStockQuotes.TEST_NO_DATA), errors);
      }
      final String message = MessageFormat.format(
              _resources.getString(L10NStockQuotes.TEST_SUCCESS_FMT),
              Integer.toString(records));
      final DownloadResult result = new DownloadResult(message, 0);
      result.historyRecordCount = records;
      return result;
    } catch (DownloadException downEx) {
      return new DownloadResult(downEx.getMessage(), 1);
    }
  }

  private DownloadResult getQuoteTest(SecuritySymbolTableModel.SecurityEntry entry,
                                      BaseConnection connection) {
    try {
      final StockRecord quote = connection.getCurrentPrice(entry.currency);
      if (quote == null) {
        return new DownloadResult(_resources.getString(L10NStockQuotes.ERROR_NO_SYMBOL), true, null);
      }
      String format = _resources.getString(L10NStockQuotes.TEST_PRICE_SUCCESS_FMT);
      String message = MessageFormat.format(format, _dateFormat.format(quote.date), quote.priceDisplay);
      return new DownloadResult(message, false, quote.priceDisplay);
    } catch (DownloadException downEx) {
      return new DownloadResult(downEx.getMessage(), true, null);
    }
  }

  private class TestResult {
    boolean _historySuccess = false;
    String _historyResult;
    boolean _quoteSuccess = false;
    String _quoteResult;
    String _testResult;
    String _toolTip;
    String _price;

    public TestResult(DownloadResult historyResult, DownloadResult quoteResult) {
      _historySuccess = (historyResult.historyErrorCount == 0);
      _historyResult = historyResult.displayMessage;
      _quoteSuccess = !quoteResult.currentError;
      _quoteResult = quoteResult.displayMessage;
      _price = quoteResult.currentResult;
    }
  }

}
