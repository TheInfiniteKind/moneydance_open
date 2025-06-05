package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;

import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.TableColumnModelEvent;
import javax.swing.event.TableColumnModelListener;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableColumn;
import javax.swing.table.TableRowSorter;
import java.awt.*;
import java.awt.event.MouseAdapter;



import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Constants;

import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.TableColumnModelEvent;
import javax.swing.event.TableColumnModelListener;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableColumn;
import javax.swing.table.TableRowSorter;
import java.awt.*;
import java.awt.event.MouseAdapter;
    public class ReportPaneTable extends JTable{
        ReportPaneTableModel model;
        ReportPaneTable tableObj;
        private MyCheckBox boxSelect = new MyCheckBox();
        private JTableHeader header;
        private Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        private Double screenHeight;
        private int[] columnWidths;
        private TableRowSorter<ReportPaneTableModel> trs;
        public static int nameCol = 0;
        public static int templateCol = 1;
        public static int selectionCol = 1;
        public static int dataParmsCol = 1;
        public static int lastVerifiedCol = 1;
        private boolean isColumnWidthChanged;

        public ReportPaneTable(ReportPaneTableModel model){
            super(model);
            this.model = model;
            tableObj = this;
            trs= new TableRowSorter<ReportPaneTableModel>(model);
            screenHeight = screenSize.getHeight();
            header = getTableHeader();
            header.setReorderingAllowed(false);
            header.setResizingAllowed(true);
            columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME + ".REP." + Constants.CRNTCOLWIDTH);
            if (columnWidths == null || columnWidths.length == 0 || columnWidths.length<model.getColumnCount()) {
                Main.preferences.put(Constants.PROGRAMNAME + ".REP." + Constants.CRNTCOLWIDTH,
                        Constants.REPDEFAULTCOLWIDTH);
                columnWidths = Constants.REPDEFAULTCOLWIDTH;
            }
            this.setAutoCreateRowSorter(false);
            this.setRowSorter(trs);
            setRowHeight(20);
            this.setFillsViewportHeight(true);
            this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
            this.setCellSelectionEnabled(false);
            this.setColumnSelectionAllowed(false);
            this.setRowSelectionAllowed(true);
            this.getColumnModel().addColumnModelListener(new com.moneydance.modules.features.reportwriter.view.ReportPaneTable.WidthListener());
            ((DefaultTableCellRenderer) this.getTableHeader().getDefaultRenderer())
                    .setHorizontalAlignment(JLabel.CENTER);
           /*
             * Field Name
             */
            this.getColumnModel().getColumn(nameCol).setResizable(true);
            this.getColumnModel().getColumn(nameCol).setPreferredWidth(columnWidths[nameCol]);
            /*
             * template
             */
            this.getColumnModel().getColumn(templateCol).setResizable(true);
            this.getColumnModel().getColumn(templateCol).setPreferredWidth(columnWidths[templateCol]);
            /*
             * selection
             */
            this.getColumnModel().getColumn(selectionCol).setResizable(true);
            this.getColumnModel().getColumn(selectionCol).setPreferredWidth(columnWidths[selectionCol]);
            /*
             * dataParms
             */
            this.getColumnModel().getColumn(dataParmsCol).setResizable(true);
            this.getColumnModel().getColumn(dataParmsCol).setPreferredWidth(columnWidths[dataParmsCol]);
            /*
             * lastVerified
             */
            this.getColumnModel().getColumn(lastVerifiedCol).setResizable(true);
            this.getColumnModel().getColumn(lastVerifiedCol).setPreferredWidth(columnWidths[lastVerifiedCol]);


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
        public ReportRow getRow(){
            return model.getRow(getSelectedRow());
        }
}
