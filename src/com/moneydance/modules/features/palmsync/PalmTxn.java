/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.        *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.apps.md.model.*;
import java.util.Date;

public class PalmTxn {
  private Date date;
  private int txnID = -1;
  private String checkNum = "";
  private String desc = "";
  private String memo = "";
  private String vendor = "";
  private String category = "";
  private long amount = 0;
  private PalmAccount palmAcct = null;
  private PalmTxnSplit splits[] = null;

  private boolean isCleared = false;

  public PalmTxn(PalmAccount palmAcct) {
    this.palmAcct = palmAcct;
  }

  public Date getDate() { return date; }
  public void setDate(Date newDate) { this.date = newDate; }

  public int getTxnID() { return txnID; }
  public void setTxnID(int newTxnID) { this.txnID = newTxnID; }

  public String getCheckNum() { return checkNum; }
  public void setCheckNum(String newCheckNum) { this.checkNum = newCheckNum; }
  
  public String getDescription() { return desc; }
  public void setDescription(String newDesc) { this.desc = newDesc; }

  public String getMemo() { return memo; }
  public void setMemo(String newMemo) { this.memo = newMemo; }

  public String getVendor() { return vendor; }
  public void setVendor(String newVendor) { this.vendor = newVendor; }

  public String getCategory() { return category; }
  public void setCategory(String newCategory) { this.category = newCategory; }
  
  public long getAmount() { return amount; }
  public void setAmount(long newAmount) { this.amount = newAmount; }

  public PalmAccount getPalmAccount() { return palmAcct; }
  public void setPalmAccount(PalmAccount newPalmAccount) { this.palmAcct = newPalmAccount; }

  public PalmTxnSplit getSplit(int splitIdx) {
    if(splits==null) return null;
    if(splitIdx<0 || splitIdx>=splits.length) return null;
    return splits[splitIdx];
  }
  public int getSplitCount() {
    return splits==null ? 0 : splits.length;
  }
  public void addSplit(String description, String category, long amount) {
    PalmTxnSplit split = new PalmTxnSplit(amount, description, category);
    if(splits==null) {
      splits = new PalmTxnSplit[] { split };
    } else {
      PalmTxnSplit tmpSplits[] = new PalmTxnSplit[splits.length+1];
      System.arraycopy(splits, 0, tmpSplits, 0, splits.length);
      tmpSplits[tmpSplits.length-1] = split;
      splits = tmpSplits;
    }
  }

  public boolean isCleared() { return isCleared; }
  public void setCleared(boolean newCleared) { this.isCleared = newCleared; }

  /** This should be called before the user sees the transactions.
      It basically "cleans up" the transaction and makes it presentable
      to the user.
  */
  public void normalize() {
    if(desc==null || desc.trim().length()<=0)
      desc = vendor;
  }

  public final Account getCategoryAcct() {
    Account acct = this.palmAcct.getSyncAccount();
    String category = getCategory();
    boolean transfer = false;
    if(category.startsWith("[") && category.endsWith("]")) {
      category = category.substring(1, category.length()-1);
    }
    return getCategoryAcct(acct.getRootAccount(), category, transfer);
  }

  private final Account getCategoryAcct(Account parentAcct, String category, 
                                        boolean transfer) {
    if(category == null || category.length()<=0) {
      category = "UNFILED";
    }
    if(category.startsWith(":") &&
       parentAcct.getAccountType()==Account.ACCOUNT_TYPE_ROOT) {
      category = category.substring(1);
    }
    if(transfer && category.indexOf(':')>=0) {
      category = category.replace(':', ' ');
    }
    int parentType = parentAcct.getAccountType();
    int colIndex = category.indexOf(':');
    String restOfCategory;
    String thisCategory;
    if(colIndex>=0) {
      restOfCategory = category.substring(colIndex+1);
      thisCategory = category.substring(0,colIndex);
    } else {
      restOfCategory = null;
      thisCategory = category;
    }
    
    // find an existing account
    for(int i=0; i<parentAcct.getSubAccountCount(); i++) {
      Account subAcct = parentAcct.getSubAccount(i);
      int subAcctType = subAcct.getAccountType();
      if(!transfer && subAcctType!=Account.ACCOUNT_TYPE_EXPENSE &&
         subAcctType!=Account.ACCOUNT_TYPE_INCOME) {
        continue;
      }
      if(subAcct.getAccountName().equalsIgnoreCase(thisCategory)) {
        if(restOfCategory==null) {
          return subAcct;
        } else {
          return getCategoryAcct(subAcct, restOfCategory, transfer);
        }
      }
    }

    // no existing sub-account was found... create one
    Account newAccount;
    if(transfer) {
      newAccount = new BankAccount(thisCategory, -1, parentAcct.getCurrencyType(),
                                   null, null, parentAcct, 0);
    } else {
      switch(parentType) {
        case Account.ACCOUNT_TYPE_INCOME:
          newAccount =
          new IncomeAccount(thisCategory, -1, parentAcct.getCurrencyType(),
                            null, null, parentAcct);
          break;
        case Account.ACCOUNT_TYPE_EXPENSE:
          newAccount =
          new ExpenseAccount(thisCategory, -1, parentAcct.getCurrencyType(),
                             null, null, parentAcct);
          break;
        default:
          if(amount<=0) {
            newAccount =
            new ExpenseAccount(thisCategory, -1, parentAcct.getCurrencyType(),
                               null, null, parentAcct);
          } else {
            newAccount =
            new IncomeAccount(thisCategory, -1, parentAcct.getCurrencyType(),
                              null, null, parentAcct);
          }
          break; 
      }
    }
    parentAcct.addSubAccount(newAccount);
    if(restOfCategory==null) {
      return newAccount;
    } else {
      return getCategoryAcct(newAccount, restOfCategory, transfer);
    }
  }



  public class PalmTxnSplit {
    private long amount = 0;
    private String desc = "";
    private String category = "";

    public PalmTxnSplit(long amt, String desc, String category) {
      this.amount = amt;
      this.desc = desc;
      this.category = category;
    }

    public long getAmount() { return amount; };
    public String getDescription() { return desc; };
    public String getCategory() { return category; }

    public Account getCategoryAccount() {
      Account acct = palmAcct.getSyncAccount();
      String category = getCategory();
      boolean transfer = false;
      if(category.startsWith("[") && category.endsWith("]")) {
        category = category.substring(1, category.length()-1);
      }
      return getCategoryAcct(acct.getRootAccount(), category, transfer);
    }
  }
  
}



