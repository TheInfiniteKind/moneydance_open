/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;

import java.sql.Timestamp;
import java.util.Observable;
import java.util.Observer;
import java.io.*;
import java.awt.*;

/** Module used to give users access to a Account List
    interface to Moneydance.
*/

public class Main extends FeatureModule implements Observer {
  private BudgetWindow                 mainWindow = null;
  private BudgetForecast               castWindow = null;
  private BudgetReportWindow           rprtWindow = null;
  private BudgetHomePageViewController homeView   = null;
  private BudgetPreferences            prefs;
  private BudgetData                   data;
  
  public Main(){
	  
  }
  
  public void init() {
	this.setup();
	this.homeView = new BudgetHomePageViewController(this);

    try {
      this.getContext().registerHomePageView(this, this.homeView);
      this.getContext().registerFeature(this, "showPie", getIcon("accountlist"), getName());
    }
    catch (Exception e) {
      e.printStackTrace(System.err);
    }
  }
  
  protected void setup(){
	if(this.prefs == null){
		  this.prefs  = new BudgetPreferences();
		  this.prefs.setContext(this.getContext());
	      this.prefs.addObserver(this);
	} 

	if(this.getRoot() != null){
		if(this.data == null){
			this.data = new BudgetData(this);
		}
		
		if(mainWindow == null) {
	    	mainWindow = new BudgetWindow(this);
	    } else {
	    	mainWindow.refresh();
	    }
		
		if(castWindow == null){
			BudgetForecastConf conf = new BudgetForecastConf(this.getBook(), 
					  "Forecast: " + this.data.getCurrentBudgetName() + 
					  " (" + data.getCurrentBudgetYear() + ") ");
			
			castWindow = new BudgetForecast(this, conf);
		}

		if(rprtWindow == null){
			rprtWindow = new BudgetReportWindow(this);
		} else {
			rprtWindow.updateReport();
		}
	  }
  }
  
  public String getName(){
	  return "MoneyPie";
  }
  
  public int getBuild(){
	  return 1007;
  }

  public void cleanup() {
    closeConsole();
  }
  
  protected AccountBook getBook() {
	    return getContext().getRootAccount().getBook();
  }
  
  protected Account getRoot() {
	    return getContext().getRootAccount();
  }

  
  public BudgetWindow getWindow(){
	  return this.mainWindow;
  }

  public void update(final Observable observable, final Object updateAll) {
      this.prefs.setContext(this.getContext());
  }
  
  protected FeatureModuleContext getUnprotectedContext() {
	  return this.getContext();
  }
	  
  protected BudgetPreferences getPreferences(){
	  return this.prefs;
  }
  
  protected BudgetData getBudgetData(){
	  return this.data;
  }
  

  /** Process an invocation of this module with the given URI */
  public void invoke(String uri) {
    String command = uri;
    int theIdx = uri.indexOf('?');
    if(theIdx>=0) {
      command = uri.substring(0, theIdx);
    } else {
      theIdx = uri.indexOf(':');
      if(theIdx>=0) {
        command = uri.substring(0, theIdx);
      }
    }

    if(command.equals("showPie")) {
    	showPie();
    }
  }
  
  void println(String message){
	  java.util.Date date= new java.util.Date();
	  System.err.println(new Timestamp(date.getTime()) + " : " + message);
  }

  protected synchronized void showPie() {
	  this.setup();
	  
	  mainWindow.setVisible(true);
  	  mainWindow.toFront();
  	  mainWindow.requestFocus();
  }
  
  protected void showForecast(){
	  this.setup();

	  castWindow.setWaitCursor();
	  castWindow.refresh();
	  castWindow.setDefaultCursor();
	  
	  castWindow.setVisible(true);
	  castWindow.toFront();
	  castWindow.requestFocus();
  }
  
  protected void showReport(){
	  this.setup();

	  rprtWindow.setVisible(true);
	  rprtWindow.toFront();
	  rprtWindow.requestFocus();
  }

  synchronized void closeConsole() {
    if(mainWindow!=null) {
    	mainWindow.goAway();
    	mainWindow = null;
        System.gc();
    }
  }
  
  private Image getIcon(String action) {
	    try {
	      ClassLoader cl = getClass().getClassLoader();
	      java.io.InputStream in =
	        cl.getResourceAsStream("/com/moneydance/modules/features/myextension/images/icon.gif");
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
}


