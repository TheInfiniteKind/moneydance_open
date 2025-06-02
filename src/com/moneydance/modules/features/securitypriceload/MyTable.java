package com.moneydance.modules.features.securitypriceload;


import javax.swing.DefaultCellEditor;
import javax.swing.JCheckBox;
import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.table.TableColumn;
import javax.swing.table.TableModel;


public class MyTable extends JTable {
	private JCheckBox boxSelect = new JCheckBox();

	public MyTable(TableModel dm) {
		super(dm);
		this.setFillsViewportHeight(true);
		this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		/*
		 * Select
		 */
		TableColumn colSelect = this.getColumnModel().getColumn(0);
		colSelect.setCellEditor(new DefaultCellEditor(boxSelect));
		colSelect.setPreferredWidth(40);
		/*
		 * Ticker
		 */
		this.getColumnModel().getColumn(1).setResizable(false);
		this.getColumnModel().getColumn(1).setPreferredWidth(100);
		/*
		 * Account
		 */
		this.getColumnModel().getColumn(2).setResizable(false);
		this.getColumnModel().getColumn(2).setPreferredWidth(300);
		/*
		 * Date
		 */
		this.getColumnModel().getColumn(3).setResizable(false);
		this.getColumnModel().getColumn(3).setPreferredWidth(80);
		/*
		 * Current Price
		 */
		this.getColumnModel().getColumn(4).setResizable(false);
		this.getColumnModel().getColumn(4).setPreferredWidth(80);
		/*
		 * New Price
		 */
		this.getColumnModel().getColumn(5).setResizable(false);
		this.getColumnModel().getColumn(5).setPreferredWidth(80);
		/*
		 * High
		 */
		this.getColumnModel().getColumn(6).setResizable(false);
		this.getColumnModel().getColumn(6).setPreferredWidth(80);
		/*
		 * Low
		 */
		this.getColumnModel().getColumn(7).setResizable(false);
		this.getColumnModel().getColumn(7).setPreferredWidth(80);
		/*
		 * Volume
		 */
		this.getColumnModel().getColumn(8).setResizable(false);
		this.getColumnModel().getColumn(8).setPreferredWidth(80);
	}


}
