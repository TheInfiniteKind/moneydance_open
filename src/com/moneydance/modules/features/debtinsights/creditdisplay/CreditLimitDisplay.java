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
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.ui.MyJLinkLabel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class CreditLimitDisplay extends NumericDisplay
{
	public static final CreditLimitDisplay instance = new CreditLimitDisplay();
	
	protected CreditLimitDisplay()
	{
	}
	@Override
	public MyJLinkLabel getComponent(CreditCardViewPanel ccvp, Account acct, long balanceAmt)
	{
		if (BetterCreditCardAccount.getHasCreditLimit(acct))
		{
			return super.getComponent(ccvp, acct, balanceAmt);
		}
		
		return new MyJLinkLabel("N/A",null, SwingConstants.RIGHT);
	}	

	@Override
	protected Long getDisplayAmount(CreditCardViewPanel ccvp, 
																	Account acct,
																	long balanceAmt)
	{
		return acct.getCreditLimit();
	}

	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		long creditLimit = getTotal(root);

		CurrencyType base = root.getCurrencies().getBaseType();

		JLabel lbl = new JLabel(base.formatFancy(creditLimit, ccvp.getDec()), SwingConstants.RIGHT);

		if (creditLimit > 0) {
			if (Main.getWidgetEnhancedColors())
				lbl.setForeground(Util.getPositiveGreen());
		}
		if (creditLimit < 0) {
			Color negFGColor = ccvp.getAcctView().getMDGUI().getColors().negativeBalFG;
			lbl.setForeground(negFGColor);
		}

		return lbl;
	}

	@Override
	public long getTotal(AccountBook root)
	{
		CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();
		return getTotal(root.getRootAccount(), base);
	}


	public long getTotal(Account startAcct, CurrencyType base){
		long creditLimit = CurrencyUtil.convertValue(startAcct.getCreditLimit(), startAcct.getCurrencyType(), base);
		for (Account sub: startAcct.getSubAccounts())
		{
			if (!sub.getAccountOrParentIsInactive() && sub.getAccountType() == Account.AccountType.CREDIT_CARD)
			{
				creditLimit += getTotal(sub, base);
			}
		}
		return creditLimit;
	}


}