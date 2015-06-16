/*
 * IconToggle.java
 * 
 * Created on Oct 20, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.ui.acctview;

import javax.swing.Icon;


public interface IconToggle
{
	public String getLabel();
	public Enum<? extends IconToggle> getNextState();
	public Icon getIcon();
	public IconToggle getState(DebtAccountView acctView);
}
