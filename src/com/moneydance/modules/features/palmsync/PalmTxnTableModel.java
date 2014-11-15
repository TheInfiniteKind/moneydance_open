/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.syncbuilder.storage.expense.Record;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.util.CustomDateFormat;
import javax.swing.*;
import javax.swing.table.*;
import java.awt.*;
import java.awt.event.*;

public class PalmTxnTableModel
  extends AbstractTableModel
{
        
  private PalmTxn[] transactions;
  private String[] columnNames;
  private Resources rr;
  private boolean DEBUG = true;
  private CustomDateFormat dateFormat = new CustomDateFormat("M/D/Y");
          
  public PalmTxnTableModel(PalmTxn[] records, Resources rr) {
    this.transactions = records;
    this.rr = rr;
    columnNames =  new String[] { rr.getString("date_table_header"), 
                                  rr.getString("desc_table_header"),
                                  rr.getString("category_table_header"),
                                  rr.getString("amount_table_header") };
  }
  
  public PalmTxn[] getTransactions() {
    return transactions;
  }
        
  public PalmTxn getTransaction(int i) {
    if(transactions.length < 1) {
      return null;
    }
    return transactions[i];
  }
        
  public int getColumnCount() {
    return columnNames.length;
  }
        
  public int getRowCount() {
    return transactions.length;
  }

  public void removeTxn(PalmTxn txn) {
    for(int i=transactions.length-1; i>=0; i--) {
      if(transactions[i]==txn)
        removeRow(i);
    }
  }
                                      

  public void removeRow(int row) {
    PalmTxn[] newArray = new PalmTxn[transactions.length-1];
    System.arraycopy(transactions, 0, newArray, 0, row);
    System.arraycopy(transactions, row+1, newArray, row, transactions.length-row-1);
    transactions =  newArray;
    fireTableRowsDeleted(row, row);
  }
        
  public String getColumnName(int col) {
    return columnNames[col];
  }

  public Object getValueAt(int row, int col) {
    switch(col) {
      case 0:
        return dateFormat.format(transactions[row].getDate());
      case 1:
        return transactions[row].getDescription();
      case 2:
        return transactions[row].getCategory();
      case 3:
        return transactions[row].getPalmAccount().getSyncAccount().getCurrencyType().
          format((transactions[row].getAmount()), '.');
      default:
        return "?";
    }
  }

  public boolean isCellEditable(int row, int col) {
    // Note that the data/cell address is constant,
    // no matter where the cell appears onscreen.
    return false;
  }

  /*
   * Don't need to implement this method unless your table's
   * data can change.
  public void setValueAt(Object value, int row, int col) { }
   */
  
}





