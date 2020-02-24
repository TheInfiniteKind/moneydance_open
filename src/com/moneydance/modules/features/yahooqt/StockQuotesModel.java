/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.util.CustomDateFormat;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.controller.time.*;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.util.BasePropertyChangeReporter;

import javax.swing.SwingUtilities;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Contains the data needed by the stock quotes synchronizer plugin.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class StockQuotesModel extends BasePropertyChangeReporter
{
  static final NoConnection NO_CONNECTION = new NoConnection();
  private final StockExchangeList _exchangeList = new StockExchangeList();
  private final SymbolMap _symbolMap = new SymbolMap(_exchangeList);
  private final Map<CurrencyType, Set<Account>> _securityMap =
          new HashMap<CurrencyType, Set<Account>>();
  private final SecuritySymbolTableModel _tableModel;
  private final AtomicBoolean _cancelTasks = new AtomicBoolean(false);
  private ResourceProvider _resources;
  private MoneydanceGUI _mdGUI = null;
  private AccountBook book = null;
  private UserPreferences _preferences = null;
  private CustomDateFormat dateFormat;
  private SimpleDateFormat dateTimeFormat;
  private BaseConnection _selectedHistoryConnection = null;
  private BaseConnection _selectedExchangeRatesConnection = null;
  private List<BaseConnection> _connectionList = null;
  private int _historyDays = 5;
  private char decimalDisplayChar = '.';
  private boolean _dirty = false;
  private FeatureModuleContext extensionContext;
  
  // runs tasks on a separate thread
  private ConnectionTask _currentTask;
  private final Object _taskSync = new Object();
  private final ExecutorService _executor = Executors.newFixedThreadPool(1);

  StockQuotesModel(FeatureModuleContext extensionContext) {
    this.extensionContext = extensionContext;
    dateFormat = new CustomDateFormat("ymd");
    
    _tableModel = new SecuritySymbolTableModel(this);
    if (_preferences == null)
    {
      _preferences = UserPreferences.getInstance();
    }
  }

  void setResources(final ResourceProvider resources) {
    _resources = resources;
    // set the 'no connection' name
    NO_CONNECTION.setDisplayName(resources.getString(L10NStockQuotes.NO_CONNECTION));
  }
  ResourceProvider getResources() { return _resources; }
  SecuritySymbolTableModel getTableModel() { return _tableModel; }
  
  /**
   * Called when the plugin initializes - does not require the data file yet.
   * @param mdGUI User interface object for the application.
   * @param resources Provider of local string resources for internationalization.
   */
  void initialize(MoneydanceGUI mdGUI, ResourceProvider resources) {
    _mdGUI = mdGUI;
    _preferences = mdGUI.getPreferences();
    dateFormat = _preferences.getShortDateFormatter();
    dateTimeFormat = new SimpleDateFormat(dateFormat.getPattern() + " h:mm a");
    decimalDisplayChar = _preferences.getDecimalChar();
    _tableModel.initialize(_preferences);
    _exchangeList.load();
    buildConnectionList(resources);
    _dirty = false;
  }

  void cleanUp() {
    try {
      _executor.shutdownNow();
    } catch (SecurityException ignore) {
      // do nothing
    }
  }

  void setData(AccountBook book) {
    _symbolMap.clear();
    this.book = book;
    if (book != null) {
      _symbolMap.loadFromFile(book);
      _cancelTasks.set(false);
    }
    _dirty = false;
  }

  void buildSecurityMap() {
    _securityMap.clear();
    // this will call back in to addSecurity
    _tableModel.load();
  }

  void addSecurity(Account account, CurrencyType securityCurrency) {
    // build a map of securities and the parent investment accounts that own them
    Set<Account> accountSet = _securityMap.get(securityCurrency);
    if (accountSet == null) {
      accountSet = new HashSet<Account>();
      _securityMap.put(securityCurrency, accountSet);
    }
    // if account!=null, then add it's parent investment account
    if(account!=null) accountSet.add(account.getParentAccount());
  }

  MoneydanceGUI getGUI() {
    return _mdGUI;
  }

  void showURL(String url) {
    extensionContext.showURL(url);
  }
  
  UserPreferences getPreferences() {
    return _preferences;
  }

  CustomDateFormat getUIDateFormat() {
    return dateFormat;
  }

  DateFormat getUIDateTimeFormat() {
    return dateTimeFormat;
  }

  SymbolMap getSymbolMap() {
    return _symbolMap;
  }

  StockExchangeList getExchangeList() {
    return _exchangeList;
  }

  Account getRootAccount() {
    return book.getRootAccount();
  }

  AccountBook getBook() {
    return book;
  }

  void setDirty() {
    _dirty = true;
  }

  boolean isDirty() {
    return _dirty;
  }

  void downloadRatesAndPricesInBackground(final PropertyChangeListener listener) {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    final StockQuotesModel model = this;
    Thread tempThread = new Thread(new Runnable() {
      public void run() {
        firePropertyChange(_eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
        
        final ConnectionTask task = new ConnectionTask(new DownloadTask(model, _resources), model, _resources);
        setCurrentTask(task, false);
        addPropertyChangeListener(listener);
        _executor.execute(_currentTask);
        waitForCurrentTaskToFinish();
        removePropertyChangeListener(listener);
      }
    }, "Download Exchange Rates and Prices");
    tempThread.start();
  }

  void runDownloadTest() {
    // the test is interactive (and on the EDT) so don't wait for the current task to finish
    DownloadTask downloadTask = new DownloadTask(this, _resources);
    downloadTask.setIncludeTestInfo(true);
    final ConnectionTask task = new ConnectionTask(downloadTask, this, _resources);
    setCurrentTask(task, true);
    _executor.execute(_currentTask);
    // all notifications are set to the Swing EDT
    firePropertyChange(_eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
  }
  
  public void runUpdateIfNeeded(final boolean delayStart, final PropertyChangeListener listener) {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    final StockQuotesModel model = this;
    Thread tempThread = new Thread(new Runnable() {
      public void run() {
        final ConnectionTask task = new ConnectionTask(new UpdateIfNeededTask(model, _resources, listener, delayStart), 
                                                       model, _resources);
        setCurrentTask(task, false);
        addPropertyChangeListener(listener);
        if (_cancelTasks.get()) return;
        _executor.execute(_currentTask);
        // all notifications are set to the Swing EDT
        if (_cancelTasks.get()) return;
        firePropertyChange(_eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
        waitForCurrentTaskToFinish();
        removePropertyChangeListener(listener);
      }
    }, "Update If Needed Task");
    tempThread.start();
  }

  void cancelCurrentTask() {
    final boolean sendEvent;
    final String taskName;
    synchronized(_taskSync) {
      sendEvent = (_currentTask != null);
      if (sendEvent) {
        taskName = _currentTask.getTaskName();
        _currentTask.cancel(true);
        _cancelTasks.set(true);
      } else {
        taskName = "";
      }
    }
    downloadDone(sendEvent, taskName, Boolean.FALSE);
  }

  boolean isStockPriceSelected() {
    return isHistoricalPriceSelected();
  }
  
  boolean isHistoricalPriceSelected() {
    final BaseConnection connection = getSelectedHistoryConnection();
    return ((connection != null) && !NO_CONNECTION.equals(connection));
  }

  boolean isExchangeRateSelected() {
    final BaseConnection connection = getSelectedExchangeRatesConnection();
    return ((connection != null) && !NO_CONNECTION.equals(connection));
  }
  
  void setHistoryDaysFromFrequency(TimeInterval frequency) {
    switch(frequency) {
      case DAY : _historyDays = 5; break;
      case WEEK : _historyDays = 7; break;
      case MONTH : _historyDays = 32; break;
      case QUARTER : _historyDays = 95; break;
      case YEAR : _historyDays = 365; break;
    }
  }

  int getHistoryDays() { return _historyDays; }

  void downloadDone(boolean sendEvent, String taskName, Boolean success) {
    if (sendEvent) fireDownloadEnd(taskName, success);
    synchronized (_taskSync) {
      if (_currentTask != null) {
        // signal any waiting threads in waitForCurrentTaskToFinish() that we're done
        _taskSync.notifyAll();
        _currentTask = null;
      }
    }
  }

  void showProgress(final float percent, final String status) {
    // all notifications are set to the Swing EDT
    firePropertyChange(_eventNotify, N12EStockQuotes.STATUS_UPDATE, Float.toString(percent), status);
  }

  void saveSettings(Account root) {
    if (root == null) return;  // do nothing; unexpected
    if (_selectedHistoryConnection != null) {
      root.setParameter(Main.HISTORY_CONNECTION_KEY, _selectedHistoryConnection.getConnectionID());
    }
    if (_selectedExchangeRatesConnection != null) {
      root.setParameter(Main.EXCHANGE_RATES_CONNECTION_KEY, _selectedExchangeRatesConnection.getConnectionID());
    }
    // store the results of the table - this updates the symbol map - must be done before symbol map
    _tableModel.save(root);
    // save the map of security/currency to stock exchanges
    _symbolMap.saveToFile(root);
    _dirty = false;
    root.syncItem();
  }

  BaseConnection getSelectedHistoryConnection() {
    // load the selected connection from preferences if it hasn't been set
    if (_selectedHistoryConnection == null)
    {
      loadSelectedConnections();
    }
    return _selectedHistoryConnection;
  }

  BaseConnection getSelectedExchangeRatesConnection() {
    // load the selected connection from preferences if it hasn't been set
    if (_selectedExchangeRatesConnection == null) {
      loadSelectedConnections();
    }
    return _selectedExchangeRatesConnection;
  }
  
  void setSelectedHistoryConnection(BaseConnection baseConnection) {
    boolean modified = !SQUtil.areEqual(baseConnection, _selectedHistoryConnection);
    _selectedHistoryConnection = baseConnection;
    if(modified) setDirty();
  }

  void setSelectedExchangeRatesConnection(BaseConnection baseConnection) {
    boolean modified = ! SQUtil.areEqual(baseConnection, _selectedExchangeRatesConnection);
    _selectedExchangeRatesConnection = baseConnection;
    if(modified) setDirty();
  }

  Vector<BaseConnection> getConnectionList(final int type) {
    final Vector<BaseConnection> results = new Vector<BaseConnection>();
    results.add(NO_CONNECTION);
    for (BaseConnection connection : _connectionList) {
      switch (type) {
        case BaseConnection.HISTORY_SUPPORT:
          if (connection.canGetHistory()) results.add(connection);
          break;
        case BaseConnection.EXCHANGE_RATES_SUPPORT:
          if (connection.canGetRates()) results.add(connection);
          break;
      }
    }
    return results;
  }

  void fireUpdateHeaderEvent() {
   firePropertyChange(_eventNotify, N12EStockQuotes.HEADER_UPDATE, null, null);
  }

  void saveLastQuoteUpdateDate(final int lastDate) {
    if (book == null) return;
    if(Main.DEBUG_YAHOOQT) System.err.println("Saving last successful price quotes date of: "+lastDate);
    book.getRootAccount().setParameter(Main.QUOTE_LAST_UPDATE_KEY, lastDate);
  }

  void saveLastExchangeRatesUpdateDate(final int lastDate) {
    if (book == null) return;
    if(Main.DEBUG_YAHOOQT) System.err.println("Saving last successful exchange rates date of: "+lastDate);
    book.getRootAccount().setParameter(Main.RATE_LAST_UPDATE_KEY, lastDate);
  }
  
  int getQuotesLastUpdateDate() {
    if (book == null) return 0;
    return book.getRootAccount().getIntParameter(Main.QUOTE_LAST_UPDATE_KEY, 0);
  }

  int getRatesLastUpdateDate() {
    if (book == null) return 0;
    return book.getRootAccount().getIntParameter(Main.RATE_LAST_UPDATE_KEY, 0);
  }
  

  private void waitForCurrentTaskToFinish() {
    synchronized (_taskSync) {
      if (_currentTask != null) {
        try {
          while (!_cancelTasks.get() && (_currentTask != null)) {
            _taskSync.wait(250L);
          }
        } catch (InterruptedException ignore) {
          // do nothing
        }
      }
    }
  }

  private void fireDownloadEnd(String taskName, Boolean success) {
    firePropertyChange(_eventNotify, N12EStockQuotes.DOWNLOAD_END, taskName, success);
  }

  private void setCurrentTask(final ConnectionTask task, final boolean cancelCurrentTask) {
    if (cancelCurrentTask) {
      cancelCurrentTask();
    } else {
      waitForCurrentTaskToFinish();
    }
    synchronized (_taskSync) {
      _currentTask = task;
    }
  }
  
  private void loadSelectedConnections() {
    _selectedHistoryConnection = null;
    _selectedExchangeRatesConnection = null;
    Account root = book==null ? null : book.getRootAccount();
    if (root == null) return;
    // stock price history
    String key = root.getParameter(Main.HISTORY_CONNECTION_KEY, null);
    if (SQUtil.isBlank(key))  {
      key = IEXConnection.PREFS_KEY; // default
    }
    if (NO_CONNECTION.getConnectionID().equals(key)) {
      _selectedHistoryConnection = NO_CONNECTION;
    } else {
      for (BaseConnection connection : _connectionList) {
        if (key.equals(connection.getConnectionID())) {
          _selectedHistoryConnection = connection;
          break;
        }
      }
    }
    
    // currency exchange rates
    key = root.getParameter(Main.EXCHANGE_RATES_CONNECTION_KEY, null);
    if (SQUtil.isBlank(key))  {
      key = ECBConnection.PREFS_KEY; // default
    }
    if (NO_CONNECTION.getConnectionID().equals(key)) {
      _selectedExchangeRatesConnection = NO_CONNECTION;
    } else {
      for (BaseConnection connection : _connectionList) {
        if (key.equals(connection.getConnectionID())) {
          _selectedExchangeRatesConnection = connection;
          break;
        }
      }
    }
  }
  
  private static void firePropertyChange(final PropertyChangeSupport notifier, final String name,
                                         final Object oldValue, final Object newValue) {
    // notify on the event data thread (Swing thread)
    final Runnable runnable = new Runnable() {
      public void run() { notifier.firePropertyChange(name, oldValue, newValue); }
    };
    if (SwingUtilities.isEventDispatchThread()) {
      runnable.run();
    } else {
      SwingUtilities.invokeLater(runnable);
    }
  }

  private void buildConnectionList(ResourceProvider resources) {
    _connectionList = new ArrayList<BaseConnection>();
    _connectionList.add(new IEXConnection(this));
    _connectionList.add(new AlphavantageConnection(this));
    //_connectionList.add(YahooConnection.getCurrenciesConnection(this)); // omitting yahoo rates since ECB bas much faster results
    _connectionList.add(YahooConnection.getDefaultConnection(this));
    //_connectionList.add(YahooConnection.getUKConnection(this)); // omitting because https://ichart.yahoo.com/table.csv no longer resolves
    
    //_connectionList.add(new GoogleConnection(this, resources.getString(L10NStockQuotes.GOOGLE)));
    _connectionList.add(new ECBConnection(this));
  }

  public char getDecimalDisplayChar() {
    return decimalDisplayChar;
  }
}
