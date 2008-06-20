/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.paypalas;

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
  private PayPalWindow extensionWindow = null;
  private Resources rr = null;;
  private com.moneydance.apps.md.controller.Main appMain = null;

  public void init() {
    FeatureModuleContext context = getContext();
    if(context instanceof com.moneydance.apps.md.controller.Main) {
      appMain = (com.moneydance.apps.md.controller.Main)context;
    }
    context.registerFeature(this, "PayPal Account Synchronizer", getIcon("paypalas"), getName());

    rr = (Resources)java.util.ResourceBundle.
      getBundle("com.moneydance.modules.features.paypalas.Resources", java.util.Locale.getDefault());
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
    }
    else setCommand(uri);

    String javaVersion = System.getProperty("java.version","");
    if(javaVersion.startsWith("1.1")) {
      JOptionPane.
        showMessageDialog(null,
                          "Sorry, this extension requires Java 1.2 or higher.",
                          "Error", JOptionPane.ERROR_MESSAGE);
      return;
    }

    showPayPalWindow();
  }

  public String getName() {
    return "PayPal Account Synchronizer";
  }

  public RootAccount getRoot() {
    return getContext().getRootAccount();
  }

  private synchronized void showPayPalWindow() {
    if(extensionWindow==null) {
      extensionWindow = new PayPalWindow(this);
      extensionWindow.setVisible(true);
    } else {
      extensionWindow.removeAllPayPalAccounts();
      extensionWindow.removeAllAccounts();
      extensionWindow.loadPayPalAccounts(getRoot());
      extensionWindow.setUserID();
      extensionWindow.loadAccounts(getRoot());
      extensionWindow.setVisible(true);
      extensionWindow.toFront();
      extensionWindow.requestFocus();
    }
  }

  synchronized void closePayPalWindow() {
    if(extensionWindow!=null) {
      extensionWindow.setVisible(false);
    }
  }

  public com.moneydance.apps.md.controller.Main getAppMain() {
    return appMain;
  }
}
