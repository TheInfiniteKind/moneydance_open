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

import java.awt.Color;
import java.util.Collections;
import java.util.List;

import javax.swing.JLabel;
import javax.swing.SwingConstants;

import com.infinitekind.moneydance.model.*;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class CreditCardPaymentDisplay extends NumericDisplay
{
	
	public static final CreditCardPaymentDisplay instance = new CreditCardPaymentDisplay();
	protected CreditCardPaymentDisplay()
	{
	}

	@Override
	protected Long getDisplayAmount(CreditCardViewPanel ccvp, 
									Account acct,
									long balanceAmt)
	{
		return getPayment(acct);
	}

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent#getTotal()
	 */
	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		long totalPayment = getTotal(root);
		
		CurrencyType baseCurr = root.getCurrencies().getBaseType();
		
		JLabel lbl = new JLabel(baseCurr.formatFancy(totalPayment, ccvp.getDec()), SwingConstants.RIGHT);
		if (totalPayment < 0)
		{
			Color negFGColor = ((CreditCardViewPanel) ccvp).getCcAccountView().getMDGUI().getColors().negativeBalFG;
			lbl.setForeground(negFGColor);
		}
		return lbl;
	}	
	
	protected Long getPayment(Account bcca)
	{
		return BetterCreditCardAccount.getNextPayment(bcca);
	}

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent#getTotal(com.infinitekind.moneydance.model.AccountBook)
	 */
	@Override
	public long getTotal(AccountBook root)
	{
		long totalPayment = 0; //AccountUtils.getCreditCardTotalPayment(root);
		for (Account acct: root.getRootAccount().getSubAccounts()){
			if (acct.getAccountType()== Account.AccountType.CREDIT_CARD) {
				totalPayment += getPayment(acct); //.getNextPayment();
			}
		}
		return totalPayment;
	}
}
