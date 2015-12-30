/*
 * HierarchyView.java
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

public enum HierarchyView implements IconToggle
{
	EXPAND_ALL ("+", new ImageIcon("com/moneydance/apps/md/debtView/gui/images/plus-8.png")), //\u2795"), 
	COLLAPSE_ALL ("-", new ImageIcon("com/moneydance/apps/md/debtView/gui/images/minus-8.png")), //\u2796"), 
	FLATTEN ("\u20E0", new ImageIcon("com/moneydance/apps/md/debtView/gui/images/gear16.png"));
	
	private String label;
	private Icon icon;

	private HierarchyView(String label, Icon icon)
	{
		this.label = label;
		this.icon = icon;
	}
	
	public static HierarchyView getNextState(HierarchyView view)
	{
		int i = view.ordinal() + 1;
		return values()[i % 3];
	}
	
	@Override
	public HierarchyView getNextState()
	{
		int i = ordinal() + 1;
		return values()[i % values().length];
	}
	
	@Override
	public String getLabel()
	{
		return this.label;
	}
	
	@Override
	public Icon getIcon()
	{
		return this.icon;
	}

	@Override
	public IconToggle getState(DebtAccountView acctView)
	{
		return acctView.getHierarchyView();
	}
}


