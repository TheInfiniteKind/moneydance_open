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
 * Mike Bray
 */
package com.moneydance.modules.features.securityquoteload;

public class SecurityPrice {
	private String ticker;
	private Double stockPrice;
	private Double highPrice;
	private Double lowPrice;
	private Long volume;
	private Boolean isCurrency;
	private Boolean isStock;
	private Boolean isETF;
	private String currencyID;
	private Integer tradeDate;
	private Boolean isCrypto;
	private String exchange;
	private String alternate;
	private String tradeCurrency;
	
	public SecurityPrice (String tickerp) {
		ticker = tickerp;
		stockPrice = 0.0;
		highPrice = 0.0;
		lowPrice = 0.0;
		volume = 0L;
		currencyID = "";
		isCrypto = false;
		if (ticker.startsWith(Constants.CURRENCYID)){
			isCurrency = true;
			currencyID = ticker.substring(3);
			if (ticker.contains("-"))
				isCrypto = true;
		}
		else
			isCurrency = false;
		
		
	}
	public String getTicker () {
		return ticker;
	}
	public Double getSecurityPrice () {
		return stockPrice;
	}
	public Double getHighPrice () {
		return highPrice;
	}
	public Double getLowPrice () {
		return lowPrice;
	}
	public Long getVolume () {
		return volume;
	}
	public String getCurrency () {
		return currencyID;
	}
	/**
	 * @return the tradeDate
	 */
	public Integer getTradeDate() {
		return tradeDate;
	}
	/**
	 * @return the exchange
	 */
	public String getExchange() {
		return exchange;
	}
	
	public String getAlternate() {
		return alternate;
	}
	public Boolean isCurrency () {
		return isCurrency;
	}
	public Boolean isStock () {
		return isStock;
	}
	public Boolean isETF () {
		return isETF;
	}
	public Boolean isCrypto() {
		return isCrypto;
	}
	public void setStock(Boolean isStockp){
		isStock = isStockp;
	}
	public void setETF(Boolean isETFp){
		isETF = isETFp;
	}
	public void setSecurityPrice (Double stockPricep) {
		stockPrice = stockPricep;
	}
	public void setHighPrice (Double highPricep) {
		highPrice = highPricep;
	}
	public void setLowPrice (Double lowPricep) {
		lowPrice = lowPricep;
	}
	public void setTicker (String tickerp){
		ticker = tickerp;
		if (ticker.startsWith(Constants.CURRENCYID)){
			isCurrency = true;
			currencyID = ticker.substring(3);
			if (ticker.contains("-"))
				isCrypto = true;
		}
	}
	public void setVolume (Long volumep) {
		volume = volumep;
	}
	
	/**
	 * @param exchange the exchange to set
	 */
	public void setExchange(String exchange) {
		this.exchange = exchange;
	}
	
	public void setAlternate(String alternate) {
		this.alternate = alternate;
	}
	public void setCurrency (String currencyIDp){
		currencyID = currencyIDp;
	}
	/**
	 * @param tradeDate the tradeDate to set
	 */
	public void setTradeDate(Integer tradeDate) {
		this.tradeDate = tradeDate;
	}
	public void setCrypto(Boolean isCryptop){
		isCrypto = isCryptop;
	}

	public String getTradeCurrency() {
		return tradeCurrency;
	}

	public void setTradeCurrency(String tradeCurrency) {
		this.tradeCurrency = tradeCurrency;
	}
}
