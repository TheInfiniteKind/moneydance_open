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
import java.util.Calendar;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.SortedMap;
import java.util.TreeMap;

import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;

import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.util.DateUtil;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.ExtraFields;
import com.moneydance.modules.features.securityquoteload.HistoryPrice;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.MainPriceWindow;
import com.moneydance.modules.features.securityquoteload.Parameters;

public class SecTableModel extends DefaultTableModel {
	private Parameters params;
	private Calendar cal = Calendar.getInstance();
	private SortedMap<String, SecurityTableLine> accounts;
	private SortedMap<String, SecurityTableLine> savedAccounts;
	private List<Entry<String, SecurityTableLine>> listAccounts;
	private CurrencyType baseCurrency;
	private DecimalFormat numberFormat;
	private DecimalFormatSymbols decimalFormat;
	private Double multiplier;
	private String[] secSources;
	private MainPriceWindow controller;
	private MRBDebug debugInst = Main.debugInst;
	private Boolean includeDonotload = true;
	private static String[] columnNames = { "Select", "Ticker", "Alt Ticker", "Exch Mod", "Name", "Source->>",
			"Last Price", "Price Date", "New Price", "% chg", "Amt chg", "Trade Date", "Trade Currency",
			"Volume" };

	public SecTableModel(Parameters params, SortedMap<String, SecurityTableLine> accounts,
			MainPriceWindow controller) {
		super();
		this.params = params;
		this.controller = controller;
		savedAccounts= new TreeMap<>();
        savedAccounts.putAll(accounts);
		resetIncluded();
		listAccounts = new ArrayList<>(this.accounts.entrySet());
		secSources = params.getSourceArray();
		baseCurrency = Main.context.getCurrentAccountBook().getCurrencies().getBaseType();
		resetNumberFormat();

	}

	public void resetNumberFormat() {
		multiplier = Math.pow(10.0, params.getDecimal());
		StringBuilder strDec = new StringBuilder("#,##0.00");
		int iDec = params.getDecimal() - 2;
		if (iDec > 0) {
            strDec.append("0".repeat(iDec));
		}
		debugInst.debug("SecTableModel", "ResetNumberFormat", MRBDebug.DETAILED, "Decimal Format " + strDec);

		decimalFormat = new DecimalFormatSymbols();
		decimalFormat.setDecimalSeparator(Main.decimalChar);
		if (Main.decimalChar == ',')
			decimalFormat.setGroupingSeparator('.');
		numberFormat = new DecimalFormat(strDec.toString(), decimalFormat);

	}

	public void resetData(SortedMap<String, SecurityTableLine> mapAccounts) {
		if (savedAccounts==null)
			savedAccounts= new TreeMap<>();
		else
			savedAccounts.clear();
        savedAccounts.putAll(mapAccounts);
		for (SecurityTableLine line : savedAccounts.values())
			line.setSelected(false);
		resetIncluded();
		if (listAccounts == null)
			listAccounts = new ArrayList<>(this.accounts.entrySet());
		else {
			listAccounts.clear();
			listAccounts.addAll(this.accounts.entrySet());
		}
		resetNumberFormat();
	}

	public void resetHistory() {
		for (SecurityTableLine line : accounts.values())
			line.setHistory(null);
	}
	public void switchDisplay() {
		includeDonotload = !includeDonotload;
		resetIncluded();
		listAccounts = new ArrayList<>(this.accounts.entrySet());
	}
	public void resetPrices() {
		for (SecurityTableLine priceEntry : savedAccounts.values()) {
			priceEntry.setNewPrice(0.0);
			priceEntry.setTradeDate(0);
			priceEntry.setPercentChg(0.0);
			priceEntry.setAmtChg(0.0);
			priceEntry.setTradeCur("");
			priceEntry.setVolume(null);
		}
		resetIncluded();
		this.fireTableDataChanged();
	}
	public void resetIncluded() {
		if (accounts==null)
			accounts= new TreeMap<>();
		else accounts.clear();
		for (Entry<String, SecurityTableLine> line :savedAccounts.entrySet()) {
			if (line.getValue().getSource()==0 && !line.getValue().getTicker().contains(Constants.TICKEREXTID)) {
				if (includeDonotload)
					accounts.put(line.getKey(),line.getValue());
			}
			else
				accounts.put(line.getKey(),line.getValue());
		}
	}
	@Override
	public int getRowCount() {
		int iRows;
		if (listAccounts == null)
			iRows = 0;
		else
			iRows = listAccounts.size();
		return iRows;
	}

	@Override
	public Class getColumnClass(int c) {
		if (c == 0)
			return Boolean.class;
		return String.class;
	}

	@Override
	public int getColumnCount() {
		return columnNames.length;
	}

	@Override
	public String getColumnName(int c) {
		return columnNames[c];
	}

	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {
		CurrencyType cellCur;
		CurrencyType relativeCur;
		SecurityTableLine rowData = listAccounts.get(rowIndex).getValue();
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
			return rowData.getTicker();
		/*
		 * Alt ticker
		 */
		case 2:
			return rowData.getAlternateTicker();
		/*
		 * Exchange
		 */
		case 3:
			return rowData.getExchange();
		/*
		 * Account Name
		 */
		case 4:
			return rowData.getAccountName();
		/*
		 * Price Source
		 */
		case 5:
			int source = rowData.getSource();
			if (rowData.getTicker().indexOf(Constants.TICKEREXTID)>0)
				return "Copy from primary";
			if (source > -1 && source < secSources.length)
				return secSources[source];
			return secSources[0];
		/*
		 * last price
		 */
		case 6:
			cellCur = baseCurrency;
			Double dValue = rowData.getLastPrice();
			if (rowData.getDifferentCur()) {
				relativeCur = rowData.getRelativeCurrencyType();
				cellCur = relativeCur;
			}
			dValue = Math.round(dValue * multiplier) / multiplier;
			if (dValue.isInfinite())
				dValue = 1.0;
			return cellCur.getPrefix() + numberFormat.format(dValue) + cellCur.getSuffix();
		/*
		 * last Price Date
		 */
		case 7:
			if (rowData.getInError())
				return Main.cdate.format(rowData.getPriceDate()) + "*";
			return Main.cdate.format(rowData.getPriceDate());
		/*
		 * New Price
		 */
		case 8:
			if (rowData.getNewPrice() == null || rowData.getNewPrice() == 0.0)
				return "0" + Main.decimalChar + "0";
			Double newValue = Math.round(rowData.getNewPrice() * multiplier) / multiplier;
			if (newValue.isInfinite())
				newValue = 0.0;
			return numberFormat.format(newValue);
		/*
		 * % Change
		 */
		case 9:
			if (rowData.getPercentChg() == 0.0 || rowData.getPercentChg().isInfinite())
				return "";
			return numberFormat.format(rowData.getPercentChg());
		/*
		 * Amount Changed
		 */
		case 10:
			if (rowData.getAmtChg() == 0.0 || rowData.getAmtChg().isInfinite())
				return "";
			return numberFormat.format(rowData.getAmtChg());
		/*
		 * Trade Date
		 */
		case 11:
			if (rowData.getTradeDate() == null || rowData.getTradeDate() == 0)
				return "";
			String dateString = Main.cdate.format(rowData.getTradeDate());
			if (rowData.getHistory() != null && !rowData.getHistory().isEmpty())
				dateString += "++";
			return dateString;
		/*
		 * trade currency
		 */
		case 12:
			String quoteCurrency = rowData.getTradeCur();
			if (quoteCurrency == null || quoteCurrency.isEmpty())
				return "";
			CurrencyType securityCurrency = rowData.getRelativeCurrencyType();
			if (securityCurrency == null)
				return quoteCurrency;
			if (!securityCurrency.getIDString().equals(quoteCurrency)) {
				return quoteCurrency + "(" + numberFormat.format(rowData.getQuotedPrice()) + ")";
			}
			return rowData.getTradeCur();
		/*
		 * Volume
		 */
		default:
			if (rowData.getVolume() != null) {
				return Long.toString(rowData.getVolume().getVolume());
			}
			return " ";
		}
	}

	@Override
	public boolean isCellEditable(int row, int col) {
		SecurityTableLine rowData = listAccounts.get(row).getValue();
		switch (col) {
		case 2:
		case 3:
            return rowData.getSource() != 0 && rowData.getTicker().indexOf(Constants.TICKEREXTID) <= 0;
		case 5:
                return rowData.getTicker().indexOf(Constants.TICKEREXTID) <= 0;
		case 0:
		case 8:
		case 11:
			return true;
		default:
			return false;
		}
	}

	@Override
	public void setValueAt(Object value, int row, int col) {
		DecimalFormat dfNumbers = new DecimalFormat("#0.0000");
		SecurityTableLine rowData = listAccounts.get(row).getValue();
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
		 * Alternate ticker
		 */
		case 2:
			rowData.setInError(false);
			for (Entry<String,SecurityTableLine> rowTmp :listAccounts){
				if (rowTmp.getKey().equalsIgnoreCase(listAccounts.get(row).getKey()))
					continue;
				if (value instanceof String) {
					if (rowTmp.getValue().getAlternateTicker() == null || rowTmp.getValue().getAlternateTicker().isEmpty()) {
						if (rowTmp.getValue().getTicker().equals((String) value)) {
							debugInst.debug("SecTableModel", "setValueAt", MRBDebug.DETAILED, "duplicate ticker found with "+rowTmp.getKey());
							rowData.setInError(true);
							break;
						}
					} else {
						if (rowTmp.getValue().getAlternateTicker().equals((String) value)) {
							debugInst.debug("SecTableModel", "setValueAt", MRBDebug.DETAILED, "duplicate alternate ticker found with "+rowTmp.getKey());
							rowData.setInError(true);
							break;
						}
					}
				}

			}
			if (rowData.getInError()) {
				JOptionPane.showMessageDialog(null, "Alternate Ticker already exists");
				break;
			}
			rowData.setAlternateTicker((String) value);
			controller.setIsSecDirty(true);
			rowData.setInError(false);
			break;
		/*
		 * Source
		 */
		case 5:

			for (int i = 0; i < secSources.length; i++) {
				if (((String) value).contentEquals(secSources[i])) {
					rowData.setSource(i);
					debugInst.debug("MyTableModel", "setValueAt", MRBDebug.DETAILED,
							"Source updated " + rowData.getTicker() + " " + i);
				}
			}
			controller.setIsSecDirty(true);
			rowData.setInError(false);
			this.fireTableCellUpdated(row, 2);
			break;
		/*
		 * new price
		 */
		case 8: 
			String newValue = ((String) value).replace(Main.decimalChar, '.');
			rowData.setNewPrice(Double.parseDouble(newValue));
			rowData.setAmtChg(rowData.getNewPrice()-rowData.getLastPrice());
			rowData.setPercentChg(((rowData.getNewPrice()-rowData.getLastPrice())/rowData.getLastPrice())*100);
			rowData.setTradeDate(DateUtil.getStrippedDateInt());
			this.fireTableCellUpdated(row, col+1);
			this.fireTableCellUpdated(row, col+2);
			this.fireTableCellUpdated(row, col+3);
			rowData.setInError(false);
			for (Entry<String, SecurityTableLine> entry : listAccounts) {
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
		case 11: 
			int date = Main.cdate.parseInt((String) value);
			rowData.setTradeDate(date);
			rowData.setInError(false);
			for (Entry<String, SecurityTableLine> entry : listAccounts) {
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
		}

	}

	public int getNumAccounts() {
		return listAccounts.size();
	}

	/**
	 * Update all non-zero lines
	 */
	public int selectAll(boolean select) {
		int numChanged = 0;
		for (SecurityTableLine line : accounts.values()) {
			if (line.getNewPrice() != null && line.getNewPrice() != 0.0) {
				line.setSelected(select);
				numChanged++;
			}
		}
		return numChanged;
	}

	/**
	 * Update exchange on all lines
	 */
	public void selectAllExchanges(String exchange) {
		String strKey;
		for (Entry<String, SecurityTableLine> entry : listAccounts) {
			strKey = entry.getKey();
			if (strKey.contains(Constants.TICKEREXTID))
				continue;
			if (exchange.isEmpty()) {
				entry.getValue().setExchange(null);
			} else {
				entry.getValue().setExchange(exchange);
			}
		}
		controller.setIsSecDirty(true);
		return;
	}

	public SortedMap<String, SecurityTableLine> getSecurities() {
		return accounts;
	}

//	public void setExchange(String ticker) {
//		if (accounts.get(ticker)!=null)
//			accounts.get(ticker).setExchange(params.getExchange(ticker));
//	}
	public String getRowType(int row) {
		return Constants.STOCKTYPE;

	}

	public Integer getTickerStatus(String ticker) {
		return accounts.get(ticker) == null ? 0 : accounts.get(ticker).getTickerStatus();
	}

	public SecurityTableLine getRowAccount(int row) {
		return listAccounts.get(row).getValue();

	}

	public CurrencyType getRowCurrency(int row) {
		return null;

	}

	public void setIsDirty(boolean isDirty) {
		controller.setIsSecDirty(isDirty);
	}

	/**
	 * Updates the sources to the same as the given row
	 * 
	 * @param row
	 * @param col
	 */
	public void updateAllSources(int source) {
		for (Entry<String, SecurityTableLine> entry : listAccounts) {
			String key = entry.getKey();
			if (key.contains(Constants.TICKEREXTID))
				continue;
			entry.getValue().setSource(source);
			debugInst.debug("MyTableModel", "setValueAt", MRBDebug.DETAILED,
					"Source updated " + key + " " + source);
		}
		controller.setIsSecDirty(true);
		this.fireTableDataChanged();
	}

	/*
	 * add list of tickers in error on automatic run
	 */
	public void addErrorTickers(List<String> errorTickers) {
		for (String ticker : errorTickers) {
			if (accounts.containsKey(ticker))
				accounts.get(ticker).setInError(true);
		}
	}

	/*
	 * clear ticker errors
	 */
	public void clearErrorTickers() {
		for (SecurityTableLine line : accounts.values())
			line.setInError(false);
	} 

	/*
	 * Update all lines, iterator moved from MainPriceWindow due to concurrency
	 * issues
	 */
	public void updateLines(BufferedWriter exportFile, boolean exportOnly) {
		Iterator<Entry<String,SecurityTableLine>>secLines = listAccounts.iterator();
		while (secLines.hasNext()) {
			SecurityTableLine line = secLines.next().getValue();
			if (line.getSelected()) {
				updateLine(line, exportFile, false);
				line.setSelected(false);
			}
			else
				line.setTickerStatus(0);
			
		}

	}
	
	
	/*
		 * update line
		 */

	public boolean updateLine(SecurityTableLine acct, BufferedWriter exportFile, boolean exportOnly) {
		CurrencyType ctTicker;
		CurrencyType ctRelative = null;
		double dRate;
		double dViewRate = 1.0;
		double dCurRate = 1.0;
		CurrencySnapshot objSnap;
		if (!acct.getSelected())
			return false; // line not selected - do not process
		String ticker = acct.getTicker();
		int tradeDate = acct.getTradeDate();
		if (acct.getNewPrice() == null || acct.getNewPrice() <= 0.0)
			return false; // no new price for line - do not process
		ctTicker = acct.getCurrencyType();
		if (ctTicker == null)
			return false; // no currency - do not process
		ctRelative = acct.getRelativeCurrencyType();
		/*
		 * assume displayed price is in security currency with MD 2019 store straight
		 */
		dRate = acct.getNewPrice();
		dViewRate = 1.0;
		dRate = dRate * dViewRate * dCurRate;
		if (exportFile != null) {
			ExtraFields extra = acct.getVolume();
			String volumeStr = "";
			if (extra != null)
				volumeStr = extra.getVolume().toString();
			String line = ticker + "," +acct.getAlternateTicker()+","+ acct.getAccountName() + "," + dRate + "," +acct.getAmtChg()+","+acct.getPercentChg()+","+ Main.cdate.format(tradeDate)
					+ "," + volumeStr + "\r\n";
			try {
				exportFile.write(line);
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		if (exportOnly)
			return true;
		Double multiplier = Math.pow(10.0, Double.valueOf(params.getDecimal()));
		dRate = Math.round(dRate * multiplier) / multiplier;
		dRate = 1 / Util.safeRate(dRate);
		debugInst.debug("MyTableModel", "updateLine", MRBDebug.DETAILED, "cumulative price " + dRate);
		ctTicker.setEditingMode();
		objSnap = ctTicker.setSnapshotInt(tradeDate, dRate, ctRelative);
		if (acct.getVolume() != null) {
			ExtraFields fields = acct.getVolume();
			if (params.getAddVolume())
				objSnap.setDailyVolume(fields.getVolume());
			if (fields.getHigh() != 0.0) {
				Double rate = fields.getHigh();
				Double viewRate = 1.0;
				rate = rate * viewRate * dCurRate;
				rate = Math.round(rate * multiplier) / multiplier;
				rate = 1 / Util.safeRate(rate);
				objSnap.setDailyHigh(rate);
			}
			if (fields.getLow() != 0.0) {
				Double rate = fields.getLow();
				Double viewRate = 1.0;
				rate = rate * viewRate * dCurRate;
				rate = Math.round(rate * multiplier) / multiplier;
				rate = 1 / Util.safeRate(rate);
				objSnap.setDailyLow(rate);
			}
		}
		int priceDate = DateUtil.convertLongDateToInt(ctTicker.getLongParameter("price_date", 0));
		if (params.isOverridePrice()) {
			ctTicker.setRate(Util.safeRate(dRate), ctRelative);
			synchronized (cal) {
				cal.clear();
				cal.set(tradeDate / 10000, tradeDate / 100 % 100 - 1, tradeDate % 100, 0, 0, 0);
				ctTicker.setParameter("price_date", cal.getTimeInMillis());
			}
		} else {
			if (tradeDate >= priceDate) {
				ctTicker.setRate(Util.safeRate(dRate), ctRelative);
				synchronized (cal) {
					cal.clear();
					cal.set(tradeDate / 10000, tradeDate / 100 % 100 - 1, tradeDate % 100, 0, 0, 0);
					ctTicker.setParameter("price_date", cal.getTimeInMillis());
				}
			}
		}
		objSnap.syncItem();
		ctTicker.syncItem();
//		acct.setSelected(false);
		if (acct.getHistory() != null) {
			List<HistoryPrice> historyList = acct.getHistory();
			ctTicker.setEditingMode();
			for (HistoryPrice priceItem : historyList) {
				dRate = priceItem.getPrice();
				dViewRate = 1.0;
				dRate = dRate * dViewRate * dCurRate;
				dRate = Math.round(dRate * multiplier) / multiplier;
				dRate = 1 / Util.safeRate(dRate);
				objSnap = ctTicker.setSnapshotInt(priceItem.getDate(), dRate, ctRelative);
				if (params.getAddVolume())
					objSnap.setDailyVolume(priceItem.getVolume());
				if (priceItem.getHighPrice() != 0.0) {
					Double rate = priceItem.getHighPrice();
					Double viewRate = 1.0;
					rate = rate * viewRate * dCurRate;
					rate = Math.round(rate * multiplier) / multiplier;
					rate = 1 / Util.safeRate(rate);
					objSnap.setDailyHigh(rate);
				}
				if (priceItem.getLowPrice() != 0.0) {
					Double rate = priceItem.getLowPrice();
					Double viewRate = 1.0;
					rate = rate * viewRate * dCurRate;
					rate = Math.round(rate * multiplier) / multiplier;
					rate = 1 / Util.safeRate(rate);
					objSnap.setDailyLow(rate);
				}
				objSnap.syncItem();
			}
			ctTicker.syncItem();
		}
		// update screen data
		acct.setLastPrice(acct.getNewPrice());
		acct.setPriceDate(acct.getTradeDate());
		acct.setNewPrice(0.0);
		acct.setPercentChg(0.0);
		acct.setAmtChg(0.0);
		acct.setTradeDate(0);
		acct.setTradeCur(null);
		acct.setVolume(null);
		acct.setHistory(null);
		acct.setTickerStatus(0);
		return true;
	}

	/*
	 * Reload current prices
	 *
	 * public void reloadPrices() { SecurityTableLine acct; CurrencyType ctTicker;
	 * for (int i = 0; i < listAccounts.size(); i++) { acct =
	 * listAccounts.get(i).getValue(); ctTicker = acct.getCurrencyType(); /* Get
	 * last price entry
	 *
	 * if (ctTicker != null) { if (!ctTicker.getTickerSymbol().equals("")) {
	 * List<CurrencySnapshot> listSnap = ctTicker.getSnapshots(); int iSnapIndex =
	 * listSnap.size() - 1; CurrencySnapshot ctssLast = listSnap.get(iSnapIndex); if
	 * (ctssLast != null) { acct.setLastPrice(1.0 / ctssLast.getRate()); } } } } }
	 */
}
