/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.ModuleUtil;
import com.moneydance.apps.md.controller.UserPreferences;

import com.moneydance.awt.*;

import com.infinitekind.moneydance.model.*;

import java.util.Vector;
import java.io.*;
import java.util.*;
import java.text.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.SwingUtilities;
import javax.swing.JFrame;
import javax.swing.event.*;
import javax.swing.border.*;
import java.net.*;

/** Pluggable module used to synchronize palm expense files with Moneydance.
*/

public class Main
  extends FeatureModule
{
  private Resources rr = null;
  private ModeWindow configWindow = null;

  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    rr = (Resources)java.util.ResourceBundle.
      getBundle("com.moneydance.modules.features.palmsync.Resources", 
                java.util.Locale.getDefault());
    try {
      context.registerFeature(this, "showcfgwindow",
        getIcon("palmpilot"),
        getName());
    } catch (Exception e) {
      e.printStackTrace(System.err);
    }
  }

  public Frame getFrame() {
    return configWindow;
  }

  public RootAccount getRoot() {
    return getContext().getRootAccount();
  }

  private Image getIcon(String action) {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in = 
        cl.getResourceAsStream("/com/moneydance/modules/features/palmsync/palmpilot.gif");
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

    if(command.equals("showcfgwindow")) {
      showConfigWindow();
    }
  }

  void eraseConfigWindow() {
    configWindow = null;
  }
  
  private void showConfigWindow()  {
    RootAccount root = getRoot();
   
    if(root != null) {
      if(configWindow==null) {
        configWindow = new ModeWindow(this, root, rr);
      }
      configWindow.setVisible(true);
      configWindow.toFront();
      configWindow.requestFocus();
    }
  }
  
  public void handleEvent(String appEvent) {
    if(appEvent.startsWith("md:file:opened")) {
      RootAccount root = getRoot();
      if(root==null) return;
      if(!root.getParameter("PalmSync.syncAtStartUp","").equals("true")) return;
      SyncController controller = null;
      PalmDataSource dataSource = 
        PalmDataSource.getDataSource(root.getParameter("PalmSync.mode",""));
      if(dataSource==null) return;
      controller = new SyncController(this, dataSource, rr, false);
      controller.doSync();
    }
  }
  
  public String getName() {
    return "Palm PDA Synchronization";
  }

}

