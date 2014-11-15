/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.awt.*;
import com.moneydance.apps.md.controller.Common;
import com.moneydance.apps.md.controller.Util;
import com.infinitekind.util.StringUtils;
import com.infinitekind.moneydance.model.*;

import javax.swing.event.*;
import java.io.File;
import java.util.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.table.*;
import javax.swing.border.*;

public class PocketmoneyAcctConfig
  extends JDialog 
  implements ActionListener 
{
  private String NO_ACCT_SELECTED = "<none>";
  private PalmAccount palmAccounts[];
  private RootAccount root = null;
  private Account mappings[];
  private Resources rr;
  private Main ext;
  private PocketmoneyPalmDataSource source;
  
  private boolean wasCanceled = true;

  private JButton okButton;
  private JButton cancelButton;

  public PocketmoneyAcctConfig(Main ext, PocketmoneyPalmDataSource source,
                               PalmAccount palmAccounts[],
                               Resources rr, RootAccount root) {
    super(ext.getFrame(), rr.getString("config_settings"), true);
    this.ext = ext;
    this.source = source;
    this.root = root;
    this.rr = rr;
    this.palmAccounts = palmAccounts;

    JTextPanel textPanel = new JTextPanel(rr.getString("select_pocketmoney_mapping"));
    okButton = new JButton(rr.getString("OK"));
    cancelButton = new JButton(rr.getString("cancel"));

    mappings = new Account[palmAccounts.length];
    for(int i=0; i<mappings.length; i++) {
      mappings[i] = palmAccounts[i].getSyncAccount();
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
    
    try { pack(); } catch (Exception e) {}
    Dimension sz = getPreferredSize();
    setSize(minmax(250, sz.width, 400), minmax(250, sz.height, 400));
    AwtUtil.centerWindow(this);
  }
  
  private class MappingModel 
    extends AbstractTableModel
  {
    public int getRowCount() {
      return palmAccounts.length;
    }
    
    public int getColumnCount() {
      return 2;
    }
    
    public String getColumnName(int col) {
      if(col==0) return rr.getString("from_acct");
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
        root.removeParameter("PalmSync."+source.getID()+"."+palmAccounts[i]+".syncAccount");
      } else {
        root.setParameter("PalmSync."+source.getID()+"."+palmAccounts[i]+".syncAccount",
                          acct.getAccountNum());
      }
    }
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

  public void actionPerformed(ActionEvent e)  {
    Object src = e.getSource();
    if(src==okButton) {
      okPressed();
    } else if(src==cancelButton) {
      cancelPressed();
    }
  }
  
}








