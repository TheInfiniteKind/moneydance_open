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
package com.moneydance.modules.features.reportwriter.factory;

import java.util.List;
import java.util.SortedMap;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.Account.AccountType;
import com.infinitekind.moneydance.model.AccountUtil;
import com.infinitekind.moneydance.model.AcctFilter;
import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.AccountBean;
import com.moneydance.modules.features.reportwriter.view.DataDataRow;
import com.moneydance.modules.features.reportwriter.view.DataParameter;

public class AccountFactory extends AcctFilter {

	private DataDataRow dataParams;
	private List<Account> selectedAccts;
	private List<String> accounts = null;
	private SortedMap<String, DataParameter> map;
	private Boolean filterByAcct = false;
	private int toDate;
	private boolean filterByDate = false;

	public AccountFactory(DataDataRow dataParamsp, OutputFactory output) throws RWException {
		dataParams = dataParamsp;
		map = dataParams.getParameters();
		if (map.containsKey(Constants.PARMSELDATES)) {
			filterByDate = true;
			if (map.containsKey(Constants.PARMTODATE) && !map.containsKey(Constants.PARMTODAY))
				toDate = Integer.valueOf(map.get(Constants.PARMTODATE).getValue());
			else
				toDate = DateUtil.getStrippedDateInt();
		}
		filterByAcct = map.containsKey(Constants.PARMSELACCT);
		if (map.containsKey(Constants.PARMACCOUNTS))
			accounts = map.get(Constants.PARMACCOUNTS).getList();
		selectedAccts = AccountUtil.allMatchesForSearch(Main.book, this);
		for (Account acct : selectedAccts) {
			AccountBean bean = new AccountBean();
			bean.setSelection(output.getSelection());
			bean.setAccount(acct);
			bean.populateData();
			try {
				output.writeRecord(bean);
			} catch (RWException e) {
				throw e;
			}
			if (acct.getAccountType() == AccountType.INVESTMENT && output.getSelection().getAcctSec()) {
				for (int i = 0; i < acct.getSubAccountCount(); i++) {
					Account subAcct = acct.getSubAccount(i);
					if (subAcct.getAccountType() == AccountType.SECURITY) {
						bean.setSubAccount(acct, subAcct);
						bean.populateData();
						try {
							output.writeRecord(bean);
						} catch (RWException e) {
							throw e;
						}
					}
				}

			}
		}
	}

	@Override
	public boolean matches(Account paramAccount) {
		if (filterByDate && paramAccount.getCreationDateInt() > toDate)
			return false;
		if (paramAccount.getAccountIsInactive() && !map.containsKey(Constants.PARMINACTIVE))
			return false;
		if (!filterByAcct) {
			switch (paramAccount.getAccountType()) {
			case ASSET:
			case BANK:
			case CREDIT_CARD:
			case INVESTMENT:
			case LIABILITY:
			case LOAN:
				return true;
			default:
				return false;

			}
		}
		if (accounts != null) {
			if (accounts.contains(paramAccount.getUUID()))
				return true;
			return false;
		}
		switch (paramAccount.getAccountType()) {
		case ASSET:
			if (map.containsKey(Constants.PARMASSET))
				return true;
			return false;
		case BANK:
			if (map.containsKey(Constants.PARMBANK))
				return true;
			return false;
		case CREDIT_CARD:
			if (map.containsKey(Constants.PARMCREDIT))
				return true;
			return false;
		case EXPENSE:
			return false;
		case INCOME:
			return false;
		case INVESTMENT:
			if (map.containsKey(Constants.PARMINVESTMENT))
				return true;
			return false;
		case LIABILITY:
			if (map.containsKey(Constants.PARMLIABILITY))
				return true;
			return false;
		case LOAN:
			if (map.containsKey(Constants.PARMLOAN))
				return true;
			return false;
		case ROOT:
			return false;
		case SECURITY:
			return false;
		default:
			break;
		}
		return false;
	}

	@Override
	public String format(Account paramAccount) {
		return paramAccount.getUUID();
	}
}
