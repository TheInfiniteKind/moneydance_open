package com.moneydance.modules.features.miscdebug;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.AwtUtil;
import java.io.*;
import java.util.Vector;
import javax.swing.*;
import javax.swing.event.*;
import java.awt.*;
import java.awt.event.*;

public class DebugWindow
  extends JDialog
{
  private RootAccount rootAccount;
  private JTextArea logArea;

  private boolean oldDebug;
  private PrintStream oldErr;
  
  public DebugWindow(RootAccount root) {
    super((Frame)null, "Information", false);

    this.rootAccount = root;

    logArea = new JTextArea(10,40);
    
    JPanel p = new JPanel(new GridBagLayout());
    p.add(new JScrollPane(logArea), AwtUtil.getConstraints(0,5,1,1,2,1,true,true,10,10,10,10));

    getContentPane().add(p);

    pack();
    setSize(getPreferredSize());

    oldDebug = com.moneydance.apps.md.controller.Main.DEBUG;
    oldErr = System.err;
    PrintStream newErr = new PrintStream(new ConsoleStream());
    System.setErr(newErr);
    com.moneydance.apps.md.controller.Main.DEBUG = true;
    enableEvents(WindowEvent.WINDOW_CLOSING);
  }
  
  public final void processEvent(AWTEvent evt) {
    int id = evt.getID();
    if(id==WindowEvent.WINDOW_CLOSING) {
      com.moneydance.apps.md.controller.Main.DEBUG = oldDebug;
      System.setErr(oldErr);
      setVisible(false);
      return;
    }
    super.processEvent(evt);
  }
  
  
  private class ConsoleStream
    extends OutputStream
    implements Runnable
  {    
    public void write(int b)
      throws IOException
    {
      logArea.append(String.valueOf((char)b));
      repaint();
    }
    public void write(byte[] b)
      throws IOException
    {
      logArea.append(new String(b));
      repaint();
    }
    public void run() {
      logArea.repaint();
    }
  }


}



