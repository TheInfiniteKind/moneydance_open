/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.infinitekind.moneydance.model.*;
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

public class SelectAccount 
  extends JPanel
  implements WizardPane
{
  private Wizard wizard;
  private Resources rr;
  private BalPredConf balpredConf;
  
  public SelectAccount(BalPredConf balpredConf) {
    this.balpredConf = balpredConf;
    this.rr = balpredConf.getResources();
    
    setLayout(new GridBagLayout());
    
    add(Box.createRigidArea(new Dimension(10,10)), GridC.getc(0,0).wxy(1,1));
    add(new JTextPanel(rr.getString("sel_acct_desc")), GridC.getc(1,1).wx(1).colspan(2).fillboth().insets(0,0,15,0));
    add(new JLabel(rr.getString("account")+":"), GridC.getc(1,2).label());
    add(balpredConf.cbAccounts, GridC.getc(2,2).field());
    add(Box.createRigidArea(new Dimension(10,10)), GridC.getc(3,3).wxy(1,1));
    setPreferredSize(new Dimension(500,350));
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
    return new SelectBasedOn(rr, balpredConf);
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
    return false;
  }

}

