/*
 * FindResultsTableColumnModel.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 16, 2008
 * Time: 3:01:26 PM
 */


package com.moneydance.modules.features.findandreplace;

import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableColumn;
import javax.swing.event.CellEditorListener;
import javax.swing.event.ChangeEvent;
import javax.swing.ListSelectionModel;

/**
 * <p>Columns for the results table.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FindResultsTableColumnModel extends DefaultTableColumnModel
{
    private final TableButtonEditor _selectionEditor;
    private ListSelectionModel _tableSelectionModel;

    /**
     * Creates a default table column model.
     * @param resources Internationalization support
     */
    public FindResultsTableColumnModel(final IResourceProvider resources)
    {
        super();
        _selectionEditor = new TableButtonEditor();
        _selectionEditor.addCellEditorListener(new CellEditorListener()
        {
            public void editingStopped(ChangeEvent e)
            {
                if (_tableSelectionModel == null)
                {
                    return;
                }
                if (e.getSource() instanceof TableButtonEditor)
                {
                    TableButtonEditor source = (TableButtonEditor)e.getSource();
                    int row = source.getRow();
                    boolean selected = _tableSelectionModel.isSelectedIndex(row);
                    boolean button = source.getSelected();
                    if (selected != button)
                    {
                        if (button)
                        {
                            // select
                            _tableSelectionModel.addSelectionInterval(row, row);
                        }
                        else
                        {
                            _tableSelectionModel.removeIndexInterval(row, row);
                        }
                    }

                }
            }

            public void editingCanceled(ChangeEvent e)
            {
                
            }
        });
        buildColumns(resources);
    }

    public void setTableSelectionModel(ListSelectionModel tableSelect)
    {
        _tableSelectionModel = tableSelect;
    }
    

    //////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////
    private void buildColumns(final IResourceProvider resources)
    {
        TableColumn column = new TableColumn(FindResultsTableModel.SEL_INDEX);
        column.setCellRenderer(new TableButtonRenderer());
        column.setCellEditor(_selectionEditor);
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.USE_INDEX);
        column.setHeaderValue(N12EFindAndReplace.EMPTY);
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.ACCOUNT_INDEX);
        column.setCellRenderer(new FindResultsTableCellRenderer());
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_ACCOUNT));
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.DATE_INDEX);
        column.setCellRenderer(new FindResultsTableCellRenderer());
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_DATE));
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.DESCRIPTION_INDEX);
        column.setCellRenderer(new FindResultsTableCellRenderer());
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_DESCRIPTION));
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.TAG_INDEX);
        column.setCellRenderer(new FindResultsTableCellRenderer());
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_TAG));
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.CATEGORY_INDEX);
        column.setCellRenderer(new FindResultsTableCellRenderer());
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_CATEGORY));
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.CLEARED_INDEX);
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_CLEARED));
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.AMOUNT_INDEX);
        column.setCellRenderer(new FindResultsTableCellRenderer());
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        addColumn(column);
    }
}
