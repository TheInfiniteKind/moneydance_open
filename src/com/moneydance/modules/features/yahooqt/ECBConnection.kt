package com.moneydance.modules.features.yahooqt

import com.infinitekind.util.DateUtil.convertIntDateToLong
import com.infinitekind.util.DateUtil.firstMinuteInDay
import com.infinitekind.util.DateUtil
import com.infinitekind.util.StringUtils.isBlank
import com.infinitekind.util.StringUtils.parseDouble
import org.w3c.dom.Document
import org.w3c.dom.Node
import org.w3c.dom.NodeList
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.*
import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.xpath.XPathConstants
import javax.xml.xpath.XPathFactory

/**
 * Connection for updating exchange rates from the European Central Bank
 */
class ECBConnection(model: StockQuotesModel) : BaseConnection(PREFS_KEY, model, EXCHANGE_RATES_SUPPORT) {
  private val dateFormat: DateFormat = SimpleDateFormat("yyyy-MM-dd")
  
  init {
    dateFormat.isLenient = true
  }
  
  override val perConnectionThrottleTime: Long
    /**
     * Alphavantage connections should be throttled to approximately one every 1.1 seconds
     */
    get() = 100 // throttle only so we dont exceed 10 requests per second
  
  
  override fun toString(): String {
    return model.resources.getString("ecb") ?: "ecb"
  }
  
  
  /** Update the currencies in the given list  */
  override fun updateExchangeRates(currenciesToUpdate: List<DownloadInfo>): Boolean {
    if (currenciesToUpdate.size <= 0) return true
    
    
    // download the page of exchange rates, and update any matching items in currenciesToUpdate
    var ratesDoc: Document? = null
    try {
      ratesDoc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(FXRATES_URL)
    } catch (e: Exception) {
      for (info in currenciesToUpdate) {
        info.recordError("Enable to retrieve rates from ECB: $e")
      }
      e.printStackTrace()
      return false
    }
    
    class ECBRate(var currencyID: String, var rate: Double)
    
    var rateDateTime = firstMinuteInDay(convertIntDateToLong(DateUtil.strippedDateInt)).time
    val rateMap = HashMap<String, Double>()
    
    try {
      val xpathLocator = XPathFactory.newInstance().newXPath()
      val rateTimeNode = xpathLocator.evaluate("//Cube[@time]", ratesDoc.documentElement, XPathConstants.NODE) as Node
      if (rateTimeNode != null) {
        val dateAttNode = rateTimeNode.attributes.getNamedItem("time")
        if (dateAttNode != null) {
          val dateValue = dateAttNode.nodeValue
          if (!isBlank(dateValue)) {
            rateDateTime = firstMinuteInDay(dateFormat.parse(dateValue)).time
            System.err.println("ECB rates date stamp: '" + dateValue + "' parsed to " + (Date(rateDateTime)))
          }
        }
      }
      val rateNodes = xpathLocator.evaluate(
        "//Cube[@currency]",
        ratesDoc.documentElement, XPathConstants.NODESET
      ) as NodeList
      for (i in 0..<rateNodes.length) {
        val rateNode = rateNodes.item(i)
        val nodeAtts = rateNode.attributes
        val currencyAttNode = nodeAtts.getNamedItem("currency")
        val rateAttNode = nodeAtts.getNamedItem("rate")
        if (currencyAttNode != null && rateAttNode != null) {
          rateMap[currencyAttNode.nodeValue] = parseDouble(rateAttNode.nodeValue, '.')
        }
      }
    } catch (e: Exception) {
      for (info in currenciesToUpdate) {
        info.recordError("Error parsing response from ECB: $e")
      }
      e.printStackTrace()
      return false
    }
    
    System.err.println("Downloaded exchange rates from ECB: $rateMap")
    
    val currencies = model.book!!.currencies
    val baseCurrency = currencies.baseType
    val baseRateD = rateMap[baseCurrency.idString]
    if (baseRateD == null) {
      for (downloadInfo in currenciesToUpdate) {
        downloadInfo.recordError(" error: Couldn't find my base currency (" + baseCurrency.idString + ") in ECB exchange rate list")
      }
      return false
    }
    
    val baseToEuroRate: Double = baseRateD
    for (downloadInfo in currenciesToUpdate) {
      val currencyID = downloadInfo.security.idString
      var rateToEuroD = rateMap[currencyID]
      if (currencyID.equals("EUR", ignoreCase = true)) { // the currencies are returned relative to the Euro, so this will be 1
        rateToEuroD = 1.0
      } else if (rateToEuroD == null) {
        downloadInfo.recordError("Couldn't find currency ($currencyID) in ECB exchange rate list")
        continue
      }
      val rateToBase = rateToEuroD / baseToEuroRate
      System.err.println(
        "new fx rate: " + currencyID + " to " + baseCurrency.idString +
        " as of " + (Date(rateDateTime)) + "; " +
        " was " + downloadInfo.security.getUserRate() + " -> " +
        rateToBase
      )
      downloadInfo.relativeCurrency = baseCurrency
      downloadInfo.setRate(rateToBase, rateDateTime)
    }
    
    
    return true
  }
  
  override fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String? {
    return null
  }
  
  override fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange?): String? {
    return null
  }
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: ECB offers exchange rates in batch, so you shouldn't see this message.")
  }
  
  override fun updateSecurity(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: ECB does not offer security prices")
  }
  
  
  companion object {
    const val PREFS_KEY: String = "ecb"
    private const val FXRATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    
    private fun infoForID(idString: String, downloadInfos: List<DownloadInfo>): DownloadInfo? {
      for (info in downloadInfos) {
        if (idString.equals(info.security.idString, ignoreCase = true)) {
          return info
        }
      }
      return null
    }
    
    private fun safeInversion(rate: Double): Double {
      return if (rate == 0.0) 0.0 else 1 / rate
    }
    
    
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
      val conn = ECBConnection(createEmptyTestModel())
      runTests(conn, null, args)
    }
  }
}
