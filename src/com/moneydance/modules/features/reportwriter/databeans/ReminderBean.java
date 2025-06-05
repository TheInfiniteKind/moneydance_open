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

import java.util.List;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.ParentTxn;
import com.infinitekind.moneydance.model.Reminder;
import com.infinitekind.moneydance.model.SplitTxn;
import com.infinitekind.moneydance.model.Account.AccountType;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Utilities;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;

public class ReminderBean extends DataBean {
	@ColumnName("AutoCommitDays")
	@ColumnTitle("Auto Commit Days")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int autoCommitDays; // ok
	@ColumnName("Description")
	@ColumnTitle("Description")
	@FieldType(BEANFIELDTYPE.STRING)
	public String description; // ok
	@ColumnName("IntialDate")
	@ColumnTitle("Initial Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date initialDate; // ok
	@ColumnName("LastDate")
	@ColumnTitle("Last Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date lastDate; // ok
	@ColumnName("Memo")
	@ColumnTitle("Memo")
	@FieldType(BEANFIELDTYPE.STRING)
	public String memo; // ok
	@ColumnName("ReminderType")
	@ColumnTitle("Reminder Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String reminderType; // ok
	@ColumnName("RepeatDaily")
	@ColumnTitle("Repeat Daily")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int repeatDaily; // ok
	@ColumnName("RepeatMonthly")
	@ColumnTitle("Repeat Monthly")
	@FieldType(BEANFIELDTYPE.STRING)
	public String repeatMonthly; // ok
	@ColumnName("RepeatWeekly")
	@ColumnTitle("Repeat Weekly")
	@FieldType(BEANFIELDTYPE.STRING)
	public String repeatWeekly; // ok
	@ColumnName("RepeatYearly")
	@ColumnTitle("Repeat Yearly")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean repeatYearly; // ok
	@ColumnName("RepeatMonthlyMod")
	@ColumnTitle("Repeat Monthly Mod")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int repeatMonthlyMod; // ok
	@ColumnName("RepeatWeeklyMod")
	@ColumnTitle("Repeat WeeklyMod")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int repeatWeeklyMod; // ok
	@ColumnName("IsLoanReminder")
	@ColumnTitle("Loan Reminder")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean isLoanReminder; // ok
	@ColumnName("id")
	@ColumnTitle("ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String id; // ok
	@ColumnName("ParentTxnID")
	@ColumnTitle("Parent Txn ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String parTxnId;
	@ColumnName("TxnID")
	@ColumnTitle("Txn ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String txnId;
	@ColumnName("AccountName")
	@ColumnTitle("Account Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String account;
	@ColumnName("CheckNum")
	@ColumnTitle("Check Number")
	@FieldType(BEANFIELDTYPE.STRING)
	public String check;
	@ColumnName("DateEntered")
	@ColumnTitle("Date Entered")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date entered;
	@ColumnName("DatePosted")
	@ColumnTitle("Date Posted Online")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date datePosted;
	@ColumnName("TxnDescription")
	@ColumnTitle("Txn Description")
	@FieldType(BEANFIELDTYPE.STRING)
	public String txnDescription;
	@ColumnName("Status")
	@ColumnTitle("Status")
	@FieldType(BEANFIELDTYPE.STRING)
	public String status;
	@ColumnName("TaxDate")
	@ColumnTitle("Tax Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date tax;
	@ColumnTitle("Parent Value")
	@ColumnName("PrntValue")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long parentValue;
	@ColumnTitle("Split Value")
	@ColumnName("SpltValue")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long splitValue;
	@ColumnTitle("Foreign Amt")
	@ColumnName("ForAmt")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long forAmt;
	@ColumnName("AcctCurrency")
	@ColumnTitle("Acct Currency")
	@FieldType(BEANFIELDTYPE.STRING)
	public String acctCurrency;
	@ColumnName("ForCurrency")
	@ColumnTitle("For Currency")
	@FieldType(BEANFIELDTYPE.STRING)
	public String forCurrency;
	@ColumnTitle("Split Num")
	@ColumnName("SplitNum")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int spltNum;
	@ColumnName("TransferType")
	@ColumnTitle("Transfer Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String transfer;
	@ColumnName("ParentTags")
	@ColumnTitle("Parent Tags")
	@FieldType(BEANFIELDTYPE.STRING)
	public String tags;
	@ColumnName("SplitTags")
	@ColumnTitle("Split Tags")
	@FieldType(BEANFIELDTYPE.STRING)
	public String splitTags;
	@ColumnName("ParentMemo")
	@ColumnTitle("Parent Memo")
	@FieldType(BEANFIELDTYPE.STRING)
	public String parentMemo;
	@ColumnName("SplitMemo")
	@ColumnTitle("Split Memo")
	@FieldType(BEANFIELDTYPE.STRING)
	public String splitMemo;
	@ColumnName("Category")
	@ColumnTitle("Category")
	@FieldType(BEANFIELDTYPE.STRING)
	public String category;
	@ColumnTitle("Transfer Account")
	@ColumnName("TransAcct")
	@FieldType(BEANFIELDTYPE.STRING)
	public String transAcct;;
	@ColumnName("Attach")
	@ColumnTitle("Has Attachments")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean hasAttach;

	/*
	 * Transient fields
	 */
	private Reminder reminder;
	private ParentTxn parent;
	private SplitTxn split;
	private int splitIdx;

	public ReminderBean() {
		super();
		tableName = "Reminder";
		screenTitle = "Reminder";
		shortName = "rmdr";
		parmsName = Constants.PARMFLDREM;
	}

	public Reminder getReminder() {
		return reminder;
	}

	public void setReminder(Reminder reminder, ParentTxn parent, SplitTxn split, int splitIdx) {
		this.reminder = reminder;
		this.parent = parent;
		this.split = split;
		this.splitIdx = splitIdx;
	}

	@Override
	public void populateData() {
		autoCommitDays = setInt(reminder.getAutoCommitDays());
		description = setString(reminder.getDescription());
		initialDate = setDate(Utilities.getSQLDate(reminder.getInitialDateInt()));
		if (reminder.getLastDateInt() == 0)
			lastDate = setDate(Constants.MISSINGDATE);
		else
			lastDate = setDate(Utilities.getSQLDate(reminder.getLastDateInt()));
		memo = setString(reminder.getMemo());
		reminderType = setString(reminder.getReminderType().toString());
		repeatDaily = setInt(reminder.getRepeatDaily());
		int[] monthlyDays = reminder.getRepeatMonthly();
		if (monthlyDays != null && monthlyDays.length > 0) {
			String tempStr = "";
			for (int i = 0; i < monthlyDays.length; i++)
				tempStr += String.valueOf(monthlyDays[i]);
			repeatMonthly = setString(tempStr);
		} else
			repeatMonthly = "";
		repeatMonthlyMod = setInt(reminder.getRepeatMonthlyModifier());
		int[] weeklyDays = reminder.getRepeatWeeklyDays();
		if (weeklyDays != null && weeklyDays.length > 0) {
			String tempStr = "";
			for (int i = 0; i < weeklyDays.length; i++)
				tempStr += String.valueOf(weeklyDays[i]);
			repeatWeekly = setString(tempStr);
		} else
			repeatWeekly = "";
		repeatWeeklyMod = setInt(reminder.getRepeatWeeklyModifier());
		repeatYearly = setBoolean(reminder.getRepeatYearly());
		isLoanReminder = setBoolean(reminder.isLoanReminder());
		id = setString(reminder.getUUID());
		if (parent != null) {
			account = setString(parent.getAccount() == null ? "" : parent.getAccount().getAccountName());
			CurrencyType acctCur = parent.getAccount() == null ? Main.baseCurrency
					: parent.getAccount().getCurrencyType();
			parentValue = setMoney(parent.getValue());
			Account splitAcct = split.getAccount();
			if (splitAcct != null) {
				if (split.getAccount().getAccountType() == AccountType.EXPENSE
						|| split.getAccount().getAccountType() == AccountType.INCOME)
					category = setString(split.getAccount().getAccountName());
				else
					transAcct = setString(split.getAccount() == null ? "" : parent.getAccount().getAccountName());
				CurrencyType splitCur = split.getAccount().getCurrencyType();
				if (splitCur == null)
					splitCur = Main.baseCurrency;
				if (splitCur != Main.baseCurrency) {
					forAmt = setMoney(split.getValue());
					splitValue = setMoney(-((SplitTxn) split).getParentValue());
					forCurrency = setString(splitCur.getIDString());
				} else
					splitValue = setMoney(split.getValue());
			} else {
				category = "";
				splitValue = 0L;
			}
			spltNum = splitIdx;
			if (splitIdx == 0)
				parentValue = setMoney(parent.getValue());
			else
				parentValue = 0L;
			acctCurrency = setString(acctCur.getIDString());
			parentMemo = ((ParentTxn) parent).getMemo();
			splitMemo = ((SplitTxn) split).getDescription();
			parTxnId = parent.getUUID();
			txnId = split.getUUID();
			check = setString(parent.getCheckNumber());
			entered = setDate(Utilities.getSQLDate(parent.getDateInt()));
			datePosted = setDate(Utilities.getSQLDate(parent.getDatePostedOnline()));
			txnDescription = setString(parent.getDescription());
			status = setString(parent.getClearedStatus().toString());
			tax = setDate(Utilities.getSQLDate(parent.getTaxDateInt()));
			transfer = setString(parent.getTransferType());
			List<String> tagList = parent.getKeywords();
			String tagString = "";
			if (tagList != null && !tagList.isEmpty())
				for (String tag : tagList)
					tagString += tag + " ";
			tags = setString(tagString);
			tagList = split.getKeywords();
			tagString = "";
			if (tagList != null && !tagList.isEmpty())
				for (String tag : tagList)
					tagString += tag + " ";
			splitTags = setString(tagString);
			hasAttach = setBoolean(parent.hasAttachments());
		} else {
			parTxnId = Constants.MISSINGSTRING;
			txnId = Constants.MISSINGSTRING;
			account = Constants.MISSINGSTRING;
			check = Constants.MISSINGSTRING;
			entered = Constants.MISSINGDATE;
			datePosted = Constants.MISSINGDATE;
			txnDescription = Constants.MISSINGSTRING;
			status = Constants.MISSINGSTRING;
			tax = Constants.MISSINGDATE;
			parentValue = Constants.MISSINGLONG;
			splitValue = Constants.MISSINGLONG;
			forAmt = Constants.MISSINGLONG;
			acctCurrency = Constants.MISSINGSTRING;
			forCurrency = Constants.MISSINGSTRING;
			spltNum = Constants.MISSINGINT;
			transfer = Constants.MISSINGSTRING;
			tags = Constants.MISSINGSTRING;
			splitTags = Constants.MISSINGSTRING;
			parentMemo = Constants.MISSINGSTRING;
			splitMemo = Constants.MISSINGSTRING;
			category = Constants.MISSINGSTRING;
			transAcct = Constants.MISSINGSTRING;
			hasAttach = false;
		}
	}
}
