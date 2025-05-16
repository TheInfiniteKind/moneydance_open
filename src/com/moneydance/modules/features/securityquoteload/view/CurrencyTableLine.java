/*
 * Copyright (c) 2023, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload.view;

import java.util.ArrayList;
import java.util.List;

import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.modules.features.securityquoteload.HistoryPrice;

public class CurrencyTableLine {
	private Boolean selected=false;
	private String ticker="";
	private String currencyName="";
	private Integer source=0;
	private Double lastPrice=0.0;
	private Integer priceDate=0;
	private Double newPrice=0.0;
	private Double percentChg=0.0;
	private Double amtChg=0.0;
	private Integer tradeDate=0;
	private List<HistoryPrice> history=null;
	/*
	 * working fields
	 */
	private CurrencyType currencyType;
	private Boolean inError=false;
	private Integer tickerStatus = 0;

	
	public CurrencyTableLine (String ticker, CurrencyType currencyType) {
		this.ticker = ticker;
		this.currencyType = currencyType;
	}

	/*
	 * Display fields getters and setters
	 */
	public Boolean getSelected() {
		return selected;
	}
	public void setSelected(Boolean selected) {
		this.selected = selected;
	}
	public String getTicker() {
		return ticker;
	}
	public void setTicker(String ticker) {
		this.ticker = ticker;
	}
	public String getCurrencyName() {
		return currencyName;
	}
	public void setCurrencyName(String currencyName) {
		this.currencyName = currencyName;
	}
	public Integer getSource() {
		return source;
	}
	public void setSource(Integer source) {
		this.source = source;
	}
	public Double getLastPrice() {
		return lastPrice;
	}
	public void setLastPrice(Double lastPrice) {
		this.lastPrice = lastPrice;
	}
	public Integer getPriceDate() {
		return priceDate;
	}
	public void setPriceDate(Integer priceDate) {
		this.priceDate = priceDate;
	}
	public Double getNewPrice() {
		return newPrice;
	}
	public void setNewPrice(Double newPrice) {
		this.newPrice = newPrice;
	}
	public Double getPercentChg() {
		return percentChg;
	}
	public void setPercentChg(Double percentChg) {
		this.percentChg = percentChg;
	}
	public Double getAmtChg() {
		return amtChg;
	}
	public void setAmtChg(Double amtChg) {
		this.amtChg = amtChg;
	}
	public List<HistoryPrice> getHistory() {
		return history;
	}
	public void setHistory(List<HistoryPrice> history) {
		this.history = history;
	}
	public void clearHistory() {
		history = new ArrayList<HistoryPrice>();
	}	
	public Integer getTradeDate() {
		return tradeDate;
	}

	public void setTradeDate(Integer tradeDate) {
		this.tradeDate = tradeDate;
	}

	/*
	 * Working fields getters and setters
	 */
	public CurrencyType getCurrencyType() {
		return currencyType;
	}
	public void setCurrencyType(CurrencyType currencyType) {
		this.currencyType = currencyType;
	}

	public Boolean getInError() {
		return inError;
	}

	public void setInError(Boolean inError) {
		this.inError = inError;
	}

	public Integer getTickerStatus() {
		return tickerStatus;
	}

	public void setTickerStatus(Integer tickerStatus) {
		this.tickerStatus = tickerStatus;
	}
	
}
