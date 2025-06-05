package com.moneydance.modules.features.qifloader;

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
	private String strAcctName;
	private String strAcctRealName;
	private int iTranType;
	public FieldLine(String strTypep, 
			String strAcctNamep, Account acctp, int iTranTypep) {
		strType = strTypep;
		strAcctName = strAcctNamep;
		acct = acctp;
		strAcctRealName = acct.getFullAccountName();
		iTranType = iTranTypep;
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
