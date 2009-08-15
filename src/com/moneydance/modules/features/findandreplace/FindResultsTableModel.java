/*
 * FindResultsTableModel.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 16, 2008
 * Time: 1:07:57 PM
 */


package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.TxnTagSet;
import com.moneydance.apps.md.model.TxnTag;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.view.gui.MDImages;
import com.moneydance.util.CustomDateFormat;

import javax.swing.table.AbstractTableModel;
import javax.swing.Icon;
import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.awt.Color;

/**
 * <p>Model for the results table.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.1
 * @since 1.0
 */
public class FindResultsTableModel extends AbstractTableModel
{
    static final int SEL_INDEX = 0;
    static final int USE_INDEX = 1;
    static final int ACCOUNT_INDEX = 2;
    static final int DATE_INDEX = 3;
    static final int DESCRIPTION_INDEX = 4;
    static final int TAG_INDEX = 5;
    static final int CATEGORY_INDEX = 6;
    static final int CLEARED_INDEX = 7;
    static final int AMOUNT_INDEX = 8;
    private static final int MEMO_INDEX = 9; // not shown except in tooltip

    private static final ParentTxn BLANK_TRANSACTION =
            new ParentTxn(
                    0,                           // int date
                    0,                           // int taxDate
                    100,                         // long dateEntered
                    "Hello",                     // java.lang.String checkNumber
                    null,                        // Account account
                    "Goodbye",                   // java.lang.String description
                    "hello",                     // java.lang.String memo
                    0,                           // long id
                    AbstractTxn.STATUS_CLEARED); // byte status
    private static final FindResultsTableEntry BLANK_ENTRY =
            new FindResultsTableEntry(BLANK_TRANSACTION, false);

    private static final String DEFAULT_DATE_FORMAT = "MM/dd/YYYY";
    private static final char DEFAULT_DECIMAL_CHAR = '.';

    private TxnTagSet _userTagSet;
    private final List<FindResultsTableEntry> _data;
    private final List<String> _columns;
    private final Set<Long> _foundIDs;

    private final IFindAndReplaceController _controller;
    private final CustomDateFormat _dateFormat;
    private final char _decimalChar;

    // commands to apply to each transaction
    private List<ReplaceCommand> _commands;

    private final Icon _statusReconciling;
    private final Icon _statusCleared;

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Construction
    //////////////////////////////////////////////////////////////////////////////////////////////

    FindResultsTableModel(final IFindAndReplaceController controller)
    {
        super();
        
        _data = new ArrayList<FindResultsTableEntry>();
        _columns = new ArrayList<String>();
        _foundIDs = new HashSet<Long>();
        _controller = controller;

        UserPreferences preferences = null;
        if (_controller.getMDMain() != null)
        {
            preferences = _controller.getMDMain().getPreferences();
        }
        if (preferences != null)
        {
            _dateFormat = _controller.getMDMain().getPreferences().getShortDateFormatter();
            _decimalChar = _controller.getMDMain().getPreferences().getDecimalChar();
        }
        else
        {
            _dateFormat = new CustomDateFormat(DEFAULT_DATE_FORMAT);
            _decimalChar = DEFAULT_DECIMAL_CHAR;
        }
        buildColumns(_controller);

        _statusReconciling = _controller.getMDGUI().getImages().getIcon(
                MDImages.TXN_STAT_RECONCILING);
        _statusCleared = _controller.getMDGUI().getImages().getIcon(
                MDImages.TXN_STAT_CLEARED);

        _commands = null;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Package Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    FindResultsTableEntry getEntry(final int index)
    {
        return _data.get(index);
    }
    
    void setUserTagSet(final TxnTagSet userTags)
    {
        _userTagSet = userTags;
    }

    void setCommandList(final List<ReplaceCommand> commands)
    {
        _commands = commands;
    }

    void reset()
    {
        _data.clear();
        _foundIDs.clear();
    }

    void addBlankTransaction()
    {
        reset();
        _data.add(BLANK_ENTRY);
        fireTableDataChanged();
    }
    
    boolean isBlankEntry(FindResultsTableEntry entry)
    {
        if (entry == null)
        {
            return true;
        }
        return entry.getParentTxn().equals(BLANK_TRANSACTION);
    }


    void add(final AbstractTxn txn, final boolean notify)
    {
        // do not add the same transaction twice -- the parent transaction and its first split
        boolean addOk = true;

        if (txn instanceof ParentTxn)
        {
            final ParentTxn parent = (ParentTxn)txn;
            if ((parent.getSplitCount() == 1) &&
                   (_foundIDs.contains(Long.valueOf(parent.getSplit(0).getTxnId()))))
            {
                // existing is the only split, new one is same as the parent
                addOk = false;
            }
        }
        if (txn instanceof SplitTxn)
        {
            //  cover the case where the split comes after the parent
            Long key = Long.valueOf(txn.getParentTxn().getTxnId());
            if (_foundIDs.contains(key) && txn.getParentTxn().getSplitCount() == 1)
            {
                // new one is the only child of the parent, which is already in there. However,
                // each entry already has both parent and split so there is no need to do anything,
                // the complete transaction is already entered.
                addOk = false;
            }
        }

        if (addOk)
        {
            final int index = _data.size();
            _data.add(new FindResultsTableEntry(txn));
            _foundIDs.add(Long.valueOf(txn.getTxnId()));
            if (notify)
            {
                fireTableRowsInserted(index, index);
            }
        }
    }

    String getToolTipText(final int rowIndex)
    {
        final FindResultsTableEntry entry = _data.get(rowIndex);
        if (entry == null)
        {
            return null;
        }

        final AbstractTxn txn;
        if (entry.isSplitPrimary())
        {
            txn = entry.getSplitTxn();
        }
        else
        {
            txn = entry.getParentTxn();
        }
        if ((txn == null) || (txn.equals(BLANK_TRANSACTION)))
        {
            return null;
        }

        StringBuffer buffer = new StringBuffer();

        buffer.append(N12EFindAndReplace.HTML_BEGIN);

        // start table
        buffer.append(N12EFindAndReplace.TABLE_BEGIN);

        // date row
        buffer.append(N12EFindAndReplace.ROW_BEGIN);
        buffer.append(N12EFindAndReplace.COL_BEGIN_RIGHT);
        buffer.append(FarUtil.getLabelText(_controller,
                L10NFindAndReplace.RESULTS_COLUMN_DATE));
        buffer.append(N12EFindAndReplace.NBSPACE);
        buffer.append(N12EFindAndReplace.COL_END);

        buffer.append(N12EFindAndReplace.COL_BEGIN);
        buffer.append(getTxnDateDisplay(txn));
        buffer.append(N12EFindAndReplace.COL_END);
        buffer.append(N12EFindAndReplace.ROW_END);

        // account row
        buffer.append(N12EFindAndReplace.ROW_BEGIN);
        buffer.append(N12EFindAndReplace.COL_BEGIN_RIGHT);
        buffer.append(FarUtil.getLabelText(_controller,
                L10NFindAndReplace.RESULTS_COLUMN_ACCOUNT));
        buffer.append(N12EFindAndReplace.NBSPACE);
        buffer.append(N12EFindAndReplace.COL_END);

        buffer.append(N12EFindAndReplace.COL_BEGIN);
        buffer.append(FarUtil.getTransactionAccountName(txn));
        buffer.append(N12EFindAndReplace.COL_END);
        buffer.append(N12EFindAndReplace.ROW_END);

        // check # row
        buffer.append(N12EFindAndReplace.ROW_BEGIN);
        buffer.append(N12EFindAndReplace.COL_BEGIN_RIGHT);
        buffer.append(FarUtil.getLabelText(_controller,
                L10NFindAndReplace.RESULTS_CHECKNO_LABEL));
        buffer.append(N12EFindAndReplace.NBSPACE);
        buffer.append(N12EFindAndReplace.COL_END);

        buffer.append(N12EFindAndReplace.COL_BEGIN);
        buffer.append(FarUtil.getTransactionCheckNo(txn));
        buffer.append(N12EFindAndReplace.COL_END);
        buffer.append(N12EFindAndReplace.ROW_END);

        // description row
        buffer.append(N12EFindAndReplace.ROW_BEGIN);
        buffer.append(N12EFindAndReplace.COL_BEGIN_RIGHT);
        buffer.append(FarUtil.getLabelText(_controller,
                L10NFindAndReplace.RESULTS_COLUMN_DESCRIPTION));
        buffer.append(N12EFindAndReplace.NBSPACE);
        buffer.append(N12EFindAndReplace.COL_END);

        buffer.append(N12EFindAndReplace.COL_BEGIN);
        buffer.append(getTxnDescriptionDisplay(txn, entry));
        buffer.append(N12EFindAndReplace.COL_END);
        buffer.append(N12EFindAndReplace.ROW_END);

        // memo row
        buffer.append(N12EFindAndReplace.ROW_BEGIN);
        buffer.append(N12EFindAndReplace.COL_BEGIN_RIGHT);
        buffer.append(FarUtil.getLabelText(_controller, L10NFindAndReplace.REPLACE_MEMO_LABEL));
        buffer.append(N12EFindAndReplace.NBSPACE);
        buffer.append(N12EFindAndReplace.COL_END);

        buffer.append(N12EFindAndReplace.COL_BEGIN);
        buffer.append(getTxnMemoDisplay(txn, entry));
        buffer.append(N12EFindAndReplace.COL_END);
        buffer.append(N12EFindAndReplace.ROW_END);

        // category row
        buffer.append(N12EFindAndReplace.ROW_BEGIN);
        buffer.append(N12EFindAndReplace.COL_BEGIN_RIGHT);
        buffer.append(FarUtil.getLabelText(_controller,
                L10NFindAndReplace.RESULTS_COLUMN_CATEGORY));
        buffer.append(N12EFindAndReplace.NBSPACE);
        buffer.append(N12EFindAndReplace.COL_END);

        buffer.append(N12EFindAndReplace.COL_BEGIN);
        buffer.append(getTxnCategoryDisplay(txn, entry));
        buffer.append(N12EFindAndReplace.COL_END);
        buffer.append(N12EFindAndReplace.ROW_END);

        // amount row
        buffer.append(N12EFindAndReplace.ROW_BEGIN);
        buffer.append(N12EFindAndReplace.COL_BEGIN_RIGHT);
        buffer.append(FarUtil.getLabelText(_controller,
                L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        buffer.append(N12EFindAndReplace.NBSPACE);
        buffer.append(N12EFindAndReplace.COL_END);

        buffer.append(N12EFindAndReplace.COL_BEGIN);
        final long value = getTxnAmountValue(txn, entry, AMOUNT_INDEX);
        final String amountText = txn.getAccount().getCurrencyType().
                formatSemiFancy(value, _decimalChar);
        if (value < 0)
        {
            final Color negColor = _controller.getMDGUI().getColors().negativeBalFG;
            buffer.append(String.format(N12EFindAndReplace.COLOR_BEGIN_FMT,
                    Integer.valueOf(negColor.getRed()),
                    Integer.valueOf(negColor.getGreen()),
                    Integer.valueOf(negColor.getBlue())));
            buffer.append(amountText);
            buffer.append(N12EFindAndReplace.COLOR_END);
        }
        else
        {
            buffer.append(amountText);
        }
        buffer.append(N12EFindAndReplace.COL_END);
        buffer.append(N12EFindAndReplace.ROW_END);

        buffer.append(N12EFindAndReplace.TABLE_END);
        buffer.append(N12EFindAndReplace.HTML_END);

        return buffer.toString();
    }

    String getAmountText(final AbstractTxn txn, final long value)
    {
        final Account account;
        if (txn != null)
        {
            account = txn.getAccount();
        }
        else
        {
            account = _controller.getDefaultAccount();
        }
        return account.getCurrencyType().formatSemiFancy(value, _decimalChar);
    }

    long getAmount(final int index)
    {
        final FindResultsTableEntry entry = _data.get(index);
        final ParentTxn parent = entry.getParentTxn();
        if (parent == null)
        {
            return 0;
        }

        final SplitTxn split = entry.getSplitTxn();
        long value;
        if (entry.isSplitPrimary())
        {
            value = getTxnAmountValue(split, entry, AMOUNT_INDEX);
        }
        else
        {
            value = getTxnAmountValue(parent, entry, AMOUNT_INDEX);
        }
        return value;
    }

    int getDateInt(final int index)
    {
        final FindResultsTableEntry entry = _data.get(index);
        final ParentTxn parent = entry.getParentTxn();
        if (parent == null)
        {
            return 0;
        }
        return FarUtil.getTransactionDate(parent); // YYYYMMDD
    }

    int getClearedInt(final int index)
    {
        final FindResultsTableEntry entry = _data.get(index);
        final ParentTxn parent = entry.getParentTxn();
        if (parent == null)
        {
            return 0;
        }
        return parent.getStatus();
    }

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  TableModel
    //////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Returns false.  This is the default implementation for all cells.
     *
     * @param rowIndex    the row being queried
     * @param columnIndex the column being queried
     * @return false
     */
    @Override
    public boolean isCellEditable(int rowIndex, int columnIndex)
    {
        return (columnIndex == USE_INDEX) || (columnIndex == SEL_INDEX);
    }

    /**
     * Returns the number of rows in the model. A
     * <code>JTable</code> uses this method to determine how many rows it
     * should display.  This method should be quick, as it
     * is called frequently during rendering.
     *
     * @return the number of rows in the model
     * @see #getColumnCount
     */
    public int getRowCount()
    {
        return _data.size();
    }

    /**
     * Returns the number of columns in the model. A
     * <code>JTable</code> uses this method to determine how many columns it
     * should create and display by default.
     *
     * @return the number of columns in the model
     * @see #getRowCount
     */
    public int getColumnCount()
    {
        return _columns.size();
    }


    @Override
    public Class<?> getColumnClass(int columnIndex)
    {
        if (columnIndex == USE_INDEX)
        {
            return Boolean.class;
        }
        return String.class;
    }

    /**
     * Returns the value for the cell at <code>columnIndex</code> and
     * <code>rowIndex</code>.
     *
     * @param    rowIndex    the row whose value is to be queried
     * @param    columnIndex the column whose value is to be queried
     * @return the value Object at the specified cell
     */
    public Object getValueAt(int rowIndex, int columnIndex)
    {
        final FindResultsTableEntry entry = _data.get(rowIndex);
        final ParentTxn parent = entry.getParentTxn();
        if (parent == null)
        {
            return null;
        }

        final SplitTxn split = entry.getSplitTxn();

        String result;
        try
        {
            if (columnIndex == SEL_INDEX)
            {
                return Integer.valueOf(rowIndex + 1);
            }

            if (parent.equals(BLANK_TRANSACTION))
            {
                if (columnIndex == DESCRIPTION_INDEX)
                {
                    return _controller.getString(L10NFindAndReplace.NONE);
                }
                if (columnIndex == USE_INDEX)
                {
                    return Boolean.FALSE;
                }
                return N12EFindAndReplace.EMPTY;
            }

            result = N12EFindAndReplace.EMPTY;
            switch (columnIndex)
            {
                case ACCOUNT_INDEX:
                {
                    // parent is preferred for the account
                    result = FarUtil.getTransactionAccountName(parent);
                    break;
                }
                case DATE_INDEX:
                {
                    // parent is preferred for the date
                    result = getTxnDateDisplay(parent);
                    break;
                }
                case DESCRIPTION_INDEX:
                {
                    // description depends upon whether it was a split or a parent
                    if (entry.isSplitPrimary())
                    {
                        result = getTxnDescriptionDisplay(split, entry);
                    }
                    else
                    {
                        result = getTxnDescriptionDisplay(parent, entry);
                    }
                    break;
                }
                case TAG_INDEX:
                {
                    // tags are always split-related
                    result = getTxnTagDisplay(split, entry);
                    break;
                }
                case CATEGORY_INDEX:
                {
                    // category is always split-related
                    result = getTxnCategoryDisplay(split, entry);
                    break;
                }
                case CLEARED_INDEX:
                {
                    switch (parent.getStatus())
                    {
                        case AbstractTxn.STATUS_CLEARED:
                            return _statusCleared;
                        case AbstractTxn.STATUS_RECONCILING:
                            return _statusReconciling;
                        default:
                            result = N12EFindAndReplace.SPACE;
                    }
                    break;
                }
                case AMOUNT_INDEX:
                {
                    long value = getAmount(rowIndex);

                    // for expense categories, a positive value should be negative, so invert
                    result += getTxnAmountDisplay(parent, value);
                    break;
                }
                case USE_INDEX:
                {
                    return Boolean.valueOf(entry.isUseInReplace());
                }
                default:
                {
                    return "?";
                }
            } // switch columnIndex
        } // try
        catch (Exception e)
        {
            result = "XC";
        }

        return result;
    }


    @Override
    public void setValueAt(Object aValue, int rowIndex, int columnIndex)
    {
        super.setValueAt(aValue, rowIndex, columnIndex);
        if ((columnIndex == USE_INDEX) && (aValue instanceof Boolean))
        {
            final FindResultsTableEntry entry = _data.get(rowIndex);
            entry.setUseInReplace(((Boolean)aValue).booleanValue());
            // do the default, which updates the row sorter
            fireTableRowsUpdated(rowIndex, rowIndex);
            // also update our own view
            _controller.updateRow(rowIndex);
        }
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////
    
    private Long getCommandValue(final FindResultsTableEntry entry)
    {
        Long value = null;
        if ((_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransaction(entry.getSplitTxn());
                if (command.getPreviewAmount() != null)
                {
                    value = command.getPreviewAmount();
                }
            }
        }
        return value;
    }

    private long getTxnAmountValue(final AbstractTxn txn, final FindResultsTableEntry entry,
                                   final int columnIndex)
    {
        long value = txn.getValue();

        Long commandValue = getCommandValue(entry);
        if (commandValue != null)
        {
            value = commandValue.longValue();
            entry.addModifiedColumn(columnIndex);
        }
        // if the transaction is under a category account, negate the value because it is the
        // 'other side' to an actual transaction
        final Account account = txn.getAccount();
        if (account != null)
        {
            int type = account.getAccountType();
            if ((type == Account.ACCOUNT_TYPE_EXPENSE) || (type == Account.ACCOUNT_TYPE_INCOME))
            {
                value = -value;
            }
        }
        return value;
    }

    private String getTxnDescriptionDisplay(final AbstractTxn txn,
                                            final FindResultsTableEntry entry)
    {
        String description = txn.getDescription();
        if ((_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransaction(txn);
                if (command.getPreviewDescription() != null)
                {
                    description = command.getPreviewDescription();
                    entry.addModifiedColumn(DESCRIPTION_INDEX);
                }
            }
        }
        return description;
    }

    private String getTxnMemoDisplay(final AbstractTxn txn,
                                     final FindResultsTableEntry entry)
    {
        ParentTxn transaction;
        if (txn instanceof ParentTxn)
        {
            transaction = (ParentTxn)txn;
        }
        else if (txn instanceof SplitTxn)
        {
            transaction = txn.getParentTxn();
        }
        else
        {
            return N12EFindAndReplace.EMPTY;
        }

        String memo = transaction.getMemo();
        if ((_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransaction(txn);
                if (command.getPreviewMemo() != null)
                {
                    memo = command.getPreviewMemo();
                    entry.addModifiedColumn(MEMO_INDEX);
                }
            }
        }
        return memo;
    } // getTxnMemoDisplay()

    private String getTxnTagDisplay(final AbstractTxn txn,
                                    final FindResultsTableEntry entry)
    {
        // user tags are associated with splits only
        TxnTag[] tags = FarUtil.getTransactionTags(txn, _userTagSet);

        // TODO: this won't work with more than one command -- fix so that tags are applied in succession
        if ((_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransaction(txn);
                if (command.getPreviewTags() != null)
                {
                    tags = command.getPreviewTags();
                    entry.addModifiedColumn(TAG_INDEX);
                }
            }
        }

        // checks for valid transaction and for a non-null user tag set
        if (tags.length == 0)
        {
            // no tags associated with parent transactions with more than one split
            return N12EFindAndReplace.EMPTY;
        }

        StringBuffer buffer = new StringBuffer(N12EFindAndReplace.EMPTY);
        for (final TxnTag tag : tags)
        {
            if (buffer.length() > 0)
            {
                buffer.append(N12EFindAndReplace.COMMA_SEPARATOR);
            }

            buffer.append(tag.getName());
        }
        return buffer.toString();
    }


    private String getTxnCategoryDisplay(final AbstractTxn txn,
                                  final FindResultsTableEntry entry)
    {
        Account category = getTxnCategory(txn, entry);

        final String result;
        if (category != null)
        {
            result = category.getAccountName();
        }
        else if (txn instanceof ParentTxn)
        {
            // for the parent, check if we have only 1 split. If we do, use that. If we have more,
            // show the words '- N splits -'
            StringBuffer buffer = new StringBuffer(_controller.getString(L10NFindAndReplace.SPLIT_1));
            buffer.append(N12EFindAndReplace.SPACE);
            buffer.append(((ParentTxn)txn).getSplitCount());
            buffer.append(N12EFindAndReplace.SPACE);
            buffer.append(_controller.getString(L10NFindAndReplace.SPLIT_2));
            result = buffer.toString();
        }
        else
        {
            result = N12EFindAndReplace.EMPTY;
        }
        return result;
    }

    private Account getTxnCategory(final AbstractTxn txn,
                                  final FindResultsTableEntry entry)
    {
        Account category = FarUtil.getTransactionCategory(txn);
        if ((category != null) && (_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransaction(txn);
                if (command.getPreviewCategory() != null)
                {
                    category = command.getPreviewCategory();
                    entry.addModifiedColumn(CATEGORY_INDEX);
                }
            }
        }
        return category;
    }

    private String getTxnDateDisplay(final AbstractTxn txn)
    {
        final int encoded = FarUtil.getTransactionDate(txn); // YYYYMMDD
        if (encoded < 0)
        {
            return N12EFindAndReplace.EMPTY;
        }
        return _dateFormat.format(encoded);
    }

    private String getTxnAmountDisplay(final AbstractTxn txn, final long value)
    {
        return getAmountText(txn, value);
    }

    /**
     * Returns a default name for the column using spreadsheet conventions:
     * A, B, C, ... Z, AA, AB, etc.  If <code>column</code> cannot be found,
     * returns an empty string.
     *
     * @param column the column being queried
     * @return a string containing the default name of <code>column</code>
     */
    @Override
    public String getColumnName(final int column)
    {
        return _columns.get(column);
    }

    /**
     * Returns a column given its name.
     * Implementation is naive so this should be overridden if
     * this method is to be called often. This method is not
     * in the <code>TableModel</code> interface and is not used by the
     * <code>JTable</code>.
     *
     * @param columnName string containing name of column to be located
     * @return the column with <code>columnName</code>, or -1 if not found
     */
    @Override
    public int findColumn(final String columnName)
    {
        for (int index = 0; index < _columns.size(); index++)
        {
            if (_columns.get(index).compareTo(columnName) == 0)
            {
                return index;
            }
        }
        return -1;
    }

    //////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    private void buildColumns(final IResourceProvider resources)
    {
        // select
        _columns.add(N12EFindAndReplace.EMPTY);
        // check (use)
        _columns.add(N12EFindAndReplace.EMPTY);
        _columns.add(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_ACCOUNT));
        _columns.add(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_DATE));
        _columns.add(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_DESCRIPTION));
        _columns.add(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_TAG));
        _columns.add(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_CATEGORY));
        _columns.add(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_CLEARED));
        _columns.add(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        // memo (not shown)
        _columns.add(N12EFindAndReplace.EMPTY);
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Inner Classes
    ///////////////////////////////////////////////////////////////////////////////////////////////

}
