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

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.SortedMap;

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.InvestFields;
import com.infinitekind.moneydance.model.SplitTxn;
import com.infinitekind.moneydance.model.TransactionSet;
import com.infinitekind.moneydance.model.Txn;
import com.infinitekind.moneydance.model.TxnSearch;
import com.infinitekind.moneydance.model.TxnSet;
import com.infinitekind.moneydance.model.AbstractTxn.ClearedStatus;
import com.infinitekind.moneydance.model.Account.AccountType;
import com.infinitekind.tiksync.SyncRecord;
import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.InvTranBean;
import com.moneydance.modules.features.reportwriter.view.DataDataRow;
import com.moneydance.modules.features.reportwriter.view.DataParameter;

public class InvestTranFactory implements TxnSearch {
	private DataDataRow dataParams;
	private List<String> invAccounts = null;
	private List<String> acctSecurities = null;
	private List<String> categories = null;
	private List<String> tags = null;
	private List<String> transfers = null;
	private List<String> securities = null;
	private SortedMap<String, DataParameter> map;
	private TransactionSet txns;
	private TxnSet selected;
	private Iterator<AbstractTxn> iter;
	private int fromDate;
	private int toDate;
	private boolean filterByDate = false;

	public InvestTranFactory(DataDataRow dataParamsp, OutputFactory output) throws RWException {
		dataParams = dataParamsp;
		map = dataParams.getParameters();
		if (map.containsKey(Constants.PARMSELDATES)) {
			filterByDate = true;
			if (map.containsKey(Constants.PARMFROMDATE))
				fromDate = Integer.valueOf(map.get(Constants.PARMFROMDATE).getValue());
			else
				fromDate = DateUtil.getStrippedDateInt();
			if (map.containsKey(Constants.PARMTODATE) && !map.containsKey(Constants.PARMTODAY))
				toDate = Integer.valueOf(map.get(Constants.PARMTODATE).getValue());
			else
				toDate = DateUtil.getStrippedDateInt();
		}
		if (map.containsKey(Constants.PARMSELSECURITY) && map.containsKey(Constants.PARMSECURITY))
			securities = map.get(Constants.PARMSECURITY).getList();
		if (map.containsKey(Constants.PARMSELINVTRANS) && map.containsKey(Constants.PARMINVACCTS)) {
			invAccounts = map.get(Constants.PARMINVACCTS).getList();
			for (String acct : invAccounts) {
				Account tempAcct = Main.book.getAccountByUUID(acct);
				if (tempAcct != null && tempAcct.getAccountType() == AccountType.SECURITY) {
					if (acctSecurities == null)
						acctSecurities = new ArrayList<String>();
					acctSecurities.add(acct);
				}
			}
			if (acctSecurities != null) {
				for (String sec : acctSecurities)
					invAccounts.remove(sec);
			}
			if (acctSecurities != null && acctSecurities.isEmpty())
				acctSecurities = null;
			if (invAccounts != null && invAccounts.isEmpty())
				invAccounts = null;
		}
		if (map.containsKey(Constants.PARMCATEGORIES))
			categories = map.get(Constants.PARMCATEGORIES).getList();
		if (map.containsKey(Constants.PARMTAGS))
			tags = map.get(Constants.PARMTAGS).getList();
		if (map.containsKey(Constants.PARMSELINVTRANS) && map.containsKey(Constants.PARMTRANSFER))
			transfers = map.get(Constants.PARMTRANSFER).getList();
		txns = Main.book.getTransactionSet();
		selected = txns.getTransactions(this);
		iter = selected.iterator();
		while (iter.hasNext()) {
			InvTranBean bean = new InvTranBean();
			bean.setSelection(output.getSelection());
			bean.setTrans(iter.next());
			bean.populateData();
			try {
				output.writeRecord(bean);
			} catch (RWException e) {
				throw e;
			}
		}
	}

	@Override
	public boolean matches(Txn txn) {
		if (filterByDate) {
			if (txn.getDateInt() < fromDate)
				return false;
			if (txn.getDateInt() > toDate)
				return false;
		}
		if (txn instanceof SplitTxn)
			return false;
		InvestFields invest = new InvestFields();
		invest.setFieldStatus(txn);
		if (txn.getTransferType().equals(AbstractTxn.TRANSFER_TYPE_BANK)) {
			boolean select = false;
			if (txn.getAccount().getAccountType() == Account.AccountType.INVESTMENT)
				select = true;
			if (invest.hasXfrAcct && invest.xfrAcct.getAccountType() == Account.AccountType.INVESTMENT)
				select = true;
			if (!select)
				return false;
			select = false;
			if (invAccounts != null) {
				if (invAccounts.contains(txn.getAccount().getUUID()))
					select = true;
				if (invest.hasXfrAcct && invAccounts.contains(invest.xfrAcct.getUUID()))
					select = true;
			} else
				select = true;
			if (!select)
				return false;
		} else {
			if (invAccounts != null && !invAccounts.contains(txn.getAccount().getUUID()))
				return false;
		}
		if (transfers != null)
			if (!transfers.contains(invest.txnType.name()))
				return false;
		if (invest.hasSecurity) {
			if (acctSecurities != null && !acctSecurities.contains(invest.security.getUUID()))
				return false;
			if (securities != null && !securities.contains(invest.security.getCurrencyType().getUUID()))
				return false;
		}
		if (invest.hasCategory) {
			if (map.containsKey(Constants.PARMSELCAT)) {
				if (categories == null) {
					/*
					 * No specific categories selected, need to test Account Type
					 */
					if (invest.category.getAccountType() == AccountType.INCOME
							&& !map.containsKey(Constants.PARMINCOME))
						return false;
					if (invest.category.getAccountType() == AccountType.EXPENSE
							&& !map.containsKey(Constants.PARMEXPENSE))
						return false;
				} else {
					/*
					 * specific categories selected test if matches
					 */
					if (!categories.contains(invest.category.getUUID()))
						return false;
				}
			}
		}
		/*
		 * Parent TXN test filters
		 */
		return testParent(txn);
	}

	private boolean testParent(Txn txn) {
		if (map.containsKey(Constants.PARMSELTRANS)) {
			// test 6/7
			if (map.containsKey(Constants.PARMCLEARED) || map.containsKey(Constants.PARMRECON)
					|| map.containsKey(Constants.PARMUNRECON)) {
				if (txn.getClearedStatus() == ClearedStatus.CLEARED && !map.containsKey(Constants.PARMCLEARED))
					return false;
				if (txn.getClearedStatus() == ClearedStatus.RECONCILING && !map.containsKey(Constants.PARMRECON))
					return false;
				if (txn.getClearedStatus() == ClearedStatus.UNRECONCILED && !map.containsKey(Constants.PARMUNRECON))
					return false;
			}
			// test 16
			if (tags != null) {
				SyncRecord sync = ((AbstractTxn) txn).getTags();
				Set<String> setKeys = sync.keySet();
				String[] keys = setKeys.toArray(new String[setKeys.size()]);
				boolean found = false;
				for (String keyitem : keys) {
					if (tags.contains(keyitem))
						found = true;
				}
				if (!found)
					return false;
			}
		}
		return true;
	}

	@Override
	public boolean matchesAll() {
		// TODO Auto-generated method stub
		return false;
	}
}
