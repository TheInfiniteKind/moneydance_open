package com.moneydance.modules.features.securityhistoryload;


public class TickerDate {
	private String strTicker;
	private Integer iDate;

	public TickerDate (String strTickerp, int iDatep){
		strTicker = strTickerp;
		iDate = iDatep;
	}
	public TickerDate (String strTickerDate){
		int iSplit = strTickerDate.indexOf(Constants.TICKERDATE);
		if (iSplit < 0) {
			strTicker = strTickerDate;
			iDate = 19000101;
		}
		else {
			strTicker = strTickerDate.substring (0, iSplit);
			iDate = Integer.parseInt(strTickerDate.substring(iSplit+1));
		}
	}
	@Override
	public String toString() {
		return strTicker+Constants.TICKERDATE+iDate.toString();
	}
	public int getDate() {
		return iDate;
	}
	public String getTicker() {
		return strTicker;
	}
}
