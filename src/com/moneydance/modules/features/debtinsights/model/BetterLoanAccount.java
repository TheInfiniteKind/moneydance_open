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
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;

/**
 * Essentially a giant wrapper around CreditCardAccount.  There is no good way
 * to replace the built in CreditCardAccount with this class but I can pass
 * all settings through the wrapped account class and send my new parameters as
 * well.
 * 
 * @author Robert Schmid
 */
public class BetterLoanAccount extends DebtAccount
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
	
	public static long getCalculatedPayment(Account wrappedAcct){
		return getCalculatedPayment(wrappedAcct, false);
	}

	public static long getCalculatedPayment(Account wrappedAcct, boolean recursive)
	{
		long pmt = 0L;
		if (!wrappedAcct.getAccountOrParentIsInactive()) {
			pmt += wrappedAcct.getPaymentSchedule().getMonthlyPayment();
		}

//		if (pmt == 0 && wrappedAcct.getSubAccountCount() > 0)
//		{
//			for (Account sub : wrappedAcct.getSubAccounts()) {
//				if (!sub.getAccountOrParentIsInactive()) {
//					pmt += getCalculatedPayment(sub);
//				}
//			}
//		}

        pmt = -Math.abs(pmt);

		if (recursive)
		{
			for (Account sub : wrappedAcct.getSubAccounts()) {
				if (!sub.getAccountOrParentIsInactive()) {
	                pmt += CurrencyUtil.convertValue(getCalculatedPayment(sub, recursive), sub.getCurrencyType(), wrappedAcct.getCurrencyType());
				}
			}
		}

		return pmt;
	}
	
//	public static String getAccountNumber(Account wrappedAcct)
//	{
//		return Strings.BLANK + wrappedAcct.getAccountNum();
//	}

	public static long getNextPayment(Account wrappedAcct)
	{
		return getNextPayment(wrappedAcct, false);
	}

	public static long getNextPayment(Account wrappedAcct, boolean recursive)
	{
		return getCalculatedPayment(wrappedAcct, recursive);
	}

	
//	public long getInterestPayment()
//	{
//		return (long) Math.round(wrappedAcct.getCurrentBalance() * getAPR()/1200f);
//	}
//
	public static long getInterestPayment(Account acct) {
		return getInterestPayment(acct, false);
	}

	public static long getInterestPayment(Account acct, boolean recursive){
		return getInterestPayment(acct, false, null, recursive);
	}

	public static long getInterestPayment(Account wrappedAcct, boolean convertToBase, DebtViewPanel ccvp) {
		return getInterestPayment(wrappedAcct, convertToBase, ccvp, false);
	}

	public static long getInterestPayment(Account wrappedAcct, boolean convertToBase, DebtViewPanel ccvp, boolean recursive)
	{
		CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();

		//		long bal = wrappedAcct.getCurrentBalance();

//		BalanceType balType = ccvp != null ? ccvp.getBalanceType() : BalanceType.CURRENT_BALANCE;
		BalanceType balType = Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType();
		long bal = AccountUtils.getActiveXRecursiveBalance(wrappedAcct, balType);
		long interest = 0L;

		long convBal = convertToBase ? CurrencyUtil.convertValue(bal, wrappedAcct.getCurrencyType(), base) : bal;
		interest += Math.round(convBal * getAPR(wrappedAcct) / 1200f);		// Divide by 100 and then by 12 months!
		Util.logConsole(true, "BLA.getInterestPayment() BT: " + balType + " Acct: " + wrappedAcct + " Bal: " + bal + "int: " + interest);

//		if (recursive) {
//			for (Account sub : wrappedAcct.getSubAccounts()) {
//				interest += CurrencyUtil.convertValue(getInterestPayment(sub, convertToBase, ccvp, recursive), sub.getCurrencyType(), wrappedAcct.getCurrencyType());
//			}
//		}

		return Math.min(0, interest);
	}


//	public static long getDisplayBalance(Account wrappedAcct, BalanceType bType)
//	{
//		switch (bType)
//		{
//			case CLEARED_BALANCE:
//				return wrappedAcct.getClearedBalance();
//			case CURRENT_BALANCE:
//				return wrappedAcct.getCurrentBalance();
//			case CONFIRMED_BALANCE:
//				return wrappedAcct.getConfirmedBalance();
//			default:
//				return wrappedAcct.getBalance();
//		}
//	}

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
