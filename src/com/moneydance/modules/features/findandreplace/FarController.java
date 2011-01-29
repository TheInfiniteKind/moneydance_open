/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.TransactionSet;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.JOptionPane;
import javax.swing.JTable;
import java.awt.Cursor;
import java.util.Enumeration;
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
 * @version 1.50
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
    public void loadData(final RootAccount data)
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
        _view.requestFocusInWindow();
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
        final RootAccount root = _model.getData();
        if ( root == null )
        {
            return;
        }

        FilterGroup filter = _model.buildTransactionFilter();

        // start with nothing
        _model.getFindResults().reset();

        // run the filter
        final int matched = filterTransactions(root, filter);
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
     * @param rootAccount The main data account
     * @param filter      The search filter.
     * @return The number of splits that matched
     */
    private int filterTransactions(RootAccount rootAccount, FilterGroup filter)
    {
        // build the list of transactions that match the criteria
        Set<Long> uniqueTxnIDs = new HashSet<Long>();
        final TransactionSet txnSet = rootAccount.getTransactionSet();
        final Enumeration txnEnum = txnSet.getAllTransactions();
        while (txnEnum.hasMoreElements())
        {
            // both parents and splits will be run through here
            final AbstractTxn txn = (AbstractTxn) txnEnum.nextElement();
            if (filter.containsTxn(txn))
            {
                // the report set should contain splits only, find any parents and add all of their splits
                if (txn instanceof ParentTxn)
                {
                    for (int ii = txn.getOtherTxnCount() - 1; ii >= 0; ii--)
                    {
                        final SplitTxn split = (SplitTxn) txn.getOtherTxn(ii);
                        final Long key = Long.valueOf(split.getTxnId());
                        if (uniqueTxnIDs.contains(key)) continue;
                        _model.getFindResults().add(split, false);
                        uniqueTxnIDs.add(key);
                    } // for ii
                }
                else
                {
                    // must be a split transaction, just add it
                    final SplitTxn split = (SplitTxn) txn;
                    final Long key = Long.valueOf(split.getTxnId());
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
            final RootAccount root = _model.getData();
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
                System.err.print("Error replacing data with Find and Replace: ");
                error.printStackTrace();
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
        _model.notifyAllListeners();
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
        final RootAccount root = _model.getData();
        if (root != null)
        {
            final Account acct = root.getAccountById(accountID);
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

    public RootAccount getRootAccount()
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

    void selectAccounts()
    {
        AccountSelectDialog dialog = new AccountSelectDialog(_view, this, _model.getData(),
                                                             _model.getAccountFilter());

        dialog.loadData();

        dialog.pack();
        dialog.setLocationRelativeTo(_view);
        dialog.setVisible(true);
        if (dialog.getResult() == JOptionPane.OK_OPTION)
        {
            // the account list was updated
            _model.accountListUpdated();
        }
        dialog.cleanUp();
    }

    void selectCategories()
    {
        AccountSelectDialog dialog = new AccountSelectDialog(_view, this, _model.getData(),
                                                             _model.getCategoryFilter());

        dialog.loadData();

        dialog.pack();
        dialog.setLocationRelativeTo(_view);
        dialog.setVisible(true);
        if (dialog.getResult() == JOptionPane.OK_OPTION)
        {
            // the category list was updated
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


    String getAccountListDisplay()
    {
        return _model.getAccountFilter().getDisplayString(this);
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
    String getCategoryListDisplay()
    {
        return _model.getCategoryFilter().getDisplayString(this);
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
        _model.setAmountRange(minimum, maximum);
    }
    long getAmountMinimum()
    {
        return _model.getAmountMinimum();
    }
    long getAmountMaximum()
    {
        return _model.getAmountMaximum();
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

    void setReplaceAmount(boolean replace)
    {
        _model.setReplaceAmount(replace);
    }
    boolean getReplaceAmount()
    {
        return _model.getReplaceAmount();
    }
    void setReplacementAmount(final long amount)
    {
        _model.setReplacementAmount(amount);
    }
    long getReplacementAmount()
    {
        return _model.getReplacementAmount();
    }

    void setReplaceDescription(boolean replace)
    {
        _model.setReplaceDescription(replace);
    }
    boolean getReplaceDescription()
    {
        return _model.getReplaceDescription();
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

    CurrencyType getCurrencyType()
    {
        final RootAccount root = _model.getData();
        if (root != null)
        {
            return root.getCurrencyType();
        }
        return null;
    }

    CurrencyTable getCurrencyTable()
    {
        final RootAccount root = _model.getData();
        if (root != null)
        {
            return root.getCurrencyTable();
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
            _view = new FarView(_model, getMDGUI(), getString(L10NFindAndReplace.TITLE));
            // hook up listeners
            _view.setController(this);
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
