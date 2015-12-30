/*
 * TransactionsUtil.java
 * 
 * Created on Oct 6, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */
package com.moneydance.modules.features.debtinsights;

import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeSet;

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.TransactionSet;
import com.infinitekind.moneydance.model.TxnSet;


public class TransactionsUtil
{
	private static Map<Account, TransactionsUtil> instanceMap = new HashMap<Account, TransactionsUtil>();
	
	private TransactionSet ts = null;
	private TreeSet<AbstractTxn> txns = new TreeSet<AbstractTxn>(new TxnDateComparator());
	private TreeSet<AbstractTxn> cleared = new TreeSet<AbstractTxn>(new TxnDateComparator());
	private TreeSet<AbstractTxn> reverseCleared = new TreeSet<AbstractTxn>(Collections.reverseOrder(new TxnDateComparator()));
	private TreeSet<AbstractTxn> uncleared = new TreeSet<AbstractTxn>(new TxnDateComparator());
	
	private TransactionsUtil(Account acct)
	{
		this.ts = acct.getBook().getTransactionSet();

		TxnSet transactions = this.ts.getTransactionsForAccount(acct);
		txns.clear();
		txns.addAll(Arrays.asList(transactions.toArray()));
		for (AbstractTxn txn : txns)
		{
			if (txn.getStatus() == AbstractTxn.STATUS_CLEARED) 
			{
				cleared.add(txn);
				reverseCleared.add(txn);
			}
			else
				uncleared.add(txn);
		}

	}
	
	public static TransactionsUtil getInstance(Account acct)
	{
		TransactionsUtil instance = instanceMap.get(acct);
		if (instance == null)
		{
			instance = new TransactionsUtil(acct);
		}
		return instance;
	}
	
	public AbstractTxn getLastClearedTransaction()
	{
		return cleared.last();
	}
	
	public AbstractTxn getFirstPostClearedCredit()
	{
		for (AbstractTxn txn : uncleared)
		{
			if (txn.getValue() > 0) return txn;
		}
		return null;		
	}
	
	public AbstractTxn getLastClearedCredit()
	{
		for (AbstractTxn txn : reverseCleared)
		{
			if (txn.getValue() > 0) return txn;
		}
		return null;		
	}
	
	private static class TxnDateComparator implements Comparator<AbstractTxn>
	{

		@Override
		public int compare(AbstractTxn txn1, AbstractTxn txn2)
		{
			Integer date1 = txn1.getDateInt();
			Integer date2 = txn2.getDateInt();
			return date1.compareTo(date2);
		}
		
	}
}
