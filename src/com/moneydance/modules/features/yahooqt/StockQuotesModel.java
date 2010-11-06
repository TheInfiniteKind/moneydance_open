/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.SecurityAccount;
import com.moneydance.apps.md.model.time.TimeInterval;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.util.BasePropertyChangeReporter;
import com.moneydance.util.CustomDateFormat;

import javax.swing.SwingUtilities;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
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
  private RootAccount _rootAccount = null;
  private UserPreferences _preferences = null;
  private BaseConnection _selectedHistoryConnection = null;
  private BaseConnection _selectedCurrentPriceConnection = null;
  private BaseConnection _selectedExchangeRatesConnection = null;
  private boolean _saveCurrentInHistorical = false;
  private Vector<BaseConnection> _connectionList = null;
  private int _historyDays = 5;
  private boolean _dirty = false;

  // runs tasks on a separate thread
  private ConnectionTask _currentTask;
  private final Object _taskSync = new Object();
  private final ExecutorService _executor = Executors.newFixedThreadPool(1);

  StockQuotesModel() {
    _tableModel = new SecuritySymbolTableModel(this);
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

  void setData(RootAccount rootAccount) {
    _symbolMap.clear();
    _rootAccount = rootAccount;
    if (rootAccount != null) {
      _symbolMap.loadFromFile(rootAccount);
      _saveCurrentInHistorical = _rootAccount.getBooleanParameter(Main.SAVE_CURRENT_IN_HISTORY_KEY, false);
      _cancelTasks.set(false);
    }
    _dirty = false;
  }

  void buildSecurityMap() {
    _securityMap.clear();
    // this will call back in to addSecurity
    _tableModel.load();
  }

  void addSecurity(SecurityAccount account, CurrencyType securityCurrency) {
    // build a map of securities and the parent investment accounts that own them
    Set<Account> accountSet = _securityMap.get(securityCurrency);
    if (accountSet == null) accountSet = new HashSet<Account>();
    // the parent of a security is always an investment account
    accountSet.add(account.getParentAccount());
    _securityMap.put(securityCurrency, accountSet);
  }

  MoneydanceGUI getGUI() {
    return _mdGUI;
  }

  UserPreferences getPreferences() {
    return _preferences;
  }

  SymbolMap getSymbolMap() {
    return _symbolMap;
  }

  StockExchangeList getExchangeList() {
    return _exchangeList;
  }

  RootAccount getRootAccount() {
    return _rootAccount;
  }

  void setDirty() {
    _dirty = true;
  }

  boolean isDirty() {
    return _dirty;
  }

  void runStockPriceDownload(final PropertyChangeListener listener) {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    final StockQuotesModel model = this;
    Thread tempThread = new Thread(new Runnable() {
      public void run() {
        final ConnectionTask task = new ConnectionTask(
                new DownloadQuotesTask(model, _resources), model, _resources);
        setCurrentTask(task, false);
        addPropertyChangeListener(listener);
        _executor.execute(task);
        // all notifications are set to the Swing EDT
        firePropertyChange(_eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
        waitForCurrentTaskToFinish();
        removePropertyChangeListener(listener);
      }
    }, "Download Security Prices");
    tempThread.start();
  }

  void runRatesDownload(final PropertyChangeListener listener) {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    final StockQuotesModel model = this;
    Thread tempThread = new Thread(new Runnable() {
      public void run() {
        final ConnectionTask task = new ConnectionTask(
                new DownloadRatesTask(model, _resources), model, _resources);
        setCurrentTask(task, false);
        addPropertyChangeListener(listener);
        _executor.execute(_currentTask);
        // all notifications are set to the Swing EDT
        firePropertyChange(_eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
        waitForCurrentTaskToFinish();
        removePropertyChangeListener(listener);
      }
    }, "Download Exchange Rates");
    tempThread.start();
  }

  void runDownloadTest() {
    // the test is interactive (and on the EDT) so don't wait for the current task to finish
    final ConnectionTask task = new ConnectionTask(
            new DownloadQuotesTest(this, _resources), this, _resources);
    setCurrentTask(task, true);
    _executor.execute(_currentTask);
    // all notifications are set to the Swing EDT
    firePropertyChange(_eventNotify, N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
  }

  public void runUpdateIfNeeded(final boolean delayStart, final PropertyChangeListener listener)
  {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    final StockQuotesModel model = this;
    Thread tempThread = new Thread(new Runnable() {
      public void run() {
        final ConnectionTask task = new ConnectionTask(
                new UpdateIfNeededTask(model, _resources, listener, delayStart), model, _resources);
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
    if (isCurrentPriceSelected()) {
      return true;
    }
    return isHistoricalPriceSelected();
  }

  boolean isCurrentPriceSelected() {
    final BaseConnection connection = getSelectedCurrentPriceConnection();
    return ((connection != null) && !NO_CONNECTION.equals(connection));
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

  void saveSettings() {
    if (_rootAccount == null) return;  // do nothing; unexpected
    if (_selectedHistoryConnection != null) {
      _rootAccount.setParameter(Main.HISTORY_CONNECTION_KEY, _selectedHistoryConnection.getId());
    }
    if (_selectedCurrentPriceConnection != null) {
      _rootAccount.setParameter(Main.CURRENT_PRICE_CONNECTION_KEY, _selectedCurrentPriceConnection.getId());
    }
    if (_selectedExchangeRatesConnection != null) {
      _rootAccount.setParameter(Main.EXCHANGE_RATES_CONNECTION_KEY, _selectedExchangeRatesConnection.getId());
    }
    _rootAccount.setParameter(Main.SAVE_CURRENT_IN_HISTORY_KEY, _saveCurrentInHistorical);
    // store the results of the table - this updates the symbol map - must be done before symbol map
    _tableModel.save();
    // save the map of security/currency to stock exchanges
    _symbolMap.saveToFile(_rootAccount);
    _dirty = false;
  }

  BaseConnection getSelectedHistoryConnection() {
    // load the selected connection from preferences if it hasn't been set
    if (_selectedHistoryConnection == null)
    {
      loadSelectedConnections();
    }
    return _selectedHistoryConnection;
  }

  BaseConnection getSelectedCurrentPriceConnection() {
    // load the selected connection from preferences if it hasn't been set
    if (_selectedCurrentPriceConnection == null)
    {
      loadSelectedConnections();
    }
    return _selectedCurrentPriceConnection;
  }

  BaseConnection getSelectedExchangeRatesConnection() {
    // load the selected connection from preferences if it hasn't been set
    if (_selectedExchangeRatesConnection == null)
    {
      loadSelectedConnections();
    }
    return _selectedExchangeRatesConnection;
  }
  
  void setSelectedHistoryConnection(BaseConnection baseConnection) {
    final BaseConnection original = _selectedHistoryConnection;
    _selectedHistoryConnection = baseConnection;
    if (!SQUtil.areEqual(original, _selectedHistoryConnection)) setDirty();
  }

  void setSelectedCurrentPriceConnection(BaseConnection baseConnection) {
    final BaseConnection original = _selectedCurrentPriceConnection;
    _selectedCurrentPriceConnection = baseConnection;
    if (!SQUtil.areEqual(original, _selectedCurrentPriceConnection)) setDirty();
  }

  void setSelectedExchangeRatesConnection(BaseConnection baseConnection) {
    final BaseConnection original = _selectedExchangeRatesConnection;
    _selectedExchangeRatesConnection = baseConnection;
    if (!SQUtil.areEqual(original, _selectedExchangeRatesConnection)) setDirty();
  }

  void setSaveCurrentAsHistory(final boolean saveInHistory) {
    boolean previous = _saveCurrentInHistorical;
    _saveCurrentInHistorical = saveInHistory;
    if (previous != saveInHistory) setDirty();
  }

  boolean getSaveCurrentAsHistory() { return _saveCurrentInHistorical; }

  Vector<BaseConnection> getConnectionList(final int type) {
    final Vector<BaseConnection> results = new Vector<BaseConnection>();
    results.add(NO_CONNECTION);
    for (BaseConnection connection : _connectionList) {
      switch (type) {
        case BaseConnection.HISTORY_SUPPORT :
          if (connection.canGetHistory()) results.add(connection);
          break;
        case BaseConnection.CURRENT_PRICE_SUPPORT :
          if (connection.canGetCurrentPrice()) results.add(connection);
          break;
        case BaseConnection.EXCHANGE_RATES_SUPPORT :
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
    if (_rootAccount == null) return;
    CustomDateFormat dateFormat = _preferences.getShortDateFormatter();
    System.err.println("Saving last successful price quotes date of: "+dateFormat.format(lastDate));
    _rootAccount.setParameter(Main.QUOTE_LAST_UPDATE_KEY, lastDate);
  }

  void saveLastExchangeRatesUpdateDate(final int lastDate) {
    if (_rootAccount == null) return;
    CustomDateFormat dateFormat = _preferences.getShortDateFormatter();
    System.err.println("Saving last successful exchange rates date of: "+dateFormat.format(lastDate));
    _rootAccount.setParameter(Main.RATE_LAST_UPDATE_KEY, lastDate);
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
    // all notifications are set to the Swing EDT already (see constructor)
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
    _selectedCurrentPriceConnection = null;
    _selectedExchangeRatesConnection = null;
    if (_rootAccount == null) return;
    // stock price history
    String key = _rootAccount.getParameter(Main.HISTORY_CONNECTION_KEY, null);
    if (SQUtil.isBlank(key))  {
      key = YahooConnectionUSA.PREFS_KEY; // default
    }
    if (NO_CONNECTION.getId().equals(key)) {
      _selectedHistoryConnection = NO_CONNECTION;
    } else {
      for (BaseConnection connection : _connectionList) {
        if (key.equals(connection.getId())) {
          _selectedHistoryConnection = connection;
          break;
        }
      }
    }

    // current stock price
    key = _rootAccount.getParameter(Main.CURRENT_PRICE_CONNECTION_KEY, null);
    if (SQUtil.isBlank(key))  {
      key = YahooConnectionUSA.PREFS_KEY; // default
    }
    if (NO_CONNECTION.getId().equals(key)) {
      _selectedCurrentPriceConnection = NO_CONNECTION;
    } else {
      for (BaseConnection connection : _connectionList) {
        if (key.equals(connection.getId())) {
          _selectedCurrentPriceConnection = connection;
          break;
        }
      }
    }
    // currency exchange rates
    key = _rootAccount.getParameter(Main.EXCHANGE_RATES_CONNECTION_KEY, null);
    if (SQUtil.isBlank(key))  {
      key = FXConnection.PREFS_KEY; // default
    }
    if (NO_CONNECTION.getId().equals(key)) {
      _selectedExchangeRatesConnection = NO_CONNECTION;
    } else {
      for (BaseConnection connection : _connectionList) {
        if (key.equals(connection.getId())) {
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
    _connectionList = new Vector<BaseConnection>();
    String displayName = resources.getString(L10NStockQuotes.YAHOO_USA);
    _connectionList.add(new YahooConnectionUSA(this, displayName));
    displayName = resources.getString(L10NStockQuotes.YAHOO_UK);
    _connectionList.add(new YahooConnectionUK(this, displayName));
    displayName = resources.getString(L10NStockQuotes.GOOGLE);
    _connectionList.add(new GoogleConnection(this, displayName));
    displayName = resources.getString(L10NStockQuotes.YAHOO_RATES);
    _connectionList.add(new FXConnection(this, displayName));
  }
}
