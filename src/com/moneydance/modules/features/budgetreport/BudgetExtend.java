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
 * Class to wrapper the Moneydance Budget class
 * 
 * This class protects the extension from changes to the Moneydance data model
 */
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.Budget;
import com.infinitekind.moneydance.model.BudgetItem;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.moneydance.model.PeriodType;
import com.moneydance.apps.md.controller.FeatureModuleContext;

public class BudgetExtend {

	
	private Budget objBudCurrent;
	private List<BudgetItem> listBudItems;
	private int iItemCount;
	/*
	 * map and tuple class for holding current items
	 */
	private Map<Account,List<Pair<DateRange,BudgetItem>>> mapItems = new HashMap<Account,List<Pair<DateRange,BudgetItem>>>();
	public class Pair<S, T> {
	    public final S x;
	    public final T y;

	    public Pair(S x, T y) { 
	        this.x = x;
	        this.y = y;
	    }
	}
	public BudgetExtend (FeatureModuleContext context, Budget bud) {
		objBudCurrent = bud;
		/*
		 * now load the budget items - map of categories, item of map is list of date ranges
		 */
		reloadItems();
	}
	
	public void refreshData (Budget bud) {
		objBudCurrent = bud;
		reloadItems();
	}
	
	public void reloadItems() {
		listBudItems = objBudCurrent.getAllItems();
		iItemCount = listBudItems.size();
		for (int i =0;i<iItemCount;i++){
			BudgetItem objItem = listBudItems.get(i);
			List<Pair<DateRange,BudgetItem>> listPairs = mapItems.get(objItem.getTransferAccount());
			DateRange drPeriod = new DateRange(objItem.getIntervalStartDate(),objItem.getIntervalEndDate());
			if (listPairs == null) {
				List<Pair<DateRange,BudgetItem>> listItems = new ArrayList<Pair<DateRange,BudgetItem>>();
				listItems.add(new Pair<DateRange,BudgetItem>(drPeriod,objItem));
				mapItems.put(objItem.getTransferAccount(), listItems);
			}
			else {
				listPairs.add(new Pair<DateRange,BudgetItem>(drPeriod,objItem));
			}
		}
		
	}

  	public int getPeriodOrder () {
 
 		PeriodType per = objBudCurrent.getPeriodType();
 		return per.getOrder();
 	}
  	public String getPeriodTypeName () {
  		 
 		return  objBudCurrent.getPeriodType().toString();

 	}
	public Budget getBudget(){
		return objBudCurrent;
	}
	public String getName() {
		return objBudCurrent.getName();
	}
	public String getKey(){
		return objBudCurrent.getKey();
	}
	public int getItemCount() {
		return listBudItems.size();
	}
	public BudgetItem getItem(int index) {
		return listBudItems.get(index);
	}
	/*
	 * get current budget values for specified dates and dates
	 */
	public long[] getCurrentValues(Account objAccountp,DateRange[] arrDates){
		long [] arrCurrentValues = new long[arrDates.length+1];
		int iTotal = arrDates.length;
		arrCurrentValues[iTotal] = 0;
		for (int j=0;j<arrDates.length;j++) {
			arrCurrentValues[j] = 0;
			DateRange drTemp = new DateRange(arrDates[j].getStartDateInt(),
					arrDates[j].getEndDateInt());
			for (BudgetItem arrItem : listBudItems){
				if (arrItem.getTransferAccount() != objAccountp)
					continue;
				if (arrItem.containsDate(drTemp.getStartDateInt()) ||
						arrItem.containsDate(drTemp.getEndDateInt())){
						arrCurrentValues[j] = arrItem.getAmount();
						arrCurrentValues[iTotal] += arrItem.getAmount();
				}
			}
		}
		return arrCurrentValues;
	}

}

