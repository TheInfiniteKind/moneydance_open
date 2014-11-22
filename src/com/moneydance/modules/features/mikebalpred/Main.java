/************************************************************\
 * Portions Copyright (C) 2008 Reilly Technologies, L.L.C.   *
\************************************************************/

package com.moneydance.modules.features.mikebalpred;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
//import com.moneydance.apps.md.controller.ModuleUtil;
import com.infinitekind.moneydance.model.*;
//import com.infinitekind.util.StreamTable;

import java.io.*;
//import java.net.*;
import java.awt.*;
//import javax.swing.JOptionPane;
import java.lang.System;

public class Main
  extends FeatureModule
{
  public String command;
  public String parameters;
//  private BalancePredicter bp = null;
  
  public void setParameters(String par) { parameters = par; }
  public void setCommand(String cmd) { command = cmd; }
  public String getCommand() { return command; }
  public String getParameters() { return parameters; }
//  private Resources rr = null;;

//  private Wizard balpredWizard = null;
  private BalancePredicter win;     // main window to display

  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    getContext().registerFeature(this, "Mike's Balance Predictor", getIcon("mikebalpred"), getName());

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

    showBalancePredicter();
  }

  public String getName() {
    return "Mike's Balance Predictor";
  }

  public AccountBook getBook() {
    return getContext().getCurrentAccountBook();
  }

  private synchronized void showBalancePredicter() {
		System.out.println("^^^^ entering showBalancePredicter");
    if(win==null || !win.isVisible()) {
      if(win!=null) {
        win.setVisible(false);
				System.out.println("^^^^ disposed old win");
      }
      BalPredConf conf = new BalPredConf(getBook(), getName());
			System.out.println("^^^^ made new BalPredConf");
      FeatureModuleContext context = getContext();
      if(context instanceof com.moneydance.apps.md.controller.Main) {
        conf.dateFormatStr = ((com.moneydance.apps.md.controller.Main)context).getPreferences().getShortDateFormat();
      }
      win = new BalancePredicter(conf); // Wizard(null, rr, getName(), new SelectAccount(conf), false);
			System.out.println("^^^^ made new win");
      win.setVisible(true);
    } else {
      win.setVisible(true);
      win.toFront();
      win.requestFocus();
			System.out.println("^^^^ using old win");
    }
  }

}
