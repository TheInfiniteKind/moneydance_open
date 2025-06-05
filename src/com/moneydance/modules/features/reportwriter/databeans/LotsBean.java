/*
 * Copyright (c) 2021, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.reportwriter.databeans;

import java.sql.Date;

import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.InvestFields;
import com.infinitekind.moneydance.model.ParentTxn;
import com.infinitekind.moneydance.model.SplitTxn;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Utilities;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;

public class LotsBean extends DataBean {
	@ColumnName("ParTxnID")
	@ColumnTitle("Parent Txn ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String txnId;
	@ColumnName("AccountName")
	@ColumnTitle("Account Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String account;
	@ColumnName("SecurityName")
	@ColumnTitle("Security Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String securityName;
	@ColumnName("TxnType")
	@ColumnTitle("Txn Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String txnType;
	@ColumnName("TxnDate")
	@ColumnTitle("Txn Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public Date txnDate;
	@ColumnName("Shares")
	@ColumnTitle("Num Shares")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double shares;
	@ColumnName("Price")
	@ColumnTitle("Price")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double price;
	@ColumnName("LotTxnId")
	@ColumnTitle("Lot Txn ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String lotTxnId;
	@ColumnName("LotTxnType")
	@ColumnTitle("Lot Txn Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String lotTxnType;
	@ColumnName("LotDate")
	@ColumnTitle("Lot Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public Date lotDate;
	@ColumnName("LotPrice")
	@ColumnTitle("Lot Price")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double lotPrice;
	@ColumnName("LotSharesAvail")
	@ColumnTitle("Lot Shares Available")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double lotSharesAvail;
	@ColumnName("LotSharesAlloc")
	@ColumnTitle("Lot Shares Allocated")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double lotSharesAlloc;
	private ParentTxn parent;
	private SplitTxn lotTxn;
	private CurrencyType secCur;
	private long allocShares;
	private boolean firstrec;

	public LotsBean() {
		super();
		tableName = "Lots";
		screenTitle = "Lot";
		shortName = "lots";
		parmsName = Constants.PARMFLDLOTS;
	}

	public void setLot(ParentTxn parent, CurrencyType secCur, SplitTxn lotTxn, long allocShares, boolean firstrec) {
		this.parent = parent;
		this.secCur = secCur;
		this.lotTxn = lotTxn;
		this.allocShares = allocShares;
		this.firstrec = firstrec;
	}

	@Override
	public void populateData() {
		txnId = setString(parent.getUUID());
		InvestFields invest = new InvestFields();
		invest.setFieldStatus(parent);
		if (invest.hasShares && firstrec)
			shares = setDouble(secCur.getDoubleValue(invest.shares));
		else
			shares = Constants.MISSINGDOUBLE;
		if (invest.hasPrice && firstrec)
			price = setDouble(100 / Util.safeRate(invest.price));
		else
			price = Constants.MISSINGDOUBLE;
		account = setString(parent.getAccount() == null ? "" : parent.getAccount().getAccountName());
		securityName = setString(secCur == null ? Constants.MISSINGSTRING : secCur.getName());
		txnType = setString(parent.getInvestTxnType().name());
		txnDate = setDate(Utilities.getSQLDate(parent.getDateInt()));
		lotTxnId = setString(lotTxn.getUUID());
		lotTxnType = setString(((ParentTxn) (lotTxn.getOtherTxn(0))).getInvestTxnType().name());
		lotDate = setDate(Utilities.getSQLDate(lotTxn.getDateInt()));
		lotSharesAvail = setDouble(secCur.getDoubleValue(lotTxn.getValue()));
		lotPrice = setDouble(100 / Util.safeRate(lotTxn.getRate()));
		lotSharesAlloc = setDouble(secCur.getDoubleValue(allocShares));
	}

}
