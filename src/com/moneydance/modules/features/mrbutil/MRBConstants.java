package com.moneydance.modules.features.mrbutil;
/**
 * Defines Constant Values
 * @author Mike Bray
 
 */

public abstract class MRBConstants {
	/**
	 * Transaction table default screen width
	 */
	public static final int TRANSCREENWIDTH = 1000;
	/**
	 * Transaction table default screen depth
	 */
	public static final int TRANSCREENDEPTH = 600;
	/**
	 * Parameter file name
	 */
	public static final String PARAMETERFILE = "MRBPreferences.dict";
	public static final String NEWPARAMETERFILE = "MRBPreferences.dict2";
	/*
	 * default file name for local language
	 */
	public static final String LOCALEFILE = "/com/moneydance/modules/features/mrbutil/strings/MRBLocale_en.dict";
	/**
	 * Program name for parameters
	 */
	public static final String PROGRAMNAME = "mrbutil";
	/**
	 * Key for report viewer window width
	 */
	public static final String REPORTWIDTH = "rptscreenwidth";
	/**
	 * Key for report viewer window depth
	 */
	public static final String REPORTDEPTH = "rptscreenheight";
	/**
	 * Key for transaction viewer window width
	 */
	public static final String TRANSWIDTH = "transscreenwidth";
	/**
	 * Key for transaction viewer window depth
	 */
	public static final String TRANSDEPTH = "transscreendepth";
	/**
	 * Constants for MRBUtil Labels
	 */
	public static final String LL_AVAILABLE = "available_items";
	public static final String LL_INCLUDED = "included_items";
	public static final String LL_TT_SCROLL ="tt_scroll_pane";
	public static final String LL_TT_ADD ="tt_add_selected";
	public static final String LL_BTN_SEL ="btn_Sel";
	public static final String LL_BTN_DES ="btn_Des";
	public static final String LL_TT_REMOVE ="tt_remove_selected";
	public static final String LL_TT_SHOW ="tt_show_selected";
	public static final String LL_SELECT ="select_accounts_categories";
	/**
	 * Select panel types
	 */
	public static final Integer SPT_MISSING = 0;
	public static final Integer SPT_SELECT= 1;

}
