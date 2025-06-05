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
import com.infinitekind.moneydance.model.AbstractTxn.ClearedStatus;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.Account.AccountType;
import com.infinitekind.moneydance.model.SplitTxn;
import com.infinitekind.moneydance.model.TransactionSet;
import com.infinitekind.moneydance.model.Txn;
import com.infinitekind.moneydance.model.TxnSearch;
import com.infinitekind.moneydance.model.TxnSet;
import com.infinitekind.tiksync.SyncRecord;
import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.TransactionBean;
import com.moneydance.modules.features.reportwriter.view.DataDataRow;
import com.moneydance.modules.features.reportwriter.view.DataParameter;

public class TransactionFactory implements TxnSearch {
	private DataDataRow dataParams;
	private List<String> accounts = null;
	private List<String> invAccounts = null;
	private List<String> securities = null;
	private List<String> categories = null;
	private List<String> tags = null;
	private SortedMap<String, DataParameter> map;
	private TransactionSet txns;
	private TxnSet selected;
	private Iterator<AbstractTxn> iter;
	private int fromDate;
	private int toDate;
	private boolean filterByDate = false;

	public TransactionFactory(DataDataRow dataParamsp, OutputFactory output) throws RWException {
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
		if (map.containsKey(Constants.PARMACCOUNTS))
			accounts = map.get(Constants.PARMACCOUNTS).getList();
		if (map.containsKey(Constants.PARMINVACCTS)) {
			invAccounts = map.get(Constants.PARMINVACCTS).getList();
			for (String acct : invAccounts) {
				Account tempAcct = Main.book.getAccountByUUID(acct);
				if (tempAcct != null && tempAcct.getAccountType() == AccountType.SECURITY) {
					if (securities == null)
						securities = new ArrayList<String>();
					securities.add(acct);
				}
			}
			if (securities != null) {
				for (String sec : securities)
					invAccounts.remove(sec);
			}
		}
		if (map.containsKey(Constants.PARMCATEGORIES))
			categories = map.get(Constants.PARMCATEGORIES).getList();
		if (map.containsKey(Constants.PARMTAGS))
			tags = map.get(Constants.PARMTAGS).getList();
		txns = Main.book.getTransactionSet();
		selected = txns.getTransactions(this);
		iter = selected.iterator();
		while (iter.hasNext()) {
			AbstractTxn parent = iter.next();
			for (int i = 0; i < parent.getOtherTxnCount(); i++) {
				TransactionBean bean = new TransactionBean();
				bean.setSelection(output.getSelection());
				bean.setTrans(parent, parent.getOtherTxn(i), i);
				bean.populateData();
				try {
					output.writeRecord(bean);
				} catch (RWException e) {
					throw e;
				}
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
		/*
		 * Only bank transactions are included. Transfers between investment accounts
		 * and other accounts are included
		 */
		if (txn instanceof SplitTxn)
			return false;
		if (txn.getTransferType() != AbstractTxn.TRANSFER_TYPE_BANK)
			return false;
		if (!testParent(txn))
			return false;
		/*
		 * Parent has passed selection, now need to check categories and transfer
		 * accounts
		 */
		boolean select = false;
		for (int i = 0; i < txn.getOtherTxnCount(); i++) {
			AbstractTxn splt = txn.getOtherTxn(i);
			if (splt.getAccount().getAccountType() != AccountType.INCOME
					&& splt.getAccount().getAccountType() != AccountType.EXPENSE) {
				if (testAccount(splt)) {
					select = true;
				}
				continue;
			}
			/*
			 * Split txn, account INCOME or EXPENSE
			 */
			if (map.containsKey(Constants.PARMSELCAT)) {
				if (categories == null) {
					/*
					 * No specific categories selected, need to test Account Type
					 */
					if (txn.getAccount().getAccountType() == AccountType.INCOME
							&& map.containsKey(Constants.PARMINCOME))
						select = true;
					if (txn.getAccount().getAccountType() == AccountType.EXPENSE
							&& map.containsKey(Constants.PARMEXPENSE))
						select = true;
				} else {
					/*
					 * specific categories selected test if matches
					 */
					if (categories.contains(txn.getAccount().getUUID()))
						select = true;
					;
				}
			} else
				select = true;
		}
		return select;
	}

	private boolean testParent(Txn txn) {
		if (!testAccount(txn))
			return false;
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
			// test 9 & 14
			if (!(txn.getCheckNumber() == null || txn.getCheckNumber().isEmpty())) {
				if (map.containsKey(Constants.PARMFROMCHEQUE)) {
					if (map.get(Constants.PARMFROMCHEQUE).getValue().compareTo(txn.getCheckNumber()) > 0)
						return false;
				}
				// test 11 & 15
				if (map.containsKey(Constants.PARMTOCHEQUE)) {
					if (map.get(Constants.PARMTOCHEQUE).getValue().compareTo(txn.getCheckNumber()) < 0)
						return false;
				}
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

	private boolean testAccount(Txn txn) {
		// test 3
		if (map.containsKey(Constants.PARMSELACCT)) {
			if (txn.getAccount().getAccountIsInactive() && !map.containsKey(Constants.PARMINACTIVE))
				return false;
			switch (txn.getAccount().getAccountType()) {
			case BANK:
				if (!map.containsKey(Constants.PARMBANK))
					return false;
				break;
			case ASSET:
				if (!map.containsKey(Constants.PARMASSET))
					return false;
				break;
			case CREDIT_CARD:
				if (!map.containsKey(Constants.PARMCREDIT))
					return false;
				break;
			case INVESTMENT:
				if (!map.containsKey(Constants.PARMINVESTMENT))
					return false;
				break;
			case LIABILITY:
				if (!map.containsKey(Constants.PARMLIABILITY))
					return false;
				break;
			case LOAN:
				if (!map.containsKey(Constants.PARMLOAN))
					return false;
				break;
			default:
				break;
			}
			if (accounts != null) {
				if (!accounts.contains(txn.getAccount().getUUID()))
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
