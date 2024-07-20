/*
 * ************************************************************************
 * Copyright (C) 2012-2015 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.AccountListener;
import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.infinitekind.util.StreamTable;
import com.infinitekind.util.StringEncodingException;
import com.infinitekind.util.StringUtils;
import com.moneydance.util.UiUtil;

import java.beans.PropertyChangeSupport;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Contains the data needed by the ratio calculator extension.
 *
 * @author Kevin Menningen
 */
class RatiosExtensionModel
    extends BasePropertyChangeReporter {
  private ResourceProvider _resources;
  private MoneydanceGUI _mdGUI = null;
  private AccountBook _rootAccount = null;
  private UserPreferences _preferences = null;
  private final AccountListener _accountListener = new RatiosAccountListener();

  private final List<RatioEntry> _ratios = new ArrayList<RatioEntry>();
  private final Object _ratioSync = new Object();
  private RatioSettings _settings = null;

  private RatioCompute _ratioCompute = null;

  // runs tasks on a separate thread
  private final Object _taskSync = new Object();
  private final ExecutorService _executor = Executors.newFixedThreadPool(1);
  private final AtomicBoolean _cancelTasks = new AtomicBoolean(false);
  private Runnable _currentTask = null;

  void setResources(final ResourceProvider resources) {
    _resources = resources;
  }

  ResourceProvider getResources() {
    return _resources;
  }

  /**
   * Called when the plugin initializes - does not require the data file yet.
   *
   * @param mdGUI     User interface object for the application.
   *
   */
  void initialize(MoneydanceGUI mdGUI) {
    _mdGUI = mdGUI;
    _preferences = mdGUI.getPreferences();
  }

  void cleanUp() {
    try {
      _executor.shutdownNow();
    } catch (SecurityException ignore) {
      // do nothing
    }
  }

  /**
   * Define the main data file. Handle the situation where the same file may be assigned several times.
   *
   * @param rootAccount The Moneydance data file.
   */
  void setData(final AccountBook rootAccount) {
    final AccountBook oldRoot = _rootAccount;
    removeAccountListener();
    _rootAccount = rootAccount;
    addAccountListener();
    if ((rootAccount != null) && !RatiosUtil.areEqual(oldRoot, rootAccount)) {
      // setup for a new file - stop any current update
      cancelCurrentTask();
      createSettings();
      loadRatioList();
      _ratioCompute = new RatioCompute(rootAccount, getGUI().getPreferences().getDecimalChar());
      recalculate();
    } else if (rootAccount == null) {
      // clear out the data
      setCurrentTask(null, true);
      _settings = null;
      _rootAccount = null;
    }
    // otherwise the same file has been assigned again, do nothing
  }

  RatioEntry getEntryFromSettingString(String setting, Map<Integer, String> tagMap) {
    try {
      StreamTable settingTable = new StreamTable();
      settingTable.readFrom(setting);
      String encodedAccounts = settingTable.getStr(N12ERatios.NUMERATOR_REQUIRED_LIST_KEY, N12ERatios.EMPTY);
      String revisedAccounts = removeMissingAccounts(encodedAccounts, _rootAccount);
      if (!revisedAccounts.equals(encodedAccounts)) {
        settingTable.put(N12ERatios.NUMERATOR_REQUIRED_LIST_KEY, revisedAccounts);
      }
      encodedAccounts = settingTable.getStr(N12ERatios.DENOMINATOR_REQUIRED_LIST_KEY, N12ERatios.EMPTY);
      revisedAccounts = removeMissingAccounts(encodedAccounts, _rootAccount);
      if (!revisedAccounts.equals(encodedAccounts)) {
        settingTable.put(N12ERatios.DENOMINATOR_REQUIRED_LIST_KEY, revisedAccounts);
      }
      return new RatioEntry(settingTable, _mdGUI, tagMap);
    } catch (StringEncodingException e) {
      Logger.log("Error reading ratio entry settings: " + e.getMessage());
    }
    return null;
  }

  private void addAccountListener() {
    if (_rootAccount != null) {
      _rootAccount.addAccountListener(_accountListener);
    }
  }

  private void removeAccountListener() {
    if (_rootAccount != null) {
      _rootAccount.removeAccountListener(_accountListener);
    }
  }

  private void createSettings() {
    // settings can be written back to the file
    final boolean readOnly = false;
    _settings = new RatioSettings(getGUI(), readOnly);
    _settings.loadFromSettings(_rootAccount, _resources);
    // override the date range from user preferences, which does not require saving the file
    String dateRangeOption = _preferences.getSetting(N12ERatios.DATE_RANGE_PREF_KEY, _settings.getDateRangeOption());
    _settings.setDateRangeOption(dateRangeOption);
  }

  private void loadRatioList() {
    synchronized (_ratioSync) {
      _ratios.clear();
      Map<Integer, String> tagMap = TxnTagUtils.loadLegacyTagMap(_rootAccount);
      for (String setting : _settings.getRatioEntryList()) {
        RatioEntry ratioEntry = getEntryFromSettingString(setting, tagMap);
        if (ratioEntry != null) {
          ratioEntry.setIndex(_ratios.size());
          _ratios.add(ratioEntry);
        }
      }
    }
  }

  private static String removeMissingAccounts(String encodedAccounts, AccountBook data) {
    if (StringUtils.isBlank(encodedAccounts)) return encodedAccounts;
    StringBuilder result = new StringBuilder();
    String[] accountsList = StringUtils.split(encodedAccounts, ',');
    for (String accountId : accountsList) {
      // first look for an individual account by GUID or integer
      try {
        boolean addThisId = false;
        Account account = data.getAccountByUUIDOrLegacyNumber(accountId);
        if (account != null) {
          addThisId = true;
        } else {
          // account types are negative numbers, always include them
          final int accountOrTypeId = Integer.parseInt(accountId);
          addThisId = (accountOrTypeId < 0);
        }
        if (addThisId) {
          if (result.length() > 0) result.append(',');
          result.append(accountId);
        } else {
          Logger.log("Removed missing account ID: " + accountId);
        }
      } catch (NumberFormatException nfex) {
        Logger.log("Invalid account ID selecting accounts: " + accountId);
      }
    } // for accountId
    return result.toString();
  }


  MoneydanceGUI getGUI() {
    return _mdGUI;
  }

  AccountBook getRootAccount() {
    return _rootAccount;
  }

  RatioSettings getSettings() {
    return _settings;
  }

  /**
   * Define a new/updated settings object. This should be on the main UI thread.
   * @param settings The new or updated settings.
   */
  void setSettings(final RatioSettings settings) {
    _settings = settings;
    loadRatioList();
    recalculate();
    eventNotify.firePropertyChange(N12ERatios.SETTINGS_CHANGE, null, settings);
  }


  ///////////////////////////////////////////////////////////////////////////////////////////
  // Ratios
  ///////////////////////////////////////////////////////////////////////////////////////////

  void setDateRangeOption(final String dateRangeOption) {
    final String oldOption = (_settings != null) ? _settings.getDateRangeOption() : "this_year";
    if (_settings != null) {
      _settings.setDateRangeOption(dateRangeOption);
      recalculate();
    }
    //  save in preferences in case the user does not save the file, the system will still remember their choice
    _preferences.setSetting(N12ERatios.DATE_RANGE_PREF_KEY, dateRangeOption);
    eventNotify.firePropertyChange(N12ERatios.DATE_RANGE_OPTION, oldOption, dateRangeOption);
  }

  void setCustomDateRange(final DateRange dateRange) {
    final String oldOption = (_settings != null) ? _settings.getDateRangeOption() : "this_year";
    if (_settings != null) {
      _settings.setCustomDateRange(dateRange);
      recalculate();
    }
    eventNotify.firePropertyChange(N12ERatios.DATE_RANGE_OPTION, oldOption, N12ERatios.CUSTOM_DATE_KEY);
  }

  void recalculate() {
    if (_ratioCompute != null) {
      setCurrentTask(new BackgroundRecalculateTask(), true);
      final Runnable computeTask = getCurrentTask();
      if (computeTask != null) _executor.submit(computeTask);
    }
  }

  int getRatioCount() {
    synchronized (_ratioSync) {
      return _ratios.size();
    }
  }

  RatioEntry getRatioItem(final int index) {
    synchronized (_ratioSync) {
      return _ratios.get(index);
    }
  }

  RatioView getRatioView(final int index) {
    synchronized (_ratioSync) {
      return new RatioView(_ratios.get(index), this);
    }
  }

  int getDecimalPlaces() {
    if (_settings == null) return 1; // default
    return _settings.getDecimalPlaces();
  }

  void cancelCurrentTask() {
    _cancelTasks.set(true);
  }

  private void waitForCurrentTaskToFinish() {
    try {
      while (getCurrentTask() != null) {
        _taskSync.wait(250L);
      }
    } catch (InterruptedException ignore) {
      // do nothing
    }
  }

  private Runnable getCurrentTask() {
    synchronized (_taskSync) {
      return _currentTask;
    }
  }

  private void currentTaskDone() {
    synchronized (_taskSync) {
      _taskSync.notifyAll();
      _currentTask = null;
    }
  }

  private void setCurrentTask(final Runnable task, final boolean cancelCurrentTask) {
    if (cancelCurrentTask) {
      cancelCurrentTask();
    } else {
      waitForCurrentTaskToFinish();
    }
    synchronized (_taskSync) {
      _currentTask = task;
      _cancelTasks.set(false);
    }
  }

  private static void firePropertyChange(final PropertyChangeSupport notifier, final String name,
                                         final Object oldValue, final Object newValue) {
    // notify on the event data thread (Swing thread)
    UiUtil.runOnUIThread(new Runnable() {
      public void run() {
        notifier.firePropertyChange(name, oldValue, newValue);
      }
    });
  }

  private class RatiosAccountListener
      implements AccountListener {
    public void accountModified(Account account) {
      // ignore, the changes could be irrelevant
    }

    public void accountBalanceChanged(Account account) {
      // any change of any balance should be responded to
      recalculate();
    }

    public void accountDeleted(Account account, Account account1) {
      // we need to rebuild our map
      loadRatioList();
      recalculate();
    }

    public void accountAdded(Account account, Account account1) {
      // we need to rebuild our map - user may have included all of an account type that the new account belongs to
      loadRatioList();
      recalculate();
    }
  }

  /**
   * Class to compute the ratios on a background thread, which does two things for us:
   * 1) Prevents long-running tasks on the main UI thread
   * 2) Collects a series of recalculate requests within 1 second into a single request, to
   * prevent needless recalculation.
   */
  private class BackgroundRecalculateTask
      implements Runnable {

    public void run() {
      // name this thread
      Thread.currentThread().setName(N12ERatios.RATIO_THREAD_NAME);
      // first wait 1/2 second to make sure we don't get an avalanche of recalculate commands
      int count = 3;
      while (!_cancelTasks.get() && count > 0) {
        try {
          Thread.sleep(200);
          --count;
        } catch (InterruptedException e) {
          // definitely do not proceed
          _cancelTasks.set(true);
        }
      }
      if (!_cancelTasks.get()) {
        // go ahead with the computation
        try {
          synchronized (_ratioSync) {
            _ratioCompute.computeRatios(_ratios, _settings.getDateRange());
          }
          // notify the UI on the main thread
          firePropertyChange(eventNotify, N12ERatios.RECALCULATE, null, null);
          currentTaskDone();

        } catch (NullPointerException error) {
          Logger.log("Error computing ratios (NPE) - Moneydance is probably shutting down... ignoring....");

        } catch (Throwable error) {
          Logger.log("Error computing ratios: " + error.getMessage());
          error.printStackTrace();
        }
      } else {
        Logger.log("Background recalculate task was canceled.");
      }
    } // run()
  }
}
