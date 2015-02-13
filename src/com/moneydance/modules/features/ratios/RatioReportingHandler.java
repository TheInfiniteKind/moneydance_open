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
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.Txn;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.view.gui.reporttool.RecordRow;
import com.moneydance.apps.md.view.gui.reporttool.Report;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Class to handle callbacks during the ratio computation so that a report can be generated as to exactly
 * how the extension calculated the ratio.
 *
 * @author Kevin Menningen
 */
class RatioReportingHandler
    implements IRatioReporting {
  /**
   * The report generator. It is generating a report for a single ratio definition.
   */
  private final RatioReportGenerator _reportGenerator;
  /**
   * The report being generated.
   */
  private final Report _report;
  /**
   * True if the user wants to see full account paths, false to show only the account name itself.
   */
  private final boolean _showFullAccountName;
  /**
   * The base currency of the file, all calculations are converted to this.
   */
  private final CurrencyType _baseCurrency;
  /**
   * Column widths, which serve as weightings for the report system.
   */
  private final int[] _widths;
  /**
   * A cache of account balances so if the same account is in both numerator and denominator, we don't re-compute.
   */
  private final Map<Account, BalanceHolder> _accountCache = new HashMap<Account, BalanceHolder>();
  /**
   * A cache of transactions so we can sort them prior to putting them on the report.
   */
  private final Map<Txn, TxnReportInfo> _txnCache = new HashMap<Txn, TxnReportInfo>();

  public RatioReportingHandler(RatioReportGenerator ratioReportGenerator,
                               final Report report, final boolean showFullAccountName,
                               final CurrencyType baseCurrency, final int[] widths) {
    _reportGenerator = ratioReportGenerator;
    _report = report;
    _showFullAccountName = showFullAccountName;
    _baseCurrency = baseCurrency;
    _widths = widths;
  }

  public void startReportSection() {
    _accountCache.clear();
    _txnCache.clear();
  }

  public void addAccountResult(Account account, long startBalance, long endBalance, long averageBalance, 
                               boolean useAverage, int startDate, int endDate) {
    _accountCache.put(account, new BalanceHolder(account, startBalance, endBalance, averageBalance, startDate, endDate, useAverage));
  }

  public void endReportAccountSection() {
    List<Account> sortedAccounts = new ArrayList<Account>(_accountCache.keySet());
    Collections.sort(sortedAccounts, RatiosUtil.getAccountComparator());
    Account.AccountType accountType = null;
    long typeTotal = 0;
    final int rowsAtStart = _report.getRowCount();
    boolean isAverageBalance = false;
    int endingDate = Util.getStrippedDateInt();
    for (Account account : sortedAccounts) {
      // skip any account that is not active - they are hidden by default
      if (account.getAccountOrParentIsInactive()) continue;
      final BalanceHolder result = _accountCache.get(account);
      RecordRow row = _reportGenerator.createAccountReportRow(result, _showFullAccountName,
                                                              _baseCurrency, _widths);
      // these won't change from account to account
      isAverageBalance = result.isAverageBalanceComputed();
      endingDate = result.getEndDate();
      if (row != null) {
        if (account.getAccountType() != accountType) {
          // close up shop on the previous type, skipping -1 and 0 (root account type)
          if (accountType != null) _reportGenerator.addAccountTypeSubtotalRow(_report, accountType, _baseCurrency, typeTotal,
                                                                          isAverageBalance, endingDate);
          typeTotal = 0;
          // change to the new type
          accountType = account.getAccountType();
          // add a header
          _reportGenerator.addAccountTypeRow(_report, accountType, isAverageBalance, true);
        }
        _report.addRow(row);
        typeTotal += isAverageBalance ? result.getAverageBalance() : result.getEndBalance();
      }
    }
    // wrap up last account type if needed
    if ((_report.getRowCount() != rowsAtStart) && (accountType != null)) {
      _reportGenerator.addAccountTypeSubtotalRow(_report, accountType, _baseCurrency, typeTotal,
                                                 isAverageBalance, endingDate);
    }
  }

  public void addTxn(Txn txn, TxnReportInfo info) {
    _txnCache.put(txn, info);
  }

  public void endReportTxnSection() {
    List<Txn> sortedTxns = new ArrayList<Txn>(_txnCache.keySet());
    final Comparator<Txn> comparator = RatiosUtil.getTransactionComparator(_reportGenerator.getUseTaxDate());
    Collections.sort(sortedTxns, comparator);
    // put in headers for each account type
    Account.AccountType accountType = null;
    long typeTotal = 0;
    final int rowsAtStart = _report.getRowCount();
    for (Txn txn : sortedTxns) {
      final TxnReportInfo info = _txnCache.get(txn);
      RecordRow row = _reportGenerator.createTxnReportRow(txn, info, _showFullAccountName,
                                                          _baseCurrency, _widths);
      if (row != null) {
        if (txn.getAccount().getAccountType() != accountType) {
          // close up shop on the previous type, skipping -1 and 0 (root account type)
          if (accountType != null) _reportGenerator.addAccountTypeSubtotalRow(_report, accountType, _baseCurrency, typeTotal,
                                                                          true, 0);
          typeTotal = 0;
          // change to the new type
          accountType = txn.getAccount().getAccountType();
          // add a header
          _reportGenerator.addAccountTypeRow(_report, accountType, false, false);
        }
        _report.addRow(row);
        typeTotal += info.convertedValue;
      }
    }
    // wrap up last account type if needed
    if ((_report.getRowCount() != rowsAtStart) && (accountType != null)) {
      _reportGenerator.addAccountTypeSubtotalRow(_report, accountType, _baseCurrency, typeTotal, true, 0);
    }
  }
}
