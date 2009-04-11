/*
 * AccountFilter.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 6, 2008
 * Time: 5:32:12 AM
 */


package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.Account;

import java.util.Set;
import java.util.HashSet;
import java.util.Collection;

/**
 * Filters accounts by two criteria:
 * <ol>
 * <li>Whether the account is an appropriate type (real account versus category)</li>
 * <li>Whether it was explicitly included or excluded (typically by the user)</li>
 * </ol>
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0 
 */
class AccountFilter
{
    private final Set<Integer> _includedAccounts;
    private int _maxCount;
    private final Set<Integer> _allowedAccountTypes;
    private FullAccountList _fullList;
    private final String _allDisplayKey;

    public AccountFilter(final String allDisplayKey)
    {
        _includedAccounts = new HashSet<Integer>();
        _allowedAccountTypes = new HashSet<Integer>();
        _maxCount = 0;
        _fullList = null;
        _allDisplayKey = allDisplayKey;
    }

    public AccountFilter(final AccountFilter other)
    {
        _includedAccounts = new HashSet<Integer>(other._includedAccounts);
        _allowedAccountTypes = new HashSet<Integer>(other._allowedAccountTypes);
        _fullList = other._fullList;
        _maxCount = other._maxCount;
        _allDisplayKey = other._allDisplayKey;
    }

    public void reset()
    {
        _includedAccounts.clear();
    }

    public void addAllowedType(final int accountType)
    {
        _allowedAccountTypes.add(Integer.valueOf(accountType));
    }

    public boolean include(final Account account)
    {
        if (_allowedAccountTypes.contains(Integer.valueOf(account.getAccountType())))
        {
            _includedAccounts.add( Integer.valueOf( account.getAccountNum() ) );
            return true;
        }
        return false;
    }

    public void includeId(final int accountId)
    {
        _includedAccounts.add(Integer.valueOf(accountId));
    }

    public boolean exclude(final Account account)
    {
        if (_allowedAccountTypes.contains(Integer.valueOf(account.getAccountType())))
        {
            _includedAccounts.remove( Integer.valueOf( account.getAccountNum() ) );
            return true;
        }
        return false;
    }

    public void excludeId(final int accountId)
    {
        _includedAccounts.remove( Integer.valueOf( accountId ) );
    }

    public Collection<Integer> getAllIncluded()
    {
        // defensively copy
        return new HashSet<Integer>(_includedAccounts);
    }

    /**
     * Decide if an account is included in this filter's criterion or not.
     *
     * @param account The account to test.
     * @return True if the account is included, false if it is excluded.
     */
    public boolean filter(final Account account)
    {
        if (_includedAccounts.isEmpty())
        {
            return false;
        }
        return _includedAccounts.contains( Integer.valueOf( account.getAccountNum() ) );
    }
    
    public boolean filterId(final int accountId)
    {
        if (_includedAccounts.isEmpty())
        {
            return false;
        }
        return _includedAccounts.contains( Integer.valueOf( accountId ) );
    }

    public FullAccountList getFullList()
    {
        return _fullList;
    }
    
    public void setFullList(final FullAccountList fullList)
    {
        _fullList = fullList;
        if (_fullList != null)
        {
            _maxCount = _fullList.getCount();
        }
        // by default, the filter allows everything
        reset();
        if (_fullList != null)
        {
            for (final Integer accountID : _fullList.getFullAccountIDs())
            {
                _includedAccounts.add(accountID);
            }
        }
    }

    boolean isAllAccounts()
    {
        return (_includedAccounts.size() == _maxCount);
    }

    public String getDisplayString(final IFindAndReplaceController controller)
    {
        if (isAllAccounts())
        {
            // all possible accounts
            return controller.getString(_allDisplayKey);
        }
        if (_includedAccounts.size() == 0)
        {
            // no accounts
            return controller.getString(L10NFindAndReplace.NONE);
        }

        String displayString = N12EFindAndReplace.EMPTY;
        HashSet<Integer> included = new HashSet<Integer>(_includedAccounts);
        for (final Integer accountType : _allowedAccountTypes)
        {
            Set<Integer> accountIDsofType = _fullList.getAccountsIDsOfType(accountType.intValue());

            // if the list is empty, we won't include that type because there are no accounts of
            // that type -- the type is allowed but no accounts exist
            if (accountIDsofType.size() == 0)
            {
                continue;
            }

            // accounts exist, see if all of the accounts of that type are included
            boolean allOfType = true;
            for (final Integer accountID : accountIDsofType)
            {
                if (!included.contains(accountID))
                {
                    allOfType = false;
                    break;
                }
            }

            if (allOfType)
            {
                StringBuffer buffer = new StringBuffer(displayString);
                if (buffer.length() > 0)
                {
                    buffer.append(N12EFindAndReplace.COMMA_SEPARATOR);
                }
                buffer.append(getAllOfTypeTitle(controller, accountType));
                displayString = buffer.toString();

                // now delete these from the included list
                for (final Integer accountID : accountIDsofType)
                {
                    included.remove(accountID);
                }
            } // if all of a type
        } // for accountType

        // remaining in the included list are all those partial accounts -- does not contain the
        // complete list of a particular type
        StringBuffer result = new StringBuffer(displayString);
        for (final Integer accountID : included)
        {
            if (result.length() > 0)
            {
                result.append(N12EFindAndReplace.COMMA_SEPARATOR);
            }
            result.append(controller.getAccountName(accountID.intValue()));
        }

        return result.toString();
    } // getDisplayString()


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    private String getAllOfTypeTitle(final IResourceProvider resources, final Integer accountType)
    {
        StringBuffer buffer = new StringBuffer(resources.getString(L10NFindAndReplace.ACCOUNTFILTER_ALL));
        buffer.append(N12EFindAndReplace.SPACE);
        buffer.append(AccountSelectModel.getAccountTypeName(resources, accountType.intValue()));
        return buffer.toString();
    }
}
