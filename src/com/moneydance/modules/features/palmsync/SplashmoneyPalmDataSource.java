package com.moneydance.modules.features.palmsync;

import com.moneydance.apps.md.model.*;
import com.syncbuilder.storage.expense.Record;
import com.syncbuilder.storage.expense.payment;

import java.io.*;
import java.util.*;

public class SplashmoneyPalmDataSource 
  extends PalmDataSource 
{
  private Main ext;
  private PalmAccount palmAccts[] = null;
  private Vector transactions;
  private RootAccount root;
  private Resources rr;
  private PalmTxn lastTxnForAccount = null;
  private File lastAccountFile = null;
    
  public SplashmoneyPalmDataSource() { }

  public String toString() {
    return "SplashMoney";
  }
  
  /** Prepares this object to synchronize with the PocketMoney application. 
      If the user cancelled the operation, this returns false. */
  public boolean initialize(RootAccount root, Resources rr, Main ext)
    throws Exception
  {
    this.root = root;
    this.rr = rr;
    this.ext = ext;

    File qifDir = new File(root.getParameter("PalmSync.qifdir"),".");
    while(!qifDir.exists() || !qifDir.canRead()) {
      if(!showDirectoryConfig(root, rr, ext))
        return false;
      qifDir = new File(root.getParameter("PalmSync.qifdir"),".");
    }
    
    readAccounts();

    boolean allMappingsExist = true;
    for(int i=0; palmAccts!=null && i<palmAccts.length; i++) {
      if(palmAccts[i].getSyncAccount()==null)
        allMappingsExist = false;
    }
    
    if(!allMappingsExist) {
      // need to show the mapping/configuration window
      // if the user cancels that window, then synchronization won't happen
      if(!showAcctConfig(root, rr, ext))
        return false;
    }

    return true;
  }

  /** Displays a window that lets the user choose the synchronization directory.
      Returns false if the user cancels the window. */
  private boolean showDirectoryConfig(RootAccount root, Resources rr, Main ext) {
    SplashmoneyDirConfig dialog = new SplashmoneyDirConfig(ext, rr, root);
    dialog.setVisible(true);
    if(dialog.wasCanceled()) return false;
    return true;
  }

  private void readAccounts()
    throws Exception
  {
    QIFParser parser = new QIFParser(root, getID());
    String[] acctNames = parser.getSplashAccountNames();
    if(acctNames==null) acctNames = new String[0];
    PalmAccount palmAccts[] = new PalmAccount[acctNames.length];
    for(int i=0; i<palmAccts.length; i++) {
      Account acct =
        root.getAccountById(root.getIntParameter("PalmSync."+getID()+"."+
                                                 acctNames[i]+".syncAccount", -1));
      palmAccts[i] = new PalmAccount(acctNames[i], acct, getID());
    }
    this.palmAccts = palmAccts;
  }

  /** Displays a window that lets the user select the account mapping for
      the SplashMoney accounts. Returns false if the user cancels the window. */
  private boolean showAcctConfig(RootAccount root, Resources rr, Main ext) {
    SplashmoneyAcctConfig dialog = new SplashmoneyAcctConfig(ext, this, palmAccts, rr, root);
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

    if(!showDirectoryConfig(root, rr, ext))
      return false;
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
    
  public PalmTxn[] getNewTransactions(PalmAccount acc) {
    QIFParser qifParser = new QIFParser(root, getID());
    PalmTxn txns[] = qifParser.getTransactionsForAccount(acc);
    if(txns!=null && txns.length>0) {
      lastTxnForAccount = txns[txns.length-1];
      lastAccountFile = qifParser.getFileForAccount(acc);
    } else {
      lastTxnForAccount = null;
      lastAccountFile = null;
    }
    return txns;
  }

  /** Returns an identifier unique to this data source. */
  public String getID() {
    return "splashmny";
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
  
  /** This is called when a transaction is accepted (or rejected)
      by the user into moneydance.  If requiresAutoFilter() returns
      false, then this method should do something that keeps track
      of which transactions have already been accepted.
  */
  public void transactionWasAbsorbed(PalmTxn txn) {
    // if this was the last transaction for the current account, reset the
    // QIF file for this account.
    if(txn!=null && txn==lastTxnForAccount) {
      try {
        lastAccountFile.delete();
      } catch (Exception e) {
        System.err.println("Error resetting QIF file: "+e);
        e.printStackTrace(System.err);
      }
    }
  }
}
