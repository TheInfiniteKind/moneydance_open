package com.moneydance.modules.features.reportwriter.view;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.FileTime;
import java.util.Date;
import java.util.SortedMap;
import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.gson.stream.JsonReader;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;

public class SelectionDataRow {
	String name;
	Boolean accounts;
	Boolean acctSec;
	Boolean address;
	Boolean budgets;
	Boolean currencies;
	Boolean securities;
	Boolean transactions;
	Boolean invTrans;
	Boolean lots;
	Boolean budgetItems;
	Boolean categories;
	Boolean securityPrices;
	Boolean currencyRates;
	Boolean reminders;
	private SortedMap<String,DataParameter> parameters;
	String fileName;
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public Boolean getAccounts() {
		if (accounts == null)
			return false;
		else
			return accounts;
	}
	public void setAccounts(Boolean accounts) {
		if (accounts == null)
			this.accounts = false;
		else
			this.accounts = accounts;
	}
	public Boolean getAcctSec() {
		if (acctSec == null)
			return false;
		else
			return acctSec;
	}
	public void setAcctSec(Boolean acctSec) {
		if (acctSec == null)
			this.acctSec=false;
		else
			this.acctSec = acctSec;
	}
	public Boolean getAddress() {
		if (address == null)
			return false;
		else
			return address;
	}
	public void setAddress(Boolean address) {
		if (address == null)
			this.address = false;
		else
			this.address = address;
	}
	public Boolean getBudgets() {
		if (budgets == null)
			return false;
		else
			return budgets;
	}
	public void setBudgets(Boolean budgets) {
		if (budgets == null)
			this.budgets = false;
		else
			this.budgets = budgets;
	}
	public Boolean getCurrencies() {
		if (currencies == null)
			return false;
		else
			return currencies;
	}
	public void setCurrencies(Boolean currencies) {
		if (currencies == null)
			this.currencies = false;
		else
			this.currencies = currencies;
	}
	public Boolean getSecurities() {
		if (securities == null)
			return false;
		else
			return securities;
	}
	public void setSecurities(Boolean securities) {
		if (securities == null)
			this.securities = false;
		else
			this.securities = securities;
	}
	public Boolean getTransactions() {
		if (transactions == null)
			return false;
		else
			return transactions;
	}
	public void setTransactions(Boolean transactions) {
		if (accounts == null)
			this.transactions = false;
		else
			this.transactions = transactions;
	}
	
	public Boolean getInvTrans() {
		if (invTrans == null)
			return false;
		else
			return invTrans;
	}
	public void setInvTrans(Boolean invTrans) {
		if (invTrans == null)
			this.invTrans = false;
		else
			this.invTrans = invTrans;
	}
	public Boolean getLots() {
		if (lots == null)
			return false;
		else
			return lots;
	}
	public void setLots(Boolean lots) {
		if (lots == null)
			this.lots=false;
		else
			this.lots = lots;
	}
	public Boolean getBudgetItems() {
		if (budgetItems == null)
			return false;
		else
			return budgetItems;
	}
	public void setBudgetItems(Boolean budgetItems) {
		if (budgetItems == null)
			this.budgetItems = false;
		else
			this.budgetItems = budgetItems;
	}
	public Boolean getCategories() {
		if (categories == null)
			return false;
		else
			return categories;
	}
	public void setCategories(Boolean categories) {
		if (categories == null)
			this.categories = false;
		else
			this.categories = categories;
	}
	public Boolean getSecurityPrices() {
		if (securityPrices == null)
			return false;
		else
			return securityPrices;
	}
	public void setSecurityPrices(Boolean securityPrices) {
		if (securityPrices == null)
			this.securityPrices = false;
		else
			this.securityPrices = securityPrices;
	}
	public Boolean getCurrencyRates() {
		if (currencyRates == null)
			return false;
		else
			return currencyRates;
	}
	public void setCurrencyRates(Boolean currencyRates) {
		if (currencyRates == null)
			this.currencyRates = false;
		else
			this.currencyRates = currencyRates;
	}
	public Boolean getReminders() {
		if (reminders == null)
			return false;
		else
			return reminders;
	}
	public void setReminders(Boolean reminders) {
		if (reminders == null)
			this.reminders = false;
		else
			this.reminders = reminders;
	}
	public SortedMap<String, DataParameter> getParameters() {
		return parameters;
	}
	public void setParameters(SortedMap<String, DataParameter> parameters) {
		this.parameters = parameters;
	}
	public boolean loadRow(String name,Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		fileName = dir+"/"+name+Constants.SELEXTENSION;
		SelectionDataRow row = new SelectionDataRow();
		try {
			JsonReader reader = new JsonReader(new FileReader(fileName));
			row = new Gson().fromJson(reader,SelectionDataRow.class);
			reader.close();
			setName(row.getName());
			setAccounts(row.getAccounts());
			setAcctSec(row.getAcctSec());
			setAddress(row.getAddress());
			setBudgets(row.getBudgets());
			setCurrencies(row.getCurrencies());
			setSecurities(row.getSecurities());
			setTransactions(row.getTransactions());
			setInvTrans(row.getInvTrans());
			setLots(row.getLots());
			setBudgetItems(row.getBudgetItems());
			setCategories(row.getCategories());
			setSecurityPrices(row.getSecurityPrices());
			setCurrencyRates(row.getCurrencyRates());
			setReminders(row.getReminders());
			setParameters(row.getParameters());
			Main.rwDebugInst.debug("SelectionDataRow", "loadRow", MRBDebug.DETAILED, "Row loaded "+name);
		}
		catch (JsonParseException e) {
			Main.rwDebugInst.debug("SelectionDataRow", "loadRow", MRBDebug.DETAILED, "Parse Exception "+e.getMessage());
			return false;
		}
		catch (IOException e){
			return false;
		}
		return true;
	}
	public void touchFile() {
		Path touchFile = Paths.get(fileName);
		try {
			Files.setAttribute(touchFile, "basic:lastAccessTime", FileTime.fromMillis(new Date().getTime()));
		}
		catch (IOException e) {}
		
	}

	public void saveRow(Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		String fileName = dir+"/"+getName()+Constants.SELEXTENSION;
		try {
			   FileWriter writer = new FileWriter(fileName);
			   String jsonString = new Gson().toJson(this);
			   writer.write(jsonString);
			   writer.close();	
			   Main.rwDebugInst.debug("SelectionDataRow", "saveRow", MRBDebug.DETAILED, "Row Saved "+name);
          }
			 catch (IOException i) {
				 Main.rwDebugInst.debug("SelectionDataRow", "saveRow", MRBDebug.DETAILED, "IO Exception "+i.getMessage());
					   i.printStackTrace();
          }
	}
	public void delete(Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		String fileName = dir+"/"+getName()+Constants.SELEXTENSION;
		Main.rwDebugInst.debug("SelectionDataRow", "delete", MRBDebug.SUMMARY, "Delete "+fileName);
		File file = new File(fileName);
		if (file.delete())
			Main.rwDebugInst.debug("SelectionDataRow", "delete", MRBDebug.SUMMARY, "Deleted "+fileName);
		else
			Main.rwDebugInst.debug("SelectionDataRow", "delete", MRBDebug.SUMMARY, "Delete failed "+fileName);

	}
	public void renameRow(String newName,Parameters paramsp) {
		delete(paramsp);
		name = newName;
		saveRow(paramsp);
	}


}
