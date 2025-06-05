package com.moneydance.modules.features.budgetreport;

import java.awt.Color;


public abstract class Constants {
	public static final String chSeperator = "/";
	/*
	 * Column Headers
	 */
	public static final String TOTALS = "Total";
	public static final String CATEGORY= "Category";
	public static final String TYPE = "Type";
	/*
	 * Internal order for Period Type - note must match internal order on MD Budget Period Type
	 */
	public static final int PERIODWEEKLY = 0;
	public static final int PERIODBIWEEKLY = 1;
	public static final int PERIODMONTHLY = 2;
	public static final int PERIODANNUAL = 3;

 	/*
	 * Type of screen
	 */
	public static final int EXPENSE_SCREEN = 1;
	public static final int INCOME_SCREEN = 2;
	public static final int MISSING= 3;
	public static final int SELECTED= 4;
	/*
	 * Type of line
	 */
	public static final int CHILD_LINE = 1;
	public static final int PARENT_LINE = 2;
	/*
	 * Default file name for report parameters
	 */
	public static final String DEFAULTFILE = "Brparms";
	public static final String CANCELLED = "***Cancelled***";
	public static final String PROGRAMNAME = "mrbbudgetreport";
	public static final String CRNTFRAMEWIDTH = "framewidth";
	public static final String CRNTFRAMEDEPTH = "framedepth";

    /*
	 * Screen Size Parameters
	 */
	public static final int FRAMEWIDTH =800;
	public static final int FRAMEDEPTH = 800;
	public static final int TOPDEPTH = 250;
	public static final int GENSCREENWIDTH = 1000;
	public static final int GENSCREENHEIGHT = 800;
	public static final int GENMINSCREENWIDTH = 600;
	public static final int GENMINSCREENHEIGHT = 300;
	public static final int TOPINSET = 3;
	public static final int BOTTOMINSET = 2;
	public static final int LEFTINSET = 5;
	public static final int RIGHTINSET = 5;
	/*
	 * Generate screen panel sizes
	 */
	public static final int GENBOTHEIGHT = 50;
	public static final int GENMINMIDWIDTH = GENMINSCREENWIDTH-50;
	public static final int GENMINMIDDEPTH = GENMINSCREENHEIGHT-10;
	public static final int GENCATPREFWIDTH = 200;
	public static final int GENCATMINWIDTH = 100;
	public static final int GENAMOUNTWIDTH = 80;
	/*
	 * Flags
	 */
	public static final int KEY_NOT_FOUND = -1;
	/*
	 * Colours
	 */
	public static final Color CLRHEAD = new Color(0xCC, 0xCC, 0xFF);
	public static final Color CLRBUDGET = new Color(0xDF, 0xF8, 0xF7);
	public static final Color CLRACTUAL = new Color(0xF9, 0xE0, 0xF3);
	public static final Color CLRPOSITIVE = Color.WHITE;
	public static final Color CLRNEGATIVE = Color.WHITE;
	public static final Color CLRFGPOSITIVE = Color.BLACK;
	public static final Color CLRFGNEGATIVE = new Color(0xFF, 0x00, 0x00);
}
