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
import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.apps.md.controller.time.DateRangeOption;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.infinitekind.util.StreamTable;
import com.infinitekind.util.StringEncodingException;
import com.infinitekind.util.StringUtils;
import com.moneydance.util.BasePropertyChangeReporter;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.TreeMap;

/**
 * Retrieves and stores the persistent settings for the ratio definitions.
 *
 * @author Kevin Menningen
 */
public class RatioSettings
    extends BasePropertyChangeReporter {
  /**
   * The date range to apply for the ratios. Global to all MD files.
   */
  private DateRangeOption _dateRangeType;
  /**
   * The date range to apply for the calculations. Global to all MD files.
   */
  private DateRange _displayInterval;
  /**
   * How many digit places past the decimal point to show for the ratio results.
   */
  private int _decimalPlaces;

  /**
   * List of ratio definitions. Per MD file. The key is the ordering index to show the ratio in the correct order
   * on the home page, the value is the definition settings string which can be fed into a {@link RatioEntry} instance.
   */
  private final Map<Integer, String> _ratioList = new TreeMap<Integer, String>();

  /**
   * Not a setting, just a cache of available date range keys.
   */
  private final List<String> _dateRangeKeys = new ArrayList<String>();
  /**
   * Flag for a temporary user-defined custom date.
   */
  private boolean _customDate = false;
  /**
   * True to send notifications on property changes, false to not notify.
   */
  private boolean _fireNotifications = true;

  private final MoneydanceGUI _mdGui;
  private final char _decimalChar;
  /**
   * True if settings are read only, false if the settings can be written back to preferences.
   */
  private final boolean _readOnly;

  public RatioSettings(final MoneydanceGUI mdGui, final boolean readOnly) {
    _mdGui = mdGui;
    if (mdGui != null) {
      _decimalChar = _mdGui.getPreferences().getDecimalChar();
    } else {
      _decimalChar = '.';
    }
    _readOnly = readOnly;
    loadChoiceList();
    setDefaults();
  }

  public RatioSettings(final RatioSettings other) {
    _mdGui = other._mdGui;
    _decimalChar = other._decimalChar;
    _readOnly = other._readOnly;
    other.copyTo(this);
    loadChoiceList();
  }

  public final void copyTo(final RatioSettings target) {
    target.setDateRangeOption(getDateRangeOption());
    target.setDecimalPlaces(_decimalPlaces);

    // do a deep copy including the order in which the user set the categories
    target.setRatioList(_ratioList);
  }


  int getDecimalPlaces() {
    return _decimalPlaces;
  }

  public void setDecimalPlaces(final int decimalPlaces) {
    final int old = _decimalPlaces;
    _decimalPlaces = decimalPlaces;

    if (_fireNotifications) {
      _eventNotify.firePropertyChange(N12ERatios.DECIMALS_CHANGE, old, decimalPlaces);
    }
  }

  DateRange getDateRange() {
    if (_displayInterval == null) buildDateRangeFromOption();
    return _displayInterval;
  }

  String getDateRangeOption() {
    return _dateRangeType.getResourceKey();
  }

  boolean getIsCustomDate() {
    return _customDate;
  }

  /**
   * Change the date range to apply to the ratio calculation. This is the only property that is global
   * to all Moneydance files. RatiosExtensionModel will fire the property change notification.
   *
   * @param dateRangeOption The new date range option.
   */
  void setDateRangeOption(final String dateRangeOption) {
    _dateRangeType = DateRangeOption.fromKey(dateRangeOption);
    // get the date range itself
    buildDateRangeFromOption();
  }

  /**
   * Change the date range to apply to the ratio calculation. This is not saved in preferences.
   * RatiosExtensionModel will fire the property change notification.
   *
   * @param dateRange The new date range.
   */
  void setCustomDateRange(final DateRange dateRange) {
    _displayInterval = dateRange;
    _customDate = true;
  }


  public List<String> getRatioEntryList() {
    return new ArrayList<String>(_ratioList.values());
  }

  void setRatioEntryList(final List<String> newEntryList) {
    // the new list is now in the correct order, renumber
    _ratioList.clear();
    int orderIndex = 0;
    for (String ratioEntrySetting : newEntryList) {
      _ratioList.put(Integer.valueOf(orderIndex), ratioEntrySetting);
      ++orderIndex;
    }

    // the notification we'll fire is just generic, no need to keep track of the old value
    ratioListUpdated();
  }

  void setRatioList(final Map<Integer, String> newRatioList) {
    // the notification we'll fire is just generic, no need to keep track of the old value
    _ratioList.clear();
    _ratioList.putAll(newRatioList);
    ratioListUpdated();
  }

  void ratioListUpdated() {
    if (_fireNotifications) {
      _eventNotify.firePropertyChange(N12ERatios.RATIO_LIST_CHANGE, null, null);
    }
  }

  void ratioListReset() {
    if (_fireNotifications) {
      _eventNotify.firePropertyChange(N12ERatios.RATIO_LIST_RESET, null, null);
    }
  }

  public void loadFromSettings(final AccountBook root, final ResourceProvider resources) {
    // if the file never contained a ratios setting, build from what we have
    if (!root.getRootAccount().doesParameterExist(N12ERatios.SETTINGS_ID)) {
      buildInitialSettings(root, resources, true);
      return;
    }

    String settings = root.getRootAccount().getParameter(N12ERatios.SETTINGS_ID);
    if (StringUtils.isBlank(settings)) {
      setDefaults();
      return;
    }

    try {
      final StreamTable stream = new StreamTable();
      stream.readFrom(settings);
      // load global settings
      _decimalPlaces = stream.getInt(N12ERatios.DECIMALS_KEY, 1);
      _dateRangeType = DateRangeOption.fromKey(stream.getStr(N12ERatios.DATE_RANGE_KEY,
                                                             DateRangeOption.DEFAULT.getResourceKey()));
      // load the list of settings for the various ratio entries
      String[] ratioEntryList = stream.getStrList(N12ERatios.RATIO_ENTRIES_KEY);
      _ratioList.clear();
      int backupIndex = 0; // in case not previously saved with ordering
      for (final String ratioEntrySetting : ratioEntryList) {
        // a colon-separated pair, index|Settings String
        String[] keyPair = ratioEntrySetting.split(N12ERatios.BAR_REGEX);
        if (keyPair.length == 1) {
          _ratioList.put(Integer.valueOf(backupIndex), keyPair[0]);
        } else if (keyPair.length == 2) {
          _ratioList.put(Integer.valueOf(keyPair[0]), keyPair[1]);
        }
        ++backupIndex;
      }
    } catch (StringEncodingException e) {
      Logger.log(N12ERatios.ERROR_LOADING_SETTINGS);
      setDefaults();
    }
    buildDateRangeFromOption();
  }

  public void saveToSettings(final AccountBook root) {
    if (_readOnly) {
      // do nothing
      return;
    }

    StreamTable stream = new StreamTable();
    // save global settings
    stream.put(N12ERatios.DECIMALS_KEY, _decimalPlaces);
    stream.put(N12ERatios.DATE_RANGE_KEY, _dateRangeType.getResourceKey());
    // save list of ratio entry settings
    String[] ratioEntryList = new String[_ratioList.size()];
    int index = 0; // separate index stays fault-tolerant if list gets messed up
    for (final Integer orderIndex : _ratioList.keySet()) {
      final String ratioEntrySetting = _ratioList.get(orderIndex);
      ratioEntryList[index] = orderIndex.toString() + N12ERatios.BAR + ratioEntrySetting;
      ++index;
    }
    stream.setField(N12ERatios.RATIO_ENTRIES_KEY, ratioEntryList);
    String settings = stream.writeToString();
    root.getRootAccount().setParameter(N12ERatios.SETTINGS_ID, settings);
  }

  public List<String> getDateRangeChoiceKeys() {
    return _dateRangeKeys;
  }

  void suspendNotifications(boolean suspend) {
    _fireNotifications = !suspend;
  }

  public void resetToDefaults(final AccountBook root, final ResourceProvider resources) {
    _ratioList.clear();
    buildInitialSettings(root, resources, false);
    ratioListUpdated();
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * Setup the ratios for the very first time. Add a debt-to-income ratio and a working capital
   * ratio. Finally save the initial settings
   *
   * @param root The account file to load.
   * @param resources Object to obtain localized strings and other resources.
   * @param save True to immediately save the initial settings to the file
   */
  private void buildInitialSettings(final AccountBook root, final ResourceProvider resources, final boolean save) {
    setDefaults();
    Logger.log("Adding example ratio entries");
    addDebtServiceToIncomeRatio(resources);
    addDebtToIncomeRatio(resources);
    addSavingsToIncomeRatio(resources);
    addSavingsRate(resources);
    addDebtToAssetRatio(resources);
    saveToSettings(root);
  }

  /**
   * Add a debt-service-to-income ratio entry as an example. This is a transaction-based ratio covered by the
   * date range. Find the debt service (all transactions going toward loans or liabilities) over
   * gross income (all income categories).
   * @param resources Object to obtain localized strings and other resources.
   */
  private void addDebtServiceToIncomeRatio(final ResourceProvider resources) {
    final RatioEntry ratioEntry = new RatioEntry();
    final int index = _ratioList.size();
    // name
    ratioEntry.setName(resources.getString(L10NRatios.DEBT_SERVICE_TO_INCOME_NAME));
    // index
    ratioEntry.setIndex(index);
    // notes
    final StringBuilder sb = new StringBuilder(resources.getString(L10NRatios.EXAMPLE_NOTES_1));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_2));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_3));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.DEBT_SERVICE_TO_INCOME_NOTES));
    ratioEntry.setNotes(sb.toString());
    // show as percent - yes, looking for less than 40% of gross income
    ratioEntry.setShowPercent(true);
    // always positive - yes, the sign doesn't really matter as debt service is always payments
    ratioEntry.setAlwaysPositive(true);
    // use tax date
    ratioEntry.setUseTaxDate(false);
    // numerator - we want debt payments (cash flowing into) only
    ratioEntry.setNumeratorTxnMatchInto();
    // numerator - label
    ratioEntry.setNumeratorLabel(resources.getString(L10NRatios.DEBT_SERVICE_NAME));
    // numerator - accounts - loans, liabilities and credit cards
    // negative account type means select all accounts of that type
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.LOAN.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.LIABILITY.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.CREDIT_CARD.code()));
    ratioEntry.setNumeratorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setNumeratorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // numerator - tags and tag logic
    ratioEntry.setNumeratorTags(null);
    // denominator - we want gross income, or the stuff coming into the income categories
    ratioEntry.setDenominatorTxnMatchInto();
    // denominator - label
    ratioEntry.setDenominatorLabel(resources.getString(L10NRatios.INCOME_NAME));
    // denominator - accounts - income
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.INCOME.code()));
    ratioEntry.setDenominatorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setDenominatorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // denominator - tags and tag logic
    ratioEntry.setDenominatorTags(null);
    _ratioList.put(Integer.valueOf(index), ratioEntry.getSettingsString());
  }

  /**
   * Add a debt-to-income ratio entry as an example. This is a balance-based ratio covered by the
   * date range. Find the total debt outstanding over gross income (all income categories).
   * @param resources Object to obtain localized strings and other resources.
   */
  private void addDebtToIncomeRatio(final ResourceProvider resources) {
    final RatioEntry ratioEntry = new RatioEntry();
    final int index = _ratioList.size();
    // name
    ratioEntry.setName(resources.getString(L10NRatios.DEBT_TO_INCOME_NAME));
    // index
    ratioEntry.setIndex(index);
    // notes
    final StringBuilder sb = new StringBuilder(resources.getString(L10NRatios.EXAMPLE_NOTES_1));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_2));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_3));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.DEBT_TO_INCOME_NOTES));
    ratioEntry.setNotes(sb.toString());
    // show percent - no, just show a numerical ratio
    ratioEntry.setShowPercent(false);
    // always positive - yes, the sign doesn't really matter as debt service is always payments
    ratioEntry.setAlwaysPositive(true);
    // use tax date
    ratioEntry.setUseTaxDate(false);
    // numerator - we want total debt outstanding so just account balances
    ratioEntry.setNumeratorEndBalanceOnly();
    // numerator - label
    ratioEntry.setNumeratorLabel(resources.getString(L10NRatios.TOTAL_DEBT_NAME));
    // numerator - accounts - loans, liabilities and credit cards
    // negative account type means select all accounts of that type
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.LOAN.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.LIABILITY.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.CREDIT_CARD.code()));
    ratioEntry.setNumeratorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setNumeratorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // numerator - tags and tag logic
    ratioEntry.setNumeratorTags(null);
    // denominator - we want gross income, or the stuff coming into the income categories
    ratioEntry.setDenominatorTxnMatchInto();
    // denominator - label
    ratioEntry.setDenominatorLabel(resources.getString(L10NRatios.INCOME_NAME));
    // denominator - accounts - income
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.INCOME.code()));
    ratioEntry.setDenominatorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setDenominatorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // denominator - tags and tag logic
    ratioEntry.setDenominatorTags(null);
    _ratioList.put(Integer.valueOf(index), ratioEntry.getSettingsString());
  }

  /**
   * Add a savings-to-income ratio entry as an example. This is a balance-based ratio covered by the
   * date range. Find the total savings and investments over gross income (all income categories).
   * @param resources Object to obtain localized strings and other resources.
   */
  private void addSavingsToIncomeRatio(final ResourceProvider resources) {
    final RatioEntry ratioEntry = new RatioEntry();
    final int index = _ratioList.size();
    // name
    ratioEntry.setName(resources.getString(L10NRatios.SAVINGS_TO_INCOME_NAME));
    // index
    ratioEntry.setIndex(index);
    // notes
    final StringBuilder sb = new StringBuilder(resources.getString(L10NRatios.EXAMPLE_NOTES_1));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_2));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_3));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.SAVINGS_TO_INCOME_NOTES));
    ratioEntry.setNotes(sb.toString());
    // show percent - no, just show a numerical ratio
    ratioEntry.setShowPercent(false);
    // always positive - yes, the sign doesn't really matter as debt service is always payments
    ratioEntry.setAlwaysPositive(true);
    // use tax date
    ratioEntry.setUseTaxDate(false);
    // numerator - we want total debt outstanding so just account balances
    ratioEntry.setNumeratorEndBalanceOnly();
    // numerator - label
    ratioEntry.setNumeratorLabel(resources.getString(L10NRatios.TOTAL_SAVINGS_NAME));
    // numerator - accounts - bank and investment accounts, but not assets as we don't include
    // non-liquid assets like a house or boat
    // negative account type means select all accounts of that type
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.BANK.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.INVESTMENT.code()));
    ratioEntry.setNumeratorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setNumeratorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // numerator - tags and tag logic
    ratioEntry.setNumeratorTags(null);
    // denominator - we want gross income, or the stuff coming into the income categories
    ratioEntry.setDenominatorTxnMatchInto();
    // denominator - label
    ratioEntry.setDenominatorLabel(resources.getString(L10NRatios.INCOME_NAME));
    // denominator - accounts - income
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.INCOME.code()));
    ratioEntry.setDenominatorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setDenominatorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // denominator - tags and tag logic
    ratioEntry.setDenominatorTags(null);
    _ratioList.put(Integer.valueOf(index), ratioEntry.getSettingsString());
  }

  /**
   * Add a savings rate entry as an example. This is a transaction-based ratio covered by the
   * date range. Find the net inflow into bank and investment accounts over gross income.
   * @param resources Object to obtain localized strings and other resources.
   */
  private void addSavingsRate(final ResourceProvider resources) {
    final RatioEntry ratioEntry = new RatioEntry();
    final int index = _ratioList.size();
    // name
    ratioEntry.setName(resources.getString(L10NRatios.SAVINGS_RATE_NAME));
    // index
    ratioEntry.setIndex(index);
    // notes
    final StringBuilder sb = new StringBuilder(resources.getString(L10NRatios.EXAMPLE_NOTES_1));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_2));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_3));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.SAVINGS_RATE_NOTES));
    ratioEntry.setNotes(sb.toString());
    // show percent - yes, we're looking for about 12% of income saved
    ratioEntry.setShowPercent(true);
    // always positive - no, savings rate can be negative if balances went down
    ratioEntry.setAlwaysPositive(false);
    // use tax date
    ratioEntry.setUseTaxDate(false);
    // numerator - we want contributions less deductions (balance difference)
    ratioEntry.setNumeratorTxnMatchBoth();
    // numerator - label
    ratioEntry.setNumeratorLabel(resources.getString(L10NRatios.SAVINGS_NAME));
    // numerator - accounts - Bank accounts only - low risk
    ratioEntry.setNumeratorEncodedRequiredAccounts(Integer.toString(-Account.AccountType.BANK.code()));
    ratioEntry.setNumeratorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // numerator - tags and tag logic
    ratioEntry.setNumeratorTags(null);
    // denominator - we want gross income, or the stuff coming into the income categories
    ratioEntry.setDenominatorTxnMatchInto();
    // denominator - label
    ratioEntry.setDenominatorLabel(resources.getString(L10NRatios.INCOME_NAME));
    // denominator - accounts - income
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.INCOME.code()));
    ratioEntry.setDenominatorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setDenominatorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // denominator - tags and tag logic
    ratioEntry.setDenominatorTags(null);
    _ratioList.put(Integer.valueOf(index), ratioEntry.getSettingsString());
  }

  /**
   * Add a debt to asset ratio as an example. This is an account-balance-based ratio defined at the end date of the
   * selected date range. This ratio is all liability balances divided by all asset balances.
   * @param resources Object to obtain localized strings and other resources.
   */
  private void addDebtToAssetRatio(final ResourceProvider resources) {
    final RatioEntry ratioEntry = new RatioEntry();
    final int index = _ratioList.size();
    // name
    ratioEntry.setName(resources.getString(L10NRatios.DEBT_TO_ASSETS_NAME));
    // index
    ratioEntry.setIndex(index);
    // notes
    final StringBuilder sb = new StringBuilder(resources.getString(L10NRatios.EXAMPLE_NOTES_1));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_2));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.EXAMPLE_NOTES_3));
    sb.append(N12ERatios.NEWLINE);
    sb.append(resources.getString(L10NRatios.DEBT_TO_ASSETS_NOTES));
    ratioEntry.setNotes(sb.toString());
    // show percent - no, just show a numerical ratio
    ratioEntry.setShowPercent(false);
    // always positive - yes, the sign doesn't really matter as debt service is always payments
    ratioEntry.setAlwaysPositive(true);
    // use tax date
    ratioEntry.setUseTaxDate(false);
    // numerator - we want total debt outstanding so just account balances
    ratioEntry.setNumeratorEndBalanceOnly();
    // numerator - label
    ratioEntry.setNumeratorLabel(resources.getString(L10NRatios.TOTAL_DEBT_NAME));
    // numerator - accounts - loans, liabilities and credit cards
    // negative account type means select all accounts of that type
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.LOAN.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.LIABILITY.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.CREDIT_CARD.code()));
    ratioEntry.setNumeratorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setNumeratorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // numerator - tags and tag logic
    ratioEntry.setNumeratorTags(null);
    // denominator - we want total assets as account balances
    ratioEntry.setDenominatorEndBalanceOnly();
    // denominator - label
    ratioEntry.setDenominatorLabel(resources.getString(L10NRatios.TOTAL_ASSETS_NAME));
    // denominator - accounts - assets
    sb.setLength(0);
    sb.append(Integer.toString(-Account.AccountType.BANK.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.INVESTMENT.code()));
    sb.append(',');
    sb.append(Integer.toString(-Account.AccountType.ASSET.code()));
    ratioEntry.setDenominatorEncodedRequiredAccounts(sb.toString());
    ratioEntry.setDenominatorEncodedDisallowedAccounts(N12ERatios.EMPTY);
    // denominator - tags and tag logic
    ratioEntry.setDenominatorTags(null);
    _ratioList.put(Integer.valueOf(index), ratioEntry.getSettingsString());
  }


  private void loadChoiceList() {
    _dateRangeKeys.clear();
    // restrict the list to everything except All Dates and Custom Dates
    List<DateRangeOption> options = new ArrayList<DateRangeOption>();
    for (DateRangeOption candidate : DateRangeOption.values()) {
      if (!DateRangeOption.DR_ALL_DATES.equals(candidate) &&
          !DateRangeOption.DR_CUSTOM_DATE.equals(candidate)) {
        options.add(candidate);
      }
    }
    // sort for display
    Collections.sort(options, new Comparator<DateRangeOption>() {
      public int compare(DateRangeOption o1, DateRangeOption o2) {
        return o1.getSortKey() - o2.getSortKey();
      }
    });
    // save the string keys
    for (DateRangeOption dateRange : options) _dateRangeKeys.add(dateRange.getResourceKey());
  }

  private void buildDateRangeFromOption() {
    // this will not work for custom date ranges
    _customDate = false;
    _displayInterval = _dateRangeType.getDateRange();
  }


  private void setDefaults() {
    _dateRangeType = DateRangeOption.DEFAULT;
    buildDateRangeFromOption();
    _decimalPlaces = 1;
    _ratioList.clear();
  }

}

