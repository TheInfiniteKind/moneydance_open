package com.moneydance.modules.features.securitypriceload;

import java.io.Serializable;


public class ExchangeLine implements Serializable {
	/*
	 * Static and transient fields are not stored 
	 */
	private static final long serialVersionUID = 1L;
 /*
     * The following fields are stored
     */

	private String strExchange;
	private int iMultiplier;
	public ExchangeLine(String strExchangep, int iMultiplierp) {
		strExchange = strExchangep;
		iMultiplier = iMultiplierp;
	}
	public String getExchange() {
		return strExchange;
	}
	public int getMultiplier() {
		return iMultiplier;
	}
	public void setMultiplier(int iMultiplierp) {
		iMultiplier = iMultiplierp;
	}
	}
