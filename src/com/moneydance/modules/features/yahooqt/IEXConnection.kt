package com.moneydance.modules.features.yahooqt

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.infinitekind.util.DateUtil.convertDateToInt
import com.infinitekind.util.DateUtil.convertIntDateToLong
import com.infinitekind.util.DateUtil.lastMinuteInDay
import com.infinitekind.util.StringUtils.fieldIndex
import com.infinitekind.util.StringUtils.isBlank
import com.moneydance.awt.GridC
import com.moneydance.awt.JLinkLabel
import com.moneydance.awt.JTextPanel
import java.awt.GridBagLayout
import java.awt.event.ActionEvent
import java.io.InputStreamReader
import java.io.Reader
import java.net.URL
import java.nio.charset.StandardCharsets
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.*
import javax.swing.*
import kotlin.math.min

/**
 * Created by sreilly -  02/11/2017 21:38
 */
class IEXConnection(model: StockQuotesModel) : BaseConnection(PREFS_KEY, model, HISTORY_SUPPORT) {
  private val dateFormat: DateFormat = SimpleDateFormat("yyyy-MM-dd")
  
  /**
   * Connections should be throttled to approximately one every 1.1 seconds
   */
  override val perConnectionThrottleTime: Long
    get() = 100  // throttle only so we dont exceed 10 requests per second
  
  override fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String? {
    if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) return null
    // check if the exchange was already added on, which will override the selected exchange
    if (!SQUtil.isBlank(parsedSymbol.suffix)) {
      return parsedSymbol.symbol + parsedSymbol.suffix
    }
    // Check if the selected exchange has a Yahoo suffix or not. If it does, add it.
    val suffix = exchange?.symbolYahoo ?: ""
    return if (suffix.isBlank()) parsedSymbol.symbol else parsedSymbol.symbol + suffix
  }
  
  override fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange?): String? {
    if (SQUtil.isBlank(rawTickerSymbol)) return null
    // check if this symbol overrides the exchange and the currency code
    val periodIdx = rawTickerSymbol.lastIndexOf('.')
    if (periodIdx > 0) {
      val marketID = rawTickerSymbol.substring(periodIdx + 1)
      if (marketID.contains("-")) {
        // the currency ID was encoded along with the market ID
        return fieldIndex(marketID, '-', 1)
      }
    }
    return exchange?.currencyCode
  }
  
  init {
    dateFormat.isLenient = true
  }
  
  fun getAPIKey(evenIfAlreadySet: Boolean): String? {
    if (!evenIfAlreadySet && cachedAPIKey != null) return cachedAPIKey
    
    val book = model?.book ?: return null
    val root = book.getRootAccount()
    val apiKey = root.getParameter(
      "iextrading.apikey",
      model.preferences.getSetting("iextrading_apikey", null)
    )
    if (!evenIfAlreadySet && !isBlank(apiKey)) {
      return apiKey
    }
    
    if (!evenIfAlreadySet && suppressAPIKeyRequestUntilTime > System.currentTimeMillis()) { // further requests for the key have been suppressed
      return null
    }
    
    val existingAPIKey = apiKey
    val uiActions = Runnable {
      val p = JPanel(GridBagLayout())
      val signupAction: AbstractAction = object : AbstractAction() {
        override fun actionPerformed(e: ActionEvent) {
          model.showURL("https://iexcloud.io/console/")
        }
      }
      val defaultAPIKey = existingAPIKey ?: ""
      signupAction.putValue(Action.NAME, model.resources.getString("iextrading.apikey_action"))
      val linkButton = JLinkLabel(signupAction)
      p.add(
        JTextPanel(model.resources.getString("iextrading.apikey_msg")),
        GridC.getc(0, 0).wxy(1f, 1f)
      )
      p.add(
        linkButton,
        GridC.getc(0, 1).center().insets(12, 16, 0, 16)
      )
      while (true) {
        val inputString = JOptionPane.showInputDialog(null, p, defaultAPIKey)
        if (inputString == null) { // the user canceled the prompt, so let's not ask again for 5 minutes unless this prompt was forced
          if (!evenIfAlreadySet) {
            suppressAPIKeyRequestUntilTime = System.currentTimeMillis() + 1000 * 60 * 5
          }
          return@Runnable
        }
        
        if (!SQUtil.isBlank(inputString) && inputString != JOptionPane.UNINITIALIZED_VALUE) {
          root.setParameter("iextrading.apikey", inputString)
          model.preferences.setSetting("iextrading_apikey", inputString)
          root.syncItem()
          cachedAPIKey = inputString
          return@Runnable
        } else {
          // the user left the field blank or entered an invalid key
          model.beep()
        }
      }
    }
    
    if (SwingUtilities.isEventDispatchThread()) {
      uiActions.run()
    } else {
      try {
        SwingUtilities.invokeAndWait(uiActions)
      } catch (e: Exception) {
        e.printStackTrace()
      }
    }
    return cachedAPIKey
  }
  
  override fun toString(): String {
    return model.resources.getString("iextrading") ?: "IEX Trading"
  }
  
  
  /** Update the currencies in the given list  */
  override fun updateExchangeRates(currenciesToUpdate: List<DownloadInfo>): Boolean {
    for (downloadInfo in currenciesToUpdate) {
      downloadInfo.recordError("Implementation error: IEXTrading does not provide exchange rates")
    }
    return false
  }
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: IEXTrading does not provide exchange rates")
  }
  
  override fun updateSecurity(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: IEXTrading connection should batch requests")
  }
  
  /**
   * Download price history for a security.
   * @param securitiesToUpdate The list of securities to be updated
   * applying (for testing).
   * @return The security price history that was downloaded.
   */
  override fun updateSecurities(securitiesToUpdate: List<DownloadInfo>): Boolean {
    // if we have more than 200 securities in the list, split this into multiple updates...
    var success = false
    var startIdx = 0
    while (startIdx < securitiesToUpdate.size) {
      success = updateLimitedSecurities(securitiesToUpdate.subList(startIdx, min(startIdx + 100, securitiesToUpdate.size)))
      startIdx += 100
    }
    return success
  }
  
  
  private fun updateLimitedSecurities(securityCurrencies: List<DownloadInfo>): Boolean {
    val decimal = model.decimalDisplayChar
    val symbolList = StringBuilder()
    
    val results: MutableMap<String, DownloadInfo> = HashMap()
    // build the symbol list for all valid securities and a SecurityDownloadInfo list to hold the symbols and results
    for (secInfo in securityCurrencies) {
      if (symbolList.length > 0) symbolList.append(",")
      symbolList.append(SQUtil.urlEncode(secInfo.fullTickerSymbol))
      results[secInfo.fullTickerSymbol.lowercase(Locale.getDefault())] = secInfo
    }
    
    
    //https://cloud.iexapis.com/v1/stock/market/batch?symbols=AAPL,BAC&types=chart&range=1m&chartLast=5&token={PRIVATE_TOKEN}
    val apiKey = getAPIKey(false)
    if (apiKey == null) {
      System.err.println("No IEX Cloud API Key Provided")
      return false
    }
    val urlStr = ("https://cloud.iexapis.com/v1/stock/market/batch?"
                  + "symbols=" + symbolList.toString()
                  + "&types=chart&range=1m&chartLast=5"
                  + "&token=" + SQUtil.urlEncode(apiKey))
    System.err.println("getting history using url: $urlStr")
    
    val info: Map<String, Map<String, List<Map<String, Any>>>>
    try {
      val url = URL(urlStr)
      val reader: Reader = InputStreamReader(
        url.openConnection().getInputStream(),
        StandardCharsets.UTF_8
      )
      //JsonReader jsonReader = new JsonReader(reader);
      val gson = Gson()
      //Map gsonData = gson.fromJson(jsonReader, Map.class);
      info = gson.fromJson(reader, object : TypeToken<Map<String?, Map<String?, List<Map<String?, Any?>?>?>?>?>() {
      }.type)
    } catch (e: Exception) {
      return false
    }
    
    for (tickerStr in info.keys) {
      val downloadInfo = results[tickerStr.lowercase(Locale.getDefault())]
      if (downloadInfo == null) {
        System.err.println("iextrading: received result for unrecognized security '$tickerStr'")
        continue
      }
      if (!downloadInfo.isValidForDownload) {
        System.err.println("iextrading: received result for invalid security '$tickerStr'. That shouldn't happen.")
        continue
      }
      val chartInfo = info[tickerStr]!!["chart"]
      if (chartInfo == null) {
        System.err.println("iextrading: response for symbol " + tickerStr + " doesn't include 'chart' data: " + info[tickerStr]!!.keys)
        continue
      }
      
      val snaps: MutableList<StockRecord> = ArrayList()
      for (historyInfo in chartInfo) {
        try {
          /* parse the JSON dictionary for one snapshot
                         {
                         "date": "2018-09-14",
                         "open": 225.75,
                         "high": 226.84,
                         "low": 222.522,
                         "close": 223.84,
                         "volume": 31999289,
                         "unadjustedVolume": 31999289,
                         "change": -2.57,
                         "changePercent": -1.135,
                         "vwap": 224.319,
                         "label": "Sep 14",
                         "changeOverTime": 0.038893530121600274
                         }
                         */
          
          val snap = StockRecord()
          val dateStr = historyInfo.getOrDefault("date", "0000-00-00").toString()
          snap.date = convertDateToInt(dateFormat.parse(dateStr))
          snap.dateTimeGMT = lastMinuteInDay(convertIntDateToLong(snap.date)).time
          snap.volume = Math.round(historyInfo.getOrDefault("volume", "0").toString().toDouble())
          
          snap.lowRate = safeInversion(historyInfo.getOrDefault("low", "0").toString().toDouble())
          snap.highRate = safeInversion(historyInfo.getOrDefault("high", "0").toString().toDouble())
          snap.closeRate = safeInversion(historyInfo.getOrDefault("close", "0").toString().toDouble())
          snap.open = safeInversion(historyInfo.getOrDefault("open", "0").toString().toDouble())
          
          val amount = if (snap.closeRate == 0.0) 0 else downloadInfo.relativeCurrency.getLongValue(1.0 / snap.closeRate)
          snap.priceDisplay = downloadInfo.relativeCurrency.formatFancy(amount, decimal)
          snaps.add(snap)
        } catch (e: Exception) {
          System.err.println("iextrading: error reading record: $historyInfo")
          e.printStackTrace(System.err)
          downloadInfo.errors.add(DownloadException(downloadInfo, "Error reading record", e))
        }
      }
      downloadInfo.addHistoryRecords(snaps)
      downloadInfo.buildPriceDisplay(downloadInfo.relativeCurrency, decimal)
    }
    
    
    // now scan the securities and mark any for which we didn't get data with the appropriate errors/messages
    for (downloadInfo in securityCurrencies) {
      if (downloadInfo.errors.size <= 0 && !downloadInfo.wasSuccess()) {
        downloadInfo.recordError("No data received")
      }
    }
    return true
  }
  
  
  companion object {
    const val PREFS_KEY: String = "iex"
    
    private var cachedAPIKey: String? = null
    private var suppressAPIKeyRequestUntilTime: Long = 0
    
    private fun safeInversion(rate: Double): Double {
      return if (rate == 0.0) 0.0 else 1 / rate
    }
    
    
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
      val iexConn = IEXConnection(createEmptyTestModel())
      runTests(null, iexConn, args)
    }
  }
}
