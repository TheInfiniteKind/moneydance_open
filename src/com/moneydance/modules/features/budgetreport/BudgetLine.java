/*
 * Copyright (c) 2014, Michael Bray. All rights reserved.
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
package com.moneydance.modules.features.budgetreport;
/*
 * Each instance of this class is a line in the Budget Details window
 */

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.apps.md.controller.FeatureModuleContext;


/*
 * Can be serialised and stored as part of the Budget Parameters
 */
public class BudgetLine implements java.io.Serializable, Comparable<BudgetLine> {
	/*
	 * Static and transient fields not stored
	 */
	private static final long serialVersionUID = 2L;
	private transient Account objCategory;
	private transient String strParent;
	private transient boolean bSelect;
	private transient boolean bDirty;
	private transient long[] arrTotals;

	/*
	 * fields to be stored
	 */
	private int iType;
	private String strCategory;
	private String strIndentedName;
	/*
	 * Constructor
	 */
	public BudgetLine(int iTypep, String strName, Account objObject) {
		iType = iTypep;
		strIndentedName = strName;
		String[] arrPath = strName.substring(1).split(Constants.chSeperator);
		strCategory = "";
		int i;
		for (i= 0;i<arrPath.length-1;i++)
			strCategory += "   ";
		strCategory += arrPath[i];
		objCategory = objObject;
		bSelect = false;
		bDirty = false;
	}
	/*
	 * returns dirty status
	 */
	public boolean isDirty() {
		return bDirty;
	}
	/*
	 * gets
	 */
	public boolean getSelect () {
		return bSelect;
	}
	public Account getCategory () {
		return objCategory;
	}
	public String getCategoryName () {
		return strCategory;
	}
	public String getCategoryIndent () {
		return strIndentedName;
	}
	public String getParent() {
		return strParent;
	}
	public int getType() {
		return iType;
	}
	public long[] getTotals() {
		return arrTotals;
	}

	/*
	 * sets
	 */
	public void setSelect (boolean bSel) {
		bDirty = true;
		bSelect = bSel;
		return;
	}
	public void setCategory (Account acct) {
		bDirty = true;
		objCategory = acct;
		return;
	}
	public void setCategoryName (String strAcct) {
		bDirty = true;
		strCategory = strAcct;
		return;
	}
	public void setParent(String strParentp){
		strParent = strParentp;
	}
			
	public void setType(int iTypep){
		iType = iTypep;
	}
	public void setDirty(boolean bParm) {
		bDirty = bParm;
	}

	/*
	 * Used to sort budget lines into indented name sequence
	 * @see java.lang.Comparable#compareTo(java.lang.Object)
	 */
	@Override
	public int compareTo(BudgetLine o) {
		return strIndentedName.compareTo(o.getCategoryIndent());
	}
	/*
	 * Generate the budget figures for the line
	 * 
	 * Uses Budget period order to determine how many items to generate
	 */
	public void generateLine(int iType, FeatureModuleContext context, DateRange[] arrPeriods){
//		if (arrTotals == null)
//			arrTotals = new long[arrPeriods.length+1];
		MyTransactionSet objTxnSet = new MyTransactionSet(context, objCategory,arrPeriods);
		arrTotals = objTxnSet.getTotals();
		if (iType == Constants.INCOME_SCREEN)
			for (int i=0;i<arrTotals.length;i++)
				arrTotals[i] = arrTotals[i]*-1;
	}

	/*
	 * Used to add generated line to parent line
	 */
	public void addChild(long[] arrChild) {
		for (int i=0;i<arrTotals.length;i++) 
			arrTotals[i] += arrChild[i];
	}

}