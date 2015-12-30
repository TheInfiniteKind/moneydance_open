/*
 * PaymentCalc.java
 * 
 * Created on Oct 1, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights.creditcards;

import java.lang.reflect.Constructor;

import javax.swing.JComponent;
import javax.swing.JLabel;

import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.awt.JCurrencyField;
import com.moneydance.awt.JRateField;
import com.moneydance.modules.features.debtinsights.Strings;


public enum PaymentCalc
{
	FIXED_PAYMENT ("Fixed Amount", JCurrencyField.class, JCurrencyField.class), 
	CLEARED_BALANCE ("Cleared Balance", JLabel.class, JLabel.class), 
	CURRENT_BALANCE ("Current Balance", JLabel.class, JLabel.class), 
	PERCENTAGE_OF_CLEARED_BALANCE("% of Cleared Balance", JRateField.class, JCurrencyField.class),
	PERCENTAGE_OF_CURRENT_BALANCE("% of Current Balance", JRateField.class, JCurrencyField.class);
	
	private String label;
	private Class<? extends JComponent> paymentVarClass;
	private Class<? extends JComponent> nextPaymentClass;
	
	PaymentCalc(String label, Class<? extends JComponent> fieldClass, Class<? extends JComponent> nextPaymentClass)
	{
		this.label = label;
		this.paymentVarClass = fieldClass;
		this.nextPaymentClass = nextPaymentClass;
	}

	
	/**
	 * @return the label
	 */
	public String getLabel()
	{
		return label;
	}

	
	/**
	 * @return the paymentVarClass
	 */
	public Class<? extends JComponent> getPaymentVarClass()
	{
		return paymentVarClass;
	}

	public JComponent getPaymentVarField(CurrencyType currencyType, CurrencyTable currTable,
			char decimalChar, char commaChar)
	{

		try
		{
			Constructor<? extends JComponent> c = null;
			switch (this)
			{
				case FIXED_PAYMENT:
					c = this.paymentVarClass.getConstructor(CurrencyType.class, CurrencyTable.class,
																								char.class, char.class);
					return c.newInstance(currencyType, currTable, decimalChar, commaChar);
				case CLEARED_BALANCE:
				case CURRENT_BALANCE:
					c = this.paymentVarClass.getConstructor(String.class);
					return c.newInstance(Strings.BLANK);
				case PERCENTAGE_OF_CLEARED_BALANCE:
				case PERCENTAGE_OF_CURRENT_BALANCE:
					c = this.paymentVarClass.getConstructor(char.class);
					return c.newInstance(decimalChar);
			}
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}

		return null;
	}
	
	public JComponent getNextPaymentField(CurrencyType currencyType, CurrencyTable currTable,
			char decimalChar, char commaChar)
	{

		try
		{
			Constructor<? extends JComponent> c = null;
			switch (this)
			{
				case FIXED_PAYMENT: 
					c = this.nextPaymentClass.getConstructor(CurrencyType.class, CurrencyTable.class,
																								char.class, char.class);
					return c.newInstance(currencyType, currTable, decimalChar, commaChar);
				case CLEARED_BALANCE:
				case CURRENT_BALANCE:
					c = this.nextPaymentClass.getConstructor(String.class);
					return c.newInstance(Strings.BLANK);
				case PERCENTAGE_OF_CLEARED_BALANCE:
				case PERCENTAGE_OF_CURRENT_BALANCE:
					c = this.nextPaymentClass.getConstructor(CurrencyType.class, CurrencyTable.class,
															char.class, char.class);
					return c.newInstance(currencyType, currTable, decimalChar, commaChar);
			}
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}

		return null;
	}
	
	public static PaymentCalc getCalcMethod(String label)
	{
		for (PaymentCalc pc: values())
		{
			if (pc.label.equals(label))
			{
				return pc;
			}
		}
		return null;
	}
}

