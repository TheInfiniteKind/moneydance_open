/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.util.DateUtil.convertIntDateToLong
import com.infinitekind.util.DateUtil.incrementDate
import com.infinitekind.util.DateUtil.strippedDateInt
import com.infinitekind.util.StringUtils.fieldIndex
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.*

/**
 * q = symbol
 * cid = Company Id
 * startdate = Start date of the historical prices
 * enddate = End date of the historical prices
 * histperiod = weekly or daily history periods
 * start = index on which to display the historical price
 * num = number of historical prices to display (this has some max like 100 or 200)
 * output = output the data in a format (I think it currently supports CSV only)
 * http://www.google.com/finance/historical?q=LON:VOD&startdate=Jun+1%2C+2010&enddate=Jun+19%2C+2010&output=csv
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class GoogleConnection(model: StockQuotesModel, private val _displayName: String) : BaseConnection(PREFS_KEY, model, HISTORY_SUPPORT) {
  // example for 6/19/2010 = Jun+19%2C+2010
  private val _dateFormat: DateFormat = SimpleDateFormat("MMM+d,+yyyy", Locale.US)
  
  override fun toString(): String {
    return _displayName
  }
  
  override fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String? {
    if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) return null
    // check if the exchange was already added on, which will override the selected exchange
    if (!SQUtil.isBlank(parsedSymbol.prefix)) {
      return parsedSymbol.prefix + ":" + parsedSymbol.symbol
    }
    // Check if the selected exchange has a Google suffix or not. If it does, add it.
    val prefix = exchange?.symbolGoogle ?: ""
    if (SQUtil.isBlank(prefix)) return parsedSymbol.symbol
    return prefix + ":" + parsedSymbol.symbol
  }
  
  override fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange?): String? {
    if (SQUtil.isBlank(rawTickerSymbol)) return null
    // check if this symbol overrides the exchange and the currency code
    val periodIdx = rawTickerSymbol.lastIndexOf(':')
    if (periodIdx > 0) {
      val marketID = rawTickerSymbol.substring(periodIdx + 1)
      if (marketID.indexOf("-") >= 0) {
        // the currency ID was encoded along with the market ID
        return fieldIndex(marketID, '-', 1)
      }
    }
    return exchange?.currencyCode
  }
  
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: Connection to Google Finance doesn't support exchange rates")
  }
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  public override fun updateSecurity(downloadInfo: DownloadInfo) {
    System.err.println("google finance: getting history for " + downloadInfo.fullTickerSymbol)
    val urlStr = getHistoryURL(downloadInfo.fullTickerSymbol)
    
    val decimal: Char = model.preferences.getDecimalChar()
    val importer = SnapshotImporterFromURL(urlStr, cookie, model.resources, downloadInfo, API_DATE_FORMAT,
                                           TimeZone.getTimeZone(timeZoneID), decimal)
    importer.setColumnsFromHeader(currentPriceHeader)
    importer.setPriceMultiplier(downloadInfo.priceMultiplier)
    
    // the return value is negative for general errors, 0 for success with no error, or a positive
    // value for overall success but one or more errors
    val errorResult = importer.importData()
    if (errorResult < 0) {
      val error = importer.lastException
      downloadInfo.errors.add(DownloadException(downloadInfo, error?.message, error))
      return
    }
    val recordList = importer.importedRecords
    if (recordList.isEmpty()) {
      val de = buildDownloadException(downloadInfo, SnapshotImporter.ERROR_NO_DATA)
      downloadInfo.errors.add(de)
      return
    }
    
    downloadInfo.addHistoryRecords(recordList)
  }
  
  fun getHistoryURL(fullTickerSymbol: String): String {
    val endDate = strippedDateInt
    val startDate = incrementDate(endDate, 0, -4, 0)
    
    
    // encoding the dates appears to break Google, so just leave the commas and plus signs in there
    // (Note: their encoder leaves the + signs, but encodes the commas as %2C, but the built-in
    // encoder will do both which is perhaps the problem)
    val encEndDate = _dateFormat.format(convertIntDateToLong(endDate))
    val encStartDate = _dateFormat.format(convertIntDateToLong(startDate))
    
    val result: StringBuilder = StringBuilder(historyBaseUrl)
    result.append("?")
    if (fullTickerSymbol.startsWith("cid=") || fullTickerSymbol.startsWith("CID=")) {
      result.append(fullTickerSymbol)
    } else {
      result.append("q=") // symbol
      result.append(fullTickerSymbol)
    }
    result.append("&startdate=") // start date
    result.append(encStartDate)
    result.append("&enddate=") // end date
    result.append(encEndDate)
    result.append("&output=csv") // output format
    return result.toString()
  }
  
  protected val currentPriceHeader: String?
    get() =// not supported
      null
  
  
  companion object {
    // http://finance.google.co.uk/finance/historical?q=LON:VOD&startdate=Oct+1,2008&enddate=Oct+9,2008&output=csv
    val historyBaseUrl = "http://www.google.com/finance/historical"
    private const val PREFS_KEY = "google"
    private val API_DATE_FORMAT = SimpleDateFormat("d-MMM-yy")
    
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
      val conn = GoogleConnection(createEmptyTestModel(), "Google Finance")
      runTests(conn, conn, args)
    }
  }
}