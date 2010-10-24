/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.util.StringUtils;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Vector;

/**
 * Imports price history / exchange rate history from a text stream into a list of
 * {@link CurrencyType.Snapshot} objects. The default format is from Yahoo price history which
 * returns data in this format:
 * <pre>
 * Date,Open,High,Low,Close,Volume,Adj Close
 * </pre>
 * where <code>Adj Close</code> is the Close price adjusted for dividends and splits. For
 * simplicity we only use the Date, High, Low, Close and Volume columns, with Date and Close
 * being the required columns.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public abstract class SnapshotImporter
{
  protected final CurrencyType _currency;
  protected final Vector<StockRecord> _importRecords = new Vector<StockRecord>();
  protected final ResourceProvider _resources;

  /**
   * This is the decimal character selected by the user, which can be used only if the data is not
   * comma-delimited.
   */
  private final char _userDecimal;
  private final SimpleDateFormat _expectedDateFormat;
  private SimpleDateFormat _defaultDateFormat;
  private SimpleDateFormat _defaultTimeFormat;
  static final String DATE_KEY = "DATE";
  static final String TIME_KEY = "TIME";
  static final String HIGH_KEY = "HIGH";
  static final String LOW_KEY = "LOW";
  static final String CLOSE_KEY = "CLOSE";
  static final String VOLUME_KEY = "VOLUME";
  static final int ERROR_NO_INPUT_STREAM = -2;
  static final int ERROR_READ_INPUT = -3;
  static final int ERROR_NO_DATA = -4;
  static final int ERROR_READING_DATA = -5;
  static final int ERROR_NO_VALID_DATA = -6;
  static final int ERROR_NOT_TEXT_DATA = -7;
  static final int ERROR_NO_COLUMNS = -8;
  static final int ERROR_MALFORMED_TEXT = -9;
  static final int ERROR_NO_HEADER = -10;
  static final int ERROR_OTHER = -11;

  private int _dateIndex = 0;
  private int _timeIndex = 1;
  private int _highIndex = 2;
  private int _lowIndex = 3;
  private int _closeIndex = 4;
  private int _volumeIndex = 5;

  private char _columnDelim = ',';
  private char _dateDelim = '-';
  private boolean _dateDelimDetected = false;
  private boolean _useDefaultDateFormat = false;
  private boolean _useExpectedDateFormat = false;
  /** Since the default is comma-delimited, the decimal character is by default a '.' */
  private char _decimal = '.';
  private boolean _autoDetectFormat = false;
  private double _priceMultiplier = 1.0;

  private Exception _lastException = null;


  /**
   * Constructor to allow input fields to be final.
   * @param resources          Object to look up localized resources.
   * @param currency           The currency whose history will be updated from the input stream.
   * @param expectedDateFormat The user-specified date format.
   * @param userDecimal        The user-specified character to use as a decimal point.
   */
  public SnapshotImporter(ResourceProvider resources, CurrencyType currency,
                          SimpleDateFormat expectedDateFormat, char userDecimal) {
    _currency = currency;
    _expectedDateFormat = expectedDateFormat;
    _userDecimal = userDecimal;
    _resources = resources;
    _defaultTimeFormat = new SimpleDateFormat("h:mma");
  }

  /**
   * Set format auto-detect, which requires that the first line of data be a header line containing
   * {@link #DATE_KEY} and {@link #CLOSE_KEY} at minimum, and optionally any of the other pre-
   * defined headers. If turned off, then either
   * {@link SnapshotImporter#setColumnsFromHeader(String)}
   * or
   * {@link SnapshotImporter#detectFormat()}
   * needs to be called prior to calling {@link #importData()}.
   *
   * @param autoDetect True if autodetect should be turned on, false otherwise.
   */
  public void setAutodetectFormat(boolean autoDetect) {
    _autoDetectFormat = autoDetect;
  }

  /**
   * Define the multiplier to be applied to all prices that come in. The default is 1.0.
   * @param priceMultiplier The multiplier to apply to prices.
   */
  public void setPriceMultiplier(double priceMultiplier) {
    _priceMultiplier = priceMultiplier;
  }

  /**
   * Determine whether the input contains appropriate information for reading price or exchange rate
   * history, and if so, how many items it can find. Call this method before calling
   * {@link #importData()}, unless you use format autodetect which requires that a header line
   * exists.
   * 
   * @return The number of valid items found. If less than zero, the input stream is not in a
   * detectable format.
   */
  public int detectFormat() {
    if (!isInputStreamValid()) return ERROR_NO_INPUT_STREAM;
    BufferedReader in;
    try {
      in = getInputStream();
    } catch (FileNotFoundException error) {
      _lastException = error;
      return ERROR_NO_INPUT_STREAM;
    } catch (IOException error) {
      _lastException = error;
      return ERROR_READ_INPUT;
    } catch (NumberFormatException error) {
      _lastException = error;
      return ERROR_MALFORMED_TEXT;
    } catch (DownloadException error) {
      _lastException = error;
      return ERROR_OTHER;
    } catch (Exception error) {
      _lastException = error;
      return ERROR_OTHER;
    }

    int validItemCount = -1;
    try {
      // find the first nonblank line and see if we have textual data
      String header = in.readLine();
      if (header == null) return ERROR_NO_VALID_DATA;        // stream is blank, no data
      while (in.ready() && SQUtil.isBlank(header)) header = in.readLine();
      if (containsNoText(header)) return ERROR_NOT_TEXT_DATA; // not the right kind of data
      _columnDelim = detectDelimiter(header);
      if (_columnDelim != ',') {
        // comma-separated data requires a decimal point '.', but other delimiters don't
        _decimal = _userDecimal;
      }
      if (StringUtils.countFields(header, _columnDelim) < 2) return ERROR_NO_COLUMNS; // not enough columns
      boolean headerDefined = setColumnsFromHeader(header);
      if (!headerDefined && !isValidItem(header)) return ERROR_MALFORMED_TEXT;  // malformed
      validItemCount = headerDefined ? 0 : 1;
      String lineItem = in.readLine();
      while (lineItem != null) {
        if (isValidItem(lineItem)) ++validItemCount;
        // next line
        lineItem = in.readLine();
      }
    }
    catch (IOException e) {
      return ERROR_READING_DATA;
    }
    finally
    {
      try {
        in.close();
      }
      catch (IOException ignore) {
        // ignore
      }
    }
    return validItemCount;
  }

  /**
   * Determine the column indices of the data using the column delimiter.
   * @param header The header text.
   * @return True if header information was found, false if no valid header information exists.
   */
  public boolean setColumnsFromHeader(String header)
  {
    int columnCount = StringUtils.countFields(header, _columnDelim);
    boolean hasAnyHeader = false;
    boolean hasDate = false;
    boolean hasTime = false;
    boolean hasClose = false;
    boolean hasHigh = false;
    boolean hasLow = false;
    boolean hasVolume = false;
    // look for Unicode marker characters, sent by Google
    int offset = findUnicodeBOM(header);
    final String parseInput = header.substring(offset);
    for (int column = 0; column < columnCount; column++) {
      String columnName = stripQuotes(StringUtils.fieldIndex(parseInput, _columnDelim, column));
      if (DATE_KEY.equalsIgnoreCase(columnName)) {
        hasAnyHeader = true;
        hasDate = true;
        _dateIndex = column;
      } else if (TIME_KEY.equalsIgnoreCase(columnName)) {
        hasAnyHeader = true;
        hasTime = true;
        _timeIndex = column;
      } else if (CLOSE_KEY.equalsIgnoreCase(columnName)) {
        hasAnyHeader = true;
        hasClose = true;
        _closeIndex = column;
      } else if (HIGH_KEY.equalsIgnoreCase(columnName)) {
        hasAnyHeader = true;
        hasHigh = true;
        _highIndex = column;
      } else if (LOW_KEY.equalsIgnoreCase(columnName)) {
        hasAnyHeader = true;
        hasLow = true;
        _lowIndex = column;
      } else if (VOLUME_KEY.equalsIgnoreCase(columnName)) {
        hasAnyHeader = true;
        hasVolume = true;
        _volumeIndex = column;
      }
    }
    if (!hasAnyHeader) return false; // first line is data, not a header, use default column indices
    if (!hasDate) return false; // the date field needs to be defined
    if (!hasClose) {
      // the column for closing price/rate uses a different header, so assume it is next to date
      if (_dateIndex == columnCount - 1) {
        // we know there are at least two columns, put price in column to left of date
        _closeIndex = _dateIndex - 1;
      } else {
        _closeIndex = _dateIndex + 1; // put price in column to right of date
      }
    }
    if (!hasHigh) _highIndex = -1;     // won't use
    if (!hasLow) _lowIndex = -1;       // won't use
    if (!hasVolume) _volumeIndex = -1; // won't use
    if (!hasTime) _timeIndex = -1;     // won't use
    return true;
  }

  /**
   * Do the import of the history items from the specified input stream. A call to
   * {@link #detectFormat()} or (@link #setColumnsFromHeader(String)}
   * should be made prior to calling this method.
   *
   * @return A number less than zero if a system error occurred, zero for no error, and a positive
   * integer if one or more candidate lines in the input stream could not be imported.
   */
  public int importData() {
    _importRecords.clear();
    if (!isInputStreamValid()) return ERROR_NO_INPUT_STREAM;
    onBeginImport();
    BufferedReader in;
    try {
      in = getInputStream();
    } catch (FileNotFoundException error) {
      _lastException = error;
      return ERROR_NO_INPUT_STREAM;
    } catch (IOException error) {
      _lastException = error;
      return ERROR_READ_INPUT;
    } catch (NumberFormatException error) {
      _lastException = error;
      return ERROR_MALFORMED_TEXT;
    } catch (DownloadException error) {
      _lastException = error;
      return ERROR_OTHER;
    } catch (Exception error) {
      _lastException = error;
      return ERROR_OTHER;
    }
    int errorCount = ERROR_NO_VALID_DATA;
    try {
      // find the first non-blank line and see if we have textual data
      String header = in.readLine();
      if (header == null) return ERROR_NO_DATA;    // stream is blank, no data
      while (in.ready() && SQUtil.isBlank(header)) header = in.readLine();
      if (containsNoText(header)) return ERROR_READING_DATA; // not the right kind of input stream
      String lineItem;
      if (_autoDetectFormat) {
        if (!setColumnsFromHeader(header)) return ERROR_NO_HEADER;
      }
      if (isValidItem(header)) {
        lineItem = header;
      } else {
        // skip the header and move on to the next line
        lineItem = in.readLine();
      }
      errorCount = 0;
      while (lineItem != null) {
        if (isValidItem(lineItem)) {
          final StockRecord record = addCurrencySnapshot(lineItem);
          if (record == null) {
            ++errorCount;
          } else {
            _importRecords.add(record);
          }
        } else {
          System.err.println("Import error: skipping invalid line: "+lineItem);
          ++errorCount;
        }
        // next line
        lineItem = in.readLine();
      }
    } catch (IOException error) {
      System.err.println("Error while importing history: "+error);
      errorCount = ERROR_NOT_TEXT_DATA;
    } finally {
      try {
        in.close();
      }
      catch (IOException ignore) {
        // ignore
      }
    }
    onEndImport(errorCount);
    return errorCount;
  }

  /**
   * Store the downloaded prices into the security currency's history. We don't save the current
   * price here because it must be decided at a higher level whether to update current price. Even
   * if the full history download successfully gets a more recent price than is stored with the
   * security, it may be overridden by the current price download (which can have intra-day pricing).
   * @param baseCurrency The currency to convert the price into (dollar, euro, etc.)
   * @return True if successful, false if there was nothing applied.
   */
  public boolean apply(CurrencyType baseCurrency) {
    if (_importRecords.isEmpty()) return false;
    boolean success = false;
    for (StockRecord record : _importRecords) {
      CurrencyType.Snapshot snap = addOrUpdateSnapshot(_currency, baseCurrency, record);
      success |= (snap.getUserRate() > 0.0);
    }
    return success;
  }

  public Vector<StockRecord> getImportedRecords() { return _importRecords; }

  public Exception getLastException() { return _lastException; }

  protected abstract void onBeginImport();
  protected abstract void onEndImport(int errorCount);
  protected abstract boolean isInputStreamValid();
  protected abstract BufferedReader getInputStream() 
          throws IOException, DownloadException, NumberFormatException;

  private static CurrencyType.Snapshot addOrUpdateSnapshot(CurrencyType currency,
                                                           CurrencyType baseCurrency,
                                                           StockRecord record)
  {
    final double newRate = CurrencyTable.convertToBasePrice(record.closeRate, baseCurrency,
            record.date);
    CurrencyType.Snapshot result = currency.setSnapshotInt(record.date, newRate);
    // downloaded values are prices in a certain currency, change to rates for the stock history
    result.setUserDailyHigh(CurrencyTable.convertToBasePrice(record.highRate, baseCurrency, record.date));
    result.setUserDailyLow(CurrencyTable.convertToBasePrice(record.lowRate, baseCurrency, record.date));
    result.setDailyVolume(record.volume);
    return result;
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

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
  private static int findUnicodeBOM(String text) {
    if (SQUtil.isBlank(text)) return 0;
    int offset = 0;
    for (int index = 0; index < text.length(); index++) {
      if (!isSpecial(text.charAt(index))) break;
      ++offset;
    }
    return offset;
  }

  /**
   * Determine if the line given is a valid line for a price history.
   * @param line The line of text to test.
   * @return True if valid, false if one or more fields are not defined.
   */
  private boolean isValidItem(String line) {
    if (SQUtil.isBlank(line)) return false;
    int columnCount = StringUtils.countFields(line, _columnDelim);
    // check the required columns
    final String dateStr = stripQuotes(StringUtils.fieldIndex(line, _columnDelim, _dateIndex));
    if ((_dateIndex >= columnCount) || hasNoDigits(dateStr)) {
      return false;
    }
    if (!_dateDelimDetected && Character.isDigit(dateStr.charAt(0)) ) {
      for (int index = 0; index < dateStr.length(); index++) {
        char ch = dateStr.charAt(index);
        if (!Character.isDigit(ch)) {
          _dateDelim = ch;
          _dateDelimDetected = true;
          StringBuilder formatStr = new StringBuilder("yyyy");
          formatStr.append(_dateDelim);
          formatStr.append("MM");
          formatStr.append(_dateDelim);
          formatStr.append("dd");
          _defaultDateFormat = new SimpleDateFormat(formatStr.toString());
          break;
        }
      }
    }

    if ((_closeIndex >= columnCount) ||
            hasNoDigits(StringUtils.fieldIndex(line, _columnDelim, _closeIndex))) {
      return false;
    }
    // check the optional fields
    if (_highIndex >= 0) {
      if ((_highIndex >= columnCount) ||
              hasNoDigits(StringUtils.fieldIndex(line, _columnDelim, _highIndex))) {
        return false;
      }
    }
    if (_lowIndex >= 0) {
      if ((_lowIndex >= columnCount) ||
              hasNoDigits(StringUtils.fieldIndex(line, _columnDelim, _lowIndex))) {
        return false;
      }
    }
    if (_volumeIndex >= 0) {
      if ((_volumeIndex >= columnCount) ||
              hasNoDigits(StringUtils.fieldIndex(line, _columnDelim, _volumeIndex))) {
        return false;
      }
    }
    // this is a valid line
    return true;
  }

  /**
   * Test if a string has a numeric digit somewhere in it, or not.
   * @param text The text to test.
   * @return True if there is a numeric digit in the string, false otherwise.
   */
  private static boolean hasNoDigits(String text) {
    if (SQUtil.isBlank(text)) return true;
    final String number = text.trim();
    if (isNA(number)) return false; // allowed value
    for (int index = 0; index < number.length(); index++) {
      if (Character.isDigit(number.charAt(index))) return false;
    }
    return true;
  }

  private static boolean isNA(final String text) { return text.compareToIgnoreCase("N/A") == 0; }

  /**
   * Convert a string line from the import stream into a history entry.
   * @param record The line from the import stream.
   * @return The history snapshot, or <code>null</code> if the line contains invalid data.
   */
  private StockRecord addCurrencySnapshot(String record) {
    int date = parseDate(StringUtils.fieldIndex(record, _columnDelim, _dateIndex));
    if(date==0) {
      System.err.println("Import error: discarding currency snapshot with zero date: "+record);
      return null;
    }
    // we have enough data to create a valid price snapshot
    final double rate = parseUserRate(
            StringUtils.fieldIndex(record, _columnDelim, _closeIndex), 0.0, _priceMultiplier);
    if (rate == 0.0) {
      System.err.println("Import error: discarding currency snapshot with zero price: "+record);
      return null;
    }
    StockRecord result = new StockRecord();
    result.date = date;
    result.closeRate = rate;         // for saving in the snapshot
    if (_volumeIndex >= 0) {
      result.volume = parseLong(
              StringUtils.fieldIndex(record, _columnDelim, _volumeIndex), 0);
    }
    if (_lowIndex >= 0) {
      result.lowRate = parseUserRate(
              StringUtils.fieldIndex(record, _columnDelim, _lowIndex), 0.0, _priceMultiplier);
    }
    if (_highIndex >= 0) {
      result.highRate = parseUserRate(
              StringUtils.fieldIndex(record, _columnDelim, _highIndex), 0.0, _priceMultiplier);
    }
    if (_timeIndex >= 0) {
      // this time will be as of the stock exchange local time
      result.dateTime = parseTime(date, StringUtils.fieldIndex(record, _columnDelim, _timeIndex));
    } else {
      // this will set the time to midnight so that it will generally be less than the current price
      // update time
      result.dateTime = getMidnightDateTime(date);
    }
    return result;
  }

  /**
   * Decipher the date. The date needs to be in YYYY*MM*DD format.
   * @param dateStr The string date to parse.
   * @return The date in integer format.
   */
  private int parseDate(String dateStr) {
    String value = stripQuotes(dateStr);
    if (SQUtil.isBlank(value)) return 0;
    if (value.indexOf(_dateDelim) < 0) return 0;
    if (_useExpectedDateFormat) return parseDateInt(_expectedDateFormat, value);
    if (_useDefaultDateFormat) return parseDateInt(_defaultDateFormat, value);
    // try the expected date format first
    if (matchesPattern(_expectedDateFormat, value)) {
      _useExpectedDateFormat = true;
      return parseDateInt(_expectedDateFormat, value);
    }
    // then try to fall back on the default
    if (matchesPattern(_defaultDateFormat, value)) {
      _useDefaultDateFormat = true;
      return parseDateInt(_defaultDateFormat, value);
    }
    // no match
    return 0;
  }

  int parseDateInt(SimpleDateFormat format, String value) {
    try {
      Date date = format.parse(value);
      return Util.convertDateToInt(date);
    } catch (ParseException e) {
      System.err.println("Encountered bad date value: " + value);
      // not parsed
      return 0;
    }
  }

  /**
   * Given a downloaded time string, return a date and time local to the stock exchange at which
   * the price is valid.
   * @param date    The integer date.
   * @param timeStr The downloaded time string, in the time zone of the stock exchange.
   * @return A date and time in the time zone of the stock exchange.
   */
  long parseTime(final int date, final String timeStr) {
    // The default time is 12 noon, so we convert to midnight before adding the parsed
    // time. The parsed time will be as of the stock exchange local time.
    long startDate = getMidnightDateTime(date);
    try {
      String value = stripQuotes(timeStr);
      if (SQUtil.isBlank(value)) return startDate;
      final long time = _defaultTimeFormat.parse(value).getTime();
      return startDate + time;
    } catch (ParseException e) {
      System.err.println("Encountered bad time value: " + timeStr);
      // not parsed
      return startDate;
    }
  }

  /**
   * Given an integer date, return a date/time at midnight for that date.
   * @param date The integer date to convert to a date and time.
   * @return The date and time, in milliseconds after 1/1/1970, for midnight of the given date.
   */
  private static long getMidnightDateTime(int date) {
    final long msecPerMinute = 60 * 1000;
    return Util.firstMinuteInDay(Util.convertIntDateToLong(date)).getTime() - msecPerMinute;
  }

  private static boolean matchesPattern(SimpleDateFormat format, String candidate) {
    boolean matches;
    try {
      final Date result = format.parse(candidate);
      matches = (result != null);
    } catch (ParseException e) {
      matches = false;
    }
    return matches;
  }

  private double parseUserRate(String doubleStr, double defaultValue, double multiplier) {
    String value = stripQuotes(doubleStr);
    if (SQUtil.isBlank(value)) return defaultValue;
    if (isNA(value)) return defaultValue;
    double userPrice = StringUtils.parseDouble(value, defaultValue, _decimal);
    if (userPrice == 0.0) return 0.0;
    userPrice *= multiplier;
    // the rate is the inverse of the price
    return 1.0 / Util.safeRate(userPrice);
  }

  private long parseLong(String longStr, long defaultValue) {
    String value = stripQuotes(longStr);
    if (SQUtil.isBlank(value)) return defaultValue;
    if (isNA(value)) return 0;
    try {
      return Long.valueOf(value).longValue();
    }
    catch (NumberFormatException e) {
      System.err.println("encountered bad integer value: " + defaultValue);
      return defaultValue;
    }
  }

  private char detectDelimiter(String header) {
    int commaCount = 0;
    int tabCount = 0;
    int barCount = 0;
    for (int index = 0; index < header.length(); index++) {
      final char ch = header.charAt(index);
      if (ch == ',') ++commaCount;
      if (ch == '\t') ++tabCount;
      if (ch == '|') ++barCount;
    }
    if (barCount != 0) return '|';
    if (tabCount >= commaCount) return '\t';
    return ',';
  }

  private static boolean containsNoText(String candidate) {
    boolean containsText = true;
    for (int index = candidate.length()-1; index >= 0; index--) {
      final char ch = candidate.charAt(index);
      containsText = Character.isWhitespace(ch) || Character.isLetterOrDigit(ch) ||
              isPunctuation(ch);
      if (containsText) break; // bad character found
    }
    return !containsText;
  }

  private static boolean isPunctuation(char ch) {
    switch (Character.getType(ch)) {
      case Character.CONNECTOR_PUNCTUATION: return true;
      case Character.CURRENCY_SYMBOL: return true;
      case Character.DASH_PUNCTUATION: return true;
      case Character.ENCLOSING_MARK: return true;
      case Character.END_PUNCTUATION: return true;
      case Character.MATH_SYMBOL: return true;
      case Character.OTHER_PUNCTUATION: return true;
      case Character.START_PUNCTUATION: return true;
    }
    return false;
  }

  private static boolean isSpecial(char ch) {
    // tried to get the Unicode block from the character and test against
    // Character.UnicodeBlock.SPECIALS, but it didn't work so I gave up on that.
    return ((ch == '\ufeff') || (ch == '\ufffe'));
  }

  private static String stripQuotes(String input) {
    if (SQUtil.isBlank(input)) return "";
    if (!input.contains("\"") && !input.contains("'")) return input.trim();
    StringBuilder sb = new StringBuilder();
    for (int index = 0; index < input.length(); index++) {
      char ch = input.charAt(index);
      if (!Character.isWhitespace(ch) && (ch != '\'') && (ch != '"')) {
        sb.append(ch);
      }
    }
    return sb.toString();
  }
}
