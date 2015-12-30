/*
 * SortView.java
 * 
 * Created on Oct 20, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.ui.acctview;

import javax.swing.Icon;
import javax.swing.ImageIcon;

import com.moneydance.awt.ArrowIcon;
import com.moneydance.modules.features.debtinsights.Strings;


public enum SortView implements IconToggle
{
	ASC (Strings.BLANK, new ArrowIcon(ArrowIcon.NORTH, true), 1), 
	DESC (Strings.BLANK,new ArrowIcon(ArrowIcon.SOUTH, true), -1), 
	OFF (Strings.BLANK, new ImageIcon("com/moneydance/apps/md/debtView/gui/images/gear16.png"), 0);

	private String label;
	private Icon icon;
	public int direction;
	
	private SortView (String label, Icon icon, int order)
	{
		this.label = label;
		this.icon = icon;
		this.direction = order;
	}
	
	@Override
	public String getLabel()
	{
		return this.label;
	}
	@Override
	public SortView getNextState()
	{
		int i = ordinal() + 1;
		return values()[i % values().length];
	}
	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.ui.acctview.IconToggle#getIcon()
	 */
	@Override
	public Icon getIcon()
	{
		return this.icon;
	}
	
	public SortView toggleOrder()
	{
		SortView order = getNextState();
		return (order == OFF ? order.getNextState() : order);
	}
	

	@Override
	public IconToggle getState(DebtAccountView acctView)
	{
		return (acctView.getAcctComparator() != null 
				? acctView.getAcctComparator().getOrder()
				: null);
	}

}
