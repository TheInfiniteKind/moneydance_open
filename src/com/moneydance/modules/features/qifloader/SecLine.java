/*
 *  Copyright (c) 2014, Michael Bray. All rights reserved.
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
 */ 
package com.moneydance.modules.features.qifloader;


import com.infinitekind.moneydance.model.Account;

public class SecLine {

	private boolean bSelect;
	private int iDate;
	private String strRef;
	private String strDesc;
	private String strTicker;
	private String strCleared;
	private long lAmount;
	private Account acct;
	private boolean bValid;
	private boolean bIgnore;
	private boolean bProcessed;

	public SecLine(int iDatep,String strRefp,String strDescp, String strTickerp,String strClearedp,long lAmountp, Account acctp) {
		
		bSelect = false;
		iDate = iDatep;
		bValid = true;
		bIgnore = false;
		if (strTickerp.equals("#N/A")) 
			strTicker = Constants.NOTICKER;
		else {
			strTicker = strTickerp;
			if (acctp == null)
				bValid = false;
		}
		strCleared = strClearedp;
		strDesc = strDescp;
		strRef = strRefp;
		lAmount = lAmountp;
		acct = acctp;
		setIgnore(false);
        setProcessed(false);

	}
	/*
	 * gets
	 * 
	 */
	public boolean getSelect() {
		return bSelect; 
	}

	public int getDate() {
		return iDate; 
	}

	public String getReference() {
		return strRef; 
	}

	public String getDescription() {
		return strDesc; 
	}

	public String getTicker() {
		return strTicker; 
	}

	public String getCleared() {
		return strCleared; 
	}

	public long getValue() {
		return lAmount; 
	}
	
	public Account getAccount() {
		return acct; 
	}
	
	public boolean getValid() {
		return bValid; 
	}
	
	public boolean getIgnore() {
		return bIgnore;
	}

	public boolean getProcessed() {
		return bProcessed;
	}

	/*
	 * sets
	 */
	public void setSelect(boolean bSelectp) {
		bSelect = bSelectp;
	}
	
	public void setIgnore(boolean bIgnorep) {
		bIgnore = bIgnorep;
	}

	public void setProcessed(boolean bProcessedp) {
		bProcessed = bProcessedp;
	}
	
	public void setValid(boolean bValidp) {
		bValid = bValidp; 
	}
	public void setCleared(String strClearedp) {
		strCleared = strClearedp; 
	}}
