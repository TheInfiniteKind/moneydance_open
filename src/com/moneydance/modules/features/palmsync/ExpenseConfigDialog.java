/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.awt.*;
import com.moneydance.apps.md.controller.Common;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.util.StringUtils;
import com.moneydance.apps.md.model.*;

import javax.swing.event.*;
import java.io.File;
import java.util.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.table.*;
import javax.swing.border.*;

public class ExpenseConfigDialog 
  extends JDialog 
  implements ActionListener 
{
  private String NO_ACCT_SELECTED = "<none>";
  private PalmAccount palmAccounts[];
  private RootAccount root = null;
  private Account mappings[];
  private Resources rr;
  private Main ext;
  private ExpensePalmDataSource source;
  
  private boolean wasCanceled = true;

  private JTextField dirField;
  private JButton browseButton;
  private JButton okButton;
  private JButton cancelButton;

  public ExpenseConfigDialog(Main ext, ExpensePalmDataSource source,
                             PalmAccount expenseAccounts[],
                             Resources rr, RootAccount root) {
    super(ext.getFrame(), rr.getString("config_settings"), true);
    this.ext = ext;
    this.source = source;
    this.root = root;
    this.rr = rr;
    this.palmAccounts = expenseAccounts;

    JTextPanel textPanel = new JTextPanel(rr.getString("select_expense_mapping"));
    okButton = new JButton(rr.getString("OK"));
    cancelButton = new JButton(rr.getString("cancel"));
    browseButton = new JButton(rr.getString("browse_button_label"));
    dirField = new JTextField(root.getParameter("PalmSync.pdbdir","."), 30);

    this.mappings = new Account[palmAccounts.length];
    for(int i=0; i<this.mappings.length; i++) {
      this.mappings[i] = palmAccounts[i].getSyncAccount();
    }
    
    // get a list of sync-able moneydance accounts
    Vector accounts = new Vector();
    addSyncableAccts(accounts, root);
    Object moneydanceAccts[] = new Object[accounts.size()+1];
    accounts.copyInto(moneydanceAccts);
    NO_ACCT_SELECTED = rr.getString("none");
    moneydanceAccts[accounts.size()] = NO_ACCT_SELECTED;
    
    JTable mappingTable = new JTable(new MappingModel());
    mappingTable.getColumnModel().getColumn(1).
      setCellEditor(new DefaultCellEditor(new JComboBox(moneydanceAccts)));

    int y = 0;
    JPanel p = new JPanel(new GridBagLayout());
    p.add(textPanel, AwtUtil.getConstraints(0,y++,1,0,3,1,true,true));
    p.add(new JScrollPane(mappingTable),
          AwtUtil.getConstraints(0,y++,1,1,3,1,true,true));
    p.add(Box.createVerticalStrut(12),
          AwtUtil.getConstraints(0,y++,0,0,3,1,true,true));
    p.add(new JLabel(rr.getString("backup_dir")+": ", JLabel.RIGHT),
          AwtUtil.getConstraints(0,y,0,0,1,1,true,true));
    p.add(dirField,
          AwtUtil.getConstraints(1,y,1,0,1,1,true,true));
    p.add(browseButton,
          AwtUtil.getConstraints(2,y++,0,0,1,1,true,true));
    p.add(Box.createVerticalStrut(16),
          AwtUtil.getConstraints(0,y++,0,0,3,1,true,true));

          

    JPanel bp = new JPanel(new GridBagLayout());
    bp.add(Box.createHorizontalStrut(60), AwtUtil.getConstraints(0,0,1,0,1,1,false,false));
    bp.add(cancelButton, AwtUtil.getConstraints(1,0,0,0,1,1,false,false));
    bp.add(Box.createHorizontalStrut(12), AwtUtil.getConstraints(2,0,0,0,1,1,false,false));
    bp.add(okButton, AwtUtil.getConstraints(3,0,0,0,1,1,false,false));
    p.add(bp, AwtUtil.getConstraints(0,y++,1,0,3,1,true,true));
    p.setBorder(new EmptyBorder(10,10,10,10));
    
    getContentPane().add(p);

    okButton.addActionListener(this);
    cancelButton.addActionListener(this);
    browseButton.addActionListener(this);
    
    try { pack(); } catch (Exception e) {}
    Dimension sz = getPreferredSize();
    setSize(minmax(250, sz.width, 400), minmax(250, sz.height, 400));
    AwtUtil.centerWindow(this);
  }
  
  private class MappingModel 
    extends AbstractTableModel
  {
    public int getRowCount() {
      return mappings.length;
    }
    
    public int getColumnCount() {
      return 2;
    }
    
    public String getColumnName(int col) {
      if(col==0) return rr.getString("from_payment");
      else return rr.getString("to_acct");
    }
    
    public Object getValueAt(int row, int column) {
      switch(column) {
        case 0: return palmAccounts[row];
        case 1:
        default:
          if(mappings[row]==null) return NO_ACCT_SELECTED;
          else return mappings[row];
      }
    }
    
    public boolean isCellEditable(int row, int column) {
      return column==1;
    }
    
    public void setValueAt(Object newValue, int row, int column) {
      if(column==0) return;
      if(newValue instanceof Account) {
        mappings[row] = (Account)newValue;
      } else {
        mappings[row] = null;
      }
      fireTableCellUpdated(row, column);
    }
  }

  /** makes a list of the moneydance account that can be synchronized */
  private void addSyncableAccts(Vector acctList, Account acct) {
    for(int i = 0; i < acct.getSubAccountCount(); i++)  {
      Account subAcct = acct.getSubAccount(i);
      int acctType = subAcct.getAccountType();
      if(acctType == Account.ACCOUNT_TYPE_BANK ||
         acctType == Account.ACCOUNT_TYPE_CREDIT_CARD) { 
        acctList.addElement(subAcct);
      }
      addSyncableAccts(acctList, subAcct);
    }        
  }
  
  private static final int minmax(int min, int num, int max) {
    if(num<min) return min;
    if(num>max) return max;
    return min;
  }

  private void okPressed() {
    Account acct = null;
    for(int i=0; i<mappings.length; i++) {
      acct = mappings[i];
      palmAccounts[i].setSyncAccount(acct);
      if(acct==null) {
        root.removeParameter("PalmSync.ExpenseAccount."+palmAccounts[i]+".syncAccount");
      } else {
        root.setParameter("PalmSync.ExpenseAccount."+palmAccounts[i]+".syncAccount",
                          acct.getAccountNum());
      }
    }
    root.setParameter("PalmSync.pdbdir", dirField.getText());
    wasCanceled = false;
    setVisible(false);
    dispose();
  }

  public boolean wasCanceled() {
    return wasCanceled;
  }

  private void cancelPressed() {
    wasCanceled = true;
    setVisible(false);
    dispose();
  }

  private void browsePressed() {
    JFileChooser fc = new JFileChooser();
    fc.setDialogTitle(rr.getString("choose_directory"));
    fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
    int returnVal = fc.showOpenDialog(this);
    if(returnVal!=JFileChooser.APPROVE_OPTION) return;
    File selectedDir = fc.getSelectedFile();
    try {
      dirField.setText(selectedDir.getCanonicalPath());
    } catch (Throwable t) {
      dirField.setText(selectedDir.getAbsolutePath());
    }
  }
  
  public void actionPerformed(ActionEvent e)  {
    Object src = e.getSource();
    if(src==okButton) {
      okPressed();
    } else if(src==cancelButton) {
      cancelPressed();
    } else if(src==browseButton) {
      browsePressed();
    }
  }
  
}

