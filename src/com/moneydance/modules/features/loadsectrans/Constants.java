package com.moneydance.modules.features.loadsectrans;


public abstract class Constants {
	public static final String PROGRAMNAME = "loadsectrans";
    /*
	 * Screen Size Parameters
	 */
	public static final int FRAMEWIDTH =100;
	public static final int FRAMEHEIGHT = 100;
	public static final int LOADSCREENWIDTH = 800;
	public static final int LOADSCREENHEIGHT = 500;
	/*
	 * Load screen panel sizes
	 */
	public static final int LOADBOTWIDTH = LOADSCREENWIDTH-50;
	public static final int LOADBOTDEPTH = (LOADSCREENHEIGHT)/8;
	public static final int LOADTOPWIDTH = LOADSCREENWIDTH-50;
	public static final int LOADTOPDEPTH = (LOADSCREENHEIGHT)/8;
	public static final int LOADMIDWIDTH = LOADSCREENWIDTH-50;
	public static final int LOADMIDDEPTH = LOADSCREENHEIGHT-LOADTOPDEPTH-LOADBOTDEPTH-50;
	public static final int LOADSELECTPREFWIDTH = 40;
	public static final int LOADSELECTMINWIDTH = 20;
	public static final int LOADCATPREFWIDTH = 200;
	public static final int LOADCATMINWIDTH = 100;
	public static final int LOADAMOUNTWIDTH = 80;
	/*
	 * transaction values
	 */
	public static final char PARENT = 'P';
	public static final char SPLIT = 'S';
	public static final String TAGGEN = "LSTGEN"; 
	public static final String TXNCLEARED = "C";
	public static final String TXNRECONCILED = "R";
	/*
	 * Types of Transactions
	 */
	public static final String SECURITY_INCOME = "Security Income";  
	public static final String SECURITY_COST = "Security Cost";  
	public static final String INVESTMENT_INCOME = "Investment Income";  
	public static final String INVESTMENT_COST = "Investment Cost";
	public static final String INVESTMENT_BUY = "Investment Buy";
	public static final String INVESTMENT_SELL = "Investment Sell";
	public static final String SECURITY_DIVIDEND = "Security Dividend";
	public static final String [] TRANSTYPES = {SECURITY_INCOME,SECURITY_DIVIDEND, SECURITY_COST,
		INVESTMENT_INCOME, INVESTMENT_COST,INVESTMENT_BUY,INVESTMENT_SELL};
	public static final String [] TRANSTYPESNOUNITS = {SECURITY_INCOME,SECURITY_DIVIDEND, SECURITY_COST,
			INVESTMENT_INCOME, INVESTMENT_COST};
	public static final String NEWTRAN = "**new**";
	public static final String NOTICKER = "main";
	public static final String SELECTEDBLACKIMAGE = "selectedblack.png";
	public static final String SELECTEDLIGHTIMAGE = "selectedlight.png";
	public static final String UNSELECTEDBLACKIMAGE = "unselectedblack.png";
	public static final String UNSELECTEDLIGHTIMAGE = "unselectedlight.png";
	/*
	 * preferences keys
	 */
	public static final String PREFLASTDIRECTORY = "lastdirectory";
}
