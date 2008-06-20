/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.moneydance.apps.md.model.*;
import com.moneydance.awt.*;
import com.moneydance.awt.graph.*;
import com.moneydance.util.*;

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
    
    add(new JTextPanel(rr.getString("sel_acct_desc")),
        AwtUtil.getConstraints(0,0,1,1,2,1,true,true));
    add(new JLabel(rr.getString("account")+"   ", JLabel.RIGHT), 
        AwtUtil.getConstraints(0,1,0,1,1,1,true,false));
    add(balpredConf.cbAccounts,
        AwtUtil.getConstraints(1,1,1,1,1,1,true,false));
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

