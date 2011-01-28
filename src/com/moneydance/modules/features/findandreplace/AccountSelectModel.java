/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.RootAccount;

import javax.swing.ListModel;
import java.util.List;
import java.util.ArrayList;

/**
 * <p>The model for the account/category selection dialog.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class AccountSelectModel extends BasePropertyChangeReporter
{
    private final RootAccount _data;
    private final IResourceProvider _resources;
    private final AccountFilter _actualFilter;
    private final AccountFilter _editingFilter;
    private final FullAccountList _fullAccountList;

    private final AccountListModel _candidateList;
    private final AccountListModel _includedList;

    AccountSelectModel(RootAccount data, AccountFilter filter, final IResourceProvider resources)
    {
        _data = data;
        _resources = resources;
        _actualFilter = filter;
        _editingFilter = new AccountFilter(_actualFilter);
        _fullAccountList = filter.getFullList();

        // UI list models for display
        _candidateList = new AccountListModel(this);
        _includedList = new AccountListModel(this);
    }

    void apply()
    {
        _actualFilter.reset();
        for (final Integer accountID : _editingFilter.getAllIncluded())
        {
            _actualFilter.includeId(accountID.intValue());
        }
    }

    void refresh() throws Exception
    {
        // rebuild the lists
        _candidateList.clear(false);
        _includedList.clear(false);

        for (final Integer accountID : _fullAccountList.getFullAccountIDs())
        {
            if (_editingFilter.filterId(accountID.intValue()))
            {
                // already included
                final Account account = _data.getAccountById(accountID.intValue());
                if (account != null)
                {
                    _includedList.add(account, false);
                }
                else
                {
                    throw new LocalizedException(L10NFindAndReplace.ERROR_ACCOUNTNOTFOUND,
                            _resources);
                }
            }
            else
            {
                // not already included
                final Account account = _data.getAccountById(accountID.intValue());
                if (account != null)
                {
                    _candidateList.add(account, false);
                }
                else
                {
                    throw new LocalizedException(L10NFindAndReplace.ERROR_ACCOUNTNOTFOUND,
                            _resources);
                }
            }
        }

        _candidateList.sort();
        _includedList.sort();

        _candidateList.notifyListeners();
        _includedList.notifyListeners();

        // generic update to get the view to refresh
        notifyAllListeners();
    }


    void moveToIncluded(final int[] indices) throws Exception
    {
        final List<Account> accountList = getIncludedAccountList(_candidateList, indices);
        add(accountList);
        refresh();
    }

    void moveToExcluded(final int[] indices) throws Exception
    {
        final List<Account> accountList = getIncludedAccountList(_includedList, indices);
        remove(accountList);
        refresh();
    }

    void includeExcept(final int[] indices) throws Exception
    {
        final List<Account> accountList = getExcludedAccountList(_candidateList, indices);
        add(accountList);
        refresh();
    }

    void excludeExcept(final int[] indices) throws Exception
    {
        final List<Account> accountList = getExcludedAccountList(_includedList, indices);
        remove(accountList);
        refresh();
    }

    void includeAll() throws Exception
    {
        _editingFilter.reset();
        for (final Integer accountID : _fullAccountList.getFullAccountIDs())
        {
            _editingFilter.includeId(accountID.intValue());
        }
        refresh();
    }

    void excludeAll() throws Exception
    {
        _editingFilter.reset();
        refresh();
    }

    ListModel getCandidateList()
    {
        return _candidateList;
    }

    ListModel getIncludedList()
    {
        return _includedList;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Static Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    static String getAccountTypeName(final IResourceProvider resources, final int type)
    {
        switch (type)
        {
            case Account.ACCOUNT_TYPE_ASSET:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_ASSET);
            }
            case Account.ACCOUNT_TYPE_BANK:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_BANK);
            }
            case Account.ACCOUNT_TYPE_CREDIT_CARD:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_CCARD);
            }
            case Account.ACCOUNT_TYPE_EXPENSE:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_EXPENSE);
            }
            case Account.ACCOUNT_TYPE_INCOME:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_INCOME);
            }
            case Account.ACCOUNT_TYPE_INVESTMENT:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_INVEST);
            }
            case Account.ACCOUNT_TYPE_LIABILITY:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_LIABILITY);
            }
            case Account.ACCOUNT_TYPE_LOAN:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_LOAN);
            }
            case Account.ACCOUNT_TYPE_SECURITY:
            {
                return resources.getString(L10NFindAndReplace.ACCOUNTTYPE_SECURITY);
            }
        }

        return N12EFindAndReplace.EMPTY;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    private List<Account> getIncludedAccountList(AccountListModel listModel, int[] indices)
    {
        List<Account> result = new ArrayList<Account>();
        for (final int index : indices)
        {
            if (listModel.isAccountTypeHeader(index))
            {
                // all accounts of a type
                result.addAll(listModel.getAllByTypeIndex(index));
            }
            else
            {
                // single account or sub-account
                final Account account = listModel.getByDisplayIndex(index);
                if (account != null)
                {
                    result.add(account);
                }
            }
        } // for index
        return result;
    }

    private List<Account> getExcludedAccountList(AccountListModel listModel, int[] indices)
    {
        // if the account is selected, then it is excluded
        List<Account> excluded = getIncludedAccountList(listModel, indices);
        List<Account> result = new ArrayList<Account>();

        // only actual accounts will be added to the excluded list, so we'll only pay attention
        // to the actual accounts
        final int count = listModel.getSize();
        for (int index = 0; index < count; index++)
        {
            if (!listModel.isAccountTypeHeader(index))
            {
                // single account or sub-account
                final Account account = listModel.getByDisplayIndex(index);
                if ((account != null) && !excluded.contains(account))
                {
                    result.add(account);
                }
            }
        }
        return result;
    }

    /**
     * Given a list of accounts, add them to the list of accounts to include in the filter.
     * @param accountList The list of accounts to include.
     */
    private void add(final List<Account> accountList)
    {
        for (final Account account : accountList)
        {
            if (account != null)
            {
                _editingFilter.include(account);
            }
        } // for index
    } // add()


    private void remove(final List<Account> accountList)
    {
        for (final Account account : accountList)
        {
            if (account != null)
            {
                _editingFilter.exclude(account);
            }
        } // for index
    } // remove()

    String getAccountTypeName(final int type)
    {
        return getAccountTypeName(_resources, type);
    }



    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Inner Classes
    ///////////////////////////////////////////////////////////////////////////////////////////////

}
