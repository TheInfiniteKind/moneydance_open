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

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.CurrencyUtil;
import com.infinitekind.moneydance.model.ParentTxn;
import com.infinitekind.moneydance.model.InvestFields;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Utilities;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;

public class InvTranBean extends DataBean {
	@ColumnName("TxnID")
	@ColumnTitle("Txn ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String txnId;
	@ColumnName("AccountName")
	@ColumnTitle("Account Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String account;
	@ColumnName("DateEntered")
	@ColumnTitle("Date Entered")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date entered;
	@ColumnName("DatePosted")
	@ColumnTitle("Date Posted Online")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date datePosted;
	@ColumnName("TaxDate")
	@ColumnTitle("Tax Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date tax;
	@ColumnName("Curr")
	@ColumnTitle("Currency")
	@FieldType(BEANFIELDTYPE.STRING)
	public String curr;
	@ColumnName("Security")
	@ColumnTitle("Security")
	@FieldType(BEANFIELDTYPE.STRING)
	public String security;
	@ColumnName("Ticker")
	@ColumnTitle("Ticker")
	@FieldType(BEANFIELDTYPE.STRING)
	public String ticker;
	@ColumnName("TransferType")
	@ColumnTitle("Transfer Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String transfer;
	@ColumnName("InvestType")
	@ColumnTitle("Investment Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String invType;
	@ColumnName("Description")
	@ColumnTitle("Description")
	@FieldType(BEANFIELDTYPE.STRING)
	public String description;
	@ColumnName("Memo")
	@ColumnTitle("Memo")
	@FieldType(BEANFIELDTYPE.STRING)
	public String memo;
	@ColumnName("Status")
	@ColumnTitle("Status")
	@FieldType(BEANFIELDTYPE.STRING)
	public String status;
	@ColumnTitle("Transfer Account")
	@ColumnName("TransAcct")
	@FieldType(BEANFIELDTYPE.STRING)
	public String transAcct;
	@ColumnName("Category")
	@ColumnTitle("Category")
	@FieldType(BEANFIELDTYPE.STRING)
	public String category;
	@ColumnName("NumShares")
	@ColumnTitle("Number Shares")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double numShares;
	@ColumnTitle("Price")
	@ColumnName("Price")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double price;
	@ColumnTitle("Amount")
	@ColumnName("Amount")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long amount;
	@ColumnTitle("Parent Value")
	@ColumnName("ParentValue")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long prntValue;
	@ColumnTitle("Split Value")
	@ColumnName("SplitValue")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long spltValue;
	@ColumnTitle("Fee")
	@ColumnName("Fee")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long fee;
	@ColumnName("FeeAcct")
	@ColumnTitle("Fee Account")
	@FieldType(BEANFIELDTYPE.STRING)
	public String feeAcct;
	@ColumnName("Attach")
	@ColumnTitle("Has Attachments")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean hasAttach;

	AbstractTxn trans;

	public InvTranBean() {
		super();
		tableName = "InvTrans";
		screenTitle = "Investment Transaction";
		shortName = "invtrans";
		parmsName = Constants.PARMFLDINVTRAN;

	}

	public AbstractTxn getTrans() {
		return trans;
	}

	public void setTrans(AbstractTxn trans) {
		this.trans = trans;
	}

	@Override
	public void populateData() {
		InvestFields invest = new InvestFields();
		invest.setFieldStatus(trans);
		account = setString(trans.getAccount() == null ? "" : trans.getAccount().getAccountName());
		curr = setString(trans.getAccount() == null ? "" : trans.getAccount().getCurrencyType().getIDString());
		if (invest.hasCategory)
			category = invest.category.getAccountName();
		else
			category = "";
		amount=setMoney(invest.amount);
		prntValue = setMoney(trans.getValue());
		if (trans.getTransferType().equals(AbstractTxn.TRANSFER_TYPE_BANK))
			spltValue = -prntValue;
		invType = setString(invest.txnType.name());
		memo = ((ParentTxn) trans).getMemo();
		if (invest.hasXfrAcct)
			transAcct = setString(invest.xfrAcct == null ? "" : invest.xfrAcct.getAccountName());
		else
			transAcct = "";
		if (invest.hasFee) {
			fee = setMoney(invest.fee);
			feeAcct = setString(invest.feeAcct == null ? "" : invest.feeAcct.getAccountName());
		} else {
			fee = 0L;
			feeAcct = "";
		}
		if (invest.hasPrice)
			price = setDouble(1.0/CurrencyUtil.getUserRate(invest.curr,invest.secCurr,invest.price));
//			price = setDouble(100 / Util.safeRate(invest.price));
		else
			price = 0.0;
		if (invest.hasSecurity) {
			security = setString(invest.security == null ? "" : invest.security.getAccountName());
			ticker = setString(invest.secCurr == null ? "" : invest.secCurr.getTickerSymbol());
		} else {
			security = "";
			ticker = "";
		}
		if (invest.hasShares)
			numShares = setDouble(invest.secCurr.getDoubleValue(invest.shares));
		else
			numShares = 0.0D;
		txnId = trans.getUUID();
		entered = setDate(Utilities.getSQLDate(trans.getDateInt()));
		datePosted = setDate(Utilities.getSQLDate(trans.getDatePostedOnline()));
		description = setString(trans.getDescription());
		status = setString(trans.getClearedStatus().toString());
		tax = setDate(Utilities.getSQLDate(trans.getTaxDateInt()));
		transfer = setString(trans.getTransferType());
		hasAttach = setBoolean(trans.hasAttachments());

	}
}
