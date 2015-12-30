/*
 * DMDebtAccountView.java
 * 
 * Created on Sep 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.ui.acctview;

import javax.swing.*;

import com.infinitekind.moneydance.model.Account;
import com.moneydance.apps.md.controller.UserPreferences;
import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;

public class CreditCardAccountView extends GenericDebtAccountView
{
	public String creditLimitTypePref = "gui.home.cc_limit_type";
//	private AccountView gav;
	   
	public CreditCardAccountView(Main main)
	{
		this(main.getMDGUI());
	}

	public CreditCardAccountView(MoneydanceGUI mdGUI)
	{
		super(mdGUI, "internal.cc_accts",
					Account.AccountType.CREDIT_CARD, "home_cc_balances", UserPreferences.GUI_HOME_CC_BAL,
					UserPreferences.GUI_HOME_CC_EXP);
	}
	

	/* (non-Javadoc)
     * @see com.moneydance.modules.features.debtinsights.BetterAccountView#getGUIView(com.infinitekind.moneydance.model.AccountBook)
     */
    @Override
    public JComponent getGUIView(AccountBook AccountBook)
    {
		if (this.debtView != null) return this.debtView;
		synchronized (this)
		{
			if (this.debtView == null)
			{
				this.debtView = new CreditCardViewPanel(this, getAccountType());
				this.debtView.setBorder(BorderFactory.createCompoundBorder(MoneydanceLAF.homePageBorder,
																																	 BorderFactory.createEmptyBorder(0, 10, 0, 10)));
			}
			return this.debtView;
		}
    }


//	public String getCCLimitTypeStr(int balType)
//	{
//		CreditLimitType type = CreditLimitType.fromInt(balType);
//		return type.getMenuName();
//	}

	@Override
	public String getID()
	{
		return "DebtInsights-CreditCard";
	}
	
	/* (non-Javadoc)
     * @see java.lang.Object#toString()
     */
    @Override
    public String toString()
    {
	    return "Enhanced Credit Cards";
    }

}
