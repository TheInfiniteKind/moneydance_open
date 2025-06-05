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

import com.infinitekind.moneydance.model.Budget;
import com.infinitekind.moneydance.model.BudgetItem;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Utilities;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;

public class BudgetItemBean extends DataBean {
	@ColumnName("BudgetName")
	@ColumnTitle("Budget Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String name;
	@ColumnName("BudgetItemId")
	@ColumnTitle("Budget Item ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String budgetItemId;
	@ColumnTitle("Amount")
	@ColumnName("Amount")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long amount;
	@ColumnName("CurrencyTypeID")
	@ColumnTitle("Currency ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currencyTypeID; // ok
	@ColumnName("CurrencyTypeName")
	@ColumnTitle("Currency Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currencyTypeName; // ok
	@ColumnName("AccountName")
	@ColumnTitle("Account Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String account;
	@ColumnName("IsIncome")
	@ColumnTitle("Is Income")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean isIncome;
	@ColumnName("IntervalType")
	@ColumnTitle("Interval Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String intervalType; // ok
	@ColumnName("IntervalStartDate")
	@ColumnTitle("Interval Start Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date start;
	@ColumnName("IntervalEndDate")
	@ColumnTitle("Interval End Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date end;

	/*
	 * Transient fields
	 */
	private Budget budget;
	private BudgetItem budgetItem;

	public BudgetItemBean() {
		super();
		tableName = "BudgetItem";
		screenTitle = "Budget Item";
		shortName = "budgi";
		parmsName = Constants.PARMFLDBUDGI;

	}

	public void setBean(Budget budget, BudgetItem budgetItem) {
		this.budget = budget;
		this.budgetItem = budgetItem;

	}

	@Override
	public void populateData() {
		name = setString(budget.getName());
		budgetItemId = budgetItem.getUUID();
		amount = setMoney(budgetItem.getAmount());
		currencyTypeID = setString(budgetItem.getCurrency().getIDString());
		currencyTypeName = setString(budgetItem.getCurrency() == null ? "" : budgetItem.getCurrency().getName());
		account = setString(budgetItem.getTransferAccount().getAccountName());
		isIncome = setBoolean(budgetItem.isIncome());
		intervalType = setString(Constants.intervaltypes.get(budgetItem.getInterval()));
		start = setDate(Utilities.getSQLDate(budgetItem.getIntervalStartDate()));
		end = setDate(Utilities.getSQLDate(budgetItem.getIntervalEndDate()));
	}
}
