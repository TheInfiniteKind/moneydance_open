package com.moneydance.modules.features.loadsectrans;

import java.io.Serializable;

import com.infinitekind.moneydance.model.Account;


public class FieldLine implements Serializable {
	/*
	 * Static and transient fields are not stored 
	 */
	private static final long serialVersionUID = 1L;
	private transient Account acct;

 /*
     * The following fields are stored
     */

	private String strType;
	private String strAcctName;  // full path name for category
	private String strAcctRealName;
	private int iTranType;
	public FieldLine(String fieldType,
			String acctName, Account acct, int tranType) {
		this.strType = fieldType;
		this.strAcctName = acctName;
		this.acct = acct;
		if (acct != null)
			strAcctRealName = this.acct.getFullAccountName();
		else
			strAcctRealName = acctName;
		this.iTranType = tranType;
	}
	public String getType() {
		return strType;
	}
	public int getTranType() {
		return iTranType;
	}
	public Account getAccount() {
		return acct;
	}
	public String getAccountName() {
		return strAcctName;
	}
	public void setAccountObject (){
		acct = Main.context.getRootAccount().getAccountByName(strAcctRealName);
	}
	public void setAccount(String strAcctNamep, Account acctp) {
		strAcctName = strAcctNamep;
		strAcctRealName = acctp.getFullAccountName();
		acct = acctp;
	}
	public void setTranType(int iTranTypep) {
		iTranType = iTranTypep;
	}
	public void setType (String strTypep) {
		strType = strTypep;
	}

}
