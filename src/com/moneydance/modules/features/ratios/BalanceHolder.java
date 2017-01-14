/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.infinitekind.moneydance.model.Account;

/**
 * Immutable class to hold an account and the balance calculation results.
 *
 * @author Kevin Menningen
 */
class BalanceHolder {
  private final Account _account;
  private final long _startBalance;
  private final long _endBalance;
  private final long _averageDailyBalance;
  private final int _startDate;
  private final int _endDate;
  private final boolean _dailyAverageComputed;
  private final boolean _useStartBalance;

  BalanceHolder(Account account, long startBalance, long endBalance, long averageDailyBalance,
                int startDate, int endDate, boolean dailyAverageComputed, boolean useStartBalance) {
    _account = account;
    _startBalance = startBalance;
    _endBalance = endBalance;
    _averageDailyBalance = averageDailyBalance;
    _startDate = startDate;
    _endDate = endDate;
    _dailyAverageComputed = dailyAverageComputed;
    _useStartBalance = useStartBalance;
  }

  Account getAccount() { return _account; }
  long getStartBalance() { return _startBalance; }
  long getEndBalance() { return _endBalance; }
  long getAverageBalance() { return _averageDailyBalance; }
  int getStartDate() { return _startDate; }
  int getEndDate() { return _endDate; }
  boolean isAverageBalanceComputed() { return _dailyAverageComputed; }
  boolean isStartBalanceUsed() { return _useStartBalance; }
}
