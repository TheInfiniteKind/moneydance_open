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

import java.util.Collections;
import java.util.List;

import javax.swing.JLabel;
import javax.swing.SwingConstants;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class CreditLimitDisplay extends NumericDisplay
{
	public static final CreditLimitDisplay instance = new CreditLimitDisplay();
	
	protected CreditLimitDisplay()
	{
	}


	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.NumericDisplay#getComponent(com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel, com.infinitekind.moneydance.model.CreditCardAccount, long)
	 */
	@Override
	public JLinkLabel getComponent(CreditCardViewPanel ccvp,
																 Account acct, long balanceAmt)
	{
		if (BetterCreditCardAccount.getHasCreditLimit(acct))
		{
			return super.getComponent(ccvp, acct, balanceAmt);
		}
		
		return new JLinkLabel("N/A",null, SwingConstants.RIGHT);
	}	

	@Override
	protected Long getDisplayAmount(CreditCardViewPanel ccvp, 
																	Account acct,
																	long balanceAmt)
	{
		return acct.getCreditLimit();
	}

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent#getTotal()
	 */
	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		long creditLimit = getTotal(root);
		
		CurrencyType baseCurr = root.getCurrencies().getBaseType();

		return new JLabel(baseCurr.formatFancy(creditLimit, ccvp.getDec()), SwingConstants.RIGHT);
	}


	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent#getTotal(com.infinitekind.moneydance.model.AccountBook)
	 */
	@Override
	public long getTotal(AccountBook root)
	{
		long creditLimit = 0;
		for (Account acct: root.getRootAccount().getSubAccounts())
		{
			if (acct.getAccountType()== Account.AccountType.CREDIT_CARD)
			{
				creditLimit += BetterCreditCardAccount.getCreditLimit(acct);
			}
		}
		return creditLimit;

	}	
}
