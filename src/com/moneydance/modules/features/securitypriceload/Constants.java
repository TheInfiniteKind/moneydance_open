package com.moneydance.modules.features.securitypriceload;

public abstract class Constants {
    /*
	 * Screen Size Parameters
	 */
	public static final String PROGRAMNAME = "mrbsecuritypriceload";
	public static final String CRNTFRAMEWIDTH = "framewidth";
	public static final String CRNTFRAMEDEPTH = "framedepth";
	public static final int FRAMEWIDTH = 800;	
	public static final int FRAMEHEIGHT = 800;
	public static final int LOADSCREENWIDTH = 1000;
	public static final int LOADSCREENHEIGHT = 800;
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
	 * Currency identifier
	 */
	private static final String strFF = String.valueOf('\u00FF');
	public static final String CURRENCYID = strFF+strFF+strFF;
	public static final String CURRENCYTICKER = "=X";
}
