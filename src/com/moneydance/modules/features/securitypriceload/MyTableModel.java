package  com.moneydance.modules.features.securitypriceload;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;
import java.util.SortedMap;

import javax.swing.table.DefaultTableModel;

import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.modules.features.mrbutil.MRBDebug;

public class MyTableModel extends DefaultTableModel {
	private Parameters objParms;
    private SortedMap<String,Double> mapPrices;
    private SortedMap<String,Double> mapHigh;
    private SortedMap<String,Double> mapLow;
    private SortedMap<String,Long> mapVolume;
    private List<Entry<String,CurrencyType>> listCurrencies;
    private List<Entry<String,Integer>> listDates;
    private List<Entry<String,DummyAccount>> listAccounts;
    private List<Entry<String,Double>> listCurrent;
    private CurrencyType ctBaseCurrency;
	private boolean[] arrSelect;
	private MRBDebug objDebug = Main.debugInst;
	private static String[] arrColumns = {"Select","Ticker","Name","Last Update","Last Price","New Price","High","Low","Volume"};

	public MyTableModel(Parameters objParmsp,SortedMap<String,Double> mapPricesp,
			SortedMap<String,Double> mapHighp,
			SortedMap<String,Double> mapLowp,
			SortedMap<String,Long> mapVolumep,
			SortedMap<String, Double> mapCurrentp,
			SortedMap<String,Integer> mapDatesp, 
			SortedMap<String,DummyAccount> mapAccountsp,
			SortedMap<String,CurrencyType> mapCurrenciesp){
		super();
		objParms = objParmsp;
		mapPrices = mapPricesp;
		mapHigh = mapHighp;
		mapLow = mapLowp;
		mapVolume = mapVolumep;
		listCurrent = new ArrayList<Entry<String,Double>>(mapCurrentp.entrySet());
		listDates = new ArrayList<Entry<String,Integer>>(mapDatesp.entrySet());
		listAccounts = new ArrayList<Entry<String,DummyAccount>>(mapAccountsp.entrySet());
		listCurrencies = new ArrayList<Entry<String, CurrencyType>>(mapCurrenciesp.entrySet());
		arrSelect = new boolean[mapCurrentp.size()];
		for (int i=0;i<arrSelect.length;i++)
			arrSelect[i] = false;
		ctBaseCurrency = Main.context.getCurrentAccountBook()
				.getCurrencies()
				.getBaseType();
	}
	public void ResetData(SortedMap<String, Double> mapCurrentp,
			SortedMap<String,Integer> mapDatesp, SortedMap<String,DummyAccount> mapAccountsp,
			SortedMap<String,CurrencyType> mapCurrenciesp){
		listCurrent = new ArrayList<Entry<String,Double>>(mapCurrentp.entrySet());
		listDates = new ArrayList<Entry<String,Integer>>(mapDatesp.entrySet());
		listAccounts = new ArrayList<Entry<String,DummyAccount>>(mapAccountsp.entrySet());
		listCurrencies = new ArrayList<Entry<String, CurrencyType>>(mapCurrenciesp.entrySet());
		for (int i=0;i<arrSelect.length;i++)
			arrSelect[i] = false;
	}
	@Override
	public int getRowCount() {
		int iRows;
		if (listAccounts == null)
			iRows = 0;
		else
			iRows = listAccounts.size();
		if (!(listCurrencies == null))
			iRows +=listCurrencies.size();
		return iRows;
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
			return 9;
	}	
	@Override
	public String getColumnName(int c) {
		return arrColumns[c];
	}
	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {
		
		String strDec = "#0.0000";
		int iDec = objParms.getDecimal();
		if (iDec > 0) {
			for (int i=0;i<iDec;i++)
				strDec += "0";
		}
		DecimalFormat dfNumbers = new DecimalFormat(strDec);
		DecimalFormat lfNumbers = new DecimalFormat("#0");
		CurrencyType ctCellCur;
		CurrencyType ctRelative;
		String strKey;
		int iCurrentRow;
		switch (columnIndex) {
		case 0:
			return  arrSelect[rowIndex];
			/*
			 * Ticker
			 */
		case 1:
			if(rowIndex > listAccounts.size())
				iCurrentRow = rowIndex - listAccounts.size();
			else
				iCurrentRow = rowIndex;
			strKey = listCurrent.get(rowIndex).getKey();
			if (strKey.length() > 3) {
				if (strKey.substring(0,3).equals(Constants.CURRENCYID))
					return strKey.substring(3);
			}
			return strKey;
			/*
			 * Account Name
			 */
		case 2:
			strKey = listCurrent.get(rowIndex).getKey();
			objDebug.debug("MyTableModel", "getValueAt", MRBDebug.DETAILED, "strKey="+strKey);
			if (strKey.length() > 3) {
				if (strKey.substring(0,3).equals(Constants.CURRENCYID)){
					iCurrentRow = rowIndex - listAccounts.size();
					return "Cur:"+listCurrencies.get(iCurrentRow).getValue().getName(); 
				}
			}
			return  listAccounts.get(rowIndex).getValue().getAccountName();
			/*
			 * last update date
			 */
		case 3:
			return  Main.cdate.format(listDates.get(rowIndex).getValue());
			/*
			 * Last Price
			 */
		case 4:
			strKey = listCurrent.get(rowIndex).getKey();
			if (strKey.length() > 3) {
				if (strKey.substring(0,3).equals(Constants.CURRENCYID)){
					iCurrentRow = rowIndex - listAccounts.size();
					return dfNumbers.format(listCurrent.get(rowIndex).getValue()); 
				}
			}
			ctCellCur = ctBaseCurrency;
			Double dValue = listCurrent.get(rowIndex).getValue();
			if (listAccounts.get(rowIndex).getValue().getDifferentCur()) {
				ctRelative = listAccounts.get(rowIndex).getValue().getRelativeCurrencyType();
//				Double dViewRate = CurrencyUtil.getUserRate(ctBaseCurrency,  ctRelative);
//				dValue *= dViewRate;
				ctCellCur = ctRelative;
			}
			return  ctCellCur.getPrefix()+dfNumbers.format(dValue)+ctCellCur.getSuffix();
		case 5:
			if (mapPrices.get(listCurrent.get(rowIndex).getKey())== null)
				return "0.0";
			return dfNumbers.format(mapPrices.get(listCurrent.get(rowIndex).getKey()));
		case 6:
			if (mapHigh.get(listCurrent.get(rowIndex).getKey())== null)
				return "0.0";
			return dfNumbers.format(mapHigh.get(listCurrent.get(rowIndex).getKey()));
		case 7:
			if (mapLow.get(listCurrent.get(rowIndex).getKey())== null)
				return "0.0";
			return dfNumbers.format(mapLow.get(listCurrent.get(rowIndex).getKey()));
		default:
			if (mapVolume.get(listCurrent.get(rowIndex).getKey())== null)
				return "0";
			return lfNumbers.format(mapVolume.get(listCurrent.get(rowIndex).getKey()));
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
		DecimalFormat dfNumbers = new DecimalFormat("#0.0000");
		if (value == null)
			return;
		if (col ==0) {
			if (mapPrices.get(listCurrent.get(row).getKey())== null)
				return;
			if (dfNumbers.format(mapPrices.get(listCurrent.get(row).getKey())).equals("0.0"))
					return;
			arrSelect [row] = (boolean) value;
		}	
	}
	/*
	 * update line
	 */
	public boolean updateLine(int iRow,int iAsOfDate, boolean bCrntPrice) {
		DummyAccount acct;
		CurrencyType ctTicker;
		CurrencyType ctRelative;
		Double dRate;
		Double dViewRate;
		CurrencySnapshot objSnap;
		if (!arrSelect[iRow])
			return false; // line not selected - do not process
		/*
		 * If no rows > no of accounts it must be a currency 
		 */
		if (iRow >= listAccounts.size()) {
			return updateCurrency(iRow, iAsOfDate, bCrntPrice);
		}
		if (mapPrices.get(listCurrent.get(iRow).getKey())== null)
			return false; // no new price for line - do not process
		acct = listAccounts.get(iRow).getValue();
		ctTicker = acct.getCurrencyType();
		if (ctTicker == null)
			return false;  // no currency - do not process
		ctRelative = acct.getRelativeCurrencyType();
		ctTicker.setEditingMode();
		String strTicker = listCurrent.get(iRow).getKey();
		if(mapPrices.get(strTicker)==null)
			dRate = 0.0;
		else
			dRate = mapPrices.get(strTicker);
		dViewRate = 1.0;
		dRate =1/Util.safeRate(dRate);
		objSnap = ctTicker.setSnapshotInt(iAsOfDate,  dRate,ctRelative);
		if (bCrntPrice)
			ctTicker.setRate(dRate,ctRelative);
		if(mapHigh.get(strTicker)==null)
			dRate = 0.0;
		else {
			dRate = mapHigh.get(strTicker);
			if (ctRelative != null && !ctRelative.equals(ctBaseCurrency)) {
				dRate *= dViewRate;
			}
			dRate = 1/Util.safeRate(dRate);
		}
		objSnap.setDailyHigh(dRate);
		if (mapLow.get(strTicker)==null)
			dRate = 0.0;
		else {
			dRate = mapLow.get(strTicker);
			if (ctRelative != null && !ctRelative.equals(ctBaseCurrency)) {
				dRate *= dViewRate;
			}
			dRate = 1/Util.safeRate(dRate);
		}
		objSnap.setDailyLow(dRate);
		if (mapVolume.get(strTicker)!= null)
			objSnap.setDailyVolume(mapVolume.get(strTicker));
		objSnap.syncItem();
		ctTicker.syncItem();
		arrSelect[iRow] = false;
		return true;
	}
	/*
	 * Update line for currency
	 */
	public boolean updateCurrency(int iRow,int iAsOfDate, boolean bCrntPrice) {
		CurrencyType ctTicker;
		Double dRate;
		CurrencySnapshot objSnap;
		if (!arrSelect[iRow])
			return false; // line not selected - do not process
		if (mapPrices.get(listCurrent.get(iRow).getKey())== null)
			return false; // no new price for line - do not process
		ctTicker = listCurrencies.get(iRow-listAccounts.size()).getValue();
		if (ctTicker == null)
			return false;  // no currency - do not process
		ctTicker.setEditingMode();
		if(mapPrices.get(listCurrent.get(iRow).getKey())==null)
			dRate = 0.0;
		else
			dRate = mapPrices.get(listCurrent.get(iRow).getKey());
		objSnap = ctTicker.setSnapshotInt(iAsOfDate,dRate);
		if (bCrntPrice)
			ctTicker.setRate(dRate,null);
		if(mapHigh.get(listCurrent.get(iRow).getKey())==null)
			dRate = 0.0;
		else
			dRate = mapHigh.get(listCurrent.get(iRow).getKey());
		objSnap.setDailyHigh(dRate);
		if (mapLow.get(listCurrent.get(iRow).getKey())==null)
			dRate = 0.0;
		else
			dRate = mapLow.get(listCurrent.get(iRow).getKey());
		objSnap.setDailyLow(dRate);
		if (mapVolume.get(listCurrent.get(iRow).getKey())!= null)
			objSnap.setDailyVolume(mapVolume.get(listCurrent.get(iRow).getKey()));
		objSnap.syncItem();
		ctTicker.syncItem();
		arrSelect[iRow] = false;
		return true;
	}
	  
}
