/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.graph.*;

import java.awt.event.*;
import javax.swing.*;

public class BalPredConf 
  implements ActionListener
{
  public static final int basedonReminders = 0;
  public static final int basedonTransactions = 1;
  public static final int DEF_NUM = 6;
  public static final int INTERVALS = 60;

  private AccountBook book = null;
  private TransactionSet ts = null;
  private TxnSet txns = null;
  private Resources rr = null;
  private int avgDays = 30;
  private GraphModel gm = null;
  public String extensionName = null;
  public JComboBox cbAccounts = new JComboBox();
  public JRadioButton rbReminders = new JRadioButton();
  public JRadioButton rbTransactions = new JRadioButton();
  public ReminderSet rs = null;
  public String dateFormatStr = "MM/dd/yyyy";
  
  public BalPredConf(AccountBook book, Resources rr, String extensionName) {
    this.book = book;
    this.rr = rr;
    this.extensionName = extensionName;
    loadAccount(book.getRootAccount());
    ts = book.getTransactionSet();
    rs = book.getReminders();
    txns = ts.getTransactionsForAccount((Account)cbAccounts.getSelectedItem());
    rbReminders.setLabel(rr.getString("reminders"));
    rbReminders.setSelected(true);
    rbTransactions.setLabel(rr.getString("transactions"));
    rbTransactions.setSelected(false);
  }
  
  public AccountBook getRootAccount() { return book; }
  public Resources getResources() { return rr; }
  public Account getAccount() { return (Account)cbAccounts.getSelectedItem(); }
  public void loadAccount(Account acct) {
    for(int i=0; i<acct.getSubAccountCount(); i++) {
      Account subAcct = acct.getSubAccount(i);
      switch(subAcct.getAccountType()) {
        case BANK:
        case CREDIT_CARD:
        case ASSET:
        case LIABILITY:
          cbAccounts.addItem(subAcct);
        default:
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
  public int getBasedOn() { 
    return rbReminders.isSelected() ? basedonReminders : basedonTransactions; 
  }
  public void setAvgDays(int avgDays) { this.avgDays = avgDays; }
  public int getAvgDays() { return avgDays; }
  public void setGraphModel(GraphModel gm) { this.gm = gm; }
  public GraphModel getGraphModel() { return gm; }
  public long getReminderCount() {
    long rc = 0;
    ParentTxn ptxn = null;
    SplitTxn stxn = null;
    Account acct = getAccount();
    for(Reminder r : book.getReminders().getAllReminders()) {
      if (r.getReminderType() == Reminder.Type.TRANSACTION) {
        ptxn = r.getTransaction();
        if (ptxn.getAccount().equals(acct)) {
          rc++;
        } else {
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
