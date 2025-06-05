/*
 * Copyright (c) 2014, Michael Bray. All rights reserved.
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
 */

package com.moneydance.modules.features.budgetgen;

import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.util.prefs.BackingStoreException;
import java.util.prefs.Preferences;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.border.EmptyBorder;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.filechooser.FileNameExtensionFilter;

import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.Budget;
import com.infinitekind.moneydance.model.BudgetList;
import com.infinitekind.moneydance.model.PeriodType;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.AwtUtil;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;

/*
 * Window to select the budget to be processes, note only budgets in new format are displayed
 * 
 * Old format has a PeriodType of 'Mixed'
 */
public class BudgetSelectWindow extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private Main extension;
	private FeatureModuleContext context;
	private AccountBook acctBook;
	private BudgetList budgets;
	private BudgetListExtend budgetList;
	private JComboBox<String> budgetCB;
	private String[] budgetNames;
	private JPanel panScreen;
	private JDialog panNewBudget;
	private BudgetValuesWindow panValues = null;
	private BudgetValuesWindow panIncomeValues = null;
	private JFrame expensesFrm;
	private JFrame incomeFrm;
	private JButton valuesBtn;
	private JButton addBudgetBtn;
	private JButton incomeValuesBtn;
	private JButton closeCB;
	private JButton chooseBtn;
	private JButton helpBtn;
	private JTextField fileNameFld;
	private JTextField budgetNameFld;
	private JComboBox<String> budgetTypesCB;
	private PeriodType[] types;
	private JFileChooser fileChooser = null;
	private File parameters;
	public boolean errorFnd;
	private MoneydanceUI mdGUI;
	private com.moneydance.apps.md.controller.Main mdMain;
	/*
	 * Preferences
	 */
	private MRBPreferences2 preferences;
	private Preferences javaPref;
	private Preferences javaRoot;
	private String fileName= Constants.DEFAULTPARAMETERS;
	private String budgetName;
	private String fileNameNode = Constants.FILENAMEPREF;
	private String budgetNameNode = Constants.BUDGETNAMEPREF ;

	/**
	 * Creates new form BudgetMainWindow
	 */
	public BudgetSelectWindow(Main ext) {
		super("Budget Generator");
		mdMain = com.moneydance.apps.md.controller.Main.mainObj;
		mdGUI = mdMain.getUI();
		errorFnd = false;
		fileChooser = new JFileChooser();
		this.extension = ext;
		context = extension.getUnprotectedContext();
		setPreferences();
		GridBagLayout panScreenLayout = new GridBagLayout();
		panScreenLayout.columnWeights = new double[] { 0.0, 1.0 };
		panScreen = new JPanel(panScreenLayout);
		panScreen.setBorder(new EmptyBorder(10, 10, 10, 10));
		int ix=0;
		int iy=0;
		// Budget
		JLabel lblAccountsName = new JLabel("Budget:");
		panScreen.add(lblAccountsName,
				GridC.getc(ix++,iy).west().fillx().insets(10, 10, 10, 10));

		// Select Budget
		acctBook = extension.getUnprotectedContext().getCurrentAccountBook();
		budgets = acctBook.getBudgets();
		budgetList = new BudgetListExtend(extension.getUnprotectedContext());
		budgetNames = budgetList.getBudgetNames();
		budgetCB = new JComboBox<String>(budgetNames);
		budgetCB.setToolTipText("Select the budget you wish to work with");
		String strBudgettemp = budgetList.getBudgetKey (budgetName);
		if (strBudgettemp == Constants.NOBUDGET)
			budgetName = "";
		if (budgetName != "")
			budgetCB.setSelectedItem(budgetName);
		else {
			if (budgetNames.length > 0) {
				budgetName = budgetNames[0];
				updatePreferences(fileName, budgetName);
			}
		}
		panScreen.add(budgetCB,
				GridC.getc(ix++,iy).west().fillx().insets(10, 10, 10, 10));
		budgetCB.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (!(budgetCB.getSelectedIndex() <0)) {
					budgetName = (String) budgetCB.getSelectedItem();
					if (fileName == "") {
						fileName = budgetList.getBudgetKey(budgetName);
						fileNameFld.setText(fileName);
					}
					updatePreferences(fileName, budgetName);
				}
			}
		});
		addBudgetBtn = new JButton("+");
		addBudgetBtn.setToolTipText("Create a new Budget");
		addBudgetBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				createBudget();
			} 
		});
		panScreen.add(addBudgetBtn,GridC.getc(ix,iy++).west().fillx().insets(10, 10, 10, 10));
		/*
		 * parameter file
		 */
		ix=0;
		JLabel lblFileName = new JLabel("Parameters : ");
		panScreen.add(lblFileName,
				GridC.getc(ix++,iy).fillx().east().insets(10, 10, 10, 10));

		fileNameFld = new JTextField();
		fileNameFld.setColumns(20);
		fileNameFld.setText(fileName);
		fileNameFld.setToolTipText("Enter the file name (without extension), or click on button to the right to find the file");
		fileNameFld.getDocument().addDocumentListener(new DocumentListener() {
			@Override
			public void changedUpdate(DocumentEvent e) {
				fileName = fileNameFld.getText();
			}
			@Override
			public void removeUpdate(DocumentEvent e) {
				fileName = fileNameFld.getText();
			}
			@Override
			public void insertUpdate(DocumentEvent e) {
				fileName = fileNameFld.getText();
			}
		});
		panScreen.add(fileNameFld, GridC.getc(ix++,iy).fillx().west().colspan(3)
				.insets(10, 10, 10, 10));
		ix=4;
		chooseBtn = new JButton();
		Image img = getIcon("Search-Folder-icon.jpg");
		if (img == null)
			chooseBtn.setText("Find");
		else
			chooseBtn.setIcon(new ImageIcon(img));
		ix++;
		panScreen.add(chooseBtn, GridC.getc(ix,iy++).fillx()
				.insets(10, 10, 10, 10));
		chooseBtn.setBorder(javax.swing.BorderFactory
				.createLineBorder(panScreen.getBackground()));
		chooseBtn.setToolTipText("Click to open file dialog to find required file");
		chooseBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				chooseFile();
			}
		});
		// Buttons
		valuesBtn = new JButton("Enter Expense Values");
		valuesBtn.setToolTipText("Click to display expense categories");
		valuesBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (budgetNames.length< 1 || ((String)budgetCB.getSelectedItem()).isEmpty())
					JOptionPane.showMessageDialog(null, "You must select a budget first");
				else
					enterValues();
			}
		});
		ix=0;
		panScreen.add(valuesBtn, GridC.getc(ix++,iy).insets(10, 10, 10, 10));

		incomeValuesBtn = new JButton("Enter Income Values");
		incomeValuesBtn.setToolTipText("Click to display income categories");
		incomeValuesBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (budgetNames.length< 1 || ((String)budgetCB.getSelectedItem()).isEmpty())
					JOptionPane.showMessageDialog(null, "You must select a budget first");
				else
					enterIncomeValues();
			}
		});

		panScreen.add(incomeValuesBtn, GridC.getc(ix++,iy).insets(10, 10, 10, 10));
		closeCB = new JButton("Close");
		closeCB.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				closeConsole();
			}
		});
		panScreen.add(closeCB, GridC.getc(ix++,iy).insets(10, 10, 10, 10));
		helpBtn = new JButton("Help");
		helpBtn.setToolTipText("Display help information");
		helpBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				String url = "https://github.com/mrbray99/moneydanceproduction/wiki/Budget-Gen";
				mdGUI.showInternetURL(url);
			}
		});
		panScreen.add(helpBtn, GridC.getc(ix, iy).west().insets(10, 10, 10, 10));
		getContentPane().add(panScreen);
		pack();
		setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		enableEvents(WindowEvent.WINDOW_CLOSING);

		AwtUtil.centerWindow(this);

	}
	private void resetBudgetList() {
		budgetList.resetList();
		budgetNames = budgetList.getBudgetNames();
		budgetCB.removeAllItems();
		for (String budget : budgetNames)
			budgetCB.addItem(budget);
	}
	/*
	 * Create a new Budget
	 */
	private void createBudget() {
		panNewBudget = new JDialog((JFrame)null);
		panNewBudget.setModal(true);
		panNewBudget.setTitle("Create New Budget");
		panNewBudget.setLayout(new GridBagLayout());
		int ix = 0;
		int iy = 0;
		JLabel budgetNameLbl = new JLabel("BudgetName");
		budgetNameFld = new JTextField();
		budgetNameFld.setPreferredSize(new Dimension(100,20));
		types = PeriodType.all();
		String[] typeStrings = new String[types.length];
		for (int i=0;i<types.length;i++) {
			typeStrings[i] = types[i].name();
		}
		budgetTypesCB = new JComboBox<String>(typeStrings);
		budgetTypesCB.setSelectedItem(PeriodType.MONTH.name());
		JLabel periodLbl = new JLabel("Period Type");
		panNewBudget.add(budgetNameLbl,GridC.getc(ix++,iy).west().insets(5,5,5,5));
		panNewBudget.add(budgetNameFld,GridC.getc(ix,iy++).west().insets(5,5,5,5));
		ix=0;
		panNewBudget.add(periodLbl,GridC.getc(ix++,iy).west().insets(5,5,5,5));
		panNewBudget.add(budgetTypesCB,GridC.getc(ix,iy++).west().insets(5,5,5,5));
		JButton okBtn = new JButton("Create New Budget");
		okBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				saveNewBudget();
			}
		});
		JButton cancelBtn = new JButton("Cancel");
		cancelBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				panNewBudget.setVisible(false);
			}
		});
		ix=0;
		panNewBudget.add(okBtn,GridC.getc(ix++,iy).west().insets(5,5,5,5));
		panNewBudget.add(cancelBtn,GridC.getc(ix,iy).west().insets(5,5,5,5));
		panNewBudget.setPreferredSize(new Dimension(300,150));
		panNewBudget.setLocationRelativeTo(null);
		panNewBudget.setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);
		panNewBudget.pack();
		panNewBudget.setVisible(true);
	}
	private void saveNewBudget() {
		if (budgetNameFld.getText().isEmpty()) {
			JOptionPane.showMessageDialog(null,"You must enter a budget name");
			return;
		}
		if (budgets.containsBudgetWithName(budgetNameFld.getText())){
			JOptionPane.showMessageDialog(null,"Budget "+budgetNameFld.getText()+" already exists");
			return;
		} 
		Budget newBudget = new Budget(acctBook);
		newBudget.setName(budgetNameFld.getText());
		newBudget.setPeriodType(types[budgetTypesCB.getSelectedIndex()]);
		budgets.addBudget(newBudget);
		panNewBudget.setVisible(false);
		panNewBudget.dispose();
		resetBudgetList();
		budgetCB.setSelectedItem(budgetNameFld.getText());
		
	}
	/*
	 * Select a file
	 */
	private void chooseFile() {
		fileChooser.setFileFilter(new FileNameExtensionFilter("Budget Files","bpic",
				"BPIC", "bpex", "BPEX"));
		fileChooser.setCurrentDirectory(extension.getUnprotectedContext()
				.getCurrentAccountBook().getRootFolder());
		int iReturn = fileChooser.showDialog(this, "Select File");
		if (iReturn == JFileChooser.APPROVE_OPTION) {
			parameters = fileChooser.getSelectedFile();
			fileNameFld.setText(parameters.getName().substring(0,
					parameters.getName().lastIndexOf('.')));
		}
		updatePreferences(fileName, budgetName);
	}

	private Image getIcon(String icon) {
		try {
			ClassLoader cl = getClass().getClassLoader();
			java.io.InputStream in = cl
					.getResourceAsStream("/com/moneydance/modules/features/budgetgen/"
							+ icon);
			if (in != null) {
				ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
				byte buf[] = new byte[256];
				int n = 0;
				while ((n = in.read(buf, 0, buf.length)) >= 0)
					bout.write(buf, 0, n);
				return Toolkit.getDefaultToolkit().createImage(
						bout.toByteArray());
			}
		} catch (Throwable e) {
		}
		return null;
	}

	public void closeConsole() {
		if (panValues != null) {
			panValues.setVisible(false);
			JFrame ValueFrame = (JFrame) SwingUtilities
					.getWindowAncestor(panValues);
			ValueFrame.dispose();
		}
		if (panIncomeValues != null) {
			panIncomeValues.setVisible(false);
			JFrame ValueFrame = (JFrame) SwingUtilities
					.getWindowAncestor(panIncomeValues);
			ValueFrame.dispose();
		}
		this.dispose();
		this.extension.closeConsole();
	}

	/*
	 * Display the detail based on selected options
	 */
	protected void enterValues() {
		// Create and set up the window.
		if (budgetName.equals("")) {
			JFrame fTemp = new JFrame();
			JOptionPane
			.showMessageDialog(fTemp,
					"No Budget Selected");
		}
		else {
			expensesFrm = new JFrame(
					"Moneydance Budget Generator - Enter Expense Values - Build "+Main.buildNum);
			expensesFrm.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
			panValues = new BudgetValuesWindow(this.extension,
					budgetName, Constants.EXPENSE_SCREEN, fileName);
			expensesFrm.getContentPane().add(panValues);
	
			// Display the window.
			expensesFrm.getContentPane().setPreferredSize(
					new Dimension(panValues.iFRAMEWIDTH, panValues.iFRAMEDEPTH));
			expensesFrm.pack();
			if (Main.imgIcon != null)
				expensesFrm.setIconImage(Main.imgIcon);
			expensesFrm.setVisible(true);
		}
	}

	protected void enterIncomeValues() {
		// Create and set up the window.
		if (budgetName.equals("")) {
			JFrame fTemp = new JFrame();
			JOptionPane
			.showMessageDialog(fTemp,
					"No Budget Selected");
		}
		else {
			incomeFrm = new JFrame(
					"Moneydance Budget Generator - Enter Income Values- Build "+Main.buildNum);
			incomeFrm.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
			panIncomeValues = new BudgetValuesWindow(this.extension,
					budgetName, Constants.INCOME_SCREEN, fileName);
			incomeFrm.getContentPane().add(panIncomeValues);
	
			// Display the window.
			incomeFrm.getContentPane().setPreferredSize(
					new Dimension(panIncomeValues.iFRAMEWIDTH,
							panIncomeValues.iFRAMEDEPTH));
			incomeFrm.pack();
			if (Main.imgIcon != null)
				incomeFrm.setIconImage(Main.imgIcon);
			incomeFrm.setVisible(true);
		}
	}


	void goAway() {
		if (panValues != null) {
			panValues.close();
			panValues = null;
		}
		if (panIncomeValues != null) {
			panIncomeValues.close();
			panIncomeValues = null;
		}
		if (expensesFrm != null) {
			expensesFrm.dispose();
			expensesFrm = null;
		}
		if (incomeFrm != null) {
			incomeFrm.dispose();
			incomeFrm = null;
		}
		setVisible(false);
		dispose();
	}

	/*
	 * preferences
	 */
	private void setPreferences() {
		MRBPreferences2.loadPreferences(context);
		preferences = MRBPreferences2.getInstance();
		budgetName = preferences.getString(Constants.PROGRAMNAME+"."+budgetNameNode, "");
		fileName = preferences.getString(Constants.PROGRAMNAME+"."+fileNameNode, "");
		if (budgetName == "" || fileName=="") {
			javaRoot = Preferences.userRoot();
			javaPref = javaRoot.node(Constants.PREFERENCESNODE);
			budgetName = javaPref.get(budgetNameNode, "");
			fileName = javaPref.get(fileNameNode,Constants.DEFAULTPARAMETERS);
			updatePreferences(fileName,budgetName);
			try {
				javaPref.removeNode();
			} catch (BackingStoreException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}

	public void updatePreferences(String strFileNamep, String strBudgetNamep) {
		if (strFileNamep != "")
			preferences.put(Constants.PROGRAMNAME+"."+fileNameNode, strFileNamep);
		if (strBudgetNamep != "")
			preferences.put(Constants.PROGRAMNAME+"."+budgetNameNode, strBudgetNamep);
		preferences.isDirty();
	}
}