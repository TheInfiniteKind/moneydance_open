package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.DateRange;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.util.CustomDateFormat;

import java.util.Enumeration;
import java.util.Vector;
import java.util.concurrent.Callable;

/**
 * Downloads exchange rates.
 */
public class DownloadRatesTask implements Callable<Boolean> {
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;

  private static final int HISTORY_INTERVAL = 7; // snapshot minimum frequency, in days

  DownloadRatesTask(final StockQuotesModel model, final ResourceProvider resources) {
    _model = model;
    _resources = resources;
  }

  public Boolean call() throws Exception {
    _model.showProgress(0.0f, "Downloading exchange rates from finance.yahoo.com...");
    RootAccount root =  _model.getRootAccount();
    if (root == null) return Boolean.FALSE;
    CurrencyTable ctable = root.getCurrencyTable();
    // figure out the last date of an update...
    final CurrencyType baseCurrency = ctable.getBaseType();
    final char decimal = _model.getPreferences().getDecimalChar();
    boolean success = false;
    try {
      Vector<CurrencyType> currenciesToCheck = new Vector<CurrencyType>();
      ctable.dumpCurrencies();
      for (Enumeration cen = ctable.getAllValues(); cen.hasMoreElements();) {
        CurrencyType ctype = (CurrencyType) cen.nextElement();
        if (ctype.getCurrencyType() == CurrencyType.CURRTYPE_CURRENCY) {
          currenciesToCheck.addElement(ctype);
        }
      }
      float progressPercent = 0.0f;
      final float progressIncrement = currenciesToCheck.isEmpty() ? 1.0f :
              100.0f / (float)currenciesToCheck.size();
      for (int i = currenciesToCheck.size() - 1; i >= 0; i--) {
        final CurrencyType currencyType = currenciesToCheck.elementAt(i);
        // skip if no conversion necessary
        if (baseCurrency.equals(currencyType)) continue;
        double rate = getRate(currencyType, baseCurrency);
        progressPercent += progressIncrement;
        final String message;
        if (rate <= 0.0) {
          message = "Unable to get rate for " + currencyType.getIDString();
        } else {
          message = "Downloaded rate for " + currencyType.getIDString() + ": " +
                  baseCurrency.formatFancy(baseCurrency.getLongValue(rate), decimal);
        }
        _model.showProgress(progressPercent, message);
      }
      success = true;
    } catch (Exception e) {
      _model.showProgress(0.0f, "Error downloading rates: " + e);
      success = false;
    } finally {
      ctable.fireCurrencyTableModified();
    }
    if (success) {
      _model.showProgress(0.0f, "Finished downloading exchange rates");
    }
    return Boolean.TRUE;
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private double getRate(CurrencyType currType, CurrencyType baseType)
      throws Exception {
    FXConnection fxConn = new FXConnection();
    FXConnection.ExchangeRate rateInfo =
        fxConn.getCurrentRate(currType.getIDString(), baseType.getIDString());
    if (rateInfo == null) {
      return -1.0;
    }

    double rate = rateInfo.getRate();
    if (rate <= 0.0)
      return rate;


    int lastDate = 0;
    for (int i = 0; i < currType.getSnapshotCount(); i++) {
      CurrencyType.Snapshot snap = currType.getSnapshot(i);
      lastDate = Math.max(lastDate, snap.getDateInt());
    }

    int today = Util.getStrippedDateInt();
    boolean addSnapshot = Util.incrementDate(lastDate, 0, 0, HISTORY_INTERVAL) < today;

    if (addSnapshot) {
      currType.setSnapshotInt(today, rate);
    }
    currType.setUserRate(rate);
    return rate;
  }

}