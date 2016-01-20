/************************************************************\
 *       Copyright (C) 2001 Appgen Personal Software        *
\************************************************************/

package com.moneydance.modules.features.detailedbudget;

import java.awt.AWTEvent;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;

import javax.swing.Box;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.WindowConstants;
import javax.swing.border.EmptyBorder;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.AwtUtil;

/** Window used for Account List interface
  ------------------------------------------------------------------------
*/

public class AccountListWindow 
  extends JFrame
  implements ActionListener
{
  private static final long serialVersionUID = 1L;
  
  private Main extension;
  private JTextArea accountListArea;
  private JButton clearButton;
  private JButton closeButton;
  private JTextField inputArea;

  public AccountListWindow(Main extension) {
    super("Account List Console");
    this.extension = extension;

    accountListArea = new JTextArea();
    
    AccountBook book = extension.getUnprotectedContext().getCurrentAccountBook();
    StringBuffer acctStr = new StringBuffer();
    if(book != null) {
      addSubAccounts(book.getRootAccount(), acctStr);
    }
    accountListArea.setEditable(false);
    accountListArea.setText(acctStr.toString());
    inputArea = new JTextField();
    inputArea.setEditable(true);
    clearButton = new JButton("Clear");
    closeButton = new JButton("Close");

    JPanel p = new JPanel(new GridBagLayout());
    p.setBorder(new EmptyBorder(10,10,10,10));
    p.add(new JScrollPane(accountListArea), AwtUtil.getConstraints(0,0,1,1,4,1,true,true));
    p.add(Box.createVerticalStrut(8), AwtUtil.getConstraints(0,2,0,0,1,1,false,false));
    p.add(clearButton, AwtUtil.getConstraints(0,3,1,0,1,1,false,true));
    p.add(closeButton, AwtUtil.getConstraints(1,3,1,0,1,1,false,true));
    getContentPane().add(p);

    setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);
    closeButton.addActionListener(this);
    clearButton.addActionListener(this);
        
    /*PrintStream c = */new PrintStream(new ConsoleStream());

    setSize(500, 400);
    AwtUtil.centerWindow(this);
  }

  public static void addSubAccounts(Account parentAcct, StringBuffer acctStr) {
    int sz = parentAcct.getSubAccountCount();
    for(int i=0; i<sz; i++) {
      Account acct = parentAcct.getSubAccount(i);
      acctStr.append(acct.getFullAccountName());
      acctStr.append("\n");
      addSubAccounts(acct, acctStr);
    }
  }


  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    if(src==closeButton) {
      extension.closeConsole();
    }
    if(src==clearButton) {
      accountListArea.setText("");
    }
  }

  @Override
public final void processEvent(AWTEvent evt) {
    if(evt.getID()==WindowEvent.WINDOW_CLOSING) {
      extension.closeConsole();
      return;
    }
    super.processEvent(evt);
  }
  
  private class ConsoleStream
    extends OutputStream
    implements Runnable
  {    
    @Override
	public void write(int b)
      throws IOException
    {
      accountListArea.append(String.valueOf((char)b));
      repaint();
    }

    @Override
	public void write(byte[] b)
      throws IOException
    {
      accountListArea.append(new String(b));
      repaint();
    }
    public void run() {
      accountListArea.repaint();
    }
  }

  void goAway() {
    setVisible(false);
    dispose();
  }
}
