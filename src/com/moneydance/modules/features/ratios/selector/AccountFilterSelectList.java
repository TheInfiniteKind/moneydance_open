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
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.modules.features.ratios.ResourceProvider;

import javax.swing.JPanel;


/**
 * <p>Control that allows the user to select one or more accounts and shows the selected
 * accounts in a table.</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class AccountFilterSelectList {
  private final AccountFilterSelectListModel _model;
  private final AccountFilterSelectListView _view;
  private final AccountFilterSelectListController _controller;

  public AccountFilterSelectList(ResourceProvider resources, MoneydanceGUI mdGui) {
    _model = new AccountFilterSelectListModel();
    _controller = new AccountFilterSelectListController(resources, _model, mdGui);
    _view = new AccountFilterSelectListView(_controller);

    _model.addPropertyChangeListener(_view);
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Interface IAccountSelector
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * Set the filter that determines which accounts are available for selection and which are not.
   *
   * @param requiredFilter The filter that specifies which accounts are required.
   * @param disallowedFilter The filter that specifies which accounts are disallowed.
   */
  public void setAccountFilters(AccountFilter requiredFilter, AccountFilter disallowedFilter) {
    _model.setRequiredAccountFilter(requiredFilter);
    _model.setDisallowedAccountFilter(disallowedFilter);
    _controller.loadData();
  }

  /**
   * @return The filter that determines which accounts are available for selection.
   */
  public AccountFilter getRequiredAccountFilter() {
    return _model.getRequiredAccountFilter();
  }

  /**
   * @return The filter that determines which accounts cause transactions to be disqualified.
   */
  public AccountFilter getDisallowedAccountFilter() {
    return _model.getDisallowedAccountFilter();
  }



  /**
   * Release any allocated resources, clean up listeners.
   */
  public void cleanUp() {
    _model.removePropertyChangeListener(_view);
    _model.cleanUp();
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Public Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////


  public void layoutComponentUI() {
    _view.layoutViewUI();
  }

  public JPanel getView() {
    return _view;
  }

  /**
   * Control whether to include or exclude child accounts automatically if the parent account
   * is included or excluded, and both parent and child exist in the filter.
   *
   * @param autoSelect True to automatically select or deselect children, false otherwise.
   */
  public void setAutoSelectChildAccounts(final boolean autoSelect) {
    _model.setAutoSelectChildAccounts(autoSelect);
  }

  public void saveControlsToData() {
    _controller.saveData();
  }
}
