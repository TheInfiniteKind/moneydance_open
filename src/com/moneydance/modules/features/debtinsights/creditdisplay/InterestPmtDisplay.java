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

import com.infinitekind.moneydance.model.*;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;


public class InterestPmtDisplay extends CreditCardPaymentDisplay
{
	public static final InterestPmtDisplay instance = new InterestPmtDisplay();
	private InterestPmtDisplay()
	{
	}

	@Override
	protected Long getPayment(Account acct)
	{
		return BetterCreditCardAccount.getInterestPayment(acct);
	}
}
