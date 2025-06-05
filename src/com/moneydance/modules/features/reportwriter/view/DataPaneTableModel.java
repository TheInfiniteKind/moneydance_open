package com.moneydance.modules.features.reportwriter.view;

import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.text.DecimalFormat;
import java.util.List;
import java.util.Map;

public class DataPaneTableModel extends DefaultTableModel {
    Parameters params;
    List<DataRow> data;
    String[] columns = {"Name","Created","Modified","Used"};
    public DataPaneTableModel(Parameters params, List<DataRow> data){
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

        DataRow rowData = data.get(rowIndex);
        switch (columnIndex) {
            /*
             * Name
             */
            case 0:
                return rowData.getName();
            /*
             * Created
             */
            case 1:
                return rowData.getCreated();
            /*
             * Modified
             */
            case 2:
                return rowData.getLastModified();
            /*
             * Used
             */
            case 3:
                return rowData.getLastUsed();

            default:
                return " ";
        }
    }

    @Override
    public boolean isCellEditable(int row, int col) {
        return false;
    }
    public void resetData(List<DataRow> data){
        this.data = data;
    }
    public DataRow getRow(int index) {
        return data.get(index);
    }
}
