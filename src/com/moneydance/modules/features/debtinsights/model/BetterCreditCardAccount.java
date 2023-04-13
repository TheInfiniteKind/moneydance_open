/*
 * BetterCreditCardAccount.java
 *
 * Created on Oct 1, 2013
 * Last Modified: 31st March 2023
 * Last Modified By: Stuart Beesley
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
import com.moneydance.awt.JCurrencyField;
import com.moneydance.awt.JRateField;
import com.moneydance.modules.features.debtinsights.*;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.creditcards.PaymentCalc;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;

import javax.swing.*;

/**
 * Essentially a giant wrapper around CreditCardAccount.  There is no good way
 * to replace the built in CreditCardAccount with this class but I can pass
 * all settings through the wrapped account class and send my new parameters as
 * well.
 *
 * @author Robert Schmid
 */
public class BetterCreditCardAccount
        extends DebtAccount {
    //	private static final Log log = LogFactory.getLog(BetterCreditCardAccount.class);
    private Account wrappedAcct;

    private static final String MD_PAYMENT_SPEC = "pmt_spec";

//	private static final String CC_PAYMENT_VAR = "cc_payment_var";
//	private static final String CC_PAYMENT_CALC = "cc_payment_calc";

//	private static final String CC_RATE_CHANGE_DATE = "cc_rate_change_date";
//	private static final String CC_PERMANENT_APR = "cc_permanent_apr";
//	private static final String CC_HAS_CREDIT_LIMIT = "cc_has_credit_limit";

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

    public static long getInterestPayment(Account acct) {
        return getInterestPayment(acct, false);
    }

    public static long getInterestPayment(Account acct, boolean recursive) {
        return getInterestPayment(acct, false, null, recursive);
    }

    public static long getInterestPayment(Account acct, boolean convertToBase, DebtViewPanel ccvp) {
        return getInterestPayment(acct, convertToBase, ccvp, false);
    }

    public static long getInterestPayment(Account acct, boolean convertToBase, DebtViewPanel ccvp, boolean recursive) {
        CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();
//		BalanceType balType = ccvp != null ? ccvp.getBalanceType() : BalanceType.CURRENT_BALANCE;
        BalanceType balType = Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType();
        long interest = 0L;
        long bal = AccountUtils.getActiveXRecursiveBalance(acct, balType);
        long convBal = convertToBase ? CurrencyUtil.convertValue(bal, acct.getCurrencyType(), base) : bal;
        interest += Math.round(convBal * acct.getAPR() / 1200f);        // Divide by 100 and then by 12 months!
        Util.logConsole(true, "BCCA.getInterestPayment() BT: " + balType + " Acct: " + acct + " Bal: " + bal + " int: " + interest);

//        if (recursive){
//            for (Account sub : acct.getSubAccounts()){
//                interest += CurrencyUtil.convertValue(getInterestPayment(sub, convertToBase, ccvp, recursive), sub.getCurrencyType(), acct.getCurrencyType());
//            }
//        }

        return Math.min(0, interest);
    }

//	public static long getDisplayBalance(Account wrappedAcct, BalanceType bType)
//	{
//		switch (bType) {
//			case BALANCE:
//				return wrappedAcct.getBalance();
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

    public static long getCreditDisplay(Account wrappedAcct, BalanceType bType, CreditLimitType cType) {
        switch (cType) {
            case CREDIT_LIMIT:
                return getCreditLimit(wrappedAcct);
            case AVAILABLE_CREDIT:
                return getCreditLimit(wrappedAcct) - AccountUtils.getActiveXBalance(wrappedAcct, bType);
            default:
                return getCreditLimit(wrappedAcct);
        }
    }

    public static double getAPR(Account wrappedAcct) {
        if (wrappedAcct.getSubAccountCount() > 0) {
            return AccountUtils.getAverageAPR(wrappedAcct);
        }
        return getAPRPercent(wrappedAcct);
    }

    public static long getAvailableCredit(Account wrappedAcct, BalanceType balType) {
        if (wrappedAcct.getAccountOrParentIsInactive() || !getHasCreditLimit(wrappedAcct))
            return 0L;

//		long bal = getBalanceForType(wrappedAcct, balType);
        long bal = AccountUtils.getActiveXRecursiveBalance(wrappedAcct, balType);
        long limit = getCreditLimit(wrappedAcct);
        Util.logConsole(true, "Inside: BCCA.getAvailableCredit() - returning creditLimit: " + (limit + bal));
        ;
//        return (limit + bal);
        return Math.max(0L, limit + bal);
    }

////	private static long getBalanceForType(Account wrappedAcct, BalanceType balType)
////	{
////		if (wrappedAcct.getSubAccountCount() == 0) {
////			switch (balType) {
////				case CURRENT_BALANCE:
////					return wrappedAcct.getUserCurrentBalance();
////				case BALANCE:
////					return wrappedAcct.getBalance();
////				case CLEARED_BALANCE:
////					return wrappedAcct.getUserClearedBalance();
////				default:
////					return wrappedAcct.getUserBalance();
////			}
////		}
////		switch (balType) {
////			case CURRENT_BALANCE:
////				return wrappedAcct.getRecursiveUserBalance();
////			case BALANCE:
////				return wrappedAcct.getRecursiveBalance();
////			case CLEARED_BALANCE:
////				return wrappedAcct.getRecursiveUserClearedBalance();
////			default:
////				return wrappedAcct.getRecursiveUserBalance();
////		}
//	}

    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //  BetterCreditCard Methods                                              //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

//    private static long getCalculatedPayments(Account acct) {
//        long pmt = 0;
//        for (Account sub : acct.getSubAccounts()) {
//            if (!sub.getAccountOrParentIsInactive())
//                pmt += BetterCreditCardAccount.getCalculatedPayments(sub);
//        }
//        return pmt;
//    }

    public static long getNextPayment(Account acct) {
        return getNextPayment(acct, false);
    }

    public static long getNextPayment(Account acct, boolean recursive) {

        long pmt = 0;

        if (!acct.getAccountOrParentIsInactive() && acct.getAccountType() == Account.AccountType.CREDIT_CARD) {

            double pmtPct = acct.getDebtPaymentProportion();
            PaymentCalc calcMethod = getCalcMethod(acct);

            boolean overrideToBalance = Main.getWidgetOverridePaymentPlanBalance();

            switch (calcMethod) {
                case FIXED_PAYMENT:
                    long pmtAmt = -Math.abs(acct.getDebtPaymentAmount());       // Assume we always mean the Fixed PP is meant to result in a payment (negative)
                    long balCheck = Math.min(0L, AccountUtils.getActiveXBalance(acct, overrideToBalance ? BalanceType.BALANCE : Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()));
                    pmt = Math.max(balCheck, pmtAmt);
                    break;
                case CLEARED_BALANCE:
                    pmt = Math.min(0L, AccountUtils.getActiveXBalance(acct, overrideToBalance ? BalanceType.BALANCE : BalanceType.CLEARED_BALANCE));
                    break;
                case CURRENT_BALANCE:
                    pmt = Math.min(0L, AccountUtils.getActiveXBalance(acct, overrideToBalance ? BalanceType.BALANCE : BalanceType.CURRENT_BALANCE));
                    break;
                case BALANCE:
                    pmt = Math.min(0L, AccountUtils.getActiveXBalance(acct, BalanceType.BALANCE));
                    break;
                case PERCENTAGE_OF_CLEARED_BALANCE:
                    pmt = Math.round(Math.min(0L, AccountUtils.getActiveXBalance(acct, overrideToBalance ? BalanceType.BALANCE : BalanceType.CLEARED_BALANCE)) * pmtPct);
                    break;
                case PERCENTAGE_OF_CURRENT_BALANCE:
                    pmt = Math.round(Math.min(0L, AccountUtils.getActiveXBalance(acct, overrideToBalance ? BalanceType.BALANCE : BalanceType.CURRENT_BALANCE)) * pmtPct);
                    break;
                case PERCENTAGE_OF_BALANCE:
                    pmt = Math.round(Math.min(0L, AccountUtils.getActiveXBalance(acct, BalanceType.BALANCE)) * pmtPct);
                    break;
            }
        }

    //        if (pmt == 0 && acct.getSubAccountCount() > 0) {
    //            pmt = getCalculatedPayments(acct);                // Seems to always return zero?!
    //        }
        pmt = -Math.abs(pmt);

        Util.logConsole(true, "Inside: BCCA.getNextPayment() acct: " + acct + " recursive: " + recursive + " pmt: " + pmt);

        if (recursive) {
            for (Account sub : acct.getSubAccounts()) {
				if (!sub.getAccountOrParentIsInactive()) {
                    pmt += CurrencyUtil.convertValue(getNextPayment(sub, recursive), sub.getCurrencyType(), acct.getCurrencyType());
                    Util.logConsole(true, "...Inside: BCCA.getNextPayment(): recursing... " + acct + " pmt: " + pmt);
                }
            }
        }

        return pmt;
    }


//	public static float getPaymentVariable(Account wrappedAcct) {
//		double pmtAmt = wrappedAcct.getCurrencyType().getDoubleValue(wrappedAcct.getDebtPaymentAmount());
//		double pmtPct = wrappedAcct.getDebtPaymentProportion();
//		PaymentCalc calcMethod = getCalcMethod(wrappedAcct);
//
//		switch (calcMethod) {
//			case FIXED_PAYMENT:
//				if (pmtAmt != 0) return (float) (pmtAmt);
//				break;
//			case PERCENTAGE_OF_CLEARED_BALANCE:
//				long clearedBal = wrappedAcct.getClearedBalance();
//				if (clearedBal != 0 && pmtPct != 0){
//					Util.logConsole(true, "clearedBal: " + clearedBal + " pmtPct:" + pmtPct);;
//					Util.logConsole(true, "" + (float) (wrappedAcct.getCurrencyType().getDoubleValue(clearedBal) * -pmtPct));
//					return (float) (wrappedAcct.getCurrencyType().getDoubleValue(clearedBal) * -pmtPct);}
//				break;
//			case PERCENTAGE_OF_CURRENT_BALANCE:
//				long currentBal = wrappedAcct.getCurrentBalance();
//				if (currentBal != 0 && pmtPct != 0)
//					return (float) (wrappedAcct.getCurrencyType().getDoubleValue(currentBal) * -pmtPct);
//				break;
//			case CLEARED_BALANCE:
//				return wrappedAcct.getClearedBalance();
//			case CURRENT_BALANCE:
//				return wrappedAcct.getCurrentBalance();
//		}
//		return 0f;
//	}

    //  public static float getPaymentVariable(Account wrappedAcct) {
//		String pv = wrappedAcct.getParameter(CC_PAYMENT_VAR, Strings.BLANK);
//		if (pv == null || pv.length() == 0 || Float.parseFloat(pv) == 0) {
//			AbstractTxn lastCredit = TransactionsUtil.getInstance(wrappedAcct).getFirstPostClearedCredit();
//			if (lastCredit == null)
//				lastCredit = TransactionsUtil.getInstance(wrappedAcct).getLastClearedCredit();
//			switch (getCalcMethod(wrappedAcct)) {
//				case FIXED_PAYMENT:
//					if (lastCredit != null)
//						return -lastCredit.getValue() / 100f;
//					break;
//				case CLEARED_BALANCE:
//					return wrappedAcct.getClearedBalance();
//				case CURRENT_BALANCE:
//					return wrappedAcct.getCurrentBalance();
//				case PERCENTAGE_OF_CLEARED_BALANCE:
//					if (lastCredit != null) {
//						long pmt = lastCredit.getValue();
//						long bal = wrappedAcct.getClearedBalance();
//						return -pmt * 100f / bal;
//					}
//					break;
//				case PERCENTAGE_OF_CURRENT_BALANCE:
//					if (lastCredit != null) {
//						long pmt = lastCredit.getValue();
//						long bal = wrappedAcct.getCurrentBalance();
//						return -pmt * 100f / bal;
//					}
//					break;
//			}
//		}
//		return Float.parseFloat(pv.length() == 0 ? "0" : pv);
//	}
//
    public static PaymentCalc getCalcMethod(Account wrappedAcct) {
        PaymentCalc pc = PaymentCalc.getCalcMethod(wrappedAcct.getParameter(MD_PAYMENT_SPEC));
        return (pc == null ? PaymentCalc.PERCENTAGE_OF_CURRENT_BALANCE : pc);
    }

//	/**
//	 * @param paymentCalc the calculatedPayment to set
//	 */
//	public static void setPaymentVariable(Account wrappedAcct, float paymentCalc)
//	{
//		wrappedAcct.setParameter(CC_PAYMENT_VAR, paymentCalc);
//	}
//
//	/**
//	 * @param paymentCalc the calculatedPayment to set
//	 */
//	public static void setPaymentVariable(Account wrappedAcct, String paymentCalc)
//	{
//		wrappedAcct.setParameter(CC_PAYMENT_VAR, paymentCalc);
//	}
//
//	public static void setCalcMethod(Account wrappedAcct, PaymentCalc calcMethod)
//	{
//		wrappedAcct.setParameter(CC_PAYMENT_CALC, calcMethod.getLabel());
//	}
//
//	/**
//	 * @param calcMethod the calcMethod to set
//	 */
//	public static void setCalcMethod(Account wrappedAcct, String calcMethod)
//	{
//		wrappedAcct.setParameter(CC_PAYMENT_CALC, calcMethod);
//	}

    public static double getPermanentAPR(Account wrappedAcct) {
//		return wrappedAcct.getDoubleParameter(CC_PERMANENT_APR, 0f);
        return 0f;
    }

//	public static void setPermanentAPR(Account wrappedAcct, double apr)
//	{
//		wrappedAcct.setParameter(CC_PERMANENT_APR, apr);
//	}

    public static Date getRateChangeDate(Account wrappedAcct) {
//		return new Date(wrappedAcct.getLongParameter(CC_RATE_CHANGE_DATE, 0));
        return new Date(0);
    }

//	public static void setRateChangeDate(Account wrappedAcct, Date date)
//	{
//		wrappedAcct.setParameter(CC_RATE_CHANGE_DATE, date.getTime());
//	}

    public static boolean getHasCreditLimit(Account wrappedAcct) {
//		return wrappedAcct.getBooleanParameter(CC_HAS_CREDIT_LIMIT, true);
        return true;
    }

//	public static void setHasCreditLimit(Account wrappedAcct, boolean has)
//	{
//		 wrappedAcct.setParameter(CC_HAS_CREDIT_LIMIT, has);
//	}


    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //  Wrapper Methods	                                                      //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    public static double getAPRPercent(Account wrappedAcct) {
        if (getRateChangeDate(wrappedAcct).after(new Date()) || getPermanentAPR(wrappedAcct) <= 0)
            return wrappedAcct.getAPRPercent();
        return getPermanentAPR(wrappedAcct);
    }

    public static long getCreditLimit(Account wrappedAcct) {
        Util.logConsole(true, "BCCA.getCreditLimit() - account: " + wrappedAcct);
        long pmt = 0L;
        if (!wrappedAcct.getAccountOrParentIsInactive()) {
            pmt += wrappedAcct.getCreditLimit();
        }
        for (Account sub : wrappedAcct.getSubAccounts()) {
            if (!sub.getAccountOrParentIsInactive()) {
                pmt += getCreditLimit(sub);
            }
        }
        Util.logConsole(true, "... returning limit:" + pmt);
        return pmt;
    }

    //	public static long getCreditLimit(Account wrappedAcct, CurrencyType relCurr)
//	{
//		long pmt = CurrencyUtil.convertValue(wrappedAcct.getCreditLimit(), wrappedAcct.getCurrencyType(), relCurr);
//		for (Account sub : wrappedAcct.getSubAccounts()) {
//			pmt += CurrencyUtil.convertValue(getCreditLimit(sub, relCurr), sub.getCurrencyType(), relCurr);
//		}
//		return pmt;
//	}

}
