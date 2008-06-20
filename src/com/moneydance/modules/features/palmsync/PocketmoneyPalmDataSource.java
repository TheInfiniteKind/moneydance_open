/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.apps.md.model.*;
import com.syncbuilder.storage.pocketmoney.TransactionRecord;
import com.syncbuilder.storage.pocketmoney.AccountRecord;

import java.net.*;
import java.io.*;
import java.util.*;
import javax.swing.*;
import java.text.*;
import java.awt.*;

public class PocketmoneyPalmDataSource 
  extends PalmDataSource
{
  private Main ext;
  private PalmAccount palmAccts[] = null;
  private Vector transactions;
  private RootAccount root;
  private Resources rr;
  private File pdbDir = null;
  
  public PocketmoneyPalmDataSource( ) { }
    
  /** Prepares this object to synchronize with the PocketMoney application. 
      If the user cancelled the operation, this returns false. */
  public boolean initialize(RootAccount root, Resources rr, Main ext)
    throws Exception
  {
    this.root = root;
    this.rr = rr;
    this.ext = ext;

    File pdbDir = new File(root.getParameter("PalmSync.pdbdir","."));
    File acctFile = new File(pdbDir, "PM-Accounts.pdb");
    while(!pdbDir.exists() || !pdbDir.canRead() ||
          !acctFile.exists() || !acctFile.canRead()) {
      if(!showDirectoryConfig(root, rr, ext))
        return false;
      pdbDir = new File(root.getParameter("PalmSync.pdbdir","."));
      acctFile = new File(pdbDir, "PM-Accounts.pdb");
    }
    
    readAccounts();

    boolean mappingExists = false;
    for(int i=0; palmAccts!=null && i<palmAccts.length; i++) {
      if(palmAccts[i].getSyncAccount()!=null) mappingExists = true;
    }
    
    if(!mappingExists) {
      // need to show the mapping/configuration window
      // if the user cancels that window, then synchronization won't happen
      if(!showConfigWindow(root, rr, ext)) return false;
    }

    readAllTxns();
    
    return true;
  }
     
  public String toString() {
    return "PocketMoney";
  }

  /** Read in the list of accounts. */
  private void readAccounts()
    throws Exception
  {   
    File accountFile = new File(root.getParameter("PalmSync.pdbdir","."), "PM-Accounts.pdb");
    DBParser accountParser = new DBParser(accountFile);
    Vector accounts = accountParser.getPocketmoneyAccountRecords();
    if(accounts==null || accounts.size()<=0)
      throw new Exception(rr.getString("cant_read_accts"));

    palmAccts = new PalmAccount[accounts.size()];
    for(int i = 0; i < accounts.size(); i++) {
      AccountRecord acctRec = (AccountRecord)accounts.elementAt(i);
      Account acct =
        root.getAccountById(root.getIntParameter("PalmSync."+getID()+"."+
                                                 acctRec.account+".syncAccount", -1));
      palmAccts[i] = new PalmAccount(acctRec.account, acct, getID());
    }
  }


  /** Displays a window that lets the user choose the synchronization directory.
      Returns false if the user cancels the window. */
  private boolean showDirectoryConfig(RootAccount root, Resources rr, Main ext) {
    PocketmoneyDirConfig dialog = new PocketmoneyDirConfig(ext, rr, root);
    dialog.setVisible(true);
    if(dialog.wasCanceled()) return false;
    return true;
  }

  /** Displays a window that lets the user select the account mapping for
      the Pocketmoney accounts. Returns false if the user cancels the window. */
  private boolean showAcctConfig(RootAccount root, Resources rr, Main ext) {
    PocketmoneyAcctConfig dialog = new PocketmoneyAcctConfig(ext, this, palmAccts, rr, root);
    dialog.setVisible(true);
    if(dialog.wasCanceled()) return false;
    return true;
  }

  
  public boolean showConfigWindow(RootAccount root, Resources rr, Main ext)
    throws Exception
  {
    this.root = root;
    this.rr = rr;
    this.ext = ext;

    boolean keepChecking = true;
    do {
      if(!showDirectoryConfig(root, rr, ext))
        return false;
      
      // try it out to make sure it works...
      try {
        File pdbDir = new File(root.getParameter("PalmSync.pdbdir","."));
        File acctFile = new File(pdbDir, "PM-Accounts.pdb");
        if(!pdbDir.exists() || !pdbDir.canRead() ||
           !acctFile.exists() || !acctFile.canRead()) {
          JOptionPane.showMessageDialog(ext.getFrame(),
                                        rr.getString("directory_does_not_contain")+
                                        "PM-Accounts.pdb, PM-Transactions.pdb.",
                                        "", JOptionPane.INFORMATION_MESSAGE);
        } else {
          keepChecking = false;
        }
      } catch (Exception e) {
        JOptionPane.showMessageDialog(ext.getFrame(),
                                      rr.getString("directory_does_not_contain")+
                                      "PM-Accounts.pdb, PM-Transactions.pdb.",
                                      "", JOptionPane.INFORMATION_MESSAGE);
      }
    } while(keepChecking);

    readAccounts();
    if(!showAcctConfig(root, rr, ext))
      return false;
    return true;
  }

  /** After initialize has been called, this requests a
      list of palm accounts that can be synchronized with md. */
  public PalmAccount[] getSyncAccounts() {
    return palmAccts;
  }
    
  /** Gets all of the new transactions that are to be synchronized
      with the given account from the list of sync-accounts. */
  public PalmTxn[] getNewTransactions(PalmAccount acc) {
    Vector trans = new Vector();
    TransactionRecord txn;
    String memoStr;
    for(int i = 0; i < transactions.size(); i++) {
      txn = (TransactionRecord)transactions.elementAt(i);
      if(txn.account.equals(acc.getName())) {
        memoStr = (txn.description==null ? "" : txn.description);
        if(!memoStr.startsWith("***ROLLUP") || !memoStr.endsWith("***"))
          trans.addElement(txn);
      }
    }
        
    CurrencyType curr = acc.getSyncAccount().getCurrencyType();
    PalmTxn[] newTxns = new PalmTxn[trans.size()];
    PalmTxn newTxn;
    TransactionRecord rec;
    for(int i = 0; i < newTxns.length; i++) {
      rec = (TransactionRecord)trans.elementAt(i);
      newTxn = new PalmTxn(acc);
      newTxn.setDate(rec.date);
      newTxn.setAmount(Math.round(rec.amount * Math.pow(10, curr.getDecimalPlaces())));
      newTxn.setDescription(rec.description);
      newTxn.setCategory(rec.category);
      newTxn.setTxnID(rec.getID().getID());
      newTxn.setVendor(rec.payee);
      newTxn.setCheckNum(rec.chkNum);
      newTxn.setCleared(rec.cleared);
      newTxns[i] = newTxn;
    }
    return newTxns;
  }


  private void readAllTxns()
    throws Exception
  {
    File transactionFile = new File(root.getParameter("PalmSync.pdbdir","."), "PM-Transactions.pdb");
    DBParser transactionParser = new DBParser(transactionFile);
    transactions = transactionParser.getPocketmoneyTransactionRecords();
  }
    
  /** Returns an identifier unique to this data source. */
  public String getID() {
    return "pocketmny";
  }
  
}





