/*
 * CreditLimitDisplay.java
 * 
 * Created on Sep 18, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.creditdisplay;

import javax.swing.JLabel;
import javax.swing.SwingConstants;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class InterestRateDisplay implements CreditLimitComponent
{
	
	public static final InterestRateDisplay instance = new InterestRateDisplay();
	private InterestRateDisplay()
	{
	}

	@Override
	public JLinkLabel getComponent(CreditCardViewPanel ccvp, 
																 Account acct,
																 long balanceAmt)
	{
		
		Double rate = acct.getAPRPercent();
		String creditLimitStr = rate.toString() + "%";

		return new JLinkLabel(creditLimitStr, acct, SwingConstants.RIGHT);
	}

	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		return new JLabel(Strings.BLANK);
	}

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent#getTotal(com.infinitekind.moneydance.model.AccountBook)
	 */
	@Override
	public long getTotal(AccountBook root)
	{
		return 0;
	}
}
