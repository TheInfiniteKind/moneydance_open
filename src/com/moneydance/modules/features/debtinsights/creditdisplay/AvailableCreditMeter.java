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


public class AvailableCreditMeter extends BarDisplay
{
	public static final AvailableCreditMeter instance = new AvailableCreditMeter();
	private AvailableCreditMeter()
	{
	}

	@Override
	protected int getValue(Account acct, long balanceAmt)
	{
		return (int) (acct.getCreditLimit() + balanceAmt);
	}
}
