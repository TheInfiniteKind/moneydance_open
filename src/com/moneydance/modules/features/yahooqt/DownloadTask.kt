/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.AccountUtil.Companion.allMatchesForSearch
import com.infinitekind.moneydance.model.AcctFilter
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.util.DateUtil
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import com.moneydance.modules.features.yahooqt.SQUtil.pauseTwoSeconds
import com.moneydance.modules.features.yahooqt.SQUtil.replaceAll
import java.text.MessageFormat
import java.util.*
import java.util.concurrent.Callable

var CurrencyType.dateLastUpdated: Long
  get() = getLongParameter("price_date", 0L)
  set(newValue) {
    setParameter("price_date", newValue)
  }

/**
 * Downloads exchange rates and security prices
 */
class DownloadTask internal constructor(private val _model: StockQuotesModel, private val _resources: ResourceProvider) : Callable<Boolean> {
  private val downloadRates = _model.isExchangeRateSelected
  private val downloadPrices = _model.isHistoricalPriceSelected
  var includeTestInfo: Boolean = false
  
  var skippedCount: Int = 0
  var errorCount: Int = 0
  var successCount: Int = 0
  
  override fun call(): Boolean {
    skippedCount = 0
    errorCount = 0
    successCount = 0
    
    if (_model.book == null) {
      QER_DLOG.log { "Skipping security prices download, no book is open!" }
      return false
    }
    
    val taskDisplayName = _resources.getString(L10NStockQuotes.QUOTES)
    // this is a Moneydance string that says 'Downloading {acctname}'
    val format = _model.gui.getStr("downloading_acct_x")
    _model.showProgress(0.0f, replaceAll(format, "{acctname}", taskDisplayName))
    val tableModel = _model.tableModel
    
    val ratesDownloader = if (downloadRates) _model.selectedExchangeRatesConnection else null
    val pricesDownloader = if (downloadPrices) _model.selectedHistoryConnection else null
    
    val securityList: MutableList<DownloadInfo> = ArrayList()
    val currencyList: MutableList<DownloadInfo> = ArrayList()
    val skippedList: MutableList<DownloadInfo> = ArrayList()
    
    
    // create the DownloadResult wrappers and sort the currencies/securities by type and validity
    // also set the initial test string information
    for (curr in _model.book!!.currencies) {
      val isSecurity = curr.currencyType == CurrencyType.Type.SECURITY
      val downloader = if (isSecurity) pricesDownloader else ratesDownloader
      if (downloader == null) continue  // no downloader is configured for this currency
      
      val currInfo = DownloadInfo(curr, downloader.model)
      val tableEntry = tableModel.getEntryByCurrency(curr)
      if ((isSecurity && !_model.symbolMap.getIsCurrencyUsed(curr))
          || !currInfo.isValidForDownload || (tableEntry != null && !tableEntry.updatesEnabled)
      ) { // skip disabled or invalid securities and currencies
        skippedList.add(currInfo)
        currInfo.skipped = true
        currInfo.updateResultSummary(_model)
      } else if (isSecurity) {
        securityList.add(currInfo)
        if (tableEntry != null) {
          if (pricesDownloader == null) {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_EXCLUDED)
          } else {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_NOTSTARTED)
          }
        }
      } else {
        currencyList.add(currInfo)
        if (tableEntry != null) {
          if (ratesDownloader == null) {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_EXCLUDED)
          } else {
            tableEntry.testResult = _resources.getString(L10NStockQuotes.TEST_NOTSTARTED)
          }
        }
      }
    }
    
    tableModel.refreshRow(-1)
    
    var ratesResult = true
    if (ratesDownloader != null) {
      _model.showProgress(
        0.0f, MessageFormat.format(
          _resources.getString(L10NStockQuotes.EXCHANGE_RATES_BEGIN),
          _model.selectedExchangeRatesConnection.toString()
        )
      )
      
      ratesResult = downloadExchangeRates(_model, currencyList, ratesDownloader)
      if (ratesResult) {
        _model.saveLastExchangeRatesUpdateDate(DateUtil.strippedDateInt)
      }
    }
    
    var pricesResult = true
    if (pricesDownloader != null) {
      pricesResult = downloadPrices(_model, securityList, pricesDownloader)
      if (pricesResult) {
        _model.saveLastQuoteUpdateDate(DateUtil.strippedDateInt)
      }
    }
    return ratesResult && pricesResult
  }
  
  fun showSecuritiesDownloadError(error: Exception) {
    val message = MessageFormat.format(
      _resources.getString(L10NStockQuotes.ERROR_DOWNLOADING_FMT),
      _resources.getString(L10NStockQuotes.QUOTES),
      error.localizedMessage
    )
    _model.showProgress(0f, message)
    QER_DLOG.log("Error while downloading Security Price Quotes:", error)
  }
  
  
  fun downloadExchangeRates(model: StockQuotesModel, currencyList: List<DownloadInfo>, ratesDownloader: BaseConnection): Boolean {
    var currencyList = currencyList
    val testingMode = includeTestInfo
    val resources = model.resources
    val book = model.book ?: return java.lang.Boolean.FALSE
    val ctable = book.currencies
    
    // build the map of currencies to accounts so that we can easily filter out unused currencies
    val currencyMap: MutableMap<CurrencyType, Account> = HashMap()
    for (acct in allMatchesForSearch(_model.book, AcctFilter.ALL_ACCOUNTS_FILTER)) {
      val curr = acct.currencyType
      if (curr.currencyType != CurrencyType.Type.CURRENCY) continue
      if (!currencyMap.containsKey(curr)) { // it's not already in the list
        currencyMap[curr] = acct
      }
    }
    
    val sortedCurrencies = ArrayList<DownloadInfo>()
    
    Collections.shuffle(currencyList) // randomize the order of the currencies
    
    
    // put the used/active currencies at the front of the list
    for (downloadInfo in currencyList) {
      if (currencyMap.containsKey(downloadInfo.security)) {
        sortedCurrencies.add(downloadInfo)
      }
    }
    
    // now add the unused currencies,...
    for (downloadInfo in currencyList) {
      if (!currencyMap.containsKey(downloadInfo.security)) {
        sortedCurrencies.add(downloadInfo)
      }
    }
    
    currencyList = sortedCurrencies
    
    val successFlag = ratesDownloader.updateExchangeRates(currencyList)
    
    for (result in currencyList) {
      result.updateResultSummary(model)
      result.buildPriceDisplay(result.relativeCurrency, model.decimalDisplayChar)
      
      model.tableModel.registerTestResults(result)
      if (!testingMode) { // if we're not in testing mode, record the results
        result.apply()
      }
    }
    
    ctable.fireCurrencyTableModified()
    
    if (successFlag) {
      pauseTwoSeconds() // wait a bit so user can read the last rate update
      val message = MessageFormat.format(
        resources.getString(L10NStockQuotes.FINISHED_DOWNLOADING_FMT),
        resources.getString(L10NStockQuotes.RATES)
      )
      model.showProgress(0f, message)
      QER_DLOG.log { "Finished downloading Currency Exchange Rates" }
    }
    
    return successFlag
  }
  
  
  
  private fun downloadPrices(model: StockQuotesModel, secList: List<DownloadInfo>, pricesDownloader: BaseConnection): Boolean {
    val securities = mutableListOf<DownloadInfo>()
    secList.forEach { secInfo ->
      if(!secInfo.isValidForDownload) {
        secInfo.skipped = true
        secInfo.updateResultSummary(model)
        model.tableModel.registerTestResults(secInfo)
        QER_DLOG.log { "Skipping security price download for ${secInfo.security.getName()} - invalid" }
      } else {
        securities.add(secInfo)
      }
    }
    
    // sort all securities so that the least-recently-updated come first. This is so that the oldest ones are 
    // updated first, which should help with connections that only allow a limited number of connections per day.
    // It should also help with connections which are throttled to a degree which makes it take a long time to
    // update all securities
    securities.sortBy { it.security.dateLastUpdated }
    val successFlag = pricesDownloader.updateSecurities(securities)
    
    for (downloadInfo in securities) {
      downloadInfo.updateResultSummary(model)
      downloadInfo.buildPriceDisplay(downloadInfo.relativeCurrency, model.decimalDisplayChar)
      if (includeTestInfo) {
        model.tableModel.registerTestResults(downloadInfo)
      } else {
        downloadInfo.apply()
      }
      
      if (downloadInfo.skipped) {
        skippedCount++
      } else if (downloadInfo.wasSuccess()) {
        successCount++
      } else {
        errorCount++
        // log any messages for those that weren't skipped
        QER_DLOG.log { downloadInfo.logMessage ?: "<no message provided>" }
      }
    }
    
    if (successFlag) {
      pauseTwoSeconds() // wait a bit so user can read the last price update
      val message = MessageFormat.format(
        _resources.getString(L10NStockQuotes.FINISHED_DOWNLOADING_FMT),
        _resources.getString(L10NStockQuotes.QUOTES)
      )
      _model.showProgress(0f, message)
      QER_DLOG.log("Finished downloading Security Price Quotes")
    }
    
    
    return successFlag
  }
  
  
  companion object {
    const val NAME: String = "DownloadTask"
  }
}