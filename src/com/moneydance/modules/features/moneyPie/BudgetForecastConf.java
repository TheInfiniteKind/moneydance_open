/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import com.infinitekind.moneydance.model.*;

import java.awt.event.*;
import java.util.List;

import javax.swing.*;

public class BudgetForecastConf implements ActionListener {
  public static final int basedonReminders = 0;
  public static final int basedonTransactions = 1;
  public static final int DEF_NUM = 6;
  public static final int INTERVALS = 60;

  private AccountBook root = null;
  private TransactionSet ts = null;
  private TxnSet txns = null;

  public String extensionName = null;
  public JComboBox cbAccounts = new JComboBox();
  public ReminderSet rs = null;
  public String dateFormatStr = "MM/dd/yy";

  public BudgetForecastConf(AccountBook root, String extensionName) {
    this.root = root;
    this.extensionName = extensionName;
    
    loadAccount(root.getRootAccount());
    ts = root.getTransactionSet();
    rs = root.getReminders();
    txns = ts.getTransactionsForAccount((Account)cbAccounts.getSelectedItem());
    if(cbAccounts.getItemCount() > 0){
    	cbAccounts.setSelectedIndex(1);
    }
  }

  public AccountBook getRootAccount() { return root; }

  public int getNumAccounts(){
	  return cbAccounts.getItemCount();
  }
  
  public Account getAccount() { 
	  return (Account)cbAccounts.getSelectedItem(); 
  }
  
  public Account getAccount(int index) { 
	  cbAccounts.getItemAt(index);
	  return (Account)cbAccounts.getItemAt(index); 
  }

  public void loadAccount(Account acct) {
    for(int i=0; i<acct.getSubAccountCount(); i++) {
      Account subAcct = acct.getSubAccount(i);

      if(subAcct.getComment().indexOf("IGNORE") == -1) {
    	  Account.AccountType acctType = subAcct.getAccountType();
          if( (acctType==Account.AccountType.BANK) || 
        	  (acctType==Account.AccountType.CREDIT_CARD) || 
        	  (acctType==Account.AccountType.ASSET) || 
        	  (acctType==Account.AccountType.INVESTMENT) || 
        	  (acctType==Account.AccountType.LIABILITY)) {
        		  cbAccounts.addItem(subAcct);
          }
          loadAccount(subAcct); 
      }
      
    }
  }

  public TxnSet returnTxnSet() {
    return txns;
  }

  public TxnSet getTxnSet() {
    txns = ts.getTransactionsForAccount((Account)cbAccounts.getSelectedItem());
    return txns;
  }

  public long getReminderCount() {
    long rc = 0;
    ParentTxn ptxn = null;
    SplitTxn stxn = null;
    Account acct = getAccount();
    
    List<Reminder> rl = rs.getAllReminders();
    
    for(int i=0; i<rl.size();i++) {
      Reminder r = rl.get(i);
      
      if (r.getReminderType() == Reminder.Type.typeForCode(Reminder.TXN_REMINDER_TYPE)) {
        ptxn = (ParentTxn)r.getTransaction();
        if (ptxn.getAccount().equals(acct)) rc++;
        else {
          for(int j=0;j<ptxn.getSplitCount();j++) {
            stxn = ptxn.getSplit(j);
            if (stxn.getAccount().equals(acct)) rc++;
          }
        }
      }
    }
    return rc;
  }

  public void actionPerformed(ActionEvent e) {
    if (e.getSource().equals(cbAccounts)) {
      txns = ts.getTransactionsForAccount((Account)cbAccounts.getSelectedItem());
    }
  }
}
