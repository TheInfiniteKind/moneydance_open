/*
 * Copyright (c) 2023, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload.view;

import java.awt.Dimension;
import java.awt.FileDialog;
import java.awt.Font;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.Point;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.util.Objects;

import javax.swing.*;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

import com.infinitekind.util.DateUtil;
import com.moneydance.apps.md.view.gui.MDColors;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;
import com.moneydance.modules.features.securityquoteload.MainPriceWindow;

public class ParameterTab extends DisplayTab {
	private JLabel fileName;
	private JComboBox<Integer> decimalComBo;
	private JComboBox<String> timeCombo;
	private JDateField secNextRunDate;
	private JDateField curNextRunDate;
	private MyCheckBox historyCB;
	private MyCheckBox zeroCB;
	private MyCheckBox currencyCB;
	private MyCheckBox addVolumeCB;
	private MyCheckBox overridePriceCB;
	private MyCheckBox exportSave;
	private MyCheckBox exportAuto;
	private JButton changeExport;
	private JRadioButton curSamePage;
	private JRadioButton curSepTab;
	private ButtonGroup curButtons;
	private JRadioButton conOff;
	private JRadioButton conInfo;
	private JRadioButton conSummary;
	private JRadioButton conDetailed;
	private JRadioButton conDeveloper;
	private ButtonGroup conOption;
	private JComboBox<String> secAutorunCombo;
	private JComboBox<String> curAutorunCombo;
	private JComboBox<String> historyPeriod;
	private JButton secCalendarBtn;
	private JButton curCalendarBtn;
	private Image calendarIcon;
	private JButton autoResetBtn;
	private JButton saveParams;
	private JButton cancelParams;
	private int gridx = 0;
	private int gridy = 0;
	private String exportFolder;
	private MDColors colors;
	private JLabel runLbl=new JLabel();
	private Boolean saveAutoChange;
	private JLabel alphaLbl;
	private JTextField alphaKey;
	private JComboBox<Integer> alphaPlanCombo;
	private JLabel uaLabel;
	private JTextField uaParam;
  private MyCheckBox throttleYahooTF; // readonly setting (for info)
	private JLabel mdLbl;
	private JTextField mdToken;

	public ParameterTab(Parameters params, Main main, MainPriceWindow controller) {
		super(params, main, controller);
		mainPanel = new JPanel(new GridBagLayout());
		this.getViewport().add(mainPanel);
		saveAutoChange= Main.autoSettingsChanged;
		mainPanel.setBorder(mainBorder);
		mainPanel.setAlignmentX(LEFT_ALIGNMENT);
		mainPanel.setAlignmentY(TOP_ALIGNMENT);
		colors=MDColors.getSingleton();

		mainPanel.setLayout(new GridBagLayout());
		calendarIcon = main.getIcon(Constants.CALENDARIMAGE);

		/*
		 * Auto Run Combos
		 */
		final int startTime = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.STARTTIME,
				Constants.RUNSTARTUP);
		timeCombo = new JComboBox<>(Constants.TIMETEXT);
		for (int i = 0; i < Constants.TIMEVALUES.length; i++) {
			if (Constants.TIMEVALUES[i] == startTime)
				timeCombo.setSelectedIndex(i);
		}

		final String secMode = Main.preferences.getString(Constants.PROGRAMNAME + "." + Constants.SECRUNMODE,
				Constants.MANUALMODE);
		final String secRunperiod = Main.preferences.getString(Constants.PROGRAMNAME + "." + Constants.SECRUNTYPE,
				Constants.RUNYEARLY);
		secAutorunCombo = new JComboBox<>(Constants.AUTOTEXT);
		if (secMode.equals(Constants.MANUALMODE))
			secAutorunCombo.setSelectedIndex(0);
		else {
			switch (secRunperiod) {
			case Constants.RUNDAILY:
				secAutorunCombo.setSelectedIndex(1);
				break;
			case Constants.RUNWEEKLY:
				secAutorunCombo.setSelectedIndex(2);
				break;
			case Constants.RUNMONTHLY:
				secAutorunCombo.setSelectedIndex(3);
				break;
			case Constants.RUNQUARTERLY:
				secAutorunCombo.setSelectedIndex(4);
				break;
			case Constants.RUNYEARLY:
				secAutorunCombo.setSelectedIndex(5);
				break;
			}
		}
		final String curMode = Main.preferences.getString(Constants.PROGRAMNAME + "." + Constants.CURRUNMODE,
				Constants.MANUALMODE);
		final String curRunperiod = Main.preferences.getString(Constants.PROGRAMNAME + "." + Constants.CURRUNTYPE,
				Constants.RUNYEARLY);
		curAutorunCombo = new JComboBox<>(Constants.AUTOTEXT);
		if (curMode.equals(Constants.MANUALMODE))
			curAutorunCombo.setSelectedIndex(0);
		else {
			switch (curRunperiod) {
			case Constants.RUNDAILY:
				curAutorunCombo.setSelectedIndex(1);
				break;
			case Constants.RUNWEEKLY:
				curAutorunCombo.setSelectedIndex(2);
				break;
			case Constants.RUNMONTHLY:
				curAutorunCombo.setSelectedIndex(3);
				break;
			case Constants.RUNQUARTERLY:
				curAutorunCombo.setSelectedIndex(4);
				break;
			case Constants.RUNYEARLY:
				curAutorunCombo.setSelectedIndex(5);
				break;
			}
		}
		timeCombo.addActionListener(e -> {
      @SuppressWarnings("unchecked")
      JComboBox<String> cbRun = (JComboBox<String>) e.getSource();
      int runTime = Constants.TIMEVALUES[cbRun.getSelectedIndex()];

      Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.STARTTIME, runTime);
      Main.preferences.isDirty();
      Main.autoSettingsChanged=true;
      runLbl.setForeground(colors.errorMessageForeground);
      Main.debugInst.debug("ParameterTab", "actionPerformed", MRBDebug.INFO, ">> auto run time changed to: " + cbRun.getSelectedItem());
    });
		secAutorunCombo.addActionListener(e -> {
      @SuppressWarnings("unchecked")
      JComboBox<String> cbRun = (JComboBox<String>) e.getSource();
      String modeStr = Constants.MANUALMODE;
      String runperiodStr = "";
      switch (cbRun.getSelectedIndex()) {
      case 0:
        modeStr = Constants.MANUALMODE;
        runperiodStr = "";
        break;
      case 1:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNDAILY;
        break;
      case 2:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNWEEKLY;
        break;
      case 3:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNMONTHLY;
        break;
      case 4:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNQUARTERLY;
        break;
      case 5:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNYEARLY;
        break;
      }
      Main.autoSettingsChanged=true;
      runLbl.setForeground(colors.errorMessageForeground);
      Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.SECRUNMODE, modeStr);
      Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.SECRUNTYPE, runperiodStr);
      Main.preferences.isDirty();
      if (modeStr.equals(Constants.AUTOMODE)) {
        showCalendar(Constants.SECRUNTYPE, Constants.SECRUNPARAM);
        int newDate = calculateNextRunDate(Constants.SECRUNTYPE, Constants.SECRUNPARAM,
            Constants.SECLASTRUN);
        if (newDate != 0)
          secNextRunDate.setDateInt(newDate);
      }
      Main.debugInst.debug("ParameterTab", "actionPerformed", MRBDebug.INFO, ">> security run mode changed to: " + cbRun.getSelectedItem());
    });
		curAutorunCombo.addActionListener(e -> {
      @SuppressWarnings("unchecked")
      JComboBox<String> cbRun = (JComboBox<String>) e.getSource();
      String modeStr = Constants.MANUALMODE;
      String runperiodStr = "";
      switch (cbRun.getSelectedIndex()) {
      case 0:
        modeStr = Constants.MANUALMODE;
        runperiodStr = "";
        break;
      case 1:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNDAILY;
        break;
      case 2:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNWEEKLY;
        break;
      case 3:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNMONTHLY;
        break;
      case 4:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNQUARTERLY;
        break;
      case 5:
        modeStr = Constants.AUTOMODE;
        runperiodStr = Constants.RUNYEARLY;
        break;
      }
      Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.CURRUNMODE, modeStr);				;
      Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.CURRUNTYPE, runperiodStr);
      Main.preferences.isDirty();
      Main.autoSettingsChanged=true;
      runLbl.setForeground(colors.errorMessageForeground);
      if (modeStr.equals(Constants.AUTOMODE)) {
        showCalendar(Constants.CURRUNTYPE, Constants.CURRUNPARAM);
        int newDate = calculateNextRunDate(Constants.CURRUNTYPE, Constants.CURRUNPARAM,
            Constants.CURLASTRUN);
        if (newDate != 0)
          curNextRunDate.setDateInt(newDate);
      }
      Main.debugInst.debug("ParameterTab", "actionPerformed", MRBDebug.INFO, ">> currency run mode changed to: " + cbRun.getSelectedItem());
    });
		/*
		 * Button Calendar
		 */
		secCalendarBtn = new JButton();
		if (calendarIcon == null)
			secCalendarBtn.setText("Calendar");
		else
			secCalendarBtn.setIcon(new ImageIcon(calendarIcon));
		secCalendarBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				showCalendar(Constants.SECRUNTYPE, Constants.SECRUNPARAM);
				int newDate = calculateNextRunDate(Constants.SECRUNTYPE, Constants.SECRUNPARAM,
						Constants.SECLASTRUN);
				if (newDate != 0) {
					secNextRunDate.setDateInt(newDate);
					Main.autoSettingsChanged=true;
					runLbl.setForeground(colors.errorMessageForeground);
				}
			}
		});
		curCalendarBtn = new JButton();
		if (calendarIcon == null)
			curCalendarBtn.setText("Calendar");
		else
			curCalendarBtn.setIcon(new ImageIcon(calendarIcon));
		curCalendarBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				showCalendar(Constants.CURRUNTYPE, Constants.CURRUNPARAM);
				int newDate = calculateNextRunDate(Constants.CURRUNTYPE, Constants.CURRUNPARAM,
						Constants.CURLASTRUN);
				if (newDate != 0) {
					curNextRunDate.setDateInt(newDate);
					Main.autoSettingsChanged=true;
					runLbl.setForeground(colors.errorMessageForeground);
				}
			}
		});
		runLbl.setText(
				"<html>Automatic Running - Note changes to these fields will be saved automatically. Click on 'Recalculate Next Run' to enable them. <br>If text is Red, changes have been made without clicking on 'Recalculate Next Run</html>");
		JLabel timeLbl = new JLabel("Time of Run");
		JLabel secRunLbl = new JLabel("Securities");
		mainPanel.add(runLbl, GridC.getc(gridx, gridy).west().colspan(8).insets(10, 5, 10, 5));
		gridx = 1;
		gridy++;
		mainPanel.add(timeLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		mainPanel.add(timeCombo, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		mainPanel.add(secRunLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		mainPanel.add(secAutorunCombo, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx += 2;
		JLabel curRunLbl = new JLabel("Exchange Rates");
		mainPanel.add(curRunLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		mainPanel.add(curAutorunCombo, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx = 3;
		gridy++;
		String lastRunStr = Main.cdate
				.format(Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.SECLASTRUN, 0));
		JLabel secDateLbl = new JLabel("Last Run " + lastRunStr);
		mainPanel.add(secDateLbl, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx += 3;
		lastRunStr = Main.cdate
				.format(Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CURLASTRUN, 0));
		JLabel curDateLbl = new JLabel("Last Run " + lastRunStr);
		mainPanel.add(curDateLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx = 1;
		gridy++;
		autoResetBtn = new JButton("Recalculate Next Run");
		autoResetBtn.setToolTipText("Click to restart the Auto Run facility after changing the Auto Run fields");
		autoResetBtn.addActionListener(e -> SwingUtilities.invokeLater(() -> {
      Main.autoSettingsChanged=false;
      runLbl.setForeground(colors.defaultTextForeground);
      Main.context.showURL("moneydance:fmodule:" + Constants.PROGRAMNAME + ":" + Constants.CHECKAUTOCMD);
    }));
		mainPanel.add(autoResetBtn, GridC.getc(gridx, gridy).east().insets(5, 5, 5, 0));
		gridx += 2;
		JPanel secNextRunPane = new JPanel();
		secNextRunDate = new JDateField(Main.cdate, 10);
		secNextRunDate.addPropertyChangeListener(arg0 -> {
      if (arg0.getPropertyName().equalsIgnoreCase(JDateField.PROP_DATE_CHANGED)) {
        JDateField date = (JDateField) arg0.getSource();
        setNextRunDate(date, Constants.SECNEXTRUN);
        Main.autoSettingsChanged=true;
        runLbl.setForeground(colors.errorMessageForeground);
        Main.debugInst.debug("ParameterTab", "actionPerformed", MRBDebug.INFO, ">> security next date set to: " + date.getDateInt());
      }
    });
		secNextRunDate.setDateInt(DateUtil.getStrippedDateInt());
		if (!secMode.equals(Constants.MANUALMODE)) {
			secNextRunDate.setDateInt(Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.SECNEXTRUN,
					DateUtil.getStrippedDateInt()));
		}
		JLabel secNextRunLbl = new JLabel("Next Run");
		mainPanel.add(secNextRunLbl, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx++;
		secNextRunPane.add(secNextRunDate);
		secNextRunPane.add(secCalendarBtn);
		mainPanel.add(secNextRunPane, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx += 2;
		JPanel curNextRunPane = new JPanel();
		curNextRunDate = new JDateField(Main.cdate, 10);	
		curNextRunDate.addPropertyChangeListener(arg0 -> {
      if (arg0.getPropertyName().equalsIgnoreCase(JDateField.PROP_DATE_CHANGED)) {
        JDateField date = (JDateField) arg0.getSource();
        setNextRunDate(date, Constants.CURNEXTRUN);
        Main.autoSettingsChanged=true;
        runLbl.setForeground(colors.errorMessageForeground);
        Main.debugInst.debug("ParameterTab", "actionPerformed", MRBDebug.INFO, ">> currency next date set to: " + date.getDateInt());
      }
    });
		curNextRunDate.setDateInt(DateUtil.getStrippedDateInt());
		if (!curRunperiod.equals(Constants.MANUALMODE)) {
			curNextRunDate.setDateInt(Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CURNEXTRUN,
					DateUtil.getStrippedDateInt()));
		}
		JLabel curNextRunLbl = new JLabel("Next Run");
		mainPanel.add(curNextRunLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		curNextRunPane.add(curNextRunDate);
		curNextRunPane.add(curCalendarBtn);
		mainPanel.add(curNextRunPane, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx = 0;
		gridy++;
		JSeparator sepLine = new JSeparator(JSeparator.HORIZONTAL);
		sepLine.setPreferredSize(new Dimension(50, 4));
		sepLine.setBackground(borderColour);
		mainPanel.add(sepLine, GridC.getc(gridx, gridy).fillx().center().colspan(8).insets(5, 5, 5, 0));
		/*
		 * Parameter Fields
		 */

		gridy++;
		JLabel securitiesLbl = new JLabel("Securities");
		mainPanel.add(securitiesLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 5));
		gridx++;
		gridy++;
		zeroCB = new MyCheckBox("Include Securities with no holdings?");
		zeroCB.setToolTipText(
				"If selected any security that does not have any holdings but has 'Show on summary page' set will be loaded");
		zeroCB.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox zeroT = (JCheckBox) e.getSource();
				params.setZero(zeroT.isSelected());
				String[] parms = new String[1];
				parms[0] = "0";
				controller.processAction(Constants.MAINACTIONS.CHANGEZERO, parms);

			}
		});
		Font cbFont = zeroCB.getFont();
		int style = cbFont.getStyle();
		style &= ~Font.BOLD;
		cbFont = cbFont.deriveFont(style);
		zeroCB.setFont(cbFont);
		zeroCB.setHorizontalTextPosition(SwingConstants.LEFT);
		mainPanel.add(zeroCB, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx += 2;
		addVolumeCB = new MyCheckBox();
		addVolumeCB.setToolTipText("Select to include volume data when saving price");
		addVolumeCB.setAlignmentX(LEFT_ALIGNMENT);
		addVolumeCB.setText("Save Volume Data if available");
		addVolumeCB.setHorizontalTextPosition(SwingConstants.LEFT);
		addVolumeCB.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox addVolumeT = (JCheckBox) e.getSource();
				params.setAddVolume(addVolumeT.isSelected());
			}
		});
		mainPanel.add(addVolumeCB, GridC.getc(gridx, gridy).colspan(2).west().insets(5, 5, 5, 0));
		gridx += 2;
		overridePriceCB = new MyCheckBox();
		overridePriceCB.setToolTipText("Select to override the current prices with the retrieved prices");
		overridePriceCB.setAlignmentX(LEFT_ALIGNMENT);
		overridePriceCB.setText("Update Moneydance Current Price");
		overridePriceCB.setHorizontalTextPosition(SwingConstants.LEFT);
		overridePriceCB.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox overridePriceT = (JCheckBox) e.getSource();
				params.setOverridePrice(overridePriceT.isSelected());
			}
		});
		mainPanel.add(overridePriceCB, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx = 1;
		gridy++;

		historyCB = new MyCheckBox("Retrieve Missed Prices");
		historyCB.setToolTipText("If selected prices since the last run will be retrieved.");
		historyCB.setFont(cbFont);
		;
		historyCB.setHorizontalTextPosition(SwingConstants.LEFT);
		historyCB.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox historyT = (JCheckBox) e.getSource();
				params.setHistory(historyT.isSelected());
			}
		});
		mainPanel.add(historyCB, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		JLabel historyLbl = new JLabel("Amount of Yahoo/AlphaVantage/MarketData History to collect");
		mainPanel.add(historyLbl, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx += 2;
		historyPeriod = new JComboBox<String>(Constants.HISTORYLIST);
		historyPeriod.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<String> historyTemp = (JComboBox<String>) e.getSource();
				params.setAmtHistory(historyTemp.getSelectedIndex());
			}
		});
		mainPanel.add(historyPeriod, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx = 0;
		gridy++;
		JLabel currencyLbl = new JLabel("Exchange Rates");
		mainPanel.add(currencyLbl, GridC.getc(gridx, gridy).colspan(2).west().insets(5, 5, 5, 5));
		gridy++;
		gridx = 1;

		currencyCB = new MyCheckBox("Include Exchange Rates");
		currencyCB.setToolTipText("If selected exchange rates with 'Show on summary Page' set will be loaded");
		currencyCB.setFont(cbFont);
		;
		currencyCB.setHorizontalTextPosition(SwingConstants.LEFT);
		currencyCB.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox chbCurrencyT = (JCheckBox) e.getSource();
				params.setCurrency(chbCurrencyT.isSelected());
				if (params.getCurrency()) {
					curSamePage.setVisible(true);
					curSepTab.setVisible(true);
				} else {
					curSamePage.setVisible(false);
					curSepTab.setVisible(false);
				}
				String[] parms = new String[1];
				parms[0] = "0";
				if (curSamePage.isSelected())
					parms[0] = String.valueOf(Constants.CurrencyDisplay.SAME.getNum());
				if (curSepTab.isSelected())
					parms[0] = String.valueOf(Constants.CurrencyDisplay.SEPARATE.getNum());
				controller.processAction(Constants.MAINACTIONS.CHANGECURDISPLAY, parms);
			}
		});
		mainPanel.add(currencyCB, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		JPanel curPlacePanel = new JPanel();
		curSamePage = new JRadioButton("Display on same tab as Securities");
		curSamePage.setHorizontalTextPosition(JRadioButton.LEFT);
		curSepTab = new JRadioButton("Display on separate tab");
		curSepTab.setHorizontalTextPosition(JRadioButton.LEFT);
		curButtons = new ButtonGroup();
		curButtons.add(curSamePage);
		curButtons.add(curSepTab);
		curSamePage.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JRadioButton samePageT = (JRadioButton) e.getSource();
				if (samePageT.isSelected()) {
					params.setDisplayOption(Constants.CurrencyDisplay.SAME);
					String[] parms = { String.valueOf(Constants.CurrencyDisplay.SAME.getNum()) };
					controller.processAction(Constants.MAINACTIONS.CHANGECURDISPLAY, parms);
				}
			}
		});
		curPlacePanel.add(curSamePage);
		curSepTab.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JRadioButton sepTabT = (JRadioButton) e.getSource();
				if (sepTabT.isSelected()) {
					params.setDisplayOption(Constants.CurrencyDisplay.SEPARATE);
					String[] parms = { String.valueOf(Constants.CurrencyDisplay.SEPARATE.getNum()) };
					controller.processAction(Constants.MAINACTIONS.CHANGECURDISPLAY, parms);
				}
			}
		});
		curPlacePanel.add(curSepTab);
		curSamePage.setFont(cbFont);
		curSamePage.setOpaque(false);
		curSepTab.setFont(cbFont);
		curSepTab.setOpaque(false);
		mainPanel.add(curPlacePanel, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0).colspan(3));
		gridx = 1;
		gridy++;
		gridx = 0;
		gridy++;
		JLabel exportLbl = new JLabel("CSV Output");
		mainPanel.add(exportLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 5));
		gridx++;
		fileName = new JLabel("Export Folder : " + params.getExportFolder());
		mainPanel.add(fileName, GridC.getc(gridx, gridy).west().colspan(6).insets(5, 5, 5, 0));
		gridx = 1;
		gridy++;
		exportSave = new MyCheckBox("Export on Save");
		exportSave.setToolTipText("Creates export csv file when prices/rates are saved");
		exportSave.setFont(cbFont);
		;
		exportSave.setHorizontalTextPosition(SwingConstants.LEFT);
		exportSave.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox exportSaveT = (JCheckBox) e.getSource();
				params.setExport(exportSaveT.isSelected());
			}
		});
		mainPanel.add(exportSave, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		exportAuto = new MyCheckBox("Export on Auto Run");
		exportAuto.setToolTipText("Creates export csv file on completion of Automatic Run");
		exportAuto.setFont(cbFont);
		;
		exportAuto.setHorizontalTextPosition(SwingConstants.LEFT);
		exportAuto.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox exportAutoT = (JCheckBox) e.getSource();
				params.setExportAuto(exportAutoT.isSelected());
			}
		});
		mainPanel.add(exportAuto, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		changeExport = new JButton("Change Export Folder");
		changeExport.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				Main.debugInst.debug("ParameterTab", "actionPerformed", MRBDebug.DETAILED, "Choose folder");
				chooseFile();
				params.setExportFolder(exportFolder);
				fileName.setText("Export Folder : " + params.getExportFolder());
			}
		});
		mainPanel.add(changeExport, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 0));
		gridx = 0;
		gridy++;

		JLabel generalLbl = new JLabel("General Settings");
		mainPanel.add(generalLbl, GridC.getc(gridx, gridy).west().colspan(2).insets(5, 5, 5, 5));
		gridx = 1;
		gridy++;
		JLabel lblDecimal = new JLabel("Decimal Digits");
		mainPanel.add(lblDecimal, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		decimalComBo = new JComboBox<>(Parameters.decimals);
		decimalComBo.setToolTipText(
				"By default the prices are shown to 4dp. You can select 5,6,7 or 8 dp to display");
		decimalComBo.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<Integer> cbDec = (JComboBox<Integer>) e.getSource();
				params.setDecimal((int) cbDec.getSelectedItem());
				controller.processAction(Constants.MAINACTIONS.RESETDISPLAY, null);
				// resetData();
			}
		});
		mainPanel.add(decimalComBo, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx = 1;
		gridy++;
		JLabel consoleLbl = new JLabel("Console Messages");
		mainPanel.add(consoleLbl, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		JPanel consolePane = new JPanel();
		conOff = new JRadioButton("Off");
		conOff.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JRadioButton conOffT = (JRadioButton) e.getSource();
				if (conOffT.isSelected()) {
					Main.debugInst.debug("ParameterTab", "actionListener", MRBDebug.DebugLevel.INFO, "Debug level set to OFF");
					Main.debugInst.setDebugLevel(MRBDebug.DebugLevel.OFF);
				}
				params.setDirty(true);
			}
		});
		conInfo = new JRadioButton("Info");
		conInfo.addActionListener(e -> {
      JRadioButton conInfoT = (JRadioButton) e.getSource();
      if (conInfoT.isSelected()) {
        Main.debugInst.setDebugLevel(MRBDebug.DebugLevel.INFO);
        reportConsoleChg();
      }
      params.setDirty(true);
    });
		conSummary = new JRadioButton("Summary");
		conSummary.addActionListener(e -> {
      JRadioButton conSummaryT = (JRadioButton) e.getSource();
      if (conSummaryT.isSelected()) {
        Main.debugInst.setDebugLevel(MRBDebug.DebugLevel.SUMMARY);
        reportConsoleChg();
      }
      params.setDirty(true);
    });
		conDetailed = new JRadioButton("Detailed");
		conDetailed.addActionListener(e -> {
      JRadioButton conDetailedT = (JRadioButton) e.getSource();
      if (conDetailedT.isSelected()) {
        Main.debugInst.setDebugLevel(MRBDebug.DebugLevel.DETAILED);
        reportConsoleChg();
      }
      params.setDirty(true);
    });
		conDeveloper = new JRadioButton("Developer");
		conDeveloper.addActionListener(e -> {
      JRadioButton conDeveloperT = (JRadioButton) e.getSource();
      if (conDeveloperT.isSelected()) {
        Main.debugInst.setDebugLevel(MRBDebug.DebugLevel.DEVELOPER);
        reportConsoleChg();
      }
      params.setDirty(true);
    });
		conOption = new ButtonGroup();
		conOption.add(conOff);
		conOption.add(conInfo);
		conOption.add(conSummary);
		conOption.add(conDetailed);
		conOption.add(conDeveloper);
		conOff.setFont(cbFont);
		conOff.setOpaque(false);
		conInfo.setFont(cbFont);
		conInfo.setOpaque(false);
		conSummary.setFont(cbFont);
		conSummary.setOpaque(false);
		conDetailed.setFont(cbFont);
		conDetailed.setOpaque(false);
		conDeveloper.setFont(cbFont);
		conDeveloper.setOpaque(false);
		consolePane.add(conOff);
		consolePane.add(conInfo);
		consolePane.add(conSummary);
		consolePane.add(conDetailed);
		consolePane.add(conDeveloper);
		mainPanel.add(consolePane, GridC.getc(gridx, gridy).west().colspan(3).insets(5, 5, 5, 0));
		gridx = 1;
		gridy++;
		alphaLbl = new JLabel("API Key for Alpha Vantage");
		alphaKey = new JTextField();
		alphaKey.setText(params.getAlphaAPIKey());
		alphaKey.getDocument().addDocumentListener(new DocumentListener(){
			@Override
			public void insertUpdate(DocumentEvent e) {params.setAlphaAPIKey(alphaKey.getText());}
			@Override
			public void removeUpdate(DocumentEvent e) {params.setAlphaAPIKey(alphaKey.getText());}
			@Override
			public void changedUpdate(DocumentEvent e) {params.setAlphaAPIKey(alphaKey.getText());}
		});
		alphaKey.setPreferredSize(new Dimension(150,20));
		mainPanel.add(alphaLbl, GridC.getc(gridx++, gridy).insets(5,5,5,5));
		mainPanel.add(alphaKey, GridC.getc(gridx++, gridy).insets(5,5,5,5).colspan(6).west());

		JLabel lblAplhaPlan = new JLabel("API calls per minute:");
		mainPanel.add(lblAplhaPlan, GridC.getc(gridx++, gridy).east().insets(5, 5, 5, 0));

    alphaPlanCombo = new JComboBox<>(Parameters.alphaPlans);
    alphaPlanCombo.setToolTipText("Select your Alpha Vantage API plan (requests per minute) 5 = Free Plan");
    alphaPlanCombo.addActionListener(e -> {
      @SuppressWarnings("unchecked")
      JComboBox<Integer> cbPlan = (JComboBox<Integer>) e.getSource();
      Integer newPlan = (Integer) cbPlan.getSelectedItem();
      params.setAlphaPlan(newPlan == null ? Parameters.alphaPlans[0] : newPlan);  // default to the fastest...
    });
    mainPanel.add(alphaPlanCombo, GridC.getc(gridx++, gridy++).west().insets(5, 5, 5, 0));

		gridx=1;
		mdLbl = new JLabel("Access Token for Market Data");
		mdToken = new JTextField();
		mdToken.setText(params.getMdToken());
		mdToken.getDocument().addDocumentListener(new DocumentListener(){
			@Override
			public void insertUpdate(DocumentEvent e) {params.setMdToken(mdToken.getText());}
			@Override
			public void removeUpdate(DocumentEvent e) {params.setMdToken(mdToken.getText());}
			@Override
			public void changedUpdate(DocumentEvent e) {params.setMdToken(mdToken.getText());}
		});
		mdToken.setPreferredSize(new Dimension(500,20));
		mainPanel.add(mdLbl, GridC.getc(gridx++, gridy).insets(5,5,5,5));
		mainPanel.add(mdToken, GridC.getc(gridx, gridy++).insets(5,5,5,5).colspan(6).west());
		gridx=1;
		uaLabel = new JLabel("User Agent");
		uaParam = new JTextField();
    	uaParam.setToolTipText("ADVANCED. Normally blank to use rotating/random user-agent browser header(s). Manually override when using Yahoo as a quote source to bypass 429/rate errors");
		uaParam.setText(params.getUaParam());
		uaParam.setPreferredSize(new Dimension(400,20));
		uaParam.getDocument().addDocumentListener(new DocumentListener(){
			@Override
			public void insertUpdate(DocumentEvent e) {params.setUaParam(uaParam.getText());}
			@Override
			public void removeUpdate(DocumentEvent e) {params.setUaParam(uaParam.getText());}
			@Override
			public void changedUpdate(DocumentEvent e) {params.setUaParam(uaParam.getText());}
		});
		mainPanel.add(uaLabel, GridC.getc(gridx++, gridy).insets(5,5,5,5).west());
		mainPanel.add(uaParam, GridC.getc(gridx, gridy++).insets(5,5,5,5).colspan(6).west());

    	throttleYahooTF = new MyCheckBox();
		throttleYahooTF.setToolTipText("When enabled then Yahoo connections will be throttled");
		throttleYahooTF.setAlignmentX(LEFT_ALIGNMENT);
		throttleYahooTF.setText("Throttle Yahoo connections");
		throttleYahooTF.setHorizontalTextPosition(SwingConstants.LEFT);
    	throttleYahooTF.setSelected(Main.THROTTLE_YAHOO);  // default is always on - users should not be able to change this
		throttleYahooTF.setEnabled(false);
		mainPanel.add(throttleYahooTF, GridC.getc(gridx, gridy++).colspan(2).west().insets(5, 5, 5, 0));

		gridx=1;
		saveParams = new JButton("Save Parameters");
		saveParams.setToolTipText("Click to save parameters");
		saveParams.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.DEBUGLEVEL,
						MRBDebug.INFO) != Main.debugInst.getDebugLevel()) {
					Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.DEBUGLEVEL,
							Main.debugInst.getDebugLevel());
					Main.preferences.isDirty();
				}
				params.save();
				saveDebugParam();
				JOptionPane.showMessageDialog(Main.frame, "Changes Saved");
			}
		});
		mainPanel.add(saveParams, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		gridx++;
		cancelParams = new JButton("Cancel Changes");
		cancelParams.setToolTipText("Click to abandon all parameter changes");
		cancelParams.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				params.reloadValues();
				Main.debugInst.setDebugLevel(Main.preferences
						.getInt(Constants.PROGRAMNAME + "." + Constants.DEBUGLEVEL, MRBDebug.INFO));
				loadParamValues();
			}
		});
		mainPanel.add(cancelParams, GridC.getc(gridx, gridy).west().insets(5, 5, 5, 0));
		loadParamValues();
		params.setDirty(false);
		if (saveAutoChange)
			runLbl.setForeground(colors.errorMessageForeground);
		else
			runLbl.setForeground(colors.defaultTextForeground);
		Main.autoSettingsChanged=saveAutoChange;


	}

  public void saveDebugParam() {
    if (Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.DEBUGLEVEL, MRBDebug.INFO) != Main.debugInst.getDebugLevel()) {
      Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.DEBUGLEVEL, Main.debugInst.getDebugLevel());
      Main.preferences.isDirty();
    }
  }

  private void reportConsoleChg() {
    String debug = Main.debugInst.getDebugLevelType().getShortName();
    Main.debugInst.debug("ParameterTab", "reportConsoleChg", MRBDebug.DebugLevel.INFO, "Debug level set to: " + debug);
  }

	private void loadParamValues() {
		zeroCB.setSelected(params.getZero());
		addVolumeCB.setSelected(params.getAddVolume());
		overridePriceCB.setSelected(params.isOverridePrice());
		historyCB.setSelected(params.getHistory());
			historyPeriod.setSelectedIndex(params.getAmtHistory());
		currencyCB.setSelected(params.getCurrency());
		if (params.getCurrency()) {
			curSamePage.setVisible(true);
			curSepTab.setVisible(true);
		} else {
			curSamePage.setVisible(false);
			curSepTab.setVisible(false);
		}

		decimalComBo.setSelectedIndex(params.getDecimal() - 2);
		fileName.setText("Export Folder : " + params.getExportFolder());
		if (params.getDisplayOption() == Constants.CurrencyDisplay.SAME) {
			curSamePage.setSelected(true);
			curSepTab.setSelected(false);
		} else {
			curSepTab.setSelected(true);
			curSamePage.setSelected(false);
		}
		exportSave.setSelected(params.isExport());
		exportAuto.setSelected(params.isExportAuto());
		decimalComBo.setSelectedIndex(params.getDecimal() - 2);
		int debugLvl = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.DEBUGLEVEL, MRBDebug.DebugLevel.INFO.getLevel());
    MRBDebug.DebugLevel levelType = MRBDebug.DebugLevel.fromInt(debugLvl);
		Main.debugInst.setDebugLevel(levelType);
    switch (levelType) {
      case INFO -> conInfo.setSelected(true);
      case SUMMARY -> conSummary.setSelected(true);
      case DETAILED -> conDetailed.setSelected(true);
      case DEVELOPER -> conDeveloper.setSelected(true);
      default -> conOff.setSelected(true);
    }

    // iterate the alpha plan entries and select the right one...
    Integer currentPlan = params.getAlphaPlan();
    for (int i = 0; i < alphaPlanCombo.getItemCount(); i++) {
      Integer item = alphaPlanCombo.getItemAt(i);
      if (item != null && Objects.equals(item, currentPlan)) {
        alphaPlanCombo.setSelectedIndex(i);
        break;
      }
    }
    if (alphaPlanCombo.getSelectedItem() == null) {
      alphaPlanCombo.setSelectedIndex(0); // default to the free option
    }

		params.setDirty(false);

	}

	private void setNextRunDate(JDateField date, String dateNode) {
		int newDate = date.getDateInt();
		Main.preferences.put(Constants.PROGRAMNAME + "." + dateNode, newDate);
		Main.preferences.isDirty();

	}

	private int calculateNextRunDate(String typeNode, String typeParam, String lastRun) {
		CalculateRunDate runDate = new CalculateRunDate(typeNode, typeParam, lastRun);
		return runDate.getDate();
	}

	private void showCalendar(String runtype, String runParam) {

		Main.debugInst.debug("loadPricesWindow", "showCalendar", MRBDebug.DETAILED, "Displaying Calendar Popup");
		CalendarPopup popup = new CalendarPopup(Main.frame, runtype, runParam);
		int ix = curCalendarBtn.getX();
		int iy = curCalendarBtn.getY();
		Point p = new Point(ix, iy);
		popup.setLocation(p);
		popup.setVisible(true);
	}

	public void removeButtons(JPanel buttonsPanel) {
		mainPanel.remove(buttonsPanel);
	}

	public void setButtons(JPanel buttonsPanel) {
		gridy++;
		mainPanel.add(buttonsPanel, GridC.getc(0, gridy).colspan(7).insets(10, 0, 10, 0));
	}

	private void chooseFile() {
		JFileChooser fileChooser;
		String directory = params.getExportFolder();
		if (MRBPlatform.isOSX()) {
			JFrame parentWindow = (JFrame) SwingUtilities.getWindowAncestor(this);
			System.setProperty("com.apple.macos.use-file-dialog-packages", "true");
			FileDialog fwin = new FileDialog(parentWindow, "choose_directory", FileDialog.LOAD);
			System.setProperty("apple.awt.fileDialogForDirectories", "true");
			fwin.setDirectory(directory);
			fwin.setVisible(true);

			directory = fwin.getDirectory() + fwin.getFile();
			Main.debugInst.debug("ParameterTab", "ChooseFile", MRBDebug.DETAILED,
					"Directory Name is:" + directory);
		} else {
			fileChooser = new JFileChooser();
			if (!(directory == null || directory == "")) {
				File directoryFile = new File(directory);
				fileChooser.setCurrentDirectory(directoryFile);
			}
			fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
			int iReturn = fileChooser.showDialog(this, "Select Directory");
			if (iReturn == JFileChooser.APPROVE_OPTION) {
				File fSecurities = fileChooser.getSelectedFile();
				directory = fSecurities.getAbsolutePath();
			}
		}
		exportFolder = directory;
		return;
	}

}
