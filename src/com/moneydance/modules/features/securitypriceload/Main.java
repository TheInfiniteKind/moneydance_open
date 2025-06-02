/*
 * Copyright (c) 2014,  Michael Bray. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */ 
package com.moneydance.modules.features.securitypriceload;

import java.awt.Image;
import java.awt.Toolkit;
import java.io.ByteArrayOutputStream;

import javax.swing.JFrame;
import javax.swing.JPanel;

import com.infinitekind.util.CustomDateFormat;
import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.modules.features.mrbutil.MRBDebug;


/** Moneydance extension to load security prices from a file using exchange code as key
 * 
 * Main class to create main window
*/

public class Main
  extends FeatureModule
{
  public static CustomDateFormat cdate;
  public static FeatureModuleContext context;
  public static UserPreferences up;
  public static MRBDebug debugInst;
  public static Main extension;
  private static int buildNum;
  public static String buildStr;
  private JPanel panScreen;

  @Override
public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
	extension = this;
    context = getContext();
    try {
      context.registerFeature(this, "showconsole",
    	    getIcon("securitypriceload"),
    	    getName());
		debugInst = new MRBDebug();
		debugInst.setDebugLevel(MRBDebug.OFF);
		debugInst.setExtension("Security Price Load");
    }
    catch (Exception e) {
      e.printStackTrace(System.err);
    }
    buildNum = getBuild();
    buildStr = String.valueOf(buildNum);  }
  /*
   * Get Icon is not really needed as Icons are not used.  Included as the 
   * register feature method requires it
   */
  
  private Image getIcon(String action) {
	    try {
	      ClassLoader cl = getClass().getClassLoader();
	      java.io.InputStream in = 
	        cl.getResourceAsStream("/com/moneydance/modules/features/securitypriceload/iconip.gif");
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
  @Override
public void cleanup() {
    closeConsole();
  }
  
  
  /** Process an invocation of this module with the given URI */
  @Override
public void invoke(String uri) {
	  String command = uri;
	  String strDateFormat;
      up = UserPreferences.getInstance();
	  strDateFormat = up.getSetting(UserPreferences.DATE_FORMAT);
	  cdate = new CustomDateFormat(strDateFormat);
      int theIdx = uri.indexOf('?');
	  if(theIdx>=0) {
	      command = uri.substring(0, theIdx);
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
    return "Security Price Loader";
  }
  /**
   * Create the GUI and show it.  For thread safety,
   * this method should be invoked from the
   * event dispatch thread.
   */
  private void createAndShowGUI() {

      //Create and set up the window.
      JFrame frame = new JFrame("Load Security Prices - Build "+buildStr);
      frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
      panScreen = new FileSelectWindow();
      frame.getContentPane().add(panScreen);

      //Display the window.
      frame.pack();
      frame.setLocationRelativeTo(null);
      frame.setVisible(true);

  }
  private synchronized void showConsole() {
      //Schedule a job for the event dispatch thread:
      //creating and showing this application's GUI.
      javax.swing.SwingUtilities.invokeLater(new Runnable() {
          @Override
		public void run() {
              createAndShowGUI();
          }
      });

  }
  
  FeatureModuleContext getUnprotectedContext() {
    return getContext();
  }

  synchronized void closeConsole() {
    if(panScreen!=null) {
    	panScreen = null;
      System.gc();
    }
  }
}


