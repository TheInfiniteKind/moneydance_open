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

public class PocketmoneyDirConfig
  extends JDialog 
  implements ActionListener 
{
  private RootAccount root = null;
  private Resources rr;
  private Main ext;
  
  private boolean wasCanceled = true;

  private JTextField dirField;
  private JButton browseButton;
  private JButton okButton;
  private JButton cancelButton;

  public PocketmoneyDirConfig(Main ext, Resources rr, RootAccount root) {
    super(ext.getFrame(), rr.getString("config_settings"), true);
    this.ext = ext;
    this.root = root;
    this.rr = rr;

    okButton = new JButton(rr.getString("OK"));
    cancelButton = new JButton(rr.getString("cancel"));
    browseButton = new JButton(rr.getString("browse_button_label"));
    dirField = new JTextField(root.getParameter("PalmSync.pdbdir","."), 30);

    int y = 0;
    JPanel p = new JPanel(new GridBagLayout());
    p.add(new JTextPanel(rr.getString("select_pdbdir")),
          AwtUtil.getConstraints(0,y++,1,0,3,1,true,true));
    p.add(Box.createVerticalStrut(12),
          AwtUtil.getConstraints(0,y++,0,0,3,1,true,true));
    p.add(new JLabel(rr.getString("backup_dir")+": ", JLabel.RIGHT),
          AwtUtil.getConstraints(0,y,0,0,1,1,true,true));
    p.add(dirField,
          AwtUtil.getConstraints(1,y,1,0,1,1,true,true));
    p.add(browseButton,
          AwtUtil.getConstraints(2,y++,0,0,1,1,true,true));
    p.add(Box.createVerticalStrut(12),
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
    setSize(minmax(200, sz.width, 400), minmax(200, sz.height, 400));
    AwtUtil.centerWindow(this);
  }
  
  private static final int minmax(int min, int num, int max) {
    if(num<min) return min;
    if(num>max) return max;
    return min;
  }

  private void okPressed() {
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

