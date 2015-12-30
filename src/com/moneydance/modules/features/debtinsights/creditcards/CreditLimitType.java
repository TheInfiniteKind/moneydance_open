/*
 * CreditLimitType.java
 * 
 * Created on Sep 15, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.creditcards;

import javax.swing.JComponent;
import javax.swing.JLabel;

import com.infinitekind.moneydance.model.*;
import com.moneydance.modules.features.debtinsights.creditdisplay.AvailableCreditDisplay;
import com.moneydance.modules.features.debtinsights.creditdisplay.AvailableCreditMeter;
import com.moneydance.modules.features.debtinsights.creditdisplay.CreditCardPaymentDisplay;
import com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitComponent;
import com.moneydance.modules.features.debtinsights.creditdisplay.CreditLimitDisplay;
import com.moneydance.modules.features.debtinsights.creditdisplay.InterestPmtDisplay;
import com.moneydance.modules.features.debtinsights.creditdisplay.InterestRateDisplay;
import com.moneydance.modules.features.debtinsights.creditdisplay.UsedCreditMeter;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;



public enum CreditLimitType
{
	CREDIT_LIMIT("Credit Limit", null, "ccLimitType_limit", CreditLimitDisplay.instance), 
	AVAILABLE_CREDIT("Available Credit", null, "ccLimitType_avail", AvailableCreditDisplay.instance), 
	AVAILABLE_CREDIT_METER("Available Credit Graph", null, "ccLimitType_avail_meter", AvailableCreditMeter.instance),
	USED_CREDIT_METER("Credit Used Graph", null, "ccLimitType_used_meter", UsedCreditMeter.instance), 
	INTEREST_RATE("APR", null, "ccLimitType_rate", InterestRateDisplay.instance),
	INTEREST_PMT("Next Interest PMT", null, "ccLimitType_int_pmt", InterestPmtDisplay.instance),
	NEXT_PAYMENT("Next Payment", null, "ccLimitType_pmt", CreditCardPaymentDisplay.instance);
	
	public static final CreditLimitType	DEFAULT;
	private  String			menuName;
	private  String			_resourceKey = null;
	private  String			_configKey = null;
	private CreditLimitComponent componentType = null;
	public final int value;
	
	private CreditLimitType (String menuName, String resKey, String configKey, CreditLimitComponent componentClass)
	{
		this.menuName = menuName;
		this._resourceKey = resKey;
		this._configKey = configKey;
		this.value = ordinal();
		this.componentType = componentClass;
	}
	
	public String getResourceKey()
	{
		return this._resourceKey;
	}
	
	public String getConfigKey()
	{
		return this._configKey;
	}
	
	public String getMenuName()
	{
		return this.menuName;
	}
	
	public static CreditLimitType fromInt(int value)
	{
		for (CreditLimitType type : values())
		{
			if (type.ordinal() == value) { return type; }
			
		}
		
		return DEFAULT;
	}
	
	public JComponent getDisplayComponent(CreditCardViewPanel ccvp, Account acct, long balanceAmount) 
	{
		try
		{
			return this.componentType.getComponent(ccvp, acct, balanceAmount);
		}
		catch (Exception e)
		{
//			log.error(e.getMessage(),e);
		}
		return null;
	}
	
	public JLabel getTotal(DebtViewPanel ccvp, AccountBook root)
	{
		try
		{
			return this.componentType.getDisplayTotal(ccvp, root);
		}
		catch (Exception e)
		{
//			log.error(e.getMessage(),e);
		}
		return null;

	}
	
	static
	{
		DEFAULT = CREDIT_LIMIT;
	}
}
