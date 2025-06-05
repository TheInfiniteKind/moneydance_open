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
package com.moneydance.modules.features.budgetgen;
/*
 * Class to wrapper the Moneydance Budget class
 * 
 * This class protects the extension from changes to the Moneydance data model
 */
import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.Budget;
import com.infinitekind.moneydance.model.BudgetItem;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.moneydance.model.PeriodType;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.awt.JDateField;

public class BudgetExtend {

	
	private Budget objBudCurrent;
	private FeatureModuleContext context;
	private List<BudgetItem> listBudItems;
	private int iFiscalMonth;
	private int iFiscalDay;
	private int iYear;
	private Calendar dtWeekStart;
	private BudgetParameters objParameters;
	private JDateField jdtFiscalStart;
	private int iItemCount;
	private int iType;
	private String strFileName;
	/*
	 * map and tuple class for holding current items
	 */
	private Map<Account,List<Pair<DateRange,BudgetItem>>> mapItems = new HashMap<>();

	public record Pair<S, T>(S x, T y) {
	}
	/*
	 * Map for previous items
	 */
	public BudgetExtend (FeatureModuleContext contextp, Budget bud, int iFiscalYear, int iTypep, String strFileNamep) {
		objBudCurrent = bud;
		context = contextp;
		iType = iTypep;
		strFileName = strFileNamep;
		iFiscalMonth = iFiscalYear/100;
	    iFiscalDay = iFiscalYear - iFiscalMonth*100;
	    Calendar gc = Calendar.getInstance();
	    iYear = gc.get(Calendar.YEAR);
	    Calendar dtYear = Calendar.getInstance();
	    dtYear.set(iYear,Calendar.JANUARY, 1);
	    Calendar dtFiscalStart = Calendar.getInstance();
	    dtFiscalStart.set(iYear,iFiscalMonth-1,iFiscalDay);
	    Calendar dtToday = new GregorianCalendar();
	    if (dtFiscalStart.after(dtToday))
	    	dtFiscalStart.set(iYear-1,iFiscalMonth-1,iFiscalDay);
	    dtWeekStart= Calendar.getInstance();
	    dtWeekStart.setWeekDate(iYear,1,Calendar.SUNDAY);
	    /*
	     * set Fiscal Start to match Budget Period Type
	     */
	    switch (getPeriodOrder()){
	    case Constants.PERIODWEEKLY :
	    	/*
	    	 * set fiscal start to closest Sunday before or equal 
	    	 */
	    	Calendar dtTemp = (Calendar) dtWeekStart.clone();
	    	while (dtTemp.before(dtFiscalStart))
	    		dtTemp.add(Calendar.DAY_OF_YEAR, 7);
	    	if (dtTemp.after(dtFiscalStart))
	    		dtTemp.add(Calendar.DAY_OF_YEAR, -7);
	    	dtFiscalStart = (Calendar)dtTemp.clone();
	    	break;
	    case Constants.PERIODBIWEEKLY :
	    	/*
	    	 * set fiscal start to closest Sunday before or equal that falls on fortnight
	    	 * boundary
	    	 */
	    	Calendar dtTempbi = (Calendar) dtWeekStart.clone();
	    	while (dtTempbi.before(dtFiscalStart))
	    		dtTempbi.add(Calendar.DAY_OF_YEAR, 14);
	    	if (dtTempbi.after(dtFiscalStart))
	    		dtTempbi.add(Calendar.DAY_OF_YEAR, -14);
	    	dtFiscalStart = (Calendar)dtTempbi.clone();
	    	break;
	    case Constants.PERIODMONTHLY :
	    	/*
	    	 * set fiscal start to month 
	    	 */
	    	dtFiscalStart.set(Calendar.DAY_OF_MONTH,1);
	    	break;
    	default :
	    	/*
	    	 * set fiscal start to start of calendar year 
	    	 */
    		dtFiscalStart = Calendar.getInstance();
    		dtFiscalStart.setTime(dtYear.getTime());
	    }
	    jdtFiscalStart = new JDateField (Main.cdate);
	    jdtFiscalStart.setDate(dtFiscalStart.getTime());
		objParameters = new BudgetParameters (context, this, jdtFiscalStart, iType, strFileName);
		/*
		 * now load the budget items - map of categories, item of map is list of date ranges
		 */
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
				List<Pair<DateRange,BudgetItem>> listItems = new ArrayList<>();
				listItems.add(new Pair<>(drPeriod, objItem));
				mapItems.put(objItem.getTransferAccount(), listItems);
			}
			else {
				listPairs.add(new Pair<>(drPeriod, objItem));
			}
		}
		
	}

  	public int getPeriodOrder () {
 
 		PeriodType per = objBudCurrent.getPeriodType();
 		if (per == null) {
			 System.err.println("MRB Extension Budge Generator - inconsistent Budget Record "+getName());
 			per = PeriodType.valueOf("MONTH");
 		}
 		return per.getOrder();
 	}
  	public String getPeriodTypeName () {
  		if (objBudCurrent.getPeriodType() == null) {
  			 System.err.println("MRB Extension Budge Generator - inconsistent Budget Record "+objBudCurrent.getName());
   			return "Month";
 		}
		return  objBudCurrent.getPeriodType().toString();

 	}
	public Budget getBudget(){
		return objBudCurrent;
	}
	public BudgetParameters getParameters(){
		return objParameters;
	}
	public String getName() {
		return objBudCurrent.getName();
	}
	public String getKey(){
		return objBudCurrent.getKey();
	}
	public JDateField getFiscalStart() {
		return jdtFiscalStart;
	}


	/*
	 * get current budget values for specified dates and dates
	 */
	public long[] getCurrentValues(int iYearp,Account objAccountp,DateRange[] arrDates){
		long [] arrCurrentValues = new long[arrDates.length];
		for (int j=0;j<arrDates.length;j++) {
			arrCurrentValues[j] = 0;
			DateRange drTemp = new DateRange(arrDates[j].getStartDateInt()+((iYearp-1)*10000),
					arrDates[j].getEndDateInt()+((iYearp-1)*10000));
			for (BudgetItem arrItem: listBudItems){
				if (arrItem.getTransferAccount() != objAccountp)
					continue;
				if (arrItem.containsDate(drTemp.getStartDateInt()) ||
						arrItem.containsDate(drTemp.getEndDateInt())){
						arrCurrentValues[j] = arrItem.getAmount();
				}
			}
		}
		return arrCurrentValues;
	}
	/*
	 * calculate prior period total
	 */
	public long getPriorAmount (Account objAccountp, int iStart, int iEnd) {
		long lReturn = 0;
		for (BudgetItem arrItem: listBudItems){
			if (arrItem.getTransferAccount() != objAccountp)
				continue;
			if (arrItem.getIntervalStartDate() >= iStart &&
					arrItem.getIntervalEndDate()<= iEnd){
					lReturn += arrItem.getAmount();
			}
		}
		return lReturn;		
	}
	/*
	 * 
	 * Find item
	 */
	private BudgetItem findItem(Account objAcct,DateRange dtPeriod){
		List<Pair<DateRange,BudgetItem>> listRanges = mapItems.get(objAcct);
		if (listRanges == null) {
			return null;
		}
		for (Pair<DateRange,BudgetItem> objPair: listRanges){
			if (objPair.x.containsInt(dtPeriod.getStartDateInt())){
				return objPair.y;
			}
		}
		return null;
	}
	/*
	 * create a particular budget item
	 */
	public void createItem(Account objAcct,DateRange dtPeriod,long lAmount) {
		if (findItem(objAcct,dtPeriod)== null){
			BudgetItem objItem = objBudCurrent.createItem();
			objItem.setTransferAccount(objAcct);
			objItem.setIntervalStartDate(dtPeriod.getStartDateInt());
			objItem.setIntervalEndDate(dtPeriod.getEndDateInt());
			objItem.setAmount(lAmount);
			/*
			 * translate budget period order into item interval type
			 */
			objItem.setInterval(Constants.intervaltypes.get(objBudCurrent.getPeriodType().getOrder()));
			objItem.syncItem();
		}
		else 
			updateItem (objAcct, dtPeriod,lAmount);
	}
	/*
	 * update a particular budget item
	 */
	public void updateItem(Account objAcct,DateRange dtPeriod,long lAmount) {
		BudgetItem objItem = findItem(objAcct,dtPeriod);
		if (objItem == null)
			createItem (objAcct, dtPeriod,lAmount);
		else {
			objItem.setAmount(lAmount);
			objItem.syncItem();
		}
	}
	/*
	 * delete a particular budget item
	 */
	public void deleteItem(Account objAcct,DateRange dtPeriod) {
		BudgetItem objItem = findItem(objAcct,dtPeriod);
		if (objItem != null)
			objItem.deleteItem();
		
	}
	}

