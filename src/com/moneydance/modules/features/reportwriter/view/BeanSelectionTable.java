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

public class BeanSelectionTable extends JTable{
    BeanSelectionTableModel model;
    BeanSelectionTable tableObj;
    private MyCheckBox boxSelect = new MyCheckBox();
    private JTableHeader header;
    private Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
    private Double screenHeight;
    private int[] columnWidths;
    private TableRowSorter<BeanSelectionTableModel> trs;
    public static int fieldNameCol = 1;
    public static int fieldTypeCol = 2;
    public static int selectedCol = 0;
    private boolean isColumnWidthChanged;
    private TableCheckBox selectRenderer;
    public static class CheckBoxRenderer extends DefaultTableCellRenderer {
        @Override
        public Component getTableCellRendererComponent(JTable table, Object color, boolean isSelected,
                                                       boolean hasFocus, int row, int column) {
            JCheckBox checkBox;
            if ((boolean) table.getValueAt(row, column))
                checkBox = new JCheckBox(Main.extension.selectedIcon);
            else
                checkBox = new JCheckBox(Main.extension.unselectedIcon);
            checkBox.setHorizontalAlignment(JLabel.CENTER);
            return checkBox;
        }
    }
    public BeanSelectionTable(BeanSelectionTableModel model){
        super(model);
        this.model = model;
        tableObj = this;
        trs= new TableRowSorter<BeanSelectionTableModel>(model);
        screenHeight = screenSize.getHeight();
        header = getTableHeader();
        header.setReorderingAllowed(false);
        header.setResizingAllowed(true);
        columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME + ".BEAN." + Constants.CRNTBEANCOLWIDTH);
        if (columnWidths == null || columnWidths.length == 0 || columnWidths.length < model.getColumnCount()) {
            Main.preferences.put(Constants.PROGRAMNAME + ".BEAN." + Constants.CRNTBEANCOLWIDTH,
                    Constants.BEANDEFAULTCOLWIDTH);
            columnWidths = Constants.BEANDEFAULTCOLWIDTH;
        }
        this.setAutoCreateRowSorter(false);
        this.setRowSorter(trs);
        setRowHeight(20);
        this.setFillsViewportHeight(true);
        this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        this.setCellSelectionEnabled(true);
        this.setRowSelectionAllowed(true);
        this.getColumnModel().addColumnModelListener(new BeanSelectionTable.WidthListener());
        ((DefaultTableCellRenderer) this.getTableHeader().getDefaultRenderer())
                .setHorizontalAlignment(JLabel.CENTER);
        selectRenderer = new TableCheckBox(this, this.getDefaultRenderer(Boolean.class),
                this.getDefaultRenderer(Object.class));

        /*
         * created
         */
        this.getColumnModel().getColumn(selectedCol).setResizable(true);
        this.getColumnModel().getColumn(selectedCol).setPreferredWidth(columnWidths[selectedCol]);
        TableColumn colSelect = this.getColumnModel().getColumn(selectedCol);
        colSelect.setCellEditor(new DefaultCellEditor(boxSelect));
        if (MRBPlatform.isFreeBSD() || MRBPlatform.isUnix())
            colSelect.setCellRenderer(new FieldSelectionTable.CheckBoxRenderer());
        colSelect.setPreferredWidth(columnWidths[selectedCol]);
        colSelect.setCellRenderer(selectRenderer);
        trs.setSortable(selectedCol, false);
        /*
         * Field Name
         */
        this.getColumnModel().getColumn(fieldNameCol).setResizable(true);
        this.getColumnModel().getColumn(fieldNameCol).setPreferredWidth(columnWidths[fieldNameCol]);
        /*
         * Field Name
         */
        this.getColumnModel().getColumn(fieldTypeCol).setResizable(true);
        this.getColumnModel().getColumn(fieldTypeCol).setPreferredWidth(columnWidths[fieldTypeCol]);


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
