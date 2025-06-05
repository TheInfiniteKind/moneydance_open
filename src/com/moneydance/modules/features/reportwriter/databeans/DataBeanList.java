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

import java.util.ArrayList;

public class DataBeanList {
	private ArrayList<AccountBean> accountList = new ArrayList<>();
	private ArrayList<AccountTypeBean> accountTypeList = new ArrayList<>();
	private ArrayList<BudgetBean> budgetList = new ArrayList<>();
	private ArrayList<AddressBean> addressList = new ArrayList<>();
	private ArrayList<CurrencyBean> currencyList = new ArrayList<>();
	private ArrayList<TransactionBean> transactionList = new ArrayList<>();

	public ArrayList<AccountBean> getAccountBeanList() {
		return accountList;
	}

	public ArrayList<AccountTypeBean> getAccountTypeBeanList() {
		return accountTypeList;
	}

	public ArrayList<BudgetBean> getBudgetBeanList() {
		return budgetList;
	}

	public ArrayList<AddressBean> getAddressBeanList() {
		return addressList;
	}

	public ArrayList<CurrencyBean> getCurrencyBeanList() {
		return currencyList;
	}

	public ArrayList<TransactionBean> getTransactionBeanList() {
		return transactionList;
	}

	public void add(DataBean bean) {
		if (bean instanceof AccountBean)
			accountList.add((AccountBean) bean);
		if (bean instanceof AccountTypeBean)
			accountTypeList.add((AccountTypeBean) bean);
		if (bean instanceof AddressBean)
			addressList.add((AddressBean) bean);
		if (bean instanceof CurrencyBean)
			currencyList.add((CurrencyBean) bean);
		if (bean instanceof BudgetBean)
			budgetList.add((BudgetBean) bean);
		if (bean instanceof TransactionBean)
			transactionList.add((TransactionBean) bean);
	}

	public boolean remove(DataBean bean) {
		if (bean instanceof AccountBean)
			return accountList.add((AccountBean) bean);
		if (bean instanceof AccountTypeBean)
			return accountTypeList.add((AccountTypeBean) bean);
		if (bean instanceof AddressBean)
			return addressList.add((AddressBean) bean);
		if (bean instanceof CurrencyBean)
			return currencyList.add((CurrencyBean) bean);
		if (bean instanceof BudgetBean)
			return budgetList.add((BudgetBean) bean);
		if (bean instanceof TransactionBean)
			return transactionList.add((TransactionBean) bean);
		return false;
	}

}
