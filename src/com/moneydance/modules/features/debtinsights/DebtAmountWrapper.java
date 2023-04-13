/*
 * DebtAmountWrapper.java
 * 
 * Created on Sep 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights;

import com.infinitekind.moneydance.model.Account;

public class DebtAmountWrapper
{

	private long		amount;
	public boolean		hasValidAccts	= false;
	private double		cumulativeRate;

	public DebtAmountWrapper()
	{
	}

	public void scannedAccount(Account acct)
	{
		if (this.hasValidAccts) return;
		if (acct.getAccountOrParentIsInactive()) return;
		if (!(acct.getHideOnHomePage()))
		{
			this.hasValidAccts = true;
		}
		else
		{
			if ((acct.getUserCurrentBalance() == 0L)
			        && (acct.getUserClearedBalance() == 0L)
			        && (acct.getUserBalance() == 0L)) { return; }
			this.hasValidAccts = true;
		}
	}
	
	public void add(long amount, double rate)
	{
		this.amount += amount;
		this.cumulativeRate += amount * rate;
	}
	
	public double getAverageRate()
	{
		return Math.round(this.cumulativeRate * 100d / this.amount)/100d;
	}
	
	public long getAmount()
	{
		return this.amount;
	}
}