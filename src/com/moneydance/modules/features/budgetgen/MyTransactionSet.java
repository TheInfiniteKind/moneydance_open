/*
 *  Copyright (c) 2014, Michael Bray. All rights reserved.
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
 */ 
package com.moneydance.modules.features.budgetgen;

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.moneydance.model.Txn;
import com.infinitekind.moneydance.model.TxnSearch;
import com.infinitekind.moneydance.model.TxnSet;
import com.moneydance.apps.md.controller.FeatureModuleContext;

public class MyTransactionSet implements TxnSearch{
	private TxnSet stlTrans;
	private Account acct;
	private long [] arrTotals;
	private int iStartDate;
	private int iEndDate;
	public MyTransactionSet(FeatureModuleContext context, Account acctp, DateRange[] arrPeriods) {
		acct = acctp;
		iStartDate = arrPeriods[0].getStartDateInt();
		iEndDate = arrPeriods[arrPeriods.length-1].getEndDateInt();
		arrTotals = new long[arrPeriods.length+1];
		for (int i = 0;i<arrPeriods.length+1;i++)
			arrTotals[i] = 0;
		stlTrans = context.getCurrentAccountBook().getTransactionSet().getTransactions(this);
		
		/*
		 * Create map of transactions by date
		 */
		for (AbstractTxn txnLine : stlTrans) {
			int x;
			int y;
			int i;
			int iTotal = arrPeriods.length;
			x=0;
			y = arrPeriods.length-1;
			int iDate = txnLine.getDateInt();
			i = findPeriod(arrPeriods,iDate, x, y);
			if (i != Constants.KEY_NOT_FOUND){
				arrTotals[i] += + txnLine.getValue();
				arrTotals[iTotal] += txnLine.getValue();
			}
		}	
	}
	private int findPeriod(DateRange[] arrPeriods,int iDate, int iMin, int iMax){
		  // test if array is empty
		  if (iMax < iMin)
		    // set is empty, so return value showing not found
		    return Constants.KEY_NOT_FOUND;
		  else
		    {
		      // calculate midpoint to cut set in half
		      int iMid =(iMax-iMin)/2+iMin;
		 
		      // three-way comparison
		      if (iDate < arrPeriods[iMid].getStartDateInt())
		        // key is in lower subset
		        return findPeriod(arrPeriods, iDate, iMin, iMid - 1);
		      else if (arrPeriods[iMid].getEndDateInt() < iDate)
		        // key is in upper subset
		        return findPeriod(arrPeriods, iDate, iMid+1, iMax);
		      else
		        // key has been found
		        return iMid;
		    }
	}
	@Override
	public boolean matches(Txn txnParm) {
		if (txnParm.getAccount() != acct)
			return false;
		if (txnParm.getDateInt() >= iStartDate &&
				txnParm.getDateInt() <= iEndDate)
			return true;
		return false;
	}

	@Override
	public boolean matchesAll() {
		return false;
	}
	/*
	 * return values
	 */
	public long[] getTotals() {
		return arrTotals;
	}

}
