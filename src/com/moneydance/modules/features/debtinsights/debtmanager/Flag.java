/*
 * Flag.java
 * 
 * Created on Nov 3, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.io.IOException;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import javax.swing.JLabel;

public enum Flag
{
	RED ("flag_red.png"),
	YELLOW("flag_yellow.png"),
	GREEN("flag_green.png");
	
	private ImageIcon flag;
	
	private Flag(String path)
	{
		try
		{
			
			flag = new ImageIcon(ImageIO.read( getClass().getResourceAsStream("/com/moneydance/modules/features/debtinsights/images/" + path) ) );
		}
		catch (IOException e)
		{
			System.err.println("Error: " + e);
		}
	}
	
	public JLabel makeFlag(String msg)
	{
		JLabel jLbl = new JLabel(flag);
		jLbl.setOpaque(true);
		jLbl.setBorder(HeaderConstants.flagBorder);
		jLbl.setToolTipText(msg);
		
		return jLbl;
	}
}
