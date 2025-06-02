package  com.moneydance.modules.features.securityhistoryload;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;
import java.util.SortedMap;

import javax.swing.table.DefaultTableModel;

import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.modules.features.mrbutil.MRBDebug;


public class MyTableModel extends DefaultTableModel {
	private NewParameters parms;
    private SortedMap<String,Double> mapPrices;
    private SortedMap<String,Double> mapCurrent;
    private SortedMap<String,Double> mapHigh;
    private SortedMap<String,Double> mapLow;
    private SortedMap<String,Long> mapVolume;
    private SortedMap<String,Integer> mapDates;
    private SortedMap<String,CurrencyType> mapCurrencies;
    private SortedMap<String,DummyAccount> mapAccounts;
    private List<Entry<String,Double>> listPrices;
    private CurrencyTable ctCurrencies;
    private CurrencyType ctBaseCurrency;
    private MRBDebug objDebug = Main.debugInst;
    private boolean[] arrSelect;
	private static String[] arrColumns = {"Select","Ticker","Date","Name","Last Update","Last Price","New Price","High","Low","Volume"};

	public MyTableModel(NewParameters objParmsp,SortedMap<String,Double> mapPricesp,
			SortedMap<String,Double> mapHighp,
			SortedMap<String,Double> mapLowp,
			SortedMap<String,Long> mapVolumep,
			SortedMap<String, Double> mapCurrentp,
			SortedMap<String,Integer> mapDatesp, 
			SortedMap<String,DummyAccount> mapAccountsp,
			SortedMap<String,CurrencyType> mapCurrenciesp){
		super();
		parms = objParmsp;
		mapPrices = mapPricesp;
		mapCurrent = mapCurrentp;
		mapHigh = mapHighp;
		mapLow = mapLowp;
		mapVolume = mapVolumep;
		mapDates = mapDatesp;
		mapCurrencies = mapCurrenciesp;
		mapAccounts = mapAccountsp;
		listPrices = new ArrayList<Entry<String,Double>>(mapPricesp.entrySet());
		ctCurrencies = Main.context.getCurrentAccountBook().getCurrencies();
		ctCurrencies.getBaseType();
		arrSelect = new boolean[mapPricesp.size()];
		for (int i=0;i<arrSelect.length;i++)
			arrSelect[i] = false;
		ctBaseCurrency = Main.context.getCurrentAccountBook()
				.getCurrencies()
				.getBaseType();
	}
	public void ResetData(SortedMap<String,Double> mapPricesp,
			SortedMap<String,Double> mapHighp,
			SortedMap<String,Double> mapLowp,
			SortedMap<String,Long> mapVolumep,
			SortedMap<String, Double> mapCurrentp,
			SortedMap<String,Integer> mapDatesp, 
			SortedMap<String,DummyAccount> mapAccountsp,
			SortedMap<String,CurrencyType> mapCurrenciesp){
		mapPrices = mapPricesp;
		mapCurrent = mapCurrentp;
		mapHigh = mapHighp;
		mapLow = mapLowp;
		mapVolume = mapVolumep;
		mapDates = mapDatesp;
		mapCurrencies = mapCurrenciesp;
		mapAccounts = mapAccountsp;
		listPrices = new ArrayList<Entry<String,Double>>(mapPricesp.entrySet());
		for (int i=0;i<arrSelect.length;i++)
			arrSelect[i] = false;
	}
	@Override
	public int getRowCount() {
		if (listPrices == null)
			return 0;
		return listPrices.size();
	}

	@Override
	@SuppressWarnings({ "rawtypes", "unchecked" })
	public Class getColumnClass(int c){
		if (c == 0)
			return Boolean.class;
		return String.class;
	}

		@Override
	public int getColumnCount() {
			return 10;
	}	
	@Override
	public String getColumnName(int c) {
		return arrColumns[c];
	}
	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {
		String strDec = "#0.0000";
		int iDec = parms.getDecimal();
		if (iDec > 0) {
			for (int i=0;i<iDec;i++)
				strDec += "0";
		}
		DecimalFormat dfNumbers = new DecimalFormat(strDec);
		DecimalFormat lfNumbers = new DecimalFormat("#0");
		CurrencyType ctCellCur;
		CurrencyType ctRelative;
		String strKey;
		TickerDate tdTemp;
		String strTicker;
		int iDate;
		switch (columnIndex) {
		/*
		 * Select
		 */
		case 0:
			return  arrSelect[rowIndex];
			/*
			 * Ticker
			 */
		case 1:
			strKey = listPrices.get(rowIndex).getKey();
			tdTemp = new TickerDate(strKey);
			strTicker = tdTemp.getTicker();
			if (strTicker.length() > 3) {
				if (strTicker.substring(0,3).equals(Constants.CURRENCYID))
					return strTicker.substring(3);
			}
			return strTicker;
			/*
			 * Date of price
			 */
		case 2:
			strKey = listPrices.get(rowIndex).getKey();
			tdTemp = new TickerDate(strKey);
			iDate = tdTemp.getDate();
			return  Main.customDateFormat.format(iDate);
			/*
			 * Account/currency name
			 */
		case 3:
			strKey = listPrices.get(rowIndex).getKey();
			tdTemp = new TickerDate(strKey);
			strTicker = tdTemp.getTicker();
			if (strTicker.length() > 3) {
				if (strTicker.substring(0,3).equals(Constants.CURRENCYID)){
					if (!mapCurrencies.containsKey(strTicker))
						return "unknown";

					return "Cur:"+mapCurrencies.get(strTicker).getName();
				}
			}
			if (!mapAccounts.containsKey(strTicker))
				return "unknown";
			return  mapAccounts.get(strTicker).getAccountName();
			/*
			 * Last update date
			 */
		case 4:
			strKey = listPrices.get(rowIndex).getKey();
			tdTemp = new TickerDate(strKey);
			strTicker = tdTemp.getTicker();
			if (!mapDates.containsKey(strTicker))
				return "unknown";
			return  Main.customDateFormat.format(mapDates.get(strTicker).intValue());
			/*
			 * Last Price
			 */
		case 5:
			strKey = listPrices.get(rowIndex).getKey();
			tdTemp = new TickerDate(strKey);
			strTicker = tdTemp.getTicker();
			objDebug.debug("MyTableModel", "getValueAt", MRBDebug.DETAILED, "Ticker"+strTicker);

			if (!mapCurrent.containsKey(strTicker))
				return "unknown";
			if (strTicker.length() > 3)
				if (strKey.substring(0,3).equals(Constants.CURRENCYID)){
					objDebug.debug("MyTableModel", "getValueAt", MRBDebug.DETAILED, "Currency"+strTicker);
					return dfNumbers.format(mapCurrent.get(strTicker));
				}
			ctCellCur = ctBaseCurrency;
			Double dValue = mapCurrent.get(strTicker);
			objDebug.debug("MyTableModel", "getValueAt", MRBDebug.DETAILED, "Security"+strTicker);
			if (mapAccounts.get(strTicker).getDifferentCur()) {
				ctRelative = mapAccounts.get(strTicker).getRelativeCurrencyType();
				ctCellCur = ctRelative;
			}
			return  ctCellCur.getPrefix()+dfNumbers.format(dValue)+ctCellCur.getSuffix();		
			/*
			 * Historic price
			 */
		case 6:
			return  dfNumbers.format(listPrices.get(rowIndex).getValue());
	    	/*
			 * High
			 */
		case 7:
			if (parms.getHighFld().equals(NewParameters.doNotLoad))
				return " ";
			strKey = listPrices.get(rowIndex).getKey();
			if (!mapHigh.containsKey(strKey))
				return "unknown";
			if (mapHigh.get(strKey)== null)
				return "0.0";
			return dfNumbers.format(mapHigh.get(strKey));
			/*
			 * low
			 */
		case 8:
			if (parms.getLowFld().equals(NewParameters.doNotLoad))
				return " ";
			strKey = listPrices.get(rowIndex).getKey();
			if (!mapLow.containsKey(strKey))
				return "unknown";
			if (mapLow.get(strKey)== null)
				return "0.0";
			return dfNumbers.format(mapLow.get(strKey));
			/* 
			 * Volume
			 */
		default:
			if (parms.getVolumeFld().equals(NewParameters.doNotLoad))
				return " ";
			strKey = listPrices.get(rowIndex).getKey();
			if (!mapVolume.containsKey(strKey))
				return "unknown";
			if (mapVolume.get(strKey)== null)
				return "0.0";
			return lfNumbers.format(mapVolume.get(strKey));
		}
	}
	@Override
    public boolean isCellEditable(int row, int col) {
 		if (col ==0)
			return true;
		else
			return false;
    }
	@Override
	public void setValueAt(Object value, int row, int col){
		String strKey;
		TickerDate tdTemp;
		String strTicker;
		DecimalFormat dfNumbers = new DecimalFormat("#0.0000");
		if (value == null)
			return;
		if (col ==0) {
			strKey = listPrices.get(row).getKey();
			tdTemp = new TickerDate(strKey);
			strTicker = tdTemp.getTicker();
			if (mapPrices.get(strKey)== null)
				return;
			if (strTicker.length() > 3) {
				if (strTicker.substring(0,3).equals(Constants.CURRENCYID)){
					if (!mapCurrencies.containsKey(strTicker))
						return;
				}
			}
			else {
				if (!mapAccounts.containsKey(strTicker))
					return;
			}
			if (dfNumbers.format(mapPrices.get(listPrices.get(row).getKey())).equals("0.0"))
					return;
			arrSelect [row] = (boolean) value;
		}	
	}
	/*
	 * update line
	 */
	public boolean updateLine(int iRow) {
		DummyAccount acct;
		CurrencyType ctTicker;
		CurrencyType ctBase = null;
		CurrencyType ctRelative = null;
		Integer iDate;
		Double dRate;
		Double dViewRate;
		CurrencySnapshot objSnap;
		if (!arrSelect[iRow])
			return false; // line not selected - do not process
		/*
		 * If ticker contains Currency ID it must be a currency 
		 */
		String strKey = listPrices.get(iRow).getKey();
		TickerDate tdTemp = new TickerDate (strKey);
		String strTicker = tdTemp.getTicker();

		if (strTicker.length() > 3) {
			if (strTicker.substring(0,3).equals(Constants.CURRENCYID))
				return updateCurrency(iRow);
		}
		acct = mapAccounts.get(tdTemp.getTicker());
		ctTicker = acct.getCurrencyType();
		if (ctTicker == null)
			return false;  // no currency - do not process
		ctRelative = getRelativeCurrency(ctTicker);
		ctBase = ctTicker.getTable().getBaseType();
		ctTicker.setEditingMode();
		dRate = listPrices.get(iRow).getValue();
		iDate = tdTemp.getDate();
		dViewRate = 1.0;
		dRate =1/Util.safeRate(dRate);
		objSnap = ctTicker.setSnapshotInt(iDate,  dRate,ctRelative);
		if (mapDates.containsKey (strTicker)) {
			int iCDate = mapDates.get(strTicker);
			if (iDate >= iCDate) {
				ctTicker.setRate(dRate,ctRelative);
				mapDates.put(strTicker, iDate);
				mapCurrent.put(strTicker, listPrices.get(iRow).getValue());
			}
		}
		if(mapHigh.get(listPrices.get(iRow).getKey())==null)
			dRate = 0.0;
		else {
			dRate = mapHigh.get(listPrices.get(iRow).getKey());
			if (ctRelative != null && !ctRelative.equals(ctBase)) {
				dRate *= dViewRate;
			}
			dRate =1/Util.safeRate(dRate);
		}
		objSnap.setDailyHigh(dRate);
		if (mapLow.get(listPrices.get(iRow).getKey())==null)
			dRate = 0.0;
		else {
			dRate = mapLow.get(listPrices.get(iRow).getKey());
			if (ctRelative != null && !ctRelative.equals(ctBase)) {
				dRate *= dViewRate;
			}
			dRate =1/Util.safeRate(dRate);
		}
		objSnap.setDailyLow(dRate);
		if (mapVolume.get(listPrices.get(iRow).getKey())!= null)
			objSnap.setDailyVolume(mapVolume.get(listPrices.get(iRow).getKey()));
		objSnap.syncItem();
		ctTicker.syncItem();
		arrSelect[iRow] = false;
		return true;
	}
	/*
	 * Update line for currency
	 */
	public boolean updateCurrency(int iRow) {
		CurrencyType ctTicker;
		Double dRate;
		Integer iDate;
		CurrencySnapshot objSnap;
		if (!arrSelect[iRow])
			return false; // line not selected - do not process
		TickerDate tdTemp = new TickerDate(listPrices.get(iRow).getKey());
		String strTicker =tdTemp.getTicker();
		ctTicker = mapCurrencies.get(strTicker);
		if (ctTicker == null)
			return false;  // no currency - do not process
		ctTicker.setEditingMode();
		if(mapPrices.get(listPrices.get(iRow).getKey())==null)
			dRate = 0.0;
		else
			dRate = mapPrices.get(listPrices.get(iRow).getKey());
		iDate = tdTemp.getDate();
		objSnap = ctTicker.setSnapshotInt(iDate,dRate);
		if (mapDates.containsKey (strTicker)) {
			int iCDate = mapDates.get(strTicker);
			if (iDate >= iCDate) {
				ctTicker.setRate(dRate,null);
				mapDates.put(strTicker, iDate);
				mapCurrent.put(strTicker, listPrices.get(iRow).getValue());
			}
		}
		if(mapHigh.get(listPrices.get(iRow).getKey())==null)
			dRate = 0.0;
		else
			dRate = mapHigh.get(listPrices.get(iRow).getKey());
		objSnap.setDailyHigh(dRate);
		if (mapLow.get(listPrices.get(iRow).getKey())==null)
			dRate = 0.0;
		else
			dRate = mapLow.get(listPrices.get(iRow).getKey());
		objSnap.setDailyLow(dRate);
		if (mapVolume.get(listPrices.get(iRow).getKey())!= null)
			objSnap.setDailyVolume(mapVolume.get(listPrices.get(iRow).getKey()));
		objSnap.syncItem();
		ctTicker.syncItem();
		arrSelect[iRow] = false;
		return true;
	}
	  /** 
	   * Get the currency that the given security is priced relative to, if it's not
	   * the base currency
	   */
	  static CurrencyType getRelativeCurrency(CurrencyType curr) {
	    String relCurrID = curr.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR);
	    return relCurrID == null ? null : curr.getBook().getCurrencies().getCurrencyByIDString(relCurrID);
	  }
	    
	/*
	 * Reload current prices
	 */
/*	public void reloadPrices () {
		Account acct;
		
		CurrencyType ctTicker;
		for (int i=0;i<listCurrent.size();i++) {
			TickerDate tdTemp = new TickerDate(listCurrent.get(i).getKey());
			acct = mapAccounts.get(tdTemp.getTicker());
			if (acct != null) {
				ctTicker = acct.getCurrencyType();
		    	/*
		    	 * Get last price entry
		    	 */
		    /*	if (ctTicker != null) {
		    	  if (!ctTicker.getTickerSymbol().equals("")) {
	    			  List<CurrencySnapshot> listSnap = ctTicker.getSnapshots();
		    		  int iSnapIndex = listSnap.size()-1;
			    	  CurrencySnapshot ctssLast = listSnap.get(iSnapIndex);
			    	  if (ctssLast != null) {
			    		  listCurrent.get(i).setValue(1.0/ctssLast.getUserRate());
			    		  }
		    		  }
		    	  }
			}

		}
	}*/
}
