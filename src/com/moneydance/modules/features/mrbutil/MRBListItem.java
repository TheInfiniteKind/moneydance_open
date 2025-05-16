package com.moneydance.modules.features.mrbutil;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.Account.AccountType;

public class MRBListItem {
	private AccountType acctType;
	private String strName;
	private String strKey;
	private Account acct;
	private Boolean bSelected;
	public MRBListItem (Account acctp){
		acct = acctp;
		acctType = acct.getAccountType();
		strName = acct.getFullAccountName();
		strKey = acctType.name()+"\\"+strName;
		bSelected = false;
	}
	public AccountType getType (){
		return acctType;
	}
	public String getName () {
		return strName;
	}
	public String getKey() {
		return strKey;
	}
	public Account getAccount() {
		return acct;
	}
	public Boolean isSelected() {
		return bSelected;
	}
	public void setSelected(Boolean bSelectedp) {
		bSelected = bSelectedp;
	}
}
