/*
 * GenericDebtAccountView.java
 * 
 * Created on Sep 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */

package com.moneydance.modules.features.debtinsights.ui.acctview;

import com.infinitekind.moneydance.model.Account;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;

public class GenericDebtAccountView extends DebtAccountView
{

	private String	id;
	private Account.AccountType acctType;
	private String	rsrcTag;
	private String	balTypePref;
	private String	expandedPref;

	public GenericDebtAccountView(MoneydanceGUI mdGUI, String id,
	        Account.AccountType acctType, String rsrcTag, String balTypePref,
	        String expandedPref)
	{
		super(mdGUI);
		this.id = id;
		this.acctType = acctType;
		this.rsrcTag = rsrcTag;
		this.balTypePref = balTypePref;
		this.expandedPref = expandedPref;
	}

	@Override
	public void refresh() {
		Util.logConsole(true, "Inside GenericDebtAccountView::refresh():... calling .super()...");
		super.refresh();
	}

	@Override
	public String getID()
	{
		return this.id;
	}

	@Override
	public String toString()
	{
		return this.mdGUI.getStr(this.rsrcTag);
	}

	@Override
	public Account.AccountType getAccountType()
	{
		return this.acctType;
	}

	@Override
	public String getBalanceTypePref()
	{
		return this.balTypePref;
	}

	@Override
	public String getSectionExpandedPref()
	{
		Util.logConsole(true, "GDAV.getSectionExpandedPref(): " + this.expandedPref);
		return this.expandedPref;
	}
}
