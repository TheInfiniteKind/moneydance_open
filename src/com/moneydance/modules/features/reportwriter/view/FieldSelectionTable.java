package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Constants;

import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.TableColumnModelEvent;
import javax.swing.event.TableColumnModelListener;
import javax.swing.table.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

public class FieldSelectionTable extends JTable{
    FieldSelectionTableModel model;
    FieldSelectionTable tableObj;
    private MyCheckBox boxSelect = new MyCheckBox();
    private JTableHeader header;
    private Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
    private Double screenHeight;
    private int[] columnWidths;
    private TableRowSorter<FieldSelectionTableModel> trs;
    private TableColumn col;
    public static int fieldnameCol = 0;
    public static int includedCol = 1;
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
    public FieldSelectionTable(FieldSelectionTableModel model){
        super(model);
        this.model = model;
        tableObj = this;
        trs= new TableRowSorter<FieldSelectionTableModel>(model);
        screenHeight = screenSize.getHeight();
        header = getTableHeader();
        header.setReorderingAllowed(false);
        header.setResizingAllowed(true);
        columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME + ".FIELD." + Constants.CRNTCOLWIDTH);
        if (columnWidths == null || columnWidths.length == 0 || columnWidths.length < model.getColumnCount()) {
            Main.preferences.put(Constants.PROGRAMNAME + ".FIELD." + Constants.CRNTCOLWIDTH,
                    Constants.FIELDDEFAULTCOLWIDTH);
            columnWidths = Constants.FIELDDEFAULTCOLWIDTH;
        }
        this.setAutoCreateRowSorter(false);
        this.setRowSorter(trs);
        setRowHeight(20);
        this.setFillsViewportHeight(true);
        this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        this.setCellSelectionEnabled(true);
        this.setRowSelectionAllowed(true);
        this.getColumnModel().addColumnModelListener(new FieldSelectionTable.WidthListener());
        ((DefaultTableCellRenderer) this.getTableHeader().getDefaultRenderer())
                .setHorizontalAlignment(JLabel.CENTER);
        selectRenderer = new TableCheckBox(this, this.getDefaultRenderer(Boolean.class),
                this.getDefaultRenderer(Object.class));
        /*
         * Field Name
         */
        col = this.getColumnModel().getColumn(fieldnameCol);
        col.setResizable(true);
        col.setPreferredWidth(columnWidths[fieldnameCol]);
        /*
         * Included
         */
        col = this.getColumnModel().getColumn(includedCol);
        col.setResizable(true);
        col.setPreferredWidth(columnWidths[includedCol]);
        col.setHeaderRenderer(new SelectAllHeader());
        TableColumn colSelect = this.getColumnModel().getColumn(includedCol);
        colSelect.setCellEditor(new DefaultCellEditor(boxSelect));
        if (MRBPlatform.isFreeBSD() || MRBPlatform.isUnix())
            colSelect.setCellRenderer(new FieldSelectionTable.CheckBoxRenderer());
        colSelect.setPreferredWidth(columnWidths[includedCol]);
        colSelect.setCellRenderer(selectRenderer);
        trs.setSortable(includedCol, false);


    }
    public boolean getColumnWidthChanged() {
        return isColumnWidthChanged;
    }

    public void setColumnWidthChanged(boolean widthChanged) {
        isColumnWidthChanged = widthChanged;
    }
    public class SelectAllHeader implements TableCellRenderer {
        private JTable table;
        private MouseEventReposter reporter=null;
        private JCheckBox editor;
        public SelectAllHeader(){
            editor = new JCheckBox("Included");
            editor.setHorizontalTextPosition(SwingConstants.LEFT);
         }
        @Override
        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int col){
            if (table != null && this.table != table) {
                this.table = table;
                final JTableHeader header = table.getTableHeader();
                if (header != null) {
  //                  this.editor.setForeground(header.getForeground());
 //                   this.editor.setBackground(header.getBackground());
                    this.editor.setFont(header.getFont());
                    editor.addActionListener(e->{
                        if (e.getSource() instanceof JCheckBox) {
                            model.setAllIncluded(((JCheckBox) (e.getSource())).isSelected());
                            model.fireTableDataChanged();
                        }
                    });
                    editor.setHorizontalAlignment(JLabel.CENTER);
                    reporter = new MouseEventReposter(header, col, this.editor);
                    header.addMouseListener(reporter);
                }
            }

            if (reporter != null) reporter.setColumn(col);

            return this.editor;
        }
        static public class MouseEventReposter extends MouseAdapter {

            private Component dispatchComponent;
            private JTableHeader header;
            private int column  = -1;
            private Component editor;

            public MouseEventReposter(JTableHeader header, int column, Component editor) {
                this.header = header;
                this.column = column;
                this.editor = editor;
            }

            public void setColumn(int column) {
                this.column = column;
            }

            private void setDispatchComponent(MouseEvent e) {
                int col = header.getTable().columnAtPoint(e.getPoint());
                if (col != column || col == -1) return;

                Point p = e.getPoint();
                Point p2 = SwingUtilities.convertPoint(header, p, editor);
                dispatchComponent = SwingUtilities.getDeepestComponentAt(editor, p2.x, p2.y);
            }

            private boolean repostEvent(MouseEvent e) {
                if (dispatchComponent == null) {
                    return false;
                }
                MouseEvent e2 = SwingUtilities.convertMouseEvent(header, e, dispatchComponent);
                dispatchComponent.dispatchEvent(e2);
                return true;
            }

            @Override
            public void mousePressed(MouseEvent e) {
                if (header.getResizingColumn() == null) {
                    Point p = e.getPoint();

                    int col = header.getTable().columnAtPoint(p);
                    if (col != column || col == -1) return;

                    int index = header.getColumnModel().getColumnIndexAtX(p.x);
                    if (index == -1) return;

                    editor.setBounds(header.getHeaderRect(index));
                    header.add(editor);
                    editor.validate();
                    setDispatchComponent(e);
                    repostEvent(e);
                }
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                repostEvent(e);
                dispatchComponent = null;
                header.remove(editor);
            }
        }
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
