/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.txtimport;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.ModuleUtil;
import com.moneydance.apps.md.model.*;
import com.moneydance.awt.*;

import java.io.*;
import java.awt.*;
import javax.swing.*;

/** Transaction Import module
*/

public class Main
  extends FeatureModule
{
  private String command;
  private String filename;
  private Integer accountNo;

  private Resources rr = null;

  private Wizard importWizard = null;
  
  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar

    rr = (Resources)java.util.ResourceBundle.
      getBundle("com.moneydance.modules.features.txtimport.Resources", java.util.Locale.getDefault());

    getContext().registerFeature(this, "TxtImport", getIcon("txtimport"), getName());
  }

  public void invoke(String uri) {
    int colonIdx = uri.indexOf(':');
    if(colonIdx>=0) {
      this.command = uri.substring(0, colonIdx);
    } else {
      this.command = uri;
    }
    int theIdx = uri.indexOf('?');
    if(theIdx>=0) {
      String parameters = uri.substring(theIdx+1);

      int fileIdx   = parameters.indexOf("file=");
      if (fileIdx>=0) {
        this.filename    = parameters.substring(fileIdx+5);
        int ampersandIdx = this.filename.indexOf('&');
        if (ampersandIdx>= 0) {
          this.filename = this.filename.substring(0, ampersandIdx);
        }
      }

      int accountNoIdx = parameters.indexOf("accountno=");
      if (accountNoIdx>=0) {
        String accountNo  = parameters.substring(accountNoIdx+10);
        int ampersandIdx  = accountNo.indexOf('&');
        if (ampersandIdx>= 0) {
          accountNo = accountNo.substring(0, ampersandIdx);
        }
        if (accountNo.length() > 0) {
           this.accountNo = Integer.valueOf(accountNo);
        }
      }
    }

    showTxtImport();
  }

  com.moneydance.apps.md.controller.Main getMainController() {
    return (com.moneydance.apps.md.controller.Main)getContext();
  }
  
  private Image getIcon(String action) {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in = 
        cl.getResourceAsStream("/com/moneydance/modules/features/"+action+"/"+action+"_icon.gif");
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
  
  public RootAccount getRoot() {
    return getContext().getRootAccount();
  }

  public String getName() {
    return "Text File Importer";
  }

  private synchronized void showTxtImport() {
    RootAccount root = getContext().getRootAccount();
    if(root==null) {
      JOptionPane.
        showMessageDialog(AwtUtil.getFrame(importWizard), 
                          rr.getString("error")+": "+rr.getString("no_file_open"),
                          rr.getString("error"),
                          JOptionPane.ERROR_MESSAGE);
      return;
    }

    if(importWizard==null || !importWizard.isVisible()) {
      if(importWizard!=null) {
        importWizard.dispose();
      }
      importWizard = new Wizard(
            null,
            rr,
            getName(),
            new SelectFilePane(
                  this.rr,
                  new ImportState(
                        this,
                        root,
                        this.rr,
                        this.filename,
                        this.accountNo)),
            false);
      importWizard.setVisible(true);
    } else {
      importWizard.setVisible(true);
      importWizard.toFront();
      importWizard.requestFocus();
    }
  }

  synchronized void closeTxtImport() {
    if(importWizard!=null) {
      importWizard.setVisible(false);
      importWizard.dispose();
      importWizard = null;
      System.gc();
    }
  }

}

