/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.util.StreamTable
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import java.util.*

/**
 * A stock exchange definition.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class StockExchange : Comparable<StockExchange?> {
  // Fields
  var exchangeId: String? = null
    private set
  var name: String? = null
  var country: String? = null
    private set
  var symbolGoogle: String? = null
  var symbolYahoo: String? = null
  var symbolThomsonReuters: String? = null
    private set
  var priceMultiplier: Double = 0.0
  var timeZone: String? = null
    private set
  var gMTDiff: Float = 0f
    private set
  var timeRangePreMarket: String? = null
    private set
  var timeRangeMarket: String? = null
    private set
  var timeRangePostMarket: String? = null
    private set
  var currencyName: String? = null
    private set
  var currencyCode: String? = null
    private set
  
  fun setCurrency(currency: CurrencyType) {
    currencyName = currency.getName()
    currencyCode = currency.idString
  }
  
  fun loadFromSettings(settings: StreamTable?) {
    if (settings == null) return
    exchangeId = settings.getStr(ID_KEY, "-")
    name = settings.getStr(NAME_KEY, "?")
    currencyCode = settings.getStr(CURRCODE_KEY, "USD")
    symbolGoogle = settings.getStr(GOOGLE_KEY, "")
    symbolYahoo = settings.getStr(YAHOO_KEY, "")
    symbolThomsonReuters = settings.getStr(THOMSON_KEY, "")
    try {
      priceMultiplier = settings.getStr(MULTIPLIER_KEY, "1.0")!!.toDouble()
    } catch (nfex: NumberFormatException) {
      System.err.println("Error parsing price multiplier for stock exchange: " + name)
      priceMultiplier = 1.0
    }
    currencyName = settings.getStr(CURRNAME_KEY, "U.S. Dollar")
    country = settings.getStr(COUNTRY_KEY, "")
    timeZone = settings.getStr(TIMEZONE_KEY, "?")
    gMTDiff = settings.getInt(GMT_DIFF_KEY, 0) / 10.0f
    timeRangePreMarket = settings.getStr(PRE_MTR_KEY, "")
    timeRangeMarket = settings.getStr(MTR_KEY, "")
    timeRangePostMarket = settings.getStr(POST_MTR_KEY, "")
    if (isBlank(exchangeId) || ("-" == exchangeId)) exchangeId = createIdFromEntry(this)
  }
  
  fun saveToSettings(): StreamTable {
    val settings = StreamTable()
    settings.put(ID_KEY, exchangeId)
    settings.put(NAME_KEY, name)
    settings.put(CURRCODE_KEY, currencyCode)
    settings.put(GOOGLE_KEY, symbolGoogle)
    settings.put(YAHOO_KEY, symbolYahoo)
    settings.put(THOMSON_KEY, symbolThomsonReuters)
    settings.put(MULTIPLIER_KEY, priceMultiplier.toString())
    settings.put(CURRNAME_KEY, currencyName)
    settings.put(COUNTRY_KEY, country)
    settings.put(TIMEZONE_KEY, timeZone)
    settings.put(GMT_DIFF_KEY, Math.round(gMTDiff * 10.0f))
    settings.put(PRE_MTR_KEY, timeRangePreMarket)
    settings.put(MTR_KEY, timeRangeMarket)
    settings.put(POST_MTR_KEY, timeRangePostMarket)
    return settings
  }
  
  override fun toString(): String {
    return name!!
  }
  
  override fun compareTo(o: StockExchange?): Int {
    if (o == null) return 1
    val otherName = o.name
    if (otherName == null) {
      if (name == null) return 0
      return 1
    }
    if (name == null) return -1
    return name!!.compareTo(otherName)
  }
  
  companion object {
    /**
     * Default exchange. This default will not make any changes to the stock symbol being looked up,
     * so the assumption is that the stock can be looked up for a quote without any additional
     * information. For U.S. stocks this is typically true.
     */
    public val DEFAULT = createFromCSV(
      "Default,USD,,,,1.0" +
      ",U.S. Dollar,United States,Eastern Standard Time (EST),-5,,,", "DEFAULT"
    )!!
    
    private const val ID_KEY = "id"
    private const val NAME_KEY = "name"
    private const val CURRCODE_KEY = "curr_id"
    private const val GOOGLE_KEY = "google_id"
    private const val YAHOO_KEY = "yahoo_id"
    private const val THOMSON_KEY = "thomson_id"
    private const val MULTIPLIER_KEY = "price_multiplier"
    private const val CURRNAME_KEY = "curr_name"
    private const val COUNTRY_KEY = "country"
    private const val TIMEZONE_KEY = "time_zone"
    private const val GMT_DIFF_KEY = "gmt_diff"
    private const val PRE_MTR_KEY = "pre_mtr"
    private const val MTR_KEY = "mtr"
    private const val POST_MTR_KEY = "post_mtr"
    
    /**
     * Generate a single stock exchange definition entry via a Comma Separated Value string. The
     * columns are defined thus:
     *
     *  1. Exchange Name
     *  1. Currency Code
     *  1. Google Finance Symbol
     *  1. Yahoo! Finance Symbol
     *  1. Thomson Reuters Symbol
     *  1. Currency Name
     *  1. Country
     *  1. Time Zone
     *  1. GMT ± (integer)
     *  1. Pre-Market Time Range
     *  1. Market Session Time Range
     *  1. Post-Market Time Range
     *
     * The first 6 columns need to be defined.
     * @param csvEntry String defining one stock exchange entity.
     * @param id The identifier to use, if `null` an identifier is auto-generated from
     * the symbols.
     * @return The stock exchange object with properties defined by `csvEntry`, or
     * `null` if an entry could not be created.
     */
    /**
     * Generate a stock exchange entry and auto-generate the unique key for it.
     * @see StockExchange.createFromCSV
     * @param csvEntry The comma-separated values for the entry.
     * @return A stock exchange entry, with an auto-generated unique key.
     */
    @JvmOverloads
    fun createFromCSV(csvEntry: String, id: String? = null): StockExchange? {
      if (isBlank(csvEntry)) return null
      val segments = csvEntry.split(",".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
      val result = StockExchange()
      result.name = getCSVEntry(segments[0])
      if (segments.size > 1) result.currencyCode = getCSVEntry(segments[1])
      if (segments.size > 2) result.symbolGoogle = getCSVEntry(segments[2])
      if (segments.size > 3) result.symbolYahoo = getCSVEntry(segments[3])
      if (segments.size > 4) result.symbolThomsonReuters = getCSVEntry(segments[4])
      try {
        if (segments.size > 5) {
          result.priceMultiplier = getCSVEntry(segments[5]).toDouble()
        }
      } catch (nfex: NumberFormatException) {
        System.err.println("Quote sync error parsing price multiplier for stock exchange: " + result.name)
        result.priceMultiplier = 1.0
      }
      if (segments.size > 6) result.currencyName = getCSVEntry(segments[6])
      if (segments.size > 7) result.country = getCSVEntry(segments[7])
      if (segments.size > 8) result.timeZone = getCSVEntry(segments[8])
      // the India exchanges are +5:30 or +5.5 so we support floating point values
      try {
        if (segments.size > 9) {
          result.gMTDiff = getCSVEntry(segments[9]).toFloat()
        }
      } catch (nfex: NumberFormatException) {
        System.err.println("Quote sync error parsing GMT difference for stock exchange: " + result.name)
        result.gMTDiff = 0.0f
      }
      if (segments.size > 10) result.timeRangePreMarket = getCSVEntry(segments[10])
      if (segments.size > 11) result.timeRangeMarket = getCSVEntry(segments[11])
      if (segments.size > 12) result.timeRangePostMarket = getCSVEntry(segments[12])
      result.exchangeId = id ?: createIdFromEntry(result)
      return result
    }
    
    private fun createIdFromEntry(result: StockExchange): String {
      val key = StringBuilder()
      val codes: MutableList<String> = ArrayList(3)
      codes.add(getIdCode(result.symbolYahoo!!))
      codes.add(getIdCode(result.symbolGoogle!!))
      codes.add(getIdCode(result.symbolThomsonReuters!!))
      Collections.sort(codes)
      key.append(codes[2])
      key.append("-")
      key.append(codes[1])
      key.append("-")
      key.append(codes[0])
      return key.toString()
    }
    
    private fun getIdCode(symbol: String): String {
      if (isBlank(symbol)) return "0"
      val result = symbol.lowercase(Locale.getDefault())
      return if (result.indexOf('.') == 0) result.substring(1) else result
    }
    
    private fun getCSVEntry(rawText: String): String {
      if (isBlank(rawText)) return ""
      return rawText.trim()
    }
  }
}
