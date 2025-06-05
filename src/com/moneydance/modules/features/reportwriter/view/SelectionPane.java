package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.OptionMessage;
import com.moneydance.modules.features.reportwriter.Parameters;



import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;


public class SelectionPane extends ScreenPanel{
	private Parameters params;
	private SelectPaneTable thisTable;
	private SelectPaneTableModel thisTableModel;
	private JButton editBtn;
	private JButton deleteBtn;
	private JButton addBtn;
	private JButton copyBtn;
	private JScrollPane scroll;
	public SelectionPane(Parameters paramsp) {
		params = paramsp;
		setLayout(new BorderLayout());
		setUpTable();
		scroll = new JScrollPane();
		JLabel templateLbl = new JLabel("Data Selection Groups",SwingConstants.CENTER);
		templateLbl.setFont(new Font("Veranda",Font.BOLD,20));
		scroll.setViewportView(thisTable);
		add(templateLbl, BorderLayout.PAGE_START);
		add(scroll,BorderLayout.CENTER);
		editBtn = new JButton();
		if (Main.loadedIcons.editImg == null)
			editBtn.setText("Edit");
		else
			editBtn.setIcon(new ImageIcon(Main.loadedIcons.editImg));
		editBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				editRow();
			}
		});
		editBtn.setToolTipText("Edit an existing Data Filter Parameters set");
		deleteBtn = new JButton();
		if (Main.loadedIcons.deleteImg == null)
			deleteBtn.setText("Delete");
		else
			deleteBtn.setIcon(new ImageIcon(Main.loadedIcons.deleteImg));
		deleteBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				deleteRow();
			}
		});
		deleteBtn.setToolTipText("Delete an existing Data Filter Parameters set");
		addBtn = new JButton();
		if (Main.loadedIcons.addImg == null)
			addBtn.setText("+");
		else
			addBtn.setIcon(new ImageIcon(Main.loadedIcons.addImg));
		addBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				addRow();
			}
		});
		addBtn.setToolTipText("Add a new Data Filter Parameters set");
		copyBtn = new JButton();
		if (Main.loadedIcons.addImg == null)
			copyBtn.setText("+");
		else
			copyBtn.setIcon(new ImageIcon(Main.loadedIcons.copyImg));
		copyBtn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				copyRow();
			}
		});
		copyBtn.setToolTipText("Copy a Data Filter Parameters set");
		JPanel buttons = new JPanel(new GridBagLayout());
		buttons.add(addBtn, GridC.getc(0,0).insets(5,10,10,10));
		buttons.add(editBtn,GridC.getc(1,0).insets(5,10,10,10));
		buttons.add(copyBtn,GridC.getc(2,0).insets(5,10,10,10));
		buttons.add(deleteBtn,GridC.getc(3,0).insets(5,10,10,10));
		add(buttons, BorderLayout.PAGE_END);
		resize();
	}
	@Override
	protected void newMsg() {
		addRow();
	}
	private void addRow() {
		SelectionDataPane selectPan = new SelectionDataPane(params);
		SelectionDataRow row = selectPan.displayPanel();
		if(row != null) {
			SelectionRow tabRow = new SelectionRow();
			tabRow.setName(row.getName());
			tabRow.setFileName(params.getDataDirectory()+"/"+row.getName()+Constants.DATAEXTENSION);
			tabRow.setLastModified(Main.cdate.format(Main.now));
			tabRow.setLastUsed(Main.cdate.format(Main.now));
			tabRow.setCreated(Main.cdate.format(Main.now));
			params.addSelectionRow(tabRow);
			row.saveRow(params);
			resetData();
		}
	}
	@Override
	protected void openMsg() {
		editRow();
	}
	private void editRow() {
		int index = thisTable.getSelectedRow();
		if (index <0) {
			OptionMessage.displayMessage("Please Select a parameter set");
			return;
		}
		SelectionRow row = thisTableModel.getRow(index);
		SelectionDataRow rowEdit = new SelectionDataRow();
		if (rowEdit.loadRow(row.getName(), params)) {
			SelectionDataPane pane = new SelectionDataPane(params,rowEdit);
			rowEdit = pane.displayPanel();
			if (rowEdit != null) {
				row.setLastModified(Main.cdate.format(Main.now));
				params.updateSelectionRow(row);
				rowEdit.saveRow(params);
				resetData();
			}
		}

	}
	protected void deleteMsg() {
		deleteRow();
	}
	private void deleteRow() {
		int index = thisTable.getSelectedRow();
		if (index <0) {
			OptionMessage.displayMessage("Please Select a Parameter Set");
			return;
		}
		SelectionRow row = thisTableModel.getRow(index);
		if(params.checkDataGroup(row.getName())) {
			OptionMessage.displayMessage("This Data Filter Parameters entry is used in a report.  It can not be deleted.");
			return;
		}
		SelectionDataRow rowEdit = new SelectionDataRow();
		if (rowEdit.loadRow(row.getName(), params)) {
			Boolean result = OptionMessage.yesnoMessage("Are you sure you wish to delete data filter parameters "+row.getName());
			if (result) {
				rowEdit.delete(params);
				params.removeSelectionRow(row);
			}
			resetData();
		}

	}
	private void copyRow() {
		int index= thisTable.getSelectedRow();
		if (index<0 ) {
			OptionMessage.displayMessage("Please Select a Parameter Set");
			return;
		}
		SelectionRow row = thisTableModel.getRow(index);
		String result = "";
		while (result.isEmpty()) {
			result = OptionMessage.inputMessage("Enter the name of the new row");
			if (result.equals(Constants.CANCELPRESSED))
				return;
			if (result.isEmpty())
				OptionMessage.displayMessage("A name must be entered");
			else {
				SelectionDataRow newRow = new SelectionDataRow();
				if (newRow.loadRow(result,params)) {
					OptionMessage.displayMessage("New Name already exists");
					result = "";
				}
				else {
					newRow.loadRow(row.getName(), params);
					newRow.setName(result);
					newRow.saveRow(params);
				}
			}
		}
		resetData();
	}
	public void resetData() {
		params.setDataTemplates();
		thisTableModel.resetData(params.getSelectionList());
		thisTableModel.fireTableDataChanged();
	}

	public void resize() {
		super.resize();
		scroll.setMinimumSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
	}
	private void setUpTable () {
		thisTableModel = new SelectPaneTableModel(params,params.getSelectionList());
		thisTable = new SelectPaneTable(params,thisTableModel);
	}


}
