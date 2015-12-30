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
import java.util.Date;
import java.util.Enumeration;
import java.util.List;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.TransactionsUtil;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.creditcards.PaymentCalc;

/**
 * Essentially a giant wrapper around CreditCardAccount.  There is no good way
 * to replace the built in CreditCardAccount with this class but I can pass
 * all settings through the wrapped account class and send my new parameters as
 * well.
 * 
 * @author Robert Schmid
 */
public class BetterCreditCardAccount
	extends DebtAccount
{
	//	private static final Log log = LogFactory.getLog(BetterCreditCardAccount.class);
	private Account wrappedAcct;

	private static final String CC_PAYMENT_VAR = "cc_payment_var";
	private static final String CC_PAYMENT_CALC = "cc_payment_calc";
	private static final String CC_RATE_CHANGE_DATE = "cc_rate_change_date";
	private static final String CC_PERMANENT_APR = "cc_permanent_apr";

	private static final String CC_HAS_CREDIT_LIMIT = "cc_has_credit_limit";

  //public BetterCreditCardAccount(Account acct) {
//		this.wrappedAcct = acct;
//	}

//	public BetterCreditCardAccount(BetterCreditCardAccount acct)
//		throws InvalidWrapperException
//	{
//		throw new InvalidWrapperException("Can't wrap a BetterCreditCardAccount in another BetterCreditCardAccount");
//	}

	////////////////////////////////////////////////////////////////////////////
	//                                                                        //
	//  DebtAccount Methods                                                   //
	//                                                                        //
	////////////////////////////////////////////////////////////////////////////

	/**
	 * @return the wrappedAcct
	 */
	@Override
	public Account getWrappedAccount() {
		return wrappedAcct;
	}


//	public static long getCalculatedPayment(Account wrappedAcct)
//
//	{
//		long pmt = 0;
//		switch (getCalcMethod(wrappedAcct)) {
//			case FIXED_PAYMENT:
//				pmt = (long) Math.round(getPaymentVariable(wrappedAcct) * 100f);
//				break;
//			case CLEARED_BALANCE:
//				pmt = wrappedAcct.getClearedBalance();
//				break;
//			case CURRENT_BALANCE:
//				pmt = wrappedAcct.getCurrentBalance();
//				break;
//			case PERCENTAGE_OF_CLEARED_BALANCE:
//				pmt = (long) Math.round(wrappedAcct.getClearedBalance() *
//																getPaymentVariable(wrappedAcct) / 100f);
//				break;
//			case PERCENTAGE_OF_CURRENT_BALANCE:
//				pmt = (long) Math.round(wrappedAcct.getCurrentBalance() *
//																getPaymentVariable(wrappedAcct) / 100f);
//				break;
//		}
//		if (pmt == 0 && wrappedAcct.getSubAccountCount() > 0) {
//			pmt = getCalculatedPayments(wrappedAcct);
//		}
//		return -Math.abs(pmt);
//	}

//	public static long getNextPayment(Account wrappedAcct)
//
//	{
//		return getCalculatedPayment(wrappedAcct);
//	}

	public static long getInterestPayment(Account acct)

	{
		long pmt = (long) Math.round(acct.getCurrentBalance() * acct.getAPR() / 1200f);
		for (Account sub : acct.getSubAccounts()) {
			pmt += BetterCreditCardAccount.getInterestPayment(sub);
		}
		return pmt;
	}

	public static long getDisplayBalance(Account wrappedAcct, BalanceType bType)
	{
		switch (bType) {
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
		switch (cType) {
			case CREDIT_LIMIT:
				return getCreditLimit(wrappedAcct);
			case AVAILABLE_CREDIT:
				return getCreditLimit(wrappedAcct) - getDisplayBalance(wrappedAcct, bType);
			default:
				return getCreditLimit(wrappedAcct);
		}
	}

	public static double getAPR(Account wrappedAcct)
	{
		if (wrappedAcct.getSubAccountCount() > 0) {
			return AccountUtils.getAverageAPR(wrappedAcct);
		}
		return getAPRPercent(wrappedAcct);
	}

	public static long getAvailableCredit(Account wrappedAcct, BalanceType balType)
	{
		if (wrappedAcct.getAccountOrParentIsInactive() || !getHasCreditLimit(wrappedAcct))
			return 0L;

		long bal = getBalanceForType(wrappedAcct, balType);
		long limit = getCreditLimit(wrappedAcct);
		return limit + bal;
	}

	private static long getBalanceForType(Account wrappedAcct, BalanceType balType)
	{
		if (wrappedAcct.getSubAccountCount() == 0) {
			switch (balType) {
				case CURRENT_BALANCE:
					return wrappedAcct.getUserCurrentBalance();
				case BALANCE:
					return wrappedAcct.getBalance();
				case CLEARED_BALANCE:
					return wrappedAcct.getUserClearedBalance();
				default:
					return wrappedAcct.getUserBalance();
			}
		}
		switch (balType) {
			case CURRENT_BALANCE:
				return wrappedAcct.getRecursiveUserBalance();
			case BALANCE:
				return wrappedAcct.getRecursiveBalance();
			case CLEARED_BALANCE:
				return wrappedAcct.getRecursiveUserClearedBalance();
			default:
				return wrappedAcct.getRecursiveUserBalance();
		}
	}
  
	////////////////////////////////////////////////////////////////////////////
	//                                                                        //
	//  BetterCreditCard Methods                                              //
	//                                                                        //
	////////////////////////////////////////////////////////////////////////////

	private static long getCalculatedPayments(Account acct)
	{
		long pmt = 0;
		for (Account account : acct.getSubAccounts()) {
			pmt += BetterCreditCardAccount.getCalculatedPayments(account);
		}
		return pmt;
	}


  public static long getNextPayment(Account acct) {
    //return acct.getPaymentSchedule().getMonthlyPayment();
    long pmt = 0;
    switch (getCalcMethod(acct)) {
      case FIXED_PAYMENT:
        pmt = (long) Math.round(getPaymentVariable(acct)* 100f);
        break;
      case CLEARED_BALANCE:
        pmt =  acct.getClearedBalance();
        break;
      case CURRENT_BALANCE:
        pmt =  acct.getCurrentBalance();
        break;
      case PERCENTAGE_OF_CLEARED_BALANCE:
        pmt = (long) Math.round(acct.getClearedBalance() * getPaymentVariable(acct)/100f);
        break;
      case PERCENTAGE_OF_CURRENT_BALANCE:
        pmt = (long) Math.round(acct.getCurrentBalance() * getPaymentVariable(acct)/100f);
        break;
    }
    if (pmt == 0 && acct.getSubAccountCount() > 0) {
      pmt = getCalculatedPayments(acct);
    }
    return -Math.abs(pmt);
  }



  public static float getPaymentVariable(Account wrappedAcct) {
		String pv = wrappedAcct.getParameter(CC_PAYMENT_VAR, Strings.BLANK);
		if (pv == null || pv.length() == 0 || Float.parseFloat(pv) == 0) {
			AbstractTxn lastCredit = TransactionsUtil.getInstance(wrappedAcct).getFirstPostClearedCredit();
			if (lastCredit == null)
				lastCredit = TransactionsUtil.getInstance(wrappedAcct).getLastClearedCredit();
			switch (getCalcMethod(wrappedAcct)) {
				case FIXED_PAYMENT:
					if (lastCredit != null)
						return -lastCredit.getValue() / 100f;
					break;
				case CLEARED_BALANCE:
					return wrappedAcct.getClearedBalance();
				case CURRENT_BALANCE:
					return wrappedAcct.getCurrentBalance();
				case PERCENTAGE_OF_CLEARED_BALANCE:
					if (lastCredit != null) {
						long pmt = lastCredit.getValue();
						long bal = wrappedAcct.getClearedBalance();
						return -pmt * 100f / bal;
					}
					break;
				case PERCENTAGE_OF_CURRENT_BALANCE:
					if (lastCredit != null) {
						long pmt = lastCredit.getValue();
						long bal = wrappedAcct.getCurrentBalance();
						return -pmt * 100f / bal;
					}
					break;
			}
		}
		return Float.parseFloat(pv.length() == 0 ? "0" : pv);
	}

	public static PaymentCalc getCalcMethod(Account wrappedAcct) {
		PaymentCalc pc = PaymentCalc.getCalcMethod(wrappedAcct.getParameter(CC_PAYMENT_CALC));
		return (pc == null ? PaymentCalc.PERCENTAGE_OF_CURRENT_BALANCE : pc);
	}

	/**
	 * @param paymentCalc the calculatedPayment to set
	 */
	public static void setPaymentVariable(Account wrappedAcct, float paymentCalc)
	{
		wrappedAcct.setParameter(CC_PAYMENT_VAR, paymentCalc);
	}

	/**
	 * @param paymentCalc the calculatedPayment to set
	 */
	public static void setPaymentVariable(Account wrappedAcct, String paymentCalc)
	{
		wrappedAcct.setParameter(CC_PAYMENT_VAR, paymentCalc);
	}

	public static void setCalcMethod(Account wrappedAcct, PaymentCalc calcMethod)
	{
		wrappedAcct.setParameter(CC_PAYMENT_CALC, calcMethod.getLabel());
	}
	
	/**
	 * @param calcMethod the calcMethod to set
	 */
	public static void setCalcMethod(Account wrappedAcct, String calcMethod)
	{
		wrappedAcct.setParameter(CC_PAYMENT_CALC, calcMethod);
	}

	public static double getPermanentAPR(Account wrappedAcct)
	{
		return wrappedAcct.getDoubleParameter(CC_PERMANENT_APR, 0f);
	}
	
	public static void setPermanentAPR(Account wrappedAcct, double apr)
	{
		wrappedAcct.setParameter(CC_PERMANENT_APR, apr);
	}
	
	public static Date getRateChangeDate(Account wrappedAcct)
	{
		return new Date(wrappedAcct.getLongParameter(CC_RATE_CHANGE_DATE, 0));
	}
	
	public static void setRateChangeDate(Account wrappedAcct, Date date)
	{
		wrappedAcct.setParameter(CC_RATE_CHANGE_DATE, date.getTime());
	}
	
	public static boolean getHasCreditLimit(Account wrappedAcct) {
		return wrappedAcct.getBooleanParameter(CC_HAS_CREDIT_LIMIT, true);
	}
	
	public static void setHasCreditLimit(Account wrappedAcct, boolean has)
	{
		 wrappedAcct.setParameter(CC_HAS_CREDIT_LIMIT, has);
	}
	
	
	////////////////////////////////////////////////////////////////////////////
	//                                                                        //
	//  Wrapper Methods	                                                      //
	//                                                                        //
	////////////////////////////////////////////////////////////////////////////

	/* (non-Javadoc)
	 * @see com.infinitekind.moneydance.model.CreditCardAccount#getAPRPercent()
	 */
	public static double getAPRPercent(Account wrappedAcct)
	{
		if (getRateChangeDate(wrappedAcct).after(new Date()) || getPermanentAPR(wrappedAcct) <= 0)
			return wrappedAcct.getAPRPercent();
		return getPermanentAPR(wrappedAcct);
	}


	public static long getCreditLimit(Account wrappedAcct)
	{
		long pmt = wrappedAcct.getCreditLimit();
		for (Account sub : wrappedAcct.getSubAccounts()) {
			pmt += getCreditLimit(sub);
		}
		return pmt;
	}
	
}
