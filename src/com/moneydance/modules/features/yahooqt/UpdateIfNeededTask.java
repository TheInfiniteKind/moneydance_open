/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.controller.Util;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.time.TimeInterval;

import java.beans.PropertyChangeListener;
import java.util.concurrent.Callable;


/**
 * Background thread task that checks whether or not security quotes or exchange rates need to be
 * updated (based upon today's date) and calls other tasks sequentially to do so. Also has an
 * optional startup delay to allow the main application to finish loading a file and/or setting
 * up the UI.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class UpdateIfNeededTask implements Callable<Boolean> {
  /** Wait 5 seconds before beginning if requested. */
  private static final long START_DELAY_NS = 5000000000L;
  static final String NAME = "Update_If_Needed";  // not translatable

  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private final PropertyChangeListener _progressListener;
  private final boolean _doStartDelay;

  public UpdateIfNeededTask(final StockQuotesModel model,
                            final ResourceProvider resources,
                            final PropertyChangeListener progressListener,
                            final boolean doStartDelay) {
    _model = model;
    _resources = resources;
    _progressListener = progressListener;
    _doStartDelay = doStartDelay;
  }

  @Override
  public String toString() { return NAME; }

  public Boolean call() throws Exception {
    if (_doStartDelay) SQUtil.delaySpecifiedTime(START_DELAY_NS);
    return updateIfNeeded();
  }

  private Boolean updateIfNeeded() {
    AccountBook book = _model.getBook();
    if (book == null) return Boolean.FALSE; // nothing to do
    UserPreferences preferences = _model.getPreferences();
    if (preferences.getBoolSetting(Main.AUTO_UPDATE_KEY, false)) {
      TimeInterval frequency = Main.getUpdateFrequency(_model.getPreferences());
      // exchange rates first so that the proper exchange rates are used for security price conversions
      return updateRatesAndPrices(book, frequency, Util.getStrippedDateInt());
    }
    return false;
  }
  
  private boolean updateRatesAndPrices(AccountBook book, TimeInterval frequency, int today) {
    int lastUpdateDate = _model.getRatesLastUpdateDate();
    int nextUpdateDate = SQUtil.getNextDate(lastUpdateDate, frequency);
    if (today >= nextUpdateDate) {
      DownloadTask task = new DownloadTask(_model, _resources);
      Boolean success;
      _model.addPropertyChangeListener(_progressListener);
      try {
        success = task.call();
        if (success.booleanValue()) _model.saveLastExchangeRatesUpdateDate(today);
      } catch (Exception e) {
        System.err.println("Error updating currency exchange rates: ");
        e.printStackTrace();
        success = Boolean.FALSE;
      }
      _model.removePropertyChangeListener(_progressListener);
      return success.booleanValue();
    }
    return true; // no update needed, so success
  }
}