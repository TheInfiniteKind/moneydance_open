/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.console;

import com.moneydance.awt.*;
import javax.swing.*;
import java.text.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.border.*;

/** Window used to show console events
  ------------------------------------------------------------------------
  $Author: sreilly $			$Date: 2002/01/29 00:13:40 $
  $Revision: 1.5 $
*/

public class ConsoleWindow 
  extends JFrame
  implements ActionListener
{
  private Main extension;
  private JTextArea consoleArea;
  private JButton clearButton;
  private JButton closeButton;
  
  public ConsoleWindow(Main extension) {
    super("Event Console");
    this.extension = extension;

    consoleArea = new JTextArea();
    consoleArea.setEditable(false);
    clearButton = new JButton("Clear");
    closeButton = new JButton("Close");

    JPanel p = new JPanel(new BorderLayout());
    JPanel bp = new JPanel(new GridBagLayout());
    bp.setBorder(new EmptyBorder(10,10,10,10));
    p.add(new JScrollPane(consoleArea), BorderLayout.CENTER);
    p.add(bp, BorderLayout.SOUTH);
    
    GridBagConstraints c = new GridBagConstraints();
    c.gridx=0;
    c.gridy=0;
    c.weightx=0;
    c.weighty=0;
    bp.add(clearButton, c);
    c.gridx++;
    c.weightx=1;
    bp.add(new JLabel(" "), c);
    c.gridx++;
    c.weightx=0;
    bp.add(closeButton, c);
    getContentPane().add(p);

    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);
    closeButton.addActionListener(this);
    clearButton.addActionListener(this);

    pack();
    setSize(500, 350);
    AwtUtil.centerWindow(this);
  }

  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    if(src==closeButton) {
      extension.closeConsole();
    } else if(src==clearButton) {
      extension.resetBuffer();
    }
  }

  public final void processEvent(AWTEvent evt) {
    if(evt.getID()==WindowEvent.WINDOW_CLOSING) {
      extension.closeConsole();
      return;
    }
    super.processEvent(evt);
  }
  
  void reset() {
    consoleArea.setText("");
  }

  void addLine(String line) {
    consoleArea.append(line);
    consoleArea.append("\n");
    consoleArea.repaint();
  }

}
