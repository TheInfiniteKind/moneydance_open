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
import com.moneydance.apps.md.controller.BalanceType;
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
	@UsedViaReflection
	public static Long getTotalDebtPayment(AccountBook root, DebtAmountWrapper aw)
	{
		return CreditCardPaymentDisplay.instance.getTotal(root) + getLoanTotalPayment(root);
	}

	@UsedViaReflection
	public static Long getTotalDebtInterest(AccountBook root, DebtAmountWrapper aw)
	{
		Util.logConsole(true, "In AccountUtils: getTotalDebtInterest()");
		return InterestPmtDisplay.instance.getTotal(root) + getTotalLoanInterestPayment(root);
	}
	
	@UsedViaReflection
	public static Long getTotalDebtBalance(AccountBook root, DebtAmountWrapper aw)
	{
		return aw.getAmount();
	}
	
	@UsedViaReflection
	public static long getCreditCardLimitTotal(AccountBook root, DebtAmountWrapper aw)
	{
		return CreditLimitDisplay.instance.getTotal(root);
	}

	@UsedViaReflection
	public static Double getAverageAPR(AccountBook acct, DebtAmountWrapper aw)
	{
		return aw.getAverageRate();
	}


	
////////////
// Support calls
///////////

	private static long getLoanTotalPayment(AccountBook cc)
	{
		long limit = 0;
		List<Account> ccList = cc.getRootAccount().getSubAccounts();
		for (Account sub: ccList)
		{
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.LOAN)
			{
				limit += BetterLoanAccount.getNextPayment(sub);
			}
		}
		return limit;
	}

	private static long getTotalLoanInterestPayment(AccountBook cc)
	{
		long limit = 0;
		List<Account> ccList = cc.getRootAccount().getSubAccounts();
		for (Account sub: ccList)
		{
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.LOAN)
			{
				limit += BetterLoanAccount.getInterestPayment(sub);
			}
		}
		return Math.min(0, limit);
	}
	
	
	
	private static int getChildCount(Account acct)
	{
		int index = 0;
		for (Account sub : acct.getSubAccounts())
		{
			if (acct.getAccountType() == sub.getAccountType())
				++index;
		}
		return index;
	}

	public static CurrencyType getRelCurrency(CurrencyType currency, Account parentAcct) {
	return currency.getRelativeCurrency();

//    String relCurrID = currency.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR);
//
//	Util.logConsole(true, "relID: '" + relCurrID + "' - relative: '" + "' - OR std: '" + currency.getRelativeCurrency() + "'");;
//
//    if (relCurrID != null) {
//      CurrencyType relCurr = currency.getBook().getCurrencies().getCurrencyByIDString(relCurrID);
//      if (relCurr != null) {
//      	return relCurr;}
//    }
//    Util.logConsole(true, "********************* returning: '" + parentAcct.getCurrencyType() + "'");
//    return parentAcct.getCurrencyType();
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
				if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.CREDIT_CARD)
				{
//					aw.add(sub.getBalance(), sub.getAPRPercent());
					aw.add(getActiveXBalance(sub, Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()), sub.getAPRPercent());
				}
				else if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() ==Account.AccountType.LOAN)
				{
//					aw.add(sub.getBalance(), sub.getInterestRate());
					aw.add(getActiveXBalance(sub, Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()), sub.getInterestRate());
				}
			}
		}

	}


	public static long getActiveXRecursiveBalance(Account account, BalanceType balType)
	{
		long bal = getActiveXBalance(account, balType);

        for (Account sub : account.getSubAccounts()) {
            bal += CurrencyUtil.convertValue(getActiveXRecursiveBalance(sub, balType), sub.getCurrencyType(), account.getCurrencyType());
        }
        return bal;
    }


	public static long getActiveXBalance(Account account, BalanceType balType) {

		if (account.getAccountOrParentIsInactive())
			return 0L;

		switch (balType) {
			case CLEARED_BALANCE:
				return account.getClearedBalance();
			case CURRENT_BALANCE:
				return account.getCurrentBalance();
			case CONFIRMED_BALANCE:
				return account.getConfirmedBalance();
			default:
				return account.getBalance();
		}
	}

}
