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

import com.infinitekind.moneydance.model.Account;

/**
 * A single item in the table for the account selector list.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class AccountFilterSelectListTableEntry {
  /**
   * The key data, used for both the account filter and the table selection model.
   */
  private FilterSelection _selected;
  /**
   * The account object, can be <code>null</code> if showing an account type instead.
   */
  private final Account _account;
  /**
   * The name of the account for display.
   */
  private final String _name;
  /**
   * If the account is a subaccount, the full name of the account for a tooltip.
   */
  private final String _toolTip;
  /**
   * The account type itself, to help with filtering.
   */
  private final int _accountType;
  /**
   * The account ID, which helps keep the account filter up-to-date.
   */
  private final Integer _accountId;

  AccountFilterSelectListTableEntry(final Account account, final String name, final String fullName,
                                    final int accountId, final int accountType) {
    _account = account;
    if (name.equalsIgnoreCase(fullName)) {
      // no tooltip needed, full name is same as short name
      _name = name;
      _toolTip = null;
    } else {
      final String[] levels = fullName.split(N12ESelector.COLON);
      StringBuilder builder = new StringBuilder();
      int indents = levels.length - 1;
      for (int ii = 0; ii < indents; ii++) {
        builder.append(N12ESelector.INDENT);
      }
      builder.append(name);
      _name = builder.toString();
      _toolTip = fullName;
    }
    _accountId = Integer.valueOf(accountId);
    _accountType = accountType;
  }

  boolean isHeader() {
    return _account == null;
  }

  boolean isRequired() {
    return FilterSelection.REQUIRED.equals(_selected);
  }

  void setRequired() {
    _selected = FilterSelection.REQUIRED;
  }

  boolean isDisallowed() {
    return FilterSelection.DISALLOWED.equals(_selected);
  }

  void setDisallowed() {
    _selected = FilterSelection.DISALLOWED;
  }

  void setAllowed() {
    _selected = FilterSelection.ALLOWED;
  }

  FilterSelection getFilterSelection() {
    return _selected;
  }

  void setFilterSelection(final FilterSelection filter) {
    _selected = filter;
  }

  String getName() {
    return _name;
  }

  /**
   * @return The account associated with the entry, or <code>null</code> if an account type.
   */
  Account getAccount() {
    return _account;
  }

  String getToolTip() {
    return _toolTip;
  }

  Integer getAccountId() {
    return _accountId;
  }

  int getAccountType() {
    return _accountType;
  }
}
