/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableColumn;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.event.CellEditorListener;
import javax.swing.event.ChangeEvent;
import javax.swing.ListSelectionModel;
import javax.swing.JTable;
import javax.swing.JLabel;
import javax.swing.Icon;
import javax.swing.SwingConstants;
import java.awt.Component;
import java.awt.Color;

/**
 * <p>Columns for the results table.</p>
 * 
 * @author Kevin Menningen
 * @version 1.50
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

        // the cleared column shows icons
        column = new TableColumn(FindResultsTableModel.CLEARED_INDEX);
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_CLEARED));
        column.setCellRenderer(new ClearedCellRenderer());
        addColumn(column);

        column = new TableColumn(FindResultsTableModel.AMOUNT_INDEX);
        if (resources instanceof FarController)
        {
            final MoneydanceGUI mdGui = ((FarController)resources).getMDGUI();
            column.setCellRenderer(new AmountCellRenderer(mdGui));
        }
        else
        {
            column.setCellRenderer(new FindResultsTableCellRenderer());
        }
        column.setHeaderValue(resources.getString(L10NFindAndReplace.RESULTS_COLUMN_AMOUNT));
        addColumn(column);
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Inner Classes
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private class ClearedCellRenderer extends DefaultTableCellRenderer
    {
        @Override
        public Component getTableCellRendererComponent(JTable table, Object value,
                                                       boolean isSelected, boolean hasFocus,
                                                       int row, int column)
        {
            // the default renderer is a JLabel
            JLabel result = (JLabel)super.getTableCellRendererComponent(table, value, isSelected,
                    hasFocus, row, column);

            result.setHorizontalAlignment(JLabel.CENTER);

            if (value instanceof Icon)
            {
                result.setText(N12EFindAndReplace.EMPTY);
                result.setIcon((Icon)value);
            }
            else
            {
                result.setIcon(null);
            }

            return result;
        }
    }

    private class AmountCellRenderer extends FindResultsTableCellRenderer
    {
        private final MoneydanceGUI _mdGui;

        AmountCellRenderer(final MoneydanceGUI mdGui)
        {
            _mdGui = mdGui;
        }

        @Override
        protected Color getNormalForeground(FindResultsTableModel tableModel, int modelIndex)
        {
            long txnValue = tableModel.getAmount(modelIndex);
            if (txnValue < 0)
            {
                return _mdGui.getColors().negativeBalFG;
            }
            return super.getNormalForeground(tableModel, modelIndex);
        }

        @Override
        protected int getTextAlignment()
        {
            return SwingConstants.RIGHT;
        }
    }
}
