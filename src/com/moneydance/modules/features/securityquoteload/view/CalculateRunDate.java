/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
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
 * 
 */
package com.moneydance.modules.features.securityquoteload.view;

import java.util.Calendar;

import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;

public class CalculateRunDate {
	String runType;
	String runParam;
	int lastRun;
	int nextRun;
	int today;
	int lastDayOfWeek;
	int todayDayOfWeek;
	int lastDayOfMonth;
	int dayOfMonth;
	int todayDayOfMonth;
	int todayFirstDayMonth;
	int todayLastDayMonth;
	int todayLastDayMonthDay;
	int todayYear;
	int todayMonth;
	MRBDebug debugInst = Main.debugInst;

	Calendar.Builder builder;
	Calendar tempDate;
	public CalculateRunDate(String runTypep,String runParamp,String lastRunp){
		runType = Main.preferences.getString(Constants.PROGRAMNAME+"."+runTypep,"");
		runParam = Main.preferences.getString(Constants.PROGRAMNAME+"."+runParamp,"");
		lastRun = Main.preferences.getInt(Constants.PROGRAMNAME+"."+lastRunp,0);
		debugInst.debug("CalculateRunDate", "Constructor", MRBDebug.DETAILED, "Params "+runType+" "+runParam+" "+lastRun);                

		today = DateUtil.getStrippedDateInt();
		todayYear = today/10000;
		todayMonth = (today-(today/10000)*10000)/100;
		builder = new Calendar.Builder();
		builder.setInstant(DateUtil.convertIntDateToLong(lastRun));
		tempDate = builder.build();
		lastDayOfWeek = tempDate.get(Calendar.DAY_OF_WEEK); // 1 to 7
		lastDayOfMonth = tempDate.get(Calendar.DAY_OF_MONTH); // 1 to 28,29,30 or 31
		builder.setInstant(DateUtil.convertIntDateToLong(today));
		tempDate = builder.build();
		todayDayOfWeek = tempDate.get(Calendar.DAY_OF_WEEK); //1 to 7
		todayDayOfMonth = tempDate.get(Calendar.DAY_OF_MONTH); // 1 to 28,29,30 or 31
		todayFirstDayMonth = DateUtil.firstDayInMonth(today); // date of first day yyyymmdd
		todayLastDayMonth = DateUtil.lastDayInMonth(today); // date of last day yyyymmdd
		todayLastDayMonthDay= todayLastDayMonth - (Math.round(todayLastDayMonth/100)*100);
		switch (runType){
		case Constants.RUNDAILY :
			calcDaily();
			break;
		case Constants.RUNWEEKLY :
			calcWeekly();
			break;
		case Constants.RUNMONTHLY :
			calcMonthly();
			break;
		case Constants.RUNQUARTERLY :
			calcQuarterly();
			break;
		case Constants.RUNYEARLY :
			calcYearly();
			break;
		}
		
	}
	public int getDate(){
		return nextRun;
	}
	private void calcDaily(){
		if (lastRun == today)
			nextRun = DateUtil.incrementDate(today, 0, 0, 1);
		else
			nextRun = today;
	}
	private void calcWeekly() {
		int startDate;	
		int dayOfWeek = 1;
		if (runParam.isEmpty())
			runParam = Constants.SCHDAY1;
		boolean lastWeek = false;
		if (lastRun < DateUtil.firstDayInWeek(today))
			lastWeek = true;
		String paramStart = Constants.SCHDAY1.substring(0, Constants.SCHDAY1.length()-1);
		if (runParam.startsWith(paramStart)) 
		      dayOfWeek = Integer.parseInt(runParam.substring(runParam.length()-1));
		else 
			dayOfWeek = 1;
		debugInst.debug("CalculateRunDate", "calcWeekly", MRBDebug.DETAILED, "Today "+today+" Day of Week "+dayOfWeek);                
		/*
		 * Check for missed run
		 */
		if(lastRun < DateUtil.incrementDate(DateUtil.firstDayInWeek(today),0,0,-7)) {
			debugInst.debug("CalculateRunDate", "calcWeekly", MRBDebug.DETAILED, "Set to today W1");                
			nextRun = today;
			return;
		}	
		if (lastWeek && lastDayOfWeek < dayOfWeek) {
			debugInst.debug("CalculateRunDate", "calcWeekly", MRBDebug.DETAILED, "Set to today W2");                
			nextRun = today;
			return;
		}
		if (lastRun < today && dayOfWeek == todayDayOfWeek){
			debugInst.debug("CalculateRunDate", "calcWeekly", MRBDebug.DETAILED, "Set to today W3");                
			nextRun = today;
			return;
		}
		startDate = today;
		if (lastRun == today && dayOfWeek <= todayDayOfWeek){
			startDate = DateUtil.incrementDate(startDate,0,0,1);
		}
		builder.setInstant(DateUtil.convertIntDateToLong(startDate));
		tempDate = builder.build();
		int i=0;
		while (i<7){
			if (tempDate.get(Calendar.DAY_OF_WEEK) == dayOfWeek)
				break;
			i++;
			tempDate.add(Calendar.DAY_OF_MONTH, 1);
		}
		nextRun = DateUtil.convertCalToInt(tempDate);
		debugInst.debug("CalculateRunDate", "calcWeekly", MRBDebug.DETAILED, "Set to "+nextRun);                
	}
	private void calcMonthly() {
		int startDate;
		int firstMonday;
		int lastFriday;
		if (runParam.isEmpty())
			runParam=Constants.SCHMONTHDAY+"01";
		builder.setInstant(DateUtil.convertIntDateToLong(todayFirstDayMonth));
		tempDate = builder.build();
		int i=0;
		while (i<7){
			if (tempDate.get(Calendar.DAY_OF_WEEK) == Calendar.MONDAY)
				break;
			i++;
			tempDate.add(Calendar.DAY_OF_MONTH, 1);
		}
		firstMonday = DateUtil.convertCalToInt(tempDate);
		builder.setInstant(DateUtil.convertIntDateToLong(todayLastDayMonth));
		tempDate = builder.build();
		i=0;
		while (i<7){
			if (tempDate.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY)
				break;
			i++;
			tempDate.add(Calendar.DAY_OF_MONTH, -1);
		}
		lastFriday = DateUtil.convertCalToInt(tempDate);
		debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "First Monday "+firstMonday+" Last Friday "+lastFriday);                
		switch (runParam){
		case Constants.SCHFIRSTMON :
			/*
			 * check for missed run
			 */
			if (lastRun < todayFirstDayMonth && today >= firstMonday){
				debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to today M1");                
				nextRun = today;
				return;
			}
			startDate = today;
			if (lastRun >= firstMonday || today > firstMonday) {
				startDate = DateUtil.incrementDate(todayFirstDayMonth,0,1,0);
			}
			builder.setInstant(DateUtil.convertIntDateToLong(startDate));
			tempDate = builder.build();
			i=0;
			while (i<7){
				if (tempDate.get(Calendar.DAY_OF_WEEK) == Calendar.MONDAY)
					break;
				i++;
				tempDate.add(Calendar.DAY_OF_MONTH, 1);
			}
			nextRun = DateUtil.convertCalToInt(tempDate);
			debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to "+nextRun);                
			return;
		case Constants.SCHLASTFRI :
			if (lastRun < todayFirstDayMonth) {
				if (today >= lastFriday) {
					nextRun = today;
					debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to today M2");                
					return;
				}
				int lastRunFriday = lastRun;
				builder.setInstant(DateUtil.convertIntDateToLong(DateUtil.lastDayInMonth(lastRun)));
				tempDate = builder.build();
				i=0;
				while (i<7){
					if (tempDate.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY)
						break;
					i++;
					tempDate.add(Calendar.DAY_OF_MONTH, -1);
				}
				lastRunFriday = DateUtil.convertCalToInt(tempDate);
				if (lastRun < lastRunFriday) {
					nextRun = today;
					debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to today M3");                
				}
				else {
					nextRun = lastFriday;
					debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to last Friday "+nextRun);                
				}
				return;
			}	
			if (today >= lastFriday){
				startDate = DateUtil.incrementDate(today,0,1,0);
				builder.setInstant(DateUtil.convertIntDateToLong(DateUtil.lastDayInMonth(startDate)));
				tempDate = builder.build();
				i=0;
				while (i<7){
					if (tempDate.get(Calendar.DAY_OF_WEEK) == Calendar.FRIDAY)
						break;
					i++;
					tempDate.add(Calendar.DAY_OF_MONTH, -1);
				}
				lastFriday = DateUtil.convertCalToInt(tempDate);
				nextRun = lastFriday;
				debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to next month last friday M4");                
			}
			else {
				nextRun = lastFriday;
				debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to last Friday 2 "+nextRun);                
			}
			return;
		case Constants.SCHLASTDAY:
			if (lastRun < todayFirstDayMonth) {
				int lastRunLastDay = DateUtil.lastDayInMonth(lastRun);
				if (lastRun < lastRunLastDay) {
					debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to today M5");                
					nextRun = today;
				}
				else {
					debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to last day of month "+todayLastDayMonth);                
					nextRun = todayLastDayMonth;
				}
				return;
			}
			if(today == todayLastDayMonth){
				if (lastRun == today) {
					nextRun = DateUtil.lastDayInMonth(DateUtil.incrementDate(today,0,1,0));
					debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to next month "+nextRun);                
				}
			}
			else {
				nextRun = todayLastDayMonth;
				debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to last day of month "+nextRun);
			}
			return;
		default :
			/*
			 * User has specified a specific day
			 * 
			 */
			int runDay=1;
			try {
				runDay = Integer.parseInt(runParam.substring(Constants.SCHMONTHDAY.length()));
			}
			catch (NumberFormatException e){
				e.printStackTrace();
			}
			if (lastRun < todayFirstDayMonth){
				/*
				 * last run was last month
				 */
				if (todayDayOfMonth> runDay){
					/*
					 * runday has been reached. 
					 */
					debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to today M6");                
					nextRun = today;
					return;
				}
				
				if (runDay > getDay(DateUtil.lastDayInMonth(today)))
					runDay = getDay(DateUtil.lastDayInMonth(today));
				nextRun = DateUtil.getDate(todayYear, todayMonth, runDay);
				debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to this month "+nextRun);                
				return;
			}
			/*
			 * a run has already been done this month, we need to set to next month
			 */
			nextRun = DateUtil.incrementDate(today, 0, 1, 0);
			int year = nextRun/10000;
			int month = (nextRun - (nextRun/10000)*10000)/100;
			if (runDay > getDay(DateUtil.lastDayInMonth(nextRun)))
				runDay = getDay(DateUtil.lastDayInMonth(nextRun));
			nextRun = DateUtil.getDate(year, month, runDay);
			debugInst.debug("CalculateRunDate", "calcMonthly", MRBDebug.DETAILED, "Set to next month "+nextRun);                
		}

	}
	private void calcQuarterly (){
		int firstDay = DateUtil.firstDayInQuarter(today);
		int lastDay = DateUtil.lastDayInQuarter(today);
		int lastRunLastDay = DateUtil.lastDayInQuarter(lastRun);
		if (runParam.isEmpty())
			runParam = Constants.SCHQUARTFIRST;
		switch (runParam){
		case Constants.SCHQUARTFIRST :
			/*
			 * check for missed run
			 */
			if (lastRun < firstDay){
				debugInst.debug("CalculateRunDate", "calcQuarterly", MRBDebug.DETAILED, "Last run missed");                
				nextRun = today;
				return;
			}
			nextRun = DateUtil.incrementDate(firstDay,0,3,0);
			debugInst.debug("CalculateRunDate", "calcQuarterly", MRBDebug.DETAILED, "Set to "+nextRun);                
			return;
		case Constants.SCHQUARTLAST :
			if (lastRun < firstDay) {
				if (lastRun < lastRunLastDay) {
					nextRun = today;
					debugInst.debug("CalculateRunDate", "calcQuarterly", MRBDebug.DETAILED, "missed run Q1");                
					return;
				}
			}
			if (lastRunLastDay == today)
				nextRun = DateUtil.incrementDate(lastRunLastDay,0,3,0);
			else
				nextRun = lastDay;
			debugInst.debug("CalculateRunDate", "calcQuarterly", MRBDebug.DETAILED, "Set to last day of quarter "+nextRun);                
			return;
		default :
			int runDate=101;
			int runDay = 1;
			int runMonth = 1;
			int todayQuarter;
			int thisQuarterRun;
			int nextQuarterRun;
			int newdate;
			int nextNewDate;
			try {
				runDate = Integer.parseInt(runParam.substring(Constants.SCHQUARTDATE.length()));
			}
			catch (NumberFormatException e){
				e.printStackTrace();
			}
			runMonth = runDate/100;
			runDay = runDate - runMonth*100;
			todayQuarter = DateUtil.firstDayInQuarter(today);
			if (runMonth > 1)
				thisQuarterRun = DateUtil.incrementDate(todayQuarter,0,runMonth-1,0);
			else 
				thisQuarterRun = todayQuarter;
			if (runDay > getDay(DateUtil.lastDayInMonth(thisQuarterRun)))
				newdate = (thisQuarterRun/100)*100 + getDay(DateUtil.lastDayInMonth(thisQuarterRun));
			else
				newdate = (thisQuarterRun/100)*100 + runDay;
			nextQuarterRun = DateUtil.incrementDate(todayQuarter,0,runMonth+2,0);
			if (runDay > getDay(DateUtil.lastDayInMonth(nextQuarterRun)))
				nextNewDate = (nextQuarterRun/100)*100 + getDay(DateUtil.lastDayInMonth(nextQuarterRun));
			else
				nextNewDate = (nextQuarterRun/100)*100 + runDay;
			if (newdate < today) {
				if (lastRun < newdate){
					nextRun = today;
					debugInst.debug("CalculateRunDate", "calcQuarterly", MRBDebug.DETAILED, "Set to today Q2");                
					return;
				}
			}
			else {
				if (lastRun != today) {
					nextRun = newdate;
					debugInst.debug("CalculateRunDate", "calcQuarterly", MRBDebug.DETAILED, "Set to quarter date "+nextRun);                
					return;
				}
			}
			nextRun = nextNewDate;
			debugInst.debug("CalculateRunDate", "calcQuarterly", MRBDebug.DETAILED, "Set to next quarter date "+nextRun);                
			return;
		}		
	}
	private void calcYearly () {
		if (lastRun == 0)
			nextRun = today;
		else
			nextRun =DateUtil.incrementDate(lastRun,1,0,0);
		while ( nextRun < today){
			nextRun = DateUtil.incrementDate(nextRun,1,0,0);
		}
	}
	private int getDay(int date) {
		return date - (date/100)*100;
	}
}
