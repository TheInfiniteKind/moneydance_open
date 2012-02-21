/*************************************************************************\
 * Copyright (C) 2009-2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 \*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.controller.AccountFilter;
import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.model.SplitTxn;

/**
 * <p>Filters out transactions that are filtered by an account filter and/or category filter. An
 * {@link AccountFilter account filter} is capable of checking if the account is contained in a
 * list of one or more accounts.</p>
 *
 * @author Kevin Menningen
 * @version Build 83
 * @since 1.0
 */
class AccountTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final AccountFilter _accountFilter;
    private final AccountFilter _categoryFilter;

    AccountTxnFilter(final AccountFilter accountFilter, final AccountFilter categoryFilter, final boolean required)
    {
        super(required);
        _accountFilter = accountFilter;
        _categoryFilter = categoryFilter;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        if (txn == null) return false;

        boolean matches = false;
        // parent transactions can be tested only for an account or category
        if (txn instanceof ParentTxn)
        {
            if (_accountFilter != null)
            {
                matches = _accountFilter.filter(txn.getAccount());
            }
            if (_categoryFilter != null)
            {
                if (isRequired())
                {
                    // user is using Intersection glue logic, so this will be true only if they
                    // add the same account to both the account and category filters (include
                    // transfers is on)
                    matches &= _categoryFilter.filter(txn.getAccount());
                }
                else
                {
                    matches |= _categoryFilter.filter(txn.getAccount());
                }
            }
            return matches;
        }

        // split transactions need to check their parents to see if they are in the right
        // account or not
        if (txn instanceof SplitTxn)
        {
            final SplitTxn split = (SplitTxn)txn;
            final ParentTxn parent = split.getParentTxn();
            final Account from = parent.getAccount();
            final Account to = split.getAccount();
            // check both sides of the split
            matches = checkAccounts(from, to);
            if (!matches)
            {
                matches = checkAccounts(to, from);
            }
        }
        return matches;
    }

    private boolean checkAccounts(Account from, Account to)
    {
        if ((_accountFilter == null) && (_categoryFilter == null))
        {
            return true; // always matches
        }
        boolean result = isRequired();
        if (_accountFilter != null)
        {
            result = _accountFilter.filter(from);
        }
        if (_categoryFilter != null)
        {
            if (isRequired())
            {
                result &= _categoryFilter.filter(to);
            }
            else
            {
                result |= _categoryFilter.filter(to);
            }
        }
        return result;
    }
}
