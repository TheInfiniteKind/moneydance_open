package com.moneydance.modules.features.budgetgen;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import javax.swing.table.DefaultTableModel;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.awt.JDateField;

public class GenerateTableModel extends DefaultTableModel {
	
	private List<String> listCategoryName;
	private List<Account> listCategoryObj;
	private List<long[]> listGenData1;
	private List<long[]> listGenData2;
	private List<long[]> listGenData3;
	private List<long[]> listCurrentData1;
	private List<long[]> listCurrentData2;
	private List<long[]> listCurrentData3;
	private List<BudgetLine> listLines;
	private List<CurrencyType> listCurrency;
	private int iPeriods = 0;
	private int iIncrement;
	private int iStartDate;
	private int iPriorStartDate;
	private int iYear;
	private int iType;
	private BudgetParameters objParams;
	private CurrencyType objLocalCur;
	private DateRange[] arrDates;
	private DateRange[] arrPriorDates;
	private String strColumn = "Date";

	public GenerateTableModel(BudgetParameters objParamsp, int iTypep) {
		super();
		objParams = objParamsp;
		iType = iTypep;
		Calendar dtTemp;
		Calendar dtPriorTemp;
        objLocalCur = Main.context.getCurrentAccountBook().getCurrencies().getBaseType();
		iStartDate = objParams.getStartDate();
		iPriorStartDate = objParams.getPriorStart();
		switch (BudgetValuesWindow.budget.getPeriodOrder()) {
		case Constants.PERIODWEEKLY :
			iPeriods = 52;
			iIncrement = 7;
			break;
		case Constants.PERIODBIWEEKLY :
			iPeriods = 26;
			iIncrement = 14;
			break;
		case Constants.PERIODMONTHLY :
			iPeriods = 12;
			iIncrement = -1;
			break;
		default :
			iPeriods = 1;
			iIncrement = -12;
		}
		dtTemp = Calendar.getInstance();
		int iYeart = iStartDate/10000;
		int iMontht = (iStartDate - iYeart*10000)/100;
		int iDayt = iStartDate - iYeart*10000 - iMontht *100;
		dtTemp.set(iYeart,iMontht-1,iDayt);
		dtPriorTemp = Calendar.getInstance();
		iYeart = iPriorStartDate/10000;
		iMontht = (iPriorStartDate - iYeart*10000)/100;
		iDayt = iPriorStartDate - iYeart*10000 - iMontht *100;
		dtPriorTemp.set(iYeart,iMontht-1,iDayt);
		arrDates = new DateRange[iPeriods];
		arrPriorDates = new DateRange[iPeriods];
		Calendar dtTemp2 = Calendar.getInstance();
		Calendar dtPriorTemp2 = Calendar.getInstance();
		for (int i=0;i<iPeriods;i++) {
			dtTemp2.setTime(dtTemp.getTime());
			dtPriorTemp2.setTime(dtPriorTemp.getTime());
			if (iIncrement >0) {
				dtTemp2.add(Calendar.DAY_OF_YEAR, iIncrement);
				dtPriorTemp2.add(Calendar.DAY_OF_YEAR, iIncrement);
			}
			else {
				dtTemp2.add(Calendar.MONTH, -iIncrement);
				dtPriorTemp2.add(Calendar.MONTH, -iIncrement);
			}
			dtTemp2.add(Calendar.DAY_OF_YEAR, -1);			
			dtPriorTemp2.add(Calendar.DAY_OF_YEAR, -1);			
			arrDates[i] = new DateRange(dtTemp.getTime(), dtTemp2.getTime());
			arrPriorDates[i] = new DateRange(dtPriorTemp.getTime(), dtPriorTemp2.getTime());
			dtTemp.setTime(dtTemp2.getTime());
			dtTemp.add(Calendar.DAY_OF_YEAR, 1);	
			dtPriorTemp.setTime(dtPriorTemp2.getTime());
			dtPriorTemp.add(Calendar.DAY_OF_YEAR, 1);	
		}
		listLines = new ArrayList<BudgetLine>();
		listCategoryName = new ArrayList<String>();
		listCategoryObj = new ArrayList<Account>();
		listCurrency = new ArrayList<CurrencyType>();
		listGenData1 = new ArrayList<long[]>();
		listGenData2 = new ArrayList<long[]>();
		listGenData3 = new ArrayList<long[]>();
		listCurrentData1 = new ArrayList<long[]>();
		listCurrentData2 = new ArrayList<long[]>();
		listCurrentData3 = new ArrayList<long[]>();		
	}

	public void AddLine (BudgetLine objLine) {
		listLines.add(objLine);
		listCategoryName.add(objLine.getCategoryName());
		listCategoryObj.add(objLine.getCategory());
		listGenData1.add(objLine.getYear1Array());
		listGenData2.add(objLine.getYear2Array());
		listGenData3.add(objLine.getYear3Array());
		Account objAcct =  objLine.getCategory();
		CurrencyType objCur;
		/*
		 * default to file base currency if currency not set
		 */
		objCur = (objAcct == null?null : objAcct.getCurrencyType());
		if (objCur == null)
			objCur = objLocalCur;
		listCurrency.add(objCur);
		/*
		 * get current budget items
		 */
		listCurrentData1.add(BudgetValuesWindow.budget.getCurrentValues(1,objLine.getCategory(),arrDates));
		listCurrentData2.add(BudgetValuesWindow.budget.getCurrentValues(2,objLine.getCategory(),arrDates));
		listCurrentData3.add(BudgetValuesWindow.budget.getCurrentValues(3,objLine.getCategory(),arrDates));
		return;
	}
	public void reloadCurrent() {
		listCurrentData1 = new ArrayList<long[]>();
		listCurrentData2 = new ArrayList<long[]>();
		listCurrentData3 = new ArrayList<long[]>();		
		for (Account objAcct:listCategoryObj) {
			listCurrentData1.add(BudgetValuesWindow.budget.getCurrentValues(1,objAcct,arrDates));
			listCurrentData2.add(BudgetValuesWindow.budget.getCurrentValues(2,objAcct,arrDates));
			listCurrentData3.add(BudgetValuesWindow.budget.getCurrentValues(3,objAcct,arrDates));
		}
	}
	public void setYear(int iYearp) {
		iYear=iYearp;
		return;
	}
	@Override
	public int getRowCount() {
		return (listGenData1 == null?0:listGenData1 .size()*2);
	}

	@Override
	public int getColumnCount() {
		return iPeriods;
	}
	
	@Override
	public String getColumnName(int c) {
		int iStart = arrDates[c].getStartDateInt() + (iYear-1)*10000;
		int iEnd = arrDates[c].getEndDateInt() + (iYear-1)*10000;
		JDateField jdtTemp = new JDateField(Main.cdate);
		strColumn= "<html>";
		strColumn += jdtTemp.getStringFromDateInt(iStart);
		strColumn +="-<br>";
		strColumn += jdtTemp.getStringFromDateInt(iEnd);
		strColumn +="</html>";
		return strColumn;
	}
	
	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {

		CurrencyType objCur = listCurrency.get(rowIndex/2);	
		if ((rowIndex & 1) == 0) {
			switch (iYear) {
			case 1:
				return objCur.formatFancy(listGenData1.get(rowIndex/2)[columnIndex],'.');
			case 2:
				return objCur.formatFancy(listGenData2.get(rowIndex/2)[columnIndex],'.');
			default:
				return objCur.formatFancy(listGenData3.get(rowIndex/2)[columnIndex],'.');
			}
		}
		else {
			switch (iYear) {
			case 1:
				String strTemp =objCur.formatFancy(listCurrentData1.get(rowIndex/2)[columnIndex],'.');
				return strTemp;
			case 2:
				return objCur.formatFancy(listCurrentData2.get(rowIndex/2)[columnIndex],'.');
			default:
				return objCur.formatFancy(listCurrentData3.get(rowIndex/2)[columnIndex],'.');
			}
		}	
	}
	@Override
    public boolean isCellEditable(int row, int col) {
		if ((row &1) == 0)
			return true;
		return false;
	}
 	@Override
	public void setValueAt(Object value, int row, int col){
		if ((row &1) == 0) {
			/*
			 * Get the currency type for the row.  If it is null use the default type for the file
			 */
			CurrencyType objCur = listCurrency.get(row/2);	
	        long lAmt =objCur.parse((String)value,'.');
			listLines.get(row/2).setPeriod(col,iYear, lAmt);
			objParams.setManual(true);
		}
		
 	}
 	/*
 	 * get budget amount for prior period
 	 */
	public String getPreviousBudget(int iRow, int iCol) {
		int iLineRow = iRow/2;
		CurrencyType objCur = listCurrency.get(iLineRow);	
		BudgetLine objLine = listLines.get(iLineRow);
		long lTotal = BudgetValuesWindow.budget.getPriorAmount(objLine.getCategory(),arrPriorDates[iCol].getStartDateInt(),arrPriorDates[iCol].getEndDateInt());
		return objCur.formatFancy(lTotal,'.');
	}
	/*
	 * get actual amount for prior period
	 */
	public String getPreviousActuals (int iRow, int iCol) {
		int iLineRow = iRow/2;
		CurrencyType objCur = listCurrency.get(iLineRow);	
		BudgetLine objLine = listLines.get(iLineRow);
		DateRange[] drPrior = new DateRange[1];
		drPrior[0] = new DateRange(arrPriorDates[iCol].getStartDateInt(),arrPriorDates[iCol].getEndDateInt());
		MyTransactionSet objTxns = new MyTransactionSet(Main.context,objLine.getCategory(), drPrior);
		long[] arrTotals = objTxns.getTotals();
		long lTotal = 0;
		for (int i=0;i<arrTotals.length-1;i++)
			lTotal += arrTotals[i];
		if (iType == Constants.INCOME_SCREEN)
			lTotal *= -1;
		return objCur.formatFancy(lTotal,'.');
	}	/*
 	 * return period dates
 	 */
 	public DateRange[] getPeriods() {
 		return arrDates;
 	}
 	/*
 	 * return generated values
 	 */
 	public long[] getGeneratedValues(int iRow) {
 		switch (iYear) {
 		case 1:
 			return listGenData1.get(iRow);
 		case 2:
 			return listGenData2.get(iRow);
 		default:
 			return listGenData3.get(iRow);
 		}
 	}
 	/*
 	 * return current values
 	 */
 	public long[] getCurrentValues(int iRow) {
 		switch (iYear) {
 		case 1:
 			return listCurrentData1.get(iRow);
 		case 2:
 			return listCurrentData2.get(iRow);
 		default:
 			return listCurrentData3.get(iRow);
 		}
 	}
 	/*
 	 * return the account object for row i
 	 */
 	public Account getCategoryObj(int iRow) {
 		return listCategoryObj.get(iRow);
 	}
 	/*
 	 * return the currency for row i
 	 */
 	public CurrencyType getCurrency(int iRow) {
 		return listCurrency.get(iRow);
 	}
}
