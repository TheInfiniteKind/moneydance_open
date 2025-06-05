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

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.InvestTxnType;
import com.infinitekind.moneydance.model.ParentTxn;
import com.infinitekind.moneydance.model.SplitTxn;

public class GenerateTransaction {
	private char tranType;
	private long amount;
	private Account acct;
	private String desc;
	private String cheque;
	private String tType;
	InvestTxnType invType;
	private int tranDate;
	private String reference;
	private int index;
	private AbstractTxn txn;
	private Parameters2 params;


	public GenerateTransaction(char tranTypep,
			Account acctp,
			int tranDatep, 
			long amountp,
			String descp,
			String chequep,
			String tTypep, 
			String referencep,
			AbstractTxn txnp) {
		tranType = tranTypep;
		acct = acctp;
		tranDate = tranDatep;
		amount = amountp;
		desc = descp;
		cheque = chequep;
		tType = tTypep;
		reference = referencep;
		setInvType();
		index = -1;
		txn=txnp;
	}
	public GenerateTransaction(char tranTypep,
							   Account acctp,
							   int tranDatep,
							   long amountp,
							   String descp,
							   String chequep,
							   String tTypep,
							   String referencep,
							   AbstractTxn txnp,
							   Parameters2 params) {
		tranType = tranTypep;
		acct = acctp;
		tranDate = tranDatep;
		amount = amountp;
		desc = descp;
		cheque = chequep;
		tType = tTypep;
		reference = referencep;
		this.params=params;
		setInvType();
		index = -1;
		txn=txnp;
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

	public String getTType () {
		return tType;
	}
	public InvestTxnType getInvType () {
		return invType;
	}
	private void setInvType() {
			if (tType.equals("xfrtp_bank")) {
				invType = InvestTxnType.BANK;
				return;
			}

			if (tType.equals("xfrtp_dividend")) {
				invType = InvestTxnType.DIVIDEND;
				return;
			}
			if (tType.equals("xfrtp_miscincexp")) {
				if (amount < 0L) {
					invType = InvestTxnType.MISCEXP;
					return;
				}
				invType = InvestTxnType.MISCINC;
				return;
			}
			if (tType.equals("xfrtp_buysell")) {
				FieldLine line = params.matchType(reference);
				if (Constants.TRANSTYPES[line.getTranType()].equals(Constants.INVESTMENT_BUY))
					invType = InvestTxnType.BUY;
				else {
					invType = InvestTxnType.SELL;
				}
				return;
			}
			invType = InvestTxnType.BANK;
	}
	public String getRef () {
		return reference;
	}
	
	public void setIndex(int indexp) {
		index = indexp;
	}

	public AbstractTxn getTxn() {
		return txn;
	}

	public void setTxn(AbstractTxn txn) {
		this.txn = txn;
	}


	
}
