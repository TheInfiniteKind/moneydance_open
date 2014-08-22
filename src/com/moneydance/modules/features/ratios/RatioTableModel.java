/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import javax.swing.table.AbstractTableModel;
import java.util.ArrayList;
import java.util.List;

/**
 * Stores a table model to allow editing and selecting ratio definitions.
 *
 * @author Kevin Menningen
 */
class RatioTableModel
    extends AbstractTableModel {
  /**
   * The string items.
   */
  private final List<RatioEntry> _data = new ArrayList<RatioEntry>();

  private final String _columnLabel;

  RatioTableModel(final String columnLabel) {
    _columnLabel = columnLabel;
  }

  public void clear() {
    _data.clear();
  }

  public String getColumnName(int column) {
    if (column == 0) return _columnLabel;
    return super.getColumnName(column);
  }

  /**
   * Add an item to the data.
   *
   * @param index  Index to add the item at.
   * @param item   The new item to add.
   * @param notify True if a notification should be sent after adding (false during load from settings).
   */
  public void add(final int index, final RatioEntry item, final boolean notify) {
    int insertIndex = index;
    if ((insertIndex < 0) || (index > _data.size())) {
      insertIndex = _data.size();
    }
    _data.add(insertIndex, item);
    if (notify) {
      fireTableRowsInserted(insertIndex, insertIndex);
    }
  }

  /**
   * Remove an item from the list.
   *
   * @param index The index of the item to delete.
   */
  public void delete(final int index) {
    if ((index >= 0) && (index < _data.size())) {
      _data.remove(index);
      // delete always notifies
      fireTableRowsDeleted(index, index);
    }
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
    return 1;
  }

  /**
   * Returns the most specific superclass for all the cell values
   * in the column.  This is used by the <code>JTable</code> to set up a
   * default renderer and editor for the column.
   *
   * @param columnIndex the index of the column
   * @return the common ancestor class of the object values in the model.
   */
  public Class<?> getColumnClass(int columnIndex) {
    if (columnIndex != 0) {
      return super.getColumnClass(columnIndex);
    }
    return String.class;
  }

  /**
   * Returns true if the cell at <code>rowIndex</code> and
   * <code>columnIndex</code>
   * is editable.  Otherwise, <code>setValueAt</code> on the cell will not
   * change the value of that cell.
   *
   * @param rowIndex    the row whose value to be queried
   * @param columnIndex the column whose value to be queried
   * @return true if the cell is editable
   * @see #setValueAt
   */
  public boolean isCellEditable(int rowIndex, int columnIndex) {
    if (columnIndex != 0) {
      return super.isCellEditable(rowIndex, columnIndex);
    }
    return true;
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
    if (columnIndex != 0) {
      return null;
    }
    return _data.get(rowIndex).getName();
  }

  /**
   * Sets the value in the cell at <code>columnIndex</code> and
   * <code>rowIndex</code> to <code>aValue</code>.
   *
   * @param aValue      the new value
   * @param rowIndex    the row whose value is to be changed
   * @param columnIndex the column whose value is to be changed
   * @see #getValueAt
   * @see #isCellEditable
   */
  public void setValueAt(Object aValue, int rowIndex, int columnIndex) {
    if (columnIndex != 0) {
      return;
    }
    if (aValue instanceof RatioEntry) {
      _data.set(rowIndex, (RatioEntry) aValue);
    } else if (aValue instanceof String) {
      _data.get(rowIndex).setName((String)aValue);
    }
    fireTableRowsUpdated(rowIndex, rowIndex);
  }

  public RatioEntry getRatioEntry(int index) {
    return _data.get(index);
  }

  public void swap(int index1, int index2) {
    final RatioEntry temp = _data.get(index1);
    _data.set(index1, _data.get(index2));
    _data.set(index2, temp);
    fireTableRowsUpdated(Math.min(index1, index2), Math.max(index1, index2));
  }
}
