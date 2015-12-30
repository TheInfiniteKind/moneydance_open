/*
 * TableHeaderListener.java
 * 
 * Created on Oct 13, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.awt.event.MouseListener;

import javax.swing.JComponent;

import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public abstract class TableHeaderListener implements MouseListener
{
	protected JComponent source;
	protected Header header;
	protected DebtViewPanel viewPanel;
	
	public TableHeaderListener(JComponent source, Header header, DebtViewPanel viewPanel)
	{
		this.source = source;
		this.header = header;
		this.viewPanel = viewPanel;
	}
}
