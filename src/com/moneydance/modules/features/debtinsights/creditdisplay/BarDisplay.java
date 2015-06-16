/*
 * BarDisplay.java
 * 
 * Created on Sep 18, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.creditdisplay;

import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JProgressBar;
import javax.swing.plaf.ProgressBarUI;

import com.infinitekind.moneydance.model.*;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;


public abstract class BarDisplay implements CreditLimitComponent
{
	
	protected BarDisplay()
	{
	}

	@Override
	public JComponent getComponent(CreditCardViewPanel ccvp, Account acct, long balanceAmt)
	{
		if (acct.getCreditLimit() <= 0)
		{
			return new JLabel(" ");
		}
//		long min = getMin(acct);
//		long max = getMax(acct);
//		long bal = getValue(acct,balanceAmt);
		
		JProgressBar bar = new JProgressBar(JProgressBar.HORIZONTAL,getMin(acct), getMax(acct));
		bar.setValue(getValue(acct, balanceAmt));
		
		if (getProgressBarUI() != null)
			bar.setUI(getProgressBarUI());
		
		return bar;
	}
	
	protected abstract int getValue(Account acct, long balanceAmt);

	protected ProgressBarUI getProgressBarUI()
	{
		return null;
	}
	

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent#getTotal(com.moneydance.modules.features.debtinsights.CreditCardViewPanel, com.infinitekind.moneydance.model.AccountBook)
	 */
	@Override
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root)
	{
		return null;
	}
	

	protected int getMin(Account acct)
	{
		return 0;
	}

	protected int getMax(Account acct)
	{
		return  (int) acct.getCreditLimit();
	}

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent#getTotal(com.infinitekind.moneydance.model.AccountBook)
	 */
	@Override
	public long getTotal(AccountBook root)
	{
		return 0;
	}

}
