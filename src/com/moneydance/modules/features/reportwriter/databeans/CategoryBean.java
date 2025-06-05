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

import com.infinitekind.moneydance.model.Account;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;

public class CategoryBean extends DataBean {
	@ColumnName("CategoryID")
	@ColumnTitle("Category ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String categoryId; // ok
	@ColumnName("CategoryName")
	@ColumnTitle("Category Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String categoryName; // ok
	@ColumnName("CategoryType")
	@ColumnTitle("Category Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String categoryType; // ok
	@ColumnName("CurrencyTypeID")
	@ColumnTitle("Currency ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currencyTypeID; // ok
	@ColumnName("CurrencyTypeName")
	@ColumnTitle("Currency Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currencyTypeName; // ok
	@ColumnName("FullName")
	@ColumnTitle("Long Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String fullName; // ok
	@ColumnName("TaxRelated")
	@ColumnTitle("Tax Related")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean taxRelated; // ok
	private Account category;

	public CategoryBean() {
		super();
		tableName = "Category";
		screenTitle = "Category";
		shortName = "catg";
		parmsName = Constants.PARMFLDCAT;
	}

	public void setCategory(Account category) {
		this.category = category;
	}

	@Override
	public void populateData() {
		categoryId = setString(category.getUUID());
		categoryName = setString(category.getAccountName());
		categoryType = setString(category.getAccountType().name());
		currencyTypeID = setString(category.getCurrencyType().getIDString());
		currencyTypeName = setString(category.getCurrencyType() == null ? "" : category.getCurrencyType().getName());
		fullName = setString(category.getFullAccountName());
		taxRelated = setBoolean(category.isTaxRelated());
	}

}
