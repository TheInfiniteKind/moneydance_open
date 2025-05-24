/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload.view;

import java.io.BufferedWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.ArrayList;
//import java.util.ArrayList;
import java.util.Calendar;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.SortedMap;

import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;

import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.util.DateUtil;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.HistoryPrice;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.MainPriceWindow;
import com.moneydance.modules.features.securityquoteload.Parameters;

public class CurTableModel extends DefaultTableModel {
	private Parameters params;
	private Calendar cal = Calendar.getInstance();
	private SortedMap<String, CurrencyTableLine> currencies;
	private List<Entry<String, CurrencyTableLine>> listCurrencies;
	private String[] arrSource;
	private DecimalFormat dfNumbers;
	private DecimalFormatSymbols dfSymbols;
	private Double multiplier;
	private MainPriceWindow controller;
	private MRBDebug debugInst = Main.debugInst;
	private static String[] arrColumns = { "Select", "Ticker", "Name", "Source->>", "Last Price", "Price Date",
			"New Price", "% chg", "Amt chg", "Trade Date" };

	public CurTableModel(Parameters params, SortedMap<String, CurrencyTableLine> currencies,
			MainPriceWindow controller) {
		super();
		this.params = params;
		listCurrencies = new ArrayList<Entry<String, CurrencyTableLine>>(currencies.entrySet());
		arrSource = params.getSourceArray();
		this.currencies = currencies;
		this.controller = controller;
		resetNumberFormat();

	}

	public void resetNumberFormat() {
		multiplier = Math.pow(10.0, Double.valueOf(params.getDecimal()));
		String strDec = "#,##0.00";
		int iDec = params.getDecimal() - 2;
		if (iDec > 0) {
			for (int i = 0; i < iDec; i++)
				strDec += "0";
		}
		debugInst.debug("MyTableModel", "MyTableModel", MRBDebug.DETAILED, "Decimal Format " + strDec);

		dfSymbols = new DecimalFormatSymbols();
		dfSymbols.setDecimalSeparator(Main.decimalChar);
		if (Main.decimalChar == ',')
			dfSymbols.setGroupingSeparator('.');
		dfNumbers = new DecimalFormat(strDec, dfSymbols);

	}

	public void resetData(SortedMap<String, CurrencyTableLine> mapAccounts) {
		if (listCurrencies == null)
			listCurrencies = new ArrayList<Entry<String, CurrencyTableLine>>(mapAccounts.entrySet());
		else{
			listCurrencies.clear();
			listCurrencies.addAll(mapAccounts.entrySet());
		}

		this.currencies = mapAccounts;
		for (CurrencyTableLine line : currencies.values())
			line.setSelected(false);
		resetNumberFormat();
	}

	public void resetHistory() {
		for (CurrencyTableLine line : currencies.values())
			line.setHistory(null);
	}

	public void resetPrices() {
		for (CurrencyTableLine priceEntry : currencies.values()) {
			priceEntry.setNewPrice(0.0);
			priceEntry.setPercentChg(0.0);
			priceEntry.setAmtChg(0.0);
			priceEntry.setTradeDate(0);
		}
		this.fireTableDataChanged();
	}

	@Override
	public int getRowCount() {
		int iRows;
		if (listCurrencies == null)
			iRows = 0;
		else
			iRows = listCurrencies.size();
		return iRows;
	}

	@Override
	@SuppressWarnings({ "rawtypes", "unchecked" })
	public Class getColumnClass(int c) {
		if (c == 0)
			return Boolean.class;
		return String.class;
	}

	@Override
	public int getColumnCount() {
		return arrColumns.length;
	}

	@Override
	public String getColumnName(int c) {
		return arrColumns[c];
	}

	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {

		CurrencyTableLine rowData = listCurrencies.get(rowIndex).getValue();
		switch (columnIndex) {
		/*
		 * Select
		 */
		case 0:
			if (rowData.getNewPrice() == null || rowData.getNewPrice() == 0.0)
				return "";
			return rowData.getSelected();
		/*
		 * Ticker
		 */
		case 1:
			return rowData.getTicker().substring(3);
		/*
		 * Account Name
		 */
		case 2:
			return rowData.getCurrencyName();
		/*
		 * Price Source
		 */
		case 3:
			int source = rowData.getSource();
			;
			if (source > -1 && source < arrSource.length)
				return arrSource[source];
			return arrSource[0];
		/*
		 * last price
		 */
		case 4:
			Double dValue = rowData.getLastPrice();
			if (dValue.isInfinite())
				dValue = 1.0;
			dValue = Math.round(dValue * multiplier) / multiplier;
			return dfNumbers.format(dValue);
		/*
		 * last Price Date
		 */
		case 5:
			if (rowData.getInError())
				return Main.cdate.format(rowData.getPriceDate()) + "*";
			return Main.cdate.format(rowData.getPriceDate());
		/*
		 * New Price
		 */
		case 6:
			if (rowData.getNewPrice() == null || rowData.getNewPrice() == 0.0
					|| rowData.getNewPrice().isInfinite())
				return "0" + Main.decimalChar + "0";
			Double newValue = Math.round(rowData.getNewPrice() * multiplier) / multiplier;
			return dfNumbers.format(newValue);
		/*
		 * % Change
		 */
		case 7:
			if (rowData.getPercentChg() == 0.0 || rowData.getPercentChg().isInfinite())
				return "";
			return dfNumbers.format(rowData.getPercentChg());
		/*
		 * Amount Changed
		 */
		case 8:
			if (rowData.getAmtChg() == 0.0 || rowData.getAmtChg().isInfinite())
				return "";
			return dfNumbers.format(rowData.getAmtChg());

		/*
		 * Trade Date
		 */
		case 9:
			if (rowData.getTradeDate() == null || rowData.getTradeDate() == 0)
				return "";
			String dateString = Main.cdate.format(rowData.getTradeDate());
			if (rowData.getHistory() != null && !rowData.getHistory().isEmpty())
				dateString += "++";
			return dateString;
		default:
			return " ";
		}
	}

	@Override
	public boolean isCellEditable(int row, int col) {
		switch (col) {
		case 0:
		case 3:
		case 6:
		case 9:
			return true;
		default:
			return false;
		}
	}

	@Override
	public void setValueAt(Object value, int row, int col) {
		DecimalFormat dfNumbers = new DecimalFormat("#0.0000");
		CurrencyTableLine rowData = listCurrencies.get(row).getValue();
		if (value == null)
			return;
		switch (col) {
		/*
		 * selected
		 */
		case 0:
			if (rowData.getNewPrice() == null) {
				JOptionPane.showMessageDialog(null, "This line does not have a price");
				return;
			}
			if (dfNumbers.format(rowData.getNewPrice()).equals("0.0"))
				return;
			rowData.setSelected((boolean) value);
			break;
		/*
		 * Source
		 */
		case 3:
			for (int i = 0; i < arrSource.length; i++) {
				if ((String) value == arrSource[i]) {
					rowData.setSource(i);
					debugInst.debug("MyTableModel", "setValueAt", MRBDebug.DETAILED,
							"Source updated " + rowData.getTicker() + " " + i);
				}
			}
			controller.setIsCurDirty(true);
			rowData.setInError(false);
			break;
		/*
		 * new price
		 */
		case 6:
			String newValue = ((String) value).replace(Main.decimalChar, '.');
			rowData.setNewPrice(Double.parseDouble(newValue));
			rowData.setAmtChg(rowData.getNewPrice() - rowData.getLastPrice());
			rowData.setPercentChg(
					((rowData.getNewPrice() - rowData.getLastPrice()) / rowData.getLastPrice()) * 100);
			rowData.setTradeDate(DateUtil.getStrippedDateInt());
			this.fireTableCellUpdated(row, col + 1);
			this.fireTableCellUpdated(row, col + 2);
			this.fireTableCellUpdated(row, col+3);
			rowData.setInError(false);
			for (Entry<String, CurrencyTableLine> entry : listCurrencies) {
				if (!entry.getKey().contains(Constants.TICKEREXTID))
					continue;
				String extTicker = entry.getKey();
				String primTicker = extTicker.substring(0, entry.getKey().indexOf(Constants.TICKEREXTID));
				if (rowData.getTickerStatus() != Constants.TASKCOMPLETED)
					continue;
				if (primTicker.equals(entry.getValue().getTicker())) {
					entry.getValue().setNewPrice(rowData.getNewPrice());
					entry.getValue().setTradeDate(rowData.getTradeDate());
				}
			}
			break;
		/*
		 * Trade Date
		 */
		case 9:
			int date = Main.cdate.parseInt((String) value);
			rowData.setTradeDate(date);
			rowData.setInError(false);
			for (Entry<String, CurrencyTableLine> entry : listCurrencies) {
				if (!entry.getKey().contains(Constants.TICKEREXTID))
					continue;
				String extTicker = entry.getKey();
				String primTicker = extTicker.substring(0, entry.getKey().indexOf(Constants.TICKEREXTID));
				if (rowData.getTickerStatus() != Constants.TASKCOMPLETED)
					continue;
				if (primTicker.equals(rowData.getTicker())) {
					entry.getValue().setTradeDate(rowData.getTradeDate());
				}
			}
			break;
		}

	}

	public int getNumAccounts() {
		return listCurrencies.size();

	}

	/**
	 * Update all non-zero lines
	 */
	public int selectAll(boolean select) {
		int numChanged = 0;
		for (CurrencyTableLine line : currencies.values()) {
			if (line.getNewPrice() != null && line.getNewPrice() != 0.0) {
				line.setSelected(select);
				numChanged++;
			}
		}
		return numChanged;
	}

	public String getRowType(int row) {
		return Constants.STOCKTYPE;

	}

	public Integer getTickerStatus(String ticker) {
		return currencies.get(ticker) == null ? 0 : currencies.get(ticker).getTickerStatus();
	}

	public CurrencyTableLine getRowCurrency(int row) {
		return listCurrencies.get(row).getValue();

	}

	/**
	 * Updates the sources to the same as the given row
	 * 
	 * @param row
	 * @param col
	 */
	public void updateAllSources(int source) {
		for (Entry<String, CurrencyTableLine> entry : listCurrencies) {
			String key = entry.getKey();
			if (key.contains(Constants.TICKEREXTID))
				continue;
			entry.getValue().setSource(source);
			debugInst.debug("MyTableModel", "updateAllSources", MRBDebug.DETAILED,
					"Source updated " + key + " " + source);
		}
		this.fireTableDataChanged();
	}

	/*
	 * add list of tickers in error on automatic run
	 */
	public void addErrorTickers(List<String> errorTickers) {
		for (String ticker : errorTickers) {
			if (currencies.containsKey(ticker))
				currencies.get(ticker).setInError(true);
		}
	}

	/*
	 * clear ticker errors
	 */
	public void clearErrorTickers() {
		for (CurrencyTableLine line : currencies.values())
			line.setInError(false);
	}
	/*
	 * Update all lines, iterator moved from MainPriceWindow due to concurrency
	 * issues
	 */

	public void updateLines(BufferedWriter exportFile, boolean exportOnly) {
		Iterator<Entry<String, CurrencyTableLine>> curLines = listCurrencies.iterator();
		while (curLines.hasNext()) {
			CurrencyTableLine line = curLines.next().getValue();
			if (line.getSelected()) {
				updateLine(line, exportFile, false);
				line.setSelected(false);
			} else
				line.setTickerStatus(0);

		}

	}

	/*
	 * update line
	 */
	public boolean updateLine(CurrencyTableLine line, BufferedWriter exportFile, boolean exportOnly) {
		debugInst.debug("CurTableModel", "updateLine", MRBDebug.DETAILED, "starting currency: " + line.getCurrencyType());
		/*
		 * Update line for currency
		 */
		CurrencyType ctTicker;
		Double dRate;
		CurrencySnapshot objSnap;
		int tradeDate = line.getTradeDate();
		ctTicker = line.getCurrencyType();
		if (ctTicker == null)
			return false; // no currency - do not process
		dRate = line.getNewPrice();
		if (exportFile != null) {
			String exportLine =ctTicker.getIDString() + ",," + line.getCurrencyName() + "," + dRate + ","+line.getAmtChg()+","+line.getPercentChg()+","
					+ Main.cdate.format(tradeDate) + ",0\r\n";
			try {
				exportFile.write(exportLine);
			} catch (IOException e) {
				e.printStackTrace();
			}

		}
		if (exportOnly)
			return true;

    AccountBook book = ctTicker.getBook();

		ctTicker.setEditingMode();

		objSnap = ctTicker.setSnapshotInt(tradeDate, dRate);
		int priceDate = DateUtil.convertLongDateToInt(ctTicker.getLongParameter("price_date", 0));
		if (params.isOverridePrice()) {
			ctTicker.setRate(Util.safeRate(dRate), null);
			synchronized (cal) {
				cal.clear();
				cal.set(tradeDate / 10000, tradeDate / 100 % 100 - 1, tradeDate % 100, 0, 0, 0);
				ctTicker.setParameter("price_date", cal.getTimeInMillis());
			}
		} else {
			if (tradeDate >= priceDate) {
				ctTicker.setRate(Util.safeRate(dRate), null);
				synchronized (cal) {
					cal.clear();
					cal.set(tradeDate / 10000, tradeDate / 100 % 100 - 1, tradeDate % 100, 0, 0, 0);
					ctTicker.setParameter("price_date", cal.getTimeInMillis());
				}
			}
		}
    book.queueModifiedItem(objSnap);

		line.setSelected(false);
		if (line.getHistory() != null) {
			List<HistoryPrice> historyList = line.getHistory();
			for (HistoryPrice priceItem : historyList) {
				dRate = priceItem.getPrice();
				objSnap = ctTicker.setSnapshotInt(priceItem.getDate(), dRate);
        book.queueModifiedItem(objSnap);
			}
		}
		line.setLastPrice(line.getNewPrice());
		line.setPriceDate(line.getTradeDate());
		line.setNewPrice(0.0);
		line.setPercentChg(0.0);
		line.setAmtChg(0.0);
		line.setTradeDate(0);
		line.setTickerStatus(0);
		line.setHistory(null);

		ctTicker.clearEditingMode();
    book.queueModifiedItem(ctTicker);
		debugInst.debug("CurTableModel", "updateLine", MRBDebug.DETAILED, "finished currency: " + ctTicker);
		return true;
	}

	/*
	 * Reload current prices
	 *
	 * public void reloadPrices () { CurrencyTableLine acct; CurrencyType ctTicker;
	 * for (int i=0;i<listCurrencies.size();i++) { acct =
	 * listCurrencies.get(i).getValue(); ctTicker = acct.getCurrencyType(); /* Get
	 * last price entry
	 *
	 * if (ctTicker != null) { if (!ctTicker.getTickerSymbol().equals("")) {
	 * List<CurrencySnapshot> listSnap = ctTicker.getSnapshots(); int iSnapIndex =
	 * listSnap.size()-1; CurrencySnapshot ctssLast = listSnap.get(iSnapIndex); if
	 * (ctssLast != null) { acct.setLastPrice(1.0/ctssLast.getRate()); } } } } }
	 */
}
