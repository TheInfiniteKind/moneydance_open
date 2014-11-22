/*************************************************************************\
* Copyright (C) 2009-2013 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.*;
import com.moneydance.util.*;
import com.moneydance.apps.md.controller.*;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.view.gui.TagLogic;

import java.util.Collection;
import java.awt.datatransfer.StringSelection;
import java.awt.Toolkit;
import java.util.regex.Pattern;
import java.util.*;

/**
 * <p>Model for the Find and Replace plugin. Stores all the settings you see in the dialog, and
 * fires property changes when selected values change.</p>
 * 
 * @author Kevin Menningen
 * @version Build 94
 * @since 1.0
 */
class FarModel extends BasePropertyChangeReporter
{
    private AccountBook _data;
    private FindResultsTableModel _findResultsModel;
    private boolean _allowEvents = true;
    
    private boolean _combineOr;
    private final AccountFilter _accountFilter;
    private FullAccountList _fullAccountList;
    private boolean _useAccountFilter;

    private AccountFilter _categoryFilter;
    private FullAccountList _fullCategoryList;
    private boolean _useCategoryFilter;

    private boolean _useAmountFilter;
    private long _amountMinimum;
    private long _amountMaximum;
    private CurrencyType _findAmountCurrency;
    private boolean _isSharesCurrency;

    private boolean _useDateFilter;
    private int _dateMinimum;
    private int _dateMaximum;
    private boolean _useTaxDate;

    private boolean _useFreeTextFilter;
    private boolean _freeTextSearchDescription;
    private boolean _freeTextSearchMemo;
    private boolean _freeTextSearchCheck;
    private boolean _freeTextIncludeSplits;
    private String _freeTextMatch;

    private TagPickerModel _includeTagPickerModel;
    private TagPickerModel _excludeTagPickerModel;
    private boolean _useTagsFilter;
    private TagLogic _combineTagsLogic;
    
    private boolean _useClearedFilter;
    private boolean _allowCleared;
    private boolean _allowReconciling;
    private boolean _allowUncleared;
    
    private boolean _replaceDirty = false;

    private boolean _doReplaceCategory;
    private Account _replacementCategory;

    private boolean _doReplaceAmount;
    private long _replacementAmount;
    private CurrencyType _replaceAmountCurrency;

    private boolean _doReplaceDescription;
    private String _replacementDescription;
    private boolean _replaceFoundDescriptionOnly;

    private boolean _doReplaceMemo;
    private String _replacementMemo;
    private boolean _replaceFoundMemoOnly;

    private boolean _doReplaceCheck;
    private String _replacementCheck;
    private boolean _replaceFoundCheckOnly;

    private boolean _doReplaceTags;
    private ReplaceTagCommandType _replaceTagCommand;
    private TagPickerModel _replaceAddTagPickerModel;
    private TagPickerModel _replaceRemoveTagPickerModel;
    private TagPickerModel _replaceReplaceTagPickerModel;

    private boolean _includeTransfers;
    private boolean _showParents;
    private boolean _splitDescriptionAsMemo;

    FarModel()
    {
        _accountFilter = new AccountFilter(L10NFindAndReplace.ACCOUNTFILTER_ALL_ACCOUNTS);
        // all types except categories and securities (which act like categories for investments)
        _accountFilter.addAllowedType(Account.AccountType.ASSET);
        _accountFilter.addAllowedType(Account.AccountType.BANK);
        _accountFilter.addAllowedType(Account.AccountType.CREDIT_CARD);
        _accountFilter.addAllowedType(Account.AccountType.INVESTMENT);
        _accountFilter.addAllowedType(Account.AccountType.LIABILITY);
        _accountFilter.addAllowedType(Account.AccountType.LOAN);

        setupCategoryFilter();

        setDefaults();
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Package Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    void setResultsModel(final FindResultsTableModel resultsModel)
    {
        _findResultsModel = resultsModel;
    }

    void setData( final AccountBook data )
    {
        _data = data;
        if (_data == null)
        {
            // nothing more to do
            cleanUp();
            return;
        }

        // store the default/base currency
        _findAmountCurrency = _data.getCurrencies().getBaseType();
        _replaceAmountCurrency = _data.getCurrencies().getBaseType();

        // create the full account list - we don't count sub-accounts for these, which generally
        // are securities within investment accounts
        _fullAccountList = new FullAccountList(_data, _accountFilter, true);
        _accountFilter.setFullList(_fullAccountList);

        // create the full category list, including sub-categories
        loadCategoryFilter();
        
        // to display user-defined tags, we have to have the list
        List<String> allTxnTags = TxnUtil.getListOfAllUsedTransactionTags(_data.getTransactionSet().getAllTxns());
        _findResultsModel.setUserTagSet(allTxnTags);

        // and the pickers need the same
        _includeTagPickerModel = new TagPickerModel(allTxnTags);
        _includeTagPickerModel.selectAll();  // all are selected by default
        _excludeTagPickerModel = new TagPickerModel(allTxnTags);
        _replaceAddTagPickerModel = new TagPickerModel(allTxnTags);
        _replaceRemoveTagPickerModel = new TagPickerModel(allTxnTags);
        _replaceReplaceTagPickerModel = new TagPickerModel(allTxnTags);
    }

    AccountBook getData()
    {
        return _data;
    }
    
    void setAllowEvents(final boolean allow)
    {
        boolean old = _allowEvents;
        _allowEvents = allow;
        if (!old && allow)
        {
            // fire a change event
            notifyAllListeners();
        }
    }

    boolean getAllowEvents()
    {
        return _allowEvents;
    }

    FindResultsTableModel getFindResults()
    {
        return _findResultsModel;
    }

    void accountListUpdated()
    {
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.ACCOUNT_SELECT, null, null);
        setUseAccountFilter(true);
    }

    void categoryListUpdated()
    {
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.CATEGORY_SELECT, null, null);
        setUseCategoryFilter(true);
    }

    void tableUpdated()
    {
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FIND_RESULTS_UPDATE, null, null);
    }

    void setDefaults()
    {
        // set defaults
        _combineOr = false;
        _useAccountFilter = false;

        _useCategoryFilter = false;

        _useAmountFilter = false;
        _amountMinimum = 0;
        _amountMaximum = 0;
        if (_data != null)
        {
            _findAmountCurrency = _data.getCurrencies().getBaseType();
            _replaceAmountCurrency = _data.getCurrencies().getBaseType();
        }
        else
        {
            _findAmountCurrency = null;
            _replaceAmountCurrency = null;
        }

        _useDateFilter = false;
        _dateMinimum = Util.getStrippedDateInt();
        _dateMaximum = _dateMinimum;

        _useFreeTextFilter = false;
        _freeTextSearchDescription = true;
        _freeTextSearchMemo = true;
        _freeTextSearchCheck = true;
        _freeTextIncludeSplits = true;
        _freeTextMatch = N12EFindAndReplace.EMPTY;

        _useTagsFilter = false;
        _combineTagsLogic = TagLogic.OR;

        _useClearedFilter = false;
        _allowCleared = true;
        _allowReconciling = true;
        _allowUncleared = true;

        _replaceDirty = false;

        _doReplaceCategory = false;
        _replacementCategory = null;

        _doReplaceAmount = false;
        _replacementAmount = 0;

        _doReplaceDescription = false;
        _replacementDescription = N12EFindAndReplace.EMPTY;
        _replaceFoundDescriptionOnly = false;

        _doReplaceMemo = false;
        _replacementMemo = N12EFindAndReplace.EMPTY;
        _replaceFoundMemoOnly = false;

        _doReplaceCheck = false;
        _replacementCheck = N12EFindAndReplace.EMPTY;
        _replaceFoundCheckOnly = false;

        _doReplaceTags = false;
        _replaceTagCommand = null;

        setIncludeTransfers(false);
        setShowParents(false);
        setSplitsAsMemos(false);

        if (_data != null)
        {
            setData(_data);
        }

    }

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Properties
    //////////////////////////////////////////////////////////////////////////////////////////////

    void setFilterCombineOr(final boolean combineOr)
    {
        final boolean oldValue = _combineOr;
        _combineOr = combineOr;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FIND_COMBINATION, oldValue, _combineOr);
    }
    
    boolean getFilterCombineOr()
    {
        return _combineOr;
    }

    AccountFilter getAccountFilter()
    {
        return _accountFilter;
    }

    void setUseAccountFilter(final boolean use)
    {
        boolean old = _useAccountFilter;
        _useAccountFilter = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.ACCOUNT_USE, old, use);
    }
    boolean getUseAccountFilter()
    {
        return _useAccountFilter;
    }

    AccountFilter getCategoryFilter()
    {
        return _categoryFilter;
    }

    void setUseCategoryFilter(final boolean use)
    {
        boolean old = _useCategoryFilter;
        _useCategoryFilter = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.CATEGORY_USE, old, use);
    }
    boolean getUseCategoryFilter()
    {
        return _useCategoryFilter;
    }

    void setUseAmountFilter(final boolean use)
    {
        boolean old = _useAmountFilter;
        _useAmountFilter = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.AMOUNT_USE, old, use);
    }
    boolean getUseAmountFilter()
    {
        return _useAmountFilter;
    }

    void setAmountRange(final long minimum, final long maximum)
    {
        _amountMinimum = minimum;
        _amountMaximum = maximum;
    }
    long getAmountMinimum()
    {
        return _amountMinimum;
    }
    long getAmountMaximum()
    {
        return _amountMaximum;
    }

    /**
     * Define what currency the user is specifying for the search on amount.
     * @param newCurrency      The currency to use for searching for amount.
     * @param isSharesCurrency True if the currency is a generic "number of shares" currency, so
     * search on the number of shares of a security, or False if it is a standard currency.
     */
    void setFindAmountCurrency(final CurrencyType newCurrency, final boolean isSharesCurrency)
    {
        final CurrencyType old = _findAmountCurrency;
        _findAmountCurrency = newCurrency;
        _isSharesCurrency = isSharesCurrency;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FIND_AMOUNT_CURRENCY, old, newCurrency);
    }
    CurrencyType getFindAmountCurrency()
    {
        return _findAmountCurrency;
    }

    /**
     * Define what currency the user is specifying for the replace amount.
     * @param newCurrency      The currency to use for replacing an amount.
     */
    void setReplaceAmountCurrency(final CurrencyType newCurrency)
    {
        final CurrencyType old = _replaceAmountCurrency;
        _replaceAmountCurrency = newCurrency;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPL_AMOUNT_CURRENCY, old, newCurrency);
    }
    CurrencyType getReplaceAmountCurrency()
    {
        return _replaceAmountCurrency;
    }

    void setUseDateFilter(final boolean use)
    {
        boolean old = _useDateFilter;
        _useDateFilter = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.DATE_USE, old, use);
    }
    boolean getUseDateFilter()
    {
        return _useDateFilter;
    }
    void setDateRange(final int minimum, final int maximum, boolean useTaxDate)
    {
        _dateMinimum = minimum;
        _dateMaximum = maximum;
        _useTaxDate = useTaxDate;
    }
    int getDateMinimum()
    {
        return _dateMinimum;
    }
    int getDateMaximum()
    {
        return _dateMaximum;
    }
    boolean getUseTaxDate()
    {
        return _useTaxDate;
    }

    void setUseFreeTextFilter(final boolean use)
    {
        boolean old = _useFreeTextFilter;
        _useFreeTextFilter = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_USE, old, use);
    }
    boolean getUseFreeTextFilter()
    {
        return _useFreeTextFilter;
    }
    void setFreeTextMatch(final String textOrRegEx)
    {
        _freeTextMatch = textOrRegEx;
    }
    String getFreeTextMatch()
    {
        return _freeTextMatch;
    }

    void setFreeTextUseDescription(final boolean use)
    {
        final boolean old = _freeTextSearchDescription;
        _freeTextSearchDescription = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_DESCRIPTION, old, use);
    }
    boolean getFreeTextUseDescription()
    {
        return _freeTextSearchDescription;
    }
    void setFreeTextUseMemo(final boolean use)
    {
        final boolean old = _freeTextSearchMemo;
        _freeTextSearchMemo = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_MEMO, old, use);
    }
    boolean getFreeTextUseMemo()
    {
        return _freeTextSearchMemo;
    }
    void setFreeTextUseCheck(final boolean use)
    {
        final boolean old = _freeTextSearchCheck;
        _freeTextSearchCheck = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_CHECK, old, use);
    }
    boolean getFreeTextUseCheck()
    {
        return _freeTextSearchCheck;
    }
    void setFreeTextIncludeSplits(final boolean include)
    {
        final boolean old = _freeTextIncludeSplits;
        _freeTextIncludeSplits = include;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_SPLITS, old, include);
    }
    boolean getFreeTextIncludeSplits()
    {
        return _freeTextIncludeSplits;
    }

    void setUseTagsFilter(final boolean use)
    {
        boolean old = _useTagsFilter;
        _useTagsFilter = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.TAGS_USE, old, use);
    }
    boolean getUseTagsFilter()
    {
        return _useTagsFilter;
    }
    void setRequireTagsFilter(final TagLogic combine)
    {
        final TagLogic old = _combineTagsLogic;
        _combineTagsLogic = combine;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.TAGS_LOGIC, old, combine);
    }
    TagLogic getRequireTagsFilter()
    {
        return _combineTagsLogic;
    }

    TagPickerModel getIncludedTagsModel()
    {
        return _includeTagPickerModel;
    }
    TagPickerModel getExcludedTagsModel()
    {
        return _excludeTagPickerModel;
    }
    
    void setUseClearedFilter(final boolean use)
    {
        boolean old = _useClearedFilter;
        _useClearedFilter = use;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_USE, old, use);
    }
    boolean getUseClearedFilter()
    {
        return _useClearedFilter;
    }
    boolean getAllowCleared()
    {
        return _allowCleared;
    }
    void setAllowCleared(final boolean allow)
    {
        final boolean old = _allowCleared;
        _allowCleared = allow;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_CLEARED, old, allow);
    }
    boolean getAllowReconciling()
    {
        return _allowReconciling;
    }
    void setAllowReconciling(final boolean allow)
    {
        final boolean old = _allowReconciling;
        _allowReconciling = allow;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_RECONCILING, old, allow);
    }
    boolean getAllowUncleared()
    {
        return _allowUncleared;
    }
    void setAllowUncleared(final boolean allow)
    {
        final boolean old = _allowUncleared;
        _allowUncleared = allow;
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_UNCLEARED, old, allow);
    }

    FilterGroup buildTransactionFilter()
    {
        final FilterGroup result = new FilterGroup();
        AccountFilter accountFilter = null;
        if (_useAccountFilter && !_accountFilter.isAllAccounts())
        {
            accountFilter = _accountFilter;
        }
        AccountFilter categoryFilter = null;
        if (_useCategoryFilter && !_categoryFilter.isAllAccounts())
        {
            categoryFilter = _categoryFilter;
        }
        if (_useAccountFilter || _useCategoryFilter)
        {
            result.addFilter(new AccountTxnFilter(accountFilter, categoryFilter, !_combineOr));
        }
        if (_useDateFilter)
        {
            result.addFilter(new DateRangeTxnFilter(_dateMinimum, _dateMaximum, _useTaxDate,
                    !_combineOr));
        }
        if (_useAmountFilter)
        {
            result.addFilter(new AmountTxnFilter(_amountMinimum, _amountMaximum, _findAmountCurrency,
                                                 _isSharesCurrency, !_combineOr));
        }
        if (_useFreeTextFilter)
        {
            result.addFilter(new FreeTextTxnFilter(_freeTextMatch, _freeTextSearchDescription,
                    _freeTextSearchMemo, _freeTextSearchCheck,
                    _freeTextIncludeSplits, !_combineOr));
        }
        if (_useTagsFilter)
        {
            // the tags filter has it's own logic combination, plus it is combined with other criteria
            result.addFilter(new TagsTxnFilter(_includeTagPickerModel.getSelectedTags(),
                    _excludeTagPickerModel.getSelectedTags(), _combineTagsLogic, !_combineOr));
        }
        if (_useClearedFilter)
        {
            result.addFilter(new ClearedTxnFilter(_allowCleared, _allowReconciling, _allowUncleared,
                    !_combineOr));
        }

        return result;
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Replace Support
    ///////////////////////////////////////////////////////////////////////////////////////////////

    boolean isReplaceDirty()
    {
        return _replaceDirty;
    }

    void setReplaceCategory(boolean replace)
    {
        final boolean old = _doReplaceCategory;
        if (old != replace)
        {
            _doReplaceCategory = replace;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_CATEGORY, old, replace);
    }
    boolean getReplaceCategory()
    {
        return _doReplaceCategory;
    }
    void setReplacementCategory(final Account category)
    {
        if ( ((_replacementCategory == null) && (category != null)) ||
             ((_replacementCategory != null) && !_replacementCategory.equals(category)) )
        {
            _replacementCategory = category;
            _replaceDirty = true;
        }
    }
    Account getReplacementCategory()
    {
        return _replacementCategory;
    }

    void setReplaceAmount(boolean replace)
    {
        final boolean old = _doReplaceAmount;
        if (old != replace)
        {
            _doReplaceAmount = replace;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_AMOUNT, old, replace);
    }
    boolean getReplaceAmount()
    {
        return _doReplaceAmount;
    }
    void setReplacementAmount(final long amount)
    {
        if (_replacementAmount != amount)
        {
            _replacementAmount = amount;
            _replaceDirty = true;
        }
    }
    long getReplacementAmount()
    {
        return _replacementAmount;
    }

    void setReplaceDescription(boolean replace)
    {
        final boolean old = _doReplaceDescription;
        if (old != replace)
        {
            _doReplaceDescription = replace;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_DESCRIPTION, old, replace);
    }
    boolean getReplaceDescription()
    {
        return _doReplaceDescription;
    }
    void setReplaceFoundDescriptionOnly(boolean foundTextOnly)
    {
        final boolean old = _replaceFoundDescriptionOnly;
        if (old != foundTextOnly)
        {
            _replaceFoundDescriptionOnly = foundTextOnly;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_FOUND_DESCRIPTION_ONLY, old,
                                        foundTextOnly);
    }
    boolean getReplaceFoundDescriptionOnly()
    {
        return _replaceFoundDescriptionOnly;
    }
    void setReplacementDescription(final String description)
    {
        if ( ((_replacementDescription == null) && (description != null)) ||
             ((_replacementDescription != null) && !_replacementDescription.equals(description)) )
        {
            _replacementDescription = description;
            _replaceDirty = true;
        }
    }
    String getReplacementDescription()
    {
        return _replacementDescription;
    }

    void setReplaceMemo(boolean replace)
    {
        final boolean old = _doReplaceMemo;
        if (old != replace)
        {
            _doReplaceMemo = replace;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_MEMO, old, replace);
    }
    boolean getReplaceMemo()
    {
        return _doReplaceMemo;
    }
    void setReplaceFoundMemoOnly(boolean foundTextOnly)
    {
        final boolean old = _replaceFoundMemoOnly;
        if (old != foundTextOnly)
        {
            _replaceFoundMemoOnly = foundTextOnly;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_FOUND_MEMO_ONLY, old,
                                        foundTextOnly);
    }
    boolean getReplaceFoundMemoOnly()
    {
        return _replaceFoundMemoOnly;
    }
    void setReplacementMemo(final String memo)
    {
        if ( ((_replacementMemo == null) && (memo != null)) ||
             ((_replacementMemo != null) && !_replacementMemo.equals(memo)) )
        {
            _replacementMemo = memo;
            _replaceDirty = true;
        }
    }
    String getReplacementMemo()
    {
        return _replacementMemo;
    }

    void setReplaceCheck(boolean replace)
    {
        final boolean old = _doReplaceCheck;
        if (old != replace)
        {
            _doReplaceCheck = replace;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_CHECK, old, replace);
    }
    boolean getReplaceCheck()
    {
        return _doReplaceCheck;
    }
    void setReplaceFoundCheckOnly(boolean foundTextOnly)
    {
        final boolean old = _replaceFoundCheckOnly;
        if (old != foundTextOnly)
        {
            _replaceFoundCheckOnly = foundTextOnly;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_FOUND_CHECK_ONLY, old,
                                        foundTextOnly);
    }
    boolean getReplaceFoundCheckOnly()
    {
        return _replaceFoundCheckOnly;
    }
    void setReplacementCheck(final String checkNumber)
    {
        if ( ((_replacementCheck == null) && (checkNumber != null)) ||
             ((_replacementCheck != null) && !_replacementCheck.equals(checkNumber)) )
        {
            _replacementCheck = checkNumber;
            _replaceDirty = true;
        }
    }
    String getReplacementCheck()
    {
        return _replacementCheck;
    }

    void setReplaceTags(boolean replace)
    {
        final boolean old = _doReplaceTags;
        if (old != replace)
        {
            _doReplaceTags = replace;
            _replaceDirty = true;
        }
        if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_TAGS, old, replace);
    }
    boolean getReplaceTags()
    {
        return _doReplaceTags;
    }
    TagPickerModel getReplaceAddTagsModel()
    {
        return _replaceAddTagPickerModel;
    }
    TagPickerModel getReplaceRemoveTagsModel()
    {
        return _replaceRemoveTagPickerModel;
    }
    TagPickerModel getReplaceReplaceTagsModel()
    {
        return _replaceReplaceTagPickerModel;
    }

    void setReplaceTagType(final ReplaceTagCommandType commandType)
    {
        if ( ((_replaceTagCommand == null) && (commandType != null)) ||
             ((_replaceTagCommand != null) && !_replaceTagCommand.equals(commandType)) )
        {
            _replaceTagCommand = commandType;
            _replaceDirty = true;
        }
    }
    ReplaceTagCommandType getReplaceTagType()
    {
        return _replaceTagCommand;
    }

    public ReplaceCommand buildReplaceCommand()
    {
        final Account category;
        if (_doReplaceCategory)
        {
            category = _replacementCategory;
        }
        else
        {
            category = null;
        }

        final Long amount;
        if (_doReplaceAmount)
        {
            amount = Long.valueOf(_replacementAmount);
        }
        else
        {
            amount = null;
        }

        final String description;
        if (_doReplaceDescription)
        {
            description = _replacementDescription;
        }
        else
        {
            description = null;
        }

        final String memo;
        if (_doReplaceMemo)
        {
            memo = _replacementMemo;
        }
        else
        {
            memo = null;
        }

        final String check;
        if (_doReplaceCheck)
        {
            check = _replacementCheck;
        }
        else
        {
            check = null;
        }

        final List<String> tags;
        if (_doReplaceTags)
        {
            if (ReplaceTagCommandType.ADD.equals(_replaceTagCommand))
            {
                tags = _replaceAddTagPickerModel.getSelectedTags();
            }
            else if (ReplaceTagCommandType.REMOVE.equals(_replaceTagCommand))
            {
                tags = _replaceRemoveTagPickerModel.getSelectedTags();
            }
            else if (ReplaceTagCommandType.REPLACE.equals(_replaceTagCommand))
            {
                tags = _replaceReplaceTagPickerModel.getSelectedTags();
            }
            else
            {
                tags = null;
            }
        }
        else
        {
            tags = null;
        }

        _replaceDirty = false;
        final boolean allowFoundOnly = _useFreeTextFilter &&
                (_freeTextMatch != null) && !"".equals(_freeTextMatch);
        final Pattern findPattern;
        if (allowFoundOnly)
        {
            findPattern = FarUtil.buildFindPattern(_freeTextMatch);
        }
        else
        {
            findPattern = null;
        }
        return new ReplaceCommand(category, amount, _replaceAmountCurrency,
                                  description, allowFoundOnly && _replaceFoundDescriptionOnly,
                                  memo, allowFoundOnly && _replaceFoundMemoOnly,
                                  check, allowFoundOnly && _replaceFoundCheckOnly,
                                  findPattern,
                                  _replaceTagCommand, tags, TxnUtil.getListOfAllUsedTransactionTags(_data.getTransactionSet().getAllTxns()));
    }

    boolean hasFindResults()
    {
        final boolean hasResults;
        final FindResultsTableModel results = getFindResults();
        if (results == null)
        {
            return false;
        }
        
        final int count = results.getRowCount();
        if (count == 0)
        {
            hasResults = false;
        }
        else if (count == 1)
        {
            // is this the blank transaction?
            hasResults = !results.isBlankEntry(results.getEntry(0));
        }
        else
        {
            hasResults = true;
        }
        return hasResults;
    }

    void resetApply()
    {
        final FindResultsTableModel tableModel = getFindResults();
        final int count = tableModel.getRowCount();
        for (int modelIndex = 0; modelIndex < count; modelIndex++)
        {
            tableModel.getEntry(modelIndex).resetApply();
        }
    }

    void setIncludeTransfers(final boolean include)
    {
        if (include != _includeTransfers)
        {
            final boolean old = _includeTransfers;
            _includeTransfers = include;

            // rebuild the category list
            final Collection<Integer> includedCats = _categoryFilter.getAllIncluded();
            setupCategoryFilter();
            loadCategoryFilter();
            if (_data != null)
            {
                for (Integer accountId : includedCats)
                {
                    Account catAccount = _data.getAccountByNum(accountId.intValue());
                    if (catAccount != null)
                    {
                        // this won't add if the account type isn't allowed - good
                        _categoryFilter.include(catAccount);
                    }
                }
            }

            if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.INCLUDE_TRANSFERS, old, include);
        }
    }

    boolean getIncludeTransfers()
    {
        return _includeTransfers;
    }

    void setShowParents(final boolean showParents)
    {
        if (showParents != _showParents)
        {
            final boolean old = _showParents;
            _showParents = showParents;
            _findResultsModel.refresh();
            if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.SHOW_PARENTS, old, showParents);
        }
    }

    boolean getShowParents()
    {
        return _showParents;
    }

    void setSplitsAsMemos(final boolean useSplitDescriptionAsMemo)
    {
        if (useSplitDescriptionAsMemo != _splitDescriptionAsMemo)
        {
            final boolean old = _splitDescriptionAsMemo;
            _splitDescriptionAsMemo = useSplitDescriptionAsMemo;
            _findResultsModel.refresh();
            if (_allowEvents) _eventNotify.firePropertyChange(N12EFindAndReplace.SPLITS_AS_MEMOS, old, useSplitDescriptionAsMemo);
        }
    }

    boolean getSplitsAsMemos()
    {
        return _splitDescriptionAsMemo;
    }

    String getSummaryText(final IResourceProvider resources)
    {
        String format = resources.getString(L10NFindAndReplace.RESULTS_SUMMARY_FMT);
        final int count = _findResultsModel.getRowCount();
        long minuses = 0;
        long plusses = 0;
        int selectedCount = 0;
        for (int modelIndex = 0; modelIndex < count; modelIndex++)
        {
            // if the user unchecks the box, remove that from the results value
            if (_findResultsModel.getEntry(modelIndex).isUseInReplace())
            {
                long value = _findResultsModel.getAmountInBaseCurrency(modelIndex);
                if (value >= 0)
                {
                    plusses += value;
                }
                else
                {
                    minuses += value;
                }
                ++selectedCount;
            }
        }

        long total = plusses + minuses;

        int displayCount = count;
        if ((count == 1) && (_findResultsModel.isBlankEntry(_findResultsModel.getEntry(0))))
        {
            displayCount = 0;
        }
        String countDisplay = String.format("%d / %d", Integer.valueOf(selectedCount),
                Integer.valueOf(displayCount));
        CurrencyType baseCurrency = _data.getCurrencies().getBaseType();
        char dec = _findResultsModel.getDecimalChar();
        String adds = baseCurrency.formatFancy(plusses, dec);
        String subtracts = baseCurrency.formatFancy(minuses, dec);
        String totalDisplay = baseCurrency.formatFancy(total, dec);
        return String.format(format, countDisplay, adds, subtracts, totalDisplay);
    }

    void copyToClipboard(final IResourceProvider resources, int[] rowOrder)
    {
        StringBuilder buffer = new StringBuilder();
        buffer.append(getSummaryText(resources));
        buffer.append(N12EFindAndReplace.NEWLINE);
        buffer.append(N12EFindAndReplace.NEWLINE);
        buffer.append(getColumnHeaders(resources));
        buffer.append(N12EFindAndReplace.NEWLINE);
        for (int rowModelIndex : rowOrder)
        {
            buffer.append(exportRowToClipboard(rowModelIndex));
            buffer.append(N12EFindAndReplace.NEWLINE);
        }

        StringSelection stringSel = new StringSelection( buffer.toString() );
        Toolkit.getDefaultToolkit().getSystemClipboard().setContents( stringSel, stringSel );
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private String getColumnHeaders(final IResourceProvider resources)
    {
        StringBuilder result = new StringBuilder();

        // account
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_ACCOUNT));
        result.append('\t');

        // date
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_DATE));
        result.append('\t');

        // check number
        result.append(resources.getString(L10NFindAndReplace.RESULTS_CHECKNO_LABEL));
        result.append('\t');

        // description
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_DESCRIPTION));
        result.append('\t');

        // memo
        result.append(resources.getString(L10NFindAndReplace.REPLACE_MEMO_LABEL));
        result.append('\t');

        // memo - parent
        if (_splitDescriptionAsMemo)
        {
            result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_PARENT_MEMO));
            result.append('\t');
        }

        // tag
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_TAG));
        result.append('\t');

        // category
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_CATEGORY));
        result.append('\t');

        // cleared
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_CLEARED));
        result.append('\t');

        // amount
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        result.append('\t');

        // shares (category currency)
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        result.append(N12EFindAndReplace.SHARES_SUFFIX);
        result.append('\t');

        // other amount (parent currency)
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        result.append(N12EFindAndReplace.OTHER_SUFFIX);
        result.append('\t');

        // selected yes/no
        result.append(N12EFindAndReplace.SPACE);

        return result.toString();
    }

    private String exportRowToClipboard(final int rowModelIndex)
    {
        StringBuilder result = new StringBuilder();

        // account
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.ACCOUNT_INDEX));
        result.append('\t');

        // date
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.DATE_INDEX));
        result.append('\t');

        // check number
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.CHECK_INDEX));
        result.append('\t');

        // description
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.DESCRIPTION_INDEX));
        result.append('\t');

        // memo
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.MEMO_INDEX));
        result.append('\t');

        // memo - parent
        if (_splitDescriptionAsMemo)
        {
            result.append(_findResultsModel.getValueAt(rowModelIndex,
                    FindResultsTableModel.MEMO_PARENT_INDEX));
            result.append('\t');
        }
        // tag
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.TAG_INDEX));
        result.append('\t');

        // category
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.FULL_CATEGORY_INDEX));
        result.append('\t');

        // cleared - here we need the text, not an image
        result.append(_findResultsModel.getEntry(rowModelIndex).getParentTxn().getStatusChar());
        result.append('\t');

        // amount
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.AMOUNT_INDEX));
        result.append('\t');

        // shares (category currency)
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.SHARES_INDEX));
        result.append('\t');

        // other amount (parent account currency)
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                                                   FindResultsTableModel.OTHER_AMOUNT_INDEX));
        result.append('\t');

        // selected
        Boolean selected = (Boolean)_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.USE_INDEX);
        if (Boolean.TRUE.equals(selected))
        {
            result.append("\u2713"); // check mark
        }
        else
        {
            result.append("");
        }

        return result.toString();
    }

    private void setupCategoryFilter()
    {
        _categoryFilter = new AccountFilter(L10NFindAndReplace.ACCOUNTFILTER_ALL_CATEGORIES);
        // all categories
        _categoryFilter.addAllowedType(Account.AccountType.INCOME);
        _categoryFilter.addAllowedType(Account.AccountType.EXPENSE);
        if (_includeTransfers)
        {
            _categoryFilter.addAllowedType(Account.AccountType.ASSET);
            _categoryFilter.addAllowedType(Account.AccountType.BANK);
            _categoryFilter.addAllowedType(Account.AccountType.CREDIT_CARD);
            _categoryFilter.addAllowedType(Account.AccountType.INVESTMENT);
            _categoryFilter.addAllowedType(Account.AccountType.LIABILITY);
            _categoryFilter.addAllowedType(Account.AccountType.LOAN);
            _categoryFilter.addAllowedType(Account.AccountType.SECURITY);
        }
    }

    private void loadCategoryFilter()
    {
        if (_data != null)
        {
            _fullCategoryList = new FullAccountList(_data, _categoryFilter, true);
            _categoryFilter.setFullList(_fullCategoryList);
        }
    }

    /**
     * Explicitly release memory for things other than the root data file
     */
    private void cleanUp()
    {
        _fullAccountList = null;
        _accountFilter.setFullList(null);
        _fullCategoryList = null;
        _categoryFilter.setFullList(null);
        _findResultsModel.reset();
        _includeTagPickerModel = null;
        _excludeTagPickerModel = null;
        _replaceAddTagPickerModel = null;
        _replaceRemoveTagPickerModel = null;
        _replaceReplaceTagPickerModel = null;
    }

}
