/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.console;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.ModuleUtil;
import com.moneydance.apps.md.controller.UserPreferences;

import com.moneydance.apps.md.model.*;

import java.io.*;
import java.util.*;
import java.text.*;
import java.awt.*;

/** Pluggable module used to give users access to their 
  * internal events in Moneydance.
  ------------------------------------------------------------------------
  $Author: sreilly $			$Date: 2001/08/31 02:00:20 $
  $Revision: 1.5 $
*/

public class Main
  extends FeatureModule
  implements AccountListener,
             TransactionListener
{
  private String buffer[] = null;
  private int bufferSize = 0;

  private RootAccount root = null;
  private ConsoleWindow consoleWindow = null;
  
  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    context.registerFeature(this, "showconsole", 
                            getIcon("event"),
                            getName());
    
    try {
      if(context.getClass()==com.moneydance.apps.md.controller.Main.class) {
        com.moneydance.apps.md.controller.Main main = null;
        main = (com.moneydance.apps.md.controller.Main)context;
      }
    } catch (Throwable t) {
      System.err.println("Error getting date format: "+t);
    }
    
    startListening();
  }
  
  private Image getIcon(String action) {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in = 
        cl.getResourceAsStream("/com/moneydance/modules/features/console/"+action+"_icon.gif");
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

  private synchronized void startListening() {
    stopListening();
    root = getContext().getRootAccount();
    if(root==null) {
      return;
    }
    root.getTransactionSet().addTransactionListener(this);
    root.addAccountListener(this);
  }

  private synchronized void stopListening() {
    if(root==null) return;
    root.getTransactionSet().removeTransactionListener(this);
    root.removeAccountListener(this);
    root = null;
  }

  public void cleanup() {
    closeConsole();
    stopListening();
    resetBuffer();
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

    if(root==null) startListening();
    if(command.equals("showconsole")) {
      showConsole();
    } else if(command.equals("reset")) {
      resetBuffer();
    }
  }

  public String getName() {
    return "Event Viewer";
  }

  private synchronized void showConsole() {
    if(consoleWindow==null) {
      consoleWindow = new ConsoleWindow(this);
      for(int i=0; i<bufferSize; i++) {
        consoleWindow.addLine(buffer[i]);
      }
      consoleWindow.setVisible(true);
    } else {
      consoleWindow.setVisible(true);
      consoleWindow.toFront();
      consoleWindow.requestFocus();
    }
  }
  
  synchronized void resetBuffer() {
    bufferSize = 0;
    if(consoleWindow!=null) {
      consoleWindow.reset();
    }
  }

  synchronized void closeConsole() {
    if(consoleWindow!=null) {
      consoleWindow.setVisible(false);
      consoleWindow = null;
      System.gc();
    }
  }
  
  private synchronized void log(String s) {
    if(buffer==null || bufferSize<buffer.length) {
      String newbuf[] = new String[bufferSize+30];
      if(buffer!=null) {
        System.arraycopy(buffer, 0, newbuf, 0, bufferSize);
      }
      buffer = newbuf;
    }
    buffer[bufferSize++] = s;
    if(consoleWindow!=null) {
      consoleWindow.addLine(s);
    }
  }

  /** Called after a transaction has been removed from
   * the transaction set. */
  public void transactionRemoved(AbstractTxn t) {
    log("Txn Removed: "+getTxnLog(t));
  }

  /** Called after a transaction has been added to
    * the transaction set. */
  public void transactionAdded(AbstractTxn t) {
    log("Txn Added: "+getTxnLog(t));
  }

  /** Called after a transaction has been modified. */
  public void transactionModified(AbstractTxn t) {
    log("Txn Removed: "+getTxnLog(t));
  }
  
  /** Is called when some aspect of the account is modified, such
      as account name, currency, etc. */
  public void accountModified(Account account) {
    log("Account Modified: "+account);
  }
  
  /** Is called when the account balance is changed */
  public void accountBalanceChanged(Account account) {
    //log("Account Balance Changed: "+account);
  }

  /** Is called when an account is removed. */
  public void accountDeleted(Account parentAcct, Account deletedAcct) {
    log("Account Deleted: "+deletedAcct+" was deleted from "+parentAcct.getAccountName());
  }
  
  /** Is called when an account is added. */
  public void accountAdded(Account parentAcct, Account newAcct) {
    log("Account Added: "+newAcct+" was added to "+parentAcct.getAccountName());
  }
  
  /** Get a string for the given transaction that can be printed to
      the console. */
  private String getTxnLog(AbstractTxn t) {
    return String.valueOf(t);
  }
}

