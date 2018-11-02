/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.DateUtil;

import java.text.MessageFormat;
import java.util.*;
import java.util.concurrent.Callable;

/**
 * Downloads exchange rates and security prices
 */
public class DownloadTask implements Callable<Boolean> {
  static final String NAME = "DownloadTask";
  
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private boolean downloadRates;
  private boolean downloadPrices;
  private boolean includeTestInfo = false;
  
  int skippedCount = 0;
  int errorCount = 0;
  int successCount = 0;
  
  DownloadTask(final StockQuotesModel model, final ResourceProvider resources) {
    _model = model;
    _resources = resources;
    downloadRates = model.isExchangeRateSelected();
    downloadPrices = model.isHistoricalPriceSelected();
  }
  
  protected boolean getIncludeTestInfo() {
    return includeTestInfo;
  }

  public void setIncludeTestInfo(boolean includeTestInfo) {
    this.includeTestInfo = includeTestInfo;
  }

  public Boolean call() {
    skippedCount = 0;
    errorCount = 0;
    successCount = 0;
    
    if (_model.getBook() == null) {
      if(Main.DEBUG_YAHOOQT) System.err.println("Skipping security prices download, no book account");
      return Boolean.FALSE;
    }
    
    final String taskDisplayName = _resources.getString(L10NStockQuotes.QUOTES);
    // this is a Moneydance string that says 'Downloading {acctname}'
    String format = _model.getGUI().getStr("downloading_acct_x");
    _model.showProgress(0.0f, SQUtil.replaceAll(format, "{acctname}", taskDisplayName));
    final SecuritySymbolTableModel tableModel = _model.getTableModel();

    BaseConnection ratesDownloader = downloadRates ? _model.getSelectedExchangeRatesConnection() : null;
    BaseConnection pricesDownloader = downloadPrices ? _model.getSelectedHistoryConnection() : null;
    
    List<DownloadInfo> securityList = new ArrayList<>();
    List<DownloadInfo> currencyList = new ArrayList<>();
    List<DownloadInfo> skippedList = new ArrayList<>();
    
    // create the DownloadResult wrappers and sort the currencies/securities by type and validity
    // also set the initial test string information
    for(CurrencyType curr : _model.getBook().getCurrencies()) {
      boolean isSecurity = curr.getCurrencyType() == CurrencyType.Type.SECURITY;
      BaseConnection downloader = isSecurity ? pricesDownloader : ratesDownloader;
      DownloadInfo currInfo = new DownloadInfo(curr, downloader);
      SecuritySymbolTableModel.SecurityEntry tableEntry = tableModel.getEntryByCurrency(curr);
      if((isSecurity && !_model.getSymbolMap().getIsCurrencyUsed(curr)) 
         || !currInfo.isValidForDownload 
         || (tableEntry!=null && !tableEntry.updatesEnabled)) 
      { // skip disabled or invalid securities and currencies
        skippedList.add(currInfo);
        currInfo.skipped = true;
        currInfo.updateResultSummary(_model);
      } else if(curr.getCurrencyType() == CurrencyType.Type.SECURITY) {
        securityList.add(currInfo);
        if(tableEntry!=null) {
          if (pricesDownloader == null) {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_EXCLUDED);
          } else {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_NOTSTARTED);
          }
        }
      } else {
        currencyList.add(currInfo);
        if(tableEntry!=null) {
          if (ratesDownloader == null) {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_EXCLUDED);
          } else {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_NOTSTARTED);
          }
        }
      }
    }
    
    tableModel.refreshRow(-1);
    
    boolean ratesResult = true;
    if(ratesDownloader!=null) {
      _model.showProgress(0.0f, MessageFormat.format(_resources.getString(L10NStockQuotes.EXCHANGE_RATES_BEGIN),
                                                     _model.getSelectedExchangeRatesConnection().toString()));
      
      ratesResult = downloadExchangeRates(_model, currencyList, ratesDownloader);
      if(ratesResult) {
        _model.saveLastExchangeRatesUpdateDate(DateUtil.getStrippedDateInt());
      }
    }
    
    boolean pricesResult = true;
    if(pricesDownloader!=null) {
      pricesResult = downloadPrices(_model, securityList, pricesDownloader);
      if(pricesResult) {
        _model.saveLastQuoteUpdateDate(DateUtil.getStrippedDateInt());
      }
    }
    return ratesResult && pricesResult;
  }
  
  void showSecuritiesDownloadError(Exception error) {
    String message = MessageFormat.format(_resources.getString(L10NStockQuotes.ERROR_DOWNLOADING_FMT),
                                          _resources.getString(L10NStockQuotes.QUOTES),
                                          error.getLocalizedMessage());
    _model.showProgress(0f, message);
    if(Main.DEBUG_YAHOOQT) {
      System.err.println(MessageFormat.format("Error while downloading Security Price Quotes: {0}",
                                              error.getMessage()));
    }
    error.printStackTrace();
  }
  
  
  final Boolean downloadExchangeRates(StockQuotesModel model, List<DownloadInfo> currencyList, BaseConnection ratesDownloader) {
    boolean testingMode = getIncludeTestInfo();
    ResourceProvider resources = model.getResources();
    AccountBook book = model.getBook();
    if (book == null) return Boolean.FALSE;
    CurrencyTable ctable = book.getCurrencies();

    // build the map of currencies to accounts so that we can easily filter out unused currencies
    Map<CurrencyType, Account> currencyMap = new HashMap<>();
    for(Account acct : AccountUtil.allMatchesForSearch(_model.getBook(), AcctFilter.ALL_ACCOUNTS_FILTER)) {
      CurrencyType curr = acct.getCurrencyType();
      if(curr.getCurrencyType() != CurrencyType.Type.CURRENCY) continue;
      if(!currencyMap.containsKey(curr)) { // it's not already in the list
        currencyMap.put(curr, acct);
      }
    }

    ArrayList<DownloadInfo> sortedCurrencies = new ArrayList<>();

    Collections.shuffle(currencyList); // randomize the order of the currencies
    
    // put the used/active currencies at the front of the list
    for(DownloadInfo downloadInfo : currencyList) {
      if(currencyMap.containsKey(downloadInfo.security)) {
        sortedCurrencies.add(downloadInfo);
      }
    }

    // now add the unused currencies,...
    for(DownloadInfo downloadInfo : currencyList) {
      if(!currencyMap.containsKey(downloadInfo.security)) {
        sortedCurrencies.add(downloadInfo);
      }
    }
    
    currencyList = sortedCurrencies;
    
    boolean successFlag = ratesDownloader.updateExchangeRates(currencyList);

    for(DownloadInfo result : currencyList) {
      result.updateResultSummary(model);
      result.buildPriceDisplay(result.relativeCurrency, model.getDecimalDisplayChar());

      model.getTableModel().registerTestResults(result);
      if(!testingMode) { // if we're not in testing mode, record the results
        result.apply();
      }
    }

    ctable.fireCurrencyTableModified();
    
    if (successFlag) {
      SQUtil.pauseTwoSeconds(); // wait a bit so user can read the last rate update
      String message = MessageFormat.format(
        resources.getString(L10NStockQuotes.FINISHED_DOWNLOADING_FMT),
        resources.getString(L10NStockQuotes.RATES));
      model.showProgress(0f, message);
      if(Main.DEBUG_YAHOOQT) System.err.println("Finished downloading Currency Exchange Rates");
    }
    
    return successFlag;
  }


  private boolean downloadPrices(StockQuotesModel model, List<DownloadInfo> securityList, BaseConnection pricesDownloader) {
    AccountBook book = model.getBook();
    
    boolean successFlag = pricesDownloader.updateSecurities(securityList);
    
    for (DownloadInfo downloadInfo : securityList) {
      downloadInfo.updateResultSummary(model);
      downloadInfo.buildPriceDisplay(downloadInfo.relativeCurrency, model.getDecimalDisplayChar());
      if(getIncludeTestInfo()) {
        model.getTableModel().registerTestResults(downloadInfo);
      } else {
        downloadInfo.apply();
      }
      
      if (downloadInfo.skipped) {
        skippedCount++;
      } else if(downloadInfo.wasSuccess()) {
        successCount++;
      } else {
        errorCount++;
        // log any messages for those that weren't skipped
        if(Main.DEBUG_YAHOOQT && !SQUtil.isBlank(downloadInfo.logMessage)) System.err.println(downloadInfo.logMessage);
      }
    }
    
    if(successFlag) {
      SQUtil.pauseTwoSeconds(); // wait a bit so user can read the last price update
        String message = MessageFormat.format(
          _resources.getString(L10NStockQuotes.FINISHED_DOWNLOADING_FMT),
          _resources.getString(L10NStockQuotes.QUOTES));
        _model.showProgress(0f, message);
        if (Main.DEBUG_YAHOOQT)
          System.err.println("Finished downloading Security Price Quotes");
    }
    

    return successFlag;
  }




}