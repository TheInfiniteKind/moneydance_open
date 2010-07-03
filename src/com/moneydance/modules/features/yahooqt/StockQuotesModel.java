package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.SecurityAccount;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.FutureTask;

/**
 * Contains the data needed by the stock quotes synchronizer plugin.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class StockQuotesModel extends BasePropertyChangeReporter {

  private final StockExchangeList _exchangeList = new StockExchangeList();
  private final SymbolMap _symbolMap = new SymbolMap(_exchangeList);
  private final Map<CurrencyType, Set<Account>> _securityMap =
          new HashMap<CurrencyType, Set<Account>>();
  private final SecuritySymbolTableModel _tableModel;
  private final ResourceProvider _resources;
  private MoneydanceGUI _mdGUI = null;
  private RootAccount _rootAccount = null;
  private UserPreferences _preferences = null;
  private BaseConnection _selectedConnection = null;
  private Vector<BaseConnection> _connectionList = null;
  private boolean _dirty = false;

  // runs tasks on a separate thread
  private FutureTask _currentTask;
  private final Object _taskSync = new Object();
  private final ExecutorService _executor = Executors.newFixedThreadPool(2);

  StockQuotesModel(final ResourceProvider resources) {
    super(true);
    _resources = resources;
    _tableModel = new SecuritySymbolTableModel(this);  
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
      // define the currency for the default exchange to be the same as the root file's
      CurrencyType baseCurrency = _rootAccount.getCurrencyTable().getBaseType();
      StockExchange.DEFAULT.setCurrency(baseCurrency);
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

  Set<Account> getSecurityAccountSet(CurrencyType securityCurrency) {
    return _securityMap.get(securityCurrency);
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
  
  BaseConnection getSelectedConnection() {
    // load the selected connection from preferences if it hasn't been set
    if (_selectedConnection == null)
    {
      loadSelectedConnection();
    }
    return _selectedConnection;
  }

  void runStockPriceDownload() {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    final StockQuotesModel model = this;
    System.err.println("[ksm] runStockPriceDownload()");
    Thread tempThread = new Thread(new Runnable() {
      public void run() {
        final ConnectionTask task = new ConnectionTask(
                new DownloadQuotesTask(model, _resources), model, _resources);
        System.err.println("[ksm] Setting stocks task, waiting for previous to finish.");
        setCurrentTask(task, false);
        System.err.println("[ksm] Submitting stocks task.");
        _executor.execute(task);
        // all notifications are set to the Swing EDT already (see constructor)
        _eventNotify.firePropertyChange(N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
      }
    });
    tempThread.start();
  }

  void runRatesDownload() {
    // make sure we don't submit this task on the Event Data Thread, which will block while waiting
    // for the previous task to complete
    final StockQuotesModel model = this;
    System.err.println("[ksm] runRatesDownload()");
    Thread tempThread = new Thread(new Runnable() {
      public void run() {
        final ConnectionTask task = new ConnectionTask(
                new DownloadRatesTask(model, _resources), model, _resources);
        System.err.println("[ksm] Setting rates task, waiting for previous to finish.");
        setCurrentTask(task, false);
        System.err.println("[ksm] Submitting rates task.");
        _executor.execute(_currentTask);
        // all notifications are set to the Swing EDT already (see constructor)
        _eventNotify.firePropertyChange(N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
      }
    });
    tempThread.start();
  }

  void runDownloadTest() {
    // the test is interactive (and on the EDT) so don't wait for the current task to finish
    final ConnectionTask task = new ConnectionTask(
            new DownloadQuotesTest(this, _resources), this, _resources);
    setCurrentTask(task, true);
    System.err.println("[ksm] Submitting download test task.");
    _executor.execute(_currentTask);
    // all notifications are set to the Swing EDT already (see constructor)
    _eventNotify.firePropertyChange(N12EStockQuotes.DOWNLOAD_BEGIN, null, null);
  }

  void cancelCurrentTask() {
    final boolean sendEvent;
    synchronized(_taskSync) {
      sendEvent = (_currentTask != null);
      if (sendEvent) {
        System.err.println("[ksm] Canceling current task.");
        _currentTask.cancel(true);
      }
    }
    downloadDone(sendEvent);
  }

  private void waitForCurrentTaskToFinish() {
    synchronized (_taskSync) {
      if (_currentTask != null) {
        try {
          System.err.println("[ksm] Waiting for current task to finish...");
          _taskSync.wait();
        } catch (InterruptedException ignore) {
          // do nothing
        }
        System.err.println("[ksm] Wait complete.");
      } else {
        System.err.println("[ksm] No waiting needed, no current task");
      }
    }
  }

  void downloadDone(boolean sendEvent) {
    System.err.println("[ksm] downloadDone()");
    synchronized (_taskSync) {
      if (_currentTask != null) {
        // signal any waiting threads in waitForCurrentTaskToFinish() that we're done
        System.err.println("[ksm] Notifying wait is complete.");
        _taskSync.notifyAll();
        System.err.println("[ksm] Setting current task to null.");
        _currentTask = null;
      }
    }
    if (sendEvent) fireDownloadEnd();
  }

  void showProgress(final float percent, final String status) {
    // all notifications are set to the Swing EDT already (see constructor)
    _eventNotify.firePropertyChange(N12EStockQuotes.STATUS_UPDATE, Float.toString(percent), status);
  }

  private void fireDownloadEnd() {
    // all notifications are set to the Swing EDT already (see constructor)
    System.err.println("[ksm] Signal download end.");
    _eventNotify.firePropertyChange(N12EStockQuotes.DOWNLOAD_END, null, null);
  }

  private void setCurrentTask(final FutureTask task, final boolean cancelCurrentTask) {
    if (cancelCurrentTask) {
      System.err.println("[ksm] Calling cancelCurrentTask().");
      cancelCurrentTask();
    } else {
      System.err.println("[ksm] Calling waitForCurrentTaskToFinish().");
      waitForCurrentTaskToFinish();
    }
    synchronized (_taskSync) {
      _currentTask = task;
    }
  }

  private void loadSelectedConnection() {
    _selectedConnection = null;
    if (_rootAccount == null) return;
    String key = _rootAccount.getParameter(Main.CONNECTION_KEY, null);
    if (SQUtil.isBlank(key))  {
      key = YahooConnectionUSA.PREFS_KEY; // default
    }
    for (BaseConnection connection : _connectionList) {
      if (key.equals(connection.getId()))
      {
        _selectedConnection = connection;
        break;
      }
    }
  }
  
  void saveSettings() {
    if (_rootAccount == null) return;  // do nothing; unexpected
    if (_selectedConnection != null) {
      _rootAccount.setParameter(Main.CONNECTION_KEY, _selectedConnection.getId());
    }
    // store the results of the table - this updates the symbol map - must be done before symbol map
    _tableModel.save();
    // save the map of security/currency to stock exchanges
    _symbolMap.saveToFile(_rootAccount);
    _dirty = false;
  }

  void setSelectedConnection(BaseConnection baseConnection) {
    final BaseConnection original = _selectedConnection;
    _selectedConnection = baseConnection;
    _dirty |= !SQUtil.isEqual(original, _selectedConnection);
  }

  Vector<BaseConnection> getConnectionList() {
    return _connectionList;
  }

  void fireUpdateHeaderEvent() {
    _eventNotify.firePropertyChange(N12EStockQuotes.HEADER_UPDATE, null, null);
  }

  private void buildConnectionList(ResourceProvider resources) {
    _connectionList = new Vector<BaseConnection>();
    String displayName = resources.getString(L10NStockQuotes.YAHOO_USA);
    _connectionList.add(new YahooConnectionUSA(this, displayName));
    displayName = resources.getString(L10NStockQuotes.YAHOO_UK);
    _connectionList.add(new YahooConnectionUK(this, displayName));
    displayName = resources.getString(L10NStockQuotes.GOOGLE);
    _connectionList.add(new GoogleConnection(this, displayName));
  }
}
