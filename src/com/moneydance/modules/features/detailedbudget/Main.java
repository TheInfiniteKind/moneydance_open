package com.moneydance.modules.features.detailedbudget;

import java.awt.Image;
import java.awt.Toolkit;
import java.io.ByteArrayOutputStream;
import java.io.IOException;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;

/** Pluggable module used to give users access to a Account List
    interface to Moneydance.
*/

public class Main
  extends FeatureModule
{
//  private AccountListWindow accountListWindow = null;
  private BudgetSettingsWindow budgetSettingsWindow = null;

  @Override
public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    try {
      context.registerFeature(this, "showconsole", getIcon(), getName());
    }
    catch (Exception e) {
      e.printStackTrace(System.err);
    }
    
  }

  @Override
public void cleanup() {
    closeConsole();
  }
  
  private Image getIcon() {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in = 
        cl.getResourceAsStream("/com/moneydance/modules/features/myextension/icon.gif");
      if (in != null) {
        ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
        byte buf[] = new byte[256];
        int n = 0;
        while((n=in.read(buf, 0, buf.length))>=0)
          bout.write(buf, 0, n);
        return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
      }
    } catch (IOException e) {
    	// TODO(divegeek) Figure out what's appropriate here.
    }
    return null;
  }
  
  /** Process an invokation of this module with the given URI */
  @Override
public void invoke(String uri) {
    String command = uri;
    //String parameters = "";
    int theIdx = uri.indexOf('?');
    if(theIdx>=0) {
      command = uri.substring(0, theIdx);
      /*parameters =*/uri.substring(theIdx+1);
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
  }

  @Override
public String getName() {
    return "Detailed Budget";
  }

  private synchronized void showConsole() {
    if(budgetSettingsWindow==null) {
    	budgetSettingsWindow = new BudgetSettingsWindow(this);
    	budgetSettingsWindow.setVisible(true);
    }
    else {
    	budgetSettingsWindow.setVisible(true);
    	budgetSettingsWindow.toFront();
    	budgetSettingsWindow.requestFocus();
    }
  }
  
  FeatureModuleContext getUnprotectedContext() {
    return getContext();
  }

  synchronized void closeConsole() {
    if(budgetSettingsWindow!=null) {
    	budgetSettingsWindow.goAway();
    	budgetSettingsWindow = null;
      System.gc();
    }
  }
}


