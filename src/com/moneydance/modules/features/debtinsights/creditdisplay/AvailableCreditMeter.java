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
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;

import javax.swing.*;


public class AvailableCreditMeter extends BarDisplay
{
	public static final AvailableCreditMeter instance = new AvailableCreditMeter();
	private AvailableCreditMeter()
	{
	}

	@Override
	public JComponent getComponent(CreditCardViewPanel ccvp, Account acct, long balanceAmt)
	{
		JComponent bar = super.getComponent(ccvp, acct, balanceAmt);
		Util.logConsole(true, "ACM.getComponent()...");
		if (Main.getWidgetEnhancedColors()) {
			bar.setForeground(Util.getPositiveGreen());
		}
		return bar;
	}


	@Override
	protected int getValue(Account acct, long balanceAmt)
	{
		return (int) (acct.getCreditLimit() + balanceAmt);
	}
}
