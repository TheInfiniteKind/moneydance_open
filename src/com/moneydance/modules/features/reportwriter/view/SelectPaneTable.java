package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;

import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.TableColumnModelEvent;
import javax.swing.event.TableColumnModelListener;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableRowSorter;
import java.awt.*;
import java.awt.event.MouseAdapter;

public class SelectPaneTable extends JTable {
    Parameters params;
    SelectPaneTableModel model;
    SelectPaneTable tableObj;
    private JTableHeader header;
    private Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
    private Double screenHeight;
    private int[] columnWidths;
    private TableRowSorter<SelectPaneTableModel> trs;
    public static int nameCol = 0;
    public static int createdCol = 1;
    public static int modifiedCol = 2;
    public static int usedCol = 3;
    private boolean isColumnWidthChanged;
    public SelectPaneTable(Parameters params, SelectPaneTableModel model){
        super(model);
        this.model = model;
        tableObj = this;
        this.params = params;
        trs= new TableRowSorter<SelectPaneTableModel>(model);
        screenHeight = screenSize.getHeight();
        header = getTableHeader();
        header.setReorderingAllowed(false);
        header.setResizingAllowed(true);
        columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME + ".SEL." + Constants.CRNTCOLWIDTH);
        if (columnWidths == null || columnWidths.length == 0 || columnWidths.length<model.getColumnCount()) {
            Main.preferences.put(Constants.PROGRAMNAME + ".SEL." + Constants.CRNTCOLWIDTH,
                    Constants.SELDEFAULTCOLWIDTH);
            columnWidths = Constants.SELDEFAULTCOLWIDTH;
        }
        this.setAutoCreateRowSorter(false);
        this.setRowSorter(trs);
        this.setFillsViewportHeight(true);
        this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        this.setCellSelectionEnabled(false);
        this.setColumnSelectionAllowed(false);
        this.setRowSelectionAllowed(true);
        this.getColumnModel().addColumnModelListener(new SelectPaneTable.WidthListener());
        ((DefaultTableCellRenderer) this.getTableHeader().getDefaultRenderer())
                .setHorizontalAlignment(JLabel.CENTER);
        /*
         * name
         */
        this.getColumnModel().getColumn(nameCol).setResizable(true);
        this.getColumnModel().getColumn(nameCol).setPreferredWidth(columnWidths[nameCol]);
        /*
         * created
         */
        this.getColumnModel().getColumn(createdCol).setResizable(true);
        this.getColumnModel().getColumn(createdCol).setPreferredWidth(columnWidths[createdCol]);

        /*
         * Modified
         */
        this.getColumnModel().getColumn(modifiedCol).setResizable(true);
        this.getColumnModel().getColumn(modifiedCol).setPreferredWidth(columnWidths[modifiedCol]);
        /*
         * Used
         */
        this.getColumnModel().getColumn(usedCol).setResizable(true);
        this.getColumnModel().getColumn(usedCol).setPreferredWidth(columnWidths[usedCol]);
    }
    public boolean getColumnWidthChanged() {
        return isColumnWidthChanged;
    }

    public void setColumnWidthChanged(boolean widthChanged) {
        isColumnWidthChanged = widthChanged;
    }

    private class WidthListener extends MouseAdapter implements TableColumnModelListener {
        @Override
        public void columnMarginChanged(ChangeEvent e) {
            /*
             * columnMarginChanged is called continuously as the column width is changed by
             * dragging. Therefore, execute code below ONLY if we are not already aware of
             * the column width having changed
             */
            if (!tableObj.getColumnWidthChanged()) {
                /*
                 * the condition below will NOT be true if the column width is being changed by
                 * code.
                 */
                if (tableObj.getTableHeader().getResizingColumn() != null) {
                    // User must have dragged column and changed width
                    tableObj.setColumnWidthChanged(true);
                }
            }
        }

        // line to force save
        @Override
        public void columnMoved(TableColumnModelEvent e) {
        }

        @Override
        public void columnAdded(TableColumnModelEvent e) {
        }

        @Override
        public void columnRemoved(TableColumnModelEvent e) {
        }

        @Override
        public void columnSelectionChanged(ListSelectionEvent e) {
        }
    }
}
