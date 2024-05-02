/*

Class: PriceTableModel

 Created: 2008-06-27

Modified: 2011-11-14
 
 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
*/


package com.moneydance.modules.features.priceui.priceEntry;

import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.CurrencyUtil;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.Util;

import javax.swing.table.AbstractTableModel;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;


/**
 * Defines the "table model" from which the JTable in PriceEntryScreen
 * will get its data.
 *
 * @author Tom Edelson
 * 
 */

public class PriceTableModel extends AbstractTableModel {
  
  private Class[] colClasses = new Class[COLUMN_COUNT];
  
  static final int COLUMN_COUNT = 3;
  static final int SECURITY_NAME_COLUMN = 0;
  static final int CURRENT_PRICE_COLUMN = 1;
  static final int NEW_PRICE_COLUMN = 2;
  
  private CurrencyTable currencyTable;
  private String basePrefix = "";
  private String baseSuffix = "";
  private List<SecurityRow> allSecurities = new ArrayList<>();
  
  private static String[] headings = {"Security", "Current Price", "New Price"};
  private char decimalChar = '.';
  
  private class SecurityRow {
    CurrencyType security;
    CurrencyType relativeCurrency;
    String currentPrice;
    Double newPrice;
    
    SecurityRow(CurrencyType security) {
      this.security = security;
      updateCurrentPrice();
    }
    
    void updateCurrentPrice() {
      relativeCurrency = security.getRelativeCurrency();

      double rate = 1 / Util.safeRate(security.getRate(null));
      
      if (relativeCurrency != null) {
        rate = CurrencyUtil.getUserRate(security, relativeCurrency);
        currentPrice = (relativeCurrency.getPrefix() + " " +
                        StringUtils.formatShortRate(rate, decimalChar) +
                        " " + relativeCurrency.getSuffix()).trim();
      } else {
        currentPrice = (basePrefix + " " +
                        StringUtils.formatShortRate(rate, decimalChar) + " " +
                        baseSuffix).trim();
      }
    }
    
    /**
     * Save the new price to the data store for this currency and update the currentPrice accordingly.
     * Returns true if any data was changed;
     */
    boolean applyPrice(int asOfDate, boolean makeCurrent) {
      if (newPrice == null || newPrice == 0) {
        updateCurrentPrice();
        return false;
      }
      
      security.setSnapshotInt(asOfDate, 1 / Util.safeRate(newPrice), relativeCurrency).syncItem();
      if (makeCurrent) {
        if(relativeCurrency!=null && !relativeCurrency.equals(currencyTable.getBaseType())) {
          double viewRateMult = CurrencyUtil.getUserRate(relativeCurrency,
                                                         currencyTable.getBaseType());
          newPrice *= viewRateMult;
        }
        security.setRate(1.0 / newPrice, null);
        security.setParameter("price_date", System.currentTimeMillis());
        security.syncItem();
      }
      newPrice = null;
      updateCurrentPrice();
      return true;
    }
  }
  
  
  
  static final Comparator<SecurityRow> SECURITY_ROW_COMPARATOR = (secRow1, secRow2) -> CurrencyUtil.CURRENCY_NAME_COMPARATOR.compare(secRow1.security, secRow2.security);
  
  
  
  public PriceTableModel(CurrencyTable currencyTable) {
    this.currencyTable = currencyTable;
    CurrencyType baseCurrency = currencyTable.getBaseType();
    basePrefix = baseCurrency.getPrefix();
    baseSuffix = baseCurrency.getSuffix();
    
    for (CurrencyType unit: currencyTable.getAllCurrencies()) {
      if (unit.getCurrencyType() == CurrencyType.Type.SECURITY) {
        allSecurities.add(new SecurityRow(unit));
      }
    }
    
    colClasses[SECURITY_NAME_COLUMN] = CurrencyType.class;
    colClasses[CURRENT_PRICE_COLUMN] = Double.class;
    colClasses[NEW_PRICE_COLUMN] = Double.class;
    
    allSecurities.sort(SECURITY_ROW_COMPARATOR);
  }
  
  /**
   * This is a separate method because, unlike the other things done in
   * initializeData, these may need to be done again.  Namely, after
   * the user has entered new prices and applied them to the data store,
   * we want those new prices to be shown in the "current price" column
   * of our window.
   */
  void loadCurrentPrices() {
    for(SecurityRow row : allSecurities) {
      row.updateCurrentPrice();
    }
    fireTableRowsUpdated(0, allSecurities.size()-1);
  }
  
  
  /**
   * Takes the prices (and other information) entered by the user, and 
   * applies them to (enters them into) the Moneydance data store.
   */
  public void applyPrices(int effectiveDate, boolean setCurrentPrice) {
    int count = 0; // How many new prices were entered?
    for (SecurityRow row : allSecurities) {
      if(row.applyPrice(effectiveDate, setCurrentPrice)) count++;
    }
    
    loadCurrentPrices();
    
    // If any new prices were entered, refresh the view
    fireTableDataChanged();
  }
  
  
  /* dumpData: used for debugging only
     * Not currently used at all.
     */
  
//    void dumpData() {
  //        System.out.println();
  //        for (Object [] row: data) {
  //            CurrencyType currency = (CurrencyType) row [SECURITY_NAME_COLUMN];
  //            System.out.println(currency);
  //            String currPrice = (String) row [CURRENT_PRICE_COLUMN];
  //            System.out.print ("  " + currPrice + "\n\n");
  //            }
  //    }
  
  
  /** 
   * 
   * @return the number of rows in the table
   * 
   */
  
  public int getRowCount() {
    return allSecurities.size();
  }
  
  
  /** 
   * 
   * @return the number of columns in the table
   * 
   */
  
  public int getColumnCount() {
    return COLUMN_COUNT;
  }
  
  
  /**
   * 
   * @param column the table column for which the caller wants to know the
   * heading
   * 
   * @return the column heading to be displayed for the column
   * 
   */
  
  @Override
  
  public String getColumnName (int column) {
    return headings [column];
  }
  
  
  /**
   * 
   * @param column the table column for which the caller wants to know the 
   * class
   * 
   * @return the class of the objects stored in this column of the table
   * 
   */
  
  @Override
  
  public Class getColumnClass (int column) {
    switch(column) {
      case SECURITY_NAME_COLUMN:
        return CurrencyType.class;
      case NEW_PRICE_COLUMN:
        return Double.class;
      case CURRENT_PRICE_COLUMN:
      default:
        return String.class;
    }
  }
  
  
  /**
   * Get the data represented in any one cell of the table, given the 
   * row number and column number.  Used only by Swing.
   * 
   * @param row the row number of the desired cell
   * 
   * @param column the column number of the desired cell
   * 
   * @return the data from the specified cell.  It is returned as an Object,
   * but one should be able to cast it to the type (the Class) returned by the
   * "getColumnClass" method for the specified column number.
   * 
   */
  
  public Object getValueAt(int row, int column) {
    switch(column) {
      case SECURITY_NAME_COLUMN: return allSecurities.get(row).security;
      case CURRENT_PRICE_COLUMN: return allSecurities.get(row).currentPrice;
      case NEW_PRICE_COLUMN: return allSecurities.get(row).newPrice;
      default: return "?";
    }
  }
  
  
  /**
   * Used by JTable to determine whether a given table cell
   * should be made editable or not.
   * 
   * Returns "true" if and only if the cell in question is
   * in the "New Price" column.
   * 
   * @param row row number of cell for which information is desired.
   * @param column column number of cell for which information is desired.
   * @return true if the cell should be editable, false if not.
   */
  @Override
  public boolean isCellEditable (int row, int column) {
    return (column == NEW_PRICE_COLUMN);
  }
  
  /**
   * Called by JTable when a table cell has been edited, to let this
   * "table model" object know the new value, so that it may store that value.
   * 
   * @param value the value to be stored
   * @param row the row in the table whose value this is
   * @param col the column in the table whose value this is
   */
  @Override
  public void setValueAt (Object value, int row, int col) {
    SecurityRow secRow = allSecurities.get(row);
    if (col == NEW_PRICE_COLUMN) {
      if(value==null) {
        secRow.newPrice = null;
      } else if(value instanceof Double) {
        secRow.newPrice = (Double)value;
      } else {
        double d = StringUtils.parseRate(String.valueOf(value), decimalChar);
        secRow.newPrice = d==0 ? null : d;
      }
      fireTableCellUpdated (row, col);
    }
  } // end method setValueAt
  

} // end class PriceTableModel
