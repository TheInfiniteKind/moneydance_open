package com.moneydance.modules.features.budgetgen;

import java.awt.Color;
import java.util.HashMap;
import java.util.Map;

import com.infinitekind.moneydance.model.BudgetItem;

public abstract class Constants {
	/*
	 * Budget Lines
	 */
	public static final String PERIOD_BIWEEK = "Bi-weekly";
	public static final String PERIOD_MONTH = "Monthly";
	public static final String PERIOD_WEEK = "Weekly";
	public static final String PERIOD_QUARTER = "Quarterly";
	public static final String PERIOD_TENMONTH = "Ten Monthly";
	public static final String PERIOD_YEAR = "Annual";
	public static final String [] arrPeriod = {PERIOD_WEEK,PERIOD_BIWEEK,PERIOD_MONTH,PERIOD_QUARTER,PERIOD_TENMONTH,PERIOD_YEAR};
	public static final String chSeperator = "/";
	/*
	 * Internal order for Period Type - note must match internal order on MD Budget Period Type
	 */
	public static final int PERIODWEEKLY = 0;
	public static final int PERIODBIWEEKLY = 1;
	public static final int PERIODMONTHLY = 2;
	public static final int PERIODANNUAL = 3;
	/*
	 * table  to match MD Period TYpe to Line Date Period - second number must match arrPeriod
	 */
	public static final Map<Integer,Integer> mapDatePeriod;
	static
	{
		mapDatePeriod = new HashMap<Integer,Integer>();
		mapDatePeriod.put(PERIODWEEKLY, 0);
		mapDatePeriod.put(PERIODBIWEEKLY, 1);
		mapDatePeriod.put(PERIODMONTHLY, 2);
		mapDatePeriod.put(PERIODANNUAL, 5);
	}
    /*
     * Table to link budget intervals item intervals
     */
    public static final Map<Integer, Integer> intervaltypes;
    static
    {
    	intervaltypes = new HashMap<Integer,Integer>();
		intervaltypes.put (PERIODANNUAL,BudgetItem.INTERVAL_ANNUALLY); 
		intervaltypes.put (PERIODWEEKLY,BudgetItem.INTERVAL_WEEKLY); 
		intervaltypes.put (PERIODBIWEEKLY,BudgetItem.INTERVAL_BI_WEEKLY); 
		intervaltypes.put (PERIODMONTHLY,BudgetItem.INTERVAL_MONTHLY); 
    }
	/*
	 * Types of date periods to determine start and end date
	 */
	public static final String PERIOD_FISCAL = "Fiscal Year";
	public static final String PERIOD_CALENDAR = "Calendar Year";
	public static final String PERIOD_CUSTOM = "Custom";
	public static final String [] PERIODS = new String [] 
			  {PERIOD_FISCAL,PERIOD_CALENDAR ,PERIOD_CUSTOM};
    /*
	 * Screen Size Parameters
	 */
	public static final int FRAMEWIDTH =800;
	public static final int FRAMEDEPTH = 800;
	public static final int TOPDEPTH = 200;
	public static final int BOTDEPTH = 100;
	public static final int ADDSCREENWIDTH = 350;
	public static final int ADDSCREENHEIGHT =300;
	public static final int GENSCREENWIDTH = 1000;
	public static final int GENSCREENHEIGHT = 800;
	/*
	 * Generate screen panel sizes
	 */
	public static final int GENSELECTPREFWIDTH = 40;
	public static final int GENSELECTMINWIDTH = 20;
	public static final int GENCATPREFWIDTH = 200;
	public static final int GENCATMINWIDTH = 100;
	public static final int GENAMOUNTWIDTH = 80;
	/*
	 * Type of screen
	 */
	public static final int EXPENSE_SCREEN = 1;
	public static final int INCOME_SCREEN = 2;
	/*
	 * Type of line
	 */
	public static final int CHILD_LINE = 1;
	public static final int PARENT_LINE = 2;
	/*
	 * Default file name for report parameters
	 */
	public static final String CANCELLED = "***Cancelled***";
	public static final String PREFERENCESNODE = "com.moneydance.modules.features.budgetgen.budgetselectwindow";
	public static final String PROGRAMNAME = "mrbbudgetgen";
	public static final String DEFAULTPARAMETERS="mrbbudgetgen";
	public static final String FRAMEWIDTHKEY = "framewidth";
	public static final String FRAMEDEPTHKEY = "framedepth";
	public static final String GENWIDTHKEY = "genscreenwidth";
	public static final String GENDEPTHKEY = "genscreenheight";
	public static final String FILENAMEPREF = "filename";
	public static final String BUDGETNAMEPREF = "budgetname";
	/*
	 * Flags
	 */
	public static final int KEY_NOT_FOUND = -1;
	public static final int GENERATE = 1;
	public static final int MANUAL = 2;
	public static final int VALUESWINDOW = 1;
	public static final int GENWINDOW=2;
	public static final String NOBUDGET = "No Budget";
	/*
	 * Colours
	 */
	public static final Color ALTERNATECLR = new Color(0xC0, 0xC0, 0xF0);
	public static final Color SELECTEDCLR = new Color(0xFF, 0xFF, 0xCC);
}
