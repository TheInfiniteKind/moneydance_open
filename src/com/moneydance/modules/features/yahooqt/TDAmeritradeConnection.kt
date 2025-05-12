package com.moneydance.modules.features.yahooqt

import com.google.gson.Gson
import com.infinitekind.moneydance.model.AccountBook
import com.infinitekind.util.AppDebug
import com.infinitekind.util.StringUtils.isBlank
import com.moneydance.awt.GridC
import com.moneydance.awt.JLinkLabel
import com.moneydance.awt.JTextPanel
import com.moneydance.modules.features.yahooqt.SQUtil.urlEncode
import com.moneydance.modules.features.yahooqt.tdameritrade.History
import java.awt.GridBagLayout
import java.awt.event.ActionEvent
import java.net.URI
import java.net.URISyntaxException
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.text.MessageFormat
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.CompletableFuture
import java.util.concurrent.ExecutionException
import java.util.function.Function
import java.util.stream.Collectors
import javax.swing.*
import kotlin.collections.ArrayList
import kotlin.math.min
import kotlin.streams.toList

/**
 * Download quotes and exchange rates from tdameritrade.com
 * This requires an API key which customers can register for at runtime and enter in the
 * prompt shown by this connection.
 *
 *
 * Note: connections are throttled to avoid TDAmeritrade's low threshold for
 * rejecting frequent connections.
 */
class TDAmeritradeConnection(model: StockQuotesModel) : APIKeyConnection(PREFS_KEY, model, HISTORY_SUPPORT) {
  private val refreshDateFmt = SimpleDateFormat("yyyy-MM-dd hh:mm:ss") // 2017-11-07 11:46:52
  
  // TDAmeritrade limits all non-order related requests to 120 per minute.
  private val BURST_RATE_PER_MINUTE = 120
  
  private var remainingToUpdate = ArrayList<DownloadInfo>()
  
  override fun getAPIKey(evenIfAlreadySet: Boolean): String? {
    if (!evenIfAlreadySet && cachedAPIKey != null) return cachedAPIKey
    
    if (model == null) return null
    
    val book = model.book ?: return null
    
    val root = book.getRootAccount()
    val apiKey = root.getParameter(
      "tdameritrade.apikey",
      model.preferences.getSetting("tdameritrade_apikey", null)
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
          model.showURL("https://developer.tdameritrade.com/content/getting-started")
        }
      }
      val defaultAPIKey = existingAPIKey ?: ""
      signupAction.putValue(Action.NAME, model.resources.getString("tdameritrade.apikey_action"))
      val linkButton = JLinkLabel(signupAction)
      p.add(
        JTextPanel(model.resources.getString("tdameritrade.apikey_msg")),
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
          root.setParameter("tdameritrade.apikey", inputString)
          model.preferences.setSetting("tdameritrade_apikey", inputString)
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
    val model = model
    return if (model == null) "" else model.resources.getString("tdameritrade")
  }
  
  /**
   * Retrieve the current exchange rate for the given currency relative to the base
   *
   * @param downloadInfo The wrapper for the currency to be downloaded and the download results
   */
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
  }
  
  @Throws(URISyntaxException::class)
  private fun getHistoryURI(fullTickerSymbol: String): URI {
    val apiKey = getAPIKey(false)
    val uriStr = String.format(HISTORY_URL, urlEncode(fullTickerSymbol), urlEncode(apiKey))
    
    println(uriStr)
    return URI(uriStr)
  }
  
  //	int processors = Runtime.getRuntime().availableProcessors();
  //	ExecutorService executorService = Executors.newFixedThreadPool(processors);
  var client: HttpClient = HttpClient.newBuilder() //			.executor(executorService)
    .version(HttpClient.Version.HTTP_2)
    .build()
  
  init {
    refreshDateFmt.isLenient = true
  }
  
  override fun updateSecurities(securitiesToUpdate: List<DownloadInfo>): Boolean {
    var progressPercent = 0.0f
    val progressIncrement = if (securitiesToUpdate.isEmpty()) 1.0f else 100.0f / securitiesToUpdate.size.toFloat()
    val success = true
    
    this.remainingToUpdate = ArrayList(securitiesToUpdate)
    val retry: MutableList<DownloadInfo> = ArrayList()
    var remaining: Int
    var completedCount = 0
    do {
      val completed = updateSecurities()
      val requests = completed.size
      val original = securitiesToUpdate.size
      for (downloadInfo in completed) {
        if (downloadInfo.historyCount == 0) {
          retry.add(downloadInfo)
        } else {
          progressPercent += progressIncrement
          val message: String
          val logMessage: String
          if (!downloadInfo.wasSuccess()) {
            message = MessageFormat.format(
              model.resources.getString(L10NStockQuotes.ERROR_EXCHANGE_RATE_FMT),
              downloadInfo.security.idString,
              downloadInfo.relativeCurrency.idString
            )
            logMessage = MessageFormat.format(
              "Unable to get rate from {0} to {1}",
              downloadInfo.security.idString,
              downloadInfo.relativeCurrency.idString
            )
          } else {
            message = downloadInfo.buildPriceDisplayText(model.quotesModel)
            logMessage = downloadInfo.buildPriceLogText(model.quotesModel)
          }
          model.showProgress(progressPercent, message)
          didUpdateItem(downloadInfo)
        }
      }
      remainingToUpdate?.removeAll(completed)
      
      remaining = remainingToUpdate.size
      completedCount = original - remaining
      println(String.format("Updated %d quotes out of %d", completedCount, original))
      
      if (remaining > 0 && requests > 119) {
        try {
          println("WAIT: 1 minute")
          Thread.sleep(60000)
        } catch (e: InterruptedException) {
          e.printStackTrace()
        }
      }
    } while (remaining > 0 && completedCount > 0)
    return true
  }
  
  private fun updateSecurities(): List<DownloadInfo> {
    val count = min(BURST_RATE_PER_MINUTE, remainingToUpdate!!.size)
    println(String.format("Updates %d quotes out of %d", count, remainingToUpdate!!.size))
    
    return remainingToUpdate.stream()
      .map { stock -> this.updateOneSecurity(stock) }
      .limit(BURST_RATE_PER_MINUTE.toLong())
      .toList()
  }
  
  override fun updateSecurity(downloadInfo: DownloadInfo) {
    //don't use this one
  }
  
  protected fun updateOneSecurity(stock: DownloadInfo): DownloadInfo {
    if (stock.historyCount > 0) return stock
    
    var di: CompletableFuture<DownloadInfo>? = null
    try {
      val uri = getHistoryURI(stock.fullTickerSymbol)
      
      di = client.sendAsync(HttpRequest.newBuilder(uri).GET().build(), HttpResponse.BodyHandlers.ofString())
        .thenApply(Function { response: HttpResponse<String> ->
          println("""
                ${stock.fullTickerSymbol}:
                ${response.body()}
                """.trimIndent()
          )
          val gson = Gson()
          
          
          // 1. JSON file to Java object
          val history = gson.fromJson(response.body(), History::class.java)
          stock.addHistory(history)
          stock
        })
    } catch (uri: URISyntaxException) {
      AppDebug.DEBUG.log("URI Error updating $stock", uri)
    }
    
    var stockReturn: DownloadInfo? = null
    try {
      stockReturn = di!!.get()
    } catch (e: InterruptedException) {
      e.printStackTrace()
    } catch (e: ExecutionException) {
      e.printStackTrace()
    }
    
    return stockReturn ?: stock
  }
  
  companion object {
    private val SNAPSHOT_DATE_FORMAT = SimpleDateFormat("yyyy-MM-dd")
    
    const val PREFS_KEY: String = "tdameritrade"
    private const val apiKey = ""
    private const val HISTORY_URL = "https://api.tdameritrade.com/v1/marketdata/%s/pricehistory?apikey=%s&periodType=month&period=1&frequencyType=daily"
    
    private var cachedAPIKey: String? = null
    private var suppressAPIKeyRequestUntilTime: Long = 0
    
    @JvmStatic
    fun main(args: Array<String>) {
      if (args.size < 1) {
        System.err.println("usage: <thiscommand> <tdameritrade-apikey> <symbols>...")
        System.err.println(
          " -x: parameters after -x in the parameter list are symbols are three digit currency codes instead of security/ticker symbols"
        )
        System.exit(-1)
      }
      
      cachedAPIKey = args[0].trim()
      
      val conn = TDAmeritradeConnection(createEmptyTestModel())
      runTests(null, conn, args.copyOfRange(1, args.size))
    }
  }
}