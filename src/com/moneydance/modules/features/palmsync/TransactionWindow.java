package com.moneydance.modules.features.palmsync;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.awt.*;
import com.infinitekind.util.StringUtils;
import com.infinitekind.util.CustomDateFormat;

import javax.swing.*;
import javax.swing.event.*;
import java.util.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.border.*;

public class TransactionWindow
  extends JDialog
  implements ActionListener,
             ListSelectionListener
{
  private JButton oneButton;
  private JButton allButton;
  private JButton rejectAllButton;
  private JButton mergeButton;
  private JButton finishButton;
  private JButton rejectButton;
  private JTextPanel mergeInfo;
  private JTable table;
  private PalmTxnTableModel tableModel;
  private JScrollPane scrollPane;
  private boolean isLast;
  private Resources rr;
  private Main ext;
  private CustomDateFormat dateFormat = new CustomDateFormat("M/D/Y");

  private SyncController syncController;
  private PalmDataSource source;
  private PalmAccount account;
  private TransactionSet globalTxnSet;
  private TxnSet matchTxnSet;
  
  private PalmTxn selectedTxn = null;
  private AbstractTxn matchTxn = null;
  private boolean goodMatch = false;

  private int lastToken = -1;
  
  public TransactionWindow(PalmDataSource source, PalmAccount account,
                           SyncController syncController,
                           PalmTxn[] txns, boolean isLast, Resources rr, Main ext,
                           TxnSet mergeTxnSet) {
    super(ext.getFrame(), account.getName() + rr.getString("trans_to_file") +
          account.getSyncAccount().getAccountName(), false);
    this.syncController = syncController;
    this.source = source;
    this.account = account;
    this.ext = ext;
    this.rr = rr;
    this.isLast = isLast;
    this.matchTxnSet = mergeTxnSet;
    
    tableModel = new PalmTxnTableModel(txns, rr);
    table = new JTable(tableModel);
    table.getSelectionModel().setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
    table.getSelectionModel().addListSelectionListener(this);
    scrollPane = new JScrollPane(table);
    oneButton = new JButton(rr.getString("accept_button_label"));
    allButton = new JButton(rr.getString("merge/accept_all_button_label"));
    rejectAllButton = new JButton(rr.getString("reject_all_button_label"));
    mergeButton = new JButton(rr.getString("merge_button_label"));
        
    if (isLast)
      finishButton = new JButton(rr.getString("finish_button_label"));
    else   
      finishButton = new JButton(rr.getString("next_account_button_label"));
        
    rejectButton = new JButton(rr.getString("reject_button_label"));
    mergeInfo = new JTextPanel("");
    mergeInfo.setVisible(false);

    JPanel p = new JPanel(new GridBagLayout());
    JPanel tablePanel = new JPanel(new BorderLayout());
    tablePanel.add(new JScrollPane(table), BorderLayout.CENTER);
    tablePanel.add(mergeInfo, BorderLayout.SOUTH);
    p.setBorder(new EmptyBorder(16,16,12,16));
    p.add(new JTextPanel(rr.getString("transaction_window_message")),
          AwtUtil.getConstraints(0,0,1,0,3,1,true,true));
    p.add(tablePanel,
          AwtUtil.getConstraints(0,1,1,1,1,12,true,true));
    p.add(Box.createHorizontalStrut(16),
          AwtUtil.getConstraints(1,1,0,0,1,1,false,false));
    p.add(Box.createVerticalStrut(12),
          AwtUtil.getConstraints(2,1,0,0,1,1,true,true));
    p.add(mergeButton,
          AwtUtil.getConstraints(2,2,0,0,1,1,true,false));
    p.add(Box.createVerticalStrut(12),
          AwtUtil.getConstraints(2,3,0,0,1,1,true,true));
    p.add(oneButton,
          AwtUtil.getConstraints(2,4,0,0,1,1,true,false));
    p.add(Box.createVerticalStrut(12),
          AwtUtil.getConstraints(2,5,0,0,1,1,true,true));
    p.add(rejectButton,
          AwtUtil.getConstraints(2,6,0,0,1,1,true,false));
    p.add(Box.createVerticalStrut(24),
          AwtUtil.getConstraints(2,7,0,1,1,1,true,true));
    p.add(allButton,
          AwtUtil.getConstraints(2,8,0,0,1,1,true,false));
    p.add(Box.createVerticalStrut(24),
          AwtUtil.getConstraints(2,7,0,1,1,1,true,true));
    p.add(rejectAllButton,
          AwtUtil.getConstraints(2,10,0,0,1,1,true,false));
    p.add(Box.createVerticalStrut(24),
          AwtUtil.getConstraints(2,11,0,1,1,1,true,true));
    p.add(finishButton,
          AwtUtil.getConstraints(2,12,0,0,1,1,true,false));
    getContentPane().add(p);

    // the global transaction list in moneydance
    globalTxnSet = account.getSyncAccount().getRootAccount().getTransactionSet();
    
    // the list of transactions that might match
    matchTxnSet = globalTxnSet.getTransactionsForAccount(account.getSyncAccount());

    try { pack(); } catch (Exception e) {}
    Dimension sz = getPreferredSize();
    setSize(minmax(300, sz.width, 550), minmax(300, sz.height, 400));
    AwtUtil.centerWindow(this);

    oneButton.addActionListener(this);
    allButton.addActionListener(this);
    rejectAllButton.addActionListener(this);
    mergeButton.addActionListener(this);
    finishButton.addActionListener(this);
    rejectButton.addActionListener(this);

    updateButtons();
  }

  public void center() {
    AwtUtil.centerWindow(this);
  }
     
  private static final int minmax(int min, int num, int max) {
    if(num<min) return min;
    if(num>max) return max;
    return min;
  }
    

  private void updateButtons() {
    table.getSelectionModel().setSelectionInterval(0,0);
    int tempInt = table.getSelectedRow();
    selectedTxn = tableModel.getTransaction(tempInt);
    if(selectedTxn == null) {
      matchTxn = null;
      oneButton.setEnabled(false);
      mergeButton.setEnabled(false);
      mergeInfo.setVisible(false);
      rejectButton.setEnabled(false);
      rejectAllButton.setEnabled(false);
      allButton.setEnabled(false);
    } else {
      findMatch(selectedTxn);
      oneButton.setEnabled(true);
      mergeButton.setEnabled(matchTxn!=null);
      if(matchTxn!=null){
        mergeInfo.setText(rr.getString("may_correspond_date") +
                          dateFormat.format(new Date(matchTxn.getDate())) +
                          rr.getString("may_correspond_amount") +
                          account.getSyncAccount().getCurrencyType().format(matchTxn.getValue(),'.') +
                          rr.getString("may_correspond_description") +
                          matchTxn.getDescription() +
                          rr.getString("."));
      } else {
        mergeInfo.setText("");
      }
      mergeInfo.repaint();
    }
  }

  private void mergePressed() {
    PalmTxn palmTxn = selectedTxn;
    AbstractTxn matchTxn = this.matchTxn;
    if(palmTxn==null || matchTxn==null) {
      try { getToolkit().beep(); } catch (Throwable t) { }
      return;
    }

    mergeTxn(palmTxn, matchTxn);
  }

  private void acceptOnePressed() {
    PalmTxn palmTxn = selectedTxn;
    if(palmTxn==null) {
      try { getToolkit().beep(); } catch (Throwable t) { }
      return;
    }

    addNewTransaction(palmTxn);
  }

  private void addNewTransaction(PalmTxn palmTxn) {
    long dt = Util.stripTimeFromDate(palmTxn.getDate()).getTime();
    
    ParentTxn trans = new ParentTxn(dt, dt, System.currentTimeMillis(),
                                    palmTxn.getCheckNum(),
                                    account.getSyncAccount(),
                                    palmTxn.getDescription(),
                                    palmTxn.getMemo(),
                                    -1,
                                    palmTxn.isCleared() ?
                                    AbstractTxn.STATUS_CLEARED :
                                    AbstractTxn.STATUS_UNRECONCILED);
    trans.setTag("palmsync."+source.getID()+".aftag",
                 source.getTransactionID(palmTxn));

    if(palmTxn.getSplitCount()<=1) {
      SplitTxn split = new SplitTxn(trans, palmTxn.getAmount(), (double)1,
                                    palmTxn.getCategoryAcct(),
                                    palmTxn.getDescription(), -1l,
                                    AbstractTxn.STATUS_UNRECONCILED);  
      trans.addSplit(split);
      /////split.setRate();
    } else {
      for(int i=0; i<palmTxn.getSplitCount(); i++) {
        PalmTxn.PalmTxnSplit split = palmTxn.getSplit(i);
        trans.addSplit(new SplitTxn(trans, split.getAmount(),
                                    (double)1,
                                    split.getCategoryAccount(),
                                    palmTxn.getDescription(), -1l,
                                    AbstractTxn.STATUS_UNRECONCILED));
      }
    }
    globalTxnSet.addNewTxn(trans);
    source.transactionWasAbsorbed(palmTxn);

    tableModel.removeTxn(palmTxn);
    updateButtons();
  }

  private void mergeTxn(PalmTxn palmTxn, AbstractTxn matchTxn) {
    matchTxn.setTag("palmsync."+source.getID()+".aftag",
                    source.getTransactionID(palmTxn));

    globalTxnSet.txnModified(matchTxn);
    source.transactionWasAbsorbed(palmTxn);

    matchTxnSet.removeTxn(matchTxn);
    tableModel.removeTxn(palmTxn);
    updateButtons();
  }


  private void rejectPressed() {
    PalmTxn palmTxn = selectedTxn;
    if(palmTxn==null) {
      try { getToolkit().beep(); } catch (Throwable t) { }
      return;
    }

    source.transactionWasAbsorbed(palmTxn);
    tableModel.removeTxn(palmTxn);
    updateButtons();
  }

  private void rejectAllPressed() {
    PalmTxn[] transactions = tableModel.getTransactions();
    for(int i=0; transactions!=null && i<transactions.length; i++) {
      PalmTxn palmTxn = transactions[i];
      source.transactionWasAbsorbed(palmTxn);
      tableModel.removeTxn(palmTxn);
    }
    updateButtons();
  }

  private void acceptAllPressed() {
    PalmTxn[] transactions = tableModel.getTransactions();
    for(int i=0; transactions!=null && i<transactions.length; i++) {
      PalmTxn palmTxn = transactions[i];
      findMatch(palmTxn);
      if(goodMatch) {         // merge the transaction
        mergeTxn(palmTxn, matchTxn);
      } else {                // add the new transaction
        addNewTransaction(palmTxn);
      }
    }
    updateButtons();
  }

  private void finishButtonPressed() {
    syncController.nextDialog();
  }

  /* find the closest match for the given transaction and return it */
  private void findMatch(PalmTxn palmTxn) {
    String description = palmTxn.getDescription().trim();
    if(description.length()<=0) description = palmTxn.getVendor().trim();
    String upperDesc = description.toUpperCase();
    
    long paymentDate = Util.stripTimeFromDate(palmTxn.getDate()).getTime();
    long amount = palmTxn.getAmount();
    String checkNum = palmTxn.getCheckNum().trim();
    String checkNumUpper = checkNum.toUpperCase();
    boolean isNumber = StringUtils.isAllNumber(checkNum);
    int checkNumLen = checkNum.length();
    goodMatch = false;
    matchTxn = null;
    
    TxnSet possibleMatches = new TxnSet();
    String txnCheckNum = "";
    AbstractTxn txn;
    long dateDiff;
    
    for(int i=matchTxnSet.getSize()-1; i>=0; i--) {
      txn = matchTxnSet.getTxnAt(i);

      // ignore already imported transactions... (disabled to allow new matching)
      ////if(txn.getTag("palmsync.id") != null) continue;

      // amounts must match exactly
      if(txn.getValue() != amount) continue;

      // the date is off by at least 30 days, no match
      dateDiff = Math.abs(txn.getDate() - paymentDate);
      if(dateDiff> 86400000*30) continue;

      txnCheckNum = txn.getCheckNumber().trim();
      
      if(isNumber) {
        // if this payment has a check# then they both must match exactly, or the
        // existing check# must be blank.
        if(checkNum.equals(txnCheckNum)) { // they match exactly
          matchTxn = txn;
          goodMatch = true;
          return;
        } else if(StringUtils.isAllNumber(txnCheckNum)) {
          // the txn has a different numeric check #, no match
          continue;
        }
      }

      // if less than 5 days away, it is still a contender for a match
      if(dateDiff <= 86400000*5) {
        possibleMatches.addTxn(txn);
      }
    }

    int sz = possibleMatches.getSize();
    if(sz<=0) return;

    // no exact match has been found.  search the more exact possible matches for the best fit
    AbstractTxn bestMatch = null;
    long minDateDiff = -1;
    for(int i=0; i<sz; i++) {
      txn = possibleMatches.getTxnAt(i);
      dateDiff = Math.abs(txn.getDate() - paymentDate);
      if((minDateDiff==-1 || dateDiff < minDateDiff) &&
         upperDesc.equals(txn.getDescription().trim().toUpperCase())) {
        minDateDiff = dateDiff;
        bestMatch = txn;
      }
    }
    if(bestMatch!=null) {
      matchTxn = bestMatch;
      goodMatch = true;
      return;
    }
    
    // find the closest date that has a matching transaction
    minDateDiff = -1;
    for(int i=0; i<sz; i++) {
      txn = possibleMatches.getTxnAt(i);
      dateDiff = Math.abs(txn.getDate() - paymentDate);
      if(minDateDiff<0 || dateDiff <= minDateDiff) {
        bestMatch = txn;
        minDateDiff = dateDiff;
      }
    }

    // it is only an exact match if the date is
    // exactly the same
    goodMatch = minDateDiff!=-1 && minDateDiff < 66400000;
    
    // get rid of all matching transactions that are further away
    for(int i=sz-1; i>=0; i--) {
      txn = possibleMatches.getTxnAt(i);
      if(Math.abs(txn.getDate() - paymentDate) > minDateDiff)
        possibleMatches.removeTxnAt(i);
    }

    sz = possibleMatches.getSize();
    if(sz<=0) return;


    // the first possible match with the same check# will do it
    for(int i=0; i<sz; i++) {
      txn = possibleMatches.getTxnAt(i);
      if(txn.getCheckNumber().trim().toUpperCase().equals(checkNumUpper)) {
        matchTxn = txn;
        return;
      }
    }
    
    // At this point we'll take the first match that is left...
    if(sz>0) {
      matchTxn = possibleMatches.getTxnAt(0);
      goodMatch = false;
    }
    return;
  }
  
  public void valueChanged(ListSelectionEvent evt) {
    updateButtons();
  }    
  
  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    if(src == mergeButton) {
      mergePressed();
    } else if(src == oneButton) {
      acceptOnePressed();
    } else if(src == rejectButton) {
      rejectPressed();
    } else if(src == allButton) {
      acceptAllPressed();
    } else if(src == rejectAllButton) {
      rejectAllPressed();
    } else if(src == finishButton) {
      finishButtonPressed();
    }
  }

  protected Account dealWithSplitAccount(String accountName, Account root) {
    if(accountName.startsWith(":") &&
       root.getAccountType()==Account.ACCOUNT_TYPE_ROOT) {
      accountName = accountName.substring(1);
    }
    
    int parentType = root.getAccountType();
    int colIndex = accountName.indexOf(':');
    String restOfAcctName;
    String thisAcctName;
    if(colIndex>=0) {
      restOfAcctName = accountName.substring(colIndex+1);
      thisAcctName = accountName.substring(0,colIndex);
    } else {
      restOfAcctName = null;
      thisAcctName = accountName;
    }

    // find an existing account
    for(int i=0; i<root.getSubAccountCount(); i++) {
      Account subAcct = root.getSubAccount(i);
      int subAcctType = subAcct.getAccountType();
      if(!(subAcctType==Account.ACCOUNT_TYPE_BANK ||
           subAcctType==Account.ACCOUNT_TYPE_CREDIT_CARD ||
           subAcctType==Account.ACCOUNT_TYPE_EXPENSE ||
           subAcctType==Account.ACCOUNT_TYPE_INCOME)) {
        continue;
      }
      if(subAcct.getAccountName().equalsIgnoreCase(thisAcctName)) {
        if(restOfAcctName==null) {
          return subAcct;
        } else {
          return dealWithSplitAccount(restOfAcctName, subAcct);
        }
      }
    }

    // no existing sub-account was found... create one
    Account newAccount;
    switch(parentType) {
      case Account.ACCOUNT_TYPE_INCOME:
        newAccount =
          new IncomeAccount(thisAcctName, -1, root.getCurrencyType(),
                            null, null, root);
        break;
      case Account.ACCOUNT_TYPE_BANK:
      case Account.ACCOUNT_TYPE_CREDIT_CARD:
      case Account.ACCOUNT_TYPE_ROOT:
      case Account.ACCOUNT_TYPE_EXPENSE:
      default:
        newAccount =
          new ExpenseAccount(thisAcctName, -1, root.getCurrencyType(),
                             null, null, root);
        break; 
    }
    root.addSubAccount(newAccount);
    if(restOfAcctName==null) {
      return newAccount;
    } else {
      return dealWithSplitAccount(restOfAcctName, newAccount);
    }

  }
    
}













