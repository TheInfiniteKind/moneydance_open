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

import com.moneydance.apps.md.controller.AccountFilter;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.modules.features.ratios.RatiosUtil;
import com.moneydance.modules.features.ratios.ResourceProvider;

import java.util.List;
import java.util.ArrayList;


/**
 * <p>Controller for a control that allows the user to indicate whether each account is required,
 * allowed, or disallowed and shows the accounts in a table.</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class AccountFilterSelectListController {
  private final ResourceProvider _resources;
  private final AccountFilterSelectListModel _model;
  private final MoneydanceGUI _mdGui;

  AccountFilterSelectListController(final ResourceProvider resources,
                                    final AccountFilterSelectListModel model,
                                    final MoneydanceGUI mdGui) {
    _resources = resources;
    _model = model;
    _mdGui = mdGui;
  }

  ResourceProvider getResourceProvider() {
    return _resources;
  }

  MoneydanceGUI getMDGUI() {
    return _mdGui;
  }

  void setTableModel(AccountFilterSelectListTableModel model) {
    _model.setTableModel(model);
  }

  /**
   * Using the account filter as the source, update the table model to match.
   */
  void loadData() {
    // we need both the account filter and the table model to be defined in order to load
    final AccountFilterSelectListTableModel tableModel = _model.getTableModel();
    final AccountFilter requiredFilter = _model.getRequiredAccountFilter();
    final AccountFilter disallowedFilter = _model.getDisallowedAccountFilter();
    if ((tableModel == null) ||
        (requiredFilter == null) ||
        (disallowedFilter == null)) {
      // nothing to do
      return;
    }

    // the table model will include all available accounts
    tableModel.reset();
    final boolean notify = false; // one notification at the end

    // all other modes show the complete list of accounts
    final List<Account> fullAccountList = requiredFilter.getFullList().getFullAccountList();
    final List<AccountFilterSelectListTableEntry> typeHeaders = new ArrayList<AccountFilterSelectListTableEntry>();
    int currentAccountType = -1;
    for (final Account account : fullAccountList) {
      final int newAccountType = account.getAccountType();
      if (newAccountType != currentAccountType) {
        // add a header row with the account type
        final String typeName = RatiosUtil.getAccountTypeNameAllCaps(_mdGui, newAccountType);
        AccountFilterSelectListTableEntry header = tableModel.add(null,
                                                           typeName,
                                                           typeName,
                                                           -1,
                                                           newAccountType,
                                                           notify);
        typeHeaders.add(header);
        currentAccountType = newAccountType;
      }
      AccountFilterSelectListTableEntry entry = tableModel.add(account,
                                                         account.getAccountName(),
                                                         account.getFullAccountName(),
                                                         account.getAccountNum(), newAccountType, notify);
      if (requiredFilter.filter(account)) {
        entry.setRequired();
      } else if (disallowedFilter.filter(account)) {
        entry.setDisallowed();
      } else {
        entry.setAllowed();
      }
    }
    // now go back through each of the headers and decide if they all have the same required/allowed/disallowed
    // setting, and if so we can define the setting for the header
    updateHeaderFilterSelection(typeHeaders, tableModel);

    // notify of the change - we don't update the selection because the user has not changed
    // anything
    tableModel.fireTableDataChanged();
  } // loadData()

  void saveData() {
    final AccountFilterSelectListTableModel tableModel = _model.getTableModel();
    final AccountFilter requiredFilter = _model.getRequiredAccountFilter();
    final AccountFilter disallowedFilter = _model.getDisallowedAccountFilter();
    if ((tableModel == null) ||
        (requiredFilter == null) ||
        (disallowedFilter == null)) {
      // nothing to do
      return;
    }

    // make the required and disallowed filters match the table model
    requiredFilter.reset();
    disallowedFilter.reset();
    final int count = tableModel.getRowCount();
    for (int rowIndex = 0; rowIndex < count; rowIndex++) {
      final AccountFilterSelectListTableEntry entry = tableModel.getEntry(rowIndex);
      // skip the headers, the child accounts will get collated automatically
      if (entry.isHeader()) continue;
      if (entry.isRequired()) {
        requiredFilter.includeId(entry.getAccountId());
      } else if (entry.isDisallowed()) {
        disallowedFilter.includeId(entry.getAccountId());
      }
    }
  }

  String getTooltip(int modelIndex) {
    return _model.getTooltip(modelIndex);
  }

  public boolean getAutoSelectChildAccounts() {
    return _model.getAutoSelectChildAccounts();
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private void updateHeaderFilterSelection(List<AccountFilterSelectListTableEntry> typeHeaders,
                                           AccountFilterSelectListTableModel tableModel) {
    final int count = tableModel.getRowCount();
    for (AccountFilterSelectListTableEntry header : typeHeaders) {
      FilterSelection filter = null;
      int accountType = header.getAccountType();
      for (int rowIndex = 0; rowIndex < count; rowIndex++) {
        AccountFilterSelectListTableEntry rowEntry = tableModel.getEntry(rowIndex);
        if (rowEntry.getAccountType() != accountType) continue;
        if (rowEntry.getAccount() == null) continue;
        // we now have an account of the correct type
        if (filter == null) {
          filter = rowEntry.getFilterSelection();
        } else {
          if (!filter.equals(rowEntry.getFilterSelection())) {
            // not all the accounts of the specified type have the same filter selection
            filter = null;
            break;
          }
        }
      }
      // We've now gone through all the accounts of the specified type. Null is allowed.
      header.setFilterSelection(filter);
    }
  }

}
