package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.TransactionSet;
import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.CurrencyTable;

import javax.swing.JOptionPane;
import java.util.Enumeration;
import java.util.List;
import java.util.ArrayList;
import java.text.DecimalFormatSymbols;
import java.awt.Image;

/**
 * <p>Controller for the plugin component for Find and Replace. This class brokers method calls
 * and performs some of the main functions of the plugin.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public class FarController implements IFindAndReplaceController
{
    private FindAndReplace _host;
    private final FarModel _model;
    private final FarView _view;

    private int _replaceIndex;
    private final List<ReplaceCommand> _commands = new ArrayList<ReplaceCommand>();

    private String _initialFreeText = null;

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Construction
    //////////////////////////////////////////////////////////////////////////////////////////////

    FarController(final FarModel model, final FarView view)
    {
        _model = model;
        _view = view;
        _replaceIndex = -1;
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
        _model.setData(null);
    }

    /**
     * Display the dialog/frame on the screen.
     */
    public void show()
    {
        _view.layoutUI();
        _view.setVisible( true );
        _view.toFront();
        _view.requestFocus();
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

    public void hide()
    {
        _view.setVisible( false );
        _host.cleanUp();
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
        final TransactionSet txnSet = root.getTransactionSet();
        final Enumeration txnEnum = txnSet.getAllTransactions();
        int matched = 0;
        while (txnEnum.hasMoreElements())
        {
            // both parents and splits will be run through here, we do not need to dig through
            // the splits ourselves
            final AbstractTxn txnBase = (AbstractTxn)txnEnum.nextElement();
            if (filter.containsTxn(txnBase))
            {
                _model.getFindResults().add(txnBase, false);
                ++matched;
            }
        }

        if (matched > 0)
        {
            _model.getFindResults().fireTableDataChanged();
        }
        else
        {
            _model.getFindResults().addBlankTransaction();
        }
        _model.tableUpdated();

        // reset for the replace operation
        _replaceIndex = -1;
        _commands.clear(); // currently only support one command at a time
        _view.getFindResultsTable().clearSelection();
        _model.resetApply();
        
    } // find()

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
            int modelIndex = _view.getFindResultsTable().convertRowIndexToModel(_replaceIndex);
            _model.getFindResults().fireTableRowsUpdated(modelIndex, modelIndex);
            _view.getFindResultsTable().setRowSelectionInterval(_replaceIndex, _replaceIndex);
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
        FindResultsTableEntry entry = findNextReplaceEntry();
        while (entry != null)
        {
            entry.applyCommand();

            // next iteration
            entry = findNextReplaceEntry();
        }

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
            if (getMDGUI() != null)
            {
                getMDGUI().setSuspendRefresh(true);
            }
            
            final FindResultsTableModel results = _model.getFindResults();
            final int count = results.getRowCount();
            boolean changed = false;
            for (int rowIndex = 0; rowIndex < count; rowIndex++)
            {
                final FindResultsTableEntry entry = results.getEntry(rowIndex);
                if (entry.isApplied() && entry.isUseInReplace())
                {
                    for (final ReplaceCommand command : _commands)
                    {
                        if (entry.isSplitPrimary())
                        {
                            command.setTransaction(entry.getSplitTxn());
                        }
                        else
                        {
                            command.setTransaction(entry.getParentTxn());
                        }

                        changed |= command.execute();
                    }
                } // if use this entry
            } // for rowIndex

            if (changed)
            {
                // flag to MoneyDance that the file has been modified
                _model.getData().setDirtyFlag();
                if (getMDGUI() != null)
                {
                    getMDGUI().setSuspendRefresh(false);
                }
                _model.getData().refreshAccountBalances();
            }

        } // if dirty
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

    public Account getDefaultAccount()
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

    void setRequireAccountFilter(final boolean require)
    {
        _model.setRequireAccountFilter(require);
    }
    boolean getRequireAccountFilter()
    {
        return _model.getRequireAccountFilter();
    }

    void setUseCategoryFilter(final boolean use)
    {
        _model.setUseCategoryFilter(use);
    }
    boolean getUseCategoryFilter()
    {
        return _model.getUseCategoryFilter();
    }
    void setRequireCategoryFilter(final boolean require)
    {
        _model.setRequireCategoryFilter(require);
    }
    boolean getRequireCategoryFilter()
    {
        return _model.getRequireCategoryFilter();
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
    void setRequireAmountFilter(final boolean require)
    {
        _model.setRequireAmountFilter(require);
    }
    boolean getRequireAmountFilter()
    {
        return _model.getRequireAmountFilter();
    }
    void setAmountRange(final long minimum, final long maximum)
    {
        _model.setAmountRange(minimum, maximum);
    }

    void setUseDateFilter(final boolean use)
    {
        _model.setUseDateFilter(use);
    }
    boolean getUseDateFilter()
    {
        return _model.getUseDateFilter();
    }
    void setRequireDateFilter(final boolean require)
    {
        _model.setRequireDateFilter(require);
    }
    boolean getRequireDateFilter()
    {
        return _model.getRequireDateFilter();
    }
    void setDateRange(final int minimum, final int maximum)
    {
        _model.setDateRange(minimum, maximum);
    }

    void setUseFreeTextFilter(final boolean use)
    {
        _model.setUseFreeTextFilter(use);
    }
    boolean getUseFreeTextFilter()
    {
        return _model.getUseFreeTextFilter();
    }
    void setRequireFreeTextFilter(final boolean require)
    {
        _model.setRequireFreeTextFilter(require);
    }
    boolean getRequireFreeTextFilter()
    {
        return _model.getRequireFreeTextFilter();
    }
    void setFreeTextMatch(final String descriptionMatch)
    {
        _model.setFreeTextMatch(descriptionMatch);
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
    void setRequireTagsFilter(final boolean require)
    {
        _model.setRequireTagsFilter(require);
    }
    boolean getRequireTagsFilter()
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


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private FindResultsTableEntry findNextReplaceEntry()
    {
        // the replace index is the view row, which may be different from the model index if
        // the user has sorted the table
        ++_replaceIndex;
        final FindResultsTableModel tableModel = _model.getFindResults();
        final int count = _view.getFindResultsTable().getRowCount();

        FindResultsTableEntry result = null;
        while (_replaceIndex < count)
        {
            int modelIndex = _view.getFindResultsTable().convertRowIndexToModel(_replaceIndex);
            final FindResultsTableEntry entry = tableModel.getEntry(modelIndex);
            if (entry.isUseInReplace())
            {
                result = entry;
                break;
            }
            ++_replaceIndex;
        }
        return result;
    }

}
