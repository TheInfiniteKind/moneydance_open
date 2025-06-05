package com.moneydance.modules.features.budgetreport;

import com.infinitekind.moneydance.model.Account;

public class AccountDetails {
	private Account acct;
	private String strParent;
	private BudgetLine objLine;
	public AccountDetails(Account acctp, String strParentp) {
		acct = acctp;
		strParent = strParentp;
	}
	public Account getAccount() {
		return acct;
	}
	public String getParent () {
		return strParent;
	}
	public BudgetLine getLine () {
		return objLine;
	}
	public void setLine (BudgetLine objLinep) {
		objLine = objLinep;
	}

}
