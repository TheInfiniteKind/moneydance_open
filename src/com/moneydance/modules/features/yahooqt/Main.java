/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
 \************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.modules.features.yahoofx.FXConnection;
import com.moneydance.util.Constants;

import javax.swing.*;
import java.awt.*;
import java.io.ByteArrayOutputStream;
import java.net.URLEncoder;
import java.util.Date;
import java.util.Enumeration;
import java.util.Vector;

/**
 * Pluggable module used to allow users to download stock quote information from quote.yahoo.com
 */
public class Main extends FeatureModule {

  private static final int DOWNLOAD_DAYS = 60;
  private static final int HISTORY_INTERVAL = 7; // snapshot minimum frequency, in days
//  private static final Logger LOGGER = Logger.getInstance();

  private static final String SHOW_DIALOG_COMMAND = "showDialog";
  private static final String UPDATE_COMMAND = "update";


  private boolean areQuotesUpdating = false;
  private boolean areRatesUpdating = false;

  public static final String RATE_LAST_UPDATE_KEY = "yahooqt.rateLastUpdate";
  public static final String AUTO_UPDATE_KEY = "yahooqt.autoUpdate";
  public static final String UPDATE_FREQUENCY_KEY = "yahooqt.updateFrequency";
  public static final String DOWNLOAD_QUOTES_KEY = "yahooqt.downloadQuotes";
  public static final String QUOTE_LAST_UPDATE_KEY = "yahooqt.quoteLastUpdate";
  public static final String DOWNLOAD_RATES_KEY = "yahooqt.downloadRates";

  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    context.registerFeature(this, SHOW_DIALOG_COMMAND, getIcon("icon-yahooqt"), getName());
  }

  private UserPreferences getPreferences() {
    return ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences();
  }

  private void updateIfNeeded() {
    RootAccount account = getContext().getRootAccount();
    String name = account.getAccountName();
    UserPreferences preferences = getPreferences();
    if (preferences.getBoolSetting(AUTO_UPDATE_KEY, false)) {
      Frequency frequency = getUpdateFrequency();
      MDDate today = new MDDate();

      MDDate lastUpdateDate = getQuotesLastUpdateDate(name, account);
      MDDate nextUpdateDate = frequency.next(lastUpdateDate);
      if (nextUpdateDate.equals(today) || nextUpdateDate.isBefore(today)) {
        getQuotes();
        account.setParameter(QUOTE_LAST_UPDATE_KEY, today.toString());
      }
      lastUpdateDate = getRatesLastUpdateDate(name, account);
      nextUpdateDate = frequency.next(lastUpdateDate);
      if (nextUpdateDate.equals(today) || nextUpdateDate.isBefore(today)) {
        getRates();
        account.setParameter(RATE_LAST_UPDATE_KEY, today.toString());
      }
    }
  }

  private MDDate getQuotesLastUpdateDate(String prefix, RootAccount account) {
    MDDate lastUpdateDate;
    try {
      lastUpdateDate = MDDate.fromString(account.getParameter(QUOTE_LAST_UPDATE_KEY));
    } catch (IllegalArgumentException e) {
      lastUpdateDate = new MDDate(new Date(0L));
    }
    return lastUpdateDate;
  }

  private MDDate getRatesLastUpdateDate(String prefix, RootAccount account) {
    MDDate lastUpdateDate;
    try {
      lastUpdateDate = MDDate.fromString(account.getParameter(RATE_LAST_UPDATE_KEY));
    } catch (IllegalArgumentException e) {
      lastUpdateDate = new MDDate(new Date(0L));
    }
    return lastUpdateDate;
  }

  private Frequency getUpdateFrequency() {
    Frequency frequency;
    try {
      frequency = SimpleFrequency.fromString(getPreferences().getSetting(UPDATE_FREQUENCY_KEY));
    } catch (IllegalArgumentException e) {
      frequency = TimeUnit.MONTH;
    }
    return frequency;
  }

  private void update() {
    UserPreferences preferences = getPreferences();
    if (preferences.getBoolSetting(DOWNLOAD_QUOTES_KEY, false)) {
      getQuotes();
    }
    if (preferences.getBoolSetting(DOWNLOAD_RATES_KEY, false)) {
      getRates();
    }
  }


  private Image getIcon(String action) {
    try {
      ClassLoader cl = getClass().getClassLoader();
      java.io.InputStream in =
          cl.getResourceAsStream("/com/moneydance/modules/features/yahooqt/" + action + ".gif");
      if (in != null) {
        ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
        byte buf[] = new byte[256];
        int n;
        while ((n = in.read(buf, 0, buf.length)) >= 0)
          bout.write(buf, 0, n);
        return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
      }
    } catch (Throwable ignored) {
    }
    return null;
  }

  public void handleEvent(String s) {
    super.handleEvent(s);
    if (s.equals("md:file:opened")) {
      updateIfNeeded();
    }
  }

  /**
   * Process an invokation of this module with the given URI
   */
  public void invoke(String uri) {
    String command = uri;
    String parameters = "";
    int colonIdx = uri.indexOf(':');
    if (colonIdx >= 0) {
      command = uri.substring(0, colonIdx);
      parameters = uri.substring(colonIdx + 1);
    }

    if (command.equals(UPDATE_COMMAND)) {
      update();
    } else if (command.equals(SHOW_DIALOG_COMMAND)) {
      // should invoke later so this can be returned to its thread
      SwingUtilities.invokeLater(new Runnable() {
        public void run() {
          YahooDialog dialog = new YahooDialog(getContext());
          dialog.setVisible(true);
          updateIfNeeded();
        }
      });
    }
  }

  public String getName() {
    return "Yahoo\u00ae Finance Synchronizer";
  }

  private float progressMeter = 0f;

  private void getQuotes() {
    Thread t = new Thread(new Runnable() {
      public void run() {
        if (areQuotesUpdating) {
          return;
        }

        showProgress(0f, "Updating stock prices...");

        RootAccount root = getContext().getRootAccount();
        if (root == null) {
          return;
        }
        CurrencyTable ctable = root.getCurrencyTable();

        boolean success = false;
        try {
          areQuotesUpdating = true;
          int totalValues = (int) ctable.getCurrencyCount();
          int currIdx = 0;
          for (Enumeration cen = ctable.getAllValues(); cen.hasMoreElements();) {
            CurrencyType ctype = (CurrencyType) cen.nextElement();
            progressMeter = currIdx / (float) totalValues;
            if (progressMeter == 0.0f)
              progressMeter = 0.01f;

            if (ctype.getCurrencyType() == CurrencyType.CURRTYPE_SECURITY) {
              updateSecurity(ctable, ctype);
            }
            currIdx++;
          }
          success = true;
        } catch (Exception e) {
          showProgress(0f, "Error downloading prices: " + e);
          success = false;
        } finally {
          progressMeter = 0f;
          areQuotesUpdating = false;
          ctable.fireCurrencyTableModified();
        }
        if (success) {
          showProgress(0f, "Finished updating prices");
        }
      }
    });
    t.start();
  }


  private void updateSecurity(CurrencyTable cTable, CurrencyType currType) {
    try {
      long lastDate = 0;
      for (int i = 0; i < currType.getSnapshotCount(); i++) {
        CurrencyType.Snapshot snap = currType.getSnapshot(i);
        if (snap.getDate() > lastDate) {
          lastDate = snap.getDate();
        }
      }

      int days;
      long now = Util.stripTimeFromDate(System.currentTimeMillis());
      if (lastDate == 0) {
        days = DOWNLOAD_DAYS;
        lastDate = Util.stripTimeFromDate(now - (DOWNLOAD_DAYS * Constants.MILLIS_PER_DAY));
      } else {
        lastDate = Util.stripTimeFromDate(lastDate + Constants.MILLIS_PER_DAY);
        days = Math.round((now - lastDate) / (float) Constants.MILLIS_PER_DAY);
      }

      days = Math.max(days, 5);

      //if(days<=0) {
      //  // nothing to update!
      //  return;
      //}

      showProgress(progressMeter, "Getting price for " + currType.getName() + " from finance.yahoo.com...");

      StockConnection stockConn = new StockConnection();
      StockConnection.StockHistory history =
          stockConn.getHistory(currType.getTickerSymbol(), now, days + 1);
      boolean haveHistory = history != null && history.getRecordCount() > 0;

      CurrencyType stockCurr = null;
      if (haveHistory) {
        // get the currency that the prices are specified in
        stockCurr = cTable.getCurrencyByIDString(history.getCurrency());
        if (stockCurr == null) {
//          LOGGER.log("Warning: currency " + history.getCurrency() + " not found, info for " + currType + " was not updated");
          haveHistory = false;
        }
      }

      if (haveHistory) {
        int recordCount = history.getRecordCount();
        for (int i = 0; i < recordCount; i++) {
          StockConnection.StockRecord record = history.getRecord(i);
          if (record.close <= 0) continue;

          haveHistory = true;

          if (record.close == 0.0) record.close = 0.00001;
          if (record.low == 0.0) record.low = record.close;
          if (record.high == 0.0) record.high = record.close;

          record.close = CurrencyTable.convertToBasePrice(1 / record.close, stockCurr, record.date);
          record.low = CurrencyTable.convertToBasePrice(1 / record.low, stockCurr, record.date);
          record.high = CurrencyTable.convertToBasePrice(1 / record.high, stockCurr, record.date);

          CurrencyType.Snapshot snap =
              currType.setSnapshot(Util.stripTimeFromDate(record.date), record.close);
          snap.setDailyVolume(record.volume);
          snap.setUserDailyLow(record.low);
          snap.setUserDailyHigh(record.high);
          if (i == 0 && record.close > 0.0) {
            currType.setUserRate(record.close);
            currType.setTag("price_date", String.valueOf(Util.getStrippedDate()));
          } else if (i == recordCount - 1) {
          }
        }
      }

      //if(!haveHistory) {
      StockConnection.StockPrice info = stockConn.getCurrentPrice(currType.getTickerSymbol());

      if (info == null) {
        return;
      }

      double price = info.getPrice();
      if (price <= 0.0) {
        return;
      }

      // get the currency that the prices are specified in
      stockCurr = cTable.getCurrencyByIDString(info.getCurrency());
      if (stockCurr == null) {
//        LOGGER.log("Warning: currency " + info.getCurrency() + " not found, info for " + currType + " was not updated");
        return;
      }

//      LOGGER.log(">yahooqt>" + stockCurr.getName() + ">converted to:");
      price = CurrencyTable.convertToBasePrice(1 / price, stockCurr, now);

//      LOGGER.log("    " + 1 / price);

      if (currType.getUserRate() != price) {
        currType.setUserRate(price);
        if (!haveHistory) {
          long asOfDate = info.getDate();
          if (asOfDate == 0)
            asOfDate = now;
          asOfDate = Util.stripTimeFromDate(asOfDate);

          CurrencyType.Snapshot snap = currType.setSnapshot(asOfDate, price);
          snap.setUserDailyLow(price);
          snap.setUserDailyHigh(price);
        }
      }
      //}
    } catch (Throwable e) {
//      LOGGER.log(e);
    }
  }

  private void getRates() {
    new Thread(new Runnable() {
      public void run() {
        if (areRatesUpdating) return;
        getContext().showURL("moneydance:setstatus:Connecting to finance.yahoo.com...");
        RootAccount root = getContext().getRootAccount();
        if (root == null) return;

        CurrencyTable ctable = root.getCurrencyTable();

        boolean success = false;
        try {
          areRatesUpdating = true;
          Vector currenciesToCheck = new Vector();
          ctable.dumpCurrencies();
          for (Enumeration cen = ctable.getAllValues(); cen.hasMoreElements();) {
            CurrencyType ctype = (CurrencyType) cen.nextElement();
            if (ctype.getCurrencyType() == CurrencyType.CURRTYPE_CURRENCY) {
              currenciesToCheck.addElement(ctype);
            }
          }
          for (int i = currenciesToCheck.size() - 1; i >= 0; i--) {
            getRate((CurrencyType) currenciesToCheck.elementAt(i), ctable);
          }
          success = true;
        } catch (Exception e) {
          getContext().showURL("moneydance:setstatus:Error downloading rates: " + e);
          success = false;
        } finally {
          areRatesUpdating = false;
          ctable.fireCurrencyTableModified();
        }
        if (success) {
          getContext().showURL("moneydance:setstatus:Finished downloading exchange rates");
        }
      }
    }).start();
  }

  private void getRate(CurrencyType currType, CurrencyTable cTable)
      throws Exception {
    // figure out the last date of an update...
    CurrencyType baseType = cTable.getBaseType();
    if (currType == baseType) {
      return;
    }

    getContext().showURL("moneydance:setstatus:Getting rate for " +
        currType.getIDString() + " from finance.yahoo.com...");

    com.moneydance.modules.features.yahoofx.FXConnection fxConn = new FXConnection();
    FXConnection.ExchangeRate rateInfo =
        fxConn.getCurrentRate(currType.getIDString(), baseType.getIDString());
    if (rateInfo == null) {
      return;
    }

    double rate = rateInfo.getRate();
    if (rate <= 0.0)
      return;


    long lastDate = 0;
    for (int i = 0; i < currType.getSnapshotCount(); i++) {
      CurrencyType.Snapshot snap = currType.getSnapshot(i);
      if (snap.getDate() > lastDate) {
        lastDate = snap.getDate();
      }
    }

    lastDate = Util.stripTimeFromDate(lastDate);
    long today = Util.stripTimeFromDate(System.currentTimeMillis());
    boolean addSnapshot = lastDate + 86400000 * HISTORY_INTERVAL < today;

    if (addSnapshot) {
      currType.setSnapshot(today, rate);
    }
    currType.setUserRate(rate);
  }

  private void showProgress(float progress, String label) {
    getContext().showURL("moneydance:setprogress:meter=" +
        URLEncoder.encode(String.valueOf(progress)) +
        (label == null ? "" : "&label=" + URLEncoder.encode(label)));
  }
}

