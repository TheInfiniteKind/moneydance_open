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

import java.awt.*;
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
import com.moneydance.modules.features.debtinsights.ui.MyJLinkLabel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class AvailableCreditDisplay extends CreditLimitDisplay
{
	public static final AvailableCreditDisplay instance = new AvailableCreditDisplay();

	protected AvailableCreditDisplay()
	{
	}


	@Override
	public MyJLinkLabel getComponent(CreditCardViewPanel ccvp, Account acct, long balanceAmt)
	{
		if(acct.getCreditLimit()!=0)
		{
			return super.getComponent(ccvp, acct, balanceAmt);
		}
		return new MyJLinkLabel("N/A", null, SwingConstants.RIGHT);
	}	


	@Override
	protected Long getDisplayAmount(CreditCardViewPanel ccvp, Account acct, long balanceAmt)
	{
		Long creditLimit = super.getDisplayAmount(ccvp, acct, balanceAmt);

		if (creditLimit != null && creditLimit > 0)
		{
			return Math.max(0L, creditLimit + balanceAmt);
//			return (creditLimit + balanceAmt);
		}
		return creditLimit;
	}

	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();
		long creditLimit = 0;
		for (Account sub: root.getRootAccount().getSubAccounts())
		{
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.CREDIT_CARD)
			{
				creditLimit += getAvailableCredit(sub, base, ccvp);
				Util.logConsole(true, "Inside: ACD.getDisplayTotal() - creditLimit: " + creditLimit);;
			}
		}
		
		JLabel lbl = new JLabel(base.formatFancy(creditLimit, ccvp.getDec()), SwingConstants.RIGHT);
		if (creditLimit > 0) {
			if (Main.getWidgetEnhancedColors())
				lbl.setForeground(Util.getPositiveGreen());		// This works OK on the row total...!
		}
		if (creditLimit < 0) {
			Color negFGColor = ccvp.getAcctView().getMDGUI().getColors().negativeBalFG;
			lbl.setForeground(negFGColor);
		}
		return lbl;

	}

	private long getAvailableCredit(Account acct, CurrencyType convertToCurr, DebtViewPanel ccvp)
	{
//		BalanceType balType = ccvp.getBalanceType();
		BalanceType balType = Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType();
		Util.logConsole(true, "***Inside ACD.getAvailableCredit() using balType: " + balType);
		long availableCredit = 0L;

		if (!acct.getAccountIsInactive() && acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
//			long bal = AccountUtils.getActiveXBalance(acct, balType);
			long bal = AccountUtils.getActiveXRecursiveBalance(acct, balType);
			long convBal = CurrencyUtil.convertValue(bal, acct.getCurrencyType(), convertToCurr);

			long limit = acct.getCreditLimit();
			long convLimit = CurrencyUtil.convertValue(limit, acct.getCurrencyType(), convertToCurr);

			availableCredit += (convLimit + convBal);
			Util.logConsole(true, "ACD.getAvailableCredit() Acct: " + acct + " bal: " + bal + " convBal: " + convBal + " limit: " + limit + " convLimit: " + convLimit + " availCredit: " + availableCredit);
		}

		for (Account sub : acct.getSubAccounts()) {
			if (!acct.getAccountIsInactive() && acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
				availableCredit += getAvailableCredit(sub, convertToCurr, ccvp);
			}
		}

		return Math.max(0L, availableCredit);
	}

}
