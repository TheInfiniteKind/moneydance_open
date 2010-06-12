/************************************************************\
 * Portions Copyright (C) 2008 Reilly Technologies, L.L.C.   *
\************************************************************/

package com.moneydance.modules.features.mikebalpred;

import com.moneydance.apps.md.model.*;
//import com.moneydance.apps.md.controller.*;
//import com.moneydance.awt.*;
//import com.moneydance.awt.graph.*;

//import java.util.*;
import java.awt.event.*;
import javax.swing.*;

public class BalPredConf 
  implements ActionListener
{
  public static final int basedonReminders = 0;
  public static final int basedonTransactions = 1;
  public static final int DEF_NUM = 6;
  public static final int INTERVALS = 60;

  private RootAccount root = null;
  private TransactionSet ts = null;
  private TxnSet txns = null;
/*  private GraphModel gm = null;*/
  public String extensionName = null;
  public JComboBox cbAccounts = new JComboBox();
  public ReminderSet rs = null;
  public String dateFormatStr = "MM/dd/yy";
  
  public BalPredConf(RootAccount root, String extensionName) {
    this.root = root;
    this.extensionName = extensionName;
    loadAccount(root);
    ts = root.getTransactionSet();
    rs = root.getReminderSet();
    txns = ts.getTransactionsForAccount((Account)cbAccounts.getSelectedItem());
		cbAccounts.setSelectedIndex(1);
  }
  
  public RootAccount getRootAccount() { return root; }

  public Account getAccount() { return (Account)cbAccounts.getSelectedItem(); }

  public void loadAccount(Account acct) {
    for(int i=0; i<acct.getSubAccountCount(); i++) {
      Account subAcct = acct.getSubAccount(i);
      int acctType = subAcct.getAccountType();
      if(		(acctType==Account.ACCOUNT_TYPE_BANK) || (acctType==Account.ACCOUNT_TYPE_CREDIT_CARD)
				 || (acctType==Account.ACCOUNT_TYPE_ASSET) || (acctType==Account.ACCOUNT_TYPE_LIABILITY)) {
        cbAccounts.addItem(subAcct);
      }
      loadAccount(subAcct);
    }
  }

  public TxnSet returnTxnSet() {
    return txns;
  }

  public TxnSet getTxnSet() {
    txns = ts.getTransactionsForAccount((Account)cbAccounts.getSelectedItem());
    return txns; 
  }

//   public void setGraphModel(GraphModel gm) { this.gm = gm; }
// 
//   public GraphModel getGraphModel() { return gm; }

  public long getReminderCount() {
    long rc = 0;
    ParentTxn ptxn = null;
    SplitTxn stxn = null;
    Account acct = getAccount();
    for(int i=0; i<rs.getReminderCount();i++) {
      Reminder r = rs.getReminder(i);
      if (r.getReminderType() == Reminder.TXN_REMINDER_TYPE) {
        ptxn = ((TransactionReminder)r).getTransaction();
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
