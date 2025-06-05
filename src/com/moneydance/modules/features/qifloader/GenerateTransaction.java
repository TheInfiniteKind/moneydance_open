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
import com.infinitekind.moneydance.model.InvestTxnType;

public class GenerateTransaction {
	private char tranType;
	private long amount;
	private Account acct;
	private String desc;
	private String cheque;
	private byte status;
	InvestTxnType invType;
	private int tranDate;
	private String reference;
	private int index;
	

	public GenerateTransaction(char tranTypep,Account acctp,
			int tranDatep, long amountp,String descp,String chequep,
			byte statusp, String referencep) {
		tranType = tranTypep;
		acct = acctp;
		tranDate = tranDatep;
		amount = amountp;
		desc = descp;
		cheque = chequep;
		status = statusp;
		reference = referencep;
		index = -1;
	}
	
	public int getIndex() {
		return index;
	}
	public char getType() {
		return tranType;
	}
	
	public long getAmount() {
		return amount;
	}
	
	public Account getAccount() {
		return acct;
	}
	
	public int getDate() {
		return tranDate;
	}
	
	public String getDesc() {
		return desc;
	}
	
	public String getCheque () {
		return cheque;
	}

	public byte getStatus () {
		return status;
	}
	public InvestTxnType getInvType () {
		return invType;
	}

	public String getRef () {
		return reference;
	}
	
	public void setIndex(int indexp) {
		index = indexp;
	}
}
