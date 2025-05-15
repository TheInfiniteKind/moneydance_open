/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.moneydance.model.InvestFields
import com.infinitekind.util.DateUtil
import com.infinitekind.util.DateUtil.convertLongDateToInt
import com.infinitekind.util.DateUtil.firstMinuteInDay
import com.infinitekind.util.StringUtils
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import com.moneydance.modules.features.yahooqt.SQUtil.parseTickerSymbol
import com.moneydance.modules.features.yahooqt.tdameritrade.Candle
import com.moneydance.modules.features.yahooqt.tdameritrade.History
import java.text.MessageFormat
import java.util.*

/**
 * Stores the result of an attempt to retrieve information for a security or currency
 */
class DownloadInfo internal constructor(var security: CurrencyType, model: DownloadModel) {
  lateinit var relativeCurrency: CurrencyType // the currency in which prices are specified by the source
  lateinit var fullTickerSymbol: String
  var exchange: StockExchange? = null
  var priceMultiplier: Double = 1.0
  var isValidForDownload: Boolean = false
  
  var skipped: Boolean = false
  
  var rate: Double = 0.0
    private set
  private var dateTimeStamp: Long = 0
  
  var testMessage: String = ""
  var logMessage: String? = null
  
  var toolTip: String? = null
  var resultText: String? = null
  
  val errors: MutableList<DownloadException> = ArrayList()
  private val history: MutableList<StockRecord> = ArrayList()
  
  init {
    if (security.currencyType == CurrencyType.Type.SECURITY) {
      initFromSecurity(model)
    } else {
      initFromCurrency()
    }
  }
  
  private fun initFromSecurity(model: DownloadModel) {
    isValidForDownload = true
    val symbolData = parseTickerSymbol(security)
    if (symbolData == null) {
      isValidForDownload = false
      recordError("No ticker symbol for: '$security")
      return
    }
    
    exchange = model.getExchangeForSecurity(symbolData, security)
    if (exchange != null) {
      priceMultiplier = exchange!!.priceMultiplier
    }
    
    fullTickerSymbol = model.getFullTickerSymbol(symbolData, exchange) ?: run {
      isValidForDownload = false
      recordError("No full ticker symbol for: '$security")
      ""
    }
    
    // check for a relative currency embedded in the symbol
    relativeCurrency = security.book.currencies.getCurrencyByIDString(symbolData.currencyCode) ?: run {
      // check for a relative currency that is specific to the provider/exchange
      val currID = model.getCurrencyCodeForQuote(security.getTickerSymbol(), exchange!!)
      security.book.currencies.getCurrencyByIDString(currID)
    } ?: run {
      // if there is still no relative currency, look for USD
      security.book.currencies.getCurrencyByIDString("USD")
    } ?: run {
      // if there is still no relative currency, fail
      isValidForDownload = false
      recordError("No relative currency found for: '$fullTickerSymbol', using base currency '${security.book.currencies.baseType}' instead. ")
      security.book.currencies.baseType
    }
  }
  
  
  private fun initFromCurrency() {
    fullTickerSymbol = security.idString
    relativeCurrency = security.book.currencies.baseType
    isValidForDownload = fullTickerSymbol!!.length == 3 && relativeCurrency!!.idString.length == 3
    
    if (fullTickerSymbol == relativeCurrency!!.idString) { // the base currency is always 1.0
      isValidForDownload = false
      this.rate = 1.0
      recordError("Base currency rate is a constant 1.0")
    } else if (!isValidForDownload) {
      recordError(
        ("Invalid currency symbol: '" + fullTickerSymbol
         + "' or '" + relativeCurrency!!.idString + "'")
      )
    }
  }
  
  fun apply() {
    // apply any historical prices
    for (record in history) {
      record.apply(security, relativeCurrency)
    }
    
    val dateStampInt = convertLongDateToInt(dateTimeStamp)
    val mostRecentRecord = findMostRecentValidRecord()
    val localUpdateDate = security.getLongParameter("price_date", 0)
    // apply the current rate, or pull it from the most recent historical price:
    if (rate > 0) {
      security.setUserRate(rate, relativeCurrency)
      security.setParameter("price_date", dateTimeStamp)
      security.syncItem()
      
      if (history.size <= 0) { // if there isn't a history, add one entry with the date of this rate
        val newRate = relativeCurrency!!.getUserRateByDateInt(dateStampInt) * rate
        val result = security.setSnapshotInt(dateStampInt, newRate)
        //result.setUserDailyHigh(relativeCurrency.getUserRateByDateInt(dateStampInt)*newRate);
        //result.setUserDailyLow(relativeCurrency.getUserRateByDateInt(dateStampInt)*newRate);
        //result.setDailyVolume(volume);
        result.syncItem()
      }
    } else {
      // update the current price if possible and if there are no more recent prices/rates
      if (mostRecentRecord != null) { // && mostRecentRecord.dateTimeGMT > lastUpdateDate) {
        // the user rate should be stored in terms of the base currency, just like the snapshots
        security.setUserRate(mostRecentRecord.closeRate, relativeCurrency)
        security.setParameter("price_date", mostRecentRecord.dateTimeGMT)
        security.syncItem()
      }
    }
    
    if (!isBlank(logMessage)) {
      // the historical price has a log message already, so just dump the current price update
      // log message now
      QER_DLOG.log { "applied updates to $security" }
    }
  }
  
  override fun toString(): String {
    return security.getName()
  }
  
  fun setRate(rate: Double, dateTimeStamp: Long) {
    this.rate = rate
    if (dateTimeStamp <= 0) {
      this.dateTimeStamp = firstMinuteInDay(Date()).time
    } else {
      this.dateTimeStamp = dateTimeStamp
    }
  }
  
  
  fun addHistoryRecords(snapshots: List<StockRecord>) {
    history.addAll(snapshots)
  }
  
  val historyCount: Int
    get() = history.size
  
  fun findMostRecentValidRecord(): StockRecord? {
    Collections.sort(history)
    for (index in history.indices.reversed()) {
      val record = history[index]
      if (record.closeRate != 0.0) return record
    }
    return null
  }
  
  fun buildPriceDisplay(priceCurrency: CurrencyType, decimal: Char) {
    for (record in history) {
      record.updatePriceDisplay(priceCurrency, decimal)
    }
  }
  
  fun buildRateDisplayText(model: StockQuotesModel): String {
    val format = model.resources.getString(L10NStockQuotes.EXCHANGE_RATE_DISPLAY_FMT)
    // get the currency that the prices are specified in
    val amount = if (rate == 0.0) 0 else security.getLongValue(1.0 / rate)
    val decimal = model.decimalDisplayChar
    val priceDisplay = security.formatFancy(amount, decimal)
    val asofDate = model.uIDateFormat.format(DateUtil.strippedDateInt)
    return MessageFormat.format(
      format, security.idString, relativeCurrency.idString,
      asofDate, priceDisplay
    )
  }
  
  
  fun buildRateLogText(model: StockQuotesModel): String {
    val amount = if (rate == 0.0) 0 else security.getLongValue(1.0 / rate)
    val priceDisplay = security.formatFancy(amount, '.')
    val asofDate = model.uIDateFormat.format(DateUtil.strippedDateInt)
    val messageKey = if (security.currencyType == CurrencyType.Type.CURRENCY) L10NStockQuotes.EXCHANGE_RATE_DISPLAY_FMT else L10NStockQuotes.SECURITY_PRICE_DISPLAY_FMT
    return MessageFormat.format(
      model.resources.getString(messageKey),
      security.idString,
      relativeCurrency.idString,
      asofDate,
      priceDisplay
    )
  }
  
  
  fun recordError(message: String?) {
    errors.add(DownloadException(this, message))
    if (isBlank(logMessage)) {
      logMessage = message
    }
  }
  
  
  fun wasSuccess(): Boolean {
    return errors.size <= 0 && (rate > 0 || history.size > 0)
  }
  
  /** Create a test result object based on the download result for a security download  */
  fun updateResultSummary(model: StockQuotesModel) {
    if (skipped) {
      toolTip = ""
      resultText = model.resources.getString(L10NStockQuotes.TEST_EXCLUDED)
    } else if (security.currencyType == CurrencyType.Type.CURRENCY) {
      toolTip = "<html><pre>" + testMessage + "</pre></html>"
      val sb = StringBuilder("<html>")
      sb.append(getSuccessIcon(errors.size <= 0)).append(' ')
      sb.append(model.resources.getString(L10NStockQuotes.HISTORY))
      sb.append("</html>")
      resultText = sb.toString()
    } else { // it's a security
      // we're just counting the number of successful symbols
      
      var sb = StringBuilder("<html><p>")
      sb.append(logMessage)
      sb.append("</p></html>")
      toolTip = sb.toString()
      
      sb = StringBuilder()
      sb.append("<html>")
      sb.append(getSuccessIcon(wasSuccess()))
      sb.append(" ")
      findMostRecentValidRecord().takeIf { it != null && it.closeRate != 0.0 }?.let { latest ->
        sb.append(latest.priceDisplay) // security. latest.priceDisplay 1/latest.closeRate)
        sb.append(" on ").append(model.uIDateFormat.format(latest.date))
      } ?: run {
        sb.append("No history records returned for security ").append(security.getName())
      }
      if (history.size > 1) {
        sb.append(" with ")
        sb.append(history.size)
        sb.append(" records")
      }
      sb.append("</html>")
      resultText = sb.toString()
    }
  }
  
  
  fun buildPriceDisplayText(model: StockQuotesModel): String {
    for (record in history) {
      val amount = if (record.closeRate == 0.0) 0 else relativeCurrency!!.getLongValue(1.0 / record.closeRate)
      record.priceDisplay = relativeCurrency!!.formatFancy(amount, model.decimalDisplayChar)
    }
    val latest = findMostRecentValidRecord()
    return MessageFormat.format(
      model.resources.getString(L10NStockQuotes.SECURITY_PRICE_DISPLAY_FMT),
      security.getName(),
      model.uIDateFormat.format(DateUtil.strippedDateInt),
      latest!!.priceDisplay
    )
  }
  
  fun buildPriceLogText(model: StockQuotesModel): String {
    val haveCurrent = rate > 0
    var asofDate: String?
    val format: String
    var displayRate: Double
    if (haveCurrent) {
      // the current price can be intra-day, so log the date and time of the price update.
      asofDate = model.uIDateTimeFormat!!.format(Date(dateTimeStamp))
      format = "Current price for {0} as of {1}: {2}"
      displayRate = rate
    } else {
      asofDate = "?"
      format = "Latest historical price for {0} as of {1}: {2}"
      displayRate = 0.0
      val snap = findMostRecentValidRecord()
      if (snap != null) {
        displayRate = snap.closeRate
        asofDate = model.uIDateFormat.format(Date(snap.dateTimeGMT))
      }
    }
    val amount = if (displayRate == 0.0) 0 else relativeCurrency!!.getLongValue(1.0 / displayRate)
    val priceDisplay = relativeCurrency!!.formatFancy(amount, '.')
    
    return MessageFormat.format(format, security.getName(), asofDate, priceDisplay)
  }
  
  
  fun addHistory(history: History) {
    history.candles?.stream()?.forEach { candle: Candle -> addDayOfData(candle) }
  }
  
  private fun addDayOfData(candle: Candle) {
    history.add(StockRecord(candle, priceMultiplier))
  }
  
  companion object {
    fun getSuccessIcon(success: Boolean): String {
      return if (success) {
        N12EStockQuotes.GREEN_FONT_BEGIN + "&#x2714;" + N12EStockQuotes.FONT_END
      } else {
        N12EStockQuotes.RED_FONT_BEGIN + "&#x2716;" + N12EStockQuotes.FONT_END
      }
    }
  }
}
