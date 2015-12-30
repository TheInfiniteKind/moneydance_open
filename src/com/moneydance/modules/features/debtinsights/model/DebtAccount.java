/*
 * DebtAccount.java
 * 
 * Created on Oct 15, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.model;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;


public abstract class DebtAccount
{
//	public long getCalculatedPayment();
	public abstract Account getWrappedAccount();
//	public long getNextPayment();
//	public long getInterestPayment();
//	public long getDisplayBalance(BalanceType bType);
//	public long getCreditDisplay(BalanceType bType, CreditLimitType type);
//	public double getAPR();


  public static long getCreditDisplay(Account acct, BalanceType bType, CreditLimitType cType) {
    switch (acct.getAccountType()) {
      case CREDIT_CARD:
        return BetterCreditCardAccount.getCreditDisplay(acct, bType, cType);
      case LOAN:
        return BetterLoanAccount.getCreditDisplay(acct, bType, cType);
      default:
        return 0;
    }
  }
  
  public static long getDisplayBalance(Account acct, BalanceType bType) {
    switch (acct.getAccountType()) {
      case CREDIT_CARD:
        return BetterCreditCardAccount.getDisplayBalance(acct, bType);
      case LOAN:
        return BetterLoanAccount.getDisplayBalance(acct, bType);
      default:
        return 0;
    }

  }

	public static long getNextPayment(Account acct) {
		switch (acct.getAccountType()) {
			case CREDIT_CARD:
				return BetterCreditCardAccount.getNextPayment(acct);
			case LOAN:
				return BetterLoanAccount.getNextPayment(acct);
			default:
				return 0;
		}
	}
	
	public static long getInterestPayment(Account acct) {
		switch (acct.getAccountType()) {
			case CREDIT_CARD:
				return BetterCreditCardAccount.getInterestPayment(acct);
			case LOAN:
				return BetterLoanAccount.getInterestPayment(acct);
			default:
				return 0;
		}
	}

	public static double getAPR(Account acct) {
		switch (acct.getAccountType()) {
			case CREDIT_CARD:
				return BetterCreditCardAccount.getAPR(acct);
			case LOAN:
				return BetterLoanAccount.getAPR(acct);
			default:
				return 0f;
		}
	}

}
