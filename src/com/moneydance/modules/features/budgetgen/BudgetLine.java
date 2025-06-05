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
 * Each instance of this class is a line in the Budget Details window
 */
import java.io.Serial;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Objects;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.awt.JDateField;

/*
 * Can be serialised and stored as part of the Budget Parameters
 */
public class BudgetLine implements java.io.Serializable, Comparable<BudgetLine> {
	/*
	 * Static and transient fields not stored
	 */
	@Serial
	private static final long serialVersionUID = 2L;
	private transient Account category;
	private transient String parent;
	private transient boolean select;
	private transient boolean dirty;
	private transient Calendar startDate = Calendar.getInstance();
	private transient int arraySize = 0;

	/*
	 * fields to be stored
	 */
	private int iType;
	private String strCategory;
	private String strIndentedName;
	private boolean bRollup;
	private long lAmount;
	private int iPeriod;
	private int iStartDate;
	private long lYear1Amt;
	private long lYear2Amt;
	private long lYear3Amt;
	private int iNumPeriods;
	private long[] arrlYear1;
	private long[] arrlYear2;
	private long[] arrlYear3;

	private double dRPI;
	/*
	 * Constructor
	 */
	public BudgetLine(int iTypep, String strName, Account objObject, int iStartDatep, int iPeriodp) {
		iType = iTypep;
		strIndentedName = strName;
		String[] arrPath = strName.substring(1).split(Constants.chSeperator);
		int i;
		StringBuilder tmpBuilder = new StringBuilder();
		for (i= 0;i<arrPath.length-1;i++)
			tmpBuilder.append("   ");
		tmpBuilder.append(arrPath[i]);
		strCategory = tmpBuilder.toString();
		category = objObject;
		select = false;
		bRollup = false;
		dirty = false;
		parent = "";
		/*
		 * forces set up of dtStartDate
		 */
		setStartDate(iStartDatep);
		iPeriod = iPeriodp;
		dRPI = 0.0;
		lYear1Amt = 0;
		lYear2Amt = 0;
		lYear3Amt = 0;
		arrlYear1 = null;
		arrlYear2 = null;
		arrlYear3 = null;
		iNumPeriods = 0;
	}
	/*
	 * returns dirty status
	 */
	public boolean isDirty() {
		return dirty;
	}
	/*
	 * gets
	 */
	public boolean getSelect () {
		return select;
	}
	public Account getCategory () {
		return category;
	}
	public String getCategoryName () {
		return strCategory;
	}
	public String getCategoryIndent () {
		return strIndentedName;
	}
	public long getAmount() {
		return lAmount;
	}
	public String getParent() {
		return parent;
	}
	public int getPeriod () {
		return iPeriod;
	}
	public int getStartDate () {
		return iStartDate;
	}
	public int getType() {
		return iType;
	}
	public boolean getRollup () {
		return bRollup;
	}
	public double getRPI () {
		return dRPI;
	}
	public long getYear1Amt () {
		return lYear1Amt;
	}
	public long getYear2Amt () {
		return lYear2Amt;
	}
	public long getYear3Amt () {
		return lYear3Amt;
	}
	public long[] getYear1Array() {
		return arrlYear1;
	}
	public long[] getYear2Array() {
		return arrlYear2;
	}
	public long[] getYear3Array() {
		return arrlYear3;
	}

	/*
	 * sets
	 */
	public void setSelect (boolean bSel) {
		dirty = true;
		select = bSel;
	}
	public void setCategory (Account acct) {
		dirty = true;
		category = acct;
	}
	public void setAmount(long lAmt) {
		dirty = true;
		lAmount = lAmt;
	}
	public void setParent(String strParentp){
		parent = strParentp;
	}
			
	public void setPeriod (int iPer) {
		dirty = true;
		iPeriod = iPer;
	}
	public void setStartDate (int iStr) {
		dirty = true;
		iStartDate = iStr;
		int iYear = iStr/10000;
		int iMonth = (iStr- iYear*10000)/100;
		int iDay = iStr-iYear*10000 - iMonth*100;
		if (startDate == null)
			startDate = Calendar.getInstance();
		startDate.set(iYear, iMonth-1,iDay);
	}
	public void setRollup (boolean bRollupp) {
		dirty = true;
		bRollup = bRollupp;
	}
	public void setRPI (double dRPIp) {
		dirty = true;
		dRPI = dRPIp;
	}
	public void setYear1Amt (long iBud) {
		dirty = true;
		lYear1Amt = iBud;
	}
	public void setYear2Amt (long iBud) {
		dirty = true;
		lYear2Amt = iBud;
	}
	public void setYear3Amt (long iBud) {
		dirty = true;
		lYear3Amt = iBud;
	}
	public void setType(int iTypep){
		iType = iTypep;
	}
	public void setDirty(boolean bParm) {
		dirty = bParm;
	}
	public void setNumPeriods(int iNumPeriodsp) {
		if (iNumPeriods != iNumPeriodsp) {
			arrlYear1 = null;
			arrlYear2 = null;
			arrlYear3 = null;
		}
		iNumPeriods = iNumPeriodsp;
		if (arrlYear1 == null)
			arrlYear1 = new long[iNumPeriods];
		if (arrlYear2 == null)
			arrlYear2 = new long[iNumPeriods];
		if (arrlYear3 == null)
			arrlYear3 = new long[iNumPeriods];
	}
	public void setPeriod (int iPeriod, int iYear, long lPeriodAmt) {
		dirty = true;
		switch (iYear) {
		case 1:
			arrlYear1[iPeriod] = lPeriodAmt;
			break;
		case 2:
			arrlYear2[iPeriod] = lPeriodAmt;
			break;
		default:
			arrlYear3[iPeriod] = lPeriodAmt;
		}
	}
	/*
	 * Determines the budget amount for the year based on the selected period
	 * 
	 * Calculates the year 2 and year 3 amounts based on the 
	 * combined RPI (RPI for Budget and RPI for the individual line)
	 * 
	 * Note: Month in Calendars is 0 to 11.
	 */
	public void calculateLine(int iStartDatep,int iEndDatep, double dRPIp) {
		Calendar calStart = Calendar.getInstance();
		calStart.set(iStartDate/10000, iStartDate/100-iStartDate/10000*100-1, iStartDate - iStartDate/100*100);
		Calendar calStartp = Calendar.getInstance();
		calStartp.set(iStartDatep/10000, iStartDatep/100-iStartDatep/10000*100-1, iStartDatep - iStartDatep/100*100);
		Calendar calEndp = Calendar.getInstance();
		calEndp.set(iEndDatep/10000, iEndDatep/100-iEndDatep/10000*100-1, iEndDatep - iEndDatep/100*100);
		switch (Constants.arrPeriod[iPeriod]){
		case Constants.PERIOD_BIWEEK:
			Calendar calTempB = (Calendar) calStart.clone();
			int ib = 0;
			while (calEndp.compareTo(calTempB)>=0) {
				calTempB.add(Calendar.DAY_OF_YEAR, 14);
				ib++;
			}
			lYear1Amt = lAmount * ib;
			break;
		case Constants.PERIOD_YEAR:
			lYear1Amt = lAmount;
			break;
		case Constants.PERIOD_WEEK:
			Calendar calTempW = (Calendar) calStart.clone();
			int iw = 0;
			while (calEndp.compareTo(calTempW)>=0) {
				calTempW.add(Calendar.DAY_OF_YEAR, 7);
				iw++;
			}
			lYear1Amt = lAmount * iw;
			break;
		case Constants.PERIOD_QUARTER:
			Calendar calTempQ = (Calendar) calStart.clone();
			int iq = 0;
			while (calEndp.compareTo(calTempQ)>=0) {
				calTempQ.add(Calendar.MONTH, 3);
				iq++;
			}
			lYear1Amt = lAmount * iq;
			break;
		case Constants.PERIOD_TENMONTH:
			Calendar calTempT = (Calendar) calStart.clone();
			int it = 0;
			while (calEndp.compareTo(calTempT)>=0 && it < 10) {
				calTempT.add(Calendar.MONTH, 1);
				it++;
			}
			lYear1Amt = lAmount * it;
			break;
		default :
			Calendar calTempM = (Calendar) calStart.clone();
			int im = 0;
			while (calEndp.compareTo(calTempM)>=0) {
				calTempM.add(Calendar.MONTH, 1);
				im++;
			}
			lYear1Amt = lAmount * im;
		}
		Double dTemp = lYear1Amt * (100+dRPI+dRPIp)/100;
		lYear2Amt = dTemp.intValue();
		dTemp = lYear2Amt * (100+dRPI+dRPIp)/100;
		lYear3Amt = dTemp.intValue();

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
	public void generateLine(DateRange[] arrPeriods, BudgetParameters objParams){
		long lAmtInc=0;
		int iDateInc = 0;
		Calendar dtBudgetStart = Calendar.getInstance();
		Calendar dtStart = Calendar.getInstance();
		Calendar dtBudgetEnd = Calendar.getInstance();
		int iBudgetStart = objParams.getStartDate();
		int iBudgetEnd = objParams.getEndDate();
		/*
		 * set calendar for budget start
		 */
		int iYear = iBudgetStart/10000;
		int iMonth = (iBudgetStart- iYear*10000)/100-1;
		int iDay = iBudgetStart - iYear*10000-(iMonth+1)*100;
		dtBudgetStart.set(iYear, iMonth,iDay);
		/*
		 * set Calendar for budget end
		 */
		iYear = iBudgetEnd/10000;
		iMonth = (iBudgetEnd - iYear*10000)/100-1;
		iDay = iBudgetEnd - iYear*10000-(iMonth+1)*100;
		dtBudgetEnd.set(iYear,iMonth, iDay);
		switch ( objParams.getPeriod()) {
		case Constants.PERIODWEEKLY:
			/*
			 * move the start date to the first week boundary on or after the line start date
			 */
			dtStart.setTime(BudgetValuesWindow.weekStart.getTime());
			while (startDate.after(dtStart)) {
				dtStart.add(Calendar.DAY_OF_YEAR, 7);
			}
			iDateInc = 7;
			switch (Constants.arrPeriod[iPeriod]) {
			case Constants.PERIOD_WEEK:
				lAmtInc = lAmount;
				break;
			case Constants.PERIOD_BIWEEK:
				lAmtInc = lAmount;
				iDateInc = 14;
				break;
			case Constants.PERIOD_MONTH:
			case Constants.PERIOD_TENMONTH:
				lAmtInc = lAmount;
				iDateInc = -1;
				break;
			case Constants.PERIOD_QUARTER:
				lAmtInc = lAmount;
				iDateInc = -3;
				break;
			default :
				lAmtInc = lAmount;
				iDateInc = -12;
			}
			break;
		case Constants.PERIODBIWEEKLY:
			/*
			 * move the start date to the first bi-week boundary on or after the line start date
			 */
			dtStart.setTime(BudgetValuesWindow.weekStart.getTime());
			while (startDate.after(dtStart)) {
				dtStart.add(Calendar.DAY_OF_YEAR, 14);
			}
			iDateInc = 14;
			switch (Constants.arrPeriod[iPeriod]) {
			case Constants.PERIOD_WEEK:
				lAmtInc = lAmount*2;
				break;
			case Constants.PERIOD_BIWEEK:
				lAmtInc = lAmount;
				break;
			case Constants.PERIOD_MONTH:
			case Constants.PERIOD_TENMONTH:
				lAmtInc = lAmount;
				iDateInc = -1;
				break;
			case Constants.PERIOD_QUARTER:
				lAmtInc = lAmount;
				iDateInc = -3;
				break;
			default :
				lAmtInc = lAmount;
				iDateInc = -12;
			}
			break;
		case Constants.PERIODMONTHLY:
			dtStart.setTime(dtBudgetStart.getTime());
			dtStart.set(Calendar.DAY_OF_MONTH, 1);
			while (startDate.after(dtStart)) {
				dtStart.add(Calendar.MONTH, 1);
			}
			iDateInc = -1;
			switch (Constants.arrPeriod[iPeriod]) {
			case Constants.PERIOD_WEEK:
				lAmtInc = lAmount*52/12;
				break;
			case Constants.PERIOD_BIWEEK:
				lAmtInc = lAmount*26/12;
				break;
			case Constants.PERIOD_MONTH:
			case Constants.PERIOD_TENMONTH:
				lAmtInc = lAmount;
				break;
			case Constants.PERIOD_QUARTER:
				lAmtInc = lAmount;
				iDateInc = -3;
				break;
			default :
				lAmtInc = lAmount;
				iDateInc = -12;
			}
			break;
		case Constants.PERIODANNUAL:
			iDateInc = -12;
			dtStart = Calendar.getInstance();
			dtStart.setTime(startDate.getTime());
            lAmtInc = switch (Constants.arrPeriod[iPeriod]) {
                case Constants.PERIOD_WEEK -> lAmount * 52;
                case Constants.PERIOD_BIWEEK -> lAmount * 26;
                case Constants.PERIOD_MONTH -> lAmount * 12;
                case Constants.PERIOD_TENMONTH -> lAmount * 10;
                case Constants.PERIOD_QUARTER -> lAmount * 4;
                default -> lAmount;
            };
			
			break;
		}
		arraySize = arrPeriods.length;
		setNumPeriods(arraySize);
		Double dTemp;
		JDateField jdtStart = new JDateField(Main.cdate);
		int i = 0;
		int iCount = 0;
		if (objParams.getPeriod()==Constants.PERIODANNUAL) {
			if (!Objects.equals(Constants.arrPeriod[iPeriod], Constants.PERIOD_YEAR) &&
					!dtBudgetStart.equals(startDate)) {
				/*
				 * If budget is Annual, the line period is not annual and the start date
				 * does not match budget start - Pro rata the amount based on start dates
				 */
				DateRange drTemp = new DateRange(dtBudgetStart.getTime(),dtBudgetEnd.getTime());
				int iBudgetDays = drTemp.getNumDays();
				DateRange drTemp2 = new DateRange(dtStart.getTime(),dtBudgetEnd.getTime());
				int iLineDays = drTemp2.getNumDays();
				lAmtInc = lAmtInc *iLineDays/iBudgetDays;
			}
			arrlYear1[i] = lAmtInc;
			dTemp = lAmtInc*(100.00+ objParams.getRPI()+dRPI)/100;
			arrlYear2[i] = dTemp.intValue();
			dTemp = arrlYear2[i]*(100.00+ objParams.getRPI()+dRPI)/100;
			arrlYear3[i] = dTemp.intValue();			
		}
		else {
			while (i< arraySize) {
				arrlYear1[i] = 0;
				arrlYear2[i] = 0;
				arrlYear3[i] = 0;
				jdtStart.setDate(dtStart.getTime());
				if (!(Constants.arrPeriod[iPeriod].equals(Constants.PERIOD_TENMONTH) && iCount >9)) {			
					if (arrPeriods[i].containsInt(jdtStart.getDateInt())){
						arrlYear1[i] = lAmtInc;
						dTemp = lAmtInc*(100.00+ objParams.getRPI()+dRPI)/100;
						arrlYear2[i] = dTemp.intValue();
						dTemp = arrlYear2[i]*(100.00+ objParams.getRPI()+dRPI)/100;
						arrlYear3[i] = dTemp.intValue();
						iCount++;
						if (iDateInc < 0)
							dtStart.add(Calendar.MONTH, -iDateInc);
						else
							dtStart.add(Calendar.DAY_OF_YEAR, iDateInc);
					}
				}
				i++;
	
			}
		}
	}

	/*
	 * Used to add generated line to parent line
	 */
	public void addChild(int iYear,boolean bInitialised, long[] arrChild) {
		switch (iYear) {
		case 1:
			if (arrlYear1 == null)
				arrlYear1 = new long[arrChild.length];
			if (!bInitialised)
                Arrays.fill(arrlYear1, 0L);
			for (int i=0;i<arrlYear1.length;i++) 
				arrlYear1[i] += arrChild[i];
			break;
		case 2:
			if (arrlYear2 == null)
				arrlYear2 = new long[arrChild.length];
			if (!bInitialised)
                Arrays.fill(arrlYear2, 0L);
			for (int i=0;i<arrlYear2.length;i++) 
				arrlYear2[i] += arrChild[i];
			break;
		default:
			if (arrlYear3 == null)
				arrlYear3 = new long[arrChild.length];
			if (!bInitialised)
                Arrays.fill(arrlYear3, 0L);
			for (int i=0;i<arrlYear3.length;i++) 
				arrlYear3[i] += arrChild[i];
			break;
		}
		
		
	}

}