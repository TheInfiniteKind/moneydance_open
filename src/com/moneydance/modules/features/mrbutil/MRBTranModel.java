package com.moneydance.modules.features.mrbutil;

import java.util.ArrayList;
import java.util.List;

import javax.swing.table.DefaultTableModel;
/**
 * Table model for the transaction display
 * 
 * @author Mike Bray
 *
 */

public class MRBTranModel extends DefaultTableModel {
	private String[] transcolumns = {"Account","Description","Date","Value","Type","P//S","Cheque","Status"};
	private List<String[]> listData;
	public MRBTranModel () {
		super();
		listData = new ArrayList<String[]>();
	}
	@Override
	public int getColumnCount() {
		return transcolumns.length;
	}
	@Override
	public String getColumnName(int iCol) {
		return transcolumns[iCol];
	}
	
	@Override
	public int getRowCount() {
		if (listData == null)
			return 0;
		return (listData.size());
	}
	/**
	 * Add a row to the model
	 * @param arrRow - array of string values for the row, last entry is the transaction ID which is not displayed
	 */
	public void addRow(String [] arrRow) {
		listData.add(arrRow);
	}
	
	@Override
	public String getValueAt(int iRow, int iCol) {
		return listData.get(iRow)[iCol];
	
	}
	
	public String getUUID(int iRow) {
		return listData.get(iRow)[8];		
	}

}
