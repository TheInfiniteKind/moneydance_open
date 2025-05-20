/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.AccountBook
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.moneydance.model.Legacy
import com.infinitekind.util.StringUtils.isInteger
import com.moneydance.apps.md.controller.Util
import com.moneydance.apps.md.controller.time.TimeInterval
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

/**
 * Stock Quote Utility methods. Most are copied from MD2010r2+ StringUtils or UiUtil, but this
 * plugin is being is being kept compatible with MD2010r1 for the time being.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
internal object SQUtil {
  /**
   * Get a label from (plugin) resources, and if it does not have a colon, add it. Also adds a
   * space at the end for better spacing in the UI layout.
   *
   * @param resources Resource provider.
   * @param key       String key to look up in the resources
   * @return A string with a colon at the end.
   */
  fun getLabelText(resources: ResourceProvider, key: String): String {
    return addLabelSuffix(resources, resources.getString(key) ?: "")
  }
  
  /**
   * Add a colon prompt after a text label if it does not have a colon. Also adds a space at
   * the end for better spacing in the UI layout.
   *
   * @param resources Resource provider.
   * @param label     String to add the colon to.
   * @return A string with a colon at the end.
   */
  fun addLabelSuffix(resources: ResourceProvider, label: String): String {
    return if ((label.length > 0) && (label[label.length - 1]) != ':') {
      label + resources.getString(L10NStockQuotes.LABEL_COLON) + ' '
    } else {
      label
    }
  }
  
  fun urlEncode(toEncode: String?): String {
    toEncode ?: return ""
    return URLEncoder.encode(toEncode, StandardCharsets.UTF_8)
  }
  
  fun getNextDate(date: Int, interval: TimeInterval): Int {
    return when (interval) {
      TimeInterval.WEEK -> Util.incrementDate(date, 0, 0, 7)
      TimeInterval.MONTH -> Util.incrementDate(date, 0, 1, 0)
      TimeInterval.QUARTER -> Util.incrementDate(date, 0, 3, 0)
      TimeInterval.YEAR -> Util.incrementDate(date, 1, 0, 0)
      else -> Util.incrementDate(date) // the default is daily
    }
  }
  
  fun getPreviousDate(date: Int, interval: TimeInterval): Int {
    return when (interval) {
      TimeInterval.WEEK -> Util.incrementDate(date, 0, 0, -7)
      TimeInterval.MONTH -> Util.incrementDate(date, 0, -1, 0)
      TimeInterval.QUARTER -> Util.incrementDate(date, 0, -3, 0)
      TimeInterval.YEAR -> Util.incrementDate(date, -1, 0, 0)
      else -> Util.incrementDate(date, 0, 0, -1) // the default is daily
    }
  }
  
  fun pauseTwoSeconds() {
    try {
      Thread.sleep(2000)
    } catch (ignore: InterruptedException) {
      // do nothing
    }
  }
  
  /**
   * Wait for the specified time period, keeping this thread quiet in the meantime.
   * @param timeInNs The length of time, in nanoseconds, to wait.
   */
  fun delaySpecifiedTime(timeInNs: Long) {
    val targetTime = System.nanoTime() + timeInNs
    while (System.nanoTime() < targetTime) {
      try {
        // should sleep 20 times or less based upon a 5 second delay
        Thread.sleep(250L)
      } catch (ignore: InterruptedException) {
        // do nothing
      }
    }
  }
  
  /**
   * Replace one or more tokens inside another string with a value.
   * @param str          The string containing the token(s).
   * @param toReplace    The token, case sensitive, to be replaced.
   * @param replaceWith  The string to replace the token with. Can be `null`.
   * @return The `str` string with the token replaced with a new value.
   */
  fun replaceAll(str: String, toReplace: String, replaceWith: String?): String {
    var ii: Int
    var lastI = 0
    val sb = StringBuilder(str.length)
    while ((str.indexOf(toReplace, lastI).also { ii = it }) >= 0) {
      sb.append(str.substring(lastI, ii)) // add the text before the matched substring
      if (!isEmpty(replaceWith)) sb.append(replaceWith)
      lastI = ii + toReplace.length
    }
    sb.append(str.substring(lastI)) // add the rest
    return sb.toString()
  }
  
  /**
   * Determine if two objects of the same type are equal or not.
   * @param object1 Left hand side object.
   * @param object2 Right hand side object.
   * @param <T> The type of object being compared.
   * @return True if the objects are equal, false otherwise.
  </T> */
  fun <T> areEqual(object1: T?, object2: T?): Boolean {
    if (object1 === object2) return true // either same instance or both null
    
    if ((object1 == null) || (object2 == null)) return false // one is null, the other isn't
    
    return object1 == object2
  }
  
  /**
   * Null safe check for "" (empty string).
   *
   * @param candidate the String to evaluate.
   * @return true if candidate is null or "" (empty string)
   */
  private fun isEmpty(candidate: String?): Boolean {
    return candidate == null || candidate.length == 0
  }
  
  /**
   * Null safe check for a String with nothing but whitespace characters.
   *
   * @param candidate the String to evaluate.
   * @return true if the candidate is null or all whitespace.
   */
  fun isBlank(candidate: String?): Boolean {
    candidate ?: return true
    var isBlank = isEmpty(candidate)
    if (!isBlank) {
      for (index in candidate.length - 1 downTo 0) {
        isBlank = Character.isWhitespace(candidate[index])
        if (!isBlank) {
          break // non-whitespace character found, don't bother checking the remainder
        }
      }
    }
    return isBlank
  }
  
  /**
   * Parse out user-defined symbol information. The user may provide overrides in the symbol using
   * the following syntax:
   * <pre>
   * {GooglePrefix} : Symbol . {YahooSuffix} - {CurrencyCode}
  </pre> *
   * Where only `Symbol` is required, and no spaces are expected.
   * @param securityCurrency The security definition to obtain information for.
   * @return The parsed symbol data along with overrides. Note that the {YahooSuffix} will contain
   * the leading period, whereas the GooglePrefix will not contain a trailing colon. This is to
   * maintain compatibility with how the stock exchanges are defined.
   */
  fun parseTickerSymbol(securityCurrency: CurrencyType?): SymbolData? {
    if (securityCurrency == null) return null
    val rawTickerSymbol = securityCurrency.getTickerSymbol()
    if (isBlank(rawTickerSymbol)) return null
    return parseTickerSymbol(rawTickerSymbol)
  }
  
  /**
   * Parse out user-defined symbol information. The user may provide overrides in the symbol using
   * the following syntax:
   * <pre>
   * {GooglePrefix} : Symbol . {YahooSuffix} - {CurrencyCode}
  </pre> *
   * Where only `Symbol` is required, and no spaces are expected.
   * @param rawTickerSymbol The raw ticker symbol with all user edits of prefix, suffix or currency
   * @return The parsed symbol data along with overrides. Note that the {YahooSuffix} will contain
   * the leading period, whereas the GooglePrefix will not contain a trailing colon. This is to
   * maintain compatibility with how the stock exchanges are defined.
   */
  fun parseTickerSymbol(rawTickerSymbol: String): SymbolData? {
    var tickerSymbol = rawTickerSymbol.trim()
    var prefix: String? = null
    var suffix: String? = null
    var currencyCode: String? = null
    
    if (tickerSymbol.startsWith("^")) tickerSymbol = tickerSymbol.substring(1).trim()
    
    
    // break off a currency code if and only if the last 4 characters is -XXX where X is a letter,
    // OR if the user put in a carat delimiter
    val len = tickerSymbol.length
    val caratIndex = tickerSymbol.lastIndexOf('^')
    val hasDashOverride = ((len > 4) && (tickerSymbol[len - 4] == '-'))
    if ((len > 4) && (hasDashOverride || (caratIndex >= 0))) {
      var currencyFound = true
      if (caratIndex >= 0) {
        // include the period as the first character
        currencyCode = tickerSymbol.substring(caratIndex + 1).trim()
        if (isBlank(currencyCode)) suffix = null // ignore empty
        
        tickerSymbol = tickerSymbol.substring(0, caratIndex).trim()
      } else {
        // old-style dash currency override, being deprecated because dashes are allowed in symbols
        for (ii in len - 3..<len) {
          if (!Character.isLetter(tickerSymbol[ii])) {
            currencyFound = false
            break
          }
        }
        if (currencyFound) {
          currencyCode = tickerSymbol.substring(len - 3).trim()
          tickerSymbol = tickerSymbol.substring(0, len - 4).trim()
        }
      }
    }
    
    
    // check if a Google exchange prefix exists
    val colonIndex = tickerSymbol.indexOf(':')
    if (colonIndex >= 0) {
      prefix = tickerSymbol.substring(0, colonIndex).trim()
      tickerSymbol = tickerSymbol.substring(colonIndex + 1).trim()
    }
    val dotIndex = tickerSymbol.indexOf('.')
    if (dotIndex >= 0) {
      // include the period as the first character
      suffix = tickerSymbol.substring(dotIndex).trim()
      if ("." == suffix) suffix = null // ignore empty
      
      tickerSymbol = tickerSymbol.substring(0, dotIndex).trim()
    }
    if (isBlank(tickerSymbol)) {
      // this part is required, so if it doesn't exist, bail
      return null
    }
    return SymbolData(prefix ?: "", tickerSymbol, suffix ?: "", currencyCode ?: "")
  }
  
  
  /** Return the currency with the given ID.  This finds a currency based on the best identifier
   * available for each currency. Tries to locate the currency in the local file using the
   * MD2015+ UUID-based identifier, then the old integer identifier, followed by the
   * text currency ID which is usually based on the currency code or ticker symbol.  */
  fun getCurrencyWithID(book: AccountBook?, currencyID: String): CurrencyType? {
    if (book == null || isBlank(currencyID)) return null
    val table = book.currencies ?: return null
    
    var curr = table.getCurrencyByUUID(currencyID)
    if (curr != null) return curr
    
    if (isInteger(currencyID)) {
      curr = table.getCurrencyByID(currencyID.toInt())
      if (curr != null) return curr
    }
    
    return table.getCurrencyByIDString(currencyID)
  }
  
  
  /**
   * Unit test the methods.
   * @param argv Test arguments (not used).
   */
  @JvmStatic
  fun main(argv: Array<String>) {
    // test the parsing of symbols. Using symbol GIL.F or GILG.DE for Gildemeister
    val fakeBook = AccountBook.fakeAccountBook()
    val security = Legacy.makeCurrencyType(5000, "GIL", "Gildemeister", 1.0, 2, "", "GIL", "",
                                           19990101, CurrencyType.CURRTYPE_SECURITY, fakeBook.currencies)
    security.setTickerSymbol("  \t   \n ")
    var data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println("Blank test: " + (if (data != null) "FAIL" else "pass"))
    // straightforward tests
    var symbol = "GIL"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA:GIL"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "GIL.F"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "GIL.F-EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA:GIL.F-EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA:GIL-EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    // mangled cases
    symbol = ":  GIL . "
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA\t:  GIL .F    -EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "\t: \n GIL .-EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA:   .F-EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println("Blank test: " + (if (data != null) "FAIL" else "pass"))
    // now ensure we support the dash before the dot for oddball symbols like COS-UN.TO
    symbol = "COS-UN.TO"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "COS-UN -CAD  "
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    // verify support for the new replacement delimiter for currency override '^'
    symbol = "GIL.F^EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA:GIL.F^EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA:GIL^EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    // mangled cases
    symbol = "GIL.F^"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA\t:  GIL .F    ^EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "\t: \n GIL .^EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
    symbol = "FRA:   .F^EUR"
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println("Blank test: " + (if (data != null) "FAIL" else "pass"))
    symbol = "COS-UN ^CAD  "
    security.setTickerSymbol(symbol)
    data = parseTickerSymbol(security) ?: return QER_LOG.log("Null value from parseTickerSymbol($security)")
    System.err.println(
      ("Symbol '" + symbol + "' ="
       + "  prefix: " + (if (data!!.prefix == null) "(null)" else "'" + data.prefix + "'")
       + "  suffix: " + (if (data.suffix == null) "(null)" else "'" + data.suffix + "'")
       + "  symbol: " + (if (data.symbol == null) "(null)" else "'" + data.symbol + "'")
       + "  currency: " + (if (data.currencyCode == null) "(null)" else "'" + data.currencyCode + "'"))
    )
  }
}
