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

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;

import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.beans.PropertyChangeEvent;
import java.util.Calendar;
import java.util.List;
import java.util.prefs.BackingStoreException;
import java.util.prefs.Preferences;

import javax.swing.BorderFactory;
import javax.swing.DefaultComboBoxModel;
/*
 * Main window of budget parameters. Contains a row for each BudgetLine.  BudgetLines are
 * obtained from the Budget Parameters
 */
import javax.swing.InputVerifier;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JFormattedTextField;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.border.Border;

import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;

public class BudgetValuesWindow extends JPanel {
	/*
	 * Identifies the budget being worked on
	 */
	public static BudgetListExtend budgetList;
	public static BudgetExtend budget;
	public BudgetParameters params;
	private String fileName;
	private JButton helpBtn;
	private MoneydanceUI mdGUI;
	private com.moneydance.apps.md.controller.Main mdMain;
	/*
	 * Screen fields
	 */
	public static MyTable budgetTable;
	public static MyTableModel budgetModel;
	private JButton btnAddAccount;
	private JButton btnSelectAll;
	private JButton btnDeselectAll;
	private JButton btnDeleteSelected;
	private JButton btnCalculateSelected;
	private JButton btnCalculateAll;
	private JButton btnGenerate;
	private JButton btnClose;
	private JButton btnSave;
	private JButton btnEdit;
	private JFormattedTextField txtRPI;
	private JComboBox<String> boxPeriod;
	private JComboBox<String> boxYears;
	private int iType;
	private boolean startError;
	private boolean endError;
	private boolean rpiError;
	private Border validBorder;
	private Border invalidBorder;
	/*
	 * date fields
	 */
	public static int iFiscalYear;
	public static int iYear;
	public static JDateField startDate;
	public static JDateField endDate;
	public static JDateField fiscalStart;
	public static JDateField fiscalEnd;
	public static JDateField startYear;
	public static JDateField endYear;
	public static Calendar weekStart;

	private JPanel panTop;
	private JPanel panMid;
	private JPanel panBot;
	private JScrollPane spScrollPane;
	private GenerateWindow panGen = null;
	private AddAccountsWindow panAcct = null;
	/*
	 * Preferences and window sizes
	 */
	private Preferences regPreferences;
	private Preferences regRoot;
	private MRBPreferences2 preferences;
	public int iFRAMEWIDTH = Constants.FRAMEWIDTH;
	public int iFRAMEDEPTH = Constants.FRAMEDEPTH;
	private int iTOPWIDTH;
	private int iMIDWIDTH;
	private int iBOTWIDTH;
	private int iMIDDEPTH;

	public BudgetValuesWindow(Main extension, String strSelectedBud, int iTypep, String strFileNamep) {
		mdMain = com.moneydance.apps.md.controller.Main.mainObj;
		mdGUI = mdMain.getUI();
		iType = iTypep;
		fileName = strFileNamep;
		FeatureModuleContext context = extension.getUnprotectedContext();
		MRBPreferences2.loadPreferences(context);
		preferences = MRBPreferences2.getInstance();
		/*
		 * set up budget objects
		 */
		budgetList = new BudgetListExtend(extension.getUnprotectedContext());
		String strFiscal = extension.up
				.getSetting(UserPreferences.FISCAL_YEAR_START_MMDD);
		iFiscalYear = StringUtils.isBlank(strFiscal) ? 101 : Integer
				.parseInt(strFiscal);
		budget = budgetList.getBudget(strSelectedBud, iFiscalYear, iType, fileName);
		if (budget == null) {
			JFrame fTemp = new JFrame();
			JOptionPane
			.showMessageDialog(fTemp,
					"Budget " + strSelectedBud + " not found");
			return;
		}
		else {
			if (budget.getPeriodOrder() == -1)
				return;
		}

		params = budget.getParameters();
		/*
		 * set up dates for periods (Fiscal Start date is set when BudgetExtend
		 * is created)
		 */
		Calendar gc = Calendar.getInstance();
		iYear = gc.get(Calendar.YEAR);
		Calendar dtYear = Calendar.getInstance();
		dtYear.set(iYear, Calendar.JANUARY, 1);
		startYear = new JDateField(Main.cdate);
		startYear.setDate(dtYear.getTime());
		endYear = new JDateField(Main.cdate);
		endYear.setDateInt(startYear.getDateInt());
		endYear.gotoLastDayInYear();
		Calendar dtFiscalEnd = Calendar.getInstance();
		weekStart = Calendar.getInstance();
		weekStart.setWeekDate(iYear, 1, Calendar.SUNDAY);
		fiscalStart = budget.getFiscalStart();
		fiscalEnd = new JDateField(Main.cdate);
		dtFiscalEnd.setTime(fiscalStart.parseDate());
		dtFiscalEnd.add(Calendar.YEAR, 1);
		fiscalEnd.setDate(dtFiscalEnd.getTime());
		fiscalEnd.decrementDate();
		startDate = new JDateField(Main.cdate);
		endDate = new JDateField(Main.cdate);
		/*
		 * set up table
		 */
		budgetTable = new MyTable(new MyTableModel(params, iType), params);
		budgetModel = (MyTableModel) budgetTable.getModel();
		/*
		 * start of screen
		 * 
		 * Top panel
		 */
		startError = false;
		endError = false;
		rpiError = false;
		invalidBorder = BorderFactory.createLineBorder(Color.RED, 1);
		addComponentListener(new ComponentListener() {

			@Override
			public void componentResized(ComponentEvent arg0) {
				JPanel panScreen = (JPanel) arg0.getSource();
				Dimension objDimension = panScreen.getSize();
				updatePreferences(objDimension);
			}

			@Override
			public void componentShown(ComponentEvent arg0) {
				// not needed
			}

			@Override
			public void componentHidden(ComponentEvent e) {
				// not needed
			}

			@Override
			public void componentMoved(ComponentEvent e) {
				// not needed
			}

		});
		setPreferences(); // set the screen sizes
		this.setLayout(new BorderLayout());
		panTop = new JPanel();
		panTop.setSize(iTOPWIDTH, Constants.TOPDEPTH);
		GridBagLayout gbl_panTop = new GridBagLayout();
		gbl_panTop.columnWeights = new double[] { 0.0, 1.0, 0.0, 1.0, 0.0 };
		gbl_panTop.columnWidths = new int[] { 100, 100, 100, 100, 0 };
		gbl_panTop.rowHeights = new int[] { 20, 20, 20, 20 };
		panTop.setLayout(gbl_panTop);
		/*
		 * Budget Selected
		 */
		int x = 0;
		int y = 0;
		JLabel lblBudget = new JLabel("Budget :");
		panTop.add(lblBudget, GridC.getc(x, y).west());
		x++;
		JLabel lblBudgetName = new JLabel(budget.getName() + "("
				+ budget.getPeriodTypeName() + ")");
		panTop.add(lblBudgetName, GridC.getc(x, y).west());
		/*
		 * Budget Period
		 */
		x++;
		JLabel lblPeriod = new JLabel("Period :");
		panTop.add(lblPeriod, GridC.getc(x, y).west().insets(10, 10, 10, 10));
		x++;
		boxPeriod = new JComboBox<>(Constants.PERIODS);
		boxPeriod.setSelectedIndex(params.getDatePeriod());
		String strTip = "<html>Select Fiscal year if you budget is to match your declared Fiscal Year.";
		strTip += "<br>Select Calendar Year if your budget is to be from 1st January to 31st December.";
		strTip += "<br>Alternately select Custom Dates to enter your own period</html>"; 
		boxPeriod.setToolTipText(strTip);
		panTop.add(boxPeriod, GridC.getc(x++, y).west().insets(10, 10, 10, 10));
		boxPeriod.addActionListener(e -> {
            params.setDatePeriod(boxPeriod.getSelectedIndex());
            changeDates();
        });
		helpBtn = new JButton("Help");
		helpBtn.setToolTipText("Display help information");
		helpBtn.addActionListener(e -> {
            String url = "https://github.com/mrbray99/moneydanceproduction/wiki/Budget-Gen";
            mdGUI.showInternetURL(url);
        });
		panTop.add(helpBtn, GridC.getc(x, y++).west().insets(10, 10, 10, 10));
		/*
		 * Start Date
		 */
		x = 0;
		y++;
		JLabel lblDatesStart = new JLabel("Dates - Start :");
		panTop.add(lblDatesStart, GridC.getc(x, y).west()
				.insets(10, 10, 10, 10));
		x++;
		/*
		 * use the border as the default valid border
		 */
		validBorder = startDate.getBorder();
		startDate.setDateInt(params.getStartDate());
		startDate.setDisabledTextColor(Color.BLACK);
		strTip = "<html>Enter or select the start date for your budget.";
		strTip += "<br>Note: Start date must start on 1st January if chosen Budget is Annual,";
		strTip+= " <br>1st of the Month if Monthly, and a Sunday if weekly or bi-weekly</html>";
		startDate.setToolTipText(strTip);
		panTop.add(startDate, GridC.getc(x, y).west().insets(10, 10, 10, 10));
		startDate.setInputVerifier(new InputVerifier() {
			@Override
			public boolean verify(JComponent jcField) {
				JDateField jdtStart = (JDateField) jcField;
				Calendar dtStart = Calendar.getInstance();
				dtStart.setTime(jdtStart.getDate());
				Calendar dtEnd = Calendar.getInstance();
				dtEnd.setTime(endDate.getDate());
				switch (budget.getPeriodOrder()) {
				case Constants.PERIODANNUAL:
					if (dtStart.get(Calendar.MONTH) != Calendar.JANUARY
							|| dtStart.get(Calendar.DAY_OF_MONTH) != 1) {
						JFrame fTemp = new JFrame();
						JOptionPane
								.showMessageDialog(fTemp,
										"Budget is annual, Start Date must be 1st of January");
						startError = true;
						startDate.setBorder(invalidBorder);
						return true;
					}
					break;
				case Constants.PERIODMONTHLY:
					if (dtStart.get(Calendar.DAY_OF_MONTH) != 1) {
						JFrame fTemp = new JFrame();
						JOptionPane
								.showMessageDialog(fTemp,
										"Budget is monthly, Start Date must be 1st day of month");
						startError = true;
						startDate.setBorder(invalidBorder);
						return true;
					}
					break;
				case Constants.PERIODWEEKLY:
				case Constants.PERIODBIWEEKLY:
					if (dtStart.get(Calendar.DAY_OF_WEEK) != Calendar.SUNDAY) {
						JFrame fTemp = new JFrame();
						JOptionPane
								.showMessageDialog(fTemp,
										"Budget is Weekly/Bi-Weekly, Start Date must be a Sunday");
						return false;
					}
					break;
				}
				dtStart.add(Calendar.YEAR, 1);
				dtStart.add(Calendar.DAY_OF_YEAR, -1);
				if (dtEnd.after(dtStart)) {
					JFrame fTemp = new JFrame();
					JOptionPane
							.showMessageDialog(fTemp,
									"End Date can not be beyond 1 year after start date");
					return false;
				}
				params.setStartDate(jdtStart.getDateInt());
				startError = false;
				startDate.setBorder(validBorder);
				return true;
			}
		});
		startDate.addPropertyChangeListener(this::changeStartDate);
		/*
		 * End Date
		 */
		x++;
		JLabel lblEnd = new JLabel("End :");
		panTop.add(lblEnd, GridC.getc(x, y).west().insets(10, 10, 10, 10));
		x++;
		endDate.setDateInt(params.getEndDate());
		endDate.setDisabledTextColor(Color.BLACK);
		strTip = "<html>Enter or select the end date for your budget.";
		strTip += "<br>Note: End date must start on 31st December if chosen Budget is Annual,";
		strTip+= " <br>last day of the Month if Monthly, and a Saturday if weekly or bi-weekly</html>";
		endDate.setToolTipText(strTip);
		panTop.add(endDate, GridC.getc(x, y).west().insets(10, 10, 10, 10));
		endDate.setInputVerifier(new InputVerifier() {
			@Override
			public boolean verify(JComponent jcField) {
				JDateField jdtEnd = (JDateField) jcField;
				Calendar dtStart = Calendar.getInstance();
				Calendar dtEnd = Calendar.getInstance();
				dtStart.setTime(startDate.getDate());
				dtEnd.setTime(jdtEnd.getDate());
				switch (budget.getPeriodOrder()) {
				case Constants.PERIODANNUAL:
					if (dtEnd.get(Calendar.MONTH) != Calendar.DECEMBER
							|| dtEnd.get(Calendar.DAY_OF_MONTH) != 31) {
						JFrame fTemp = new JFrame();
						JOptionPane
								.showMessageDialog(fTemp,
										"Budget is annual, End Date must be 31st December");
						endError = true;
						endDate.setBorder(invalidBorder);
						return true;
					}
					break;
				case Constants.PERIODMONTHLY:
					if (dtEnd.get(Calendar.DAY_OF_MONTH) != dtEnd
							.getActualMaximum(Calendar.DAY_OF_MONTH)) {
						JFrame fTemp = new JFrame();
						JOptionPane
								.showMessageDialog(fTemp,
										"Budget is monthly, End Date must be Last day of month");
						endError = true;
						endDate.setBorder(invalidBorder);
						return true;
					}
					break;
				case Constants.PERIODWEEKLY:
				case Constants.PERIODBIWEEKLY:
					if (dtEnd.get(Calendar.DAY_OF_WEEK) != Calendar.SATURDAY) {
						JFrame fTemp = new JFrame();
						JOptionPane
								.showMessageDialog(fTemp,
										"Budget is Weekly/Bi-Weekly, End Date must be a Saturday");
						endError = true;
						endDate.setBorder(invalidBorder);
						return true;
					}
					break;
				}
				dtStart.add(Calendar.YEAR, 1);
				dtStart.add(Calendar.DAY_OF_YEAR, -1);
				if (dtEnd.after(dtStart)) {
					JFrame fTemp = new JFrame();
					JOptionPane
							.showMessageDialog(fTemp,
									"End Date can not be beyond 1 year after start date");
					endError = true;
					endDate.setBorder(invalidBorder);
					return true;
				}
				endError = false;
				endDate.setBorder(validBorder);
				params.setEndDate(jdtEnd.getDateInt());
				return true;
			}
		});
		/*
		 * years to generate
		 */
		x = 0;
		y++;
		JLabel lblYearsl = new JLabel("Years:");
		lblYearsl.setHorizontalAlignment(SwingConstants.RIGHT);
		panTop.add(lblYearsl, GridC.getc(x, y).west().insets(10, 10, 10, 10));

		x++;
		boxYears = new JComboBox<>();
		boxYears.setModel(new DefaultComboBoxModel<>(new String[]{"1",
                "2", "3"}));
		boxYears.setSelectedIndex(0);
		boxYears.setToolTipText("Determines how many columns are shown");
		panTop.add(boxYears, GridC.getc(x, y).west().insets(10, 10, 10, 10));
		boxYears.addActionListener(e -> changeYears());
		/*
		 * RPI
		 */
		x++;
		JLabel lblRPIl = new JLabel("RPI:");
		lblRPIl.setHorizontalAlignment(SwingConstants.RIGHT);
		panTop.add(lblRPIl, GridC.getc(x, y).west().insets(10, 10, 10, 10));

		x++;
		txtRPI = new JFormattedTextField();
		txtRPI.setInputVerifier(new InputVerifier() {
			@Override
			public boolean verify(JComponent input) {
				double dTemp;
				JFormattedTextField ftf = (JFormattedTextField) input;
				String text = ftf.getText();
				try {
					dTemp = Double.parseDouble(text);
				} catch (NumberFormatException pe) {
					if (text.endsWith("%"))
						text = text.substring(0, text.length() - 1);
					try {
						dTemp = Double.parseDouble(text);
					} catch (NumberFormatException pe2) {
						JFrame fTemp = new JFrame();
						JOptionPane.showMessageDialog(fTemp,
								"Invalid RPI amount");
						rpiError = true;
						txtRPI.setBorder(invalidBorder);
						return true;
					}
				}
				if (dTemp < -100.00 || dTemp > 100.00) {
					JFrame fTemp = new JFrame();
					JOptionPane.showMessageDialog(fTemp,
							"RPI amount must be within -100 to +100");
					rpiError = true;
					txtRPI.setBorder(invalidBorder);
					return true;
				}
				try {
					params.setRPI(Double.parseDouble(text));
					txtRPI.setValue(String.format("%1$,.2f%%",
							params.getRPI()));
					rpiError = false;
					txtRPI.setBorder(validBorder);
				} catch (NumberFormatException pe) {
					rpiError = true;
					txtRPI.setBorder(invalidBorder);
				}
				return true;
			}
		});
		txtRPI.setValue(String.format("%1$,.2f%%", params.getRPI()));
		txtRPI.setColumns(10);
		txtRPI.setToolTipText("<html>RPI must be between -100 and +100.<br>  It is used to increase the amount in years 2 and 3</html>");
		txtRPI.addPropertyChangeListener("value", e -> {
            JFormattedTextField source = (JFormattedTextField) e
                    .getSource();
            String strTemp = (String) source.getValue();
            if (strTemp.endsWith("%")) {
                strTemp = strTemp.substring(0, strTemp.length() - 1);
            }
            try {
                params.setRPI(Double.parseDouble(strTemp));
                source.setValue(String.format("%1$,.2f%%",
                        params.getRPI()));
                rpiError = false;
                txtRPI.setBorder(validBorder);
            } catch (NumberFormatException pe) {
                rpiError = true;
                txtRPI.setBorder(invalidBorder);
            }
        });

		panTop.add(txtRPI, GridC.getc(x, y).west().insets(10, 10, 10, 10));
		this.add(panTop, BorderLayout.PAGE_START);

		/*
		 * Middle panel - table
		 */
		spScrollPane = new JScrollPane(budgetTable);
		panMid = new JPanel(new GridLayout(1, 1));
		panMid.setSize(iMIDWIDTH, iMIDDEPTH);
		panMid.add(spScrollPane);
		this.add(panMid, BorderLayout.CENTER);
		/*
		 * Bottom Panel - buttons
		 */
		panBot = new JPanel(new GridBagLayout());
		panBot.setSize(iBOTWIDTH, Constants.BOTDEPTH);
		/*
		 * Button 0 - Add Account
		 */
		x = 0;
		y = 0;
		btnAddAccount = new JButton("Add Category");
		btnAddAccount.setToolTipText("Allows you to add any categories not included in the list above");
		btnAddAccount.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                addAccount();
        });
		panBot.add(btnAddAccount,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));
		/*
		 * Button 1 - Select All
		 */
		x++;
		btnSelectAll = new JButton("Select All");
		btnSelectAll.setToolTipText("Selects every line that is valid");
		btnSelectAll.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                selectAll();
        });
		panBot.add(btnSelectAll,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));
		/*
		 * Button 2 - Calculate Selected
		 */
		x++;
		btnCalculateSelected = new JButton("Calculate \r\nSelected");
		btnCalculateSelected.setToolTipText("Calculates the Year 1, 2 and 3 amounts for the selected lines");
		btnCalculateSelected.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                calculateSelected();
        });
		panBot.add(btnCalculateSelected, GridC.getc(x, y).west().fillx()
				.insets(15, 15, 15, 15));
		/*
		 * Button 8 - Save
		 */
		x++;
		btnSave = new JButton("Save Parameters");
		btnSave.setToolTipText("Saves the parameters. You will be asked for a file name");
		btnSave.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                save();
        });
		panBot.add(btnSave,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));
		/*
		 * Button 4 - Close
		 */
		x++;
		btnClose = new JButton("Close");
		btnClose.setToolTipText("<html>Closes the window.  If the parameters have been changed<br> you will be asked if you wish to save them.<br> You will be asked for a file name</html>");
		btnClose.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                int iResult = JOptionPane.showConfirmDialog(fTemp,
                        "There are errors, do you wish to close anyway?");
                if (iResult == JOptionPane.YES_OPTION)
                    close();
            } else
                close();
        });
		panBot.add(btnClose,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));
		/*
		 * Button 3 - Delete Selected
		 */
		x = 0;
		y++;
		btnDeleteSelected = new JButton("Delete Selected");
		btnDeleteSelected.setToolTipText("Deletes the selected lines from the parameters");
		btnDeleteSelected.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                deleteSelected();
        });
		panBot.add(btnDeleteSelected,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));
		/*
		 * Button 5 - De-Select All
		 */
		x++;
		btnDeselectAll = new JButton("Deselect All");
		btnDeselectAll.setToolTipText("Unsets the select flag on all lines");
		btnDeselectAll.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                deselectAll();
        });
		panBot.add(btnDeselectAll,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));
		/*
		 * Button 6 - Calculate All
		 */
		x++;
		btnCalculateAll = new JButton("Calculate \r\nAll");
		btnCalculateAll.setToolTipText("Calculates the Year 1, 2 and 3 amounts for all lines with an amount");
		btnCalculateAll.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                calculateAll();
        });

		panBot.add(btnCalculateAll,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));

		/*
		 * Button 7 - Generate values
		 */
		x++;
		btnGenerate = new JButton("Generate");
		strTip = "<html>Generates the Budget Item Amounts for all lines based on the data in the table";
		strTip+="<br>If you have previously entered the figures manually you will overwrite them.";
		strTip+="<br>You will be asked to confirm this</html>";
		btnGenerate.setToolTipText(strTip);
		btnGenerate.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                generate();
        });
		panBot.add(btnGenerate,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));

		x++;
		btnEdit = new JButton("Enter Manually");
		strTip = "Allows you to enter the Budget Item amounts manually";
		btnEdit.setToolTipText(strTip);
		btnEdit.addActionListener(e -> {
            if (startError || endError || rpiError) {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp,
                        "Please correct errors");
            } else
                editfigures();
        });
		panBot.add(btnEdit,
				GridC.getc(x, y).west().fillx().insets(15, 15, 15, 15));

		this.add(panBot, BorderLayout.PAGE_END);
		budgetModel.fireTableDataChanged();
		/*
		 * Set dirty back to false so real changes are caught
		 */
		params.resetDirty();
	}

	/*
	 * When period is changed update dates to reflect new start and end dates
	 */
	public void changeDates() {
		GridBagConstraints con = new GridBagConstraints();
		if (boxPeriod.getSelectedItem().equals(Constants.PERIOD_FISCAL)) {
			startDate.setDate(fiscalStart.getDate());
			endDate.setDate(fiscalEnd.getDate());
		} else if (boxPeriod.getSelectedItem()
				.equals(Constants.PERIOD_CALENDAR)) {
			startDate.setDate(startYear.getDate());
			endDate.setDate(endYear.getDate());
		}
		/*
		 * update budget lines with new start date
		 */
		List<BudgetLine> listLines = params.getLines();
		for (BudgetLine objBline : listLines) {
			objBline.setStartDate(startDate.getDateInt());
		}
		/*
		 * set parameters
		 */
		params.setStartDate(startDate.getDateInt());
		params.setEndDate(endDate.getDateInt());
		/*
		 * Remove and Add back dates to update panel
		 */
		panTop.remove(startDate);
		panTop.validate();
		con.gridwidth = 1;
		con.gridheight = 1;
		con.anchor = GridBagConstraints.FIRST_LINE_START;
		con.insets = new Insets(10, 10, 10, 10);
		con.gridx = 1;
		con.gridy = 1;
		startDate.setDisabledTextColor(Color.BLACK);
		panTop.add(startDate, con);
		startDate.setEnabled(false);
		panTop.remove(endDate);
		GridBagConstraints conend = new GridBagConstraints();
		conend.insets = new Insets(10, 10, 10, 10);
		conend.gridx = 3;
		conend.gridy = 1;
		conend.anchor = GridBagConstraints.FIRST_LINE_START;
		conend.gridwidth = 1;
		conend.gridheight = 1;
		endDate.setDisabledTextColor(Color.BLACK);
		panTop.add(endDate, conend);
		endDate.setEnabled(false);
		panTop.validate();
		panTop.repaint();
		budgetModel.fireTableDataChanged();
	}

	/*
	 * When period is changed update dates to reflect new start and end dates
	 */
	public void changeStartDate(PropertyChangeEvent e) {
		Calendar dtTemp = Calendar.getInstance();
		JDateField jdtStart = (JDateField) e.getSource();
		/*
		 * do not do anything if date has not changed
		 */
		if (jdtStart.parseDateInt() == params.getStartDate())
			return;
		dtTemp.setTime(jdtStart.getDate());
		dtTemp.add(Calendar.YEAR, 1);
		dtTemp.add(Calendar.DAY_OF_YEAR, -1);
		endDate.setDate(dtTemp.getTime());
		/*
		 * update budget lines with new start date
		 */
		List<BudgetLine> listLines = params.getLines();
		for (BudgetLine objBline : listLines) {
			objBline.setStartDate(startDate.getDateInt());
		}
		/*
		 * set parameters
		 */
		params.setStartDate(startDate.getDateInt());
		params.setEndDate(endDate.getDateInt());
		endDate.revalidate();
		budgetModel.fireTableDataChanged();
	}

	/*
	 * when the number of years has been changed add/remove table columns (done
	 * in table model) adjust screen sizes
	 */
	private void changeYears() {
		int iYears = boxYears.getSelectedIndex() + 1;
		budgetModel.alterYears(iYears);
		panTop.setSize(iTOPWIDTH + (iYears - 1) * 100, Constants.TOPDEPTH);
		panMid.setSize(iMIDWIDTH + (iYears - 1) * 100, iMIDDEPTH);
		panBot.setSize(iBOTWIDTH + (iYears - 1) * 100, Constants.BOTDEPTH);
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.setSize(Constants.FRAMEWIDTH + (iYears - 1) * 100,
				Constants.FRAMEDEPTH);
		topFrame.invalidate();
		topFrame.validate();
		budgetTable.resetCombo(iYears);

	}

	/*
	 * Button actions
	 * 
	 * Add Accounts - creates new window of Expense Categories not in the Budget
	 * Lines
	 */
	private void addAccount() {
		if (params.getMissing().isEmpty()) {
			JFrame fTemp = new JFrame();
			JOptionPane.showMessageDialog(fTemp,
					"No more categories available.  Please add using Tools/Categories and restart the extension.");
			return;
		}
		// Schedule a job for the event dispatch thread:
		// creating and showing this application's GUI.
		javax.swing.SwingUtilities.invokeLater(() -> {
            showAddAccountsWindow();
            budgetModel.fireTableDataChanged();
        });
	}

	/**
	 * Display the add accounts window
	 */
	private void showAddAccountsWindow() {

		// Create and set up the window.
		JFrame frame = new JFrame(
				"Moneydance Budget Generator - Add missing Categories");
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		frame.setPreferredSize(new Dimension(Constants.ADDSCREENWIDTH,
				Constants.ADDSCREENHEIGHT));
		panAcct = new AddAccountsWindow(params);
		frame.getContentPane().add(panAcct);

		// Display the window.
		frame.pack();
		frame.setVisible(true);

	}

	/*
	 * Select all lines - sets Selected to true for all lines
	 */
	private void selectAll() {
		for (BudgetLine objLine : params.getLines()) {
			objLine.setSelect(true);
		}
		budgetModel.fireTableDataChanged();
		panMid.invalidate();
	}

	/*
	 * Deselect all lines - sets Selected to false for all lines
	 */
	private void deselectAll() {
		for (BudgetLine objLine : params.getLines()) {
			objLine.setSelect(false);
		}
		budgetModel.fireTableDataChanged();
		panMid.revalidate();
	}

	/*
	 * calculate selected lines - use Budget Parameters to do this work
	 */
	private void calculateSelected() {

		if (!params.calculateSelected()) {
			JFrame fTemp = new JFrame();
			JOptionPane.showMessageDialog(fTemp, "No lines to calculate");
		}
		budgetModel.fireTableDataChanged();
		panMid.revalidate();
	}

	/*
	 * calculate all lines - use Budget Parameters to do this work
	 */
	private void calculateAll() {
		if (!params.calculateAll()) {
			JFrame fTemp = new JFrame();
			JOptionPane.showMessageDialog(fTemp, "No lines to calculate");
		}
		budgetModel.fireTableDataChanged();
		panMid.revalidate();
	}

	/*
	 * delete selected lines, asks for confirmation
	 */
	private void deleteSelected() {
		JFrame fTemp = new JFrame();
		List<BudgetLine> listLines = params.getLines();
		/*
		 * determine if there are any lines to delete
		 */
		boolean bFound = false;
		for (BudgetLine objLine : listLines) {
			if (objLine.getSelect()) {
				bFound = true;
				break;
			}
		}
		if (!bFound) {
			JOptionPane.showMessageDialog(fTemp, "No lines to delete");
			return;
		}
		int iResult = JOptionPane.showConfirmDialog(fTemp,
				"Are you sure you wish to delete the selected items?");
		if (iResult == JOptionPane.YES_OPTION) {
			boolean bSelected = true;
			while (bSelected) {
				bSelected = false;
				for (int i = 0; i < listLines.size(); i++) {
					if (params.getItem(i).getSelect()) {
						if (i < listLines.size() - 1
								&& params
										.getItem(i + 1)
										.getParent()
										.equals(params.getItem(i)
												.getCategoryIndent())) {
							JOptionPane
									.showMessageDialog(fTemp,
											"You can not delete a line that has children");
							break;
						}
						params.deleteLine(i);
						bSelected = true;
						/*
						 * listLines has changed, need to reload and reiterate
						 * the list
						 */
						listLines = params.getLines();
						break;
					}
				}
			}
			params.setDirty(true);
			budgetModel.fireTableDataChanged();
			panMid.revalidate();
		}
	}

	/*
	 * Generate Budget Items using lines
	 */
	private void generate() {
		if (params.getManual()) {
			JFrame fTemp = new JFrame();
			int iResult = JOptionPane
					.showConfirmDialog(
							fTemp,
							"The budget values have been updated manually.  Do you wish to overwrite these values?");
			if (iResult == JOptionPane.NO_OPTION) {
				return;
			}
		}
		// Create and set up the window.
		JFrame frame = new JFrame(
				"Moneydance Budget Generator - Generated Figures");
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		panGen = new GenerateWindow(boxYears.getSelectedIndex(), iType,
				params, Constants.GENERATE);
		frame.getContentPane().add(panGen);

		// Display the window.
		frame.getContentPane().setPreferredSize(
				new Dimension(panGen.iGENSCREENWIDTH, panGen.iGENSCREENHEIGHT));
		frame.setTitle("Budget Items - Build "+Main.buildNum);
		if (Main.imgIcon != null)
			frame.setIconImage(Main.imgIcon);
		frame.pack();
		if (Main.imgIcon != null)
			frame.setIconImage(Main.imgIcon);
		frame.setVisible(true);

	}

	/*
	 * Generate Budget Items using lines
	 */
	private void editfigures() {
		// Create and set up the window.
		JFrame frame = new JFrame(
				"Moneydance Budget Generator - Generated Figures");
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		panGen = new GenerateWindow(boxYears.getSelectedIndex(), iType,
				params, Constants.MANUAL);
		frame.getContentPane().add(panGen);

		// Display the window.
		frame.getContentPane().setPreferredSize(
				new Dimension(panGen.iGENSCREENWIDTH, panGen.iGENSCREENHEIGHT));
		frame.pack();
		frame.setVisible(true);

	} /*
	 * Close the window checking for data changes first. Give user chance to
	 * save the data
	 */

	public void close() {
		if (params.isDirty()) {
			JFrame fTemp = new JFrame();
			int iResult = JOptionPane
					.showConfirmDialog(fTemp,
							"The parameters have been changed.  Do you wish to save them?");
			if (iResult == JOptionPane.YES_OPTION) {
				params.saveParams();
			}
		}
		/*
		 * check if other windows are open
		 */
		if (panAcct != null) {
			panAcct.setVisible(false);
			JFrame AcctFrame = (JFrame) SwingUtilities
					.getWindowAncestor(panAcct);
			AcctFrame.dispose();
		}
		if (panGen != null) {
			panGen.setVisible(false);
			JFrame GenFrame = (JFrame) SwingUtilities.getWindowAncestor(panGen);
			GenFrame.dispose();
		}
		this.setVisible(false);
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.dispose();
	}

	/*
	 * save parameters at user request
	 */
	private void save() {
		params.saveParams();
	}

	/*
	 * preferences
	 */
	private void setPreferences() {
		String strType = iType == 1 ? "exp" : "inc";
		iFRAMEWIDTH = preferences.getInt(Constants.PROGRAMNAME+"."+Constants.FRAMEWIDTHKEY+strType,-1);
		iFRAMEDEPTH = preferences.getInt(Constants.PROGRAMNAME+"."+Constants.FRAMEDEPTHKEY+strType,-1);
		if (iFRAMEWIDTH < 0 || iFRAMEDEPTH < 0 ) {
			regRoot = Preferences.userRoot();
			regPreferences = regRoot
					.node("com.moneydance.modules.features.budgetgen.budgetvalueswindow");
			iFRAMEWIDTH = regPreferences.getInt(Constants.FRAMEWIDTHKEY + strType,
					Constants.FRAMEWIDTH);
			iFRAMEDEPTH = regPreferences.getInt(Constants.FRAMEDEPTHKEY + strType,
					Constants.FRAMEDEPTH);
			updatePreferences(new Dimension(iFRAMEWIDTH,iFRAMEDEPTH));
			try {
				regPreferences.removeNode();
			} catch (BackingStoreException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		iTOPWIDTH = iFRAMEWIDTH - 100;
		iBOTWIDTH = iFRAMEWIDTH - 100;
		iMIDWIDTH = iFRAMEWIDTH;
		iMIDDEPTH = iFRAMEDEPTH - Constants.BOTDEPTH - Constants.TOPDEPTH;
	}

	private void updatePreferences(Dimension objDim) {
		String strType = iType == 1 ? "exp" : "inc";
		preferences.put(Constants.PROGRAMNAME+"."+Constants.FRAMEWIDTHKEY + strType, objDim.width);
		preferences.put(Constants.PROGRAMNAME+"."+Constants.FRAMEDEPTHKEY + strType, objDim.height);
		setPreferences();
		preferences.isDirty();
	}
}
