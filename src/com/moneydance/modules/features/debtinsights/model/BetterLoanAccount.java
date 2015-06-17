/*
 * BetterCreditCardAccount.java
 * 
 * Created on Oct 1, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.model;

import java.util.Collections;
import java.util.Enumeration;
import java.util.List;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;

/**
 * Essentially a giant wrapper around CreditCardAccount.  There is no good way
 * to replace the built in CreditCardAccount with this class but I can pass
 * all settings through the wrapped account class and send my new parameters as
 * well.
 * 
 * @author Robert Schmid
 */
public class BetterLoanAccount 
	extends DebtAccount
{
	private Account wrappedAcct;
	
	public BetterLoanAccount(Account acct)
	{
		this.wrappedAcct = acct;
	}
	
	public BetterLoanAccount(BetterLoanAccount acct) throws InvalidWrapperException
	{
		throw new InvalidWrapperException("Can't wrap a BetterLoanAccount in another BetterLoanAccount");
//		this.wrappedAcct = (CreditCardAccount) acct;
	}

	////////////////////////////////////////////////////////////////////////////
	//                                                                        //
	//  DebtAccount Methods                                                   //
	//                                                                        //
	////////////////////////////////////////////////////////////////////////////
	
	/**
	 * @return the wrappedAcct
	 */
	@Override
	public Account getWrappedAccount()
	{
		return wrappedAcct;
	}
	
	public static long getCalculatedPayment(Account wrappedAcct)
	{
		long pmt = wrappedAcct.getPaymentSchedule().getMonthlyPayment();
		if (pmt == 0 && wrappedAcct.getSubAccountCount() > 0)
		{
			for (Account sub : wrappedAcct.getSubAccounts()) {
				pmt += getCalculatedPayment(sub);
			}
		}
		
		return -Math.abs(pmt);
	}
	
	public static String getAccountNumber(Account wrappedAcct)
	{
		return Strings.BLANK + wrappedAcct.getAccountNum();
	}

	public static long getNextPayment(Account wrappedAcct)
	{
		return getCalculatedPayment(wrappedAcct);
	}

	
//	@Override
//	public long getInterestPayment()
//	{
//		return (long) Math.round(wrappedAcct.getCurrentBalance() * getAPR()/1200f);
//	}
	
	public static long getInterestPayment(Account wrappedAcct)
	{
		long pmt = (long) Math.round(wrappedAcct.getCurrentBalance() * getAPR(wrappedAcct)/1200f);
		if (pmt == 0 && wrappedAcct.getSubAccountCount() > 0)
		{
			for (Account sub: wrappedAcct.getSubAccounts())	{
				pmt += getInterestPayment(sub);
			}
		}
		return pmt;
	}
	
  
	public static long getDisplayBalance(Account wrappedAcct, BalanceType bType)
	{
		switch (bType)
		{
			case BALANCE:
				return wrappedAcct.getBalance();
			case CLEARED_BALANCE:
				return wrappedAcct.getClearedBalance();
			case CURRENT_BALANCE:
				return wrappedAcct.getCurrentBalance();
			case CONFIRMED_BALANCE:
				return wrappedAcct.getConfirmedBalance();
			default:
				return wrappedAcct.getBalance();
		}
	}

	public static long getCreditDisplay(Account wrappedAcct, BalanceType bType, CreditLimitType cType)
	{
		return 0;
	}

	public static double getAPR(Account wrappedAcct)
	{
		if (wrappedAcct.getSubAccountCount() > 0)
		{
			return AccountUtils.getAverageAPR(wrappedAcct);
		}

		return wrappedAcct.getInterestRate();
	}


}
