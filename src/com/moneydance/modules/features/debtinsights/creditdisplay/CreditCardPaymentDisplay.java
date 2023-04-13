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

import java.awt.Color;
import java.util.Collections;
import java.util.List;

import javax.swing.JLabel;
import javax.swing.SwingConstants;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.model.BetterLoanAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class CreditCardPaymentDisplay extends NumericDisplay
{
	
	public static final CreditCardPaymentDisplay instance = new CreditCardPaymentDisplay();
	protected CreditCardPaymentDisplay()
	{
	}

	@Override
	protected Long getDisplayAmount(CreditCardViewPanel ccvp, 
									Account acct,
									long balanceAmt)
	{
		return getPayment(acct);
	}

	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		CurrencyType base = root.getCurrencies().getBaseType();

		long totalPayment = 0L;		// long totalPayment = getTotal(root);
		Account startAcct = root.getRootAccount();
		for (Account sub : startAcct.getSubAccounts()) {
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.CREDIT_CARD) {
				totalPayment += getNextPayment(sub, base, ccvp);
			}
		}

		JLabel lbl = new JLabel(base.formatFancy(totalPayment, ccvp.getDec()), SwingConstants.RIGHT);
		if (totalPayment < 0)
		{
			Color negFGColor = ((CreditCardViewPanel) ccvp).getCcAccountView().getMDGUI().getColors().negativeBalFG;
			lbl.setForeground(negFGColor);
		}
		return lbl;
	}	

	private long getNextPayment(Account acct, CurrencyType convertToCurr, DebtViewPanel ccvp)
	{
		long nextPmt = 0L;

		if (!acct.getAccountIsInactive() && acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
			long next = BetterCreditCardAccount.getNextPayment(acct);
			long convNext = CurrencyUtil.convertValue(next, acct.getCurrencyType(), convertToCurr);
			nextPmt += convNext;
			Util.logConsole(true, "CCPD.getNextPayment() Acct: " + acct + " next: " + next + " nextPmt: " + nextPmt);
		}

		for (Account sub : acct.getSubAccounts()) {
			if (!acct.getAccountIsInactive() && acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
				nextPmt += getNextPayment(sub, convertToCurr, ccvp);
			}
		}
		return nextPmt;
	}

	protected Long getPayment(Account bcca)
	{
		return BetterCreditCardAccount.getNextPayment(bcca);
	}


	public long getTotal(Account startAcct, CurrencyType base){
		long totalPayment = CurrencyUtil.convertValue(getPayment(startAcct), startAcct.getCurrencyType(), base);
		for (Account sub: startAcct.getSubAccounts()){
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.CREDIT_CARD) {
				totalPayment += getTotal(sub, base);
			}
		}
		return totalPayment;
	}

	public long getTotal(AccountBook root)
	{
		Util.logConsole(true, "CCPD: getTotal()...");
		// Widget: getTotal for Next Payment
		CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();
		return getTotal(root.getRootAccount(), base);
	}
}
