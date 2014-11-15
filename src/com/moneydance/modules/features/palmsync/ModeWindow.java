/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.apps.md.controller.Common;
import com.moneydance.apps.md.controller.Util;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.RootAccount;
import com.infinitekind.util.StringUtils;
import com.moneydance.awt.*;

import javax.swing.event.*;
import java.net.*;
import java.io.*;
import java.util.*;
import javax.swing.*;
import java.text.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.SwingUtilities;
import javax.swing.border.*;
import java.util.Vector;

/**
 * Window that lets the user modify their palm synchronization settings
 */
public class ModeWindow 
  extends JFrame
  implements ActionListener,
             Runnable
{
  private RootAccount root;
  private Main ext;
  private JButton doneButton, nowButton, configButton, helpButton;
  private JComboBox appChoice;
  private JCheckBox syncAtStartBox;
  private PalmDataSource palmApps[];
  private Resources rr;

  /**
   *Constructor for the ModeWindow object
   *
   * @param  root  The current account/model object
   * @param  rr    Localized Resources
   */
  public ModeWindow(Main ext, RootAccount root, Resources rr) {
    super(rr.getString("config_settings"));
    this.ext = ext;
    this.root = root;
    this.rr = rr;

    palmApps = PalmDataSource.getAllDataSources();
    
    JLabel appLabel = new JLabel(rr.getString("choose_program"), JLabel.RIGHT);
    appChoice = new JComboBox(palmApps);
    doneButton = new JButton(rr.getString("done_button_label"));
    syncAtStartBox = new JCheckBox(rr.getString("sync_at_start"));

    helpButton = new JButton(rr.getString("help_button_label"));
    nowButton = new JButton(rr.getString("sync_now"));
    configButton = new JButton(rr.getString("configure_button_label"));

    int y = 0;
    JPanel p = new JPanel(new GridBagLayout());
    p.setBorder(new EmptyBorder(10, 10, 10, 10));
    p.add(Box.createVerticalStrut(12), 
          AwtUtil.getConstraints(0,y++,0,1,1,1,false,false));
    p.add(appLabel, 
          AwtUtil.getConstraints(0,y,0,0,1,1,true,false));
    p.add(appChoice, 
          AwtUtil.getConstraints(1,y++,1,0,1,1,true,false));
    p.add(configButton, 
          AwtUtil.getConstraints(1,y++,1,0,1,1,false,false,GridBagConstraints.WEST));
    p.add(Box.createVerticalStrut(18), 
          AwtUtil.getConstraints(0,y++,0,1,1,1,false,false));
    p.add(syncAtStartBox, 
          AwtUtil.getConstraints(1, y++, 1, 0, 1, 1, true, false));
    p.add(Box.createVerticalStrut(18), 
          AwtUtil.getConstraints(0,y++,0,1,1,1,false,false));
    p.add(nowButton, 
          AwtUtil.getConstraints(1,y++,1,0,1,1,false,false,GridBagConstraints.WEST));
    p.add(Box.createVerticalStrut(18), 
          AwtUtil.getConstraints(0,y++,0,1,1,1,false,false));

    JPanel bp = new JPanel(new GridBagLayout());
    bp.add(helpButton, AwtUtil.getConstraints(0,0,0,0,1,1,false,false));
    bp.add(Box.createHorizontalStrut(18),AwtUtil.getConstraints(1,0,1,0,1,1,false,false));
    bp.add(doneButton, AwtUtil.getConstraints(2,0,0,0,1,1,false,false));
    p.add(bp, AwtUtil.getConstraints(0,y++,1,0,3,1,true,false));

    getContentPane().add(p);
    
    populateFields();
    
    configButton.addActionListener(this);
    helpButton.addActionListener(this);
    doneButton.addActionListener(this);
    nowButton.addActionListener(this);

    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);

    try { pack(); } catch (Exception e) {}
    Dimension sz = getPreferredSize();
    setSize(450,300);
    AwtUtil.centerWindow(this);
  }

  public void run() {
    PalmDataSource palmApp = (PalmDataSource)appChoice.getSelectedItem();
    SyncController controller = new SyncController(ext, palmApp, rr, true);
    
    controller.doSync();
  }
  
  private void populateFields() {
    if(root.getParameter("PalmSync.syncAtStartUp","false").equals("true")) {
      syncAtStartBox.setSelected(true);
    } else {
      syncAtStartBox.setSelected(false);
    }
    
    String syncMode = root.getParameter("PalmSync.mode",palmApps[0].getID());
    appChoice.setSelectedIndex(0);
    for(int i=0; i<palmApps.length; i++) {
      if(syncMode.equals(palmApps[i].getID())) {
        appChoice.setSelectedIndex(i);
        break;
      }
    }
  }

  private final static int minmax(int min, int num, int max) {
    if(num < min)
      return min;
    if(num > max)
      return max;
    return min;
  }

  private final void okPressed() {
    if(root==null) return;
    root.setParameter("PalmSync.mode", ((PalmDataSource)appChoice.getSelectedItem()).getID());
    root.setParameter("PalmSync.syncAtStartUp", syncAtStartBox.isSelected()?"true":"false");
    ext.eraseConfigWindow();
    setVisible(false);
    dispose();
  }
  
  private final void configPressed() {
    if(root==null) return;
    PalmDataSource source = ((PalmDataSource)appChoice.getSelectedItem());
    try {
      source.showConfigWindow(root, rr, ext);
    } catch (Exception e) {
      e.printStackTrace(System.err);
      JOptionPane.showMessageDialog(this, rr.getString("error")+": "+e,
                                    rr.getString("error"),
                                    JOptionPane.INFORMATION_MESSAGE);
    }
  }
  
  public void actionPerformed(ActionEvent e) {
    Object src = e.getSource();
    if(src == nowButton) {
      okPressed();
      SwingUtilities.invokeLater(this);
    } else if(src == configButton) {
      configPressed();
    } else if(src == doneButton) {
      okPressed();
    } else if(src == helpButton) {
      HelpDialog hd = new HelpDialog(rr);
      hd.setVisible(true);
    }
  }


}

