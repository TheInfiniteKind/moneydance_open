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
 * Class to wrapper the Moneydance BudgetList class
 * 
 * This class protects the extension from changes to the Moneydance data model
 */

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.infinitekind.moneydance.model.Budget;
import com.infinitekind.moneydance.model.BudgetList;
import com.moneydance.apps.md.controller.FeatureModuleContext;

public class BudgetListExtend {
	private FeatureModuleContext contextCurrent;
	private BudgetList objBudgetCurrent;
	private List<Budget> listBudgets;
	private Map<String,Budget> mapBudgets = new HashMap<String,Budget>();
	/*
	 * Constructor - take context and load BudgetList
	 */
	public BudgetListExtend(FeatureModuleContext context) {
		contextCurrent= context;
		objBudgetCurrent = context.getCurrentAccountBook().getBudgets();
		listBudgets = objBudgetCurrent.getAllBudgets();
		/*
		 * Create the map of budgets - only load new style budgets
		 */
		for (Budget objBudget : listBudgets) {
			if (objBudget.isNewStyle())
				mapBudgets.put(objBudget.getName(),objBudget);
		}
	}
	/*
	 * Get an array of Budget names 
	 */
	public String [] getBudgetNames () {
		Set<String> setNames = mapBudgets.keySet();
		String [] arrNames = setNames.toArray(new String[0]);
		return arrNames;
	}
	/*
	 * Return a new BudgetExtend object from a name
	 */
	public BudgetExtend getBudget(String strName) {
		Budget objBud;
		if (listBudgets.size() < 1)
			return null;
		if (strName.equals("")) 
			objBud = listBudgets.get(0);
		else {
			objBud = mapBudgets.get(strName);
			if (objBud == null)
				objBud = listBudgets.get(0);
		}
		if (objBud == null)
			return null;
		return new BudgetExtend (contextCurrent, objBud);
	}
	/*
	 * Return a new BudgetExtend object from a name
	 */
	public Budget refreshData(String strName) {
		Budget objBud;
		if (strName.equals(""))
			objBud = listBudgets.get(0);
		else
			objBud = mapBudgets.get(strName);
		return objBud;
	}}
