/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.google.gson.JsonArray
import com.google.gson.JsonElement
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import com.infinitekind.moneydance.model.DateRange
import com.infinitekind.util.DateUtil
import com.infinitekind.util.DateUtil.convertIntDateToLong
import com.infinitekind.util.DateUtil.incrementDate
import com.infinitekind.util.DateUtil.strippedDateInt
import com.infinitekind.util.StringUtils.isBlank
import com.moneydance.modules.features.yahooqt.tdameritrade.Candle
import org.apache.http.HttpStatus
import org.apache.http.client.HttpClient
import org.apache.http.client.config.CookieSpecs
import org.apache.http.client.config.RequestConfig
import org.apache.http.client.methods.HttpGet
import org.apache.http.impl.client.HttpClients
import org.apache.http.message.BasicHeader
import org.apache.http.util.EntityUtils
import kotlin.math.max
import kotlin.math.pow

/**
 * Class for downloading security prices from Yahoo
 */
class YahooConnection private constructor(model: StockQuotesModel, connectionType: YahooConnectionType) : BaseConnection(connectionType.preferencesKey(), model, connectionType.updateTypes()) {
  private enum class YahooConnectionType {
    DEFAULT, UK, CURRENCIES;
    
    fun preferencesKey(): String {
      return when (this) {
        UK -> "yahooUK"
        CURRENCIES -> "yahooRates"
        DEFAULT -> "yahooUSA"
        else -> "yahooUSA"
      }
    }
    
    val isUK: Boolean
      get() = this == UK
    
    fun updateTypes(): Int {
      return when (this) {
        CURRENCIES -> EXCHANGE_RATES_SUPPORT
        UK, DEFAULT -> HISTORY_SUPPORT
        else -> HISTORY_SUPPORT
      }
    }
  }
  
  private val requestConfig: RequestConfig = RequestConfig.custom().setCookieSpec(CookieSpecs.STANDARD).build()
  private val httpClient: HttpClient = HttpClients.custom().setDefaultRequestConfig(requestConfig)
    .setUserAgent(ConnectionTweaks.rotatingUserAgent)
    .setDefaultHeaders(java.util.List.of(BasicHeader("Accept-Language", "en-US,en;q=0.9")))
    .build()
  
  override fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String? {
    if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) return null
    // check if the exchange was already added on, which will override the selected exchange
    if (!SQUtil.isBlank(parsedSymbol.suffix)) {
      return parsedSymbol.symbol + parsedSymbol.suffix
    }
    // Check if the selected exchange has a Yahoo suffix or not. If it does, add it.
    val suffix = exchange?.symbolYahoo
    if (SQUtil.isBlank(suffix)) return parsedSymbol.symbol
    return parsedSymbol.symbol + suffix
  }
  
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: YahooConnection does not currently support exchange rate downloads")
  }
  
  
  override fun updateSecurities(securitiesToUpdate: List<DownloadInfo>): Boolean {
    // TODO: if there's any initialisation step, that goes here before updateSecurity() is invoked for each individual security
    
    return super.updateSecurities(securitiesToUpdate)
  }
  
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  public override fun updateSecurity(downloadInfo: DownloadInfo) {
    QER_LOG.log("yahoo: updating security: " + downloadInfo.fullTickerSymbol)
    val today = strippedDateInt
    val history = downloadInfo.security.snapshots
    var firstDate = incrementDate(today, 0, -6, -0)
    if (!history.isEmpty()) {
      firstDate = max(history.last().dateInt, firstDate)
    }
    
    val urlStr = getHistoryURL(downloadInfo.fullTickerSymbol, DateRange(firstDate, today))
    val httpGet = HttpGet(urlStr)
    val ua = ConnectionTweaks.rotatingUserAgent
    httpGet.setHeader("User-Agent", ua)
    
    try {
      val response = httpClient.execute(httpGet)
      val errMessage = "retrieving quote from " + urlStr + " : " + response.statusLine + " (user-agent: '${ua}')"
      if (response.statusLine.statusCode != HttpStatus.SC_OK) {
        QER_LOG.log("Error $errMessage")
        downloadInfo.recordError("Error $errMessage")
        return
      } else {
        QER_DLOG.log(lazyMessage = { "Success $errMessage" })
      }
      
      val json = EntityUtils.toString(response.entity)
      val jsonData = JsonParser.parseString(json).asJsonObject
      
      extractHistoryFromJSON(downloadInfo, jsonData)
    } catch (e: Exception) {
      downloadInfo.recordError("Error retrieving quote from " + urlStr + " : " + e.message)
      QER_LOG.log("Error retrieving quote for " + downloadInfo.fullTickerSymbol + " from " + urlStr + " (user-agent: '${ua}')", e)
    }
  }
  
  private fun extractHistoryFromJSON(downloadInfo: DownloadInfo, jsonData: JsonObject) {
    val chart = jsonData.getAsJsonObject("chart")
    val error = if (chart["error"].isJsonNull) null else chart["error"].asString
    if (!isBlank(error)) {
      downloadInfo.recordError(error)
      return
    }
    
    val result = chart.getAsJsonArray("result").asJsonArray[0].asJsonObject
    
    var meta: JsonObject? = null
    var priceHint: Int? = null
    var regularMarketPrice: Double? = null

    val metaStr = "meta"
    val priceHintStr = "priceHint"
    val regularMarketPriceStr = "regularMarketPrice"
    
    // grab the main meta section
    if (result != null && result.has(metaStr) && !result[metaStr].isJsonNull) {
      meta = result.getAsJsonObject(metaStr)
      // grab price hint for number of decimals and price rounding
      if (meta.has(priceHintStr) && !meta[priceHintStr].isJsonNull) {
        priceHint = meta[priceHintStr].asInt
      }
      // grab the regular market price - (i.e. the price now) as displayed on the yahoo main web page - NOTE: this needs no rounding!
      if (meta.has(regularMarketPriceStr) && !meta[regularMarketPriceStr].isJsonNull) {
        regularMarketPrice = meta[regularMarketPriceStr].asDouble
      }
    }
    
    // map a list of the timestamps to long objects
    val timestampArray = result.getAsJsonArray("timestamp")
    if (timestampArray == null || timestampArray.isEmpty) {
      downloadInfo.recordError("No timestamped results received")
      return
    }
    val timestamps = timestampArray.asList().stream().mapToLong { obj: JsonElement -> obj.asLong }.toArray()
    val indicators = result.getAsJsonObject("indicators")
    val quoteArray = indicators.getAsJsonArray("quote")
    if (quoteArray == null || quoteArray.isEmpty) {
      downloadInfo.recordError("Response had missing or empty quote indicator")
      return
    }
    val quoteInfo = quoteArray[0].asJsonObject
    if (quoteInfo == null || quoteInfo.isJsonNull) {
      downloadInfo.recordError("Response had empty quote indicator")
      return
    }
    
    val closeValues = quoteInfo.getAsJsonArray("close")
    val volumeValues = quoteInfo.getAsJsonArray("volume")
    val highValues = quoteInfo.getAsJsonArray("high")
    val openValues = quoteInfo.getAsJsonArray("open")
    val lowValues = quoteInfo.getAsJsonArray("low")
    val records = ArrayList<StockRecord>()
    for (i in timestamps.indices) {
      val candle = Candle()
      candle.datetime = timestamps[i] * 1000
      volumeValues.getSafeLong(i)?.let { candle.volume = it }
      openValues.getSafeDouble(i)?.let { candle.open = it.priceHintRound(priceHint) }
      lowValues.getSafeDouble(i)?.let { candle.low = it.priceHintRound(priceHint) }
      highValues.getSafeDouble(i)?.let { candle.high = it.priceHintRound(priceHint) }
      closeValues.getSafeDouble(i)?.let { candle.close = it.priceHintRound(priceHint) }
      if (candle.datetime > 0 && candle.close > 0.0) // protect against scenario where the date is present with no valid (or null) data for that date.
        records.add(StockRecord(candle, downloadInfo.priceMultiplier))
    }
    downloadInfo.addHistoryRecords(records.sortedBy { it.date })
  }
  
  private fun getHistoryURL(fullTickerSymbol: String, dateRange: DateRange): String {
    //  private static final String CURRENT_PRICE_URL_BASE_UK = "https://uk.old.finance.yahoo.com/d/quotes.csv";
    //  private static final String HISTORY_URL_BASE_UK =       "https://ichart.yahoo.com/table.csv";
    
    val encodedTicker = SQUtil.urlEncode(fullTickerSymbol)
    
    val startTime = convertIntDateToLong(dateRange.startDateInt).time / 1000
    val endTime = convertIntDateToLong(dateRange.endDateInt).time / 1000
    
    val baseURL = "https://query1.finance.yahoo.com/v8/finance/chart/$encodedTicker"
    val commonParams = listOf(
      "interval=1d",
      "includePrePost=true",
      "events=div%7Csplit%7Cearn", // possibly "events=history"
      "lang=en-US",
      "region=US"
    )
    
    val queryURL = if (DateUtil.calculateDaysBetween(dateRange.startDateInt, dateRange.endDateInt) <= 5) {
      "$baseURL?range=5d&${commonParams.joinToString("&")}"
    } else {
      "$baseURL?period1=${startTime}&period2=${endTime}&${commonParams.joinToString("&")}"
    }
      return queryURL
  }
  
  private fun Double.priceHintRound(hint: Int?): Double {
    hint ?: return this
    if (hint < 0 || hint > 20) return this
    val scale: Double = 10.0.pow(hint)
    return Math.round(this * scale) / scale
  }
  
  private fun JsonArray?.getSafeDouble(idx:Int): Double? {
    this ?: return null
    val safeVal = if (idx < 0 || idx >= this.size()) { return null } else { this[idx] ?: return null }
    if(safeVal.isJsonNull) return null
    if(safeVal.isJsonPrimitive) return safeVal.asDouble
    return null
  }
  
  private fun JsonArray?.getSafeLong(idx:Int): Long? {
    this ?: return null
    val safeVal = if (idx < 0 || idx >= this.size()) { return null } else { this[idx] ?: return null }
    if(safeVal.isJsonNull) return null
    if(safeVal.isJsonPrimitive) return safeVal.asLong
    return null
  }
  
  
  override fun toString(): String {
    return if (model == null) "??" else model.resources.getString(connectionID)
  }
  
  
  companion object {
    fun getDefaultConnection(model: StockQuotesModel): YahooConnection {
      return YahooConnection(model, YahooConnectionType.DEFAULT)
    }
    
    fun getUKConnection(model: StockQuotesModel): YahooConnection {
      return YahooConnection(model, YahooConnectionType.UK)
    }
    
    fun getCurrenciesConnection(model: StockQuotesModel): YahooConnection {
      return YahooConnection(model, YahooConnectionType.CURRENCIES)
    }
  }
}
