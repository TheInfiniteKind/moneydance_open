/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.CurrencySnapshot
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.util.DateUtil.convertDateToInt
import com.moneydance.apps.md.controller.Util
import com.moneydance.modules.features.yahooqt.tdameritrade.Candle
import java.util.*

/**
 * Stores a single entry for a historical price entry (snapshot) for a security.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class StockRecord : Comparable<StockRecord> {
  /** The integer date of the quote.  */
  var date: Int = 0
  
  /** The exact date of the quote, which can have the time of day set as well.  */
  var dateTimeGMT: Long = 0
  
  /** Number of shares traded.  */
  var volume: Long = 0
  
  /** The high price in terms of the price currency (gets converted to base currency).  */
  var highRate: Double = -1.0
  
  /** The low price in terms of the price currency (gets converted to base currency).  */
  var lowRate: Double = -1.0
  
  /** The open price in terms of the price currency. Currently not used.  */
  var open: Double = -1.0
  
  /** The close price in terms of the price currency (gets converted to base currency).  */
  var closeRate: Double = -1.0
  
  var priceDisplay: String = ""
  private var multiplier = 0.0
  
  constructor() : super()
  
  constructor(candle: Candle, multiplier: Double) : super() {
    this.multiplier = multiplier
    this.dateTimeGMT = candle.datetime
    val dateObj = Date(this.dateTimeGMT)
    
    this.date = convertDateToInt(dateObj)
    this.volume = candle.volume
    this.highRate = parseUserRate(candle.high)
    this.lowRate = parseUserRate(candle.low)
    this.open = parseUserRate(candle.open)
    this.closeRate = parseUserRate(candle.close)
  }
  
  override fun toString(): String {
    return "close=$closeRate; volume=$volume; high=$highRate; low=$lowRate; date=$date"
  }
  
  override fun compareTo(o: StockRecord): Int {
    // sort by date
    return date - o.date
  }
  
  fun updatePriceDisplay(priceCurrency: CurrencyType, decimal: Char) {
    val amount = if (closeRate == 0.0) 0 else priceCurrency.getLongValue(1.0 / closeRate)
    priceDisplay = priceCurrency.formatFancy(amount, decimal)
  }
  
  fun apply(security: CurrencyType, priceCurrency: CurrencyType): CurrencySnapshot {
    // all snapshots are recorded in terms of the base currency.

    // don't update the price if one already exists...
    security.getSnapshotForDate(date)?.let { if (it.dateInt == date) return it}

    val newRate = priceCurrency.getUserRateByDateInt(date) * closeRate
    val result = security.setSnapshotInt(date, newRate)
    // downloaded values are prices in a certain currency, change to rates for the stock history
    result.userDailyHigh = priceCurrency.getUserRateByDateInt(date) * highRate
    result.userDailyLow = priceCurrency.getUserRateByDateInt(date) * lowRate
    result.dailyVolume = volume
    result.syncItem()
    return result
  }
  
  private fun parseUserRate(value: Double): Double {
    var userPrice = value
    if (userPrice == 0.0) return 0.0
    userPrice *= multiplier
    // the rate is the inverse of the price
    return 1.0 / Util.safeRate(userPrice)
  }
}
