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

import com.moneydance.apps.md.controller.*;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.reporttool.GraphReportUtil;
import com.moneydance.apps.md.view.gui.select.IAccountSelector;

import java.util.ArrayList;
import java.util.List;

/**
 * A special instance of an account selector that supports IAccountSelector but does
 * not have a UI at all
 */
public class RatioAccountSelector
    implements IAccountSelector {
  private final List<Integer> _selectedAccountIds = new ArrayList<Integer>();
  private final AccountBook _rootAccount;
  private AccountFilter _filter;

  //////////////////////////////////////////////////////////////////////////////
  // Static Methods
  //////////////////////////////////////////////////////////////////////////////

  /**
   * Create a filter based upon the current account selection settings which includes or
   * excludes source accounts.
   *
   * @param book The root account of the file.
   * @return The new account filter containing all accounts now available.
   */
  public static AccountFilter buildAccountFilter(final AccountBook book) {
    // any type is allowed except security accounts or root, since those are special
    final AccountFilter accountFilter = new AccountFilter("all_accounts");
    accountFilter.addAllowedType(Account.AccountType.ASSET);
    accountFilter.addAllowedType(Account.AccountType.BANK);
    accountFilter.addAllowedType(Account.AccountType.CREDIT_CARD);
    accountFilter.addAllowedType(Account.AccountType.INVESTMENT);
    accountFilter.addAllowedType(Account.AccountType.LIABILITY);
    accountFilter.addAllowedType(Account.AccountType.LOAN);
    accountFilter.addAllowedType(Account.AccountType.INCOME);
    accountFilter.addAllowedType(Account.AccountType.EXPENSE);
    FullAccountList fullAccountList = new FullAccountList(book, accountFilter, true);
    
    // this will automatically include all allowed accounts
    accountFilter.setFullList(fullAccountList);
    // so we reset it because we want the default to be no accounts
    accountFilter.reset();

    return accountFilter;
  }

  public RatioAccountSelector(final AccountBook book) {
    _rootAccount = book;
    _filter = buildAccountFilter(book);
  }

  //////////////////////////////////////////////////////////////////////////////
  // IAccountSelector
  //////////////////////////////////////////////////////////////////////////////

  public void setAccountFilter(AccountFilter accountFilter) {
    _filter = accountFilter;
    loadSelectedIds();
  }

  public AccountFilter getAccountFilter() {
    return _filter;
  }

  public void setSpecialDisplayFilter(AccountFilter accountFilter) {
    // not implemented
  }

  public List<Integer> getSelectedAccountIds() {
    return _selectedAccountIds;
  }

  public int getSelectedCount() {
    int count = 0;
    for (Integer value : getSelectedAccountIds()) {
      if (value.intValue() < 0) {
        // account type, find the total number of that type
        count += getAccountTypeCount(Account.AccountType.typeForCode(-value.intValue()));
      } else {
        ++count;
      }
    }
    return count;
  }

  public void cleanUp() {
    _filter = null;
  }

  //////////////////////////////////////////////////////////////////////////////
  // Public Methods
  //////////////////////////////////////////////////////////////////////////////

  /**
   * Select accounts from an encoded string (from settings) and return a new instance
   * of account filter with those accounts selected.
   *
   * @param encoded The encoded string from settings.
   * @return A new account filter with the given accounts selected.
   */
  public AccountFilter selectFromEncodedString(final String encoded) {
    // we reset each time because the GraphReportUtil code assumes a blank string will mean
    // leave the filter as-is, instead of no accounts selected
    _filter.reset();
    GraphReportUtil.selectIndices(encoded, this, true);
    // return a new instance so subsequent calls won't affect it
    return new AccountFilter(_filter);
  }

  //////////////////////////////////////////////////////////////////////////////
  // Private Methods
  //////////////////////////////////////////////////////////////////////////////

  private int getAccountTypeCount(final Account.AccountType accountType) {
    return AccountUtil.allMatchesForSearch(_rootAccount.getRootAccount(), AccountUtil.getFilterForType(accountType)).size();
  }
  
  private void loadSelectedIds() {
    // commit user settings to the model in preparation for save.
    _selectedAccountIds.clear();
    // we're capable of collapsing all accounts of a type into the type ID, with a negative
    // number (account IDs are positive).
    _selectedAccountIds.addAll(_filter.getAllIncludedCollapsed());
  }
}
