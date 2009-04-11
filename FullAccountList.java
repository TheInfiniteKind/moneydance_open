/**
 * @author Kevin Menningen
 * Created: Mar 15, 2008 4:43:14 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.Account;

import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Map;
import java.util.HashMap;

/**
 * <p>Holds the full list of possible accounts, given a filter. Could hold all normal accounts,
 * or all categories, or everything.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FullAccountList
{
    private final List<Account> _fullAccountList;
    private final Map<Integer, List<Account>> _typeIndex;

    FullAccountList(final RootAccount root, final AccountFilter filter, final boolean includeSubAccounts)
    {
        _fullAccountList = new ArrayList<Account>();
        _typeIndex = new HashMap<Integer, List<Account>>();
        buildAccountList(root, filter, includeSubAccounts);
    }

    int getCount()
    {
        return _fullAccountList.size();
    }

    Set<Integer> getFullAccountIDs()
    {
        final Set<Integer> result = new HashSet<Integer>();
        for (final Account acct : _fullAccountList)
        {
            result.add(Integer.valueOf(acct.getAccountNum()));
        }
        return result;
    }

    Set<Integer> getAccountsIDsOfType(final int type)
    {
        final Set<Integer> result = new HashSet<Integer>();
        final List<Account> accountsByType = _typeIndex.get(Integer.valueOf(type));
        if (accountsByType != null)
        {
            for (final Account acct : accountsByType)
            {
                result.add(Integer.valueOf(acct.getAccountNum()));
            }
        }
        return result;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    private void buildAccountList(final RootAccount root, final AccountFilter filter,
                                  final boolean includeSubAccounts)
    {
        // this will copy the allowed types list, which is all we need
        final AccountFilter tempFilter = new AccountFilter(filter);
        tempFilter.reset();

        if (root != null)
        {
            final int count = root.getSubAccountCount();
            for (int accountIndex = 0; accountIndex < count; accountIndex++)
            {
                // the filter won't add types not in the allowed type list
                final Account acct = root.getSubAccount(accountIndex);
                if (tempFilter.include(acct))
                {
                    _fullAccountList.add(acct);

                    // index it by type
                    addToTypeIndex(acct);

                    // since the parent account is included, the sub accounts must also be included
                    if (includeSubAccounts)
                    {
                        addSubAccounts(tempFilter, acct);
                    } // if include
                } // if tempFilter.include
            } // for accountIndex
        } // if root
    } // buildAccountList()

    private void addSubAccounts(AccountFilter filter, Account parent)
    {
        final int subCount = parent.getSubAccountCount();
        for (int subAccountIndex = 0; subAccountIndex < subCount; subAccountIndex++)
        {
            final Account subAcct = parent.getSubAccount(subAccountIndex);
            // sub-accounts can be added only if they are a compatible type
            if ((subAcct != null) && (filter.include(subAcct)))
            {
                _fullAccountList.add(subAcct);
                addToTypeIndex(subAcct);
                // recurse
                addSubAccounts(filter, subAcct);
            }
        } // includeSubAccounts
    }

    private void addToTypeIndex(Account acct)
    {
        final Integer accountType = Integer.valueOf(acct.getAccountType());
        List<Account> accountsByType = _typeIndex.get(accountType);
        if (accountsByType == null)
        {
            accountsByType = new ArrayList<Account>();
        }
        accountsByType.add(acct);
        _typeIndex.put(accountType, accountsByType);
    }

}
