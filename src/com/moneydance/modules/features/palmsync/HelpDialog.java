/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.awt.*;
import com.moneydance.apps.md.controller.Common;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.util.StringUtils;

import javax.swing.event.*;
import java.net.*;
import javax.swing.table.AbstractTableModel;
import java.io.*;
import java.util.*;
import javax.swing.*;
import java.text.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.JFrame;
import javax.swing.JTable;
import javax.swing.table.AbstractTableModel;
import javax.swing.JScrollPane;
import javax.swing.SwingUtilities;
import javax.swing.border.*;
import java.util.Vector;
import java.net.URL;

public class HelpDialog extends JDialog implements ActionListener {
    JButton doneButton;
    Resources rr;
    JEditorPane htmlArea;
    
    public HelpDialog(Resources rr) {
        super(new Frame(), rr.getString("help_title"),true);
        this.rr = rr;
        htmlArea = new JEditorPane();
        htmlArea.setEditable(false);        
        doneButton = new JButton(rr.getString("done_button_label"));
        doneButton.addActionListener(this);
        
        try {
          htmlArea.setContentType("text/html");
          htmlArea.setText(getTxt());
          htmlArea.setCaretPosition(0);
        } catch (Exception e) {
          System.err.println("got exception: "+e);
          e.printStackTrace(System.err);
        }

        JPanel p = new JPanel(new GridBagLayout());
        p.add(new JScrollPane(htmlArea), AwtUtil.getConstraints(1,0,1,1,5,10,true,true));
        p.add(Box.createHorizontalStrut(12), AwtUtil.getConstraints(0,11,0,0,5,1,true,true));
        p.add(doneButton, AwtUtil.getConstraints(5,11,0,0,1,1,false,false));
        p.setBorder(new EmptyBorder(16,16,12,16));
        getContentPane().add(p);
        pack();
        setSize(600,450);
        AwtUtil.centerWindow(this);
    }
  
  private String getTxt() {
    StringBuffer sb = new StringBuffer(500);
    try {
      InputStream in = getClass().getResourceAsStream(Common.HELP_RSRC);
      BufferedReader rdr = new BufferedReader(new InputStreamReader(in, "UTF8"));
      while(true) {
        String line = rdr.readLine();
        if(line==null)
          break;
        sb.append("  ");
        sb.append(line);
        sb.append("  ");
        sb.append("\n");
      }
    } catch (Exception e) {
      System.err.println("Unable to access help info: "+e);
      e.printStackTrace(System.err);
    }
    return sb.toString();
  }  
  
  public void actionPerformed(ActionEvent e) {
    Object src = e.getSource();
    if(src == doneButton) {
      setVisible(false);
      dispose();
    }
  }
}