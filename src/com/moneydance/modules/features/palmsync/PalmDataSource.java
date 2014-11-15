/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.awt.*;
import com.moneydance.apps.md.controller.Common;
import com.moneydance.apps.md.controller.Util;
import com.infinitekind.util.StringUtils;

import javax.swing.event.*;
import javax.swing.*;
import java.net.*;
import java.io.*;
import java.util.*;
import java.text.*;
import java.awt.*;
import com.infinitekind.moneydance.model.RootAccount;
import com.infinitekind.util.CustomDateFormat;

abstract class PalmDataSource {

  private CustomDateFormat dateFormat = new CustomDateFormat("y.m.d");
  
  /** Tell the data source to prepare itself for synchronizing.
      returns false if it was unable to initialize itself. */
  public abstract boolean initialize(RootAccount root, Resources rr, Main ext)
    throws Exception;
  
  /** Tell the data source to display a configuration window.
      Returns false if the user cancels the window. */
  public abstract boolean showConfigWindow(RootAccount root, Resources rr, Main ext)
    throws Exception;
  
  /** After initialize has been called, this requests a
      list of palm accounts that can be synchronized with md. */
  public abstract PalmAccount[] getSyncAccounts();
    
  /** Gets all of the new transactions that are to be synchronized
      with the given account from the list of sync-accounts. */
  public abstract PalmTxn[] getNewTransactions(PalmAccount acc);

  /** Returns an identifier unique to this data source. */
  public abstract String getID();

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
  }

  /** Return a unique ID for the given transaction.  The ID must
      be unique across all transactions that come from this data
      source and are in the account of this transaction.
      Transactions with the same ID, data source, and account are
      considered identical and are automatically filtered if
      the requiresAutoFilter() method returns true.
      The default implementation should be overridden by subclasses
      if there are specific items that should be in the ID string.
  */
  public String getTransactionID(PalmTxn palmTxn) {
    return getID()+':'+
      dateFormat.format(palmTxn.getDate())+':'+
      encode(palmTxn.getCheckNum())+':'+
      encode(palmTxn.getDescription())+':'+
      encode(palmTxn.getMemo())+':'+
      encode(palmTxn.getVendor())+':'+
      encode(palmTxn.getCategory())+':'+
      palmTxn.getAmount()+':'
      +encode(palmTxn.getPalmAccount().getName())+':';
  }

  /** Encode a string for use as part of a transaction ID. */
  protected final String encode(String s) {
    int idx = -1;
    StringBuffer sb = null;
    while((idx = s.indexOf(':',idx+1))>=0) {
      if(sb==null) sb = new StringBuffer(s);
      sb.setCharAt(idx, '?');
    }
    if(sb!=null) return sb.toString();
    return s;
  }
  
  
  /** Returns the palm data source that has the given ID, or null if
      none of the data sources have that ID. */
  public static final PalmDataSource getDataSource(String sourceID) {
    lazyInit();
    if(sourceID==null) return null;
    for(int i=0; i<dataSources.length; i++) {
      if(sourceID.equals(dataSources[i].getID()))
        return dataSources[i];
    }
    return null;
  }
    
  /** Return an array of all available data sources. */
  public static final PalmDataSource[] getAllDataSources() {
    lazyInit();
    return dataSources;
  }
    
  private static PalmDataSource[] dataSources = null;
  private static synchronized final void lazyInit() {
    if(dataSources!=null) return;
    dataSources = new PalmDataSource[] { new ExpensePalmDataSource(),
                                         new SplashmoneyPalmDataSource(),
                                         new PocketmoneyPalmDataSource() };
  }
}


