package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.RootAccount;

import javax.swing.AbstractListModel;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;
import java.util.TreeMap;
import java.util.Set;
import java.util.HashSet;
import java.util.HashMap;
import java.util.Comparator;

/**
 * <p>Stores a list of accounts (could also be categories) for a list control.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
@SuppressWarnings({"BooleanMethodIsAlwaysInverted"})
class AccountListModel extends AbstractListModel
{
    /** First String is the account type name, second is list of accounts of that type. */
    private final Map<String, List<Account>> _accounts;
    /** Index of displayed index to the underlying account. Types will not be in this map. */
    private final Map<Integer, Account> _displayIndex;
    /** The user sees both the types and the account names. */
    private final List<String> _displayText;
    /** The set of display text indices that contain the account types, not names. */
    private final Set<Integer> _typeIndices;

    private boolean _needsRebuild;
    private final AccountSelectModel _accountSelectModel;

    AccountListModel(final AccountSelectModel model)
    {
        super();
        _accountSelectModel = model;
        // use the tree map to get a defined ordering
        _accounts = new TreeMap<String, List<Account>>();
        _displayIndex = new HashMap<Integer, Account>();
        _displayText = new ArrayList<String>();
        _typeIndices = new HashSet<Integer>();
    }


    ///////////////////////////////////////////////////////////////////////////////////////////
    // Package Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////

    void clear(final boolean notify)
    {
        _accounts.clear();
        _needsRebuild = true;
        if (notify)
        {
            fireContentsChanged(this, 0, 0);
        }
    }

    void add(final Account account, final boolean notify)
    {
        final int index = getSize();
        final String accountType = _accountSelectModel.getAccountTypeName(account.getAccountType());
        List<Account> accountList = _accounts.get(accountType);
        if (accountList == null)
        {
            accountList = new ArrayList<Account>();
        }
        if (!isAccountInList(accountList, account))
        {
            accountList.add(account);
        }
        _needsRebuild = true;
        _accounts.put(accountType, accountList);
        if (notify)
        {
            rebuildDisplayText();
            fireIntervalAdded(this, index, index);
        }
    } // add()

    void sort()
    {
        for (final List<Account> accountsByType : _accounts.values())
        {
            if (accountsByType.size() > 0)
            {
                Account[] values = accountsByType.toArray(new Account[accountsByType.size()]);
                Arrays.sort(values, new AccountSorterByName());
                accountsByType.clear();
                accountsByType.addAll(Arrays.asList(values));
            } // if list is not empty
        }

        if (_needsRebuild)
        {
            rebuildDisplayText();
        }
    }

    boolean isAccountTypeHeader(final int index)
    {
        return _typeIndices.contains(Integer.valueOf(index));
    }

    void notifyListeners()
    {
        final int lastIndex = getSize() - 1;
        fireContentsChanged(this, 0, lastIndex);
    }


    ///////////////////////////////////////////////////////////////////////////////////////////
    // Interface ListModel
    ///////////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns the length of the list.
     *
     * @return the length of the list
     */
    public int getSize()
    {
        return _displayText.size();
    }

    /**
     * Returns the value at the specified index.
     *
     * @param index the requested index
     * @return the value at <code>index</code>
     */
    public Object getElementAt(final int index)
    {
        return _displayText.get(index);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void rebuildDisplayText()
    {
        _displayText.clear();
        _displayIndex.clear();
        _typeIndices.clear();
        for (final String accountType : _accounts.keySet())
        {
            int index = _displayText.size();
            _displayText.add(accountType);
            _typeIndices.add(Integer.valueOf(index));

            final List<Account> accountsByType = _accounts.get(accountType);
            for (final Account account : accountsByType)
            {
                StringBuffer buffer = new StringBuffer();
                buffer.append(N12EFindAndReplace.INDENT);
                buffer.append(getAccountDisplayText(account));

                index = _displayText.size();
                _displayText.add(buffer.toString());
                _displayIndex.put(Integer.valueOf(index), account);
            }
        }
        _needsRebuild = false;
    }

    private static String getAccountDisplayText(Account account)
    {
        // if the parent account isn't the root account, then it's a sub-account
        List<String> names = new ArrayList<String>();
        names.add(account.getAccountName());
        Account parent = account.getParentAccount();
        while (!(parent instanceof RootAccount))
        {
            // push name to start of list
            names.add(0, parent.getAccountName());
            parent = parent.getParentAccount();
        }

        // the list of names is now in the right order, with the topmost parent at the start
        StringBuffer buffer = new StringBuffer();
        for (final String name : names)
        {
            if (buffer.length() > 0)
            {
                buffer.append(N12EFindAndReplace.COLON);
            }
            buffer.append(name);
        }

        return buffer.toString();
    }

    private boolean isAccountInList(List<Account> accountList, Account account)
    {
        for (final Account existingAcct : accountList)
        {
            if (existingAcct.equals(account))
            {
                return true;
            }
        }
        return false;
    }

    public Account getByDisplayIndex(int index)
    {
        return _displayIndex.get(Integer.valueOf(index));
    }
    
    public List<Account> getAllByTypeIndex(int index)
    {
        // there are no spaces added to the display list for the types, so we can look it up
        final String accountType = _displayText.get(index);
        return _accounts.get(accountType);
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Inner Classes
    //////////////////////////////////////////////////////////////////////////////////////////////

    private class AccountSorterByName implements Comparator<Account>
    {
        /**
         * {@inheritDoc}
         *
         * @param lhs the first object to be compared.
         * @param rhs the second object to be compared.
         * @return a negative integer, zero, or a positive integer as the
         *         first argument is less than, equal to, or greater than the
         *         second.
         * @throws ClassCastException if the arguments' types prevent them from
         *                            being compared by this comparator.
         */
        public int compare(final Account lhs, final Account rhs)
        {
            if ((lhs == null) && (rhs == null))
            {
                return 0;
            }
            if (lhs == null)
            {
                // rhs != null
                return -1;
            }
            if (rhs == null)
            {
                // lhs != null
                return 1;
            }

            final String lhsName = getAccountDisplayText(lhs);
            final String rhsName = getAccountDisplayText(rhs);
            if ((lhsName == null) && (rhsName == null))
            {
                return 0;
            }
            if (lhsName == null)
            {
                // rhs != null
                return -1;
            }
            if (rhsName == null)
            {
                // lhs != null
                return 1;
            }

            return lhsName.compareTo(rhsName);
        }
    }
}
