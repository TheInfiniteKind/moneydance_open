package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;

import javax.swing.table.DefaultTableModel;
import java.util.List;

public class FieldSelectionTableModel extends DefaultTableModel {
    Parameters params;
    List<FieldSelectionRow> data;
    String[] columns = {"Name","Included"};
    public FieldSelectionTableModel(List<FieldSelectionRow> data){
        this.params = params;
        this.data = data;
    }
    @Override
    public int getRowCount() {
        int rows;
        if (data == null)
            rows = 0;
        else
            rows = data.size();
        return rows;
    }

    @Override
    @SuppressWarnings({ "rawtypes", "unchecked" })
    public Class getColumnClass(int c) {
        if (c==0)
            return String.class;
        return Boolean.class;
    }

    @Override
    public int getColumnCount() {
        return columns.length;
    }

    @Override
    public String getColumnName(int c) {
        return columns[c];
    }

    @Override
    public Object getValueAt(int rowIndex, int columnIndex) {

        FieldSelectionRow rowData = data.get(rowIndex);
        switch (columnIndex) {
            /*
             * Name
             */
            case 0:
                return rowData.getFieldName();
            /*
             * Created
             */
            case 1:
                return rowData.getSelected();

            default:
                return " ";
        }
    }
    @Override
    public void setValueAt(Object value,int row, int col){
        if (col==1)
            data.get(row).setSelected((Boolean) value);
    }
    public void setAllIncluded(boolean value){
        for (FieldSelectionRow row :data)
            row.setSelected(value);
    }

    @Override
    public boolean isCellEditable(int row, int col) {
        if (col==1)
            return true;
        return false;
    }
    public void resetData(List<FieldSelectionRow> data){
        this.data = data;
    }
    public FieldSelectionRow getRow(int index) {
        return data.get(index);
    }
}
