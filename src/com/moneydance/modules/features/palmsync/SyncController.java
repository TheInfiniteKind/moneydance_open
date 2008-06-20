/************************************************************\
 *      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.apps.md.model.*;
import java.awt.*;
import java.util.*;
import javax.swing.*;

public class SyncController {

  private Main ext;
  private PalmDataSource source;
  private Resources rr;
  private boolean interactive;

  private PalmAccount accounts[] = null;
  private int currentAccountIdx;
  private boolean hadNewTransactions = false;
  private TransactionWindow currentTxnWin = null;
  
  public SyncController(Main ext, PalmDataSource source, Resources rr, boolean interactive) {
    this.ext = ext;
    this.source = source;
    this.rr = rr;
    this.interactive = interactive;
  }
    
  /** Synchronize transactions between the given palm data source
      and the moneydance. */
  public synchronized void doSync() {
    try {
      if(source.initialize(ext.getRoot(), rr, ext)) {
        accounts = source.getSyncAccounts();
        hadNewTransactions = false;
        currentAccountIdx = -1;
        nextDialog();
      }
    } catch (Exception e) {
      e.printStackTrace(System.err);
      JOptionPane.showMessageDialog(ext.getFrame(), rr.getString("error")+": "+e,
                                    rr.getString("error"),
                                    JOptionPane.INFORMATION_MESSAGE);
    }
  }

  void nextDialog() {
    Point pt = null;
    Dimension dm = null;
    if(currentTxnWin!=null) {
      pt = currentTxnWin.getLocation();
      dm = currentTxnWin.getSize();
      currentTxnWin.setVisible(false);
      currentTxnWin.dispose();
      currentTxnWin = null;
    }
    
    while(true) { // find the next acccount that needs synchronization
      currentAccountIdx++;
      if(currentAccountIdx>=accounts.length) {
        // we are done!
        if(!hadNewTransactions && interactive) {
          JOptionPane.showMessageDialog(ext.getFrame(), rr.getString("no_new_transactions"),
                                        "", JOptionPane.INFORMATION_MESSAGE);
        }
        return;
      }
      
      Account mdAccount = accounts[currentAccountIdx].getSyncAccount();
      if(mdAccount==null) continue;
      
      TransactionSet allTxns = mdAccount.getRootAccount().getTransactionSet();
      
      PalmTxn[] txns = source.getNewTransactions(accounts[currentAccountIdx]);
      if(txns==null || txns.length<=0) continue;

      for(int j=0; j<txns.length; j++) {
        if(txns[j]!=null) txns[j].normalize();
      }
      
      // this is the set of transactions that the transaction window
      // will merge against
      TxnSet mergeSet = allTxns.getTransactionsForAccount(mdAccount);
      
      if(source.requiresAutoFilter()) {
        // need to filter out transactions that this account definitely
        // already has.
        
        // remove all transactions from the auto-match set that did
        // not come from the current palm data source.  The mergeSet is
        // the set of transactions that the user will merge against.
        TxnSet txnSet = allTxns.getTransactionsForAccount(mdAccount);
        String palmSourceID = source.getID();
        String afTagID = "palmsync."+palmSourceID+".aftag";
        String txnSourceID;
        AbstractTxn atxn;
        for(int j=txnSet.getSize()-1; j>=0; j--) {
          atxn = txnSet.getTxnAt(j);
          if(atxn.getTag(afTagID)==null) {
            txnSet.removeTxnAt(j);
            continue;
          }
        }
        
        // eliminate exact matches
        PalmTxn palmTxn;
        String palmTxnID;
        String mdTxnID;
        int numRemoved = 0;
        for(int j=0; j<txns.length; j++) {
          palmTxn = txns[j];
          palmTxnID = source.getTransactionID(palmTxn);
          
          for(int k=txnSet.getSize()-1; k>=0; k--) {
            atxn = txnSet.getTxnAt(k);
            if(palmTxnID.equals(atxn.getTag(afTagID))) {
              txns[j] = null;
              numRemoved++;
              mergeSet.removeTxn(atxn);
              txnSet.removeTxnAt(k);
            }
          }
        }
        
        // if some txns were removed, compress the array
        if(numRemoved>0) {
          PalmTxn newTxns[] = new PalmTxn[txns.length - numRemoved];
          int k = 0;
          for(int j=0; k<newTxns.length && j<txns.length; j++) {
            if(txns[j]!=null)
              newTxns[k++] = txns[j];
          }
          txns = newTxns;
        }
      }
      
      // check again if there are no more transactions after filtering..
      if(txns==null || txns.length<=0) continue;
      
      hadNewTransactions = true;
      boolean isLastSet = (currentAccountIdx == accounts.length - 1);
      
      currentTxnWin = new TransactionWindow(source, accounts[currentAccountIdx],
                                            this, txns, isLastSet, rr, ext, mergeSet);
      if(pt != null && dm != null) {
        currentTxnWin.setLocation(pt);
        currentTxnWin.setSize(dm);
      } else {
        currentTxnWin.center();
      }
      currentTxnWin.setVisible(true);
      return;
    }
  }

}
