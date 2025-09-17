/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.AccountBook
import com.infinitekind.util.DateUtil
import com.moneydance.apps.md.controller.time.TimeInterval
import com.moneydance.modules.features.yahooqt.SQUtil.delaySpecifiedTime
import com.moneydance.modules.features.yahooqt.SQUtil.getNextDate
import java.beans.PropertyChangeListener
import java.util.concurrent.Callable

/**
 * Background thread task that checks whether or not security quotes or exchange rates need to be
 * updated (based upon today's date) and calls other tasks sequentially to do so. Also has an
 * optional startup delay to allow the main application to finish loading a file and/or setting
 * up the UI.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class UpdateIfNeededTask(private val _model: StockQuotesModel,
                         private val _resources: ResourceProvider,
                         private val _progressListener: PropertyChangeListener?,
                         private val _doStartDelay: Boolean) : Callable<Boolean> {
  override fun toString(): String {
    return NAME
  }
  
  @Throws(Exception::class)
  override fun call(): Boolean {
    if (_doStartDelay) delaySpecifiedTime(START_DELAY_NS)
    return updateIfNeeded()
  }
  
  private fun updateIfNeeded(): Boolean {
    val book = _model.book ?: return java.lang.Boolean.FALSE
    // nothing to do
    
    val preferences = _model.preferences
    if (preferences.getBoolSetting(Main.AUTO_UPDATE_KEY, false)) {
      val frequency = Main.getUpdateFrequency(_model.preferences)
      // exchange rates first so that the proper exchange rates are used for security price conversions
      return updateRatesAndPrices(book, frequency, DateUtil.strippedDateInt)
    }
    return false
  }
  
  private fun updateRatesAndPrices(book: AccountBook, frequency: TimeInterval, today: Int): Boolean {
    val lastUpdateDate = _model.ratesLastUpdateDate
    val nextUpdateDate = getNextDate(lastUpdateDate, frequency)
    if (today >= nextUpdateDate) {
      val task = DownloadTask(_model, _resources)
      var success: Boolean
      _model.addPropertyChangeListener(_progressListener)
      try {
        success = task.call()
        if (success) _model.saveLastExchangeRatesUpdateDate(today)
      } catch (e: Exception) {
        System.err.println("Error updating currency exchange rates: ")
        e.printStackTrace()
        success = java.lang.Boolean.FALSE
      }
      _model.removePropertyChangeListener(_progressListener)
      return success
    }
    return true // no update needed, so success
  }
  
  companion object {
    /** Wait 5 seconds before beginning if requested.  */
    private const val START_DELAY_NS = 5000000000L
    const val NAME: String = "Update_If_Needed" // not translatable
  }
}