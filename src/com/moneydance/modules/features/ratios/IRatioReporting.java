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
import com.infinitekind.moneydance.model.Txn;

/**
 * Interface to gather reporting data during a ratio calculation.
 *
 * @author Kevin Menningen
 */
public interface IRatioReporting {
  void startReportSection();
  void addAccountResult(Account account, long startBalance, long endBalance, long avgBalance,
                        boolean useAverage, int startDate, int endDate);
  void addTxn(Txn txn, TxnReportInfo info);
  void endReportAccountSection();
  void endReportTxnSection();
}
