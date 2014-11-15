/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
 \************************************************************/

package com.moneydance.modules.features.miscdebug;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.HomePageView;
import com.infinitekind.util.*;

import javax.swing.*;
import java.io.*;
import java.lang.String;
import java.security.SecureRandom;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import javax.net.ssl.*;
import javax.swing.JOptionPane;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

/** Extension used to examine moneydance and data file for errors */
public class Main
  extends FeatureModule
{


  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    context.registerFeature(this, "clear_all_online", null,
                            "Debug: Clear all online services");
    context.registerFeature(this, "install_dummy_trust_manager", null,
                            "Debug: Enable Dummy Trust Manager");
    context.registerFeature(this, "set_debug_mode", null,
                            "Debug: Set DEBUG Flag");
    context.registerFeature(this, "add_manual_fi", null,
                            "Debug: Add Manual OFX Service");
    context.registerFeature(this, "dump_currency_info", null, "Debug: Dump Currency/Security Info to Console");
    //context.registerHomePageView(this, new HPView());
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

    if(command.equals("clear_all_online")) {
      clearAllOnline();
    } else if(command.equals("install_dummy_trust_manager")) {
      installDummyTrustManager();
    } else if(command.equals("set_debug_mode")) {
      enableDebugMode();
    } else if(command.equals("add_manual_fi")) {
      addManualFI();
    } else if(command.equals("dump_currency_info")) {
      dumpCurrencyInfo();
    }
  }

  private void clearAllOnline() {
    try {
      RootAccount root = getContext().getRootAccount();
      if(root==null) return;

      root.removeParameter(RootAccount.STORE_PINS_PARAM);
      root.removeParameter(RootAccount.PASSWD_CACHE_KEY);
      OnlineInfo olInfo = root.getOnlineInfo();
      while(olInfo.getServiceCount()>0) {
        OnlineService svc = olInfo.getService(0);
        svc.clearAuthenticationCache();
        olInfo.removeService(0);
      }
      root.removeParameter(RootAccount.STORE_PINS_PARAM);
      root.removeParameter(RootAccount.PASSWD_CACHE_KEY);
      AccountIterator acctIterator = new AccountIterator(root);
      while(acctIterator.hasNext()) {
        Account acct = acctIterator.next();
        acct.setBankingFI(null);
        acct.setBankingFI(null);
        acct.setOFXAccountKey(null);
        acct.setOFXAccountNumber(null);
        acct.setOFXAccountType(null);
        acct.setOFXBankID(null);
        acct.removeParameter("ofx_acct_msg_type");
        acct.setOFXBillPayAccountNumber(null);
        acct.setOFXBillPayAccountType(null);
        acct.setOFXBillPayBankID(null);
        acct.setOFXBranchID(null);
        acct.setOFXBrokerID(null);
        acct.removeParameter("ofx_last_txn_update");
      }

      JOptionPane.showMessageDialog(null, "All Online Services and settings have been reset");
    } catch (Exception e) {
      e.printStackTrace(System.err);
      JOptionPane.showMessageDialog(null,
                                    "Error: Unable to complete clearing all online services: "+e,
                                    "Error",
                                    JOptionPane.ERROR_MESSAGE);
    }
  }

  private void enableDebugMode() {
    com.moneydance.apps.md.controller.Main.DEBUG = true;
    com.moneydance.apps.md.controller.olb.ofx.OFXConnection.DEBUG = true;
    com.moneydance.apps.md.controller.olb.ofx.OFXConnection.DEBUG_MESSAGES = true;
    JOptionPane.showMessageDialog(null,
                                  "Debug mode is now enabled",
                                  "",
                                  JOptionPane.INFORMATION_MESSAGE);
  }

  
  private void dumpCurrencyInfo() {
    RootAccount root = getContext().getRootAccount();
    if(root==null) return;
    System.err.println("printing info for all currencies and securities.");
    System.err.println("types: "+CurrencyType.CURRTYPE_CURRENCY+"=currency, "+CurrencyType.CURRTYPE_SECURITY+"=security");
    for(CurrencyType curr : root.getCurrencyTable().getAllCurrencies()) {
      System.err.println("Currency: '"+curr.getName()+"'");
      System.err.println("  type: "+curr.getCurrencyType());
      System.err.println("  decimalplaces: " + curr.getDecimalPlaces());
      System.err.println("  ID: " + curr.getID());
      System.err.println("  IDString: " + curr.getIDString());
      System.err.println("  ticker: " + curr.getTickerSymbol());
      System.err.println("  rawrate: " + curr.getRawRate());
      System.err.println("  userrate: " + curr.getUserRate());
      System.err.println("  dailychange: " + curr.getDailyChange());
      System.err.println("  dailyvolume: " + curr.getDailyVolume());
      System.err.println("  effectivedate: " + curr.getEffectiveDateInt());
      System.err.println("  hideinUI: " + curr.getHideInUI());
      System.err.println("  prefix: '" + curr.getPrefix() + "'");
      System.err.println("  suffix: '" + curr.getSuffix() + "'");
      System.err.println("  uuid: " + curr.getUUID());
      TagSet tags = curr.getTags();
      for(int i=0; i<tags.getTagCount(); i++) {
        System.err.println("  tag:"+tags.getTagAt(i).getKey()+":"+tags.getTagAt(i).getValue());
      }
      for(int i=0; i<curr.getStockSplitCount(); i++) {
        CurrencyType.StockSplit split = curr.getStockSplit(i);
        System.err.println("  stock split on "+split.getDateInt()+", trading "+split.getOldShares()+" for "+split.getNewShares()+" shares at a ratio of "+split.getSplitRatio());
      }
      for(int i=0; i<curr.getSnapshotCount(); i++) {
        CurrencyType.Snapshot snap = curr.getSnapshot(i);
        System.err.println("  snapshot on "+snap.getDateInt()+" ");
        System.err.println("  --userrate: "+snap.getUserRate());
        System.err.println("  --rawrate: "+snap.getRawRate());
        System.err.println("  --volume: "+snap.getDailyVolume());
        System.err.println("  --high: "+snap.getUserDailyHigh());
        System.err.println("  --low: "+snap.getUserDailyLow());
      }
    }
    
  }

  private void addManualFI() {
    RootAccount root = getContext().getRootAccount();
    if(root==null) return;

    String infoStr =
      "{\n"
      + "bootstrap_url = \"https://onlinebankingqa1.kdc.capitalone.com/ofx/process.ofx\" \n"
      + "access_type = \"OFX\" \n"
      + "uses_fi_tag = \"y\" \n"
      + "fi_name = \"Test OFX Service\" \n"
      + "fi_org = \"Hibernia\" \n"
      + "fi_id = \"1001\" \n"
      + "app_id = \"MDNC\" \n"
      + "app_ver = \"2012\" \n"
      + "ofx_version = \"103\" \n"
      +"}";
    while(true) {
      JTextArea area = new JTextArea(infoStr, 12, 50);
      JScrollPane scroll = new JScrollPane(area,
                                           JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                                           JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
      int result =
        JOptionPane.showOptionDialog(null, scroll, "Enter OFX Server Information", JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE, null, null, null);
      if(result!=JOptionPane.OK_OPTION) return;

      infoStr = area.getText();

      StreamTable infoTable = new StreamTable();
      try {
        infoTable.readFrom(infoStr);
      } catch (Exception e) {
        JOptionPane.showMessageDialog(null, "Unable to parse input: "+e);
        continue;
      }

      OnlineInfo olInfo = root.getOnlineInfo();
      OnlineService newService = new OnlineService(null, infoTable);

      for(int i=olInfo.getServiceCount()-1; i>=0; i--) {
        OnlineService svc = olInfo.getService(i);
        if(svc.isSameAs(newService)) {
          svc.setMsgSetURL(OnlineService.MESSAGE_TYPE_PROF, newService.getBootstrapURL());
          svc.mergeDataTables(newService.getTable());
          svc.setProfileUpdateNeeded();
          JOptionPane.showMessageDialog(null, "Updated existing FI with new information: "+newService);
          return;
        }
      }

      // no existing FI matched.. so add it
      olInfo.addService(newService);
      JOptionPane.showMessageDialog(null, "Added new FI: "+newService);
      return;
    }
  }


  private void installDummyTrustManager() {
    SSLContext sslContext = null;
    try {
      sslContext = SSLContext.getInstance("SSL");

      // Retrieve certificates and use them to configure a trust manager factory
      TrustManager managers[] = { new CustomX509TrustManager() };
      sslContext.init(null, managers, new SecureRandom());

      SSLSocketFactory factory = sslContext.getSocketFactory();
      javax.net.ssl.HttpsURLConnection.setDefaultSSLSocketFactory(factory);

    } catch (Throwable t) {
      System.err.println("Error installing dummy trust manager: "+t);
      t.printStackTrace(System.err);
      JOptionPane.showMessageDialog(null, "Error installing dummy trust manager: "+t);
      return;
    }
    JOptionPane.showMessageDialog(null, "Dummy certificate trust manager is now active");
  }


  public String getName() {
    return "Moneydance Debugging Helper";
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

  private final class CustomX509TrustManager
    implements X509TrustManager
  {
    X509Certificate rootCAs[] = {};

    public CustomX509TrustManager() {
    }

    public X509Certificate[] getAcceptedIssuers() {
      System.err.println("TRUSTMGR: returning accepted issuers");
      return rootCAs;
    }

    private final boolean isCertTrusted(X509Certificate cert) {
      return true;
    }

    public void checkServerTrusted(X509Certificate certChain[], String authType)
      throws CertificateException
    {
      checkClientTrusted(certChain, authType);
    }

    public void checkClientTrusted(X509Certificate certChain[], String authType)
      throws CertificateException
    {
      // ok... just ignore it
    }

    public boolean isClientTrusted(X509Certificate certChain[]) {
      return isServerTrusted(certChain);
    }



    public boolean isServerTrusted(X509Certificate certChain[]) {
      System.err.println("TRUSTMGR: checking cert chain, starting with: "+certChain[0]);
      return true;
    }

    private void saveCert(X509Certificate c, int certNum) {
      try {
        String filename = "unknown_cert_"+certNum+".der";
        System.err.println("Saving certificate: "+certNum);
        System.err.println("    subject: "+c.getSubjectDN());
        System.err.println("     issuer: "+c.getIssuerDN());
        System.err.println("  not after: "+c.getNotAfter());
        System.err.println(" not before: "+c.getNotBefore());
        System.err.println("   filename: "+filename);


        java.io.FileOutputStream out = new FileOutputStream(filename);
        out.write(c.getEncoded());
        out.close();
      } catch (Exception e) {
        System.err.println("Error writing unknown cert to file: "+e);
      }
    }

  }



}

