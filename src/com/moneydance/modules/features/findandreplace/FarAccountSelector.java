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

import com.moneydance.apps.md.controller.AccountFilter;
import com.moneydance.apps.md.model.AccountUtil;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.view.gui.reporttool.GraphReportUtil;
import com.moneydance.apps.md.view.gui.select.IAccountSelector;

import java.util.ArrayList;
import java.util.List;

/**
 * A special instance of an account selector that supports IAccountSelector but does
 * not have a UI at all
 */
public class FarAccountSelector
        implements IAccountSelector
{
    private final List<Integer> _selectedAccountIds = new ArrayList<Integer>();
    private final RootAccount _rootAccount;
    private AccountFilter _filter;

    public FarAccountSelector(final RootAccount root, final AccountFilter filter)
    {
        _rootAccount = root;
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

    public List<Integer> getSelectedAccountIds()
    {
        return _selectedAccountIds;
    }

    public int getSelectedCount()
    {
        int count = 0;
        for (Integer value : getSelectedAccountIds())
        {
            if (value.intValue() < 0)
            {
                // account type, find the total number of that type
                count += getAccountTypeCount(-value.intValue());
            }
            else
            {
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

    private int getAccountTypeCount(final int accountType)
    {
        return AccountUtil.getAccountIdsOfType(_rootAccount, accountType).size();
    }

    private void loadSelectedIds()
    {
        // commit user settings to the model in preparation for save.
        _selectedAccountIds.clear();
        // we're capable of collapsing all accounts of a type into the type ID, with a negative
        // number (account IDs are positive).
        _selectedAccountIds.addAll(_filter.getAllIncludedCollapsed());
    }
}
