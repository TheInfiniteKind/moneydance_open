/*
 * DMDebtAccountView.java
 * 
 * Created on Sep 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */

package com.moneydance.modules.features.debtinsights.ui.acctview;

import java.util.*;

import javax.swing.JComponent;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.AccountFilter;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.apps.md.view.HomePageView;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;
import com.moneydance.apps.md.view.gui.homepage.AccountView;
import com.moneydance.modules.features.debtinsights.model.DebtAccount;
import com.moneydance.modules.features.debtinsights.model.DebtAccountComparator;
import com.moneydance.modules.features.debtinsights.model.DebtAccountUtils;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;

public abstract class DebtAccountView implements HomePageView
{
	protected DebtViewPanel	       debtView	             = null;
	private List<Account.AccountType> acctTypes;
	protected MoneydanceGUI mdGUI;
	private HierarchyView hierarchy = HierarchyView.EXPAND_ALL;
	private DebtAccountComparator acctComparator;

	public DebtAccountView(MoneydanceGUI mdGUI) //, AccountBook AccountBook)
	{
		this.mdGUI = mdGUI;
	}

	public abstract Account.AccountType getAccountType();
	
	public List<Account.AccountType> getAccountTypes()
	{
		if (acctTypes == null)
		{
			acctTypes = Arrays.asList(getAccountType());
		}
		return acctTypes;
	}
	
	public void setAccountTypes(List<Account.AccountType> accountTypes)
	{
		this.acctTypes = accountTypes;
	}
	
	public boolean includes(Account.AccountType accountType)
	{
		return getAccountTypes().contains(accountType);
	}
	
	public abstract String getBalanceTypePref();

	public abstract String getSectionExpandedPref();

	@Override
	public JComponent getGUIView(AccountBook AccountBook)
	{
		if (this.debtView != null) return this.debtView;
		synchronized (this)
		{
			if (this.debtView == null)
			{
				this.debtView = new DebtViewPanel(this, getAccountType());
				this.debtView.setBorder(MoneydanceLAF.homePageBorder);
			}
			return this.debtView;
		}
	}

	public MoneydanceGUI getMDGUI()
	{
		return this.mdGUI;
	}

	@Override
	public void setActive(boolean active)
	{
		if (this.debtView != null) 
		{
			if (active)
				this.debtView.activate();
			else
				this.debtView.deactivate();
		}
	}
	
	@Override
	public void refresh()
	{
		if (this.mdGUI.getSuspendRefreshes() == true) 
			return;
		if (this.debtView != null) this.debtView.refresh();
	}


	public String getBalStr(int balType)
	{
		BalanceType type = BalanceType.fromInt(balType);
		return this.mdGUI.getStr(type.getResourceKey());
	}
	
	@Override
	public synchronized void reset()
	{
		setActive(false);
		this.debtView = null;
	}
	/**
	 * @return the showHierarchy
	 */
	public HierarchyView getHierarchyView()
	{
		return hierarchy;
	}

	
	/**
	 * @return the accounts
	 */
	public List<Account> getAccounts(Account parentAccount)
	{	
		if (parentAccount == null) return null ;
		
		List<Account> acctList = AccountUtil.allMatchesForSearch(parentAccount, new AcctFilter() {
		@Override
		public boolean matches(Account account) {
			return getAccountTypes().contains(account.getAccountType());
		}
			
			@Override
		public String format(Account account) { return account.getFullAccountName(); }
		});
		
		if (acctComparator != null)	{
			Collections.sort(acctList, acctComparator);
		}
		return acctList;
	}

	
	/**
	 * @param showHierarchy the showHierarchy to set
	 */
	public void setHierarchyView(HierarchyView showHierarchy)
	{
		this.hierarchy = showHierarchy;
	}

	/**
	 * @param acctComparator the acctComparator to set
	 */
	public void setAcctComparator(DebtAccountComparator acctComparator)
	{
		this.acctComparator = acctComparator;
		refresh();
	}

	/**
	 * return the acctComparator
	 */
	public DebtAccountComparator getAcctComparator()
	{
		return this.acctComparator;
	}
	

//	public static long getBalance(int balType, Account acct) 
//	{
//	    if (acct.getAccountOrParentIsInactive()) return 0L;
//	    
//	    if (acct instanceof DebtAccount) 
//	    	acct = ((DebtAccount) acct).getWrappedAccount();
//	    switch (BalanceType.fromInt(balType)) 
//	    {
//	    	case CURRENT_BALANCE:
//	    		return acct.getUserCurrentBalance();
//	    	case BALANCE:
//	    		return acct.getBalance();
//	    	case CLEARED_BALANCE:
//	    		return acct.getUserClearedBalance();
//	    	default:
//	    		return acct.getUserBalance();
//	    }
//    
//	}
	
	public static long getBalance(BalanceType balType, Account acct) 
	{
	    if (acct.getAccountOrParentIsInactive()) return 0L;
	    switch (balType) {
	    	case CURRENT_BALANCE:
	    		return acct.getUserCurrentBalance();
	    	case BALANCE:
	    		return acct.getBalance();
	    	case CLEARED_BALANCE:
	    		return acct.getUserClearedBalance();
	    	default:
	    		return acct.getUserBalance();
	    }
    
  }

}