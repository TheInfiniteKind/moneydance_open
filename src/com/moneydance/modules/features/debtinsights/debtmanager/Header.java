/*
 * Header.java
 * 
 * Created on Oct 13, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import javax.swing.JComponent;
import javax.swing.SwingConstants;
import javax.swing.border.Border;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.model.DebtAccount;
import com.moneydance.modules.features.debtinsights.ui.acctview.HierarchyView;
import com.moneydance.modules.features.debtinsights.ui.acctview.IconToggle;
import com.moneydance.modules.features.debtinsights.ui.acctview.SortView;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public enum Header implements HeaderConstants, Strings
{

	HIERARCHY	(BLANK,		BLANK,	null, 
					HierarchyView.EXPAND_ALL,	SwingConstants.CENTER,	
					nameBorder,		GroupListener.class, null),
	NAME		("Name",	"TOTAL",	null, 		
					SortView.OFF, 				SwingConstants.LEFT,	
					nameBorder,		SortListener.class, "getAccountName"),
	ACCT_NUM	("Acct #",	BLANK,	null, 			
					SortView.OFF, 				SwingConstants.LEFT,	
					textBorder,		SortListener.class,	"getAccountNumber"),
	PAYMENT		("Payment*",	"getTotalDebtPayment",	"Calculated payments are estimated", 
					SortView.OFF, 				SwingConstants.RIGHT,	
					flaggedBorder,	SortListener.class,	"getNextPayment"),
	PMT_FLG 	(BLANK, BLANK, null, SortView.OFF, SwingConstants.LEFT, nameBorder, null, BLANK),
	INTEREST	("Interest*",	"getTotalDebtInterest",	"Estimated", 
			SortView.OFF, 				SwingConstants.RIGHT,	
			amountBorder,	SortListener.class,	"getInterestPayment"),
	BALANCE		("Balance",	"getTotalDebtBalance", null, 
					SortView.OFF, 				SwingConstants.RIGHT,	
					flaggedBorder,	SortListener.class,	"getDisplayBalance", BalanceType.class),
	BAL_FLG 	(BLANK, BLANK, null, SortView.OFF, SwingConstants.LEFT, nameBorder, null, BLANK),
	LIMIT		("Limit",	"getCreditCardLimitTotal", null, 
					SortView.OFF, 				SwingConstants.RIGHT,	
					amountBorder,	SortListener.class,	"getCreditDisplay", BalanceType.class, CreditLimitType.class),
	APR			("APR*",		"getAverageAPR", "Some APRs are estimated", 
					SortView.OFF, 				SwingConstants.RIGHT,	
					flaggedBorder,	SortListener.class,	"getAPR"),
	APR_FLG 	(BLANK, BLANK, null, SortView.OFF, SwingConstants.LEFT, nameBorder, null, BLANK);
	
	public String label;
	public String totAccessor;
	public String tooltip;
	public Enum<? extends IconToggle> icon;
	public int align;
	public Border border;
	private Class<? extends TableHeaderListener> listenerClass;
	private TableHeaderListener listener;
	public String comparatorAccessor;
	private Class<?>[] args = null;
//	private Object[] params = null;

	
	private Header(String label, String totalStr, String tooltip,
					Enum<? extends IconToggle> toggle, int align, Border border, 
					Class<? extends TableHeaderListener> listener, 
					String comparatorAccessor, Class<?>... argClasses)
	{
		this.label = label;
		this.totAccessor = totalStr;
		this.tooltip = tooltip;
		this.icon = toggle;
		this.align = align;
		this.border = border;
		this.listenerClass = listener;
		this.comparatorAccessor = comparatorAccessor;
		this.args = argClasses;
	}
	
	public TableHeaderListener getListener(JComponent comp, Header header, DebtViewPanel viewPanel)
	{
		if (this.listener == null && listenerClass != null)
		{
			try
			{
				Constructor<TableHeaderListener> m = 
					(Constructor<TableHeaderListener>) listenerClass.getConstructor(JComponent.class, Header.class, DebtViewPanel.class);
				this.listener = m.newInstance(comp, header, viewPanel);
			}
			catch (IllegalArgumentException e)
			{
				System.err.println("Error: " + e);
			}
			catch (InstantiationException e)
			{
				System.err.println("Error: " + e);
			}
			catch (IllegalAccessException e)
			{
				System.err.println("Error: " + e);
			}
			catch (InvocationTargetException e)
			{
				System.err.println("Error: " + e);
			}
			catch (SecurityException e)
			{
				System.err.println("Error: " + e);
			}
			catch (NoSuchMethodException e)
			{
				System.err.println("Error: " + e);
			}
		}
		return this.listener;
	}

  
  public int compareAccounts(Account a1, Account a2, BalanceType bType, CreditLimitType cType) {
    if(bType==null) bType = BalanceType.BALANCE;
    if(cType==null) cType = CreditLimitType.CREDIT_LIMIT;
    long tmp = 0;
    switch(this) {
      case HIERARCHY: 
      case NAME:
        return AccountUtil.compareAccountNames(a1, a2);
      case ACCT_NUM: // account number 
        return a1.getBankAccountNumber().compareTo(a2.getBankAccountNumber());
      case PAYMENT:
        tmp = DebtAccount.getNextPayment(a1)-DebtAccount.getNextPayment(a2);
        if(tmp<0) return -1;
        if(tmp>0) return 1;
        return 0;
      case PMT_FLG:
        return 0;
      case INTEREST:
        tmp = DebtAccount.getInterestPayment(a1)-DebtAccount.getInterestPayment(a2);
        if(tmp<0) return -1;
        if(tmp>0) return 1;
        return 0;
      case BALANCE:
        tmp = DebtAccount.getDisplayBalance(a1, bType) - DebtAccount.getDisplayBalance(a2, bType);
        if(tmp<0) return -1;
        if(tmp>0) return 1;
        return 0;
      case BAL_FLG:
        return 0;
      case LIMIT:
        tmp = DebtAccount.getCreditDisplay(a1, bType, cType) - DebtAccount.getCreditDisplay(a2, bType, cType);
        if(tmp<0) return -1;
        if(tmp>0) return 1;
        return 0;
      case APR:
        double aprDiff = DebtAccount.getAPR(a1) - DebtAccount.getAPR(a2);
        if(aprDiff<0) return -1;
        if(aprDiff>0) return 1;
        return 0;
      case APR_FLG:
        return 0;
    }
    return 0;
  }
  
}
