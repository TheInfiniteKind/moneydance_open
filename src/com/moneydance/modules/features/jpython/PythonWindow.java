/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.jpython;

import com.moneydance.awt.*;
import com.moneydance.apps.md.controller.Common;
import com.moneydance.apps.md.controller.Util;

import org.python.util.InteractiveConsole;
import org.python.core.*;

import java.io.*;
import java.util.*;
import javax.swing.*;
import java.text.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.border.*;

/** Window used for Python interface
*/

public class PythonWindow 
  extends JFrame
  implements ActionListener
{
  private Main extension;
  private JTextArea pythonArea;
  private JTextField inputArea;
  private JButton clearButton;
  private JButton closeButton;
  private JButton readFile;
  private InteractiveConsole interpreter;
  private Resources rr = null;

  public PythonWindow(Main extension) {
    super("Python Console");
    this.extension = extension;

    rr = (Resources)java.util.ResourceBundle.
      getBundle("com.moneydance.modules.features.jpython.Resources", java.util.Locale.getDefault());

    pythonArea = new JTextArea();
    pythonArea.setEditable(false);
    inputArea = new JTextField();
    inputArea.setEditable(true);
    clearButton = new JButton(rr.getString("clear"));
    closeButton = new JButton(rr.getString("close"));
    readFile = new JButton(rr.getString("r_f"));

    JPanel p = new JPanel(new GridBagLayout());
    //p.setBorder(new EmptyBorder(10,10,10,10));
    p.add(new JScrollPane(pythonArea), GridC.getc(0,0).wxy(1,1).colspan(4).fillboth());
    p.add(inputArea, GridC.getc(0,1).colspan(4).fillboth().insets(2,0,8,0));
    p.add(clearButton, GridC.getc(0,2).insets(4,4,4,4));
    p.add(Box.createHorizontalStrut(200), GridC.getc(1,2).wx(1));
    p.add(readFile, GridC.getc(3,2).insets(4,4,4,4));
    getContentPane().add(p);
    
    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);
    closeButton.addActionListener(this);
    clearButton.addActionListener(this);
    readFile.addActionListener(this);
    inputArea.addActionListener(this);

    //Prepares system for Python interpreter.

    try {
      File pythonJarFile = new File(Common.getFeatureModulesDirectory(), "jpython.jar");
      File origPythonJarFile = new File(Common.getFeatureModulesDirectory(), "jpython.mxt");
      try {
        Util.copyFile(origPythonJarFile,pythonJarFile);
      }
      catch (Exception e) {
        System.err.println("Exception.");
      }
      Properties props = System.getProperties();
      String newClassPath = props.getProperty("java.class.path");
      newClassPath = newClassPath + File.pathSeparator + pythonJarFile.getCanonicalPath();
      props.put("java.class.path", newClassPath);
      String pythonHome = Common.getTemporaryDirectory() + File.separator + "pythonTemp";
      File pHome = new File(pythonHome);
      pHome.mkdir();
      props.put("python.home", pHome.toString());
      System.setProperties(props);
    }
    catch (IOException ioe) {
      System.err.println("IO Exception.");
    }
        
    //Redirect System.out to the pythonArea
    PrintStream c = new PrintStream(new ConsoleStream());

    //Instantiate the interpreter.
    interpreter=new InteractiveConsole();
    interpreter.setOut(c);
    interpreter.setErr(c);

    //Give it the context
    interpreter.set("moneydance", extension.getUnprotectedContext());

    pack();
    setSize(500,400);
    AwtUtil.centerWindow(this);
  }

  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    if(src==closeButton) {
      extension.closeConsole();
    }
    if(src==clearButton) {
      pythonArea.setText("");
    }
    if(src==inputArea) {
      processInputCommand();
    }
    if(src==readFile) {
      addLine("\n");
      readAFile();
      addLine(">>> ");
    }
  }

  private void readAFile() {
    FileDialog fwin = new FileDialog(this, "Choose Python Script File");
    fwin.setVisible(true);
    String filename = fwin.getFile();
    String dirname = fwin.getDirectory();
    if(filename==null || dirname==null) return;
    extension.runFile(new File(new File(dirname), filename), interpreter);
  }

  private void processInputCommand() {
    String theCommand=inputArea.getText();
    inputArea.setText("");
    addLine(theCommand+"\n");
    executePythonStatement(theCommand);
  }

  public void executePythonStatement(String theCommand) {
    if(interpreter.push(theCommand))
      addLine("... ");
    else
      addLine(">>> ");
  }

  public final void processEvent(AWTEvent evt) {
    if(evt.getID()==WindowEvent.WINDOW_CLOSING) {
      extension.closeConsole();
      return;
    }
    if(evt.getID()==WindowEvent.WINDOW_OPENED) {
      addLine(">>> ");
      inputArea.requestFocus();
    }
    super.processEvent(evt);
  }

  void goAway() {
    setVisible(false);
    dispose();
  }

  private class ConsoleStream
    extends OutputStream
    implements Runnable
  {    
    public void write(int b)
      throws IOException
    {
      pythonArea.append(String.valueOf((char)b));
      repaint();
    }
    public void write(byte[] b)
      throws IOException
    {
      pythonArea.append(new String(b));
      repaint();
    }
    public void run() {
      pythonArea.repaint();
    }
  }

  void addLine(String line) {
    pythonArea.append(line);
    pythonArea.repaint();
  }
}
