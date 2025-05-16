/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */
package com.moneydance.modules.features.securityquoteload;


/**
 * Class to store the source from selected by the user.  It will be stored in the 
 * parameter file
 * 
 * @author Mike Bray
 *
 */
public class NewAccountLine{
	private String name;
	private int source;
	private Boolean currency;
	private String exchange;
	private String ftAlternate;
	private String yahooAlternate;
	private String alphaAlternate;
	/**
	 * Create class, uses the structure of the Ticker to determine if the account is a
	 * currency
	 * @param namep the Ticker of the account
	 * @param sourcep the Source selected by the user
	 */
	public NewAccountLine () {
		
	}
	/**
	 * Get the Source
	 * @return Source
	 */
	public int getSource() {
		return source;
	}
	/**
	 * Get the Ticker
	 * @return Ticker
	 */
	public String getName() {
		return name;
	}
	/**
	 * @return the exchange
	 */
	public String getExchange() {
		if (exchange !=null && exchange.isEmpty())
			return null;
		return exchange;
	}
	/**
	 * set the source 
	 * @param sourcep the source
	 */
	public void setSource (int sourcep) {
		source = sourcep;
	}
	/**
	 * Returns whether or not the account is a currency
	 * @return true/false
	 */
	public Boolean isCurrency() {
		if (currency==null)
			currency=false;
		return currency;
	}
	public void setName (String namep){
		name = namep;
	}
	public void setCurrency (boolean currencyp){
		currency = currencyp;
	}
	/**
	 * @param exchange the exchange to set
	 */
	public void setExchange(String exchange) {
		if (exchange != null && exchange.isEmpty())
			this.exchange = null;
		else
			this.exchange = exchange;
	}
	public String getFtAlternate() {
		return ftAlternate;
	}
	public void setFtAlternate(String ftAlternate) {
		this.ftAlternate = ftAlternate;
	}
	public String getYahooAlternate() {
		return yahooAlternate;
	}
	public void setYahooAlternate(String yahooAlternate) {
		this.yahooAlternate = yahooAlternate;
	}

	public String getAlphaAlternate() {
		return alphaAlternate;
	}

	public void setAlphaAlternate(String alphaAlternate) {
		this.alphaAlternate = alphaAlternate;
	}
}

