/*
 * DMDebtAccountView.java
 * 
 * Created on Sep 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.util.Arrays;
import java.util.List;

import javax.swing.JComponent;

import com.moneydance.apps.md.controller.UserPreferences;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.ui.acctview.GenericDebtAccountView;

public class DMDebtAccountView extends GenericDebtAccountView
{
	public String creditLimitTypePref = "gui.home.cc_limit_type";
	public List<Account.AccountType> debtAccountTypes = 
		Arrays.asList(new Account.AccountType[] { Account.AccountType.CREDIT_CARD,
																							Account.AccountType.LOAN });
	
//	public DMDebtAccountView(MoneydanceGUI mdGUI) {
//		super(mdGUI, "internal.cc_accts",
//				null,
//				"home_cc_balances",
//				UserPreferences.GUI_HOME_CC_BAL,
//		        UserPreferences.GUI_HOME_CC_EXP);
//		setAccountTypes(this.debtAccountTypes);
//	}

	public DMDebtAccountView(MoneydanceGUI mdGUI, String expandedPrefKey)
	{
		super(mdGUI, "internal.cc_accts",
				null,
				"home_cc_balances",
				UserPreferences.GUI_HOME_CC_BAL,
		        expandedPrefKey);

		setAccountTypes(this.debtAccountTypes);
	}
	
	/* (non-Javadoc)
     * @see com.moneydance.modules.features.debtinsights.BetterAccountView#getGUIView(com.infinitekind.moneydance.model.AccountBook)
     */
    @Override
    public JComponent getGUIView(AccountBook AccountBook)
    {
        Util.logConsole(true, ".getGUIView() called (book: " + book + ")");
        if (book == null){
            return null;
        }
		return this.debtView;

//		if (this.debtView != null) return this.debtView;
//		synchronized (this)
//		{
//			if (this.debtView == null)
//			{
//				this.debtView = new DebtManagerPanel(this);
//				this.debtView.setBorder(MoneydanceLAF.homePageBorder);
//			}
//			return this.debtView;
//		}
    }

	public String getCCLimitTypeStr(int balType)
	{
		CreditLimitType type = CreditLimitType.fromInt(balType);
		return type.getMenuName();
	}
//
//	/* (non-Javadoc)
//	 * @see com.moneydance.modules.features.debtinsights.BetterAccountView#getAccountTypes()
//	 */
//	@Override
//	public List<Integer> getAccountTypes()
//	{
//		return this.debtAccountTypes;
//	}
}
