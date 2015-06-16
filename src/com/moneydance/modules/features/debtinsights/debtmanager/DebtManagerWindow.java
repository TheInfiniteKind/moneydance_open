/*
 * DebtManagerWindow.java
 * 
 * Created on Oct 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.awt.HeadlessException;

import javax.swing.JOptionPane;
import javax.swing.JScrollPane;

import com.infinitekind.moneydance.model.Account;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.SecondaryFrame;
import com.moneydance.awt.AwtUtil;


public class DebtManagerWindow extends SecondaryFrame
{
	private DebtManagerPanel view;
	
	public DebtManagerWindow(MoneydanceGUI mdGUI) throws HeadlessException
	{
		super(mdGUI, "Debt Manager");
		
		if (hasDebtAccounts(mdGUI.getCurrentAccount()))
		{
			DMDebtAccountView ccAccountView = new DMDebtAccountView(mdGUI);
			ccAccountView.setActive(true);
	
			view = new DebtManagerPanel(ccAccountView);
			add(new JScrollPane(view));
					
		    AwtUtil.centerWindow(this);
		}
		else
		{
			JOptionPane.showMessageDialog(this,
				    "There are no CreditCard or Loan Accounts to show.");
		}
	}
		
	public boolean refresh()
	{
		if (this.view != null)
		{
			this.view.refresh();
			return true;
		}
			return false;

	}
	
	
	private boolean hasDebtAccounts(Account root)
	{
		if (root.getSubAccountCount() > 0)
		{
			for (int i=0; i < root.getSubAccountCount(); i++)
			{
				if (hasDebtAccounts(root.getSubAccount(i)) == true)
				{
					return true;
				}
				else if ( isDebtAccount(root.getSubAccount(i)) == true)
				{
					return true;
				}
			}
		}
		return false;
	}
	
	private boolean isDebtAccount(Account acct)
	{
		return acct.getAccountType() == Account.AccountType.CREDIT_CARD || 
					 acct.getAccountType() == Account.AccountType.LOAN;
	}

	/* (non-Javadoc)
	 * @see com.moneydance.apps.md.view.gui.SecondaryFrame#preferencesUpdated()
	 */
	@Override
	public void preferencesUpdated()
	{
		super.preferencesUpdated();
	}
}
