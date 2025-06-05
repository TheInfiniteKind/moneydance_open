package com.moneydance.modules.features.reportwriter.view;

import javax.swing.table.DefaultTableModel;
import java.util.List;

public class ReportPaneTableModel extends DefaultTableModel {
    List<ReportRow> data;
    String[] columns = {"Name","Template","Selection","Data Parms","Last Verfied Date"};
    public ReportPaneTableModel(List<ReportRow> data){
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

        ReportRow rowData = data.get(rowIndex);
        if (rowData == null)
            return "no data";
        return switch (columnIndex) {
            /*
             * Name
             */
            case 0 -> rowData.getName();
            /*
             * Template
             */
            case 1 -> {
                if (rowData.getType() == null)
                    rowData.setType(4);
                yield switch (rowData.getType()) {
                    case 2 -> "Create Database";
                    case 4 -> "Output CSV";
                    case 3 -> "Create Spreadsheet";
                    default -> "Unsupported";
                };
            }
            case 2 -> rowData.getSelection();
            case 3 -> rowData.getData();
            case 4 -> rowData.getLastUsed();
            default -> " ";
        };
    }

    @Override
    public boolean isCellEditable(int row, int col) {
        return false;
    }
    public void resetData(List<ReportRow> data){
        this.data = data;
    }
    public ReportRow getRow(int index) {
        if (index < 0)
            return null;
        return data.get(index);
    }}
