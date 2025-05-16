/*
 *   Copyright (c) 2020, Michael Bray.  All rights reserved.
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

public class ExchangeLine {
	private String exchange;
	private String name;
	private String currency;
	private String ftPrefix;
	private String ftSuffix;
	private String yahooPrefix;
	private String yahooSuffix;
	private String alphaPrefix;
	private String alphaSuffix;
	private Double multiplier;
	public ExchangeLine () {
		
	}
	/**
	 * @return the exchange
	 */
	public String getExchange() {
		if (exchange == null)
			return "unknown";
		else
			return exchange;
	}
	/**
	 * @return the name
	 */
	public String getName() {
		if (name == null)
			return "unknown";
		else
			return name;
	}

	public String getCurrency() {
		return currency;
	}

	public void setCurrency(String currency) {
		this.currency = currency;
	}

	/**
	 * @return the ftPrefix
	 */
	public String getFtPrefix() {
		if (ftPrefix == null)
			return "unknown";
		else
			return ftPrefix;
	}
	/**
	 * @return the ftSuffix
	 */
	public String getFtSuffix() {
		if (ftSuffix == null)
			return "unknown";
		else
			return ftSuffix;
	}
	/**
	 * @return the yahooPrefix
	 */
	public String getYahooPrefix() {
		if (yahooPrefix == null)
			return "unknown";
		else
			return yahooPrefix;
	}
	/**
	 * @return the yahooSuffix
	 */
	public String getYahooSuffix() {
		if (yahooSuffix == null)
			return "unknown";
		else
			return yahooSuffix;
	}
	/**
	 * @return the multiplier
	 */
	public Double getMultiplier() {
		if (exchange == null)
			return 0.0;
		else
			return multiplier;
	}

	/**
	 * @param exchange the exchange to set
	 */
	public void setExchange(String exchange) {
		this.exchange = exchange;
	}
	/**
	 * @param name the name to set
	 */
	public void setName(String name) {
		this.name = name;
	}
	/**
	 * @param ftPrefix the ftPrefix to set
	 */
	public void setFtPrefix(String ftPrefix) {
		this.ftPrefix = ftPrefix;
	}
	/**
	 * @param ftSuffix the ftSuffix to set
	 */
	public void setFtSuffix(String ftSuffix) {
		this.ftSuffix = ftSuffix;
	}
	/**
	 * @param yahooPrefix the yahooPrefix to set
	 */
	public void setYahooPrefix(String yahooPrefix) {
		this.yahooPrefix = yahooPrefix;
	}
	/**
	 * @param yahooSuffix the yahooSuffix to set
	 */
	public void setYahooSuffix(String yahooSuffix) {
		this.yahooSuffix = yahooSuffix;
	}

	public String getAlphaPrefix() {
		return alphaPrefix;
	}

	public void setAlphaPrefix(String alphaPrefix) {
		this.alphaPrefix = alphaPrefix;
	}

	public String getAlphaSuffix() {
		return alphaSuffix;
	}

	public void setAlphaSuffix(String alphaSuffix) {
		this.alphaSuffix = alphaSuffix;
	}

	/**
	 * @param multiplier the multiplier to set
	 */
	public void setMultiplier(Double multiplier) {
		this.multiplier = multiplier;
	}
}
