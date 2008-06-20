/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.ModuleUtil;
import com.moneydance.apps.md.controller.UserPreferences;

import com.moneydance.apps.md.model.*;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.util.Constants;

import java.net.URLEncoder;
import java.io.*;
import java.util.*;
import java.text.*;
import java.awt.*;

/** Pluggable module used to allow users to download stock
 *  quote information from quote.yahoo.com
 */
public class Main
  extends FeatureModule
{

  private boolean isUpdating = false;
  private static final int DOWNLOAD_DAYS = 60;
  
  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    context.registerFeature(this, "getquotes", 
                            getIcon("icon-yahooqt"),
                            getName());
  }
  
  private Image getIcon(String action) {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in = 
        cl.getResourceAsStream("/com/moneydance/modules/features/yahooqt/"+action+".gif");
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

    if(command.equals("getquotes")) {
      getQuotes();
    }
  }

  public String getName() {
    return "Stock Quote Synchronizer";
  }

  private float progressMeter = 0f;
  private void getQuotes() {
    Thread t = new Thread(new Runnable() {
        public void run() {
          if(isUpdating) return; 
          
          showProgress(0f, "Updating stock prices...");
          
          RootAccount root = getContext().getRootAccount();
          if(root==null) return;
          CurrencyTable ctable = root.getCurrencyTable();

          boolean success = false;
          try {
            isUpdating = true;
            int totalValues = (int)ctable.getCurrencyCount();
            int currIdx = 0;
            for(Enumeration cenum=ctable.getAllValues(); cenum.hasMoreElements();) {
              CurrencyType ctype = (CurrencyType)cenum.nextElement();
              progressMeter = currIdx/(float)totalValues;
              if(progressMeter==0.0f)
                progressMeter = 0.01f;
              
              if(ctype.getCurrencyType()==CurrencyType.CURRTYPE_SECURITY) {
                updateSecurity(ctable, ctype);
              }
              currIdx++;
            }
            success = true;
          } catch (Exception e) {
            showProgress(0f, "Error downloading prices: "+e);
            success = false;
          } finally {
            progressMeter = 0f;
            isUpdating = false;
            ctable.fireCurrencyTableModified();
          }
          if(success) {
            showProgress(0f, "Finished updating prices");
          }
        }
      });
    t.start();
  }
                          

  private void updateSecurity(CurrencyTable cTable, CurrencyType currType) {
    try {
      long lastDate = 0;
      for(int i=0; i<currType.getSnapshotCount(); i++) {
        CurrencyType.Snapshot snap = currType.getSnapshot(i);
        if(snap.getDate()>lastDate)
          lastDate = snap.getDate();
      }

      int days;
      long now = Util.stripTimeFromDate(System.currentTimeMillis());
      if(lastDate==0) {
        days = DOWNLOAD_DAYS;
        lastDate = Util.stripTimeFromDate(now-(DOWNLOAD_DAYS*Constants.MILLIS_PER_DAY));
      } else {
        lastDate = Util.stripTimeFromDate(lastDate + Constants.MILLIS_PER_DAY);
        days = (int)Math.round((now-lastDate)/(float)Constants.MILLIS_PER_DAY);
      }

      days = Math.max(days, 5);

      //if(days<=0) {
      //  // nothing to update!
      //  return;
      //}
      
      showProgress(progressMeter, "Getting price for "+currType.getName()+" from finance.yahoo.com...");
      
      StockConnection stockConn = new StockConnection();
      StockConnection.StockHistory history =
        stockConn.getHistory(currType.getTickerSymbol(), now, days+1);
      boolean haveHistory = history!=null && history.getRecordCount()>0;

      CurrencyType stockCurr = null;
      if(haveHistory) {
        // get the currency that the prices are specified in
        stockCurr = cTable.getCurrencyByIDString(history.getCurrency());
        if(stockCurr==null) {
          System.err.println("Warning: currency "+history.getCurrency()+
                             " not found, info for "+currType+" was not updated");
          haveHistory = false;
        }
      }

      if(haveHistory) {
        long dt = lastDate;
        int recordCount = history.getRecordCount();
        for(int i=0; i<recordCount; i++) {
          StockConnection.StockRecord record = history.getRecord(i);
          if(record.close<=0) continue;

          haveHistory = true;
          
          if(record.close==0.0) record.close = 0.00001;
          if(record.low==0.0) record.low = record.close;
          if(record.high==0.0) record.high = record.close;

          record.close = cTable.convertToBasePrice(1/record.close,
                                                   stockCurr,
                                                   record.date);
          record.low = cTable.convertToBasePrice(1/record.low,
                                                 stockCurr,
                                                 record.date);
          record.high = cTable.convertToBasePrice(1/record.high,
                                                  stockCurr,
                                                  record.date);
        
          CurrencyType.Snapshot snap =
            currType.setSnapshot(Util.stripTimeFromDate(record.date),
                                 record.close);
          snap.setDailyVolume(record.volume);
          snap.setUserDailyLow(record.low);
          snap.setUserDailyHigh(record.high);
          if(i==0 && record.close>0.0) {
            currType.setUserRate(record.close);
            currType.setTag("price_date", String.valueOf(Util.getStrippedDate()));
          } else if(i==recordCount-1) {
          }
        }
      }

      //if(!haveHistory) {
        StockConnection.StockPrice info = stockConn.getCurrentPrice(currType.getTickerSymbol());

        if(info==null)
          return;

        double price = info.getPrice();
        if(price<=0.0)
          return;
        
        // get the currency that the prices are specified in
        stockCurr = cTable.getCurrencyByIDString(info.getCurrency());
        if(stockCurr==null) {
          System.err.println("Warning: currency "+info.getCurrency()+
                             " not found, info for "+currType+" was not updated");
          return;
        }

        if(StockConnection.DEBUG)
          System.err.println(">yahooqt>"+stockCurr.getName()+">converted to:");
        price = cTable.convertToBasePrice(1/price, stockCurr, now);

        if(StockConnection.DEBUG) System.err.println("    "+1/price);
        
        if(currType.getUserRate()!=price) {
          currType.setUserRate(price);
          if(!haveHistory) {
            long asOfDate = info.getDate();
            if(asOfDate==0)
              asOfDate = now;
            asOfDate = Util.stripTimeFromDate(asOfDate);

            CurrencyType.Snapshot snap = currType.setSnapshot(asOfDate, price);
            snap.setUserDailyLow(price);
            snap.setUserDailyHigh(price);
          }
        }
        //}
    } catch (Throwable e) {
      e.printStackTrace(System.err);
    }
  }

  private void showProgress(float progress, String label) {
    getContext().showURL("moneydance:setprogress:meter="+
                         URLEncoder.encode(String.valueOf(progressMeter))+
                         (label==null ? "" : "&label="+URLEncoder.encode(label)));
  }
}

