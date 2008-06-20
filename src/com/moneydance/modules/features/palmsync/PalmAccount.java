/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.apps.md.model.Account;

/** Abstract class that all palm accounts inherit from. */
public class PalmAccount {
  private String palmAcctName;
  private String sourceID;
  private Account syncAccount;
  

  public PalmAccount(String palmAcctName, Account syncAccount, String sourceID) {
    this.syncAccount = syncAccount;
    this.palmAcctName = palmAcctName;
    this.sourceID = sourceID;
  }
    
  /** Get the name of the account */
  public String getName() {
    return palmAcctName;
  }
  
  public String toString() {
    return getName();
  }

  /** Get the ID for the palm data source that provided this palm account. */
  public String getSourceID() {
    return this.sourceID;
  }

  /** Get the account in Moneydance that transactions
      should be synchronized with. */
  public Account getSyncAccount() {
    return syncAccount;
  }
  
  /** Set the account in Moneydance that transactions
      should be synchronized with. */
  void setSyncAccount(Account syncAccount) {
    this.syncAccount = syncAccount;
  }

  /** Get a token that marks the point where synchronization last left off
      for this account. */
  public int getSyncToken() {
    return syncAccount.getRootAccount().
      getIntParameter("PalmSync."+sourceID + '.'+ palmAcctName + ".syncToken", 0);
  }

  /** Set the token that marks the point where synchronization last left
      off for this account. */
  public void setSyncToken(int token) {
    syncAccount.getRootAccount().setPreference("PalmSync."+sourceID + '.'+ palmAcctName + ".syncToken",
                                               token);
  }
  
}
