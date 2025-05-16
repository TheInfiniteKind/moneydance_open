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

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Constants.QuoteSource;
import com.moneydance.modules.features.securityquoteload.ExtraFields;
import com.moneydance.modules.features.securityquoteload.HistoryPrice;

public class SecurityTableLine {
	/*
	 * Display fields
	 */
	private Boolean selected=false;
	private String ticker;
	private String exchange="";
	private String alternateTicker="";
	private String accountName="";
	private Integer  source=0;
	private Double lastPrice=0.0;
	private Integer priceDate=0;
	private Double newPrice=0.0;
	private Double quotedPrice=0.0;
	private Double percentChg=0.0;
	private Double amtChg=0.0;
	private Integer tradeDate=0;
	private String tradeCur="";
	private ExtraFields volume=null;
	private List<HistoryPrice> history=new ArrayList<HistoryPrice>();;
	/*
	 * working fields
	 */
	private Account account;
	private CurrencyType currency;
	private CurrencyType relativeCurrencyType;
	private Boolean differentCur=false;
	private CurrencyType baseCurrency;
	private Boolean inError=false;
	private Integer tickerStatus = 0;
	private String ftAlternate;
	private String yahooAlternate;
	private String alphaAlternate;

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
	public String getExchange() {
		return exchange;
	}
	public void setExchange(String exchange) {
		this.exchange = exchange;
	}
	
	public String getAlternateTicker() {
		return alternateTicker;
	}
	public void setAlternateTicker(String alternateTicker) {
		this.alternateTicker = alternateTicker;
		setAlternate(alternateTicker);
	}
	public String getAccountName() {
		return accountName;
	}
	public void setAccountName(String accountName) {
		this.accountName = accountName;
	}
	public Integer getSource() {
		return source;
	}
	public void setSource(Integer source) {
		this.source = source;
		alternateTicker="";
		if ((source == Constants.FTINDEX ||source==Constants.FTHISTINDEX)&& ftAlternate != null)
			alternateTicker=ftAlternate;
		if ((source == Constants.YAHOOINDEX ||source==Constants.YAHOOHISTINDEX)&& yahooAlternate != null)
				alternateTicker=yahooAlternate;
		if ((source == Constants.ALPHAINDEX)&& alphaAlternate !=null)
			alternateTicker = alphaAlternate;
			
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
	
	public Double getQuotedPrice() {
		return quotedPrice;
	}
	public void setQuotedPrice(Double quotedPrice) {
		this.quotedPrice = quotedPrice;
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
	public Integer getTradeDate() {
		return tradeDate;
	}
	public void setTradeDate(Integer tradeDate) {
		this.tradeDate = tradeDate;
	}
	public String getTradeCur() {
		return tradeCur;
	}
	public void setTradeCur(String tradeCur) {
		this.tradeCur = tradeCur;
	}
	public ExtraFields getVolume() {
		return volume;
	}
	public void setVolume(ExtraFields volume) {
		this.volume = volume;
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
	
	/*
	 * Working fields getters and setters
	 */
	public Account getAccount() {
		return account;
	}
	public void setAccount(Account acct) {
		this.account = acct;
	}
	
	public CurrencyType getCurrencyType() {
		return currency;
	}
	public void setCurrencyType(CurrencyType currency) {
		this.currency = currency;
	}
	public CurrencyType getRelativeCurrencyType() {
		return relativeCurrencyType;
	}
	public void setRelativeCurrencyType(CurrencyType relativeCurrencyType) {
		this.relativeCurrencyType = relativeCurrencyType;
	}
	public Boolean getDifferentCur() {
		return differentCur;
	}
	public void setDifferentCur(Boolean differentCur) {
		this.differentCur = differentCur;
	}
	public CurrencyType getBaseCurrency() {
		return baseCurrency;
	}
	public void setBaseCurrency(CurrencyType baseCurrency) {
		this.baseCurrency = baseCurrency;
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
	public String getAlphaAlterate() {
		return alphaAlternate;}

	public void setAlphaAlternate(String alphaAlternate){
		this.alphaAlternate = alphaAlternate;
	}
	public void setAlternate(String alternate) {
		QuoteSource sourceType = QuoteSource.findSource(source);
		switch (sourceType) {
		case FT:
		case FTHD:
			ftAlternate = alternate;
			break;
		case YAHOO:
		case YAHOOHD:
			yahooAlternate = alternate;
			break;
		case ALPHAVAN :
			alphaAlternate= alternate;
		}
	}


}
