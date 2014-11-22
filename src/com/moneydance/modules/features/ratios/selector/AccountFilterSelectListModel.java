/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios.selector;
import com.moneydance.util.*;

import com.moneydance.apps.md.controller.AccountFilter;
//import com.infinitekind.util.BasePropertyChangeReporter;

/**
 * <p>Model for a control that allows the user to select one or more accounts and shows the
 * selected accounts in a table.</p>
 * <p/>
 * <p>There are actually two models in use: the table model for display and user selection, and
 * two account filters which are kept up-to-date for the host object's benefit.</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class AccountFilterSelectListModel
    extends BasePropertyChangeReporter {
  /**
   * The model for the table, containing the items and whether they are selected or not.
   */
  private AccountFilterSelectListTableModel _tableModel;
  /**
   * The account filter which contains all possible accounts to select, and the list of accounts
   * that are selected as required - a transaction cannot match unless the account is in the filter.
   */
  private AccountFilter _requiredFilter;
  /**
   * The account filter which contains all possible accounts to select, and the list of accounts
   * that are selected as disallowed - a transaction cannot match if the account is in the filter.
   */
  private AccountFilter _disallowedFilter;

  /**
   * True to automatically select or deselect children, false otherwise.
   */
  private boolean _autoSelectChildAccounts = false;

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Package Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  void setTableModel(AccountFilterSelectListTableModel model) {
    _tableModel = model;
  }

  AccountFilterSelectListTableModel getTableModel() {
    return _tableModel;
  }

  void setRequiredAccountFilter(AccountFilter accountFilter) {
    _requiredFilter = accountFilter;
    _eventNotify.firePropertyChange(N12ESelector.FILTER_CHANGE, false, true);
  }

  AccountFilter getRequiredAccountFilter() {
    return _requiredFilter;
  }

  void setDisallowedAccountFilter(AccountFilter accountFilter) {
    _disallowedFilter = accountFilter;
    _eventNotify.firePropertyChange(N12ESelector.FILTER_CHANGE, false, true);
  }

  AccountFilter getDisallowedAccountFilter() {
    return _disallowedFilter;
  }

  void cleanUp() {
    _requiredFilter = null;
    _disallowedFilter = null;
    _tableModel.reset();
    _tableModel = null;
  }

  String getTooltip(final int modelIndex) {
    final AccountFilterSelectListTableEntry entry = _tableModel.getEntry(modelIndex);
    if (entry == null) {
      return null;
    }
    return entry.getToolTip();
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Package Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  void setAutoSelectChildAccounts(boolean autoSelectChildAccounts) {
    _autoSelectChildAccounts = autoSelectChildAccounts;
  }

  boolean getAutoSelectChildAccounts() {
    return _autoSelectChildAccounts;
  }
}
