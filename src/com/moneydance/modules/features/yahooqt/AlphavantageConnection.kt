package com.moneydance.modules.features.yahooqt

import com.google.gson.Gson
import com.google.gson.stream.JsonReader
import com.infinitekind.util.DateUtil
import com.infinitekind.util.IOUtils
import com.infinitekind.util.StringUtils
import com.infinitekind.util.StringUtils.isBlank
import com.moneydance.apps.md.controller.UserPreferences
import com.moneydance.awt.GridC
import com.moneydance.awt.JLinkLabel
import com.moneydance.awt.JTextPanel
import java.awt.GridBagLayout
import java.awt.event.ActionEvent
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStreamReader
import java.net.URL
import java.nio.charset.StandardCharsets
import java.text.SimpleDateFormat
import java.util.*
import javax.swing.*

// TODO: Implement batch quote retrieval as in https://www.alpha-vantage.community/post/example-batchstockquotes-code-9629661?highlight=batch&pid=1302984266
/**
 *
 * Download quotes and exchange rates from alphavantage.co
 * This requires an API key which customers can register for at runtime and enter in the
 * prompt shown by this connection.
 *
 * Note: connections are *heavily* throttled to avoid Alphavantage's low threshold for
 * rejecting frequent connections.
 */
class AlphavantageConnection(model: StockQuotesModel) : APIKeyConnection(PREFS_KEY, model, HISTORY_SUPPORT or EXCHANGE_RATES_SUPPORT) {

  private val refreshDateFmt = SimpleDateFormat("yyyy-MM-dd hh:mm:ss").also { it.isLenient = true }  // 2017-11-07 11:46:52
  
  private val prefs = model.preferences
  private val remainingRequests = Int.MAX_VALUE
  private val lastRequestDate = 0
  
  private var connectionThrottleCounter = 0
  
  
  init {
    refreshDateFmt.isLenient = true
  }
  
  /**
   * Alphavantage connections should be throttled to approximately one every 1.1 seconds
   */
  override val perConnectionThrottleTime:Long
    get() {
    connectionThrottleCounter++
    return 1500
    //    if(connectionThrottleCounter%4 == 0) {
//      return 20000; // every Nth connection, delay for 15 seconds
//    } else {
//      return 10000; // pause for 1.5 seconds after each connection
//    }
  }
  
  
  override fun getAPIKey(evenIfAlreadySet: Boolean): String? {
    if (!evenIfAlreadySet && cachedAPIKey != null) return cachedAPIKey
    
    if (model == null) return null
    
    val book = model.book ?: return null
    
    val root = book.getRootAccount() ?: return null
    val apiKey = root.getParameter("alphavantage.apikey") ?: model.preferences.getSetting("alphavantage_apikey")
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
          model.showURL("https://infinitekind.com/alphavantage")
        }
      }
      val defaultAPIKey = existingAPIKey ?: ""
      signupAction.putValue(Action.NAME, model.resources?.getString("alphavantage.apikey_action") ?: "")
      val linkButton = JLinkLabel(signupAction)
      p.add(
        JTextPanel(model.resources?.getString("alphavantage.apikey_msg") ?: ""),
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
          root.setParameter("alphavantage.apikey", inputString)
          model.preferences.setSetting("alphavantage_apikey", inputString)
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
    return model?.resources?.getString("alphavantage") ?: "Alphavantage"
  }
  
  /**
   * Retrieve the current exchange rate for the given currency relative to the base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
    val baseCurrencyID = downloadInfo.relativeCurrency.idString.uppercase(Locale.getDefault())
    if (!downloadInfo.isValidForDownload) return
    
    val apiKey = getAPIKey(false)
    if (apiKey == null) {
      downloadInfo.recordError("No Alphavantage API Key Provided")
      return
    }
    
    val urlStr = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE" +
                 "&from_currency=" + SQUtil.urlEncode(downloadInfo.fullTickerSymbol) +
                 "&to_currency=" + SQUtil.urlEncode(baseCurrencyID) +
                 "&apikey=" + SQUtil.urlEncode(apiKey) +
                 "&outputsize=compact"
    
    
    /*
     {
     "Realtime Currency Exchange Rate": {
         "1. From_Currency Code": "USD",
         "2. From_Currency Name": "United States Dollar",
         "3. To_Currency Code": "EUR",
         "4. To_Currency Name": "Euro",
         "5. Exchange Rate": "0.86488300",
         "6. Last Refreshed": "2017-11-07 11:46:52",
         "7. Time Zone": "UTC"
      }
    }
    */
    try {
      val url = URL(urlStr)
      val bout = ByteArrayOutputStream()
      IOUtils.copyStream(url.openConnection().getInputStream(), bout)
      val jsonReader = JsonReader(InputStreamReader(ByteArrayInputStream(bout.toByteArray()), StandardCharsets.UTF_8))
      val gson = Gson()
      val gsonData = gson.fromJson<Map<*, *>>(jsonReader, MutableMap::class.java)
      
      val rateInfoObj = gsonData["Realtime Currency Exchange Rate"]
      if (rateInfoObj is Map<*, *>) {
        val rateInfo = rateInfoObj
        val rateObj = rateInfo["5. Exchange Rate"]
        val rateDateObj = rateInfo["6. Last Refreshed"]
        var rateDate = DateUtil.firstMinuteInDay(Date()).time
        if (rateDateObj != null) {
          rateDate = refreshDateFmt.parse(rateDateObj.toString()).time
        }
        
        if (rateObj != null) {
          val rate = StringUtils.parseDouble(rateObj.toString(), -1.0, '.')
          if (rate > 0) {
            downloadInfo.setRate(1 / rate, rateDate)
          }
        }
      }
      try {
        downloadInfo.testMessage = String(bout.toByteArray(), charset("UTF8"))
      } catch (t: Throwable) {
      }
    } catch (connEx: Exception) {
      downloadInfo.recordError("Connection Error: $connEx")
    }
  }
  
  protected val currentPriceHeader: String
    get() = "date,open,high,low,close,volume"
  
  fun getHistoryURL(fullTickerSymbol: String?, apiKey:String): String? {
    return ("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY" +
                                          "&symbol=" + SQUtil.urlEncode(fullTickerSymbol) +
                                          "&apikey=" + SQUtil.urlEncode(apiKey) +
                                          "&datatype=csv" +
                                          "&outputsize=compact")
  }
  
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  public override fun updateSecurity(downloadInfo: DownloadInfo) {
    System.err.println("alphavantage: getting history for " + downloadInfo.fullTickerSymbol)
    val apiKey = getAPIKey(false).takeIf { !it.isNullOrBlank() }
    if(apiKey==null) {
      downloadInfo.recordError("No Alphavantage API Key Provided")
      return
    }
    val urlStr = getHistoryURL(downloadInfo.fullTickerSymbol, apiKey)
    if (urlStr == null) {
      // this basically means that an API key wasn't available
      downloadInfo.recordError("No API Key Available")
      return
    }
    
    val decimal = model.preferences.decimalChar
    val importer = SnapshotImporterFromURL(urlStr, cookie, model.resources,
                                           downloadInfo, SNAPSHOT_DATE_FORMAT,
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
    
    if (downloadInfo.fullTickerSymbol.endsWith(".L") && recordList.size > 1) {
      // special case when Alphavantage provides the first (aka current date) price in pence instead of GBP for some LSE securities
      val first = recordList[0]
      val second = recordList[1]
      if (first.closeRate > (second.closeRate / 100) * 0.9 && first.closeRate < (second.closeRate / 100) * 1.1) {
        for (i in recordList.size - 1 downTo 1) { // adjust all but the first entry
          val record = recordList[i]
          record.closeRate /= 100.0
          record.highRate /= 100.0
          record.lowRate /= 100.0
          record.open /= 100.0
        }
      }
    }
    downloadInfo.addHistoryRecords(recordList)
  }
  
  companion object {
    private val SNAPSHOT_DATE_FORMAT = SimpleDateFormat("yyyy-MM-dd")
    
    const val PREFS_KEY: String = "alphavantage"
    private var cachedAPIKey: String? = null
    private var suppressAPIKeyRequestUntilTime: Long = 0
    
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
      if (args.size < 1) {
        System.err.println("usage: <thiscommand> <alphavantage-apikey> <symbols>...")
        System.err.println(" -x: parameters after -x in the parameter list are symbols are three digit currency codes instead of security/ticker symbols")
        System.exit(-1)
      }
      
      cachedAPIKey = args[0].trim()
      
      val conn = AlphavantageConnection(createEmptyTestModel())
      runTests(conn, conn, Arrays.copyOfRange(args, 1, args.size))
    }
  }
}
