package com.moneydance.modules.features.budgetgen;

import java.util.ArrayList;
import java.util.List;

import javax.swing.table.DefaultTableModel;

import com.infinitekind.moneydance.model.Account;

public class GenerateTableHeaderModel extends DefaultTableModel {
	
	private List<Boolean> listSelect;
	private List<String> listCategoryName;
	private List<Account> listCategoryObj;
	private static String NOSELECT = "  ";
	private static String CURRENT = "    ";

	public GenerateTableHeaderModel() {
		super();
		listSelect = new ArrayList<Boolean>();
		listCategoryName = new ArrayList<String>();
		listCategoryObj = new ArrayList<Account>();
	}

	public void AddLine (BudgetLine objLine) {
		listSelect.add(false);
		listCategoryName.add(objLine.getCategoryName());
		listCategoryObj.add(objLine.getCategory());
		return;
	}
	@Override
	public int getRowCount() {
		return (listSelect == null?0:listSelect.size()*2);
	}

	@Override
	public int getColumnCount() {
		return 2;
	}
	
	@Override
	public String getColumnName(int c) {
		if (c == 0)
			return "Select";
		return "Category";
	}
	
	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {

		if ((rowIndex & 1) == 0) {
			if (columnIndex == 0)
				return listSelect.get(rowIndex/2);
			return listCategoryName.get(rowIndex/2);
		}
		else {
			if (columnIndex == 0)
				return NOSELECT;
			return CURRENT;
		}	
	}
	@Override
    public boolean isCellEditable(int row, int col) {
		if (col ==0 && (row &1)==0)
			return true;
		else
			return false;
	}
 	@Override
	public void setValueAt(Object value, int row, int col){
 		if ((row & 1) == 0)
 			listSelect.set(row/2,(Boolean)value);
 	}
 	/*
 	 * return the account object for row i
 	 */
 	public Account getCategoryObj(int iRow) {
 		return listCategoryObj.get(iRow);
 	}}
