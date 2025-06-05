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
package  com.moneydance.modules.features.securityquoteload;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
/**
 * Stores details about the account.  If a currency or a security without any holdings
 * the Account will be null
 * @author Mike Bray
 *
 */
public class DummyAccount {
	private String accountName;
	private Account acct;
	private CurrencyType currency;
	private CurrencyType relativeCurrency;
	private Boolean differentCur;
	private CurrencyType baseCurrency;
	public  DummyAccount (){
		baseCurrency = Main.context.getCurrentAccountBook().getCurrencies().getBaseType();
	}
	/**
	 * Returns the Account Name
	 * @return Account Name
	 */
	public String getAccountName (){
		return accountName;
	}
	public void setDifferentCur(Boolean differentCur) {
		this.differentCur = differentCur;
	}
	/**
	 * Returns the CurrencyType record that can represent an actual currency
	 * or a security
	 * @return Currency Type
	 */
	public CurrencyType getCurrencyType() {
		return currency;
	}
	/**
	 * Returns the relative currency for a security.  Only set when the account is
	 * a security and it held in a currency not the same as the base currency. This is 
	 * set when the currency type is set
	 * @return Currency Type
	 */
	public CurrencyType getRelativeCurrencyType() {
		return relativeCurrency;
	}
	/**
	 * Returns whether or not the security is held in a different currency, set when the
	 * currency type is set
	 * @return true/false
	 */
	public Boolean getDifferentCur(){
		return differentCur;
	}
	/**
	 * Returns the Account associated with a security.  Will be null for a currency
	 * @return Account
	 */
	public Account getAccount(){
		return acct;
	}
	/**
	 * Set the Ticker
	 * @param accountNamep the Ticker
	 */
	public void setAccountName (String accountNamep){
		accountName = accountNamep;
	}
	/**
	 * set the currency type for the record.  If it has a relative currency (held in the parms
	 * of the CurrencyType.
	 * @param currencyp the CurrencyType record representing a security
	 */
	public void setCurrencyType (CurrencyType currencyp){
		currency = currencyp;
		relativeCurrency = getRelativeCurrency(currency);
		if (relativeCurrency == null || Main.context.getCurrentAccountBook().getCurrencies().getBaseType()== relativeCurrency)
			differentCur = false;
		else
			differentCur = true;
	}
	/**
	 * Set the Account
	 * @param acctp the Account to be set
	 */
	public void setAccount (Account acctp){
		acct = acctp;
	}
	/**
	 * gets the relative currency of a particular currency type
	 * @param curr the currency type to be searched
	 */
	private CurrencyType getRelativeCurrency(CurrencyType curr) {
	  String relCurrID = curr.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR);
	  return relCurrID == null ? baseCurrency : curr.getBook().getCurrencies().getCurrencyByIDString(relCurrID);
    }
}
