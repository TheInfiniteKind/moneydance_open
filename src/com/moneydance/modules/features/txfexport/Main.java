/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.txfexport;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.ModuleUtil;
import com.moneydance.apps.md.model.*;
import com.moneydance.util.StreamTable;

import java.io.*;
import java.net.*;
import java.awt.*;
import javax.swing.JOptionPane;

public class Main
  extends FeatureModule
{
  public String command;
  public String parameters;
  
  public void setParameters(String par) { parameters = par; }
  public void setCommand(String cmd) { command = cmd; }
  public String getCommand() { return command; }
  public String getParameters() { return parameters; }
  private TXFExport extensionWindow = null;
  private Resources rr = null;
  private FeatureModuleContext context;

  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    context = getContext();
    context.registerFeature(this, "TXF Export", getIcon("txfexport"), getName());

    rr = (Resources)java.util.ResourceBundle.
      getBundle("com.moneydance.modules.features.txfexport.Resources", java.util.Locale.getDefault());
  }

  private Image getIcon(String action) {
    try {
      InputStream in = 
        getClass().getClassLoader().getResourceAsStream("/com/moneydance/modules/features/"+action+"/"+action+"_icon.gif");
      if (in != null) {
        ByteArrayOutputStream bout = new ByteArrayOutputStream(2000);
        byte buf[] = new byte[256];
        int n = 0;
        while((n=in.read(buf, 0, buf.length))>=0)
          bout.write(buf, 0, n);
        return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
      }
    } catch (Throwable e) { }
    return null;
  }

  public void invoke(String uri) {
    setParameters("");
    int colonIdx = uri.indexOf(':');
    if(colonIdx>=0) {
      setCommand(uri.substring(0, colonIdx));
      setParameters(uri.substring(colonIdx+1));
    } else {
      setCommand(uri);
    }

    showTXFExport();
  }

  public String getName() {
    return "TXF Export";
  }

  public RootAccount getRoot() {
    return getContext().getRootAccount();
  }
  
  public Resources getResources() {
    return rr;
  }

  private synchronized void showTXFExport() {
    if(extensionWindow==null) {
      extensionWindow = new TXFExport(this, context);
      extensionWindow.setVisible(true);
    } else {
      extensionWindow.setVisible(true);
      extensionWindow.toFront();
      extensionWindow.requestFocus();
    }
  }

  synchronized void closeTXFExport() {
    if(extensionWindow!=null) {
      extensionWindow.setVisible(false);
    }
  }

}
