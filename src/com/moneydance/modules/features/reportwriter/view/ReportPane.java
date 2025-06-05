package com.moneydance.modules.features.reportwriter.view;



import java.awt.*;

import java.util.List;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.OptionMessage;
import com.moneydance.modules.features.reportwriter.Parameters;

import javax.swing.*;

public class ReportPane extends ScreenPanel {
	private Parameters params;
	private List<ReportRow> rows;
    private ReportPaneTable thisTable;
	private ReportPaneTableModel thisModel;
    private JButton editBtn;
    private JButton deleteBtn;
    private JButton addBtn;
    private JButton viewBtn;
    private JButton openOutBtn;
    private JButton copyBtn;
	private String csvRunTip;
	private String spreadRunTip;
	private String dbRunTip;

    private ImageIcon csvIcon;
    private ImageIcon spreadIcon;
    private ImageIcon dbIcon;
    private ScreenPanel thisObj;
	private JScrollPane scroll;

	public ReportPane(Parameters paramsp) {
		params = paramsp;
		thisObj = this;
		csvIcon = Main.loadedIcons.csvImg==null?null:new ImageIcon(Main.loadedIcons.csvImg);
		spreadIcon = Main.loadedIcons.spreadImg==null?null:new ImageIcon(Main.loadedIcons.spreadImg);
		dbIcon = Main.loadedIcons.dbImg==null?null:new ImageIcon(Main.loadedIcons.dbImg);
		setLayout(new BorderLayout());
		setUpTable();
		scroll = new JScrollPane();
		scroll.setViewportView(thisTable);
		JLabel templateLbl = new JLabel("Reports",SwingConstants.CENTER);
		templateLbl.setFont(new Font("Veranda",Font.BOLD,20));
		add(templateLbl, BorderLayout.PAGE_START);
		add(scroll,BorderLayout.CENTER);
		editBtn = new JButton();
		if (Main.loadedIcons.editImg == null)
			editBtn.setText("Edit");
		else
			editBtn.setIcon(new ImageIcon(Main.loadedIcons.editImg));
		editBtn.addActionListener(e -> editRow());
		editBtn.setToolTipText("Edit an existing Reports set");
		deleteBtn = new JButton();
		if (Main.loadedIcons.deleteImg == null)
			deleteBtn.setText("Delete");
		else
			deleteBtn.setIcon(new ImageIcon(Main.loadedIcons.deleteImg));
		deleteBtn.addActionListener(e -> deleteRow());
		deleteBtn.setToolTipText("Delete an existing Reports set");
		addBtn = new JButton();
		if (Main.loadedIcons.addImg == null)
			addBtn.setText("+");
		else
			addBtn.setIcon(new ImageIcon(Main.loadedIcons.addImg));
		addBtn.addActionListener(e -> addRow());
		addBtn.setToolTipText("Add a new Reports set");
		csvRunTip ="Create the selected .csv file";
		spreadRunTip = "Create the selected Spreadsheet";
		dbRunTip = "Create the selected Database";
		viewBtn = new JButton();
		if (csvIcon == null)
			viewBtn.setText("Create CSV file");
		else
			viewBtn.setIcon(csvIcon);
		viewBtn.setToolTipText(csvRunTip);
		viewBtn.addActionListener(e -> viewReport());
		openOutBtn = new JButton();
		if (Main.loadedIcons.searchImg == null)
			openOutBtn.setText("Output Directory");
		else
			openOutBtn.setIcon(new ImageIcon(Main.loadedIcons.searchImg));
		openOutBtn.setToolTipText("Click to open Output folder");
		openOutBtn.addActionListener(e -> SwingUtilities.invokeLater(() -> Main.extension.openOutput()));
		copyBtn = new JButton();
		if (Main.loadedIcons.addImg == null)
			copyBtn.setText("+");
		else
			copyBtn.setIcon(new ImageIcon(Main.loadedIcons.copyImg));
		copyBtn.addActionListener(e -> copyRow());
		copyBtn.setToolTipText("Copy a Data Selection Group");
		JPanel buttons = new JPanel(new GridBagLayout());
		buttons.add(addBtn,GridC.getc(0,0).insets(5,10,10,10));
		buttons.add(editBtn,GridC.getc(1,0).insets(5,10,10,10));
		buttons.add(copyBtn,GridC.getc(2,0).insets(5,10,10,10));
		buttons.add(deleteBtn,GridC.getc(3,0).insets(5,10,10,10));
		buttons.add(viewBtn,GridC.getc(4,0).insets(5,10,10,10));
		buttons.add(openOutBtn,GridC.getc(5,0).insets(5,10,10,10));
		add(buttons,BorderLayout.PAGE_END);
		resize();
	}
	@Override
	protected void newMsg() {
		addRow();
	}

	private void addRow() {
		ReportDataPane reportDataPan = new ReportDataPane(params);
		ReportDataRow row = reportDataPan.displayPanel();
		if(row != null) {
			ReportRow tabRow = new ReportRow();
			tabRow.setName(row.getName());
			tabRow.setFileName(params.getDataDirectory()+"/"+row.getName()+Constants.SELEXTENSION);
			tabRow.setLastUsed(Main.cdate.format(Main.now));
			tabRow.setCreated(Main.cdate.format(Main.now));
			tabRow.setTemplate(row.getTemplate());
			tabRow.setSelection(row.getSelection());
			tabRow.setData(row.getDataParms());
			tabRow.setType(row.getTypeInt());
			params.addReportRow(tabRow);
			row.saveRow(params);
			resetData();
		}
	}
	@Override
	protected void openMsg() {
		editRow();
	}
	private void editRow() {
		ReportRow row = thisTable.getRow();
		if (row ==null) {
			OptionMessage.displayMessage("Please Select a report");
			return;
		}
		ReportDataRow rowEdit = new ReportDataRow();
		if (rowEdit.loadRow(row.getName(), params)) {
			ReportDataPane pane = new ReportDataPane(params,rowEdit);
			rowEdit = pane.displayPanel();
			if (rowEdit != null) {
				row.setLastUsed(Main.cdate.format(Main.now));
				row.setTemplate(rowEdit.getTemplate());
				row.setData(rowEdit.getDataParms());
				row.setSelection(rowEdit.getSelection());
				params.updateReportRow(row);
				rowEdit.saveRow(params);
				resetData();
			}
		}
		
	}
	protected void deleteMsg() {
		deleteRow();
	}
	private void deleteRow() {
		ReportRow row = thisTable.getRow();
		if (row ==null) {
			OptionMessage.displayMessage("Please Select a report");
			return;
		}
		ReportDataRow rowEdit = new ReportDataRow();
		if (rowEdit.loadRow(row.getName(), params)) {
			boolean result = OptionMessage.yesnoMessage("Are you sure you wish to delete report "+row.getName());
			if (result) {
				row.delete();
				params.removeReportRow(row);
			}
			resetData();
		}
		
	}
	
	private void viewReport() {
		ReportRow row = thisTable.getRow();
		if (row ==null) {
			OptionMessage.displayMessage("Please Select a report");
			return;
		}
		ReportDataRow rowEdit = new ReportDataRow();
		if (rowEdit.loadRow(row.getName(), params)) {
			SelectionDataRow selection = new SelectionDataRow();
			if (!selection.loadRow(rowEdit.getSelection(), params)){
				OptionMessage.displayMessage("Selection Group file "+rowEdit.getSelection()+" not found");
				return;
			}
			DataDataRow data = new DataDataRow();
			if(!data.loadRow(rowEdit.getDataParms(), params)){
				OptionMessage.displayMessage("Data Parameters file "+rowEdit.getDataParms()+" not found");
				return;				
			}
			/*
			 * send command to read data and view report running it on the EDT rather than FX Thread
			 */
			javax.swing.SwingUtilities.invokeLater(() -> Main.context.showURL("moneydance:fmodule:" + Constants.PROGRAMNAME + ":"+Constants.VIEWREPORTCMD+"?"+row.getName()));

		}

	}
	private void copyRow() {
		ReportRow row = thisTable.getRow();
		if (row ==null) {
			OptionMessage.displayMessage("Please Select a Report");
			return;
		}
		String result = "";
		while (result.isEmpty()) {
			result = OptionMessage.inputMessage("Enter the name of the new row");
			if (result.equals(Constants.CANCELPRESSED))
				return;
			if (result.isEmpty())
				OptionMessage.displayMessage("A name must be entered");
			else {
				ReportDataRow newRow = new ReportDataRow();
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

	public void resize() {
		super.resize();
		scroll.setMinimumSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
	}
	public void resetData() {
		params.setDataTemplates();
		rows=params.getReportList();
		thisModel.resetData(rows);
		thisModel.fireTableDataChanged();
	}
	
	private void setUpTable () {
		rows = params.getReportList();
		thisModel = new ReportPaneTableModel(rows);
		thisTable = new ReportPaneTable(thisModel);
		thisTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
  		ListSelectionModel tableSelectionModel = thisTable.getSelectionModel();
		tableSelectionModel.addListSelectionListener(e -> {
         if (e.getValueIsAdjusting())
             return;
         ReportRow row = rows.get(e.getFirstIndex());
         if(row!=null){
             ReportDataRow rowEdit = new ReportDataRow();
              if (rowEdit.loadRow(row.getName(), params)) {
                 switch (rowEdit.getType()) {
                 case DATABASE:
                        removeBtnImages();
                     if (dbIcon == null)
                         viewBtn.setText("Create Database");
                     else
                         viewBtn.setIcon(dbIcon);
                     viewBtn.setToolTipText(dbRunTip);
                     break;
                  case SPREADSHEET :
                     if (spreadIcon == null)
                         viewBtn.setText("Output Spreadsheet");
                     else
                         viewBtn.setIcon(spreadIcon);
                     viewBtn.setToolTipText(spreadRunTip);
                     break;
                 case CSV:
                     if (csvIcon == null)
                         viewBtn.setText("Output CSV");
                     else
                         viewBtn.setIcon(csvIcon);
                     viewBtn.setToolTipText(csvRunTip);
                     break;
                 }
             }

         }

     });
	}
	private void removeBtnImages() {
		for (Component comp :thisObj.getComponents()){
			if (comp instanceof JButton){
				if (((JButton)comp).getIcon()==dbIcon)
					((JButton)comp).setIcon(null);
				if (((JButton)comp).getIcon()==csvIcon)
					((JButton)comp).setIcon(null);
				if (((JButton)comp).getIcon()==spreadIcon)
					((JButton)comp).setIcon(null);
			}
		}
	}


}
