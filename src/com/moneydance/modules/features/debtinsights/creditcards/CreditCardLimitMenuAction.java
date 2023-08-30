/*
 * CreditCardLimitMenuAction.java
 * 
 * Created on Sep 16, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.creditcards;

import java.awt.event.ActionEvent;

import javax.swing.AbstractAction;
import javax.swing.Icon;

import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;


public class CreditCardLimitMenuAction extends AbstractAction
{
	private CreditLimitType type;
	private CreditCardViewPanel ccvp;
	
	public CreditCardLimitMenuAction(CreditLimitType type, CreditCardViewPanel ccav)
	{
		super(type.getMenuName());
		this.type = type;
		this.ccvp = ccav;
	}
	
	public CreditCardLimitMenuAction(String paramString)
	{
		super(paramString);
	}
	
	public CreditCardLimitMenuAction(String paramString, Icon paramIcon)
	{
		super(paramString, paramIcon);
	}

	@Override
	public void actionPerformed(ActionEvent paramActionEvent)
	{
		boolean different = type.ordinal() != this.ccvp.getCreditLimitType().ordinal();

//		ccvp.prefs.setSetting(	ccvp.getCcAccountView().creditLimitTypePref, type.ordinal());
		ccvp.prefs.setSetting(Main.EXTN_MD_CCLIMIT_PREF_KEY, type.ordinal());

		if (!different) return;
		ccvp.setCreditLimitType(type);
		Util.logConsole(true, "@@@ CreditCardLimitMenuAction:: calling .refresh() ??");
        Main.lastRefreshTriggerWasAccountListener = false;
		ccvp.refresh();
	}
	
	
}
