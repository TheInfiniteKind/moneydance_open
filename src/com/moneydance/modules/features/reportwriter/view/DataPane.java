/*
 * Copyright (c) 2020, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */
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

/*
 * Displays a panel of available data parameters.  The user can create, update and delete data parameters
 * A data parameter group determines how individual records are selected
 */
public class DataPane extends ScreenPanel {
	private Parameters params;
    private DataPaneTable thisTable;
	private DataPaneTableModel thisTableModel;
    private JButton editBtn;
    private JButton deleteBtn;
    private JButton addBtn;
    private JButton copyBtn;
	private JScrollPane scroll;
	public DataPane(Parameters paramsp) {
		params = paramsp;
		setLayout(new BorderLayout());
		setUpTable();
		scroll = new JScrollPane();
		scroll.setViewportView(thisTable);
		JLabel templateLbl = new JLabel("Data Filter Parameters",SwingConstants.CENTER);
		templateLbl.setFont(new Font("Veranda",Font.BOLD,20));
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
		DataDataPane dataDataPan = new DataDataPane(params);
		DataDataRow row = dataDataPan.displayPanel();
		if(row != null) {
			DataRow tabRow = new DataRow();
			tabRow.setName(row.getName());
			tabRow.setFileName(params.getDataDirectory()+"/"+row.getName()+Constants.DATAEXTENSION);
			tabRow.setLastModified(Main.cdate.format(Main.now));
			tabRow.setLastUsed(Main.cdate.format(Main.now));
			tabRow.setCreated(Main.cdate.format(Main.now));
			params.addDataRow(tabRow);
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
		DataRow row = thisTableModel.getRow(index);
		DataDataRow rowEdit = new DataDataRow();
		if (rowEdit.loadRow(row.getName(), params)) {
			DataDataPane pane = new DataDataPane(params,rowEdit);
			rowEdit = pane.displayPanel();
			if (rowEdit != null) {
				row.setLastModified(Main.cdate.format(Main.now));
				params.updateDataRow(row);
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
		DataRow row = thisTableModel.getRow(index);
		if(params.checkDataGroup(row.getName())) {
			OptionMessage.displayMessage("This Data Filter Parameters entry is used in a report.  It can not be deleted.");
			return;
		}
		DataDataRow rowEdit = new DataDataRow();
		if (rowEdit.loadRow(row.getName(), params)) {
			Boolean result = OptionMessage.yesnoMessage("Are you sure you wish to delete data filter parameters "+row.getName());
			if (result) {
				rowEdit.delete(params);
				params.removeDataRow(row);
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
		DataRow row = thisTableModel.getRow(index);
		String result = "";
		while (result.isEmpty()) {
			result = OptionMessage.inputMessage("Enter the name of the new row");
			if (result.equals(Constants.CANCELPRESSED))
				return;
			if (result.isEmpty())
				OptionMessage.displayMessage("A name must be entered");
			else {
				DataDataRow newRow = new DataDataRow();
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
		thisTableModel.resetData(params.getDataList());
		thisTableModel.fireTableDataChanged();
	}

	public void resize() {
		super.resize();
		scroll.setMinimumSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
	}
	private void setUpTable () {
		thisTableModel = new DataPaneTableModel(params,params.getDataList());
		thisTable = new DataPaneTable(params,thisTableModel);
	}

}
