/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.AccountBook
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.util.CustomDateFormat
import com.moneydance.apps.md.controller.FeatureModuleContext
import com.moneydance.apps.md.controller.UserPreferences
import com.moneydance.apps.md.controller.time.TimeInterval
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import java.beans.PropertyChangeListener
import java.beans.PropertyChangeSupport
import java.io.IOException
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean
import javax.swing.SwingUtilities
import kotlin.Comparator

/**
 * Contains the data needed by the stock quotes synchronizer plugin.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class StockQuotesModel internal constructor(private val extensionContext: FeatureModuleContext) : BasePropertyChangeReporter() {
  private val NO_CONNECTION = NoConnection(this)
  
  val exchangeList: StockExchangeList = StockExchangeList()
  val symbolMap: SymbolMap = SymbolMap(exchangeList)
  private val _securityMap: MutableMap<CurrencyType, MutableSet<Account?>> = HashMap()
  val tableModel: SecuritySymbolTableModel
  private val _cancelTasks = AtomicBoolean(false)
  var gui = (extensionContext as com.moneydance.apps.md.controller.Main).ui as MoneydanceGUI
    private set
  var book: AccountBook? = null
    private set
  val preferences = gui.preferences
  var uIDateFormat: CustomDateFormat
    private set
  private var dateTimeFormat: SimpleDateFormat? = null
  private var _selectedHistoryConnection: BaseConnection? = null
  private var _selectedExchangeRatesConnection: BaseConnection? = null
  private var _connectionList = mutableListOf<BaseConnection>()
  var historyDays: Int = 5
    private set
  var decimalDisplayChar: Char = '.'
    private set
  var isDirty: Boolean = false
    private set
  
  private var languageBundle:XmlResourceBundle? = null
    set(newBundle) {
      field = newBundle
      NO_CONNECTION.setDisplayName(resources.getString(L10NStockQuotes.NO_CONNECTION))
    }
  
  var resources = object: ResourceProvider {
    override fun getString(key: String): String {
      return languageBundle?.getString(key) ?: "<<$key>>"
    }
  }
  
  // runs tasks on a separate thread
  private var _currentTask: ConnectionTask? = null
  private val _taskSync = Any()
  private val _executor: ExecutorService = Executors.newFixedThreadPool(1)
  
  init {
    val englishInputStream = BaseConnection::class.java.getResourceAsStream(N12EStockQuotes.ENGLISH_PROPERTIES_FILE)
    try {
      languageBundle = XmlResourceBundle(englishInputStream)
    } catch (e: IOException) {
      languageBundle = null
      e.printStackTrace()
    }
    
    uIDateFormat = CustomDateFormat("ymd")
    tableModel = SecuritySymbolTableModel(this)
  }
  
  /**
   * Called when the plugin initializes - does not require the data file yet.
   * @param mdGUI User interface object for the application.
   * @param resources Provider of local string resources for internationalization.
   */
  fun initialize(mdGUI: MoneydanceGUI, resources: ResourceProvider) {
    gui = mdGUI
    uIDateFormat = preferences.getShortDateFormatter()
    dateTimeFormat = SimpleDateFormat(uIDateFormat.pattern + " h:mm a")
    decimalDisplayChar = preferences.getDecimalChar()
    tableModel.initialize(preferences)
    exchangeList.load()
    buildConnectionList(resources)
    isDirty = false
  }
  
  fun cleanUp() {
    try {
      _executor.shutdownNow()
    } catch (ignore: SecurityException) {
      // do nothing
    }
  }
  
  fun setData(book: AccountBook?) {
    symbolMap.clear()
    this.book = book
    if (book != null) {
      symbolMap.loadFromFile(book)
      _cancelTasks.set(false)
    }
    isDirty = false
  }
  
  fun buildSecurityMap() {
    _securityMap.clear()
    // this will call back in to addSecurity
    tableModel.load()
  }
  
  fun addSecurity(account: Account?, securityCurrency: CurrencyType) {
    // build a map of securities and the parent investment accounts that own them
    var accountSet = _securityMap[securityCurrency]
    if (accountSet == null) {
      accountSet = HashSet()
      _securityMap[securityCurrency] = accountSet
    }
    // if account!=null, then add it's parent investment account
    if (account != null) accountSet.add(account.getParentAccount())
  }
  
  fun showURL(url: String?) {
    extensionContext.showURL(url)
  }
  
  val uIDateTimeFormat: DateFormat?
    get() = dateTimeFormat
  
  val rootAccount: Account?
    get() = book?.getRootAccount()
  
  fun setDirty() {
    isDirty = true
  }
  
  fun downloadRatesAndPricesInBackground(listener: PropertyChangeListener?) {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    val model = this
    val tempThread = Thread({
                              firePropertyChange(eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null)
                              val task = ConnectionTask(DownloadTask(model, resources), model, resources)
                              setCurrentTask(task, false)
                              addPropertyChangeListener(listener)
                              _executor.execute(_currentTask)
                              waitForCurrentTaskToFinish()
                              removePropertyChangeListener(listener)
                            }, "Download Exchange Rates and Prices")
    tempThread.start()
  }
  
  fun runDownloadTest() {
    // the test is interactive (and on the EDT) so don't wait for the current task to finish
    val downloadTask = DownloadTask(this, resources)
    downloadTask.includeTestInfo = true
    val task = ConnectionTask(downloadTask, this, resources)
    setCurrentTask(task, true)
    _executor.execute(_currentTask)
    // all notifications are set to the Swing EDT
    firePropertyChange(eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null)
  }
  
  fun runUpdateIfNeeded(delayStart: Boolean, listener: PropertyChangeListener?) {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    val model = this
    val tempThread = Thread(Runnable {
      val task = ConnectionTask(UpdateIfNeededTask(model, resources, listener, delayStart), model, resources)
      setCurrentTask(task, false)
      addPropertyChangeListener(listener)
      if (_cancelTasks.get()) return@Runnable
      _executor.execute(_currentTask)
      // all notifications are set to the Swing EDT
      if (_cancelTasks.get()) return@Runnable
      firePropertyChange(eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null)
      waitForCurrentTaskToFinish()
      removePropertyChangeListener(listener)
    }, "Update If Needed Task")
    tempThread.start()
  }
  
  fun cancelCurrentTask() {
    val sendEvent: Boolean
    val taskName: String
    synchronized(_taskSync) {
      sendEvent = (_currentTask != null)
      if (sendEvent) {
        taskName = _currentTask!!.taskName
        _currentTask!!.cancel(true)
        _cancelTasks.set(true)
      } else {
        taskName = ""
      }
    }
    downloadDone(sendEvent, taskName, java.lang.Boolean.FALSE)
  }
  
  val isStockPriceSelected: Boolean
    get() = isHistoricalPriceSelected
  
  val isHistoricalPriceSelected: Boolean
    get() {
      val connection = selectedHistoryConnection
      return ((connection != null) && NO_CONNECTION != connection)
    }
  
  val isExchangeRateSelected: Boolean
    get() {
      val connection = selectedExchangeRatesConnection
      return ((connection != null) && NO_CONNECTION != connection)
    }
  
  fun setHistoryDaysFromFrequency(frequency: TimeInterval) {
    when (frequency) {
      TimeInterval.DAY -> historyDays = 5
      TimeInterval.WEEK -> historyDays = 7
      TimeInterval.MONTH -> historyDays = 32
      TimeInterval.QUARTER -> historyDays = 95
      TimeInterval.YEAR -> historyDays = 365
      else -> historyDays = 5
    }
  }
  
  fun downloadDone(sendEvent: Boolean, taskName: String, success: Boolean) {
    if (sendEvent) fireDownloadEnd(taskName, success)
    synchronized(_taskSync) {
      if (_currentTask != null) {
        // signal any waiting threads in waitForCurrentTaskToFinish() that we're done
        (_taskSync as Object).notifyAll()
        _currentTask = null
      }
    }
  }
  
  fun showProgress(percent: Float, status: String?) {
    // all notifications are set to the Swing EDT
    firePropertyChange(eventNotify, N12EStockQuotes.STATUS_UPDATE, percent.toString(), status)
  }
  
  fun saveSettings(root: Account?) {
    if (root == null) return  // do nothing; unexpected
    
    if (_selectedHistoryConnection != null) {
      root.setParameter(Main.HISTORY_CONNECTION_KEY, _selectedHistoryConnection!!.connectionID)
    }
    if (_selectedExchangeRatesConnection != null) {
      root.setParameter(Main.EXCHANGE_RATES_CONNECTION_KEY, _selectedExchangeRatesConnection!!.connectionID)
    }
    // store the results of the table - this updates the symbol map - must be done before symbol map
    tableModel.save(root)
    // save the map of security/currency to stock exchanges
    symbolMap.saveToFile(root)
    isDirty = false
    root.syncItem()
  }
  
  var selectedHistoryConnection: BaseConnection?
    get() {
      // load the selected connection from preferences if it hasn't been set
      if (_selectedHistoryConnection == null) {
        loadSelectedConnections()
      }
      return _selectedHistoryConnection
    }
    set(baseConnection) {
      val modified = !SQUtil.areEqual(baseConnection, _selectedHistoryConnection)
      _selectedHistoryConnection = baseConnection
      if (modified) setDirty()
    }
  
  var selectedExchangeRatesConnection: BaseConnection?
    get() {
      // load the selected connection from preferences if it hasn't been set
      if (_selectedExchangeRatesConnection == null) {
        loadSelectedConnections()
      }
      return _selectedExchangeRatesConnection
    }
    set(baseConnection) {
      val modified = !SQUtil.areEqual(baseConnection, _selectedExchangeRatesConnection)
      _selectedExchangeRatesConnection = baseConnection
      if (modified) setDirty()
    }
  
  fun getConnectionList(type: Int): Array<BaseConnection> {
    val results = mutableListOf<BaseConnection>()
    results.add(NO_CONNECTION)
    for (connection in _connectionList) {
      when (type) {
        BaseConnection.HISTORY_SUPPORT -> if (connection.canGetHistory()) results.add(connection)
        BaseConnection.EXCHANGE_RATES_SUPPORT -> if (connection.canGetRates()) results.add(connection)
      }
    }
    return results.toTypedArray()
  }
  
  fun fireUpdateHeaderEvent() {
    firePropertyChange(eventNotify, N12EStockQuotes.HEADER_UPDATE, null, null)
  }
  
  fun saveLastQuoteUpdateDate(lastDate: Int) {
    book ?: return
    QER_DLOG.log { "Saving last successful price quotes date of: $lastDate" }
    book?.getRootAccount()?.setParameter(Main.QUOTE_LAST_UPDATE_KEY, lastDate)
  }
  
  fun saveLastExchangeRatesUpdateDate(lastDate: Int) {
    book ?: return
    QER_DLOG.log { "Saving last successful exchange rates date of: $lastDate" }
    book?.getRootAccount()?.setParameter(Main.RATE_LAST_UPDATE_KEY, lastDate)
  }
  
  val quotesLastUpdateDate: Int
    get() {
      return book?.getRootAccount()?.getIntParameter(Main.QUOTE_LAST_UPDATE_KEY, 0) ?: 0
    }
  
  val ratesLastUpdateDate: Int
    get() {
      return book?.getRootAccount()?.getIntParameter(Main.RATE_LAST_UPDATE_KEY, 0) ?: 0
    }
  
  
  private fun waitForCurrentTaskToFinish() {
    synchronized(_taskSync) {
      if (_currentTask != null) {
        try {
          while (!_cancelTasks.get() && (_currentTask != null)) {
            (_taskSync as Object).wait(250L)
          }
        } catch (ignore: InterruptedException) {
          // do nothing
        }
      }
    }
  }
  
  private fun fireDownloadEnd(taskName: String, success: Boolean) {
    firePropertyChange(eventNotify, N12EStockQuotes.DOWNLOAD_END, taskName, success)
  }
  
  private fun setCurrentTask(task: ConnectionTask, cancelCurrentTask: Boolean) {
    if (cancelCurrentTask) {
      cancelCurrentTask()
    } else {
      waitForCurrentTaskToFinish()
    }
    synchronized(_taskSync) {
      _currentTask = task
    }
  }
  
  private fun loadSelectedConnections() {
    _selectedHistoryConnection = null
    _selectedExchangeRatesConnection = null
    val root = book?.getRootAccount() ?: return
    // stock price history
    var key = root.getParameter(Main.HISTORY_CONNECTION_KEY)
    if(key==null || key.isBlank()) {
      key = IEXConnection.PREFS_KEY
    }
    if (NO_CONNECTION.connectionID == key) {
      _selectedHistoryConnection = NO_CONNECTION
    } else {
      for (connection in _connectionList) {
        if (key == connection.connectionID) {
          _selectedHistoryConnection = connection
          break
        }
      }
    }
    
    
    // currency exchange rates
    key = root.getParameter(Main.EXCHANGE_RATES_CONNECTION_KEY, null)
    if (SQUtil.isBlank(key)) {
      key = ECBConnection.PREFS_KEY // default
    }
    if (NO_CONNECTION.connectionID == key) {
      _selectedExchangeRatesConnection = NO_CONNECTION
    } else {
      for (connection in _connectionList) {
        if (key == connection.connectionID) {
          _selectedExchangeRatesConnection = connection
          break
        }
      }
    }
  }
  
  private fun buildConnectionList(resources: ResourceProvider) {
    _connectionList.add(IEXConnection(this))
    _connectionList.add(AlphavantageConnection(this))
    _connectionList.add(TDAmeritradeConnection(this))
    //_connectionList.add(YahooConnection.getCurrenciesConnection(this)); // omitting yahoo rates since ECB bas much faster results
    _connectionList.add(YahooConnection.getDefaultConnection(this))
    //_connectionList.add(FTConnection.getDefaultConnection(this));
    //_connectionList.add(YahooConnection.getUKConnection(this)); // omitting because https://ichart.yahoo.com/table.csv no longer resolves
    //_connectionList.add(new GoogleConnection(this, resources.getString(L10NStockQuotes.GOOGLE)));
    _connectionList.add(ECBConnection(this))
  }
  
  companion object {
    private fun firePropertyChange(notifier: PropertyChangeSupport, name: String,
                                   oldValue: Any?, newValue: Any?) {
      // notify on the event data thread (Swing thread)
      val runnable = Runnable { notifier.firePropertyChange(name, oldValue, newValue) }
      if (SwingUtilities.isEventDispatchThread()) {
        runnable.run()
      } else {
        SwingUtilities.invokeLater(runnable)
      }
    }
  }
}
