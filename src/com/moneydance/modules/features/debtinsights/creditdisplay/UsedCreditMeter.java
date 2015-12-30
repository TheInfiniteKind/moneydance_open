/*
 * CreditLimitDisplay.java
 * 
 * Created on Sep 18, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.creditdisplay;

import javax.swing.plaf.ProgressBarUI;

import com.infinitekind.moneydance.model.*;


public class UsedCreditMeter extends BarDisplay
{
	public static final UsedCreditMeter instance = new UsedCreditMeter();

	private UsedCreditMeter()
	{
	}

	@Override
	protected int getValue(Account acct, long balanceAmt)
	{
		return (int) -balanceAmt;
	}

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.creditdisplay.BarDisplay#getProgressBarUI()
	 */
	@Override
	protected ProgressBarUI getProgressBarUI()
	{
		return null;
//	    UIManager.put("ProgressBar.background",new Color(0x80, 0x00, 0x00));  
//	    UIManager.put("ProgressBar.foreground",new Color(0x00, 0x80, 0x00)); 
//	    UIManager.put("ProgressBar.selectionBackground",new Color(0x80, 0x00, 0x00));  
//	    UIManager.put("ProgressBar.selectionForeground",new Color(0x00, 0x80, 0x00)); 
////	    UIManager.put("ProgressBar.border",new Color(0x80, 0x80, 0x00));  
//	    UIManager.put("ProgressBar.opaque",Boolean.TRUE);  
//
//		return new TwoToneProgressBarUI();
	}
//
//	private class TwoToneProgressBarUI extends MetalProgressBarUI
//	{
//		public TwoToneProgressBarUI()
//		{
//			super();
//		}		
//	}
	
}
