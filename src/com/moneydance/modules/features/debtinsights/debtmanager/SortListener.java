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

import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.model.DebtAccountComparator;
import com.moneydance.modules.features.debtinsights.ui.acctview.SortView;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class SortListener extends TableHeaderListener
{
	private DebtAccountComparator comparator;

	public SortListener(JComponent source, Header header, DebtViewPanel viewPanel)
	{
		super(source, header, viewPanel);
		this.viewPanel = viewPanel;
		this.comparator = new DebtAccountComparator(header, viewPanel, SortView.OFF);
	}
	

	@Override
	public void mouseClicked(MouseEvent paramMouseEvent)
	{
		DMDebtAccountView acctView = (DMDebtAccountView) this.viewPanel.getAcctView();
		comparator.toggleOrder();
		acctView.setAcctComparator(comparator);
		Util.logConsole(true, "@@@ SortListener::mouseClicked() calling .refresh() ??");
        Main.lastRefreshTriggerWasAccountListener = false;
		this.viewPanel.refresh();
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
