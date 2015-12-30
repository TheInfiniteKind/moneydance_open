/*
 * DebtAccountComparator.java
 * 
 * Created on Oct 13, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.model;

import java.util.Comparator;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountUtil;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.debtmanager.DebtManagerPanel;
import com.moneydance.modules.features.debtinsights.debtmanager.Header;
import com.moneydance.modules.features.debtinsights.ui.acctview.SortView;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class DebtAccountComparator implements Comparator<Account>
{
//	private static Log log = LogFactory.getLog(DebtAccountComparator.class);
	
	private Header header;
	private CreditLimitType cType;
	private BalanceType bType;
	private SortView order;

	public DebtAccountComparator(Header header, DebtViewPanel panel, SortView order) 
	{
		this.header = header;
		this.bType = panel.getBalanceType();
		if (panel instanceof DebtManagerPanel)
		{
			this.cType = DebtManagerPanel.getCreditLimitType();
		}
		this.order = order;
	}

	@SuppressWarnings({ "rawtypes", "unchecked"})
	@Override
	public int compare(Account a1, Account a2)
	{
    if (a1 == null && a2 == null)	return 0;
    if (a1 == null) return -1;
    if (a2 == null) return 1;
    
    int c = this.header.compareAccounts(a1, a2, bType, cType);
    return (c==0 ? AccountUtil.compareAccountNames(a1, a2) : c) * order.direction;
  }
	
	public void toggleOrder()
	{
		this.order = order.toggleOrder();
	}
	
	public SortView getOrder()
	{
		return this.order;
	}
	
	public Header getHeader()
	{
		return this.header;
	}
}
