/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.*;

import java.net.*;
import java.io.*;
import java.util.*;
import javax.swing.*;
import java.text.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Vector;
import com.syncbuilder.storage.expense.Record;
import com.syncbuilder.storage.expense.payment;


public class ExpensePalmDataSource
  extends PalmDataSource
{
  private final String expenseAccts[] = { "AmEx", "Cash", "Check", "Credit Card", "MasterCard",
                                          "Prepaid", "VISA", "Unfile" };
  private PalmAccount palmAccts[] = null;
  private Vector transactions = null;
  private RootAccount root = null;
  private Main ext = null;
  private Resources rr = null;

  public ExpensePalmDataSource() { }

  /** Prepares this object to synchronize with the Expense application. 
      If the user cancelled the operation, this returns false. */
  public boolean initialize(RootAccount root, Resources rr, Main ext)
    throws Exception
  {
    this.root = root;
    this.rr = rr;
    this.ext = ext;
    
    getPalmAccounts();

    boolean mappingExists = false;
    for(int i=0; palmAccts!=null && i<palmAccts.length; i++) {
      if(palmAccts[i].getSyncAccount()!=null) mappingExists = true;
    }

    System.err.println("pdbdir: "+root.getParameter("PalmSync.pdbdir"));

    if(!mappingExists || root.getParameter("PalmSync.pdbdir")==null) {
      // need to show the mapping/configuration window
      // if the user cancels that window, then synchronization won't happen
      System.err.println("need to show config window...");
      if(!showConfigWindow(root, rr, ext)) return false;
    }

    String syncDir = root.getParameter("PalmSync.pdbdir",".");
    File theFile = new File(syncDir, "ExpenseDB.pdb");
    
    // read the transactions
    try {
      DBParser parser = new DBParser(theFile);
      transactions = parser.getExpenseRecords();
    } catch (com.syncbuilder.storage.DatabaseException e) {
      throw new Exception("File Selected not a valid Expense PDB File: " + e);
    }
    return true;
  }

  public String toString() {
    return "Expense";
  }
  
  /** Displays a configuration window.
      Returns false if the user cancels the window. */
  public boolean showConfigWindow(RootAccount root, Resources rr, Main ext) {
    this.root = root;
    this.rr = rr;
    this.ext = ext;

    getPalmAccounts();

    boolean keepChecking = true;
    do {
      ExpenseConfigDialog dialog = 
        new ExpenseConfigDialog(ext, this, palmAccts, rr, root);
      dialog.setVisible(true);
      if(dialog.wasCanceled()) return false;
      
      // try it out to make sure it works...
      try {
        File pdbDir = new File(root.getParameter("PalmSync.pdbdir","."));
        File acctFile = new File(pdbDir, "ExpenseDB.pdb");
        if(!pdbDir.exists() || !pdbDir.canRead() ||
           !acctFile.exists() || !acctFile.canRead()) {
          JOptionPane.showMessageDialog(ext.getFrame(),
                                        rr.getString("directory_does_not_contain")+
                                        "ExpenseDB.pdb.",
                                        "", JOptionPane.INFORMATION_MESSAGE);
        } else {
          keepChecking = false;
        }
      } catch (Exception e) {
        JOptionPane.showMessageDialog(ext.getFrame(),
                                      rr.getString("directory_does_not_contain")+
                                      "ExpenseDB.pdb.",
                                      "", JOptionPane.INFORMATION_MESSAGE);
      }
    } while(keepChecking);

    return true;
  }
  
  
  private synchronized void getPalmAccounts() {
    if(palmAccts!=null) return;
    
    // if the account mapping has not yet been made or is incomplete, 
    // show a configuration window.
    palmAccts = new PalmAccount[expenseAccts.length];
    for(int i=0; i<expenseAccts.length; i++) {
      Account mdAccount = 
        root.getAccountById(root.getIntParameter("PalmSync.ExpenseAccount."+
                                                 expenseAccts[i]+".syncAccount",-1));
      palmAccts[i] = new PalmAccount(expenseAccts[i], mdAccount, getID());
    }
  }    
    
  public PalmAccount[] getSyncAccounts() {
    getPalmAccounts();
    return palmAccts;
  }

  /** Get any new transactions that are associated with the given account. */    
  public PalmTxn[] getNewTransactions(PalmAccount acc) {
    String accName = acc.getName();
    Vector trans = new Vector();
    Record rec;
    CurrencyType curr = acc.getSyncAccount().getCurrencyType();
    for(int i = 0; i < transactions.size(); i++) {
      rec = (Record)transactions.elementAt(i);
      if(rec.payment.getName().equals(accName) &&
         rec.amount != null && curr.parse(rec.amount, '.') != 0) {
        trans.addElement(transactions.elementAt(i));
      }
    }
    
    PalmTxn[] newTxns = new PalmTxn[trans.size()];
    PalmTxn palmTxn;
    String amtStr;
    for(int i = 0; i < newTxns.length; i++) {
      palmTxn = new PalmTxn(acc);
      rec = (Record)trans.elementAt(i);
      amtStr = rec.amount;

      char decimalChar = '.';
      boolean foundit = false;
      for(int j = 0; !foundit && j < amtStr.length() ; j++) {
        switch(amtStr.charAt(j)) {
          case ',':
            decimalChar = ',';
            foundit = true;
            break;
          case '.':
            decimalChar = '.';
            foundit = true;
            break;
        }
      }
      
      palmTxn.setCategory(rec.type.getName());
      palmTxn.setVendor(rec.vendor);
      palmTxn.setTxnID(rec.getID().getID());
      palmTxn.setDate(rec.date);
      palmTxn.setAmount(-curr.parse(amtStr, decimalChar));
      palmTxn.setMemo(rec.note);
      newTxns[i] = palmTxn;
    }
    return newTxns;
  }

  /** If this returns true, all transactions that are received from this
      data source will be subject to filtering.  Transactions that have
      already been added to Moneydance will not be presented to the user.
      If this returns false then the data source is counted on to do its
      own filtering of already-accepted transactions.
  */
  public boolean requiresAutoFilter() {
    return true;
  }
  
  /** Returns an identifier unique to this data source. */
  public String getID() {
    return "expense";
  }
  
}
