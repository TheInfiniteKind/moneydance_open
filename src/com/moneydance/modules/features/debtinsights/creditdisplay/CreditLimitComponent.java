/*
 * CreditLimitComponent.java
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

import com.infinitekind.moneydance.model.*;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;


public interface CreditLimitComponent
{
	public JComponent getComponent(CreditCardViewPanel ccvp, Account acct, long balanceAmt);
	public long getTotal(AccountBook root);
	public JLabel getDisplayTotal(DebtViewPanel ccvp, AccountBook root);
}
