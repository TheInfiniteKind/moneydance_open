/*
 * NumericDisplay.java
 * 
 * Created on Sep 18, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.creditdisplay;

import java.awt.Color;

import javax.swing.SwingConstants;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.model.DebtAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;


public abstract class NumericDisplay implements CreditLimitComponent
{
	private static final String UNKNOWN = "??";
	public NumericDisplay()
	{
	}
	
	@Override
	public JLinkLabel getComponent(CreditCardViewPanel ccvp, 
																 Account acct,
																 long balanceAmt)
	{
		JLinkLabel creditLimitDisplay = new JLinkLabel(Strings.BLANK, acct, SwingConstants.RIGHT);
		Long displayAmt = null;
		String creditLimitStr = UNKNOWN;
		if (!acct.getAccountOrParentIsInactive())
		{
			CurrencyType relCurr = AccountUtils.getRelCurrency(acct.getCurrencyType(), acct.getParentAccount());
			displayAmt = getDisplayAmount(ccvp, acct, balanceAmt);

			if (displayAmt != null)
			{
				displayAmt = CurrencyUtil.convertValue(displayAmt, 
													acct.getCurrencyType(),
													relCurr);
				
				creditLimitStr = relCurr.formatFancy(displayAmt, ccvp.getDec());
			}
		}
		creditLimitDisplay.setText(creditLimitStr);
		
		if (displayAmt < 0L)
		{
			Color negFGColor = ccvp.getCcAccountView().getMDGUI().getColors().negativeBalFG;
			creditLimitDisplay.setForeground(negFGColor);
		}

		return creditLimitDisplay;
	}
	
	protected abstract Long getDisplayAmount(CreditCardViewPanel ccvp, 
																					 Account acct,
																					 long balanceAmt);

}
