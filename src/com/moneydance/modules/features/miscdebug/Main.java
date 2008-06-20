/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.miscdebug;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.ModuleUtil;
import com.moneydance.apps.md.controller.UserPreferences;

import com.moneydance.apps.md.model.*;
import com.moneydance.apps.md.view.HomePageView;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.util.Constants;

import java.io.*;
import java.util.*;
import java.text.*;
import java.awt.*;

/** Extension used to examine moneydance and data file for errors */
public class Main
  extends FeatureModule
{

  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    context.registerFeature(this, "dodebug", 
                            getIcon("icon-debug"),
                            getName());
    context.registerHomePageView(this, new HPView());
  }
  
  private Image getIcon(String action) {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in = 
        cl.getResourceAsStream("/com/moneydance/modules/features/miscdebug/"+action+".gif");
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
    int colonIdx = uri.indexOf(':');
    if(colonIdx>=0) {
      command = uri.substring(0, colonIdx);
      parameters = uri.substring(colonIdx+1);
    }

    if(command.equals("dodebug")) {
      doDebug();
    }
  }

  public String getName() {
    return "Moneydance Debugging Helper";
  }

  private void doDebug() {
    RootAccount root = getContext().getRootAccount();
    if(root==null) return;

    DebugWindow debugWin = new DebugWindow(root);
    debugWin.setVisible(true);
    
  }

  public FeatureModuleContext getExtContext() {
    return getContext();
  }
  
  private class HPView 
  implements HomePageView
  {
    private javax.swing.JLabel label;
    
    HPView() {
      this.label = new javax.swing.JLabel("test test");
    }
    
    /** Returns a unique identifier for this view.  This identifier
      * must be unique across all identifiers for all extensions. */
    public String getID() {
      return "miscdebug_test";
    }
    
    /** Returns a short descriptive name of this view. */
    public String toString() {
      return "Debug Test";
    }
    
    /** Returns a GUI component that provides a view of the info panel
      for the given data file. */
    public javax.swing.JComponent getGUIView(RootAccount rootAccount) {
      return label;
    }
    
    /** Sets the view as active or inactive.  When not active, a view
      should not have any registered listeners with other parts of
      the program.  This will be called when an view is added to the
      home page, or the home page is refreshed after not being visible
      for a while.
      */
    public void setActive(boolean active) {
      FeatureModuleContext context = getContext();
    }
    
    /** Forces a refresh of the information in the view.
      For example, this is called after the preferences
      are updated.
      */
    public void refresh() {}
    
    /** Called when the view should clean up everything.  For
      example, this is called when a file is closed and the
      GUI is reset.  The view should disconnect from any resources
      that are associated with the currently opened data file.
      */
    public void reset() {}
    
  }
  
}

