/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.*;
import java.util.*;
import java.io.*;

public class QIFParser {

  private RootAccount root;
  private String directory;
  private String sourceID;
    
  public QIFParser(RootAccount root, String sourceID) {
    this.root = root;
    this.sourceID = sourceID;
    directory = root.getParameter("PalmSync.qifdir",".");
  }
  
  public File getFileForAccount(PalmAccount account) {
    try {
      return new File(directory, account.getName() + ".qif");
    } catch (Exception e) {
      System.err.println("Exception occurred in getTransactions for account : " + e);
    }
    return null;
  }

  public PalmTxn[] getTransactionsForAccount(PalmAccount account) {
    try {
      File QFile = new File(directory, account.getName() + ".qif");
      QIFDataReader reader = new QIFDataReader(root, QFile, account);
      return reader.readTransactions();
    }
    catch (Exception e) {
      System.err.println("Exception occurred in getTransactions for account : " + e);
    }
    return null;
  }
  
  public String[] getSplashAccountNames() {
    File direc = new File(directory);
    String[] files = direc.list();
    if(files==null) return new String[0];
    Vector strings = new Vector();
      
    for(int i = 0; i < files.length; i++) {
      if(files[i].toUpperCase().endsWith(".QIF")) {
        strings.add(files[i].substring(0, files[i].length() - 4));
      }
    }
  
    String[] list = new String[strings.size()];
    for(int i = 0; i < strings.size(); i++) {
      list[i] = (String) strings.elementAt(i);
    }
    return list;
  }
    
  public PalmAccount[] getSplashAccounts() {
    File direc = new File(directory);
    String[] files = direc.list();
    Vector strings = new Vector();
    for(int i = 0; i < files.length; i++) {
      String thisOne = files[i].toUpperCase();
      if(thisOne.endsWith(".QIF")) {
        thisOne = thisOne.substring(0, thisOne.length() - 4);
        strings.add(thisOne);
      }
    }
      
    PalmAccount[] accounts = new PalmAccount[strings.size()];
    for(int i = 0; i < strings.size(); i++) {
      String name = (String) strings.elementAt(i);
      Account acc =
        root.getAccountById(root.getIntParameter("PalmSync."+sourceID+"." +
                                                 name + ".syncAccount", 0));
      accounts[i] = new PalmAccount(name, acc, sourceID);
    }
    return accounts;
  }
}













