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

import java.awt.*;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.util.DateUtil;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.OptionMessage;
import com.moneydance.modules.features.reportwriter.Parameters;



import javax.swing.*;

public class DataDataPane extends ScreenDataPane {
	private Parameters params;
	private JTextField name;
	private SelectionDataRow selRow;
	private SortedMap<String,DataParameter> parameters;
	private MyGridPane pane;
	private DataDataRow row;
	private JPanel parmPanes;
	private JPanel buttons;
	private boolean newRow = false;
	private JDateField fromDate;
	private JDateField toDate;
	private JCheckBox selectDates;
	private JCheckBox selectAccounts;
	private JCheckBox selectCategories;
	private JCheckBox selectBudgets;
	private JCheckBox selectCurrencies;
	private JCheckBox selectSecurities;
	private JCheckBox selectTrans;
	private JCheckBox selectInvestTrans;
	private JCheckBox selAsset;
	private JCheckBox selBank;
	private JCheckBox selCredit;
	private JCheckBox selInvestment;
	private JCheckBox selLiability;
	private JCheckBox selLoan;
	private JCheckBox today;
	private JCheckBox inactiveAccts;
	private  JButton acctSelBtn;
	private JCheckBox selIncome;
	private JCheckBox selExpense;
	private  JButton catSelBtn;
	private  JButton budgets;
	private  JButton currSelBtn;
	private  JButton secSelBtn;
	private JCheckBox selCleared;
	private JCheckBox selReconciling;
	private JCheckBox selUnreconciled;
	private  JButton tagsSelBtn;
	private JTextField fromCheque;
	private JTextField toCheque;
	private  JButton ttypSelBtn;
	private  JButton invAcctBtn;
	private boolean dirty=false;
	private   BeanSelectionPanel acctPanel=null;
	private   BeanSelectionPanel catPanel=null;
	private   BeanSelectionPanel budPanel=null;
	private   BeanSelectionPanel currPanel=null;
	private   BeanSelectionPanel secPanel=null;
	private   BeanSelectionPanel invPanel=null;
	private   BeanSelectionPanel ttypPanel=null;
	private   BeanSelectionPanel tagsPanel=null;
	


	public DataDataPane(Parameters params) {
		super();
		screenName = "DataDataPane";
		screenTitle = "Data Filter Parameters";
		this.params = params;
		row = new DataDataRow();
		parameters = new TreeMap<>();
		row.setParameters(parameters);
		newRow= true;
		selRow = new SelectionDataRow();
	}
	public DataDataPane(Parameters params, DataDataRow row) {
		super();
		screenName = "DataDataPane";
		this.row = row;
		this.params = params;
		selRow = new SelectionDataRow();
		selRow.loadRow(row.getName(), params);
		parameters = row.getParameters();
	}
	public DataDataRow displayPanel() {
		DEFAULTSCREENWIDTH = Constants.DATADATASCREENWIDTH;
		DEFAULTSCREENHEIGHT = Constants.DATADATASCREENHEIGHT;
		setStage(new JDialog());
		stage.setResizable(true);
		stage.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
		stage.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
		pane = new MyGridPane(Constants.WINDATADATA);
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
						stage.setVisible(false);
					}
				}
					stage.setVisible(false);
			}

			@Override
			public void windowClosed(WindowEvent e) {
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
				if (saveRow(name.getText()))
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
		});
*/

		int ix = 0;
		int iy=0;
		parmPanes = setParameters();
		pane.add(parmPanes, GridC.getc(ix, iy++).insets(10,10,10,10).colspan(3));
        buttons = new JPanel();
		buttons.setLayout(new BoxLayout(buttons, BoxLayout.X_AXIS));
		JButton okBtn = new JButton();
		if (Main.loadedIcons.okImg == null)
			okBtn.setText("OK");
		else
			okBtn.setIcon(new ImageIcon(Main.loadedIcons.okImg));
		okBtn.addActionListener(e -> {
            if (saveRow(name.getText()))
				stage.setVisible(false);
        });
		JButton cancelBtn = new JButton();
		if (Main.loadedIcons.cancelImg == null)
			cancelBtn.setText("Cancel");
		else
			cancelBtn.setIcon(new ImageIcon(Main.loadedIcons.cancelImg));
		cancelBtn.addActionListener(e -> {
			if (dirty){
				boolean result = OptionMessage.yesnoMessage(Constants.ABANDONMSG);
				if (result) {
					row=null;
					stage.setVisible(false);
				}
			}
			else {
				row = null;
				stage.setVisible(false);
			}
        });
		buttons.add(okBtn);
		buttons.add(Box.createRigidArea(new Dimension(5, 0)));
		buttons.add(cancelBtn);
		pane.add(buttons,GridC.getc(0, iy).colspan(2).west().insets(5,5,5,5));
		resize();
		dirty=false;
		stage.pack();
		setLocation();
		stage.setVisible(true);
		return row;
	}
	private boolean saveRow(String fileName) {
		if (name.getText().isEmpty()) {
			OptionMessage.displayMessage("Name must be entered");
			return false;
		}
		boolean updateName=false;
		DataDataRow tempRow = new DataDataRow();
		if (!newRow && !row.getName().equals(name.getText()))
			updateName=true;
		if ((newRow || updateName) && tempRow.loadRow(fileName, params)) {
			if (OptionMessage.yesnoMessage("Data Parameters already exists.  Do you wish to overwrite them?"))  
				tempRow.delete(params);
			else
				return false;
		}
		if (!updateParms())
			return false;
		if (newRow) {
			row.setName(fileName);
			row.saveRow(params);
		}
		else {
			if (updateName) 
				row.renameRow(fileName,params);
			else
				row.saveRow(params);
		}
		return true;
	}

	private JPanel setParameters() {
		JPanel pane = new JPanel();
		pane.setLayout(new GridBagLayout());
		name = new JTextField();
		name.setColumns(40);
		if (!newRow) {
			name.setText(row.getName());
		}
		name.addPropertyChangeListener("value", evt -> dirty=true);
		JLabel nameLbl = new JLabel("Name");
		JLabel fromDateLbl = new JLabel("From Date");
		fromDate = new JDateField(Main.cdate);

		fromDate.addPropertyChangeListener(arg0 -> dirty = true);
	    if (parameters.containsKey(Constants.PARMFROMDATE)) {
			Date tempDate = DateUtil.convertIntDateToLong(Integer.parseInt(parameters.get(Constants.PARMFROMDATE).getValue()));
			fromDate.setDate(tempDate);
		}
		else
			fromDate.setDate(new Date());
		JLabel toDateLbl = new JLabel("To Date");
		toDate = new JDateField(Main.cdate);

		toDate.addPropertyChangeListener(arg0 -> dirty = true);
	    today = new JCheckBox("Today");
	    if (parameters.containsKey(Constants.PARMTODATE)) {
			Date tempDate = DateUtil.convertIntDateToLong(Integer.parseInt(parameters.get(Constants.PARMTODATE).getValue()));
			toDate.setDate(tempDate);
		}
		else
			toDate.setDate(new Date());
    	today.setSelected(parameters.containsKey(Constants.PARMTODAY));
		selectDates = new JCheckBox("Filter by Dates");
		selectDates.setSelected(parameters.containsKey(Constants.PARMSELDATES));
		selectAccounts = new JCheckBox("Filter by Accounts");
		selectAccounts.setSelected(parameters.containsKey(Constants.PARMSELACCT));
		selectAccounts.addActionListener(e -> {
            JCheckBox tmp = (JCheckBox)e.getSource();
            if (tmp.isSelected() != selectAccounts.isSelected())
                dirty=true;
        });
		selectCategories = new JCheckBox("Filter by Categories");
		selectCategories.setSelected(parameters.containsKey(Constants.PARMSELCAT));
		selectCategories.addActionListener(e -> {
            JCheckBox tmp = (JCheckBox)e.getSource();
            if (tmp.isSelected() != selectCategories.isSelected())
                dirty=true;
        });		selectBudgets = new JCheckBox("Filter by Budgets");
		selectBudgets.setSelected(parameters.containsKey(Constants.PARMSELBUDGET));
		selectBudgets.addActionListener(e -> dirty = true);
		selectCurrencies = new JCheckBox("Filter by Currencies");
		selectCurrencies.setSelected(parameters.containsKey(Constants.PARMSELCURRENCY));
		selectCurrencies.addActionListener(e -> dirty = true);
		selectSecurities = new JCheckBox("Filter by Securities");
		selectSecurities.setSelected(parameters.containsKey(Constants.PARMSELSECURITY));
		selectSecurities.addActionListener(e -> dirty = true);
		selectTrans = new JCheckBox ("Filter by Transactions");
		selectTrans.setSelected(parameters.containsKey(Constants.PARMSELTRANS));
		selectTrans.addActionListener(e -> dirty = true);
		selectInvestTrans = new JCheckBox ("Filter by Invest. Transactions");
		selectInvestTrans.setSelected(parameters.containsKey(Constants.PARMSELINVTRANS));
		selectInvestTrans.addActionListener(e -> dirty = true);
		selAsset = new JCheckBox("Assets");
		selAsset.setSelected(parameters.containsKey(Constants.PARMASSET));
		selAsset.addActionListener(e -> dirty = true);
		selBank = new JCheckBox("Banks");
		selBank.setSelected(parameters.containsKey(Constants.PARMBANK));
		selBank.addActionListener(e -> dirty = true);
		selCredit = new JCheckBox("Credit Cards");
		selCredit.setSelected(parameters.containsKey(Constants.PARMCREDIT));
		selCredit.addActionListener(e -> dirty = true);
		selInvestment = new JCheckBox("Investments");
		selInvestment.setSelected(parameters.containsKey(Constants.PARMINVESTMENT));
		selInvestment.addActionListener(e -> dirty = true);
		selLiability = new JCheckBox("Liabilities");
		selLiability.setSelected(parameters.containsKey(Constants.PARMLIABILITY));
		selLiability.addActionListener(e -> dirty = true);
		selLoan = new JCheckBox("Loans");
		selLoan.setSelected(parameters.containsKey(Constants.PARMLOAN));
		selLoan.addActionListener(e -> dirty = true);
		inactiveAccts = new JCheckBox("Include Inactive");
	    if (parameters.containsKey(Constants.PARMINACTIVE))
	    	inactiveAccts.setSelected(parameters.containsKey(Constants.PARMINACTIVE));
	    else
	    	inactiveAccts.setSelected(false);
		acctSelBtn = new JButton("Select");
		acctSelBtn.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>();
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMACCOUNTS))
                selected = parameters.get(Constants.PARMACCOUNTS).getList();
            else
                selected = new ArrayList<>();
            if (selAsset.isSelected())
                addAccounts(list,Main.extension.assetAccounts);
            if (selBank.isSelected())
                addAccounts(list,Main.extension.bankAccounts);
            if (selCredit.isSelected())
                addAccounts(list,Main.extension.creditAccounts);
            if (selLiability.isSelected())
                addAccounts(list,Main.extension.liabilityAccounts);
            if (selInvestment.isSelected())
                addAccounts(list,Main.extension.investmentAccounts);
            if (selLoan.isSelected())
                addAccounts(list,Main.extension.loanAccounts);
            if (list.isEmpty()) {
                OptionMessage.displayMessage("No accounts available for the selected types");
                return;
            }
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            acctPanel = new BeanSelectionPanel(list,null,"Select Accounts");
            acctPanel.display();
        });
		selIncome = new JCheckBox("Income");
		selIncome.setSelected(parameters.containsKey(Constants.PARMINCOME));
		selIncome.addActionListener(e -> dirty = true);
		selExpense = new JCheckBox("Expense");
		selExpense.setSelected(parameters.containsKey(Constants.PARMEXPENSE));
		selExpense.addActionListener(e -> dirty = true);		catSelBtn = new JButton("Select");
		catSelBtn.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>();
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMCATEGORIES))
                selected = parameters.get(Constants.PARMCATEGORIES).getList();
            else
                selected = new ArrayList<>();
            if (selExpense.isSelected())
                list.addAll(Main.extension.expenseCategories);
            if (selIncome.isSelected())
                list.addAll(Main.extension.incomeCategories);
            if (list.isEmpty()) {
                OptionMessage.displayMessage("Please select at least one type of category");
                return;
            }
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            catPanel = new BeanSelectionPanel(list,"Select Active","Select Categories");
            catPanel.display();
            dirty=true;
        });
		budgets = new JButton("Select");
		budgets.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>(Main.extension.budgets);
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMBUDGET))
                selected = parameters.get(Constants.PARMBUDGET).getList();
            else
                selected = new ArrayList<>();
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            budPanel = new BeanSelectionPanel(list,null,"Select Budgets");
            budPanel.display();
            dirty=true;
        });
		currSelBtn = new JButton("Select");
		currSelBtn.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>(Main.extension.currencies);
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMCURRENCY))
                selected = parameters.get(Constants.PARMCURRENCY).getList();
            else
                selected = new ArrayList<>();
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            currPanel = new BeanSelectionPanel(list,"Shown on Summary Page","Select Currencies");
            currPanel.display();
            dirty=true;
        });
		secSelBtn = new JButton("Select");
		secSelBtn.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>(Main.extension.securities);
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMSECURITY))
                selected = parameters.get(Constants.PARMSECURITY).getList();
            else
                selected = new ArrayList<>();
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            secPanel = new BeanSelectionPanel(list,"Shown on Summary Page","Select Securities");
            secPanel.display();
            dirty=true;
        });
		selCleared = new JCheckBox("Cleared");
		selCleared.setSelected(parameters.containsKey(Constants.PARMCLEARED));
		selCleared.addActionListener(e -> dirty = true);		selReconciling = new JCheckBox("Reconciling");
		selReconciling.setSelected(parameters.containsKey(Constants.PARMRECON));
		selReconciling.addActionListener(e -> dirty = true);		selUnreconciled = new JCheckBox("Unreconciled");
		selUnreconciled.setSelected(parameters.containsKey(Constants.PARMUNRECON));
		selUnreconciled.addActionListener(e -> dirty = true);		tagsSelBtn = new JButton("Filter by Tags");
		tagsSelBtn.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>(Main.extension.tags);
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMTAGS))
                selected = parameters.get(Constants.PARMTAGS).getList();
            else
                selected = new ArrayList<>();
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            tagsPanel = new BeanSelectionPanel(list,null,"Select Tags");
            tagsPanel.display();
            dirty=true;
        });
		Label fromChequeLbl = new Label("From Cheque No");
		fromCheque = new JTextField();
		fromCheque.setColumns(15);
		fromCheque.addActionListener(e -> dirty = true);
		if (parameters.containsKey(Constants.PARMFROMCHEQUE))
			fromCheque.setText(parameters.get(Constants.PARMFROMCHEQUE).getValue());
		Label toChequeLbl = new Label("To Cheque No");
		toCheque = new JTextField();
		toCheque.setColumns(15);
		toCheque.addActionListener(e -> dirty = true);
		if (parameters.containsKey(Constants.PARMTOCHEQUE))
			toCheque.setText(parameters.get(Constants.PARMTOCHEQUE).getValue());
		invAcctBtn = new JButton("Select Accounts and Securities");
		invAcctBtn.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>(Main.extension.securityAccounts);
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMINVACCTS))
                selected = parameters.get(Constants.PARMINVACCTS).getList();
            else
                selected = new ArrayList<>();
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            invPanel = new BeanSelectionPanel(list,"Select with Holdings","Select Investment Accounts and Security Holdings");
            invPanel.display();
            dirty=true;
        });
		ttypSelBtn = new JButton("Filter by Transfer Types");
		ttypSelBtn.addActionListener(e -> {
            List<BeanSelectionRow> list = new ArrayList<>(Main.extension.transferTypes);
            List<String> selected;
            SortedMap<String,String> selMap = new TreeMap<>();
            if (parameters.containsKey(Constants.PARMTRANSFER))
                selected = parameters.get(Constants.PARMTRANSFER).getList();
            else
                selected = new ArrayList<>();
            for (String acct : selected) {
                selMap.put(acct,acct);
            }
            for (BeanSelectionRow row : list) {
                if (selMap.get(row.getRowId()) != null)
                    row.setSelected(true);
            }
            ttypPanel = new BeanSelectionPanel(list,null,"Select Investment Transfer Types");
            ttypPanel.display();
            dirty=true;
        });

		int ix = 0;
		int iy = 0;
		pane.add(nameLbl, GridC.getc(ix++,iy).west());
		pane.add(name, GridC.getc(ix, iy++).west().colspan(3));
		ix= 0;
		pane.add(selectDates,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		JPanel datePane = new JPanel();
		datePane.setLayout(new BoxLayout(datePane,BoxLayout.X_AXIS));
		datePane.add(fromDateLbl);
		datePane.add(Box.createRigidArea(new Dimension(5,0)));
		datePane.add(fromDate);
		datePane.add(Box.createRigidArea(new Dimension(5,0)));
		datePane.add(toDateLbl);
		datePane.add(Box.createRigidArea(new Dimension(5,0)));
		datePane.add(toDate);
		datePane.add(Box.createRigidArea(new Dimension(5,0)));
		datePane.add(today);
		pane.add(datePane, GridC.getc(ix, iy++).colspan(5).west());
		ix=0;
		pane.add(selectAccounts, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(selAsset, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(selBank, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(selCredit,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(inactiveAccts,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(acctSelBtn, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=1;
		pane.add(selInvestment,GridC.getc(ix++,iy).west().insets(5,5,5,5));
		pane.add(selLiability,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(selLoan, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix = 0;
		pane.add(selectCategories,GridC.getc(ix++,iy).west().insets(5,5,5,5));
		pane.add(selIncome, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(selExpense,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(catSelBtn, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=0;
		pane.add(selectBudgets,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(budgets,GridC.getc( ix, iy++).west().insets(5,5,5,5));
		ix=0;
		pane.add(selectCurrencies, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(currSelBtn, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=0;
		pane.add(selectSecurities, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(secSelBtn, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=0;
		pane.add(selectTrans, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(selCleared, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(selUnreconciled,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(selReconciling, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=1;
		pane.add(fromChequeLbl, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(fromCheque, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=1;
		pane.add(toChequeLbl,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(toCheque, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=1;
		pane.add(tagsSelBtn, GridC.getc(ix, iy++).west().insets(5,5,5,5));
		ix=0;
		pane.add(selectInvestTrans,GridC.getc( ix++, iy).west().insets(5,5,5,5));
		pane.add(invAcctBtn, GridC.getc(ix++, iy).west().insets(5,5,5,5));
		pane.add(ttypSelBtn, GridC.getc(ix, iy).west().insets(5,5,5,5));

		return pane;
	}
	private void addAccounts(List<BeanSelectionRow> list,List<BeanSelectionRow> accounts) {
		for (BeanSelectionRow row:accounts) {
			String uuid = row.getRowId();
			Account acct = Main.book.getAccountByUUID(uuid);
			if(acct !=null && acct.getAccountIsInactive() && !inactiveAccts.isSelected())
				continue;
			list.add(row);
		}
	}
	private boolean updateParms() {
		DataParameter nullParm = new DataParameter();
		if (selectDates.isSelected())
			parameters.put(Constants.PARMSELDATES,nullParm);
		else
			parameters.remove(Constants.PARMSELDATES);
		if (selectDates.isSelected()) {
			nullParm.setValue(null);
			DataParameter fromDateParm = new DataParameter();
			int intDate=fromDate.getDateInt();
			fromDateParm.setValue(String.valueOf(intDate));
			parameters.put(Constants.PARMFROMDATE, fromDateParm);
			DataParameter toDateParm = new DataParameter();
			int toIntDate=toDate.getDateInt();
			toDateParm.setValue(String.valueOf(toIntDate));
			parameters.put(Constants.PARMTODATE, toDateParm);
			if (today.isSelected())
				parameters.put(Constants.PARMTODAY,nullParm);
			else {
				parameters.remove(Constants.PARMTODAY);
				if(intDate > toIntDate) {
					OptionMessage.displayMessage("From Date must be before To Date unless Today is checked");
					return false;					
				}
			}
		}
		if (selectAccounts.isSelected())
			parameters.put(Constants.PARMSELACCT,nullParm);
		else
			parameters.remove(Constants.PARMSELACCT);
		if (selectCategories.isSelected())
			parameters.put(Constants.PARMSELCAT,nullParm);
		else
			parameters.remove(Constants.PARMSELCAT);
		if (selectBudgets.isSelected())
			parameters.put(Constants.PARMSELBUDGET,nullParm);
		else
			parameters.remove(Constants.PARMSELBUDGET);
		if (selectCurrencies.isSelected())
			parameters.put(Constants.PARMSELCURRENCY,nullParm);
		else
			parameters.remove(Constants.PARMSELCURRENCY);
		if (selectSecurities.isSelected())
			parameters.put(Constants.PARMSELSECURITY,nullParm);
		else
			parameters.remove(Constants.PARMSELSECURITY);
		if (selectTrans.isSelected())
			parameters.put(Constants.PARMSELTRANS,nullParm);
		else
			parameters.remove(Constants.PARMSELTRANS);
		if (selAsset.isSelected())
			parameters.put(Constants.PARMASSET,nullParm);
		else
			parameters.remove(Constants.PARMASSET);
		if (selBank.isSelected())
			parameters.put(Constants.PARMBANK,nullParm);
		else
			parameters.remove(Constants.PARMBANK);
		if (selCredit.isSelected())
			parameters.put(Constants.PARMCREDIT,nullParm);
		else
			parameters.remove(Constants.PARMCREDIT);
		if (selLiability.isSelected())
			parameters.put(Constants.PARMLIABILITY,nullParm);
		else
			parameters.remove(Constants.PARMLIABILITY);
		if (selLoan.isSelected())
			parameters.put(Constants.PARMLOAN,nullParm);
		else
			parameters.remove(Constants.PARMLOAN);
		if (selInvestment.isSelected())
			parameters.put(Constants.PARMINVESTMENT,nullParm);
		else
			parameters.remove(Constants.PARMINVESTMENT);
		if (inactiveAccts.isSelected())
			parameters.put(Constants.PARMINACTIVE,nullParm);
		else
			parameters.remove(Constants.PARMINACTIVE);
		if (selIncome.isSelected())
			parameters.put(Constants.PARMINCOME,nullParm);
		else
			parameters.remove(Constants.PARMINCOME);
		if (selExpense.isSelected())
			parameters.put(Constants.PARMEXPENSE,nullParm);
		else
			parameters.remove(Constants.PARMEXPENSE);
		if (selCleared.isSelected())
			parameters.put(Constants.PARMCLEARED,nullParm);
		else
			parameters.remove(Constants.PARMCLEARED);
		if (selReconciling.isSelected())
			parameters.put(Constants.PARMRECON,nullParm);
		else
			parameters.remove(Constants.PARMRECON);
		if (selUnreconciled.isSelected())
			parameters.put(Constants.PARMUNRECON,nullParm);
		else
			parameters.remove(Constants.PARMUNRECON);		
		if (fromCheque.getText().isBlank())
			parameters.remove(Constants.PARMFROMCHEQUE);
		else {
			DataParameter parm = new DataParameter();
			parm.setValue(fromCheque.getText());
			parameters.put(Constants.PARMFROMCHEQUE, parm);
		}
		if (toCheque.getText().isBlank())
			parameters.remove(Constants.PARMTOCHEQUE);
		else {
			DataParameter parm = new DataParameter();
			parm.setValue(toCheque.getText());
			parameters.put(Constants.PARMTOCHEQUE, parm);
		}

		if (selectInvestTrans.isSelected())
			parameters.put(Constants.PARMSELINVTRANS,nullParm);
		else
			parameters.remove(Constants.PARMSELINVTRANS);
		List<String>panelList;
		if (acctPanel != null)
		{
			parameters.remove(Constants.PARMACCOUNTS);
			DataParameter parm = new DataParameter();
			panelList = acctPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
				parameters.put(Constants.PARMACCOUNTS, parm);
			}
		}
		if (catPanel != null)
		{
			parameters.remove(Constants.PARMCATEGORIES);
			DataParameter parm = new DataParameter();
			panelList = catPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
				parameters.put(Constants.PARMCATEGORIES, parm);
			}
		}
		if (budPanel != null)
		{
			parameters.remove(Constants.PARMBUDGET);
			DataParameter parm = new DataParameter();
			panelList = budPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
				parameters.put(Constants.PARMBUDGET, parm);
			}
		}
		if (currPanel != null)
		{
			parameters.remove(Constants.PARMCURRENCY);
			DataParameter parm = new DataParameter();
			panelList = currPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
				parameters.put(Constants.PARMCURRENCY, parm);
			}
		}
		if (secPanel != null)
		{
			parameters.remove(Constants.PARMSECURITY);
			DataParameter parm = new DataParameter();
			panelList = secPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
				parameters.put(Constants.PARMSECURITY, parm);
			}
		}
		if (ttypPanel != null)
		{
			parameters.remove(Constants.PARMTRANSFER);
			DataParameter parm = new DataParameter();
			panelList = ttypPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
				parameters.put(Constants.PARMTRANSFER, parm);
			}
		}
		if (invPanel != null ) {
			parameters.remove(Constants.PARMINVACCTS);
			DataParameter parm = new DataParameter();
			panelList = invPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
				parameters.put(Constants.PARMINVACCTS, parm);
			}
		}
		if (tagsPanel != null)
		{
			parameters.remove(Constants.PARMTAGS);
			DataParameter parm = new DataParameter();
			panelList = tagsPanel.getSelected();
			if (panelList != null && !panelList.isEmpty()) {
				parm.setList(panelList);
			parameters.put(Constants.PARMTAGS, parm);
			}
		}
		return true;
	}
}

