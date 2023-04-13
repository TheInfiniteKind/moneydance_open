/*
 * GroupListener.java
 * 
 * Created on Oct 13, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.awt.event.MouseEvent;

import javax.swing.JComponent;
import javax.swing.JLabel;

import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class GroupListener extends TableHeaderListener
{
	
	public GroupListener(JComponent source, Header header, DebtViewPanel viewPanel)
	{
		super(source, header, viewPanel);
	}

	@Override
	public void mouseClicked(MouseEvent paramMouseEvent)
	{
		Util.logConsole(true, "**** mouseClicked() ***");;
		this.viewPanel.toggleShowHierarchy((JLabel) this.source);
//		-  U+2796
//		+  U+2795	
//		0  U+20E0

	}

	@Override
	public void mousePressed(MouseEvent paramMouseEvent)
	{
	}

	@Override
	public void mouseReleased(MouseEvent paramMouseEvent)
	{
	}

	@Override
	public void mouseEntered(MouseEvent paramMouseEvent)
	{
	}

	@Override
	public void mouseExited(MouseEvent paramMouseEvent)
	{
	}
	
}
