/*************************************************************************\
* Copyright (C) 2009-2013 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.view.gui.MDImages;
import com.infinitekind.util.CustomDateFormat;

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
 * @author Kevin Menningen
 * @version Build 94
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
    static final int MEMO_INDEX = 9;           // not shown except in tooltip and export
    static final int SHARES_INDEX = 10;        // not shown except in export to clipboard
    static final int CHECK_INDEX = 11;         // not shown except in export to clipboard
    static final int FULL_CATEGORY_INDEX = 12; // not shown except in export to clipboard
    static final int MEMO_PARENT_INDEX = 13;   // not shown except in export to clipboard
    static final int OTHER_AMOUNT_INDEX = 14;  // not shown except in export to clipboard

    private static final ParentTxn BLANK_TRANSACTION = 
      ParentTxn.makeParentTxn(null,
                              0,                           // int date
                              0,                           // int taxDate
                              100,                         // long dateEntered
                              "Hello",                     // java.lang.String checkNumber
                              null,                        // Account account
                              "Goodbye",                   // java.lang.String description
                              "hello",                     // java.lang.String memo
                              0,                           // long id
                              AbstractTxn.STATUS_CLEARED); // byte status
    private static final FindResultsTableEntry BLANK_ENTRY = new FindResultsTableEntry(BLANK_TRANSACTION, false, null);

    private static final String DEFAULT_DATE_FORMAT = "MM/dd/YYYY";
    private static final char DEFAULT_DECIMAL_CHAR = '.';

    private List<String> _userTagSet;
    /** The full set of data, including all splits. */
    private final List<FindResultsTableEntry> _splitData;
    /** Display data. Can be the full splits data or could be just one entry per parent. */
    private final List<FindResultsTableEntry> _data;
    private final List<String> _columns;

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
        _splitData = new ArrayList<FindResultsTableEntry>();
        _data = new ArrayList<FindResultsTableEntry>();
        _columns = new ArrayList<String>();
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

    char getDecimalChar()
    {
        return _decimalChar;
    }

    void refresh()
    {
        _data.clear();
        final Set<String> foundIDs = new HashSet<String>(_splitData.size());
        if (_controller.getShowParents())
        {
            // build a smaller list of entries containing only one entry per parent transaction
            for (FindResultsTableEntry entry : _splitData)
            {
                final String parentId = entry.getParentTxn().getUUID();
                if (!foundIDs.contains(parentId)) {
                    // add the first one found in the splits list, all others will be ignored
                    _data.add(entry);
                    foundIDs.add(parentId);
                }
            }
        }
        else
        {
            // the list of splits is exactly what we show
            _data.addAll(_splitData);
        }
        fireTableDataChanged();
    }

    FindResultsTableEntry getEntry(final int index)
    {
        return _data.get(index);
    }
    
    void setUserTagSet(final List<String> userTags)
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
        _splitData.clear();
    }

    void addBlankTransaction()
    {
        reset();
        _splitData.add(BLANK_ENTRY);
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


    void add(final SplitTxn txn, final boolean notify)
    {
        final int index = _splitData.size();
        _splitData.add(new FindResultsTableEntry(txn, _controller.getCurrencyType()));
        if (notify)
        {
            fireTableRowsInserted(index, index);
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
        if (_controller.getShowParents())
        {
            txn = entry.getParentTxn();
        }
        else
        {
            txn = entry.getSplitTxn();
        }
        if ((txn == null) || (txn.equals(BLANK_TRANSACTION)))
        {
            return null;
        }

        StringBuilder buffer = new StringBuilder();

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
        buffer.append(getTxnCheckDisplay(txn, entry));
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
        buffer.append(getTxnCategoryDisplay(txn, entry, true));
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
        final TxnValue value = getTxnAmount(txn, entry, AMOUNT_INDEX);
        // For stocks and the like, this will display in shares versus the base currency. Because
        // the table shows the base currency in the amount column, the tooltip can provide
        // additional information in this way.
        final String amountText = getAmountTooltipText(txn, value);
        if (value.value < 0)
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

    private String getAmountTooltipText(AbstractTxn txn, TxnValue value)
    {
        // start with the default display
        StringBuilder result = new StringBuilder(getAmountText(null, value));
        // if a split, or if a parent with only one split, we can tack on the other side's currency
        CurrencyType otherCurrency = (txn.getOtherTxnCount() == 1) ?
                txn.getOtherTxn(0).getAccount().getCurrencyType() : null;
        // by default the table shows base currency, so include that into the mix
        CurrencyType baseCurrency = _controller.getCurrencyType();
        if (baseCurrency == null)
        {
            return result.toString();
        }
        if (!baseCurrency.equals(value.currency))
        {
            // show the base currency value
            result.append(" (");
            result.append(baseCurrency.formatFancy(
                    CurrencyUtil.convertValue(value.value, value.currency, baseCurrency, txn.getDateInt()),
                    _decimalChar));
            if ((otherCurrency != null) && !otherCurrency.equals(value.currency) && !otherCurrency.equals(baseCurrency))
            {
                // include the other side's currency too
                result.append(" | ");
                result.append(otherCurrency.formatFancy(
                        CurrencyUtil.convertValue(value.value, value.currency, otherCurrency, txn.getDateInt()),
                        _decimalChar));
            }
            result.append(')');
        }
        else if ((otherCurrency != null) && !otherCurrency.equals(value.currency))
        {
            // show the other side's currency
            result.append(" (");
            result.append(otherCurrency.formatFancy(
                    CurrencyUtil.convertValue(value.value, value.currency, otherCurrency, txn.getDateInt()),
                    _decimalChar));
            result.append(')');
        }
        return result.toString();
    }

    String getAmountText(final CurrencyType displayCurrency, final TxnValue txnValue)
    {
        if (displayCurrency != null)
        {
            long displayValue = CurrencyUtil.convertValue(txnValue.value, txnValue.currency, displayCurrency, txnValue.date);
            return displayCurrency.formatFancy(displayValue, _decimalChar);
        }
        return txnValue.currency.formatFancy(txnValue.value, _decimalChar);
    }

    long getAmountInBaseCurrency(final int index)
    {
        final CurrencyType baseCurrency = _controller.getCurrencyType();
        return getAmountInCurrency(index, baseCurrency);
    }

    boolean isNegative(final int index)
    {
        final FindResultsTableEntry entry = _data.get(index);
        final ParentTxn parent = entry.getParentTxn();
        if ((parent == null) || BLANK_TRANSACTION.equals(parent))
        {
            return false;
        }

        final SplitTxn split = entry.getSplitTxn();
        final Account.AccountType type = _controller.getShowParents() ? parent.getAccount().getAccountType() : split.getAccount().getAccountType();
        final boolean flip = ((type == Account.AccountType.EXPENSE) || (type == Account.AccountType.INCOME));
        if (_controller.getShowParents())
        {
            return flip ? (parent.getValue() > 0) : (parent.getValue() < 0);
        }
        return flip ? (split.getValue() > 0) : (split.getValue() < 0);
    }

    private long getAmountInCurrency(int index, CurrencyType outputCurrency)
    {
        final FindResultsTableEntry entry = _data.get(index);
        final ParentTxn parent = entry.getParentTxn();
        if ((parent == null) || BLANK_TRANSACTION.equals(parent))
        {
            return 0;
        }

        final SplitTxn split = entry.getSplitTxn();
        TxnValue value;
        if (_controller.getShowParents())
        {
            value = getTxnAmount(parent, entry, AMOUNT_INDEX);
        }
        else
        {
            value = getTxnAmount(split, entry, AMOUNT_INDEX);
        }
        return CurrencyUtil.convertValue(value.value, value.currency, outputCurrency, value.date);
    }

    CurrencyType getDisplayCurrency(final int index)
    {
        final FindResultsTableEntry entry = _data.get(index);
        // if we've replaced the value, return the replacement currency
        CurrencyType displayCurrency = getCommandCurrency(entry);
        return (displayCurrency != null) ? displayCurrency : _controller.getCurrencyType();
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
        final AbstractTxn primaryTxn;
        if (_controller.getShowParents())
        {
            primaryTxn = parent;
        }
        else
        {
            primaryTxn = split;
        }

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
                    // parent gives the 'flip side' account for splits - the 'from' account
                    result = FarUtil.getTransactionAccountName(parent);
                    break;
                }
                case DATE_INDEX:
                {
                    // parent is preferred for the date, either would work
                    result = getTxnDateDisplay(parent);
                    break;
                }
                case DESCRIPTION_INDEX:
                {
                    // description depends upon whether it was a split or a parent
                    result = getTxnDescriptionDisplay(primaryTxn, entry);
                    break;
                }
                case TAG_INDEX:
                {
                    // tags are normally split-related but can be put on parents
                    result = getTxnTagDisplay(primaryTxn, entry);
                    break;
                }
                case CATEGORY_INDEX:
                case FULL_CATEGORY_INDEX:
                {
                    // category displays the 'to' account or the # of splits for parents > 1 split
                    result = getTxnCategoryDisplay(primaryTxn, entry,
                                                   (columnIndex == FULL_CATEGORY_INDEX));
                    break;
                }
                case CLEARED_INDEX:
                {
                    // only parents are really marked 'cleared' at this point
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
                    // for expense categories, a positive value should be negative, so invert
                    TxnValue txnValue = getTxnAmount(primaryTxn, entry, AMOUNT_INDEX);
                    // we show the value in the table either using the replace currency or base currency
                    result += getAmountText(getDisplayCurrency(rowIndex), txnValue);
                    break;
                }
                case SHARES_INDEX:
                {
                    // this will only be useful for splits
                    if (split == null)
                    {
                        result += N12EFindAndReplace.SPACE;
                    }
                    else
                    {
                        final TxnValue value = getTxnAmount(split, entry, AMOUNT_INDEX);
                        // in this case we convert the result to the category's currency
                        result += getAmountText(split.getAccount().getCurrencyType(), value);
                    }
                    break;
                }
                case OTHER_AMOUNT_INDEX:
                {
                    // this will only be useful for splits
                    if (split == null)
                    {
                        result += N12EFindAndReplace.SPACE;
                    }
                    else
                    {
                        final TxnValue value = getTxnAmount(split, entry, AMOUNT_INDEX);
                        // in this case we convert the result to the other side's (parent's) currency
                        result += getAmountText(split.getOtherTxn(0).getAccount().getCurrencyType(), value);
                    }
                    break;
                }
                case MEMO_INDEX:
                {
                    // with the Splits as Memos option, we may need either the split or the parent
                    result += getTxnMemoDisplay(primaryTxn, entry);
                    break;
                }
                case MEMO_PARENT_INDEX:
                {
                    // this column always has the parent transaction's memo regardless of the
                    // splits-as-memos or consolidate splits setting
                    result += getTxnMemoDisplay(parent, entry);
                    break;
                }
                case CHECK_INDEX:
                {
                    // the parent currently has the only check # field exposed in the UI
                    result += getTxnCheckDisplay(parent, entry);
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
        if ((_commands != null) && !_commands.isEmpty() && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransactionEntry(entry);
                if (command.getPreviewAmount() != null)
                {
                    value = command.getPreviewAmount();
                }
            }
        }
        return value;
    }

    private CurrencyType getCommandCurrency(final FindResultsTableEntry entry)
    {
        CurrencyType currencyType = null;
        if ((_commands != null) && !_commands.isEmpty() && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransactionEntry(entry);
                if (command.getPreviewAmount() != null)
                {
                    currencyType = command.getAmountCurrency();
                }
            }
        }
        return currencyType;
    }

    private TxnValue getTxnAmount(final AbstractTxn txn,
                              final FindResultsTableEntry entry,
                              final int columnIndex)
    {
        long value = txn.getValue();
        CurrencyType sourceCurrency = null;
        Long commandValue = getCommandValue(entry);
        if (commandValue != null)
        {
            value = commandValue.longValue();
            entry.addModifiedColumn(columnIndex);
            sourceCurrency = getCommandCurrency(entry);
        }
        // if the transaction is under a category account, negate the value because it is the
        // 'other side' to an actual transaction
        final Account account = txn.getAccount();
        if (account != null)
        {
            if (sourceCurrency == null)
            {
                sourceCurrency = account.getCurrencyType();
            }
            Account.AccountType type = account.getAccountType();
            if ((type == Account.AccountType.EXPENSE) || (type == Account.AccountType.INCOME))
            {
                value = -value;
            }
        }

        return new TxnValue(value, sourceCurrency, txn.getDateInt());
    }

    private String getTxnDescriptionDisplay(final AbstractTxn txn,
                                            final FindResultsTableEntry entry)
    {
        String description = txn.getDescription();
        if (txn instanceof SplitTxn)
        {
            ParentTxn parentTxn = txn.getParentTxn();
            if (_controller.getSplitsAsMemos() && (parentTxn.getSplitCount() > 1))
            {
                description = parentTxn.getDescription();
            }
        }
        if ((_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransactionEntry(entry);
                if (command.getPreviewDescription(_controller.getShowParents()) != null)
                {
                    description = command.getPreviewDescription(_controller.getShowParents());
                    entry.addModifiedColumn(DESCRIPTION_INDEX);
                }
            }
        }
        return description;
    }

    private String getTxnMemoDisplay(final AbstractTxn txn,
                                     final FindResultsTableEntry entry)
    {
        String memo;
        if (txn instanceof ParentTxn)
        {
            memo = ((ParentTxn)txn).getMemo();
        }
        else if (txn instanceof SplitTxn)
        {
            ParentTxn parentTxn = txn.getParentTxn();
            if (_controller.getSplitsAsMemos() && (parentTxn.getSplitCount() > 1))
            {
                memo = txn.getDescription();
            }
            else
            {
                memo = parentTxn.getMemo();
            }
        }
        else
        {
            return N12EFindAndReplace.EMPTY;
        }

        if ((_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransactionEntry(entry);
                if (command.getPreviewMemo() != null)
                {
                    memo = command.getPreviewMemo();
                    entry.addModifiedColumn(MEMO_INDEX);
                }
            }
        }
        return memo;
    } // getTxnMemoDisplay()

    private String getTxnCheckDisplay(final AbstractTxn txn,
                                      final FindResultsTableEntry entry)
    {
        String checkNumber = FarUtil.getTransactionCheckNo(txn);
        if ((_commands != null) && (_commands.size() > 0) && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransactionEntry(entry);
                if (command.getPreviewCheckNumber() != null)
                {
                    checkNumber = command.getPreviewCheckNumber();
                    entry.addModifiedColumn(CHECK_INDEX);
                }
            }
        }
        return checkNumber;
    } // getTxnCheckDisplay()

    private String getTxnTagDisplay(final AbstractTxn txn,
                                    final FindResultsTableEntry entry)
    {
        // user tags are associated with splits only
        List<String> tags = FarUtil.getTransactionTags(txn, _userTagSet);

        // TODO: this won't work with more than one command -- fix so that tags are applied in succession
        if ((_commands != null) && !_commands.isEmpty() && entry.isApplied())
        {
            for (final ReplaceCommand command : _commands)
            {
                command.setTransactionEntry(entry);
                if (command.getPreviewTags() != null)
                {
                    tags = command.getPreviewTags();
                    entry.addModifiedColumn(TAG_INDEX);
                }
            }
        }

        // checks for valid transaction and for a non-null user tag set
        if (tags.size() == 0)
        {
            // no tags associated with parent transactions with more than one split
            return N12EFindAndReplace.EMPTY;
        }

        StringBuilder buffer = new StringBuilder(N12EFindAndReplace.EMPTY);
        for (final String tag : tags)
        {
            if (buffer.length() > 0)
            {
                buffer.append(N12EFindAndReplace.COMMA_SEPARATOR);
            }

            buffer.append(tag);
        }
        return buffer.toString();
    }


    private String getTxnCategoryDisplay(final AbstractTxn txn,
                                  final FindResultsTableEntry entry,
                                  final boolean useFullName)
    {
        Account category = getTxnCategory(txn, entry);

        final String result;
        if (category != null)
        {
            if (useFullName)
            {
                result = category.getFullAccountName();
            }
            else
            {
                result = category.getAccountName();
            }
        }
        else if (txn instanceof ParentTxn)
        {
            // for the parent, check if we have only 1 split. If we do, use that. If we have more,
            // show the words '- N splits -'
            StringBuilder buffer = new StringBuilder(_controller.getString(L10NFindAndReplace.SPLIT_1));
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
                command.setTransactionEntry(entry);
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

}
