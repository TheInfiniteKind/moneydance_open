package com.moneydance.modules.features.reportwriter.view;


import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.OptionMessage;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.databeans.AccountBean;
import com.moneydance.modules.features.reportwriter.databeans.AddressBean;
import com.moneydance.modules.features.reportwriter.databeans.BudgetBean;
import com.moneydance.modules.features.reportwriter.databeans.BudgetItemBean;
import com.moneydance.modules.features.reportwriter.databeans.CategoryBean;
import com.moneydance.modules.features.reportwriter.databeans.CurrencyBean;
import com.moneydance.modules.features.reportwriter.databeans.CurrencyRateBean;
import com.moneydance.modules.features.reportwriter.databeans.DataBean;
import com.moneydance.modules.features.reportwriter.databeans.InvTranBean;
import com.moneydance.modules.features.reportwriter.databeans.LotsBean;
import com.moneydance.modules.features.reportwriter.databeans.ReminderBean;
import com.moneydance.modules.features.reportwriter.databeans.SecurityBean;
import com.moneydance.modules.features.reportwriter.databeans.SecurityPriceBean;
import com.moneydance.modules.features.reportwriter.databeans.TransactionBean;

import javax.swing.*;
import java.awt.Dialog;

public class SelectionDataPane extends ScreenDataPane {
	private Parameters params;
	private JTextField name;
	private JButton accountsFieldBtn;
	private JButton addressFieldBtn;
	private JButton budgetsFieldBtn;
	private JButton currenciesFieldBtn;
	private JButton securitiesFieldBtn;
	private JButton transactionsFieldBtn;
	private JButton categoriesFieldBtn;
	private JButton invTransFieldBtn;
	private JButton budgetItemsFieldBtn;
	private JButton securityPricesFieldBtn;
	private JButton lotsFieldBtn;
	private JButton currencyRatesFieldBtn;
	private JButton remindersFieldBtn;
	private JCheckBox accountsCB;
	private JCheckBox acctSecCB;
	private JCheckBox addressCB ;
	private JCheckBox budgetsCB;
	private JCheckBox currenciesCB;
	private JCheckBox securitiesCB;
	private JCheckBox lotsCB;
	private JCheckBox transactionsCB;
	private JCheckBox invTransCB;
	private JCheckBox budgetItemsCB;
	private JCheckBox categoriesCB;
	private JCheckBox securityPricesCB;
	private JCheckBox currencyRatesCB;
	private JCheckBox remindersCB;
	private JPanel pane;
	private SelectionDataRow row;
	private boolean newRow = false;
	private boolean dirty=false;
	private SortedMap<String,DataParameter> dataParams;
	
	public SelectionDataPane(Parameters params) {
		super();
		screenName = "SelectionDataPane";
		screenTitle="Selection Data Groups";
		this.params = params;
		row = new SelectionDataRow();
		dataParams = new TreeMap<String,DataParameter>();
		newRow= true;
	}
	public SelectionDataPane(Parameters params, SelectionDataRow row) {
		super();
		screenName = "SelectionDataPane";
		this.row = row;
		this.params = params;
		dataParams = row.getParameters();
		if (dataParams == null )
			dataParams = new TreeMap<String,DataParameter>();	
}
	public SelectionDataRow displayPanel() {
		DEFAULTSCREENWIDTH = Constants.DATASELECTSCREENWIDTH;
		DEFAULTSCREENHEIGHT = Constants.DATASELECTSCREENHEIGHT;
		setStage(new JDialog());
		stage.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
		pane = new MyGridPane(Constants.WINSELECTIONDATA);
		stage.add(pane);
		stage.addWindowListener(new WindowListener() {
			@Override
			public void windowOpened(WindowEvent e) {}

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

		resize();
		JLabel selectionLbl = new JLabel("Selection Name");
		name = new JTextField();
		name.setColumns(40);
		name.addPropertyChangeListener("value", evt -> dirty=true);
		accountsCB = new JCheckBox("Accounts");
		acctSecCB = new JCheckBox("Include Securities");
		accountsFieldBtn = new JButton("Fields");
		accountsCB.addActionListener(e->{
			JCheckBox tmp = (JCheckBox)e.getSource();
			dirty=true;
			setFieldBtn(tmp, accountsFieldBtn);
			if (tmp.isSelected()) {
				acctSecCB.setEnabled(true);
			}
			else {
				acctSecCB.setEnabled(false);
			}
		});
		acctSecCB.addActionListener(e->{dirty=true;});
		accountsFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new AccountBean(),Constants.PARMFLDACCT,accountsCB);
				dirty=true;
			}
		});
		addressCB = new JCheckBox("Addresses");
		addressCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(addressCB, addressFieldBtn);
		});
		addressFieldBtn = new JButton("Fields");
		addressFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new AddressBean(),Constants.PARMFLDADDR,addressCB);
				dirty=true;
			}
		});
		budgetsCB = new JCheckBox("Budgets");
		budgetsCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(budgetsCB, budgetsFieldBtn);
		});
		budgetsFieldBtn = new JButton("Fields");
		budgetsFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new BudgetBean(),Constants.PARMFLDBUDG,budgetsCB);
				dirty=true;
			}
		});
		currenciesCB = new JCheckBox("Currencies");
		currenciesCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(currenciesCB, currenciesFieldBtn);
		});
		currenciesFieldBtn = new JButton("Fields");
		currenciesFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new CurrencyBean(),Constants.PARMFLDCUR,currenciesCB);
				dirty=true;
			}
		});
		securitiesCB = new JCheckBox("Securities");
		securitiesCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(securitiesCB, securitiesFieldBtn);
		});
		securitiesFieldBtn = new JButton("Fields");
		securitiesFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new SecurityBean(),Constants.PARMFLDSEC,securitiesCB);
				dirty=true;
			}
		});
		transactionsCB = new JCheckBox("Transactions");
		transactionsCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(transactionsCB, transactionsFieldBtn);
		});
		transactionsFieldBtn = new JButton("Fields");
		transactionsFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new TransactionBean(),Constants.PARMFLDTRAN,transactionsCB);
				dirty=true;
			}
		});
		invTransCB = new JCheckBox("Invest. Trans");
		invTransCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(invTransCB, invTransFieldBtn);
		});
		invTransFieldBtn = new JButton("Fields");
		invTransFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new InvTranBean(),Constants.PARMFLDINVTRAN,invTransCB);
				dirty=true;
			}
		});
		lotsCB = new JCheckBox("Security Lots");
		lotsCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(lotsCB, lotsFieldBtn);
		});
		lotsFieldBtn = new JButton("Fields");
		lotsFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new LotsBean(),Constants.PARMFLDLOTS,lotsCB);
				dirty=true;
			}
		});
		budgetItemsCB = new JCheckBox("Budget Items");
		budgetItemsCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(budgetItemsCB, budgetItemsFieldBtn);
		});
		budgetItemsFieldBtn = new JButton("Fields");
		budgetItemsFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new BudgetItemBean(),Constants.PARMFLDBUDGI,budgetItemsCB);
				dirty=true;
			}
		});
		categoriesCB = new JCheckBox("Categories");
		categoriesCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(categoriesCB, categoriesFieldBtn);
		});
		categoriesFieldBtn = new JButton("Fields");
		categoriesFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new CategoryBean(),Constants.PARMFLDCAT,categoriesCB);
				dirty=true;
			}
		});
		securityPricesCB = new JCheckBox("Sec. prices");
		securityPricesCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(securityPricesCB, securityPricesFieldBtn);
		});
		securityPricesFieldBtn = new JButton("Fields");
		securityPricesFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new SecurityPriceBean(),Constants.PARMFLDSECP,securityPricesCB);
				dirty=true;
			}
		});
		currencyRatesCB = new JCheckBox("Currency Rates");
		currencyRatesCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(currencyRatesCB, currencyRatesFieldBtn);
		});
		currencyRatesFieldBtn = new JButton("Fields");
		currencyRatesFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new CurrencyRateBean(),Constants.PARMFLDCURR,currencyRatesCB);
				dirty=true;
			}
		});
		remindersCB = new JCheckBox("Reminders");
		remindersCB.addActionListener(e->{
			dirty=true;
			setFieldBtn(remindersCB, remindersFieldBtn);
		});
		remindersFieldBtn = new JButton("Fields");
		remindersFieldBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				displayFields(new ReminderBean(),Constants.PARMFLDREM,remindersCB );
				dirty=true;
			}
		});
		if (!newRow) {
			name.setText(row.getName());
			accountsCB.setSelected(row.getAccounts());
			acctSecCB.setSelected(row.getAcctSec());
			addressCB.setSelected(row.getAddress());
			budgetsCB.setSelected(row.getBudgets());
			currenciesCB.setSelected(row.getCurrencies());
			securitiesCB.setSelected(row.getSecurities());
			transactionsCB.setSelected(row.getTransactions());
			invTransCB.setSelected(row.getInvTrans());
			lotsCB.setSelected(row.getLots());
			budgetItemsCB.setSelected(row.getBudgetItems());
			categoriesCB.setSelected(row.getCategories());
			securityPricesCB.setSelected(row.getSecurityPrices());
			currencyRatesCB.setSelected(row.getCurrencyRates());
			remindersCB.setSelected(row.getReminders());
		}
		setFieldBtn(accountsCB, accountsFieldBtn);
		setFieldBtn(addressCB, addressFieldBtn);
		setFieldBtn(budgetsCB, budgetsFieldBtn);
		setFieldBtn(currenciesCB, currenciesFieldBtn);
		setFieldBtn(securitiesCB, securitiesFieldBtn);
		setFieldBtn(securitiesCB, securitiesFieldBtn);
		setFieldBtn(transactionsCB, transactionsFieldBtn);
		setFieldBtn(invTransCB, invTransFieldBtn);
		setFieldBtn(lotsCB, lotsFieldBtn);
		setFieldBtn(budgetItemsCB, budgetItemsFieldBtn);
		setFieldBtn(categoriesCB, categoriesFieldBtn);
		setFieldBtn(securityPricesCB, securityPricesFieldBtn);
		setFieldBtn(currencyRatesCB, currencyRatesFieldBtn);
		setFieldBtn(remindersCB, remindersFieldBtn);
		int ix = 0;
		int iy = 0;
		pane.add(selectionLbl, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(name, GridC.getc(ix, iy++).insets(10,10,10,10).colspan(4).west());
		ix = 0;
		pane.add(accountsCB, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(accountsFieldBtn, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(acctSecCB, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		ix++;
		pane.add(addressCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(addressFieldBtn,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(budgetsCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(budgetsFieldBtn,GridC.getc( ix, iy++).insets(10,10,10,10).west());
		ix=0;
		pane.add(transactionsCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(transactionsFieldBtn,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(invTransCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(invTransFieldBtn, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(lotsCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(lotsFieldBtn, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(budgetItemsCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(budgetItemsFieldBtn,GridC.getc( ix, iy++).insets(10,10,10,10).west());
		ix=0;
		pane.add(securitiesCB,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(securitiesFieldBtn,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(currenciesCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(currenciesFieldBtn,GridC.getc( ix++, iy).insets(10,10,10,10).west());
		pane.add(categoriesCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(categoriesFieldBtn,GridC.getc( ix, iy++).insets(10,10,10,10).west());
		ix=0;
		pane.add(securityPricesCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(securityPricesFieldBtn, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(currencyRatesCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(currencyRatesFieldBtn, GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(remindersCB,GridC.getc(ix++, iy).insets(10,10,10,10).west());
		pane.add(remindersFieldBtn, GridC.getc(ix, iy++).insets(10,10,10,10).west());
		ix=0;
		JButton okBtn = new JButton();
		if (Main.loadedIcons.okImg == null)
			okBtn.setText("OK");
		else
			okBtn.setIcon(new ImageIcon(Main.loadedIcons.okImg));
		okBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (saveRow()) {
					closePane();
				}
			}
		});
		JButton cancelBtn = new JButton();
		if (Main.loadedIcons.cancelImg == null)
			cancelBtn.setText("Cancel");
		else
			cancelBtn.setIcon(new ImageIcon(Main.loadedIcons.cancelImg));
		cancelBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (dirty){
					boolean result = OptionMessage.yesnoMessage(Constants.ABANDONMSG);
				if (!result)
						return;
				}
				row=null;
				stage.setVisible(false);
			}
		});
		ix=1;
		pane.add(okBtn, GridC.getc(ix++, iy).insets(10,10,10,10));
		pane.add(cancelBtn,GridC.getc(ix++, iy).insets(10,10,10,10));
		dirty=false;
		stage.pack();
		setLocation();
		stage.setVisible(true);
		return row;
	}
	private void setFieldBtn(JCheckBox cb, JButton btn) {
		if (cb.isSelected())
			btn.setEnabled(true);
		else
			btn.setEnabled(false);
	}
	private void displayFields(DataBean bean, String parm, JCheckBox box) {
		if (!box.isSelected()) {
			OptionMessage.displayMessage("You must select the records before selecting fields");
			return;
		}
		List<String> selectedFields;
		if (dataParams.containsKey(parm)) 
			selectedFields = dataParams.get(parm).getList();
		else
			selectedFields = new ArrayList<String>();
		FieldSelectionPane fieldPane = new FieldSelectionPane(parm,bean,selectedFields);
		selectedFields= fieldPane.displayPanel();
		if (selectedFields.isEmpty()) {
			if(dataParams.containsKey(parm))
				dataParams.remove(parm);
		}
		else {
			if (dataParams.containsKey(parm))
				dataParams.get(parm).setList(selectedFields);
			else {
					DataParameter newParams = new DataParameter();
					newParams.setList(selectedFields);
					dataParams.put(parm, newParams);
			}
		}
			
	}
	private boolean saveRow() {
		if (name.getText().isEmpty()) {
			OptionMessage.displayMessage("Name must be entered");
			return false;
		}
		int count = 0;
		if (accountsCB.isSelected()) 
			count++;
		if (addressCB.isSelected())
			count++;
		if (budgetsCB.isSelected())
			count++;
		if (currenciesCB.isSelected())
			count++;
		if (securitiesCB.isSelected())
			count++;
		if (lotsCB.isSelected())
			count++;
		if (transactionsCB.isSelected())
			count++;
		if (invTransCB.isSelected())
			count++;
		if (budgetItemsCB.isSelected())
			count++;
		if (categoriesCB.isSelected())
			count++;
		if (securityPricesCB.isSelected())
			count++;
		if (currencyRatesCB.isSelected())
			count++;
		if (remindersCB.isSelected())
			count++;
		if (count < 1) {
			OptionMessage.displayMessage("At least one selection must be chosen");
			return false;
		}
		else
		{
			boolean updateName=false;
			SelectionDataRow tempRow = new SelectionDataRow();
			if (!newRow && !row.getName().equals(name.getText()))
				updateName=true;
			if ((newRow || updateName) && tempRow.loadRow(name.getText(), params)) {
				if (OptionMessage.yesnoMessage("Data Parameters already exists.  Do you wish to overwrite them?"))  
					tempRow.delete(params);
				else
					return false;
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
		}
		return true;
	}
	private void updateParms() {
		row.setAccounts(accountsCB.isSelected());
		row.setAcctSec(acctSecCB.isSelected());
		row.setAddress(addressCB.isSelected());
		row.setBudgets(budgetsCB.isSelected());
		row.setTransactions(transactionsCB.isSelected());
		row.setInvTrans(invTransCB.isSelected());
		row.setLots(lotsCB.isSelected());
		row.setCurrencies(currenciesCB.isSelected());
		row.setSecurities(securitiesCB.isSelected());
		row.setBudgetItems(budgetItemsCB.isSelected());
		row.setCategories(categoriesCB.isSelected());
		row.setSecurityPrices(securityPricesCB.isSelected());
		row.setCurrencyRates(currencyRatesCB.isSelected());
		row.setReminders(remindersCB.isSelected());
		row.setParameters(dataParams);
	}

}
