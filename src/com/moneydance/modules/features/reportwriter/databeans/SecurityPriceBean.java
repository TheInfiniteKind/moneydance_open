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

import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Utilities;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;
import com.moneydance.apps.md.controller.Util;

public class SecurityPriceBean extends DataBean {
	@ColumnName("SecurityId")
	@ColumnTitle("Security ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String securityId;
	@ColumnName("Ticker")
	@ColumnTitle("Ticker")
	@FieldType(BEANFIELDTYPE.STRING)
	public String ticker;
	@ColumnName("Name")
	@ColumnTitle("Security Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String secName;
	@ColumnName("Currency")
	@ColumnTitle("Currency")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currency;
	@ColumnName("CurrencyId")
	@ColumnTitle("Currency ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currencyId;
	@ColumnName("Prefix")
	@ColumnTitle("Value Prefix")
	@FieldType(BEANFIELDTYPE.STRING)
	public String prefix;
	@ColumnName("Suffix")
	@ColumnTitle("Value Suffix")
	@FieldType(BEANFIELDTYPE.STRING)
	public String suffix;
	@ColumnName("Date")
	@ColumnTitle("Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date dateInt;
	@ColumnName("DailyHigh")
	@ColumnTitle("Daily High")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double dailyHigh;
	@ColumnName("DailyLow")
	@ColumnTitle("Daily Low")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double dailyLow;
	@ColumnName("Rate")
	@ColumnTitle("Rate")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double rate;
	@ColumnName("DailyVolume")
	@ColumnTitle("Daily Volume")
	@FieldType(BEANFIELDTYPE.LONG)
	public long dailyVolume;
	private CurrencyType security;
	private CurrencySnapshot snapshot;

	public SecurityPriceBean() {
		super();
		tableName = "SecurityPrice";
		screenTitle = "Security Price";
		shortName = "secp";
		parmsName = Constants.PARMFLDSECP;
	}

	public void setBean(CurrencyType security, CurrencySnapshot snapshot) {
		this.security = security;
		this.snapshot = snapshot;
	}

	@Override
	public void populateData() {
		securityId = setString(security.getIDString());
		ticker = setString(security.getTickerSymbol());
		secName = setString(security.getName());
		prefix = setString(security.getPrefix());
		suffix = setString(security.getSuffix());
		CurrencyType relative = security.getRelativeCurrency() == null ? Main.baseCurrency
				: security.getRelativeCurrency();
		currency = setString(relative.getName());
		currencyId = setString(relative.getIDString());
		dateInt = setDate(Utilities.getSQLDate(snapshot.getDateInt()));
		dailyHigh = setDouble(1 / Util.safeRate(snapshot.getDailyHigh()));
		dailyLow = setDouble(1 / Util.safeRate(snapshot.getDailyLow()));
		rate = setDouble(1 / Util.safeRate(snapshot.getRate()));
		dailyVolume = setLong(snapshot.getDailyVolume());

	}

}
