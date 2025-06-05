package com.moneydance.modules.features.reportwriter.view;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.util.ArrayList;
import java.util.List;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.OptionMessage;
import com.moneydance.modules.features.reportwriter.Parameters;

import javax.swing.*;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

public class ReportDataPane extends ScreenDataPane {
	private Parameters params;
	private JTextField name;
	private JComboBox<String> selections;
	private JComboBox<String> dataParms;
	private JComboBox<String> csvDelimiter;
	private JLabel delimiterLbl;
	private JRadioButton createDatabase;
	private JRadioButton createSpreadsheet;
	private JRadioButton createCsvFile;
	private JCheckBox addBOM;
	private JCheckBox generateName;
	private JCheckBox overWriteFile;
	private JCheckBox addDateStamp;
	private JTextField fileName;
	private ButtonGroup group;
	private JPanel csvBox;
	private List<SelectionRow> listSelections;
	private List<DataRow> listDataParms;
	private List<String> listSelNames;
	private List<String> listDataNames;
	private JPanel pane;
	private ReportDataRow row;
	private boolean newRow = false;
	private boolean dirty = false;
	
	public ReportDataPane(Parameters paramsp) {
		super();
		screenName = "ReportDataPane";
		screenTitle = "Report Definition Screen";
		params = paramsp;
		row = new ReportDataRow();
		newRow= true;
	}
	public ReportDataPane(Parameters paramsp, ReportDataRow rowp) {
		super();
		screenName = "ReportDataPane";
		row = rowp;
		params = paramsp;
	}
	public ReportDataRow displayPanel() {
		DEFAULTSCREENWIDTH = Constants.DATAREPORTSCREENWIDTH;
		DEFAULTSCREENHEIGHT = Constants.DATAREPORTSCREENHEIGHT;
		setStage(new JDialog());
		stage.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
		pane = new MyGridPane(Constants.WINREPORTDATA);
		stage.add(pane);
		stage.addWindowListener(new WindowListener() {
			@Override
			public void windowOpened(WindowEvent e) {

			}

			@Override
			public void windowClosing(WindowEvent e) {
				if (dirty) {
					if (OptionMessage.yesnoMessage(Constants.ABANDONMSG)) {
						row = null;
						dirty=false;
					}
				}
			}

			@Override
			public void windowClosed(WindowEvent e) {
				if (dirty) {
					if (OptionMessage.yesnoMessage(Constants.ABANDONMSG)) {
						row = null;
						dirty=false;
					}
				}
			}

			@Override
			public void windowIconified(WindowEvent e) {

			}

			@Override
			public void windowDeiconified(WindowEvent e) {

			}

			@Override
			public void windowActivated(WindowEvent e) {

			}

			@Override
			public void windowDeactivated(WindowEvent e) {

			}
		});

//TODO		Main.accels.setSceneSave(scene, new Runnable () {
/*			@Override
			public void run() {
				if (saveRow())
					stage.close();
				}
		});
		Main.accels.setSceneClose(scene, new Runnable () {
			@Override
			public void run() {
				if (dirty) {
					if (OptionMessage.yesnoMessage("Parameters have changed.  Do you wish to abandon them?")) {
						row = null;
						stage.close();
					}
				}
				else {
					row = null;
					stage.close();
				}
			}
		}); */
		resize();
		listSelections = params.getSelectionList();
		listDataParms = params.getDataList();
		JLabel reportLbl = new JLabel("Name");
		name = new JTextField();
		name.setColumns(40);
		if (!newRow) {
			name.setText(row.getName());	
		}
		name.getDocument().addDocumentListener(new DocumentListener(){
			public void changedUpdate(DocumentEvent e){
				dirty=true;
			}
			public void insertUpdate(DocumentEvent e){}
			public void removeUpdate(DocumentEvent e){}
		});

		delimiterLbl = new JLabel("CSV Delimiter");
		delimiterLbl.setVisible(true);
		csvDelimiter = new JComboBox<>(Constants.DELIMITERS);
		csvDelimiter.addActionListener(e -> dirty = true);
		JLabel addBOMLbl = new JLabel("Target Excel");
		addBOM = new JCheckBox();
		addBOM.addActionListener(e -> dirty = true);
		csvBox = new JPanel();
		csvBox.setLayout(new BoxLayout(csvBox,BoxLayout.X_AXIS));
		csvBox.add(delimiterLbl);
		csvBox.add(Box.createRigidArea(new Dimension(10,0)));
		csvBox.add(csvDelimiter);
		csvBox.add(Box.createRigidArea(new Dimension(10,0)));
		csvBox.add(addBOMLbl);
		csvBox.add(Box.createRigidArea(new Dimension(10,0)));
		csvBox.add(addBOM);
		createDatabase = new JRadioButton ("Create Database");
		createSpreadsheet = new JRadioButton ("Create Spreadsheet");
		createCsvFile = new JRadioButton ("Create .CSV file");
		group = new ButtonGroup();
		class GroupListener implements ActionListener {
			public void actionPerformed(ActionEvent e) {
				JRadioButton rb = (JRadioButton) e.getSource();
				dirty = true;
				csvDelimiter.setEnabled(false);
				addBOM.setEnabled(false);
				 if (rb==createCsvFile && rb.isSelected()) {
					 csvDelimiter.setEnabled(true);
					 addBOM.setEnabled(true);

				 }
			}
		}
		GroupListener listener = new GroupListener();
		createDatabase.addActionListener(listener);
		createSpreadsheet.addActionListener(listener);
		createCsvFile.addActionListener(listener);
		group.add(createDatabase);
		group.add(createSpreadsheet);
		group.add(createCsvFile);
		csvDelimiter.setEnabled(false);
		addBOM.setEnabled(false);
		if (newRow) {
			createCsvFile.setSelected(true);
			csvDelimiter.setEnabled(true);
			addBOM.setEnabled(true);
			csvDelimiter.setSelectedItem(row.getDelimiter());
			addBOM.setSelected(row.getTargetExcel());
		}
		else {
			switch (row.getType()) {
			case DATABASE:
				createDatabase.setSelected(true);
				break;
			case SPREADSHEET:
				createSpreadsheet.setSelected(true);
				break;
			case CSV:
				createCsvFile.setSelected(true);
				csvDelimiter.setEnabled(true);
				addBOM.setEnabled(true);
				csvDelimiter.setSelectedItem(row.getDelimiter());
				addBOM.setSelected(row.getTargetExcel());
				break;
			}
		}
		JLabel fileNameLbl = new JLabel("File Name");
		fileName = new JTextField();
		fileName.setColumns(50);
		fileName.addPropertyChangeListener("value", evt -> dirty=true);
		generateName = new JCheckBox("Generate Name");
		generateName.addActionListener(e -> {
			JCheckBox tmp = (JCheckBox)e.getSource();
			dirty = true;

			if(tmp.isSelected()) {
				fileName.setEnabled(false);
				addDateStamp.setEnabled(false);
			}
			else {
				fileName.setEnabled(true);
				addDateStamp.setEnabled(true);
			}
		});
		overWriteFile = new JCheckBox("Ovewrwrite");
		overWriteFile.addActionListener(e -> dirty = true);
		addDateStamp = new JCheckBox("Add Date Stamp");
		addDateStamp.addActionListener(e -> dirty = true);
		if(!newRow) {
			fileName.setText(row.getOutputFileName());
			generateName.setSelected(row.getGenerate());
			if (row.getGenerate()) {
				fileName.setEnabled(false);
				addDateStamp.setEnabled(false);
			}
			else {
				fileName.setEnabled(true);
				addDateStamp.setEnabled(true);
			}
			overWriteFile.setSelected(row.getOverWrite());
			addDateStamp.setSelected(row.getAddDate());
		}
		JLabel selectionLbl = new JLabel("Selection Group");
		listSelNames = new ArrayList<>();
		for (SelectionRow rowT : listSelections) {
			listSelNames.add(rowT.getName());
		}
		selections = new JComboBox(listSelNames.toArray());
		selections.addActionListener(e -> dirty=true);
		if (!newRow)
			selections.setSelectedItem(row.getSelection());
		JLabel dataParmsLbl = new JLabel("Data Parameters");
		listDataNames = new ArrayList<>();
		for (DataRow rowT : listDataParms) {
			listDataNames.add(rowT.getName());
		}
		dataParms = new JComboBox(listDataNames.toArray());
		dataParms.addActionListener(e -> dirty=true);
		if (!newRow)
			dataParms.setSelectedItem(row.getDataParms());
		JButton okBtn = new JButton();
		if (Main.loadedIcons.okImg == null)
			okBtn.setText("OK");
		else
			okBtn.setIcon(new ImageIcon(Main.loadedIcons.okImg));
		okBtn.addActionListener(e -> saveRow());
		JButton cancelBtn = new JButton();
		if (Main.loadedIcons.cancelImg == null)
			cancelBtn.setText("Cancel");
		else
			cancelBtn.setIcon(new ImageIcon(Main.loadedIcons.cancelImg));
		cancelBtn.addActionListener(e -> {
            if (dirty){
                boolean result = OptionMessage.yesnoMessage(Constants.ABANDONMSG);
            if (!result)
                    return;
            }
            row=null;
            closePane();
        });

		int ix=0;
		int iy=0;
		pane.add(reportLbl, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(name, GridC.getc(ix, iy++).insets(10,10,10,10).west().colspan(5));
		ix=1;
		pane.add(createDatabase, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(createSpreadsheet, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(createCsvFile, GridC.getc(ix++, iy));
		pane.add(csvBox, GridC.getc(ix, iy++).colspan(3).insets(10,10,10,10).west());
		ix=0;
		pane.add(fileNameLbl,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(fileName, GridC.getc(ix, iy++).insets(10,10,10,10).west().colspan(3));
		ix=1;
		pane.add(generateName,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(overWriteFile, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(addDateStamp, GridC.getc(ix, iy++).insets(10,10,10,10).west());
		ix=0;
		pane.add(selectionLbl,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(selections, GridC.getc(ix, iy++).insets(10,10,10,10).west());
		ix=0;
		pane.add(dataParmsLbl,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(dataParms, GridC.getc(ix, iy++).insets(10,10,10,10).west());
		ix=0;
		pane.add(okBtn, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(cancelBtn,GridC.getc(ix, iy).insets(10,10,10,10).west());
		dirty=false;
		stage.pack();
		setLocation();
		stage.setVisible(true);
		return row;
	}

	private void saveRow() {
		if (name.getText().isEmpty()) {
			OptionMessage.displayMessage("Name must be entered");
			return;
		}
		if (selections.getSelectedIndex()<0) {
			OptionMessage.displayMessage("A Selection Group must be selected");
			return;
		}
		if (dataParms.getSelectedIndex()<0) {
			OptionMessage.displayMessage("A Data Parameter Group must be selected");
			return;
		}
		if (fileName.getText().isEmpty() && !generateName.isSelected()) {
			OptionMessage.displayMessage("You must either enter a file name or select Generate Name");
			return;
		}
		boolean updateName=false;
		ReportDataRow tempRow = new ReportDataRow();
		if (!newRow && !row.getName().equals(name.getText()))
			updateName=true;
		if ((newRow || updateName) && tempRow.loadRow(name.getText(), params)) {
			if (OptionMessage.yesnoMessage("Report already exists.  Do you wish to overwrite them?"))  
				tempRow.delete(params);
			else
				return;
		}
		updateParms();
		if (newRow) {
			row.setName(name.getText());
			row.saveRow(params);
		}
		else {
			if (updateName) 
				row.renameRow(name.getText(),params);
			else
				row.saveRow(params);
		}
		closePane();
	}
	private void updateParms() {
		row.setSelection((String)selections.getSelectedItem());
		row.setDataParms((String)dataParms.getSelectedItem());
		if (createCsvFile.isSelected()) {
			row.setType(Constants.ReportType.CSV);
		}
		else {
			if (createDatabase.isSelected()) {
				row.setType(Constants.ReportType.DATABASE);
			}
			else 
				row.setType(Constants.ReportType.SPREADSHEET);
		}
		row.setOutputFileName(fileName.getText());
		row.setGenerate(generateName.isSelected());
		row.setOverWrite(overWriteFile.isSelected());
		row.setAddDate(addDateStamp.isSelected());
		row.setDelimiter((String)csvDelimiter.getSelectedItem());
		row.setTargetExcel(addBOM.isSelected());
		
	}
}
