/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.controller.AccountFilter;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.reporttool.GraphReportUtil;
import com.moneydance.apps.md.view.gui.select.AddRemoveAccountDialog;

import javax.swing.JOptionPane;
import javax.swing.JTable;
import java.awt.Cursor;
import java.util.HashSet;
import java.util.List;
import java.util.ArrayList;
import java.text.DecimalFormatSymbols;
import java.awt.Image;
import java.awt.Point;
import java.util.Set;

/**
 * <p>Controller for the plugin component for Find and Replace. This class brokers method calls
 * and performs some of the main functions of the plugin.</p>
 * 
 * @author Kevin Menningen
 * @version Build 94
 * @since 1.0
 */
public class FarController implements IFindAndReplaceController
{
    private FindAndReplace _host;
    private final FarModel _model;
    private FarView _view = null;

    private int _replaceViewIndex = -1;
    private final List<ReplaceCommand> _commands = new ArrayList<ReplaceCommand>();

    private String _initialFreeText = null;
    private String _dateRangeKey = null;

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Construction
    //////////////////////////////////////////////////////////////////////////////////////////////

    FarController(final FarModel model)
    {
        _model = model;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  IFindAndReplaceController
    //////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Initialize the dialog with the data from the application.
     *
     * @param data The data to load with.
     */
    public void loadData(final AccountBook data)
    {
        _model.setData( data );
    }

    public void cleanUp()
    {
        cleanupView();
        _model.setData(null);
    }

    /**
     * Display the dialog/frame on the screen.
     */
    public void show()
    {
        createView();
        _view.layoutUI();
        loadSizeAndPositionFromPreferences();
        _view.setVisible( true );
        _view.toFront();
        _view.setFreeText(_initialFreeText);
        if (_initialFreeText != null)
        {
            _view.fireFind();
        }

        refresh();
    }

    public void refresh()
    {
        _model.notifyAllListeners();
    }

    /**
     * This is called when the dialog is to be destroyed
     */
    public void hide()
    {
        // save our size and location
        if (_view != null)
        {
            Point location = _view.getLocation();
            Point size = new Point(_view.getSize().width, _view.getSize().height);
            if (getMDGUI() != null)
            {
                final String locationSetting = FarUtil.settingsStringFromPoint(location);
                getMDGUI().getPreferences().setSetting(
                        N12EFindAndReplace.SETTINGS_DLG_LOCATION_SETTING, locationSetting);

                final String sizeSetting = FarUtil.settingsStringFromPoint(size);
                getMDGUI().getPreferences().setSetting(
                        N12EFindAndReplace.SETTINGS_DLG_SIZE_SETTING, sizeSetting);
            }
        }
        cleanupView();
        _host.cleanUp(this);
    }

    public void find()
    {
        final AccountBook book = _model.getData();
        if ( book == null )
        {
            return;
        }

        FilterGroup filter = _model.buildTransactionFilter();

        // start with nothing
        _model.getFindResults().reset();

        // run the filter
        final int matched = filterTransactions(book, filter);
        if (matched > 0)
        {
            _model.getFindResults().refresh();
        }
        else
        {
            _model.getFindResults().addBlankTransaction();
        }
        _model.tableUpdated();

        // reset for the replace operation
        setReplaceViewIndex(0);
        _commands.clear(); // currently only support one command at a time
        _view.getFindResultsTable().clearSelection();
        _model.resetApply();
        
    } // find()

    /**
     * Add all of the matching splits to the report set. When displayed, either the list of splits
     * will be shown or the parents will be shown. Both lists are derived from the splits list, so
     * we simply create the split list here.
     *
     * @param book The main data account
     * @param filter      The search filter.
     * @return The number of splits that matched
     */
    private int filterTransactions(AccountBook book, FilterGroup filter)
    {
        // build the list of transactions that match the criteria
        Set<String> uniqueTxnIDs = new HashSet<String>();
        final TransactionSet txnSet = book.getTransactionSet();
        for(AbstractTxn txn : txnSet.iterableTxns())
        {
            // both parents and splits will be run through here
            if (filter.containsTxn(txn))
            {
                // the report set should contain splits only, find any parents and add all of their splits
                if (txn instanceof ParentTxn)
                {
                    for (int ii = txn.getOtherTxnCount() - 1; ii >= 0; ii--)
                    {
                        final SplitTxn split = (SplitTxn) txn.getOtherTxn(ii);
                        final String key = split.getUUID();
                        if (uniqueTxnIDs.contains(key)) continue;
                        _model.getFindResults().add(split, false);
                        uniqueTxnIDs.add(key);
                    } // for ii
                }
                else
                {
                    // must be a split transaction, just add it
                    final SplitTxn split = (SplitTxn) txn;
                    final String key = split.getUUID();
                    if (uniqueTxnIDs.contains(key)) continue;
                    _model.getFindResults().add(split, false);
                    uniqueTxnIDs.add(key);
                }
            }
        }
        return uniqueTxnIDs.size();
    }

    public void replace()
    {
        // currently only support one command at a time
        if (_model.isReplaceDirty())
        {
            _commands.clear();
            _model.tableUpdated();
        }
        if (_commands.isEmpty())
        {
            // first time for the command, add it
            _commands.add(_model.buildReplaceCommand());
        }

        final FindResultsTableEntry entry = findNextReplaceEntry();
        if (entry != null)
        {
            // build a command using the current settings
            entry.applyCommand();

            // update display
            final JTable resultsTable = _view.getFindResultsTable();
            int modelIndex = resultsTable.convertRowIndexToModel(_replaceViewIndex);
            _model.getFindResults().fireTableRowsUpdated(modelIndex, modelIndex);
            // move to the next eligible row
            findNextReplaceEntry();
            if ((_replaceViewIndex >= 0) && (_replaceViewIndex < resultsTable.getRowCount()))
            {
                resultsTable.setRowSelectionInterval(_replaceViewIndex, _replaceViewIndex);
            }
            else
            {
                // clear selection because it isn't valid anymore
                resultsTable.clearSelection();
            }
            _model.tableUpdated();
        }
    }

    public void replaceAll()
    {
        // currently only support one command at a time
        if (_model.isReplaceDirty())
        {
            _commands.clear();
            _model.tableUpdated();
        }
        if (_commands.isEmpty())
        {
            // first time for the command, add it
            _commands.add(_model.buildReplaceCommand());
        }

        _view.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
        // Replace All always starts at the beginning
        setReplaceViewIndex(0);
        FindResultsTableEntry entry = findNextReplaceEntry();
        while (entry != null)
        {
            entry.applyCommand();

            // next iteration
            entry = findNextReplaceEntry();
        }
        _view.setCursor(Cursor.getDefaultCursor());

        // update display
        _model.getFindResults().fireTableDataChanged();
        _view.getFindResultsTable().clearSelection();
        _model.tableUpdated();
    }

    public void commit()
    {
        // save everything to the Moneydance file
        if (isDirty())
        {
            final AccountBook root = _model.getData();
            final MoneydanceGUI mdGui = getMDGUI();
            if (mdGui != null)
            {
                mdGui.setSuspendRefresh(true);
                root.setRecalcBalances(false);
            }

            boolean changed = false;
            try
            {
                final FindResultsTableModel results = _model.getFindResults();
                final int count = results.getRowCount();
                _view.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
                for (int rowIndex = 0; rowIndex < count; rowIndex++)
                {
                    final FindResultsTableEntry entry = results.getEntry(rowIndex);
                    if (entry.isApplied() && entry.isUseInReplace())
                    {
                        for (final ReplaceCommand command : _commands)
                        {
                            command.setTransactionEntry(entry);
                            if (command.execute())
                            {
                                changed = true;
                                // this will notify the system of the modification
                                root.getTransactionSet().txnModified( command.getParentTransaction() );
                            }
                        }
                    } // if use this entry
                } // for rowIndex

                _view.setCursor(Cursor.getDefaultCursor());
            } // try
            catch (Exception error)
            {
                Logger.logError("Error replacing data with Find and Replace", error);
            }
            finally
            {
                if (changed)
                {
                    // flag to MoneyDance that the file has been modified
                    if (mdGui != null)
                    {
                        mdGui.setSuspendRefresh(false);
                    }
                    root.setRecalcBalances(true);
                    root.refreshAccountBalances();
                }
            } // finally
        } // if dirty
    } // commit()

    public void reset()
    {
        _model.setDefaults();
        _model.getFindResults().reset();

        // update display
        _model.getFindResults().fireTableDataChanged();
        _view.getFindResultsTable().clearSelection();
        // send a global refresh request
        if (_model.getAllowEvents()) _model.notifyAllListeners();
    }

    public void updateRow(int modelIndex)
    {
        _model.tableUpdated();
    }

    public void setInitialFreeText(final String freeText)
    {
        if ((freeText != null) && (freeText.length() > 0))
        {
            _initialFreeText = freeText;
        }
        else
        {
            _initialFreeText = null;
        }
    }

    public boolean getShowParents()
    {
        return _model.getShowParents();
    }

    public boolean getSplitsAsMemos()
    {
        return _model.getSplitsAsMemos();
    }

    public boolean isDirty()
    {
        boolean dirty = _model.hasFindResults();
        if (dirty)
        {
            // check if any are applied
            boolean applied = false;
            final FindResultsTableModel results = _model.getFindResults();
            final int count = results.getRowCount();
            for (int rowIndex = 0; !applied && (rowIndex < count); rowIndex++)
            {
                applied = results.getEntry(rowIndex).isApplied();
            }

            dirty = applied;
        }
        return dirty;
    }

    /**
     * Obtain the user-defined name of a specific account.
     * @param accountID The account identifier.
     * @return The name of the account.
     */
    public String getAccountName(final int accountID)
    {
        final AccountBook root = _model.getData();
        if (root != null)
        {
            final Account acct = root.getAccountByNum(accountID);
            if (acct == null)
            {
                return N12EFindAndReplace.EMPTY;
            }

            return acct.getAccountName();
        }
        return N12EFindAndReplace.EMPTY;
    }

    public com.moneydance.apps.md.controller.Main getMDMain()
    {
        return _host.getMDMain();
    }

    public com.moneydance.apps.md.view.gui.MoneydanceGUI getMDGUI()
    {
        return _host.getMDGUI();
    }

    public AccountBook getBook()
    {
        return _model.getData();
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // IResourceProvider
    ///////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Obtain the given string from the resource bundle.
     * @param resourceKey The key to look up the resources.
     * @return The associated string, or <code>null</code> if the key is not found.
     */
    public String getString(final String resourceKey)
    {
        return _host.getString( resourceKey );
    }

    /**
     * Obtain the given image from the resource bundle. The key specifies an image URL.
     * @param resourceKey The key to look up the resources with.
     * @return The associated image, or <code>null</code> if the key is not found or the image
     * could not be loaded.
     */
    public Image getImage(final String resourceKey)
    {
        return _host.getImage( resourceKey );
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Package Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    String getBuildString()
    {
        return _host.getBuildString();
    }

    void setAllowEvents(final boolean allow)
    {
        _model.setAllowEvents(allow);
    }

    void setHost(final FindAndReplace host)
    {
        _host = host;
        
        // this needs the host to look up strings
        final FindResultsTableModel tableModel = new FindResultsTableModel(this);
        tableModel.setCommandList(_commands);
        _model.setResultsModel(tableModel);

    }

    void setReplaceViewIndex(final int viewIndex)
    {
        _replaceViewIndex = viewIndex;
    }

    @SuppressWarnings({"BooleanMethodIsAlwaysInverted"})
    boolean getFilterCombineOr()
    {
        return _model.getFilterCombineOr();
    }
    void setFilterCombineOr(final boolean combineOr)
    {
        _model.setFilterCombineOr(combineOr);
    }

    void selectAccounts(final MoneydanceGUI mdGui)
    {
        final AccountFilter filter = _model.getAccountFilter();
        AddRemoveAccountDialog dialog = new AddRemoveAccountDialog(_view,
                                                                   mdGui, filter,
                                                                   mdGui.getCurrentAccount());
        dialog.setHeadersAreSpecial(false);
        dialog.loadData();

        dialog.pack();
        dialog.setLocationRelativeTo(_view);
        dialog.setVisible(true);
        if (dialog.getResult() == JOptionPane.OK_OPTION)
        {
            // the user accepted the new changes to the listed nodes
            final List<Account> newNodeList = dialog.getSelectedNodes();
            filter.reset();
            for (final Account account : newNodeList)
            {
                filter.include(account);
            }
            // the account list was updated
            _model.accountListUpdated();
        }
        dialog.cleanUp();
    }

    void selectCategories(final MoneydanceGUI mdGui)
    {
        final AccountFilter filter = _model.getCategoryFilter();
        AddRemoveAccountDialog dialog = new AddRemoveAccountDialog(_view,
                                                                   mdGui, filter,
                                                                   mdGui.getCurrentAccount());
        dialog.setHeadersAreSpecial(false);
        dialog.loadData();

        dialog.pack();
        dialog.setLocationRelativeTo(_view);
        dialog.setVisible(true);
        if (dialog.getResult() == JOptionPane.OK_OPTION)
        {
            // the user accepted the new changes to the listed nodes
            final List<Account> newNodeList = dialog.getSelectedNodes();
            filter.reset();
            for (final Account account : newNodeList)
            {
                filter.include(account);
            }
            // the account list was updated
            _model.categoryListUpdated();
        }
        dialog.cleanUp();
    }

    void markAll()
    {
        if (_model.hasFindResults())
        {
            final FindResultsTableModel results = _model.getFindResults();
            final int count = results.getRowCount();
            for (int rowIndex = 0; rowIndex < count; rowIndex++)
            {
                results.getEntry(rowIndex).setUseInReplace(true);
            }
            results.fireTableDataChanged();
            _model.tableUpdated();
        }
    }

    void markNone()
    {
        if (_model.hasFindResults())
        {
            final FindResultsTableModel results = _model.getFindResults();
            final int count = results.getRowCount();
            for (int rowIndex = 0; rowIndex < count; rowIndex++)
            {
                results.getEntry(rowIndex).setUseInReplace(false);
            }
            results.fireTableDataChanged();
            _model.tableUpdated();
        }
    }

    void gotoTransaction(int tableModelRow)
    {
        if (_model.hasFindResults() && (tableModelRow >= 0))
        {
            final FindResultsTableModel results = _model.getFindResults();
            final int count = results.getRowCount();
            if (tableModelRow < count)
            {
                final FindResultsTableEntry tableEntry = results.getEntry(tableModelRow);
                AbstractTxn targetTxn = tableEntry.getParentTxn();
                getMDGUI().showTxn(targetTxn);
            }
        }
    }

    void saveUserEdits()
    {
        _view.saveFindEdits();
        _view.saveReplaceEdits();
    }

    String getAccountListDisplay(final MoneydanceGUI mdGui)
    {
        return _model.getAccountFilter().getDisplayString(getBook(), mdGui);
    }
    
    String getAccountListSave()
    {
        return GraphReportUtil.encodeAcctList(_model.getAccountFilter());
    }
    void setAccountListSave(final String accountList)
    {
        FarAccountSelector accountSelector = new FarAccountSelector(_model.getData(),
                                                                    _model.getAccountFilter());
        accountSelector.selectFromEncodedString(accountList);
    }

    void setUseAccountFilter(final boolean use)
    {
        _model.setUseAccountFilter(use);
    }
    boolean getUseAccountFilter()
    {
        return _model.getUseAccountFilter();
    }

    void setUseCategoryFilter(final boolean use)
    {
        _model.setUseCategoryFilter(use);
    }
    boolean getUseCategoryFilter()
    {
        return _model.getUseCategoryFilter();
    }
    String getCategoryListDisplay(final MoneydanceGUI mdGui)
    {
        return _model.getCategoryFilter().getDisplayString(getBook(), mdGui);
    }
    String getCategoryListSave()
    {
        return GraphReportUtil.encodeAcctList(_model.getCategoryFilter());
    }
    void setCategoryListSave(final String accountList)
    {
        FarAccountSelector accountSelector = new FarAccountSelector(_model.getData(),
                                                                    _model.getCategoryFilter());
        accountSelector.selectFromEncodedString(accountList);
    }

    void setUseAmountFilter(final boolean use)
    {
        _model.setUseAmountFilter(use);
    }
    boolean getUseAmountFilter()
    {
        return _model.getUseAmountFilter();
    }
    void setAmountRange(final long minimum, final long maximum)
    {
        final long lhs = Math.abs(minimum);
        final long rhs = Math.abs(maximum);
        _model.setAmountRange(Math.min(lhs, rhs), Math.max(lhs, rhs));
    }
    long getAmountMinimum()
    {
        return _model.getAmountMinimum();
    }
    long getAmountMaximum()
    {
        return _model.getAmountMaximum();
    }
    void setAmountCurrency(final CurrencyType newCurrency, final boolean isSharesCurrency)
    {
        _model.setFindAmountCurrency(newCurrency, isSharesCurrency);
    }
    CurrencyType getAmountCurrency()
    {
        return _model.getFindAmountCurrency();
    }

    void setUseDateFilter(final boolean use)
    {
        _model.setUseDateFilter(use);
    }
    boolean getUseDateFilter()
    {
        return _model.getUseDateFilter();
    }
    void setDateRange(final int minimum, final int maximum, final boolean useTaxDate)
    {
        _model.setDateRange(minimum, maximum, useTaxDate);
    }
    String getDateRangeKey()
    {
        return _dateRangeKey;
    }
    void setDateRangeKey(final String rangeKey)
    {
        _dateRangeKey = rangeKey;
    }
    int getDateMinimum()
    {
        return _model.getDateMinimum();
    }
    int getDateMaximum()
    {
        return _model.getDateMaximum();
    }
    boolean getUseTaxDate()
    {
        return _model.getUseTaxDate();
    }

    void setUseFreeTextFilter(final boolean use)
    {
        _model.setUseFreeTextFilter(use);
    }
    boolean getUseFreeTextFilter()
    {
        return _model.getUseFreeTextFilter();
    }
    void setFreeTextMatch(final String textOrRegEx)
    {
        _model.setFreeTextMatch(textOrRegEx);
    }
    String getFreeTextMatch()
    {
        return _model.getFreeTextMatch();
    }
    void setFreeTextUseDescription(final boolean use)
    {
        _model.setFreeTextUseDescription(use);
    }
    boolean getFreeTextUseDescription()
    {
        return _model.getFreeTextUseDescription();
    }
    void setFreeTextUseMemo(final boolean use)
    {
        _model.setFreeTextUseMemo(use);
    }
    boolean getFreeTextUseMemo()
    {
        return _model.getFreeTextUseMemo();
    }
    void setFreeTextUseCheck(final boolean use)
    {
        _model.setFreeTextUseCheck(use);
    }
    boolean getFreeTextUseCheck()
    {
        return _model.getFreeTextUseCheck();
    }
    void setFreeTextIncludeSplits(final boolean include)
    {
        _model.setFreeTextIncludeSplits(include);
    }
    boolean getFreeTextIncludeSplits()
    {
        return _model.getFreeTextIncludeSplits();
    }

    void setUseTagsFilter(final boolean use)
    {
        _model.setUseTagsFilter(use);
    }
    boolean getUseTagsFilter()
    {
        return _model.getUseTagsFilter();
    }
    void setTagsFilterLogic(final TagLogic combine)
    {
        _model.setRequireTagsFilter(combine);
    }
    TagLogic getRequireTagsFilter()
    {
        return _model.getRequireTagsFilter();
    }

    TagPickerModel getIncludedTagsModel()
    {
        return _model.getIncludedTagsModel();
    }
    TagPickerModel getExcludedTagsModel()
    {
        return _model.getExcludedTagsModel();
    }

    void setUseClearedFilter(final boolean use)
    {
        _model.setUseClearedFilter(use);
    }
    boolean getUseClearedFilter()
    {
        return _model.getUseClearedFilter();
    }
    boolean getAllowCleared()
    {
        return _model.getAllowCleared();
    }
    void setAllowCleared(final boolean allow)
    {
        _model.setAllowCleared(allow);
    }
    boolean getAllowReconciling()
    {
        return _model.getAllowReconciling();
    }
    void setAllowReconciling(final boolean allow)
    {
        _model.setAllowReconciling(allow);
    }
    boolean getAllowUncleared()
    {
        return _model.getAllowUncleared();
    }
    void setAllowUncleared(final boolean allow)
    {
        _model.setAllowUncleared(allow);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Replace Controls Support
    ///////////////////////////////////////////////////////////////////////////////////////////////

    void setReplaceCategory(boolean replace)
    {
        _model.setReplaceCategory(replace);
    }
    boolean getReplaceCategory()
    {
        return _model.getReplaceCategory();
    }
    void setReplacementCategory(final Account category)
    {
        _model.setReplacementCategory(category);
    }
    Account getReplacementCategory()
    {
        return _model.getReplacementCategory();
    }

    void setReplaceAmount(boolean replace)
    {
        _model.setReplaceAmount(replace);
    }
    boolean getReplaceAmount()
    {
        return _model.getReplaceAmount();
    }
    void setReplacementAmount(final long amount, final CurrencyType replaceCurrency)
    {
        _model.setReplacementAmount(amount);
        _model.setReplaceAmountCurrency(replaceCurrency);
    }
    long getReplacementAmount()
    {
        return _model.getReplacementAmount();
    }
    CurrencyType getReplaceAmountCurrency()
    {
        return _model.getReplaceAmountCurrency();
    }

    void setReplaceDescription(boolean replace)
    {
        _model.setReplaceDescription(replace);
    }
    boolean getReplaceDescription()
    {
        return _model.getReplaceDescription();
    }
    void setReplaceFoundDescriptionOnly(boolean foundTextOnly)
    {
        _model.setReplaceFoundDescriptionOnly(foundTextOnly);
    }
    boolean getReplaceFoundDescriptionOnly()
    {
        return _model.getReplaceFoundDescriptionOnly();
    }
    void setReplacementDescription(final String description)
    {
        _model.setReplacementDescription(description);
    }
    String getReplacementDescription()
    {
        return _model.getReplacementDescription();
    }

    void setReplaceMemo(boolean replace)
    {
        _model.setReplaceMemo(replace);
    }
    boolean getReplaceMemo()
    {
        return _model.getReplaceMemo();
    }
    void setReplaceFoundMemoOnly(boolean foundTextOnly)
    {
        _model.setReplaceFoundMemoOnly(foundTextOnly);
    }
    boolean getReplaceFoundMemoOnly()
    {
        return _model.getReplaceFoundMemoOnly();
    }
    void setReplacementMemo(final String memo)
    {
        _model.setReplacementMemo(memo);
    }
    String getReplacementMemo()
    {
        return _model.getReplacementMemo();
    }

    void setReplaceCheck(boolean replace)
    {
        _model.setReplaceCheck(replace);
    }
    boolean getReplaceCheck()
    {
        return _model.getReplaceCheck();
    }
    void setReplaceFoundCheckOnly(boolean foundTextOnly)
    {
        _model.setReplaceFoundCheckOnly(foundTextOnly);
    }
    boolean getReplaceFoundCheckOnly()
    {
        return _model.getReplaceFoundCheckOnly();
    }
    void setReplacementCheck(final String memo)
    {
        _model.setReplacementCheck(memo);
    }
    String getReplacementCheck()
    {
        return _model.getReplacementCheck();
    }

    void setReplaceTags(boolean replace)
    {
        _model.setReplaceTags(replace);
    }
    boolean getReplaceTags()
    {
        return _model.getReplaceTags();
    }

    void setReplaceTagType(final ReplaceTagCommandType commandType)
    {
        _model.setReplaceTagType(commandType);
    }
    ReplaceTagCommandType getReplaceTagType()
    {
        return _model.getReplaceTagType();
    }
    TagPickerModel getReplaceAddTagsModel()
    {
        return _model.getReplaceAddTagsModel();
    }
    TagPickerModel getReplaceRemoveTagsModel()
    {
        return _model.getReplaceRemoveTagsModel();
    }
    TagPickerModel getReplaceReplaceTagsModel()
    {
        return _model.getReplaceReplaceTagsModel();
    }

    public CurrencyType getCurrencyType()
    {
        CurrencyTable currencyTable = getCurrencyTable();
        if (currencyTable != null)
        {
            return currencyTable.getBaseType();
        }
        return null;
    }

    CurrencyTable getCurrencyTable()
    {
        final AccountBook book = _model.getData();
        if (book != null)
        {
            return book.getCurrencies();
        }
        return null;
    }

    char getDecimalChar()
    {
        return DecimalFormatSymbols.getInstance().getDecimalSeparator();
    }

    char getCommaChar()
    {
        return DecimalFormatSymbols.getInstance().getGroupingSeparator();
    }

    void setIncludeTransfers(final boolean include)
    {
        _model.setIncludeTransfers(include);
    }

    boolean getIncludeTransfers()
    {
        return _model.getIncludeTransfers();
    }

    void setShowParents(final boolean showParents)
    {
        _model.setShowParents(showParents);
    }

    void setSplitsAsMemos(final boolean useSplitDescriptionAsMemo)
    {
        _model.setSplitsAsMemos(useSplitDescriptionAsMemo);
    }

    void copyToClipboard()
    {
        JTable table = _view.getFindResultsTable();
        final int rowCount = table.getRowCount();
        int[] rowOrder = new int[rowCount];
        for (int viewRow = 0; viewRow < rowCount; viewRow++)
        {
            rowOrder[viewRow] = table.convertRowIndexToModel(viewRow);
        }
        _model.copyToClipboard(this, rowOrder);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void createView()
    {
        if (_view == null)
        {
            _view = new FarView(_model, this, getMDGUI(), getString(L10NFindAndReplace.TITLE));
            // hook up listeners
            _model.addPropertyChangeListener(_view);
        }
    }

    private void cleanupView()
    {
        if (_view != null)
        {
            _view.setVisible(false);
            _view.setController(null);
            _model.removePropertyChangeListener(_view);
            _view = null;
        }
    }

    private void loadSizeAndPositionFromPreferences()
    {
        if (getMDGUI() != null)
        {
            final String settingsLocation =  getMDGUI().getPreferences().getSetting(
                    N12EFindAndReplace.SETTINGS_DLG_LOCATION_SETTING,
                    N12EFindAndReplace.EMPTY);
            if (settingsLocation.length() > 0)
            {
                Point location = FarUtil.pointFromSettingsString(settingsLocation);
                if (location != null)
                {
                    _view.setLocation(location);
                }
            }

            final String settingsSize =  getMDGUI().getPreferences().getSetting(
                    N12EFindAndReplace.SETTINGS_DLG_SIZE_SETTING,
                    N12EFindAndReplace.EMPTY);
            if (settingsSize.length() > 0)
            {
                final Point size = FarUtil.pointFromSettingsString(settingsSize);
                if (size != null)
                {
                    _view.setSize(size.x, size.y);
                }
            }

        }
    }

    private FindResultsTableEntry findNextReplaceEntry()
    {
        // the replace index is the view row, which may be different from the model index if
        // the user has sorted the table
        final FindResultsTableModel tableModel = _model.getFindResults();
        final int count = _view.getFindResultsTable().getRowCount();
        if (_replaceViewIndex < 0)
        {
            _replaceViewIndex = 0;
        }
        FindResultsTableEntry result = null;
        while (_replaceViewIndex < count)
        {
            int modelIndex = _view.getFindResultsTable().convertRowIndexToModel(_replaceViewIndex);
            final FindResultsTableEntry entry = tableModel.getEntry(modelIndex);
            if (entry.isUseInReplace() && !entry.isApplied())
            {
                result = entry;
                break;
            }
            ++_replaceViewIndex;
        }
        if (_replaceViewIndex >= count)
        {
            _replaceViewIndex = -1;
        }
        return result;
    }
}
