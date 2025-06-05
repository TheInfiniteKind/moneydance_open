/*
 * Copyright (c) 2020, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.reportwriter;

import java.sql.Date;
import java.util.SortedMap;
import java.util.TreeMap;

import com.infinitekind.moneydance.model.BudgetItem;

/**
 * Constants used throughout the extension
 * @author Mike Bray
 *
 */
public abstract class Constants {
	/*
	 * General
	 */
	public static final String ABOUT1 = "   Moneydance Report Writer Extension\n";
	public static final String ABOUT2 = "         By Mike Bray (2021)\n";
	public static final String ABOUT3 = "         Build ";
	public static final String ABOUT4 = " Icons used with this extension are supplied by http://icons8.com\n";
	public static final String SELECTEDBLACKIMAGE = "selectedblack.png";
	public static final String SELECTEDLIGHTIMAGE = "selectedlight.png";
	public static final String UNSELECTEDBLACKIMAGE = "unselectedblack.png";
	public static final String UNSELECTEDLIGHTIMAGE = "unselectedlight.png";
	public static final String ABANDONMSG = "Parameters have changed, do you wish to abandon the changes?";
	/*
	 * Program control
	 */
	public static final String PROGRAMNAME = "reportwriter";
	public static final String EXTENSIONNAME = "Report Writer";
	public static final String DATABASEADAPTER = "databaseadapter.xml";
	public static final String DATABASEJAR= "h2-1.4.200.jarsav";
	public static final String DEFAULTPARAMETERFILE = "mrbrwdefault";
	public static final String PARMEXTENSION = ".mbjrp";
	public static final String SELEXTENSION = ".mbjrs";
	public static final String DATAEXTENSION = ".mbjrd";
	public static final String REPORTEXTENSION = ".mbjrr";
	public static final String NODIRECTORY = "none";
	public static final String RESOURCES = "/com/moneydance/modules/features/reportwriter/resources/";
	public static final String VIEWREPORTCMD = "ViewReport";
	public static final String DEFAULTDATABASE = "database.mv.db";
	public static final String REPOSITORY = "http://github.com/mrbray99/moneydanceproduction/blob/main/downloads";
	public static final String SAMPLESFILE = "rwsamples.zip";
	public static final String HELPURL = "https://github.com/mrbray99/moneydanceproduction/wiki/Report-Writer";
	public static final String SHOWHELP = "showhelp";
	public static final String FIRSTRUNDIR = "firstrundir";
/*
 * Preferences
 */
	
	public static final String CRNTFRAMEWIDTH = "framewidth";
	public static final String CRNTFRAMEHEIGHT = "frameheight";
	public static final String DATAPANEWIDTH = "datapanewidth";
	public static final String DATAPANEHEIGHT = "datapaneheight";
	public static final String FIELDPANEWIDTH = "fieldpanewidth";
	public static final String FIELDPANEHEIGHT = "fieldpaneheight";
	public static final String CRNTFRAMEX = "framex";
	public static final String CRNTFRAMEY = "framey";
	public static final String DEBUGLEVEL="debuglevel";
	public static final String CRNTCOLWIDTH = "columnwidth";
	public static final String CRNTBEANCOLWIDTH = "beancolumnwidth";
	public static final String CRNTBEANPANEWIDTH= "crntbeanpanewidth";
	public static final String CRNTBEANPANEHEIGHT= "crntbeanpaneheight";

	/*
 * Screen parameters
 */
	public static final int FRAMEWIDTH = 800;
	public static final int MAINSCREENWIDTH = 1430;
	public static final int MAINSCREENHEIGHT = 510;
	public static final int DATASCREENHEIGHT = 100;
	public static final int DATASCREENWIDTH = 100;
	public static final int DATADATASCREENHEIGHT = 500;
	public static final int DATADATASCREENWIDTH = 500;
	public static final int DATASELECTSCREENHEIGHT = 350;
	public static final int DATASELECTSCREENWIDTH = 800;
	public static final int DATAREPORTSCREENHEIGHT = 370;
	public static final int DATAREPORTSCREENWIDTH = 800;
	public static final int FIELDSCREENHEIGHT = 530;
	public static final int FIELDSCREENWIDTH = 530;
	public static final int BEANSCREENWIDTH=600;
	public static final int BEANSCREENHEIGHT=600;
	public static final int[]  DATDEFAULTCOLWIDTH = {100,100,100,100};
	public static final int[]  SELDEFAULTCOLWIDTH = {100,100,100,100};
	public static final int[]  FIELDDEFAULTCOLWIDTH = {100,100};
	public static final int[]  BEANDEFAULTCOLWIDTH = {100,100,50};
	public static final int[]  REPDEFAULTCOLWIDTH = {100,100,100,100,100};
	/*
	 * Window Names
	 */
	public static final String WINSELECTIONDATA = "WINSELECTIONDATA";
	public static final String WINDATADATA = "WINDATADATA";
	public static final String WINREPORTDATA = "WINREPORTDATA";
	/*
	 * not present values
	 */
	public static final String MISSINGSTRING="****no value*****";
	public static final Long MISSINGLONG=-99999999L;
	public static final Integer MISSINGINT=-99999999;
	public static final Date MISSINGDATE=Utilities.getSQLDate(19000101);
	public static final Double MISSINGDOUBLE=-99999999.9;
	public static final String CANCELPRESSED="***cancel***";
	
     /*
     * parameter field names
     */
    public static final String PARMFROMDATE=  "parmfromdate";
    public static final String PARMTODATE=  "parmtodate";
    public static final String PARMTODAY= "parmtoday";
    public static final String PARMSELACCT=  "parmselacct";
    public static final String PARMSELDATES=  "parmseldates";
    public static final String PARMACCOUNTS=  "parmaccounts";
    public static final String PARMASSET=  "parmasset";
    public static final String PARMBANK=  "parmbank";
    public static final String PARMCREDIT=  "parmcredit";
    public static final String PARMLIABILITY=  "parmliability";
    public static final String PARMLOAN=  "parmloan";
    public static final String PARMINACTIVE = "parminactive";
    public static final String PARMINVESTMENT=  "parminvestment";
    public static final String PARMFROMCHEQUE=  "parmfromcheque";
    public static final String PARMTOCHEQUE=  "parmtocheque";
     public static final String PARMSELCAT=  "parmselcat";
    public static final String PARMINCOME=  "parmincome";
    public static final String PARMEXPENSE=  "parmexpense";
    public static final String PARMCATEGORIES=  "parmcategories";
    public static final String PARMSELBUDGET=  "parmselbudget";
    public static final String PARMBUDGET=  "parmbudget";
    public static final String PARMSELCURRENCY=  "parmselcurrency";
    public static final String PARMCURRENCY=  "parmcurrency";
    public static final String PARMSELSECURITY=  "parmselsecurity";
    public static final String PARMSECURITY=  "parmsecurity";
    public static final String PARMSELTRANS=  "parmseltrans";
    public static final String PARMSELINVTRANS=  "parmselinvtrans";
    public static final String PARMCLEARED=  "parmcleared";
    public static final String PARMUNRECON=  "parmunrecon";
    public static final String PARMRECON=  "parmrecon";
    public static final String PARMTRANSFER=  "parmtransfer";
    public static final String PARMINVACCTS=  "parminvaccts";
    public static final String PARMTAGS=  "parmtags";
    public static final String PARMFLDACCT = "parmfldacct";
    public static final String PARMFLDADDR = "parmfldaddr";
    public static final String PARMFLDBUDG = "parmfldbudg";
    public static final String PARMFLDCAT = "parmfldcat";
    public static final String PARMFLDCUR = "parmfldcur";
    public static final String PARMFLDSEC = "parmfldsec";
    public static final String PARMFLDLOTS = "parmfldlots";
    public static final String PARMFLDCURR = "parmfldcurr";
    public static final String PARMFLDSECP = "parmfldsecp";
    public static final String PARMFLDBUDGI = "parmfldbnudgi";
    public static final String PARMFLDTRAN = "parmfldtran";
    public static final String PARMFLDINVTRAN = "parmfldinvtran";
    public static final String PARMFLDREM = "parmfldrem";
    public static final String PARMLASTDB="parmlastdb";


    /*
     * Lists
     */
	public static String[] DELIMITERS = {",",".","#","|","Tab",";",":"};
    /*
     * types
     */
	public enum ReportType {DATABASE, SPREADSHEET, CSV}
	/*
	 * Table to link budget intervals to a string
	 */
	public static final SortedMap<Integer, String> intervaltypes;
	static {
		intervaltypes = new TreeMap<>();
		intervaltypes.put(BudgetItem.INTERVAL_ANNUALLY, "Annually");
		intervaltypes.put(BudgetItem.INTERVAL_BI_MONTHLY, "Bi-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_BI_WEEKLY, "Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_DAILY, "Daily");
		intervaltypes.put(BudgetItem.INTERVAL_MONTHLY, "Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_NO_REPEAT, "No Repeat");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_ANNUALLY, "Once Annually ");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_BI_MONTHLY,
				"Once Bi-Monthly");
		intervaltypes
				.put(BudgetItem.INTERVAL_ONCE_BI_WEEKLY, "Once Bi-Weekly ");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_MONTHLY, "Once Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_SEMI_ANNUALLY,
				"Once Semi-Annually");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_SEMI_MONTHLY,
				"Once Semi-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_TRI_MONTHLY,
				"Once Tri-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_TRI_WEEKLY,
				"Once Tri-Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_WEEKLY, "Once Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_SEMI_ANNUALLY, "Semi-Annually");
		intervaltypes.put(BudgetItem.INTERVAL_SEMI_MONTHLY, "Semi-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_TRI_MONTHLY, "Tri-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_TRI_WEEKLY, "Tri-Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_WEEKLY, "Weekly");
	}
	public static String[] INTROTEXT = {"**Welcome to the Report Writer extension by Mike Bray**::",
			"This extension takes the data in your Moneydance file and outputs it into easy to use files. These files can be in Comma Separated Value format, an Excel workbook or an SQL Database.::",
			"Before the extension can be used you need to tell it where you will store the parameters and the data output.  These can all be the same folder.::",
			"To make best use of the extension it is important that you read the Help information. To access this click on the Question Mark at the bottom of the screen and click on 'Show Help'.::",
			"If you have any questions please post to the General Moneydance Public Discussion and mention me (Mike Bray) and Report Writer in the title of the post.::",
			"Regards::",
			"Mike Bray::"};
}
