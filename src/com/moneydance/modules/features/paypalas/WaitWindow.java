/************************************************************\
 *        Copyright 2017 The Infinite Kind, Limited         *
\************************************************************/

package com.moneydance.modules.features.paypalas;

import com.moneydance.awt.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.border.*;

public class WaitWindow
  extends JDialog
  implements Runnable
{

  private Task task = null;
  private Thread taskThread = null;
  private JLabel label;
  private JProgressBar progressBar = null;
  private Throwable taskException = null;
  private Component parent;

  public WaitWindow(JDialog parent) {
    this(parent, false);
  }
  
  public WaitWindow(Component parent, boolean showProgress) {
    super((Frame)null, "", true);

    this.parent = parent;
    
    JPanel p = new JPanel(new GridBagLayout());
    p.setBorder(new EmptyBorder(15,15,15,15));
    label = new JLabel(" ",SwingConstants.CENTER);
    if(showProgress)
      progressBar = new JProgressBar(0, 100);

    int y = 0;
    p.add(new JLabel(" "), AwtUtil.getConstraints(0,y++,1,1,1,1,true,true));
    p.add(label, AwtUtil.getConstraints(1,y++,1,1,1,1,true,true));
    if(showProgress) {
      p.add(progressBar, AwtUtil.getConstraints(1,y++,1,0,1,1,true,true));
    }
    p.add(new JLabel(" "), AwtUtil.getConstraints(2,y++,1,1,1,1,true,true));
    
    getContentPane().add(p);

    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);
    enableEvents(WindowEvent.WINDOW_OPENED);
  }

  public void setValue(int value) {
    if(progressBar!=null) {
      progressBar.setValue(Math.max(0, Math.min(100,value)));
      progressBar.repaint();
    }
  }
  
  public void setLabel(String newValue) {
    label.setText(newValue);
    label.repaint();
  }
  
  public synchronized void invokeTask(Task task, String taskLabel)
    throws Throwable
  {
    label.setText(taskLabel);
    try { pack(); } catch (Exception e) {}
    Dimension prefSize = getPreferredSize();
    setSize(prefSize.width+120, prefSize.height+20);
    AwtUtil.setWindowPosition(this, parent);
    
    this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
    this.task = task;
    this.taskThread = new Thread(this, taskLabel);
    this.taskThread.start();
    setVisible(true);
    this.taskThread = null;
    if(taskException!=null) {
      Throwable te = taskException;
      taskException = null;
      throw te;
    }
  }

  public void run() {
    // wait until the window becomes visible...
    while(!isVisible()) {
      try {
        Thread.currentThread().sleep(500);
      } catch (Throwable e) {}
    }
      
    try {
      task.performTask();
    } catch (Throwable e) {
      taskException = e;
    } finally {
      taskFinished();
    }
  }

  public final void processEvent(AWTEvent evt) {
    int id = evt.getID();
    if(id==WindowEvent.WINDOW_CLOSING) {
      if(task==null)
        setVisible(false);
      return;
    } else if(id==WindowEvent.WINDOW_OPENED) {
      requestFocus();
    }
    super.processEvent(evt);
  }
  
  private void taskFinished() {
    this.task = null;
    this.taskThread = null;
    SwingUtilities.invokeLater(new Runnable() {
      public void run() {
        setVisible(false);
      }
    });
  }

}
