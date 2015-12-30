/*
 * DebtAccountUtils.java
 * 
 * Created on Oct 15, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.model;

import com.infinitekind.moneydance.model.*;

public class DebtAccountUtils
{
	
	public DebtAccountUtils()
	{
	}
	
	public static Account wrapAccount(Account acct)
	{
		return acct;
//		
//		switch(acct.getAccountType()) {
//			case CREDIT_CARD:
//				return new BetterCreditCardAccount(acct);
//			case LOAN:
//				return new BetterLoanAccount(acct);
//			default:
//				return acct;
//		}
	}
}
