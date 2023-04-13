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

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;

import javax.swing.*;
import java.awt.*;


public class InterestPmtDisplay extends CreditCardPaymentDisplay
{
	public static final InterestPmtDisplay instance = new InterestPmtDisplay();
	private InterestPmtDisplay()
	{
	}

	@Override
	protected Long getPayment(Account acct)
	{
		return BetterCreditCardAccount.getInterestPayment(acct);
	}

	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		CurrencyType base = root.getCurrencies().getBaseType();

		long totalPayment = 0L;		// long totalPayment = getTotal(root);
		Account startAcct = root.getRootAccount();
		for (Account sub : startAcct.getSubAccounts()) {
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.CREDIT_CARD) {
				totalPayment += getInterestPayment(sub, base, ccvp);
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

	private long getInterestPayment(Account acct, CurrencyType convertToCurr, DebtViewPanel ccvp)
	{
//		BalanceType balType = (ccvp == null) ? BalanceType.CURRENT_BALANCE : ccvp.getBalanceType();
		BalanceType balType = Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType();
		long intPmt = 0L;

		if (!acct.getAccountIsInactive() && acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
//			long bal = AccountUtils.getActiveXBalance(acct, balType);
			long bal = AccountUtils.getActiveXRecursiveBalance(acct, balType);
			long convBal = CurrencyUtil.convertValue(bal, acct.getCurrencyType(), convertToCurr);
			intPmt += Math.round(convBal * acct.getAPR() / 1200f);        // Divide by 100 and then by 12 months!
			Util.logConsole(true, "IPD.getInterestPayment() BT: " + balType + " Acct: " + acct + " bal: " + bal + " convBal: " + convBal + " intPmt: " + intPmt);
		}

//		for (Account sub : acct.getSubAccounts()) {
//			if (!acct.getAccountIsInactive() && acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
//				intPmt += getInterestPayment(sub, convertToCurr, ccvp);
//			}
//		}
		return Math.min(0, intPmt);
	}

	public long getTotal(AccountBook root)
	{
		Util.logConsole(true, "IPD: getTotal()...");
		CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();

		long totalPayment = 0L;
		Account startAcct = root.getRootAccount();
		for (Account sub : startAcct.getSubAccounts()) {
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.CREDIT_CARD) {
				totalPayment += getInterestPayment(sub, base, null);
			}
		}
		return totalPayment;

	}

}
