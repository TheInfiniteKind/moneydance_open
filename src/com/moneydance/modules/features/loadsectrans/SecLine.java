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
package com.moneydance.modules.features.loadsectrans;


import com.infinitekind.moneydance.model.Account;

public class SecLine {

	private boolean select;
	private int lineDate;
	private String lineType;
	private String desc;
	private String ticker;
	private String cleared;
	private double unit;
	private long lAmount;
	private Account acct;
	private boolean bValid;
	private boolean bIgnore;
	private boolean bProcessed;

	public SecLine(int lineDate,String lineType,String desc, String ticker,String strClearedp,long lAmount, Account acct,double unit) {
		
		select = false;
		this.lineDate = lineDate;
		bValid = true;
		bIgnore = false;
		this.unit =unit;
		if (ticker.equals("#N/A"))
			this.ticker = Constants.NOTICKER;
		else {
			this.ticker = ticker;
			if (acct == null)
				bValid = false;
		}
		cleared = strClearedp;
		this.desc = desc;
		this.lineType = lineType;
		this.lAmount = lAmount;
		this.acct = acct;
		setIgnore(false);
        setProcessed(false);

	}
	/*
	 * gets
	 * 
	 */
	public boolean getSelect() {
		return select;
	}

	public int getDate() {
		return lineDate;
	}

	public String getTranType() {
		return lineType;
	}

	public String getDescription() {
		return desc;
	}

	public String getTicker() {
		return ticker;
	}

	public String getCleared() {
		return cleared;
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

	public double getUnit() {
		return unit;
	}

	/*
	 * sets
	 */
	public void setSelect(boolean bSelectp) {
		select = bSelectp;
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
		cleared = strClearedp;
	}

	public void setUnit(double unit) {
		this.unit = unit;
	}
}
