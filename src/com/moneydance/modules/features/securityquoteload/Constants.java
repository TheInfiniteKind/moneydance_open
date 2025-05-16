/*
 *  Copyright (c) 2018, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload;

import java.util.prefs.Preferences;
/**
 * Constants used throughout the extension
 * @author Mike Bray
 *
 */
public abstract class Constants {
	/*
	 * General
	 */
	public static final Integer MINIMUMVERSIONNO = 2019;
	public static final String YAHOO ="Yahoo";
	public static final String YAHOOHIST ="Yahoo HD";
	public static final String FT ="FT";
	public static final String FTHIST ="FT HD";
	public static final String ALPHAVAN = "AlphaVantage HD";
	public static final String[] SOURCELITS= {YAHOO,FT,YAHOOHIST,FTHIST,ALPHAVAN};
	public static final String DONOTLOAD ="Do not load";
	public static final Integer YAHOOINDEX = 1;
	public static final Integer FTINDEX = 2;
	public static final Integer YAHOOHISTINDEX = 3;
	public static final Integer FTHISTINDEX = 4;
	public static final Integer ALPHAINDEX= 5;
	public static final Integer[] SOURCELIST= {YAHOOINDEX, FTINDEX, YAHOOHISTINDEX, FTHISTINDEX, ALPHAINDEX};
	public static final String[] AUTOTEXT = {"Manual Only","Daily","Weekly","Monthly","Quarterly","Yearly"};
	public static final String[] HISTORYLIST= {"1 Month","2 Months","3 Months"};
	public static final String[] TIMETEXT = {"At Start Up","02:00","04:00","06:00","08:00","09:00","11:00","13:00","15:00","17:00","19:00","21:00","22:00","23:00","24:00"};
	public static final String CALENDARIMAGE = "calendar.png";
	public static final String SELECTEDBLACKIMAGE = "selectedblack.png";
	public static final String SELECTEDLIGHTIMAGE = "selectedlight.png";
	public static final String UNSELECTEDBLACKIMAGE = "unselectedblack.png";
	public static final String UNSELECTEDLIGHTIMAGE = "unselectedlight.png";
	public static final String QUOTELOADIMAGE = "quote loader.png";
	public static final String MISSINGDATE="19000101T00:00";
	public static final String SECURITYTITLE = "Securities";
	public static final String CURRENCYTITLE = "Exchange Rates";
	public static final String PARAMETERTITLE = "Parameters";
	public static final String JOINTTITLE = "Securities/Exchange Rates";
	public static final String SPLITPERCENT="splitpercent";
	public static final String SELECTALL="Select All Lines";
	public static final String DESELECTALL="Deselect All Lines";
	public static final String SORTCOLUMN="sortcolumn";
	

    /*
	 * Program control
	 */
	public static final String EXCHANGEFILE = "stockexchanges.dict";
	public static final String CURRENCYFILE = "pseudocurrency.dict";
	public static final String PROGRAMNAME = "securityquoteload";
	public static final String RESOURCEPATH = "com/moneydance/modules/features/securityquoteload/resources";
	public static final String PARAMETERFILE1 =  PROGRAMNAME+".bpam";
	public static final String PARAMETERFILE2 = PROGRAMNAME+".bpam2";
	public static enum FILEFOUND {NEW2, NEW1, OLD2, OLD1,NONE};
	public static final String DEBUGLEVEL ="debuglevel";
	public static final String GETQUOTECMD = "getQuote";
	public static final String TIDCMD = "tid";
	public static final String CURRENCYTYPE = "y";
	public static final String LASTPRICEDATETYPE = "ld";
	public static final String STOCKTYPE = "s";
	public static final String SOURCETYPE = "qs";
	public static final String TRADEDATETYPE = "d";
	public static final String PRICETYPE = "p";
	public static final String HIGHTYPE = "ht";
	public static final String LOWTYPE = "lt";
	public static final String VOLUMETYPE = "v";
	public static final String OKTYPE = "ok";
	public static final String ERRTYPE = "err";
	public static final String TOTALTYPE = "n";
	public static final String TRADECURRTYPE = "c";
	public static final String SOURCEYAHOOHIST = "yh";	
	public static final String SOURCEYAHOO = "yahoo";
	public static final String SOURCEFT = "ft";
	public static final String SOURCEFTHIST = "fth";
	public static final String SOURCEALPHA = "alpha";
	public static final String[] SOURCES = {SOURCEYAHOO,SOURCEFT,SOURCEYAHOOHIST,SOURCEFTHIST,SOURCEALPHA};
	public static final Long OVERALLTIMEOUT=20L;
	public static final int TIMEOUTCOUNT=12;
	public static final String SHOWCONSOLECMD = "showconsole";
	public static final String LOADPRICECMD = "loadPrice";
	public static final String LOADHISTORYCMD = "loadHistory";
	public static final String ERRORQUOTECMD = "errorQuote";
	public static final String DONEQUOTECMD = "doneQuote";
	public static final String TIMEOUTCMD = "timeout";
	public static final String CHECKPROGRESSCMD = "checkprogress";
	public static final String STARTQUOTECMD = "startQuote";
	public static final String TESTTICKERCMD = "testticker";
	public static final String RUNAUTOCMD = "runauto";
	public static final String CHECKAUTOCMD = "checkauto";
	public static final String CHECKAUTOSYNC = "checkautosync";
	public static final String AUTODONECMD = "autodone";
	public static final String STANDALONEDONE="standalonedone";
	public static final String MANUALDONECMD = "manualdone";
	public static final String RUNSECONDRUNCMD = "runsecondrun";
	public static final String RUNSTANDALONECMD="runstandalone";
	public static final String STANDALONEREQUESTED="standalonerequested";
	public static final String CLOSEDOWNCMD="closedown";
	public static final int NORUN=0;
	public static final int MANUALRUN = 1;
	public static final int SECAUTORUN = 2;
	public static final int CURAUTORUN = 3;
	public static final int BOTHAUTORUN = 4;
	public static final int STANDALONERUN=5;
	public static final String EXPORTHEADER = "Ticker,AltTicker,Name,Price,AmtChg,PerChg,Date,Volume\r\n";
	public static final String TICKEREXTID="#";
	public enum MAINACTIONS {
		CHANGECURDISPLAY,
		RESETDISPLAY,
		GETCURRENCYRATES,
		CHANGEZERO
	}
	/*
	 * Scheduling parameters
	 */
	public static final String SCHDAY1 = "DAY1";
	public static final String SCHDAY2 = "DAY2";
	public static final String SCHDAY3 = "DAY3";
	public static final String SCHDAY4 = "DAY4";
	public static final String SCHDAY5 = "DAY5";
	public static final String SCHDAY6 = "DAY6";
	public static final String SCHDAY7 = "DAY7";
	public static final String SCHFIRSTMON = "MONTHFM";
	public static final String SCHLASTFRI = "MONTHLF";
	public static final String SCHLASTDAY = "MONTHLD";
	public static final String SCHMONTHDAY = "MONTHDY";
	public static final String SCHQUARTFIRST = "QUARTFIRST";
	public static final String SCHQUARTLAST = "QUARTLAST";
	public static final String SCHQUARTDATE = "QUARTDY";
	/*
	 * screen sizes
	 */
	public static final String CRNTFRAMEWIDTH = "framewidth";
	public static final String CRNTFRAMEDEPTH = "framedepth";
	public static final String CRNTCOLWIDTH = "columnwidth";
	public static final int FRAMEWIDTH = 800;	
	public static final int FRAMEHEIGHT = 800;
	public static final int LOADSCREENHEIGHT = 800;
	public static final String SELECTEDSECURITY= "SEC";
	public static final String SELECTEDCURRENCY= "CUR";
	public static final String SELECTEDSECCUR= "SECCUR";
	public static final String SELECTEDPARAMETER= "PARM";
	/*
	 * auto running
	 */
	public static final String SECRUNMODE = "runmode";
	public static final String CURRUNMODE = "currunmode";
	public static final String MANUALMODE = "manualmode";
	public static final String AUTOMODE = "automode";
	public static final String SERVERTYPE = "servertype";
	public static final String USESTANDALONE = "standalone";
	public static final String SECLASTRUN = "lastrun";
	public static final String CURLASTRUN = "curlastrun";
	public static final String SECNEXTRUN = "secnextrun";
	public static final String CURNEXTRUN = "curnextrun";
	public static final String SECRUNTYPE = "runtype";
	public static final String CURRUNTYPE = "curruntype";
	public static final String SECRUNPARAM = "runparam";
	public static final String CURRUNPARAM = "currunparam";
	public static final String STARTTIME = "starttime";
	public static final String RUNDAILY = "rundaily";
	public static final String RUNWEEKLY = "runweekly";
	public static final String RUNMONTHLY = "runmonthly";
	public static final String RUNQUARTERLY = "runquarterly";
	public static final String RUNYEARLY = "runyearly";
	public static final int RUNSTARTUP = 0;
	public static final int RUN0900 = 1;
	public static final int RUN1100 = 3;
	public static final int RUN1300 = 4;
	public static final int RUN1500 = 5;
	public static final int RUN1700 = 6;
	public static final int RUN1900 = 7;
	public static final int RUN2100 = 8;
	public static final int RUN2200 = 9;
	public static final int RUN2300 = 10;
	public static final int RUN2400 = 11;
	public static final int RUN0200 = 12;
	public static final int RUN0400 = 13;
	public static final int RUN0600 = 14;
	public static final int RUN0800 = 15;
	public static final int[] TIMEVALUES= {RUNSTARTUP,RUN0200,RUN0400,RUN0600,RUN0800,RUN0900,RUN1100,RUN1300,RUN1500,RUN1700,RUN1900,RUN2100,RUN2200,RUN2300,RUN2400};
	public static final int[] TIMESTART = {0,2,4,6,8,9,11,13,15,17,19,21,22,23,24};
	public static final int NUMTABLECOLS = 14; 
	public static final int NUMCURTABLECOLS = 10; 
	public static final int[]  DEFAULTCOLWIDTH = {40,100,100,100,300,80,80,80,80,80,80,80,80,80};
	public static final int[]  DEFAULTCURCOLWIDTH = {40,100,300,80,80,80,80,80,80,80};
	/*
	 * Currency identifier
	 */
	private static final String str7f = String.valueOf('\u007F');
	public static final String CURRENCYID = str7f+str7f+str7f;
	public static final String CURRENCYTICKER = "=X";
    /*
     * task status
     */
    public static final int TASKSTARTED = 1;
    public static final int TASKFAILED = 2;
    public static final int TASKCOMPLETED = 3;
    /*
     * currency table control
     */
	public  enum CurrencyDisplay {
		SAME(0),
		SEPARATE(1);
		private int sourceNum;
		CurrencyDisplay(int sourceNum){
			this.sourceNum = sourceNum;
		}
		public int getNum() {
			return sourceNum;
		}
	};
	public enum SaveAction {SECURITIES,CURRENCIES,BOTH};

    /*
     * source management
     */
    public enum QuoteSource  {
	    FT(FTINDEX),
	    FTHD(FTHISTINDEX),
	    YAHOO(YAHOOINDEX),
	    YAHOOHD(YAHOOHISTINDEX),
		ALPHAVAN(ALPHAINDEX);
	    private Integer source;
	    private String uuid="";
	    QuoteSource(Integer sourceValue){
		    source=sourceValue;
	    }
	    public Integer getSource() {
		    return source;
	    }
	    public String getUuid() {
		    return uuid;
	    }
	    public void setUuid(String uuid) {
		    this.uuid=uuid;
	    }
	    public static QuoteSource findSource(Integer source) {
		    for (QuoteSource qs:QuoteSource.values()) {
			    if ( qs.getSource()==source)
				    return qs;
		    }
		    return null;
			    
	    }
    }
}
