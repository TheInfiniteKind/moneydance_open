/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.jpython;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.ModuleUtil;
import com.moneydance.apps.md.controller.UserPreferences;

import com.moneydance.apps.md.model.*;

import org.python.util.PythonInterpreter;
import org.python.core.*;

import java.io.*;
import java.util.*;
import java.text.*;
import java.awt.*;

/** Pluggable module used to give users access to a Python
    interface to Moneydance.
*/

public class Main
  extends FeatureModule
{
  private RootAccount root = null;
  private PythonWindow pythonWindow = null;

  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    try {
      context.registerFeature(this, "showconsole",
        getIcon("icon-pythonprompt"),
        getName());
    }
    catch (Exception e) {
      e.printStackTrace(System.err);
    }
  }

  public void cleanup() {
    closeConsole();
  }
  
  private Image getIcon(String action) {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in = 
        cl.getResourceAsStream("/com/moneydance/modules/features/jpython/"+action+".gif");
      if (in != null) {
        ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
        byte buf[] = new byte[256];
        int n = 0;
        while((n=in.read(buf, 0, buf.length))>=0)
          bout.write(buf, 0, n);
        return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
      }
    } catch (Throwable e) { }
    return null;
  }
  
  /** Process an invokation of this module with the given URI */
  public void invoke(String uri) {
    String command = uri;
    String parameters = "";
    int theIdx = uri.indexOf('?');
    if(theIdx>=0) {
      command = uri.substring(0, theIdx);
      parameters = uri.substring(theIdx+1);
    }
    else {
      theIdx = uri.indexOf(':');
      if(theIdx>=0) {
        command = uri.substring(0, theIdx);
      }
    }

    if(command.equals("showconsole")) {
      showConsole();
    }

    if(command.equals("runfile")||command.equals("runfile:")) {
      String filename = "";
      theIdx = parameters.indexOf('=');
      if(theIdx>=0) {
        filename = parameters.substring(theIdx+1);
      }
      File file = new File(filename);
      PythonInterpreter interpreter = new PythonInterpreter();
      interpreter.set("moneydance", getUnprotectedContext());
      runFile(file, interpreter);
    }
    
    if(command.equals("runresource")||command.equals("runresource:")) {
      String resourcename = "";
      theIdx = parameters.indexOf('=');
      if(theIdx>=0) {
        resourcename = parameters.substring(theIdx+1);
      }
      runResource(resourcename);
    }
  }

  public synchronized void runFile(File inputFile, PythonInterpreter interpreter) {
    BufferedReader reader = null;
    boolean fileNotFound = false;
    try {
      try {
        reader = new BufferedReader(new InputStreamReader(new FileInputStream(inputFile),"UTF8"));
      } catch (FileNotFoundException fnfe) {
        fileNotFound = true;
        System.err.println("Python input file not found.");
      }
    } catch (UnsupportedEncodingException uee) {
      System.err.println("Exception running file: "+uee);
    }
    if(!fileNotFound)
      runSource(interpreter, reader);
  }

  private synchronized void runResource(String resourceToRun) {
    PythonInterpreter interpreter = new PythonInterpreter();
    interpreter.set("moneydance", getUnprotectedContext());
    BufferedReader reader = null;
    boolean resNotFound = false;
    try {
      try {
        reader = new BufferedReader(new InputStreamReader(
          getClass().getClassLoader().getResourceAsStream(resourceToRun),"UTF8"));
      }
      catch(NullPointerException npe) {
         System.err.println("Resource not found.");
         resNotFound = true;
      }
    }
    catch(UnsupportedEncodingException uee) {
    }
    if(!resNotFound)
      runSource(interpreter, reader);
  }

  public String getName() {
    return "Python Interface";
  }

  public void runSource(PythonInterpreter interpreter,
                        BufferedReader reader) {
    boolean breakWhile = false;
    String currentLine;
    interpreter.exec("\n");
    try {
      while(!breakWhile) {
        if(reader.ready()) {
          currentLine = reader.readLine();
          System.err.println("reading line:>>>"+currentLine+"<<<");
          interpreter.exec(currentLine);
        } else {
          breakWhile = true;
        }
      }
    } catch(IOException ioe) {
      pythonWindow.addLine("Error Reading File : " + ioe + "\n");
    }
  }

  private synchronized void showConsole() {
    if(pythonWindow==null) {
      pythonWindow = new PythonWindow(this);
      pythonWindow.setVisible(true);
    }
    else {
      pythonWindow.setVisible(true);
      pythonWindow.toFront();
      pythonWindow.requestFocus();
    }
  }
  
  FeatureModuleContext getUnprotectedContext() {
    return getContext();
  }

  synchronized void closeConsole() {
    if(pythonWindow!=null) {
      pythonWindow.goAway();
      pythonWindow = null;
      System.gc();
    }
  }
}


