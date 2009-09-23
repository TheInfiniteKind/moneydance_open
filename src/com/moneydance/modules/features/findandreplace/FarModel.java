package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.TxnTag;
import com.moneydance.apps.md.controller.Util;

import java.util.Collection;
import java.awt.datatransfer.StringSelection;
import java.awt.Toolkit;

/**
 * <p>Model for the Find and Replace plugin. Stores all the settings you see in the dialog, and
 * fires property changes when selected values change.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.2
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

    private AccountFilter _categoryFilter;
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
    
    private boolean _useClearedFilter;
    private boolean _requireClearedFilter;
    private boolean _allowCleared;
    private boolean _allowReconciling;
    private boolean _allowUncleared;
    
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

    private boolean _includeTransfers;

    FarModel()
    {
        _accountFilter = new AccountFilter(L10NFindAndReplace.ACCOUNTFILTER_ALL_ACCOUNTS);
        // all types except categories and securities (which act like categories for investments)
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_ASSET);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_BANK);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_CREDIT_CARD);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_INVESTMENT);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_LIABILITY);
        _accountFilter.addAllowedType(Account.ACCOUNT_TYPE_LOAN);

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

    void setData( final RootAccount data )
    {
        _data = data;
        if (_data == null)
        {
            // nothing more to do
            cleanUp();
            return;
        }

        // create the full account list - we don't count sub-accounts for these, which generally
        // are securities within investment accounts
        _fullAccountList = new FullAccountList(_data, _accountFilter, true);
        _accountFilter.setFullList(_fullAccountList);

        // create the full category list, including sub-categories
        loadCategoryFilter();

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

    void setDefaults()
    {
        // set defaults
        _combineOr = false;
        _useAccountFilter = false;
        _requireAccountFilter = false;

        _useCategoryFilter = false;
        _requireCategoryFilter = false;

        _useAmountFilter = false;
        _requireAmountFilter = false;
        _amountMinimum = 0;
        _amountMaximum = 0;

        _useDateFilter = false;
        _requireDateFilter = false;
        _dateMinimum = Util.getStrippedDateInt();
        _dateMaximum = _dateMinimum;

        _useFreeTextFilter = false;
        _requireFreeTextFilter = false;
        _freeTextSearchDescription = true;
        _freeTextSearchMemo = true;
        _freeTextSearchCheck = true;
        _freeTextIncludeSplits = true;
        _freeTextMatch = N12EFindAndReplace.EMPTY;

        _useTagsFilter = false;
        _requireTagsFilter = false;

        _useClearedFilter = false;
        _requireClearedFilter = false;
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

        _doReplaceMemo = false;
        _replacementMemo = N12EFindAndReplace.EMPTY;

        _doReplaceTags = false;
        _replaceTagCommand = null;

        setIncludeTransfers(false);

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
        if (_useClearedFilter)
        {
            setRequireClearedFilter(!_combineOr);
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
    long getAmountMinimum()
    {
        return _amountMinimum;
    }
    long getAmountMaximum()
    {
        return _amountMaximum;
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
    int getDateMinimum()
    {
        return _dateMinimum;
    }
    int getDateMaximum()
    {
        return _dateMaximum;
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
    
    void setUseClearedFilter(final boolean use)
    {
        boolean old = _useClearedFilter;
        _useClearedFilter = use;
        _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_USE, old, use);
    }
    boolean getUseClearedFilter()
    {
        return _useClearedFilter;
    }
    void setRequireClearedFilter(final boolean require)
    {
        final boolean old = _requireClearedFilter;
        _requireClearedFilter = require;
        _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_REQUIRED, old, require);
    }
    boolean getRequireClearedFilter()
    {
        return _requireClearedFilter;
    }
    boolean getAllowCleared()
    {
        return _allowCleared;
    }
    void setAllowCleared(final boolean allow)
    {
        final boolean old = _allowCleared;
        _allowCleared = allow;
        _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_CLEARED, old, allow);
    }
    boolean getAllowReconciling()
    {
        return _allowReconciling;
    }
    void setAllowReconciling(final boolean allow)
    {
        final boolean old = _allowReconciling;
        _allowReconciling = allow;
        _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_RECONCILING, old, allow);
    }
    boolean getAllowUncleared()
    {
        return _allowUncleared;
    }
    void setAllowUncleared(final boolean allow)
    {
        final boolean old = _allowUncleared;
        _allowUncleared = allow;
        _eventNotify.firePropertyChange(N12EFindAndReplace.CLEARED_UNCLEARED, old, allow);
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
        if (_useClearedFilter)
        {
            result.addFilter(new ClearedTxnFilter(_allowCleared, _allowReconciling, _allowUncleared,
                    _requireClearedFilter));
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
    String getReplacementMemo()
    {
        return _replacementMemo;
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
                    Account catAccount = _data.getAccountById(accountId.intValue());
                    if (catAccount != null)
                    {
                        // this won't add if the account type isn't allowed - good
                        _categoryFilter.include(catAccount);
                    }
                }
            }

            _eventNotify.firePropertyChange(N12EFindAndReplace.INCLUDE_TRANSFERS, old, include);
        }
    }

    boolean getIncludeTransfers()
    {
        return _includeTransfers;
    }

    String getSummaryText(final IResourceProvider resources)
    {
        String format = resources.getString(L10NFindAndReplace.RESULTS_SUMMARY_FMT);
        final int count = _findResultsModel.getRowCount();
        long minuses = 0;
        long plusses = 0;
        for (int modelIndex = 0; modelIndex < count; modelIndex++)
        {
            // if the user unchecks the box, remove that from the results value
            if (_findResultsModel.getEntry(modelIndex).isUseInReplace())
            {
                long value = _findResultsModel.getAmount(modelIndex);
                if (value >= 0)
                {
                    plusses += value;
                }
                else
                {
                    minuses += value;
                }
            }
        }

        long total = plusses + minuses;

        int displayCount = count;
        if ((count == 1) && (_findResultsModel.isBlankEntry(_findResultsModel.getEntry(0))))
        {
            displayCount = 0;
        }
        String countDisplay = Integer.toString(displayCount);
        String adds = _findResultsModel.getAmountText(null, plusses);
        String subtracts = _findResultsModel.getAmountText(null, minuses);
        String totalDisplay = _findResultsModel.getAmountText(null, total);
        return String.format(format, countDisplay, adds, subtracts, totalDisplay);
    }

    void copyToClipboard(final IResourceProvider resources, int[] rowOrder)
    {
        StringBuffer buffer = new StringBuffer();
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
        StringBuffer result = new StringBuffer();

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

        // shares
        result.append(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        result.append(N12EFindAndReplace.SHARES_SUFFIX);

        return result.toString();
    }

    private String exportRowToClipboard(final int rowModelIndex)
    {
        StringBuffer result = new StringBuffer();

        // account
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.ACCOUNT_INDEX));
        result.append('\t');

        // date
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.DATE_INDEX));
        result.append('\t');

        // check number
        result.append(FarUtil.getTransactionCheckNo(
                _findResultsModel.getEntry(rowModelIndex).getParentTxn()));
        result.append('\t');

        // description
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.DESCRIPTION_INDEX));
        result.append('\t');

        // memo
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.MEMO_INDEX));
        result.append('\t');

        // tag
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.TAG_INDEX));
        result.append('\t');

        // category
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.CATEGORY_INDEX));
        result.append('\t');

        // cleared - here we need the text, not an image
        result.append(_findResultsModel.getEntry(rowModelIndex).getParentTxn().getStatusChar());
        result.append('\t');

        // amount
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.AMOUNT_INDEX));
        result.append('\t');

        // shares
        result.append(_findResultsModel.getValueAt(rowModelIndex,
                FindResultsTableModel.SHARES_INDEX));

        return result.toString();
    }

    private void setupCategoryFilter()
    {
        _categoryFilter = new AccountFilter(L10NFindAndReplace.ACCOUNTFILTER_ALL_CATEGORIES);
        // all categories
        _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_INCOME);
        _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_EXPENSE);
        if (_includeTransfers)
        {
            _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_ASSET);
            _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_BANK);
            _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_CREDIT_CARD);
            _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_INVESTMENT);
            _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_LIABILITY);
            _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_LOAN);
            _categoryFilter.addAllowedType(Account.ACCOUNT_TYPE_SECURITY);
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
