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

import java.util.List;

import javax.swing.JComboBox;
import javax.swing.table.DefaultTableModel;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.util.DateUtil;
import com.moneydance.awt.JDateField;

public class MyTableModel extends DefaultTableModel {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private int iYears = 1;
	private int iType;
	private BudgetParameters objParams;
	private static final String[] strColumns = 
		{"Select", "Category","Roll up", "Amount", "Period", "Start Date","Extra RPI", "Year 1"};
	@SuppressWarnings("rawtypes")
	private static final Class[] columnTypes = new Class[] {
			Boolean.class, Object.class, Object.class, String.class, JComboBox.class, String.class,String.class, String.class
		};
	public MyTableModel (BudgetParameters objParamsp, int iTypep){
		super();
		objParams = objParamsp;
		iType = iTypep;
	}
	@Override
	public int getRowCount() {
		return ( objParams == null? 0 :  objParams.getLineCount());
	}

	@Override
	public int getColumnCount() {
			return strColumns.length+iYears-1;
	}
	
	@Override
	@SuppressWarnings({ "rawtypes", "unchecked" })
	public Class getColumnClass(int c){
		if (c == strColumns.length || c == strColumns.length+1)
			return String.class;
		return columnTypes[c];
	}
	@Override
	public String getColumnName(int c) {
		if (c == strColumns.length)
			return "Year 2";
		if (c == strColumns.length+1)
			return "Year 3";
		return strColumns[c];
	}
	@Override
	public Object getValueAt(int iRow, int iCol) {
		Account objAcct =  objParams.getLines().get(iRow).getCategory();
        CurrencyType objLocalCur = Main.context.getCurrentAccountBook().getCurrencies().getBaseType();
		CurrencyType objCur;
		BudgetLine objLine = objParams.getLines().get(iRow);
		/*
		 * default to file base currency if currency not set
		 */
		objCur = (objAcct == null?null : objAcct.getCurrencyType());
		if (objCur == null)
			objCur = objLocalCur;
		switch (iCol) {
		case 0:
			return  objLine.getSelect();
		case 1:
			return  objLine.getCategoryName();
		case 2:
			return objLine.getRollup();
		case 3:
			return objCur.formatFancy( objLine.getAmount(),'.');
		case 4:
			return Constants.arrPeriod[ objLine.getPeriod()];
		case 5:
			JDateField jdtTemp = new JDateField(Main.cdate);
			return 	jdtTemp.getStringFromDateInt(objLine.getStartDate());
		case 6:
			return  objLine.getRPI()/100.0;
		case 7:
			return objCur.formatFancy( objLine.getYear1Amt(),'.');
		case 8:
			return objCur.formatFancy( objLine.getYear2Amt(),'.');
		default:
			return objCur.formatFancy( objLine.getYear3Amt(),'.');
		}
	}
	public String getPreviousBudget(int iRow) {
        CurrencyType objLocalCur = Main.context.getCurrentAccountBook().getCurrencies().getBaseType();
		CurrencyType objCur;
		BudgetLine objLine = objParams.getLines().get(iRow);
		/*
		 * default to file base currency if currency not set
		 */
		objCur = (objLine.getCategory() == null?null : objLine.getCategory().getCurrencyType());
		if (objCur == null)
			objCur = objLocalCur;
		long lTotal = BudgetValuesWindow.budget.getPriorAmount(objLine.getCategory(),objParams.getPriorStart(),objParams.getPriorEnd());
		long lReturn = 0;
		int iDays;
		int iMonths;
		switch (Constants.arrPeriod[objLine.getPeriod()]) {
		case Constants.PERIOD_BIWEEK :
			iDays = objParams.getPriorDays();
			lReturn = lTotal/iDays * 14;
			break;
		case Constants.PERIOD_WEEK :
			iDays = objParams.getPriorDays();
			lReturn = lTotal/iDays * 7;
			break;
		case Constants.PERIOD_MONTH :
			iMonths = Math.round(DateUtil.monthsInPeriod(objParams.getPriorStart(), objParams.getPriorEnd()));
			lReturn = lTotal/iMonths;
			break;
		case Constants.PERIOD_TENMONTH :
			iMonths = Math.round(DateUtil.monthsInPeriod(objParams.getPriorStart(), objParams.getPriorEnd()));
			lReturn = lTotal/iMonths*10/12;
			break;
		case Constants.PERIOD_QUARTER :
			iMonths = Math.round(DateUtil.monthsInPeriod(objParams.getPriorStart(), objParams.getPriorEnd()));
			iMonths = iMonths/3;
			lReturn = lTotal/iMonths;
			break;
		default :
			lReturn = lTotal;
		}
		if (iType == Constants.INCOME_SCREEN)
			lReturn *= -1;
		return objCur.formatFancy(lReturn,'.');
	}
	public String getPreviousActuals (int iRow) {
        CurrencyType objLocalCur = Main.context.getCurrentAccountBook().getCurrencies().getBaseType();
		CurrencyType objCur;
		BudgetLine objLine = objParams.getLines().get(iRow);
		/*
		 * default to file base currency if currency not set
		 */
		objCur = (objLine.getCategory() == null?null : objLine.getCategory().getCurrencyType());
		if (objCur == null)
			objCur = objLocalCur;
		DateRange[] drPrior = new DateRange[1];
		drPrior[0] = new DateRange(objParams.getPriorStart(),objParams.getPriorEnd());
		MyTransactionSet objTxns = new MyTransactionSet(Main.context,objLine.getCategory(), drPrior);
		long[] arrTotals = objTxns.getTotals();
		long lTotal = arrTotals[arrTotals.length-1];
		long lReturn = 0;
		int iDays;
		int iMonths;
		switch (Constants.arrPeriod[objLine.getPeriod()]) {
		case Constants.PERIOD_BIWEEK :
			iDays = objParams.getPriorDays();
			lReturn = lTotal/iDays * 14;
			break;
		case Constants.PERIOD_WEEK :
			iDays = objParams.getPriorDays();
			lReturn = lTotal/iDays * 7;
			break;
		case Constants.PERIOD_MONTH :
			iMonths = Math.round(DateUtil.monthsInPeriod(objParams.getPriorStart(), objParams.getPriorEnd()));
			lReturn = lTotal/iMonths;
			break;
		case Constants.PERIOD_TENMONTH :
			iMonths = Math.round(DateUtil.monthsInPeriod(objParams.getPriorStart(), objParams.getPriorEnd()));
			lReturn = lTotal/iMonths*10/12;
			break;
		case Constants.PERIOD_QUARTER :
			iMonths = Math.round(DateUtil.monthsInPeriod(objParams.getPriorStart(), objParams.getPriorEnd()));
			iMonths = iMonths/3;
			lReturn = lTotal/iMonths;
			break;
		default :
			lReturn = lTotal;
		}
		if (iType == Constants.INCOME_SCREEN)
			lReturn *= -1;
		return objCur.formatFancy(lReturn,'.');
	}
	@Override
    public boolean isCellEditable(int iRow, int iCol) {
        /*
         * Only Select, amount, period, start date and RPI are editable if not parent and
         * not roll up
         * Category, Year 1, Year 2, Year 3 are not
         */
		BudgetLine objLine = objParams.getLines().get(iRow);
		switch (iCol) {
        case 0:
        	return true;
        case 2:
        	if (objLine.getType() == Constants.PARENT_LINE)
        		return true;
        	else
        		return false;
        case 3:
        case 4:
        case 5:
        case 6:
        	if (objLine.getType()==Constants.PARENT_LINE && objLine.getRollup())
        		return false;
            return true;
        case 1:
        case 7:
        case 8:
       default:
            return false;
        }
    }
	@Override
	public void setValueAt(Object value, int iRow, int iCol){
		BudgetLine objBud =  objParams.getItem(iRow);
		/*
		 * copes with call when data is invalid
		 */
		if (value == null)
			return;
		switch (iCol) {
		case 0:
			objBud.setSelect((Boolean)value);
			break;
		case 2:
			objBud.setRollup((Boolean)value);
			break;
		case 3:
			/*
			 * Get the currency type for the row.  If it is null use the default type for the file
			 */
	        List<BudgetLine> listLines =  objParams.getLines();
	        CurrencyType objCur =(listLines.get(iRow).getCategory() == null ? 
	        		Main.context.getCurrentAccountBook().getCurrencies().getBaseType():listLines.get(iRow).getCategory().getCurrencyType());
	        long lAmt =objCur.parse((String)value,'.');
			objBud.setAmount((int)lAmt);
			break;
		case 4:
			for (int i=0;i<Constants.arrPeriod.length;i++){
				if (((String)value).equals(Constants.arrPeriod[i]))
					objBud.setPeriod(i);				
			}
			break;
		case 5:
			JDateField jdtField = new JDateField(Main.cdate);
			objBud.setStartDate(jdtField.getDateIntFromString((String)value));
			break;
		case 6:
			objBud.setRPI(Double.parseDouble((String)value));
		}
	}
	public void alterYears(int iYearsp) {
		if (this.iYears > iYearsp) {
			iYears = iYearsp;
		}
		else {
			while (this.iYears < iYearsp) {
				this.addColumn("Year "+(iYears+1));
				iYears++;
			}
		}
		this.fireTableStructureChanged();		
	}
}


