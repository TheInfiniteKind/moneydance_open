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

	public Comparable<?> getComparable(Account a1, Object... params)
	{
		try
		{
			Method m1 = a1.getClass().getMethod(this.comparatorAccessor, args);	
			Object[] actualParams = null;
			if (args != null && args.length > 0)
			{
				actualParams = new Object[args.length];
				for (int i=0; i < args.length; i++)
				{
					actualParams[i] = params[i];
				}
			}
			return (Comparable<?>) m1.invoke(a1, actualParams);
		}
		catch (NoSuchMethodException e)
		{
			System.err.println(this.comparatorAccessor + " not found in " +
												 a1.getClass().getSimpleName() + ": " + e);
		}
		catch (IllegalArgumentException e)
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

		return null;
	}
}
