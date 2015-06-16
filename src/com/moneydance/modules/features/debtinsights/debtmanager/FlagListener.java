/*
 * FlagListener.java
 * 
 * Created on Nov 3, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.Popup;
import javax.swing.PopupFactory;


public class FlagListener implements MouseListener
{
	private Popup popup;
	private JPanel panel;
	private JLabel lbl;
	private String msg;
	
	public FlagListener(JPanel panel, JLabel lbl, String msg)
	{
		this.panel = panel;
		this.lbl = lbl;
		this.msg = msg;
	}
	
	@Override
	public void mouseClicked(MouseEvent arg0)
	{
	}
	
	@Override
	public void mouseEntered(MouseEvent event)
	{
		PopupFactory factory = PopupFactory.getSharedInstance();
		int x = event.getXOnScreen();
		int y = event.getYOnScreen();
		this.popup = factory.getPopup(panel, new JLabel(msg), x, y);
		this.popup.show();
	}
	
	@Override
	public void mouseExited(MouseEvent arg0)
	{
		popup.hide();
	}
	
	@Override
	public void mousePressed(MouseEvent arg0)
	{
	}
	
	@Override
	public void mouseReleased(MouseEvent arg0)
	{
	}
	
}
