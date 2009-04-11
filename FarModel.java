package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.TxnTag;

/**
 * <p>Model for the Find and Replace plugin. Stores all the settings you see in the dialog, and
 * fires property changes when selected values change.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FarModel extends BasePropertyChangeReporter
{
    private RootAccount _data;
    private FindResultsTableModel _findResultsModel;

    private boolean _combineOr;
    private final AccountFilter _accountFilter;
    private FullAccountList _fullAccountList;
    private boolean _useAccountFilter;
    private boolean _requireAccountFilter;

    private final AccountFilter _categoryFilter;
    private FullAccountList _fullCategoryList;
    private boolean _useCategoryFilter;
    private boolean _requireCategoryFilter;

    private boolean _useAmountFilter;
    private boolean _requireAmountFilter;
    private long _amountMinimum;
    private long _amountMaximum;

    private boolean _useDateFilter;
    private boolean _requireDateFilter;
    private int _dateMinimum;
    private int _dateMaximum;

    private boolean _useFreeTextFilter;
    private boolean _requireFreeTextFilter;
    private boolean _freeTextSearchDescription;
    private boolean _freeTextSearchMemo;
    private boolean _freeTextSearchCheck;
    private boolean _freeTextIncludeSplits;
    private String _freeTextMatch;

    private TagPickerModel _includeTagPickerModel;
    private TagPickerModel _excludeTagPickerModel;
    private boolean _useTagsFilter;
    private boolean _requireTagsFilter;
    private boolean _replaceDirty = false;

    private boolean _doReplaceCategory;
    private Account _replacementCategory;

    private boolean _doReplaceAmount;
    private long _replacementAmount;

    private boolean _doReplaceDescription;
    private String _replacementDescription;

    private boolean _doReplaceMemo;
    private String _replacementMemo;

    private boolean _doReplaceTags;
    private ReplaceTagCommandType _replaceTagCommand;
    private TagPickerModel _replaceAddTagPickerModel;
    private TagPickerModel _replaceRemoveTagPickerModel;
    private TagPickerModel _replaceReplaceTagPickerModel;


    FarModel()
    {
        // set defaults
        _combineOr = false;
        _accountFilter = new AccountFilter(L10NFindAndReplace.ACCOUNTFILTER_ALL_ACCOUNTS);
        _useAccountFilter = false;
        _requireAccountFilter = false;
        _categoryFilter = new AccountFilter(L10NFindAndReplace.ACCOUNTFILTER_ALL_CATEGORIES);
        _freeTextSearchDescription = true;
        _freeTextSearchMemo = true;
        _freeTextSearchCheck = true;
        _freeTextIncludeSplits = true;
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Package Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    void setResultsModel(final FindResultsTableModel resultsModel)
    {
        _findResultsModel = resultsModel;
    }

    void setData( final RootAccount data )
    {
        _data = data;

        // all types except categories
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_ASSET);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_BANK);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_CREDIT_CARD);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_INVESTMENT);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_LIABILITY);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_LOAN);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_SECURITY);

        // create the full account list - we don't count sub-accounts for these, which generally
        // are securities within investment accounts
        _fullAccountList = new FullAccountList(_data, _accountFilter, true);
        _accountFilter.setFullList(_fullAccountList);

        // all categories
        _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_INCOME);
        _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_EXPENSE);

        // create the full category list, including sub-categories
        _fullCategoryList = new FullAccountList(_data, _categoryFilter, true);
        _categoryFilter.setFullList(_fullCategoryList);

        // to display user-defined tags, we have to have the list
        _findResultsModel.setUserTagSet(_data.getTxnTagSet());

        // and the pickers need the same
        _includeTagPickerModel = new TagPickerModel(_data.getTxnTagSet());
        _includeTagPickerModel.selectAll();  // all are selected by default
        _excludeTagPickerModel = new TagPickerModel(_data.getTxnTagSet());
        _replaceAddTagPickerModel = new TagPickerModel(_data.getTxnTagSet());
        _replaceRemoveTagPickerModel = new TagPickerModel(_data.getTxnTagSet());
        _replaceReplaceTagPickerModel = new TagPickerModel(_data.getTxnTagSet());
    }

    RootAccount getData()
    {
        return _data;
    }

    FindResultsTableModel getFindResults()
    {
        return _findResultsModel;
    }

    FullAccountList getFullAccountList()
    {
        return _fullAccountList;
    }

    FullAccountList getFullCategoryList()
    {
        return _fullCategoryList;
    }

    void accountListUpdated()
    {
        _eventNotify.firePropertyChange(N12EFindAndReplace.ACCOUNT_SELECT, null, null);
        setUseAccountFilter(true);
        setRequireAccountFilter(!_combineOr);
    }

    void categoryListUpdated()
    {
        _eventNotify.firePropertyChange(N12EFindAndReplace.CATEGORY_SELECT, null, null);
        setUseCategoryFilter(true);
        setRequireCategoryFilter(!_combineOr);
    }

    void tableUpdated()
    {
        _eventNotify.firePropertyChange(N12EFindAndReplace.FIND_RESULTS_UPDATE, null, null);
    }

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Properties
    //////////////////////////////////////////////////////////////////////////////////////////////

    void setFilterCombineOr(final boolean combineOr)
    {
        final boolean oldValue = _combineOr;
        _combineOr = combineOr;

        // for all selected criteria, toggle the required value
        if (_useAccountFilter)
        {
            setRequireAccountFilter(!_combineOr);
        }
        if (_useCategoryFilter)
        {
            setRequireCategoryFilter(!_combineOr);
        }
        if (_useDateFilter)
        {
            setRequireDateFilter(!_combineOr);
        }
        if (_useAmountFilter)
        {
            setRequireAmountFilter(!_combineOr);
        }
        if (_useFreeTextFilter)
        {
            setRequireFreeTextFilter(!_combineOr);
        }
        if (_useTagsFilter)
        {
            setRequireTagsFilter(!_combineOr);
        }

        _eventNotify.firePropertyChange(N12EFindAndReplace.FIND_COMBINATION, oldValue, _combineOr);
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
        _eventNotify.firePropertyChange(N12EFindAndReplace.ACCOUNT_USE, old, use);
    }
    boolean getUseAccountFilter()
    {
        return _useAccountFilter;
    }

    void setRequireAccountFilter(final boolean require)
    {
        final boolean old = _requireAccountFilter;
        _requireAccountFilter = require;
        _eventNotify.firePropertyChange(N12EFindAndReplace.ACCOUNT_REQUIRED, old, require);
    }
    boolean getRequireAccountFilter()
    {
        return _requireAccountFilter;
    }


    AccountFilter getCategoryFilter()
    {
        return _categoryFilter;
    }

    void setUseCategoryFilter(final boolean use)
    {
        boolean old = _useCategoryFilter;
        _useCategoryFilter = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.CATEGORY_USE, old, use);
    }
    boolean getUseCategoryFilter()
    {
        return _useCategoryFilter;
    }

    void setRequireCategoryFilter(final boolean require)
    {
        final boolean old = _requireCategoryFilter;
        _requireCategoryFilter = require;
        _eventNotify.firePropertyChange(N12EFindAndReplace.CATEGORY_REQUIRED, old, require);
    }
    boolean getRequireCategoryFilter()
    {
        return _requireCategoryFilter;
    }

    void setUseAmountFilter(final boolean use)
    {
        boolean old = _useAmountFilter;
        _useAmountFilter = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.AMOUNT_USE, old, use);
    }
    boolean getUseAmountFilter()
    {
        return _useAmountFilter;
    }

    void setRequireAmountFilter(final boolean require)
    {
        final boolean old = _requireAmountFilter;
        _requireAmountFilter = require;
        _eventNotify.firePropertyChange(N12EFindAndReplace.AMOUNT_REQUIRED, old, require);
    }
    boolean getRequireAmountFilter()
    {
        return _requireAmountFilter;
    }
    void setAmountRange(final long minimum, final long maximum)
    {
        _amountMinimum = minimum;
        _amountMaximum = maximum;
    }

    void setUseDateFilter(final boolean use)
    {
        boolean old = _useDateFilter;
        _useDateFilter = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.DATE_USE, old, use);
    }
    boolean getUseDateFilter()
    {
        return _useDateFilter;
    }
    void setRequireDateFilter(final boolean require)
    {
        final boolean old = _requireDateFilter;
        _requireDateFilter = require;
        _eventNotify.firePropertyChange(N12EFindAndReplace.DATE_REQUIRED, old, require);
    }
    boolean getRequireDateFilter()
    {
        return _requireDateFilter;
    }
    void setDateRange(final int minimum, final int maximum)
    {
        _dateMinimum = minimum;
        _dateMaximum = maximum;
    }

    void setUseFreeTextFilter(final boolean use)
    {
        boolean old = _useFreeTextFilter;
        _useFreeTextFilter = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_USE, old, use);
    }
    boolean getUseFreeTextFilter()
    {
        return _useFreeTextFilter;
    }
    void setRequireFreeTextFilter(final boolean require)
    {
        final boolean old = _requireFreeTextFilter;
        _requireFreeTextFilter = require;
        _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_REQUIRED, old, require);
    }
    boolean getRequireFreeTextFilter()
    {
        return _requireFreeTextFilter;
    }
    void setFreeTextMatch(final String description)
    {
        _freeTextMatch = description;
    }

    void setFreeTextUseDescription(final boolean use)
    {
        final boolean old = _freeTextSearchDescription;
        _freeTextSearchDescription = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_DESCRIPTION, old, use);
    }
    boolean getFreeTextUseDescription()
    {
        return _freeTextSearchDescription;
    }
    void setFreeTextUseMemo(final boolean use)
    {
        final boolean old = _freeTextSearchMemo;
        _freeTextSearchMemo = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_MEMO, old, use);
    }
    boolean getFreeTextUseMemo()
    {
        return _freeTextSearchMemo;
    }
    void setFreeTextUseCheck(final boolean use)
    {
        final boolean old = _freeTextSearchCheck;
        _freeTextSearchCheck = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_CHECK, old, use);
    }
    boolean getFreeTextUseCheck()
    {
        return _freeTextSearchCheck;
    }
    void setFreeTextIncludeSplits(final boolean include)
    {
        final boolean old = _freeTextIncludeSplits;
        _freeTextIncludeSplits = include;
        _eventNotify.firePropertyChange(N12EFindAndReplace.FREETEXT_SPLITS, old, include);
    }
    boolean getFreeTextIncludeSplits()
    {
        return _freeTextIncludeSplits;
    }

    void setUseTagsFilter(final boolean use)
    {
        boolean old = _useTagsFilter;
        _useTagsFilter = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.TAGS_USE, old, use);
    }
    boolean getUseTagsFilter()
    {
        return _useTagsFilter;
    }
    void setRequireTagsFilter(final boolean require)
    {
        final boolean old = _requireTagsFilter;
        _requireTagsFilter = require;
        _eventNotify.firePropertyChange(N12EFindAndReplace.TAGS_REQUIRED, old, require);
    }
    boolean getRequireTagsFilter()
    {
        return _requireTagsFilter;
    }

    TagPickerModel getIncludedTagsModel()
    {
        return _includeTagPickerModel;
    }
    TagPickerModel getExcludedTagsModel()
    {
        return _excludeTagPickerModel;
    }

    FilterGroup buildTransactionFilter()
    {
        final FilterGroup result = new FilterGroup();

        if (_useAccountFilter)
        {
            result.addFilter(new AccountTxnFilter(_accountFilter, _requireAccountFilter));
        }
        if (_useCategoryFilter)
        {
            result.addFilter(new CategoryTxnFilter(_categoryFilter, _requireCategoryFilter));
        }
        if (_useDateFilter)
        {
            result.addFilter(new DateRangeTxnFilter(_dateMinimum, _dateMaximum, _requireDateFilter));
        }
        if (_useAmountFilter)
        {
            result.addFilter(new AmountTxnFilter(_amountMinimum, _amountMaximum, _requireAmountFilter));
        }
        if (_useFreeTextFilter)
        {
            result.addFilter(new FreeTextTxnFilter(_freeTextMatch, _freeTextSearchDescription,
                    _freeTextSearchMemo, _freeTextSearchCheck,
                    _freeTextIncludeSplits, _requireFreeTextFilter));
        }
        if (_useTagsFilter)
        {
            result.addFilter(new TagsTxnFilter(_includeTagPickerModel.getSelectedTags(),
                    _excludeTagPickerModel.getSelectedTags(), _requireTagsFilter));
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
        _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_CATEGORY, old, replace);
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

    void setReplaceAmount(boolean replace)
    {
        final boolean old = _doReplaceAmount;
        if (old != replace)
        {
            _doReplaceAmount = replace;
            _replaceDirty = true;
        }
        _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_AMOUNT, old, replace);
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

    void setReplaceDescription(boolean replace)
    {
        final boolean old = _doReplaceDescription;
        if (old != replace)
        {
            _doReplaceDescription = replace;
            _replaceDirty = true;
        }
        _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_DESCRIPTION, old, replace);
    }
    boolean getReplaceDescription()
    {
        return _doReplaceDescription;
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

    void setReplaceMemo(boolean replace)
    {
        final boolean old = _doReplaceMemo;
        if (old != replace)
        {
            _doReplaceMemo = replace;
            _replaceDirty = true;
        }
        _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_MEMO, old, replace);
    }
    boolean getReplaceMemo()
    {
        return _doReplaceMemo;
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

    void setReplaceTags(boolean replace)
    {
        final boolean old = _doReplaceTags;
        if (old != replace)
        {
            _doReplaceTags = replace;
            _replaceDirty = true;
        }
        _eventNotify.firePropertyChange(N12EFindAndReplace.REPLACE_TAGS, old, replace);
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

        final TxnTag[] tags;
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

        return new ReplaceCommand(category, amount, description, memo, _replaceTagCommand, tags,
                _data.getTxnTagSet());
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

    public void resetApply()
    {
        final FindResultsTableModel tableModel = getFindResults();
        final int count = tableModel.getRowCount();
        for (int modelIndex = 0; modelIndex < count; modelIndex++)
        {
            tableModel.getEntry(modelIndex).resetApply();
        }
    }
}
