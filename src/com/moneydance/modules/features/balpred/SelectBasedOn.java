/************************************************************\
 *        Copyright 2017 The Infinite Kind, Limited         *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.*;
import com.moneydance.awt.*;
import com.moneydance.awt.graph.*;
import com.infinitekind.util.*;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;
import javax.swing.border.*;
import java.io.*;
import java.util.*;
import java.net.*;
import java.text.*;

public class SelectBasedOn 
  extends JPanel
  implements WizardPane,
             ActionListener
{
  private Wizard wizard;
  private Resources rr = null;
  private BalPredConf balpredConf = null;
  private JTextPanel tpDescReminders;
  private JTextPanel tpDescTransactions;

  public SelectBasedOn(Resources rr, BalPredConf balpredConf) {
    this.rr = rr;
    this.balpredConf = balpredConf;

    setLayout(new GridBagLayout());
    if (balpredConf.getReminderCount()==0) {
      balpredConf.rbReminders.setSelected(false);
      balpredConf.rbReminders.setEnabled(false);
      balpredConf.rbTransactions.setSelected(true);
    }
    tpDescReminders = new JTextPanel(rr.getString("basedon_rem_desc"));
    tpDescTransactions =  new JTextPanel(rr.getString("basedon_txn_desc"));
    int y = 0;
    balpredConf.rbReminders.addActionListener(this);
    balpredConf.rbTransactions.addActionListener(this);
    add(new JTextPanel(rr.getString("basedon_info")), AwtUtil.getConstraints(0,y++,1,1,1,1,true,true));
    add(balpredConf.rbReminders, GridC.getc(0,y++).west());
    add(tpDescReminders, GridC.getc(0,y++).wxy(1,1).fillboth().insets(0,15,15,0));
    add(balpredConf.rbTransactions, GridC.getc(0,y++).west());
    add(tpDescTransactions, GridC.getc(0,y++).wxy(1,1).fillboth().insets(0,15,15,0));
  }

  public void actionPerformed(ActionEvent e) {
    if (e.getSource().equals(balpredConf.rbReminders)) {
      balpredConf.rbReminders.setSelected(true);
      balpredConf.rbTransactions.setSelected(false);
      return;
    }
    if (e.getSource().equals(balpredConf.rbTransactions)) {
      balpredConf.rbReminders.setSelected(false);
      balpredConf.rbTransactions.setSelected(true);
      return;
    }
  }

  public void activated(Wizard wiz) {
    this.wizard = wiz;
    this.wizard.setNextButtonEnabled(true);
  }

  /** Is called when the 'next' button is clicked to store
      the values entered in this pane.  Returns the next pane
      that the wizard should go to.  Returns null if the user
      should not be sent to the next pane. */
  public WizardPane storeValues() {
    SwingUtilities.invokeLater(new BalancePredicter(rr, balpredConf));
    return this;
  }

  /** Is called when no longer in use so that things can be
      cleaned up. */
  public void goneAway() {}
  
  /** Get the component that contains the GUI for this pane. */
  public JComponent getPanel() {
    return this;
  }
  
  /** Get whether or not this pane is the last one. */
  public boolean isLastPane() {
    return true;
  }

}

