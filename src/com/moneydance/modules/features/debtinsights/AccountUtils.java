/*
 * AccountUtils.java
 * 
 * Created on Sep 13, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights;

import java.util.Collections;
import java.util.List;

import com.infinitekind.moneydance.model.*;
import com.moneydance.modules.features.debtinsights.creditdisplay.CreditCardPaymentDisplay;
import com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitDisplay;
import com.moneydance.modules.features.debtinsights.creditdisplay.InterestPmtDisplay;
import com.moneydance.modules.features.debtinsights.model.BetterLoanAccount;

@SuppressWarnings("unchecked")
public final class AccountUtils
{
	
	private AccountUtils()
	{
	}
	
	///////////////////////
	//Called for Totals Row
	///////////////////////
	public static Long getTotalDebtPayment(AccountBook root, DebtAmountWrapper aw)
	{
		return CreditCardPaymentDisplay.instance.getTotal(root) + getLoanTotalPayment(root);
	}

	public static Long getTotalDebtInterest(AccountBook root, DebtAmountWrapper aw)
	{
		return InterestPmtDisplay.instance.getTotal(root) + getTotalLoanInterestPayment(root);
	}
	
	public static Long getTotalDebtBalance(AccountBook root, DebtAmountWrapper aw)
	{
		return aw.getAmount();
	}
	
	public static long getCreditCardLimitTotal(AccountBook root, DebtAmountWrapper aw)
	{
		return CreditLimitDisplay.instance.getTotal(root);
	}

	public static Double getAverageAPR(AccountBook acct, DebtAmountWrapper aw)
	{
		return aw.getAverageRate();
	}


	
////////////
// Support calls
///////////
	//TODO: Move to LoanPaymentDisplay class?
	private static long getLoanTotalPayment(AccountBook cc)
	{
		long limit = 0;
		List<Account> ccList = cc.getRootAccount().getSubAccounts();
		for (Account sub: ccList)
		{
			if (sub.getAccountType()==Account.AccountType.LOAN)
			{
				limit += BetterLoanAccount.getNextPayment(sub);
			}
		}
		return limit;
	}

	//TODO: Move to LoanInterestPmtDisplay class?
	private static long getTotalLoanInterestPayment(AccountBook cc)
	{
		long limit = 0;
		List<Account> ccList = cc.getRootAccount().getSubAccounts();
		for (Account sub: ccList)
		{
			if (sub.getAccountType()==Account.AccountType.LOAN)
			{
				limit += BetterLoanAccount.getInterestPayment(sub);
			}
		}
		return limit;
	}
	
	
	
	private static int getChildCount(Account acct)
	{
		int index = 0;
		for (int i = 0; i < acct.getSubAccountCount(); ++i)
		{
			if (acct.getAccountType() == acct.getSubAccount(i).getAccountType())
				++index;
		}
		return index;
	}


	public static CurrencyType getRelCurrency(CurrencyType currency, Account parentAcct) {
    String relCurrID = currency.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR);
    if(relCurrID!=null) {
      CurrencyType relCurr = currency.getBook().getCurrencies().getCurrencyByIDString(relCurrID);
      if(relCurr!=null) return relCurr;
    }
    
    return parentAcct.getCurrencyType();
	}

	
	
	private static Double getAverageAPR(DebtAmountWrapper aw)
	{
		return aw.getAverageRate();
	}
	
	public static Double getAverageAPR(Account cc)
	{
		DebtAmountWrapper aw = new DebtAmountWrapper();
		addAccounts(cc, aw);
		return getAverageAPR(aw);
	}
	
	private static void addAccounts(Account root, DebtAmountWrapper aw)
	{
		List<Account> ccList = root.getSubAccounts();
		for (Account sub: ccList)
		{
			if (getChildCount(sub) > 0)
			{
				addAccounts(sub, aw);
			}
			else
			{
				if (sub.getAccountType()== Account.AccountType.CREDIT_CARD)
				{
					aw.add(sub.getBalance(), sub.getAPRPercent());
				}
				else if (sub.getAccountType()==Account.AccountType.LOAN)
				{
					aw.add(sub.getBalance(), sub.getInterestRate());
				}
			}
		}

	}
}
