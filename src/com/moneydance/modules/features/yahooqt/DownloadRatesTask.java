/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.Util;
import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.CustomDateFormat;

import java.text.MessageFormat;
import java.util.Enumeration;
import java.util.Vector;
import java.util.concurrent.Callable;

/**
 * Downloads exchange rates.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class DownloadRatesTask implements Callable<Boolean> {
  static final String NAME = "Download_Exchange_Rates"; // not translatable
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private final CustomDateFormat _dateFormat;

  private static final int HISTORY_INTERVAL = 7; // snapshot minimum frequency, in days

  DownloadRatesTask(final StockQuotesModel model, final ResourceProvider resources) {
    _model = model;
    _resources = resources;
    _dateFormat = _model.getPreferences().getShortDateFormatter();
  }

  @Override
  public String toString() { return NAME; }

  public Boolean call() throws Exception {
    _model.showProgress(0.0f, MessageFormat.format(
            _resources.getString(L10NStockQuotes.EXCHANGE_RATES_BEGIN),
            _model.getSelectedExchangeRatesConnection().toString()));
    AccountBook book =  _model.getBook();
    if (book == null) return Boolean.FALSE;
    CurrencyTable ctable = book.getCurrencies();
    // figure out the last date of an update...
    final CurrencyType baseCurrency = ctable.getBaseType();
    final int today = Util.getStrippedDateInt();
    boolean success = true;
    try {
      Vector<CurrencyType> currenciesToCheck = new Vector<CurrencyType>();
      ctable.dumpCurrencies();
      for (CurrencyType ctype : ctable.getAllCurrencies()) {
        if (ctype.getCurrencyType() == CurrencyType.Type.CURRENCY) {
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
        
        System.err.println("updating currency: "+currencyType+" ("+currencyType.getTickerSymbol()+")");
        try {
          final FXConnection connection = (FXConnection) _model.getSelectedExchangeRatesConnection();
          double rate = getRate(currencyType, baseCurrency, connection);
          progressPercent += progressIncrement;
          final String message, logMessage;
          if (rate <= 0.0) {
            message = MessageFormat.format(
                                            _resources.getString(L10NStockQuotes.ERROR_EXCHANGE_RATE_FMT), 
                                            currencyType.getIDString(),  baseCurrency.getIDString());
            logMessage = MessageFormat.format("Unable to get rate from {0} to {1}",
                                              currencyType.getIDString(),  baseCurrency.getIDString());
          } else {
            message = buildRateDisplayText(currencyType, baseCurrency, rate, today);
            logMessage = buildRateLogText(currencyType, baseCurrency, rate, today);
          }
          _model.showProgress(progressPercent, message);
          if(Main.DEBUG_YAHOOQT) System.err.println(logMessage);
        } catch (Exception error) {
          String message = MessageFormat.format(
                                                 _resources.getString(L10NStockQuotes.ERROR_DOWNLOADING_FMT),
                                                 _resources.getString(L10NStockQuotes.RATES),
                                                 error.getLocalizedMessage());
          _model.showProgress(0f, message);
          if(Main.DEBUG_YAHOOQT) System.err.println(MessageFormat.format("Error while downloading Currency Exchange Rates: {0}",
                                                                         error.getMessage()));
          error.printStackTrace();
          success = false;
        }
      }
    } finally {
      ctable.fireCurrencyTableModified();
    }
    if (success) {
      SQUtil.pauseTwoSeconds(); // wait a bit so user can read the last rate update
      String message = MessageFormat.format(
              _resources.getString(L10NStockQuotes.FINISHED_DOWNLOADING_FMT),
              _resources.getString(L10NStockQuotes.RATES));
      _model.showProgress(0f, message);
      if(Main.DEBUG_YAHOOQT) System.err.println("Finished downloading Currency Exchange Rates");
    }
    return Boolean.TRUE;
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private double getRate(CurrencyType currType, CurrencyType baseType, FXConnection connection)
      throws Exception {
    FXConnection.ExchangeRate rateInfo =
        connection.getCurrentRate(currType.getIDString(), baseType.getIDString());
    if (rateInfo == null) {
      return -1.0;
    }

    double rate = rateInfo.getRate();
    if (rate <= 0.0)
      return rate;

    int lastDate = 0;
    for (CurrencySnapshot snap : currType.getSnapshots()) {
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

  private String buildRateDisplayText(CurrencyType fromCurrency, CurrencyType toCurrency,
                                      double rate, int date) {
    String format = _resources.getString(L10NStockQuotes.EXCHANGE_RATE_DISPLAY_FMT);
    // get the currency that the prices are specified in
    long amount = (rate == 0.0) ? 0 : fromCurrency.getLongValue(1.0 / rate);
    final char decimal = _model.getPreferences().getDecimalChar();
    String priceDisplay = fromCurrency.formatFancy(amount, decimal);
    String asofDate =_dateFormat.format(date);
    return MessageFormat.format(format, fromCurrency.getIDString(), toCurrency.getIDString(),
            asofDate, priceDisplay);
  }

  private String buildRateLogText(CurrencyType fromCurrency, CurrencyType toCurrency,
                                  double rate, int date) {
    String format = "Exchange Rate from {0} to {1} as of {2}: {3}";
    // get the currency that the prices are specified in
    long amount = (rate == 0.0) ? 0 : fromCurrency.getLongValue(1.0 / rate);
    String priceDisplay = fromCurrency.formatFancy(amount, '.');
    String asofDate = _dateFormat.format(date);
    return MessageFormat.format(format, fromCurrency.getIDString(), toCurrency.getIDString(),
            asofDate, priceDisplay);
  }

}