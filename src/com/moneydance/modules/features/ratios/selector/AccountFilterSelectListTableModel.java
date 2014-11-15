/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios.selector;

import com.infinitekind.moneydance.model.Account;
import com.moneydance.apps.md.view.resources.MDResourceProvider;
import com.moneydance.modules.features.ratios.L10NRatios;
import com.moneydance.modules.features.ratios.RatiosUtil;

import javax.swing.table.AbstractTableModel;
import java.util.List;
import java.util.ArrayList;

/**
 * <p>Table model for a control that allows the user to select one or more accounts and shows the
 * selected accounts in a table.</p>
 * <p/>
 * <p>There's a bit of clever design here: this serves both as the table model and the table
 * selection model. The first column is the checkbox that includes or excludes an item. This
 * is the same as selecting it. Leaving the default table selection model in the table required
 * special 'glue' logic to keep the selection model in sync with the table model, and the
 * performance was less than ideal (blinking selection due to multiple screen refreshes). The
 * approach of combining them provides a much cleaner and responsive display, at the expense of
 * only a little extra mouse logic in the view.</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class AccountFilterSelectListTableModel
    extends AbstractTableModel {
  static final int NAME_INDEX = 0;
  static final int SEL_INDEX = 1;

  private final List<AccountFilterSelectListTableEntry> _data;
  private final List<String> _columns;

  private final AccountFilterSelectListController _controller;


  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Construction
  //////////////////////////////////////////////////////////////////////////////////////////////

  AccountFilterSelectListTableModel(final AccountFilterSelectListController controller) {
    super();
    _controller = controller;

    _data = new ArrayList<AccountFilterSelectListTableEntry>();
    _columns = new ArrayList<String>();
    buildColumns(_controller.getMDGUI());
  }


  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Package Private Methods
  //////////////////////////////////////////////////////////////////////////////////////////////

  AccountFilterSelectListTableEntry getEntry(final int index) {
    return _data.get(index);
  }

  void reset() {
    _data.clear();
  }


  AccountFilterSelectListTableEntry add(final Account account, final String name, final String fullName,
                                  final int accountId, final int accountType, boolean notify) {
    final int index = _data.size();
    final AccountFilterSelectListTableEntry entry = new AccountFilterSelectListTableEntry(account, name, fullName,
                                                                              accountId, accountType);
    _data.add(entry);

    if (notify) {
      fireTableRowsInserted(index, index);
    }
    return entry;
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
  public boolean isCellEditable(int rowIndex, int columnIndex) {
    return (columnIndex == SEL_INDEX);
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
  public int getRowCount() {
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
  public int getColumnCount() {
    return 2;  // selector and name
  }


  @Override
  public Class<?> getColumnClass(int columnIndex) {
    if (columnIndex == SEL_INDEX) {
      return FilterSelection.class;
    }
    return String.class;
  }

  /**
   * Returns the value for the cell at <code>columnIndex</code> and
   * <code>rowIndex</code>.
   *
   * @param rowIndex    the row whose value is to be queried
   * @param columnIndex the column whose value is to be queried
   * @return the value Object at the specified cell
   */
  public Object getValueAt(int rowIndex, int columnIndex) {
    final AccountFilterSelectListTableEntry entry = _data.get(rowIndex);
    switch (columnIndex) {
      case NAME_INDEX: {
        Account account = entry.getAccount();
        if (account != null) return account;   // could be an account type
        return entry.getName();
      }
      case SEL_INDEX: {
        return entry.getFilterSelection();
      }
      default: {
        return N12ESelector.EMPTY;
      }
    } // switch columnIndex
  }


  @Override
  public void setValueAt(Object aValue, int rowIndex, int columnIndex) {
    super.setValueAt(aValue, rowIndex, columnIndex);
    if ((columnIndex == SEL_INDEX) && (aValue instanceof FilterSelection)) {
      final AccountFilterSelectListTableEntry entry = _data.get(rowIndex);
      final FilterSelection selection = (FilterSelection)aValue;
      entry.setFilterSelection(selection);
      int maxRowIndex = rowIndex;
      int minRowIndex = rowIndex;
      if (entry.isHeader()) {
        maxRowIndex = setAllOfType(entry.getAccountType(), selection, rowIndex);
      } else {
        // set all the children with the parent
        if (_controller.getAutoSelectChildAccounts()) {
          maxRowIndex = setAllChildrenOfAccount(selection, rowIndex);
        }
        minRowIndex = updateHeaderRow(entry.getAccountType(), selection, rowIndex);
      }
      // notify
      fireTableRowsUpdated(minRowIndex, maxRowIndex);
    }
  }

  /**
   * For the given account type, find the header row and update it according to whether the
   * children are all of the same filter setting or not.
   *
   * @param accountType The account type to update.
   * @param selection   The filter setting to check for.
   * @param rowIndex    The row of the account item that was changed.
   * @return The minimum row index of an item that changed.
   */
  private int updateHeaderRow(int accountType, FilterSelection selection, int rowIndex) {
    int headerIndex = -1;
    // this assumes a sorted order where the header precedes the account
    for (int index = rowIndex - 1; index >= 0; index--) {
      final AccountFilterSelectListTableEntry entry = _data.get(index);
      if ((entry.isHeader()) && (entry.getAccountType() == accountType)) {
        headerIndex = index;
        break;
      }
    }
    if (headerIndex < 0) return rowIndex; // header not found, error condition
    final AccountFilterSelectListTableEntry header = _data.get(headerIndex);
    FilterSelection headerFilter = selection;
    for (int index = headerIndex + 1; index < _data.size(); index++) {
      final AccountFilterSelectListTableEntry entry = _data.get(index);
      if (entry.getAccountType() != accountType) break; // we're done
      if (!selection.equals(entry.getFilterSelection())) {
        // there are accounts of the given type that don't share the same selection,
        // therefore the header has a null filter selection and we're done
        headerFilter = null;
        break;
      }
    }
    if (!RatiosUtil.areEqual(header.getFilterSelection(), headerFilter)) {
      // we're going to change the header item (can be null)
      header.setFilterSelection(headerFilter);
      return headerIndex;
    }
    return rowIndex;
  }

  /**
   * Set all accounts of the given account type to the given filter type.
   *
   * @param accountType The account type.
   * @param selection   The new filter setting.
   * @param headerIndex The index of the header row that was clicked on.
   * @return The maximum row index of an entry that changed.
   */
  private int setAllOfType(int accountType, FilterSelection selection, int headerIndex) {
    int maxRowIndex = headerIndex;
    // this assumes accounts sorted by type, so header is above all others of that type
    for (int index = headerIndex; index < _data.size(); index++) {
      final AccountFilterSelectListTableEntry entry = _data.get(index);
      // skip headers
      if (entry.isHeader()) continue;
      // skip accounts of wrong type
      if (entry.getAccountType() != accountType) continue;
      // skip accounts that already have the given filter
      if (selection.equals(entry.getFilterSelection())) continue;
      entry.setFilterSelection(selection);
      maxRowIndex = Math.max(maxRowIndex, index);
    }
    return maxRowIndex;
  }

  /**
   * Set all accounts that are children of the given account to the given filter type.
   *
   * @param selection   The new filter setting.
   * @param parentIndex The index of the header row that was clicked on.
   * @return The maximum row index of an entry that changed.
   */
  private int setAllChildrenOfAccount(FilterSelection selection, int parentIndex) {
    int maxRowIndex = parentIndex;
    final Account parentAccount = _data.get(parentIndex).getAccount();
    if (parentAccount == null) return maxRowIndex; // error, should not happen
    // this assumes all child accounts are below the parent in the list, and the first account
    // that is not a child or descendant breaks the loop, there won't be any others below
    for (int index = parentIndex + 1; index < _data.size(); index++) {
      final AccountFilterSelectListTableEntry entry = _data.get(index);
      final Account childAccount = entry.getAccount();
      // if we reach a header, we're done
      if (childAccount == null) break;
      // skip when we find one that isn't a child, we're done
      if (!childAccount.isDescendantOf(parentAccount)) break;
      // skip accounts that already have the given filter
      if (selection.equals(entry.getFilterSelection())) continue;
      entry.setFilterSelection(selection);
      maxRowIndex = Math.max(maxRowIndex, index);
    }
    return maxRowIndex;
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
  public String getColumnName(final int column) {
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
  public int findColumn(final String columnName) {
    for (int index = 0; index < _columns.size(); index++) {
      if (_columns.get(index).compareTo(columnName) == 0) {
        return index;
      }
    }
    return -1;
  }

  //////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  //////////////////////////////////////////////////////////////////////////////////////////////

  private void buildColumns(final MDResourceProvider resources) {
    _columns.add(resources.getStr(L10NRatios.ACCOUNT_NAME));
    _columns.add(resources.getStr(L10NRatios.SELECT));
  }


}
