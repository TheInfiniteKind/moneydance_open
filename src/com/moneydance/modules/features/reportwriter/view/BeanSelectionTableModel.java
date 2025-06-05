package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.reportwriter.Parameters;

import javax.swing.table.DefaultTableModel;
import java.util.List;

public class BeanSelectionTableModel extends DefaultTableModel {
    Parameters params;
    List<BeanSelectionRow> data;
    String[] columns = {"Sel","Details","Type"};
    public BeanSelectionTableModel(List<BeanSelectionRow> data){
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
            return Boolean.class;
        return String.class;
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

        BeanSelectionRow rowData = data.get(rowIndex);
        return switch (columnIndex) {
            /*
             * Selected
             */
            case 0 -> rowData.isSelected();
            /*
             * Name
             */
            case 1 -> rowData.getText();
            /*
             * Type
             */            case 2 -> rowData.getType();
            default -> " ";
        };
    }
    @Override
    public void setValueAt(Object value,int row, int col){

        if (col==0)
            data.get(row).setSelected((Boolean) value);
    }

    @Override
    public boolean isCellEditable(int row, int col) {
        if (col==0) return true;
        return false;
    }
    public void resetData(List<BeanSelectionRow> data){
        this.data = data;
    }
    public BeanSelectionRow getRow(int index) {
        return data.get(index);
    }}
