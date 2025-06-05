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


import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;

import javax.swing.DefaultListModel;

public class MyListModel extends DefaultListModel<String> {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private BudgetParameters objParams;
	private int iType;
	private int iList;
	private List<Entry<String, AccountDetails>> listLines;

	public MyListModel (BudgetParameters objParamsp, int iTypep, int iListp){
		super();
		objParams = objParamsp;
		iType = iTypep;
		iList = iListp;
		if (iType == Constants.EXPENSE_SCREEN)
			if (iList == Constants.MISSING) {
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getExpenseMissing().entrySet());
			}
			else {
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getExpenseSelect().entrySet());
			}
		else
			if (iList == Constants.MISSING) {
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getIncomeMissing().entrySet());
			}
			else
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getIncomeSelect().entrySet());
	}
	@Override
	public int getSize() {
		return listLines.size();
	}

	
	@Override
	public String getElementAt(int index) {
		BudgetLine objLine;
		objLine = listLines.get(index).getValue().getLine();
		return objLine.getCategoryName();
	}
	public String getLineKey(int index) {
		BudgetLine objLine;
		objLine = listLines.get(index).getValue().getLine();
		return objLine.getCategoryIndent();
	}
	public void addElement(String strName) {
		if (iType == Constants.EXPENSE_SCREEN)
			if (iList == Constants.MISSING)
				objParams.deselectExpenseLine(strName);
			else
				objParams.addExpenseLine(strName);
		else
			if (iList == Constants.MISSING)
				objParams.deselectIncomeLine(strName);
			else
				objParams.addIncomeLine(strName);		
	}
	public String remove(int iRow) {
		String strName = listLines.get(iRow).getKey();
		if (iType == Constants.EXPENSE_SCREEN)
			if (iList == Constants.MISSING)
				objParams.deleteExpenseMissing(strName);
			else
				objParams.deleteExpenseLine(strName);
		else
			if (iList == Constants.MISSING)
				objParams.deleteIncomeMissing(strName);
			else
				objParams.deleteIncomeLine(strName);		
		return listLines.remove(iRow).getKey();
	}
	public void update() {
		if (iType == Constants.EXPENSE_SCREEN)
			if (iList == Constants.MISSING) {
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getExpenseMissing().entrySet());
			}
			else {
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getExpenseSelect().entrySet());
			}
		else
			if (iList == Constants.MISSING) {
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getIncomeMissing().entrySet());
			}
			else
				listLines = new ArrayList<Entry<String, AccountDetails>>(objParams.getIncomeSelect().entrySet());
		this.fireContentsChanged(this, 0, this.size()-1);
	}
}


