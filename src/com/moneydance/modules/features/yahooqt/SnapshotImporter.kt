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
import com.infinitekind.util.DateUtil.convertIntDateToLong
import com.infinitekind.util.DateUtil.lastMinuteInDay
import com.infinitekind.util.StringUtils.countFields
import com.infinitekind.util.StringUtils.fieldIndex
import com.infinitekind.util.StringUtils.parseDouble
import com.moneydance.apps.md.controller.Util
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import java.io.BufferedReader
import java.io.FileNotFoundException
import java.io.IOException
import java.text.ParseException
import java.text.SimpleDateFormat
import java.util.*

/**
 * Imports price history / exchange rate history from a text stream into a list of
 * [CurrencySnapshot] objects. The default format is from Yahoo price history which
 * returns data in this format:
 * <pre>
 * Date,Open,High,Low,Close,Volume,Adj Close
</pre> *
 * where `Adj Close` is the Close price adjusted for dividends and splits. For
 * simplicity we only use the Date, High, Low, Close and Volume columns, with Date and Close
 * being the required columns.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
abstract class SnapshotImporter
  (protected val _resources: ResourceProvider, protected val downloadInfo: DownloadInfo,
   private val _expectedDateFormat: SimpleDateFormat, timeZone: TimeZone?,
   /**
    * This is the decimal character selected by the user, which can be used only if the data is not
    * comma-delimited.
    */
   private val _userDecimal: Char) {
  protected val _importRecords: MutableList<StockRecord> = ArrayList()
  
  private var _defaultDateFormat: SimpleDateFormat? = null
  private var _defaultTimeFormat = SimpleDateFormat("h:mma")
  private var _dateIndex = 0
  private var _timeIndex = 1
  private var _highIndex = 2
  private var _lowIndex = 3
  private var _closeIndex = 4
  private var _volumeIndex = 6
  
  private var _columnDelim = ','
  private var _dateDelim = '-'
  private var _dateDelimDetected = false
  private var _useDefaultDateFormat = false
  private var _useExpectedDateFormat = false
  
  /** Since the default is comma-delimited, the decimal character is by default a '.'  */
  private var _decimal = '.'
  private var _autoDetectFormat = true
  private var _priceMultiplier = 1.0
  
  var lastException: Exception? = null
    private set
  
  
  /**
   * Set format auto-detect, which requires that the first line of data be a header line containing
   * [.DATE_HEADERS] and [.CLOSE_HEADERS] at minimum, and optionally any of the other pre-
   * defined headers. If turned off, then either
   * [SnapshotImporter.setColumnsFromHeader]
   * or
   * [SnapshotImporter.detectFormat]
   * needs to be called prior to calling [.importData].
   *
   * @param autoDetect True if autodetect should be turned on, false otherwise.
   */
  fun setAutodetectFormat(autoDetect: Boolean) {
    _autoDetectFormat = autoDetect
  }
  
  /**
   * Define the multiplier to be applied to all prices that come in. The default is 1.0.
   * @param priceMultiplier The multiplier to apply to prices.
   */
  fun setPriceMultiplier(priceMultiplier: Double) {
    _priceMultiplier = priceMultiplier
  }
  
  /**
   * Determine whether the input contains appropriate information for reading price or exchange rate
   * history, and if so, how many items it can find. Call this method before calling
   * [.importData], unless you use format autodetect which requires that a header line
   * exists.
   *
   * @return The number of valid items found. If less than zero, the input stream is not in a
   * detectable format.
   */
  fun detectFormat(): Int {
    if (!isInputStreamValid) return ERROR_NO_INPUT_STREAM
    val reader: BufferedReader
    try {
      reader = inputStream
    } catch (error: FileNotFoundException) {
      lastException = error
      return ERROR_NO_INPUT_STREAM
    } catch (error: IOException) {
      lastException = error
      return ERROR_READ_INPUT
    } catch (error: NumberFormatException) {
      lastException = error
      return ERROR_MALFORMED_TEXT
    } catch (error: DownloadException) {
      lastException = error
      return ERROR_OTHER
    } catch (error: Exception) {
      lastException = error
      return ERROR_OTHER
    }
    
    var validItemCount = -1
    try {
      // find the first nonblank line and see if we have textual data
      var header = reader.readLine() ?: return ERROR_NO_VALID_DATA
      // stream is blank, no data
      
      while (reader.ready() && isBlank(header)) header = reader.readLine()
      if (containsNoText(header)) return ERROR_NOT_TEXT_DATA // not the right kind of data
      
      _columnDelim = detectDelimiter(header)
      if (_columnDelim != ',') {
        // comma-separated data requires a decimal point '.', but other delimiters don't
        _decimal = _userDecimal
      }
      if (countFields(header, _columnDelim) < 2) return ERROR_NO_COLUMNS // not enough columns
      
      val headerDefined = setColumnsFromHeader(header)
      if (!headerDefined && !isValidItem(header)) return ERROR_MALFORMED_TEXT // malformed
      
      validItemCount = if (headerDefined) 0 else 1
      var lineItem = reader.readLine()
      while (lineItem != null) {
        if (isValidItem(lineItem)) ++validItemCount
        // next line
        lineItem = reader.readLine()
      }
    } catch (e: IOException) {
      return ERROR_READING_DATA
    } finally {
      try {
        reader.close()
      } catch (ignore: IOException) {
        // ignore
      }
    }
    return validItemCount
  }
  
  
  /**
   * Constructor to allow input fields to be final.
   * @param resources          Object to look up localized resources.
   * @param downloadInfo       The currency/security download information whose history will be updated from the input stream.
   * @param expectedDateFormat The user-specified date format.
   * @param timeZone           Time zone to use when parsing downloaded time values.
   * @param userDecimal        The user-specified character to use as a decimal point.
   */
  init {
    if (timeZone != null) _defaultTimeFormat.timeZone = timeZone
  }
  
  /**
   * Determine the column indices of the data using the column delimiter.
   * @param header The header text.
   * @return True if header information was found, false if no valid header information exists.
   */
  fun setColumnsFromHeader(header: String?): Boolean {
    val header = header ?: ""
    val columnCount = countFields(header, _columnDelim)
    var hasAnyHeader = false
    var hasDate = false
    var hasTime = false
    var hasClose = false
    var hasHigh = false
    var hasLow = false
    var hasVolume = false
    // look for Unicode marker characters, sent by Google
    val offset = findUnicodeBOM(header)
    val parseInput = header.substring(offset)
    for (column in 0..<columnCount) {
      val columnName = stripQuotes(fieldIndex(parseInput, _columnDelim, column)).lowercase(Locale.getDefault())
      if (DATE_HEADERS.contains(columnName)) {
        hasAnyHeader = true
        hasDate = true
        _dateIndex = column
      } else if (TIME_HEADERS.contains(columnName)) {
        hasAnyHeader = true
        hasTime = true
        _timeIndex = column
      } else if (CLOSE_HEADERS.contains(columnName)) {
        hasAnyHeader = true
        hasClose = true
        _closeIndex = column
      } else if (HIGH_HEADERS.contains(columnName)) {
        hasAnyHeader = true
        hasHigh = true
        _highIndex = column
      } else if (LOW_HEADERS.contains(columnName)) {
        hasAnyHeader = true
        hasLow = true
        _lowIndex = column
      } else if (VOLUME_HEADERS.contains(columnName)) {
        hasAnyHeader = true
        hasVolume = true
        _volumeIndex = column
      }
    }
    
    if (!hasAnyHeader) return false // first line is data, not a header, use default column indices
    
    if (!hasDate) return false // the date field needs to be defined
    
    if (!hasClose) {
      // the column for closing price/rate uses a different header, so assume it is next to date
      _closeIndex = if (_dateIndex == columnCount - 1) {
        // we know there are at least two columns, put price in column to left of date
        _dateIndex - 1
      } else {
        _dateIndex + 1 // put price in column to right of date
      }
    }
    if (!hasHigh) _highIndex = -1 // won't use
    
    if (!hasLow) _lowIndex = -1 // won't use
    
    if (!hasVolume) _volumeIndex = -1 // won't use
    
    if (!hasTime) _timeIndex = -1 // won't use
    
    return true
  }
  
  /**
   * Do the import of the history items from the specified input stream. A call to
   * [.detectFormat] or (@link #setColumnsFromHeader(String)}
   * should be made prior to calling this method.
   *
   * @return A number less than zero if a system error occurred, zero for no error, and a positive
   * integer if one or more candidate lines in the input stream could not be imported.
   */
  fun importData(): Int {
    _importRecords.clear()
    if (!isInputStreamValid) return ERROR_NO_INPUT_STREAM
    onBeginImport()
    val `in`: BufferedReader
    try {
      `in` = inputStream
    } catch (error: FileNotFoundException) {
      lastException = error
      return ERROR_NO_INPUT_STREAM
    } catch (error: IOException) {
      lastException = error
      return ERROR_READ_INPUT
    } catch (error: NumberFormatException) {
      lastException = error
      return ERROR_MALFORMED_TEXT
    } catch (error: DownloadException) {
      lastException = error
      return ERROR_OTHER
    } catch (error: Exception) {
      lastException = error
      return ERROR_OTHER
    }
    var errorCount = ERROR_NO_VALID_DATA
    try {
      // find the first non-blank line and see if we have textual data
      var header: String? = `in`.readLine() ?: return ERROR_NO_DATA
      // stream is blank, no data
      
      QER_DLOG.log { "h:$header" }
      while (`in`.ready() && isBlank(header)) {
        header = `in`.readLine()
        QER_DLOG.log { "h:$header" }
      }
      if (containsNoText(header)) return ERROR_READING_DATA // not the right kind of input stream
      
      var lineItem: String?
      if (_autoDetectFormat) {
        if (!setColumnsFromHeader(header)) return ERROR_NO_HEADER
      }
      if (isValidItem(header)) {
        lineItem = header
      } else {
        // skip the header and move on to the next line
        lineItem = `in`.readLine()
        QER_DLOG.log { "dh:$lineItem" }
      }
      
      errorCount = 0
      while (lineItem != null) {
        if (isValidItem(lineItem)) {
          val record = parseStockRecordFromCSV(lineItem)
          if (record == null) {
            ++errorCount
          } else {
            _importRecords.add(record)
          }
        } else {
          System.err.println("Import error: skipping invalid line: $lineItem")
          ++errorCount
        }
        // next line
        lineItem = `in`.readLine()
        QER_DLOG.log { "dl:$lineItem" }
      }
    } catch (error: IOException) {
      System.err.println("Error while importing history: $error")
      errorCount = ERROR_NOT_TEXT_DATA
      lastException = error
    } catch (error: Exception) {
      lastException = error
    } finally {
      try {
        `in`.close()
      } catch (ignore: IOException) {
        // ignore
      }
    }
    
    onEndImport(errorCount)
    return errorCount
  }
  
  /**
   * Store the downloaded prices into the security currency's history. We don't save the current
   * price here because it must be decided at a higher level whether to update current price. Even
   * if the full history download successfully gets a more recent price than is stored with the
   * security, it may be overridden by the current price download (which can have intra-day pricing).
   * @return True if successful, false if there was nothing applied.
   */
  fun apply(): Boolean {
    if (_importRecords.isEmpty()) return false
    var success = false
    for (record in _importRecords) {
      val snap = addOrUpdateSnapshot(downloadInfo, record)
      //System.err.println("security updated snapshot: "+snap);
      success = success or (snap.rate > 0.0)
    }
    return success
  }
  
  val importedRecords: List<StockRecord>
    get() = _importRecords
  
  protected abstract fun onBeginImport()
  protected abstract fun onEndImport(errorCount: Int)
  protected abstract val isInputStreamValid: Boolean
  
  @get:Throws(IOException::class, DownloadException::class, NumberFormatException::class)
  protected abstract val inputStream: BufferedReader
  
  /**
   * Determine if the line given is a valid line for a price history.
   * @param line The line of text to test.
   * @return True if valid, false if one or more fields are not defined.
   */
  private fun isValidItem(line: String?): Boolean {
    if (line==null || isBlank(line)) return false
    val columnCount = countFields(line, _columnDelim)
    // check the required columns
    val dateStr = stripQuotes(fieldIndex(line, _columnDelim, _dateIndex))
    if ((_dateIndex >= columnCount) || hasNoDigits(dateStr)) {
      return false
    }
    if (!_dateDelimDetected && Character.isDigit(dateStr[0])) {
      for (index in 0..<dateStr.length) {
        val ch = dateStr[index]
        if (!Character.isDigit(ch)) {
          _dateDelim = ch
          _dateDelimDetected = true
          val formatStr = StringBuilder("yyyy")
          formatStr.append(_dateDelim)
          formatStr.append("MM")
          formatStr.append(_dateDelim)
          formatStr.append("dd")
          _defaultDateFormat = SimpleDateFormat(formatStr.toString())
          break
        }
      }
    }
    
    if ((_closeIndex >= columnCount) ||
        hasNoDigits(fieldIndex(line, _columnDelim, _closeIndex))
    ) {
      return false
    }
    // check the optional fields
    if (_highIndex >= 0) {
      if ((_highIndex >= columnCount) ||
          hasNoDigits(fieldIndex(line, _columnDelim, _highIndex))
      ) {
        return false
      }
    }
    if (_lowIndex >= 0) {
      if ((_lowIndex >= columnCount) ||
          hasNoDigits(fieldIndex(line, _columnDelim, _lowIndex))
      ) {
        return false
      }
    }
    if (_volumeIndex >= 0) {
      if ((_volumeIndex >= columnCount) ||
          hasNoDigits(fieldIndex(line, _columnDelim, _volumeIndex))
      ) {
        return false
      }
    }
    // this is a valid line
    return true
  }
  
  /**
   * Convert a string line from the import stream into a history entry.
   * @param record The line from the import stream.
   * @return The history snapshot, or `null` if the line contains invalid data.
   */
  private fun parseStockRecordFromCSV(record: String): StockRecord? {
    val date = parseDate(fieldIndex(record, _columnDelim, _dateIndex))
    if (date == 0) {
      System.err.println("Import error: discarding currency snapshot with zero date: $record")
      return null
    }
    // we have enough data to create a valid price snapshot
    val rate = parseUserRate(
      fieldIndex(record, _columnDelim, _closeIndex), 0.0, _priceMultiplier
    )
    if (rate == 0.0) {
      System.err.println("Import error: discarding currency snapshot with zero price: $record")
      return null
    }
    val result = StockRecord()
    result.date = date
    result.closeRate = rate // for saving in the snapshot
    if (_volumeIndex >= 0) {
      result.volume = parseLong(
        fieldIndex(record, _columnDelim, _volumeIndex), 0
      )
    }
    if (_lowIndex >= 0) {
      result.lowRate = parseUserRate(
        fieldIndex(record, _columnDelim, _lowIndex), 0.0, _priceMultiplier
      )
    }
    if (_highIndex >= 0) {
      result.highRate = parseUserRate(
        fieldIndex(record, _columnDelim, _highIndex), 0.0, _priceMultiplier
      )
    }
    if (_timeIndex >= 0) {
      // this time will be as of the connection time (Yahoo U.S. = EDT, Yahoo U.K. = GMT)
      result.dateTimeGMT = parseTimeInGMT(date, fieldIndex(record, _columnDelim, _timeIndex))
    } else {
      // this will set the time to midnight so that it will generally be less than the current price
      // update time
      result.dateTimeGMT = lastMinuteInDay(convertIntDateToLong(date)).time
    }
    return result
  }
  
  /**
   * Decipher the date. The date needs to be in YYYY*MM*DD format.
   * @param dateStr The string date to parse.
   * @return The date in integer format.
   */
  private fun parseDate(dateStr: String): Int {
    val value = stripQuotes(dateStr)
    if (isBlank(value)) return 0
    if (value.indexOf(_dateDelim) < 0) return 0
    if (_useExpectedDateFormat) return parseDateInt(_expectedDateFormat, value)
    if (_useDefaultDateFormat) return parseDateInt(_defaultDateFormat!!, value)
    // try the expected date format first
    if (matchesPattern(_expectedDateFormat, value)) {
      _useExpectedDateFormat = true
      return parseDateInt(_expectedDateFormat, value)
    }
    // then try to fall back on the default
    if (matchesPattern(_defaultDateFormat!!, value)) {
      _useDefaultDateFormat = true
      return parseDateInt(_defaultDateFormat!!, value)
    }
    // no match
    return 0
  }
  
  fun parseDateInt(format: SimpleDateFormat, value: String): Int {
    try {
      val date = format.parse(value)
      return Util.convertDateToInt(date)
    } catch (e: ParseException) {
      System.err.println("Encountered bad date value: $value")
      // not parsed
      return 0
    }
  }
  
  /**
   * Given a downloaded time string, return a date and time in GMT converted from the time that is
   * local to the connection, i.e. Yahoo U.S. is in EDT, Yahoo U.K. is in GMT.
   * @param date    The integer date.
   * @param timeStr The downloaded time string, in the time zone of the stock exchange.
   * @return A date and time in GMT.
   */
  fun parseTimeInGMT(date: Int, timeStr: String): Long {
    // The default time is 12 noon, so we convert to midnight before adding the parsed
    // time. The parsed time will be as of the stock exchange local time.
    val startDate = getMidnightDateTime(date)
    try {
      val value = stripQuotes(timeStr)
      if (isBlank(value)) return startDate
      // this converts the time into GMT as if the time were in the current locale or specified time zone
      val time = _defaultTimeFormat.parse(value.uppercase(Locale.getDefault())).time
      return startDate + time
    } catch (e: ParseException) {
      System.err.println("Encountered bad time value: $timeStr")
      // not parsed
      return startDate
    }
  }
  
  private fun parseUserRate(doubleStr: String, defaultValue: Double, multiplier: Double): Double {
    val value = stripQuotes(doubleStr)
    if (isBlank(value)) return defaultValue
    if (isNA(value)) return defaultValue
    var userPrice = parseDouble(value, defaultValue, _decimal)
    if (userPrice == 0.0) return 0.0
    userPrice *= multiplier
    // the rate is the inverse of the price
    return 1.0 / Util.safeRate(userPrice)
  }
  
  private fun parseLong(longStr: String, defaultValue: Long): Long {
    val value = stripQuotes(longStr)
    if (isBlank(value)) return defaultValue
    if (isNA(value)) return 0
    
    try {
      return value.toLong()
    } catch (e: NumberFormatException) {
      System.err.println("encountered bad integer value: $defaultValue")
      return defaultValue
    }
  }
  
  private fun detectDelimiter(header: String): Char {
    var commaCount = 0
    var tabCount = 0
    var barCount = 0
    for (index in 0..<header.length) {
      val ch = header[index]
      if (ch == ',') ++commaCount
      if (ch == '\t') ++tabCount
      if (ch == '|') ++barCount
    }
    if (barCount != 0) return '|'
    if (tabCount >= commaCount) return '\t'
    return ','
  }
  
  companion object {
    const val ERROR_NO_INPUT_STREAM: Int = -2
    const val ERROR_READ_INPUT: Int = -3
    const val ERROR_NO_DATA: Int = -4
    const val ERROR_READING_DATA: Int = -5
    const val ERROR_NO_VALID_DATA: Int = -6
    const val ERROR_NOT_TEXT_DATA: Int = -7
    const val ERROR_NO_COLUMNS: Int = -8
    const val ERROR_MALFORMED_TEXT: Int = -9
    const val ERROR_NO_HEADER: Int = -10
    const val ERROR_OTHER: Int = -11
    
    private val DATE_HEADERS: List<String> = mutableListOf("date", "timestamp")
    private val TIME_HEADERS: List<String> = mutableListOf("time")
    private val CLOSE_HEADERS: List<String> = mutableListOf("close")
    private val HIGH_HEADERS: List<String> = mutableListOf("high")
    private val LOW_HEADERS: List<String> = mutableListOf("low")
    private val VOLUME_HEADERS: List<String> = mutableListOf("volume", "vol")
    
    
    private fun addOrUpdateSnapshot(downloadInfo: DownloadInfo,
                                    record: StockRecord): CurrencySnapshot {
      // all snapshots are recorded in terms of the base currency.
      val newRate = convertToBasePrice(record.closeRate, downloadInfo.relativeCurrency, record.date)
      val result = downloadInfo.security.setSnapshotInt(record.date, newRate)
      // downloaded values are prices in a certain currency, change to rates for the stock history
      result.dailyHigh = convertToBasePrice(record.highRate, downloadInfo.relativeCurrency, record.date)
      result.dailyLow = convertToBasePrice(record.lowRate, downloadInfo.relativeCurrency, record.date)
      result.dailyVolume = record.volume
      result.syncItem()
      return result
    }
    
    
    /**
    * Convert the given price (in terms of the given currency) to a price in terms of the base currency.
    *
    * This is copied from CurrencyTable.convertToBasePrice() to avoid an unnecessary conversion to
    * an integer date, which is already available.
    * @param priceFromCurr The downloaded price, in terms of `priceCurrency`
    * @param priceCurrency The currency that the price is defined in .
    * @param date Integer date of the conversion.
    * @ return The price, converted to the base currency of the file.
    */
    private fun convertToBasePrice(priceFromCurr: Double, priceCurrency: CurrencyType, date: Int): Double {
      return (priceCurrency.getSnapshotForDate(date)?.rate ?: priceCurrency.relativeRate) * priceFromCurr
    }
    
    /**
     * Finds all the Unicode characters in the Special block, which are used to identify the Unicode
     * stream's Byte Order Mark or BOM. For example, Google adds character 0xFEFF = 65279 as the first
     * character in the stream to identify the stream as UTF-8 .
     * See http://en.wikipedia.org/wiki/Byte_order_mark
     *
     * @param text The text to scan.
     * @return The offset into the string where the first non-BOM character exists, or 0 to include
     * all of the string, there is no BOM.
     */
    private fun findUnicodeBOM(text: String?): Int {
      text ?: return 0
      if (isBlank(text)) return 0
      var offset = 0
      for (index in 0..<text.length) {
        if (!isSpecial(text[index])) break
        ++offset
      }
      return offset
    }
    
    /**
     * Test if a string has a numeric digit somewhere in it, or not.
     * @param text The text to test.
     * @return True if there is a numeric digit in the string, false otherwise.
     */
    private fun hasNoDigits(text: String): Boolean {
      if (isBlank(text)) return true
      val number = text.trim()
      if (isNA(number)) return false // allowed value
      
      for (index in 0..<number.length) {
        if (Character.isDigit(number[index])) return false
      }
      return true
    }
    
    private fun isNA(text: String): Boolean {
      return text.compareTo("N/A", ignoreCase = true) == 0
    }
    
    /**
     * Given an integer date, return a date/time at midnight for that date.
     * @param date The integer date to convert to a date and time.
     * @return The date and time, in milliseconds after 1/1/1970, for midnight of the given date.
     */
    private fun getMidnightDateTime(date: Int): Long {
      val msecPerMinute = (60 * 1000).toLong()
      return Util.firstMinuteInDay(Util.convertIntDateToLong(date)).time - msecPerMinute
    }
    
    private fun matchesPattern(format: SimpleDateFormat, candidate: String): Boolean {
      var matches: Boolean
      try {
        val result = format.parse(candidate)
        matches = (result != null)
      } catch (e: ParseException) {
        matches = false
      }
      return matches
    }
    
    private fun containsNoText(candidate: String?): Boolean {
      candidate ?: return true
      var containsText = true
      for (index in candidate.length - 1 downTo 0) {
        val ch = candidate[index]
        containsText = Character.isWhitespace(ch) || Character.isLetterOrDigit(ch) ||
                       isPunctuation(ch)
        if (containsText) break // bad character found
      }
      return !containsText
    }
    
    private fun isPunctuation(ch: Char): Boolean {
      when (Character.getType(ch).toByte()) {
        Character.CONNECTOR_PUNCTUATION -> return true
        Character.CURRENCY_SYMBOL -> return true
        Character.DASH_PUNCTUATION -> return true
        Character.ENCLOSING_MARK -> return true
        Character.END_PUNCTUATION -> return true
        Character.MATH_SYMBOL -> return true
        Character.OTHER_PUNCTUATION -> return true
        Character.START_PUNCTUATION -> return true
      }
      return false
    }
    
    private fun isSpecial(ch: Char): Boolean {
      // tried to get the Unicode block from the character and test against
      // Character.UnicodeBlock.SPECIALS, but it didn't work so I gave up on that.
      return ((ch == '\ufeff') || (ch == '\ufffe'))
    }
    
    private fun stripQuotes(input: String): String {
      if (isBlank(input)) return ""
      if (!input.contains("\"") && !input.contains("'")) return input.trim()
      val sb = StringBuilder()
      for (index in 0..<input.length) {
        val ch = input[index]
        if (!Character.isWhitespace(ch) && (ch != '\'') && (ch != '"')) {
          sb.append(ch)
        }
      }
      return sb.toString()
    }
  }
}
