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
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;

public class BudgetBean extends DataBean {
	@ColumnName("BudgetName")
	@ColumnTitle("Budget Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String name;
	@ColumnName("BudgetPeriod")
	@ColumnTitle("Budget Period")
	@FieldType(BEANFIELDTYPE.STRING)
	public String period;
	@ColumnName("isNewStyle")
	@ColumnTitle("Is New Style")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean isNewStyle;
	@ColumnName("BudgetId")
	@ColumnTitle("Budget ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String budgetId;

	/*
	 * Transient fields
	 */
	private transient Budget budget;

	public BudgetBean() {
		super();
		tableName = "Budget";
		screenTitle = "Budget";
		shortName = "budg";
		parmsName = Constants.PARMFLDBUDG;
	}

	public void setBudget(Budget budget) {
		this.budget = budget;
	}

	@Override
	public void populateData() {
		name = setString(budget.getName());
		period = setString(budget.getPeriodType().toString());
		isNewStyle = setBoolean(budget.isNewStyle());
		budgetId = setString(budget.getUUID());
	}

}
