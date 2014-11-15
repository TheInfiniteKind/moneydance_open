/*
 * ************************************************************************
 * Copyright (C) 2012-2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.apps.md.controller.Util;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountUtil;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.CurrencyUtil;
import com.infinitekind.moneydance.model.RootAccount;
import com.infinitekind.moneydance.model.Txn;
import com.infinitekind.moneydance.model.TxnIterator;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Computes ratios efficiently using one pass through the data for each numerator or denominator.
 *
 * @author Kevin Menningen
 */
class RatioCompute {
  private static final double MINIMUM_DENOMINATOR = 0.00001;
  private final RootAccount _root;
  private final char _decimal;
  private final Map<Account,BalanceHolder> _balanceCache;

  public RatioCompute(final RootAccount root, final char decimal) {
    _root = root;
    _decimal = decimal;
    _balanceCache = new HashMap<Account, BalanceHolder>();
  }

  public void computeRatios(final List<RatioEntry> ratios, DateRange dateRange) {
    _balanceCache.clear();
    computeTxnBasedValues(ratios, dateRange);
    computeBalanceBasedValues(ratios, dateRange);
    computeConstantValues(ratios, dateRange);
    computeFinalRatios(ratios);
  }

  static boolean shouldFlipTxn(final Account sourceAccount, final Account targetAccount,
                               final boolean isSourceRequired, final boolean isTargetRequired) {
    // if the source is a category and the target isn't, flip
    final boolean isSourceCategory =
      (sourceAccount.getAccountType() == Account.ACCOUNT_TYPE_EXPENSE)
      || (sourceAccount.getAccountType() == Account.ACCOUNT_TYPE_INCOME);
    final boolean isTargetCategory = (targetAccount.getAccountType() == Account.ACCOUNT_TYPE_EXPENSE)
      || (targetAccount.getAccountType() == Account.ACCOUNT_TYPE_INCOME);
    if (isSourceCategory && !isTargetCategory) return true;
    // if the source is not a Required account but the target is, flip as long as that doesn't
    // violate the first clause where the target is a category.
    return !isSourceRequired && isTargetRequired && !isTargetCategory;
  }

  static int getDaysInPeriod(DateRange dateRange) {
    return Util.calculateDaysBetween(dateRange.getStartDateInt(), dateRange.getEndDateInt()) + 1;
  }

  private void computeBalanceBasedValues(List<RatioEntry> ratios, DateRange dateRange) {
    if (_root == null) {
      System.err.println("ratios: no data file defined for balance calculations");
      return;
    }
    final CurrencyType baseCurrency = _root.getCurrencyTable().getBaseType();
    for (RatioEntry ratio : ratios) {
      computeBalances(ratio, baseCurrency, dateRange);
    }
  }

  private void computeConstantValues(List<RatioEntry> ratios, DateRange dateRange) {
    for (RatioEntry ratio : ratios) {
      if (TxnMatchLogic.CONSTANT.equals(ratio.getNumeratorMatchingLogic())) {
        final double value = RatiosUtil.getConstantValue(ratio.getNumeratorLabel(), _decimal, true, 0.0);
        ratio.setNumeratorValue(value);
        if (value == 0.0) {
          System.err.println("ratios: did not parse numerator constant '" + ratio.getNumeratorLabel() + "' correctly for ratio: " + ratio.getName());
        }
      } else if (TxnMatchLogic.DAYS_IN_PERIOD.equals(ratio.getNumeratorMatchingLogic())) {
        ratio.setNumeratorValue(getDaysInPeriod(dateRange));
      }
      if (TxnMatchLogic.CONSTANT.equals(ratio.getDenominatorMatchingLogic())) {
        final double value = RatiosUtil.getConstantValue(ratio.getDenominatorLabel(), _decimal, false, 1.0);
        ratio.setDenominatorValue(value);
        if (value == 1.0) {
          System.err.println("ratios: did not parse denominator constant '" + ratio.getDenominatorLabel() + "' correctly for ratio: " + ratio.getName());
        }
      } else if (TxnMatchLogic.DAYS_IN_PERIOD.equals(ratio.getDenominatorMatchingLogic())) {
        ratio.setDenominatorValue(getDaysInPeriod(dateRange));
      }
    }
  }

  private void computeBalances(RatioEntry ratio, CurrencyType baseCurrency, DateRange dateRange) {
    if (RatiosUtil.isAccountBalanceType(ratio.getNumeratorMatchingLogic())) {
      boolean useDailyAverage = ratio.getNumeratorAverageBalance();
      boolean useStartBalance = ratio.getNumeratorBeginningBalance();
      long result = computeBalanceResult(dateRange, baseCurrency,
                                         ratio.getNumeratorRequiredAccountList(),
                                         useDailyAverage,
                                         useStartBalance,
                                         null);
      // now calculate the final result
      ratio.setNumeratorValue(baseCurrency.getDoubleValue(result));
    }
    if (RatiosUtil.isAccountBalanceType(ratio.getDenominatorMatchingLogic())) {
      boolean useDailyAverage = ratio.getDenominatorAverageBalance();
      boolean useStartBalance = ratio.getDenominatorBeginningBalance();
      long result = computeBalanceResult(dateRange, baseCurrency,
                                         ratio.getDenominatorRequiredAccountList(),
                                         useDailyAverage,
                                         useStartBalance,
                                         null);
      // now calculate the final result
      ratio.setDenominatorValue(baseCurrency.getDoubleValue(result));
    }
  }

  /**
   * Calculate the end balance of a list of accounts. This method does not allow transaction filtering.
   * Also, it currently computes both the starting and the ending balance, but only uses the end balance
   * at this time. It may be useful in the future to compute a balance difference (again, no transaction
   * filtering).
   * @param dateRange       The date range to compute the balances for.
   * @param baseCurrency    Target currency to convert all values into.
   * @param accountList     The list of accounts to compute balances for.
   * @param useDailyAverage True if a daily average daily balance should be computed. If false, use start or end balance.
   * @param useStartBalance True if a the start balance should be used, false if the end balance should be used.
   * @param reporting       If non-null, the report generator handling object.
   * @return The sum of the end balances for the given date range and account list, converted to base currency.
   */
  long computeBalanceResult(DateRange dateRange, CurrencyType baseCurrency,
                            final List<Account> accountList,
                            boolean useDailyAverage,
                            boolean useStartBalance,
                            IRatioReporting reporting) {
    long startBalance = 0;
    long averageDailyBalance = 0;
    long endBalance = 0;
    // since transactions on the start date are included in this report, and since the account
    // balance computation includes the date (it is as of the end of the day), then we want the
    // start balance at the start of the begin date, so we reduce the start day by one.
    int[] asOfDates = new int[] {
        Util.incrementDate(dateRange.getStartDateInt(), 0, 0, -1),
        dateRange.getEndDateInt()
    };
    final int[] dailyDates;
    if (useDailyAverage) {
      // Compute the daily dates array only once, it won't change.
      // For the daily average balance, we don't want the decremented start date calculated previously,
      // so compute based on the dates the user specified and therefore expects
      // Add one day since we are including both start and end days
      int numDays = getDaysInPeriod(dateRange);
      // fill in a daily range
      dailyDates = new int[numDays];
      int thisDay = dateRange.getStartDateInt();
      for (int index = 0; index < numDays; index++) {
        dailyDates[index] = thisDay;
        thisDay = Util.incrementDate(thisDay);
      }
    } else {
      dailyDates = null;
    }
    for (Account account : accountList) {
      // skip any account that is not active - they are hidden by default
      if (account.getAccountOrParentIsInactive()) continue;
      final BalanceHolder balance = useDailyAverage ?
                                    calculateBalancesWithDailyAverage(account, _balanceCache, asOfDates, dailyDates) :
                                    calculateBalances(account, _balanceCache, asOfDates);
      // convert to the base currency
      final long accountStartBalance = CurrencyUtil.convertValue(balance.getStartBalance(),
                                               account.getCurrencyType(),
                                               baseCurrency,
                                               asOfDates[0]);
      startBalance += accountStartBalance;
      final long accountEndBalance = CurrencyUtil.convertValue(balance.getEndBalance(),
                                               account.getCurrencyType(),
                                               baseCurrency,
                                               asOfDates[1]);
      endBalance += accountEndBalance;
      final long accountAvgBalance = CurrencyUtil.convertValue(balance.getAverageBalance(),
                                                               account.getCurrencyType(),
                                                               baseCurrency,
                                                               asOfDates[1]);
      averageDailyBalance += accountAvgBalance;

      if (reporting != null) reporting.addAccountResult(account, accountStartBalance, accountEndBalance, accountAvgBalance,
                                                        useDailyAverage, asOfDates[0], asOfDates[1]);
    }
    // here you would subtract (endBalance - startBalance) if you wanted balance difference.
    return useDailyAverage ? averageDailyBalance : (useStartBalance ? startBalance : endBalance);
  }

  private BalanceHolder calculateBalances(Account account, Map<Account, BalanceHolder> cache, int[] asOfDates) {
    BalanceHolder result = (cache == null) ? null : cache.get(account);
    if (result == null) {
      // this will get balances in the account's currency type
      long[] balances = AccountUtil.getBalancesAsOfDates(_root, account, asOfDates, true);
      // For investment accounts only, we must include the child accounts, the securities, since security accounts
      // are not included in the filter criteria. Users assume the security accounts are part of the investment
      // account balance. If we don't do this, all we get is the cash balance of the investment account.
      if (account.getAccountType() == Account.ACCOUNT_TYPE_INVESTMENT) {
        for (int index = 0; index < account.getSubAccountCount(); index++) {
          Account security = account.getSubAccount(index);
          long[] securityBalances = AccountUtil.getBalancesAsOfDates(_root, security, asOfDates, true);
          // convert to the account's currency type, later that will be converted to base currency
          balances[0] += CurrencyUtil.convertValue(securityBalances[0],
                                                   security.getCurrencyType(),
                                                   account.getCurrencyType(),
                                                   asOfDates[0]);
          balances[1] += CurrencyUtil.convertValue(securityBalances[1],
                                                   security.getCurrencyType(),
                                                   account.getCurrencyType(),
                                                   asOfDates[1]);
        }
      }
      if (account.balanceIsNegated()) {
        result = new BalanceHolder(account, -balances[0], -balances[1], 0, asOfDates[0], asOfDates[1], false);
      } else {
        result = new BalanceHolder(account, balances[0], balances[1], 0, asOfDates[0], asOfDates[1], false);
      }
      if (cache != null) cache.put(account, result);
    }
    return result;
  }
  
  private BalanceHolder calculateBalancesWithDailyAverage(Account account, Map<Account, BalanceHolder> cache, int[] asOfDates,
                                                          int[] datesToCompute) {
    BalanceHolder result = (cache == null) ? null : cache.get(account);
    if ((result == null) || !result.isAverageBalanceComputed()) {
      final int numDays = datesToCompute.length;
      // this will get balances in the account's currency type
      long[] balances = AccountUtil.getBalancesAsOfDates(_root, account, datesToCompute, true);
      // For investment accounts only, we must include the child accounts, the securities, since security accounts
      // are not included in the filter criteria. Users assume the security accounts are part of the investment
      // account balance. If we don't do this, all we get is the cash balance of the investment account.
      if (account.getAccountType() == Account.ACCOUNT_TYPE_INVESTMENT) {
        for (int index = 0; index < account.getSubAccountCount(); index++) {
          Account security = account.getSubAccount(index);
          long[] securityBalances = AccountUtil.getBalancesAsOfDates(_root, security, datesToCompute, true);
          // convert to the account's currency type, later that will be converted to base currency
          for (int dateIndex = 0; dateIndex < numDays; dateIndex++) {
            balances[dateIndex] += CurrencyUtil.convertValue(securityBalances[dateIndex],
                                                     security.getCurrencyType(),
                                                     account.getCurrencyType(),
                                                     datesToCompute[dateIndex]);
          }
        }
      }
      double average = 0;
      for (int index = 0; index < numDays; index++) average += balances[index];
      long averageDailyBalance = Math.round(average / (double)numDays);
      if (account.balanceIsNegated()) {
        result = new BalanceHolder(account, -balances[0], -balances[numDays-1], averageDailyBalance, asOfDates[0], asOfDates[1], true);
      } else {
        result = new BalanceHolder(account, balances[0], balances[numDays-1], averageDailyBalance, asOfDates[0], asOfDates[1], true);
      }
      if (cache != null) cache.put(account, result);
    }
    return result;
  }

  void computeTransactionResult(final RatioEntry ratio, final DateRange dateRange, boolean isNumerator, final IRatioReporting reporting) {
    ratio.prepareForTxnProcessing(_root, dateRange, isNumerator, reporting);
    // calculate for each ratio on each matching transaction
    TxnIterator txnIterator = new TxnIterator(_root.getTransactionSet());
    while (txnIterator.hasNext()) {
      Txn txn = txnIterator.next();
      ratio.accumulateTxn(txn, isNumerator, reporting);
    }
    // final computation
    ratio.endTxnProcessing(isNumerator, reporting);
  }

  private void computeTxnBasedValues(List<RatioEntry> ratios, DateRange dateRange) {
    if (_root == null) {
      System.err.println("ratios: no data file defined for transaction calculations");
      return;
    }
    if (noTransactionPartsExist(ratios)) return;
    // setup
    for (RatioEntry ratio : ratios) ratio.prepareForTxnProcessing(_root, dateRange, true, null);
    // calculate for each ratio on each matching transaction
    TxnIterator txnIterator = new TxnIterator(_root.getTransactionSet());
    while(txnIterator.hasNext()) {
      Txn txn = txnIterator.next();
      for (RatioEntry ratio : ratios) {
        // with a null reporting callback, it doesn't matter whether we specify numerator or denominator, both will compute
        ratio.accumulateTxn(txn, true, null);
      }
    }
    // final computation
    for (RatioEntry ratio : ratios) ratio.endTxnProcessing(true, null);
  }

  /**
   * Determine if all of the ratios use account balances or constant values, which means it's pointless to run
   * through all the transactions.
   * @param ratios The list of ratio definitions.
   * @return True if all ratios (numerator and denominator) are account-balance-based, false otherwise.
   */
  private boolean noTransactionPartsExist(List<RatioEntry> ratios) {
    for (RatioEntry ratio : ratios) {
      if (!ratio.getNumeratorEndBalanceOnly()
          && !ratio.getNumeratorAverageBalance()
          && !ratio.getNumeratorBeginningBalance()
          && !ratio.getNumeratorConstant()
          && !ratio.getNumeratorDaysInPeriod()) return false;
      if (!ratio.getDenominatorEndBalanceOnly()
          && !ratio.getDenominatorAverageBalance()
          && !ratio.getDenominatorBeginningBalance()
          && !ratio.getDenominatorConstant()
          && !ratio.getDenominatorDaysInPeriod()) return false;
    }
    return true;
  }
  /**
   * Divide the numerator by the denominator on all ratios, checking for oddball numbers.
   * @param ratios The list of ratio definitions.
   */
  private void computeFinalRatios(List<RatioEntry> ratios) {
    for (RatioEntry ratio : ratios) {
      computeFinalRatio(ratio);
    }
  }

  static void computeFinalRatio(RatioEntry ratio) {
    final double numerator = ratio.getNumeratorValue();
    final double denominator = ratio.getDenominatorValue();
    if (Math.abs(denominator) < MINIMUM_DENOMINATOR) {
      // divide by zero
      ratio.setValue(Double.NaN);
    } else if (Double.isNaN(numerator) || Double.isNaN(denominator)) {
      // not defined
      ratio.setValue(Double.NaN);
    } else if (ratio.getAlwaysPositive()) {
      ratio.setValue(Math.abs(numerator / denominator));
    } else {
      ratio.setValue(numerator / denominator);
    }
  }

}
