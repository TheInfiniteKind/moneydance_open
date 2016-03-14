/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.controller.AccountFilter;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.reporttool.GraphReportUtil;
import com.moneydance.apps.md.view.gui.select.IAccountSelector;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * A special instance of an account selector that supports IAccountSelector but does
 * not have a UI at all
 */
public class FarAccountSelector
        implements IAccountSelector
{
    private final List<String> _selectedAccountIds = new ArrayList<String>();
    private final AccountBook _book;
    private AccountFilter _filter;

    public FarAccountSelector(final AccountBook book, final AccountFilter filter)
    {
        _book = book;
        _filter = filter;
    }

    //////////////////////////////////////////////////////////////////////////////
    // IAccountSelector
    //////////////////////////////////////////////////////////////////////////////

    public void setAccountFilter(AccountFilter accountFilter)
    {
        _filter = accountFilter;
        loadSelectedIds();
    }

    public AccountFilter getAccountFilter()
    {
        return _filter;
    }

    public void setSpecialDisplayFilter(AccountFilter accountFilter)
    {
        // not implemented
    }

    public List<String> getSelectedAccountIds()
    {
        return _selectedAccountIds;
    }

    public int getSelectedCount() {
        int count = 0;
        for (String value : getSelectedAccountIds()) {
            if (value.startsWith("-")) {
                // account type, find the total number of that type
                try {
                    int typeCode = -Integer.parseInt(value);
                    count += getAccountTypeCount(Account.AccountType.typeForCode(typeCode));
                } catch (NumberFormatException e) {
                    Logger.log("Failed to get account type: " + value);
                }
            } else {
                ++count;
            }
        }
        return count;
    }

    public void cleanUp()
    {
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
    public AccountFilter selectFromEncodedString(final String encoded)
    {
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

    private int getAccountTypeCount(final Account.AccountType accountType)
    {
        return getAccountIdsOfType(_book, accountType).size();
    }

    private void loadSelectedIds()
    {
        // commit user settings to the model in preparation for save.
        _selectedAccountIds.clear();
        // we're capable of collapsing all accounts of a type into the type ID, with a negative
        // number (account IDs are positive).
        _selectedAccountIds.addAll(_filter.getAllIncludedCollapsed());
    }


  /**
   * Get all account IDs of a particular type.
   * @param book The account book object
   * @param accountType The type of account to get a list for.
   * @return A list of all account IDs of the specified type.
   */
  public static List<Integer> getAccountIdsOfType(AccountBook book, Account.AccountType accountType) {
    List<Integer> result = new ArrayList<Integer>();
    for (Iterator acctIter = AccountUtil.getAccountIterator(book.getRootAccount()); acctIter.hasNext(); )
    {
      final Account account = (Account)acctIter.next();
      if (account.getAccountType() == accountType) {
        result.add(Integer.valueOf(account.getAccountNum()));
      }
    }
    return result;
  }


}
