/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.time.TimeInterval;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

/**
 * Stock Quote Utility methods. Most are copied from MD2010r2+ StringUtils or UiUtil, but this
 * plugin is being is being kept compatible with MD2010r1 for the time being.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
final class SQUtil {

  /**
   * Get a label from (plugin) resources, and if it does not have a colon, add it. Also adds a
   * space at the end for better spacing in the UI layout.
   *
   * @param resources Resource provider.
   * @param key       String key to look up in the resources
   * @return A string with a colon at the end.
   */
  static String getLabelText(final ResourceProvider resources, final String key) {
    return addLabelSuffix(resources, resources.getString(key));
  }

  /**
   * Add a colon prompt after a text label if it does not have a colon. Also adds a space at
   * the end for better spacing in the UI layout.
   *
   * @param resources Resource provider.
   * @param label     String to add the colon to.
   * @return A string with a colon at the end.
   */
  static String addLabelSuffix(final ResourceProvider resources, final String label) {
    StringBuffer result = new StringBuffer(label);
    if ((result.length() > 0) && (result.charAt(result.length() - 1)) != ':') {
      result.append(resources.getString(L10NStockQuotes.LABEL_COLON));
    }
    result.append(' ');
    return result.toString();
  }

  static String urlEncode(final String toEncode) {
    String result;
    try {
      result = URLEncoder.encode(toEncode, N12EStockQuotes.URL_ENC);
    } catch (UnsupportedEncodingException e) {
      result = toEncode;
    }
    return result;
  }

  static int getNextDate(int date, TimeInterval interval) {
    switch (interval) {
      case WEEK: return Util.incrementDate(date, 0, 0, 7);
      case MONTH: return Util.incrementDate(date, 0, 1, 0);
      case QUARTER: return Util.incrementDate(date, 0, 3, 0);
      case YEAR: return Util.incrementDate(date, 1, 0, 0);
    }
    return Util.incrementDate(date);  // the default is daily
  }

  static int getPreviousDate(int date, TimeInterval interval) {
    switch (interval) {
      case WEEK: return Util.incrementDate(date, 0, 0, -7);
      case MONTH: return Util.incrementDate(date, 0, -1, 0);
      case QUARTER: return Util.incrementDate(date, 0, -3, 0);
      case YEAR: return Util.incrementDate(date, -1, 0, 0);
    }
    return Util.incrementDate(date, 0, 0, -1);  // the default is daily
  }

  static void pauseTwoSeconds() {
    try{
      Thread.sleep(2000);
    } catch (InterruptedException ignore) {
      // do nothing
    }
  }

  /**
   * Wait for the specified time period, keeping this thread quiet in the meantime.
   * @param timeInNs The length of time, in nanoseconds, to wait.
   */
  static void delaySpecifiedTime(final long timeInNs) {
    final long targetTime = System.nanoTime() + timeInNs;
    while (System.nanoTime() < targetTime) {
      try {
        // should sleep 20 times or less based upon a 5 second delay
        Thread.sleep(250L);
      } catch (InterruptedException ignore) {
        // do nothing
      }
    }
  }

  /**
   * Replace one or more tokens inside another string with a value.
   * @param str          The string containing the token(s).
   * @param toReplace    The token, case sensitive, to be replaced.
   * @param replaceWith  The string to replace the token with. Can be <code>null</code>.
   * @return The <code>str</code> string with the token replaced with a new value.
   */
  static String replaceAll(String str, String toReplace, String replaceWith) {
    int ii;
    int lastI = 0;
    StringBuilder sb = new StringBuilder(str.length());
    while((ii=str.indexOf(toReplace, lastI))>=0) {
      sb.append(str.substring(lastI, ii)); // add the text before the matched substring
      if (!isEmpty(replaceWith)) sb.append(replaceWith);
      lastI = ii + toReplace.length();
    }
    sb.append(str.substring(lastI)); // add the rest
    return sb.toString();
  }

  /**
   * Determine if two objects of the same type are equal or not.
   * @param object1 Left hand side object.
   * @param object2 Right hand side object.
   * @param <T> The type of object being compared.
   * @return True if the objects are equal, false otherwise.
   */
  static <T> boolean areEqual(final T object1, final T object2) {
    if (object1 == object2) return true;                      // either same instance or both null
    if ((object1 == null) || (object2 == null)) return false; // one is null, the other isn't
    return object1.equals(object2);
  }

  /**
   * Null safe check for "" (empty string).
   *
   * @param candidate the String to evaluate.
   * @return true if candidate is null or "" (empty string)
   */
  static boolean isEmpty(String candidate) {
    return candidate == null || candidate.length() == 0;
  }

  /**
   * Null safe check for a String with nothing but whitespace characters.
   *
   * @param candidate the String to evaluate.
   * @return true if the candidate is null or all whitespace.
   */
  static boolean isBlank(String candidate) {
    boolean isBlank = isEmpty(candidate);
    if (!isBlank) {
      for (int index = candidate.length()-1; index >= 0; index--) {
        isBlank = Character.isWhitespace(candidate.charAt(index));
        if (!isBlank) {
          break; // non-whitespace character found, don't bother checking the remainder
        }
      }
    }
    return isBlank;
  }

  /**
   * Parse out user-defined symbol information. The user may provide overrides in the symbol using
   * the following syntax:
   * <pre>
   *     {GooglePrefix} : Symbol . {YahooSuffix} - {CurrencyCode}
   * </pre>
   * Where only <code>Symbol</code> is required, and no spaces are expected.
   * @param securityCurrency The security definition to obtain information for.
   * @return The parsed symbol data along with overrides. Note that the {YahooSuffix} will contain
   * the leading period, whereas the GooglePrefix will not contain a trailing colon. This is to
   * maintain compatibility with how the stock exchanges are defined.
   */
  static SymbolData parseTickerSymbol(CurrencyType securityCurrency) {
    if (securityCurrency == null) return null;
    final String rawTickerSymbol = securityCurrency.getTickerSymbol();
    if (isBlank(rawTickerSymbol)) return null;
    return parseTickerSymbol(rawTickerSymbol);
  }

  /**
   * Parse out user-defined symbol information. The user may provide overrides in the symbol using
   * the following syntax:
   * <pre>
   *     {GooglePrefix} : Symbol . {YahooSuffix} - {CurrencyCode}
   * </pre>
   * Where only <code>Symbol</code> is required, and no spaces are expected.
   * @param rawTickerSymbol The raw ticker symbol with all user edits of prefix, suffix or currency
   * @return The parsed symbol data along with overrides. Note that the {YahooSuffix} will contain
   * the leading period, whereas the GooglePrefix will not contain a trailing colon. This is to
   * maintain compatibility with how the stock exchanges are defined.
   */
  static SymbolData parseTickerSymbol(String rawTickerSymbol) {
    String tickerSymbol = rawTickerSymbol.trim();
    String prefix = null;
    String suffix = null;
    String currencyCode = null;

    // break off a currency code if and only if the last 4 characters is -XXX where X is a letter,
    // OR if the user put in a carat delimiter
    final int len = tickerSymbol.length();
    int caratIndex = tickerSymbol.lastIndexOf('^');
    final boolean hasDashOverride = ((len > 4) && (tickerSymbol.charAt(len - 4) == '-'));
    if ((len > 4) && (hasDashOverride || (caratIndex >= 0)))
    {
      boolean currencyFound = true;
      if (caratIndex >= 0) {
        // include the period as the first character
        currencyCode = tickerSymbol.substring(caratIndex + 1).trim();
        if (isBlank(currencyCode)) suffix = null;   // ignore empty
        tickerSymbol = tickerSymbol.substring(0, caratIndex).trim();
      } else {
        // old-style dash currency override, being deprecated because dashes are allowed in symbols
        for (int ii = len - 3; ii < len; ii++) {
          if (!Character.isLetter(tickerSymbol.charAt(ii))) {
            currencyFound = false;
            break;
          }
        }
        if (currencyFound) {
          currencyCode = tickerSymbol.substring(len - 3).trim();
          tickerSymbol = tickerSymbol.substring(0, len - 4).trim();
        }
      }
    }

    // check if a Google exchange prefix exists
    int colonIndex = tickerSymbol.indexOf(':');
    if (colonIndex >= 0) {
      prefix = tickerSymbol.substring(0, colonIndex).trim();
      tickerSymbol = tickerSymbol.substring(colonIndex + 1).trim();
    }
    int dotIndex = tickerSymbol.indexOf('.');
    if (dotIndex >= 0) {
      // include the period as the first character
      suffix = tickerSymbol.substring(dotIndex).trim();
      if (".".equals(suffix)) suffix = null;   // ignore empty
      tickerSymbol = tickerSymbol.substring(0, dotIndex).trim();
    }
    if (isBlank(tickerSymbol)) {
      // this part is required, so if it doesn't exist, bail
      return null;
    }
    return new SymbolData(prefix, tickerSymbol, suffix, currencyCode);
  }

  /**
   * Static utilities only - do not instantiate.
   */
  private SQUtil() { }

  /**
   * Unit test the methods.
   * @param argv Test arguments (not used).
   */
  public static void main(String argv[]) {
    // test the parsing of symbols. Using symbol GIL.F or GILG.DE for Gildemeister
    CurrencyType security = new CurrencyType(5000, "GIL", "Gildemeister", 1.0, 2, "", "GIL", "",
            19990101, CurrencyType.CURRTYPE_SECURITY, null);
    security.setTickerSymbol("  \t   \n ");
    SymbolData data = parseTickerSymbol(security);
    System.err.println("Blank test: " + ((data != null) ? "FAIL" : "pass"));
    // straightforward tests
    String symbol = "GIL";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA:GIL";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "GIL.F";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "GIL.F-EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA:GIL.F-EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA:GIL-EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    // mangled cases
    symbol = ":  GIL . ";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA\t:  GIL .F    -EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "\t: \n GIL .-EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA:   .F-EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Blank test: " + ((data != null) ? "FAIL" : "pass"));
    // now ensure we support the dash before the dot for oddball symbols like COS-UN.TO
    symbol = "COS-UN.TO";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "COS-UN -CAD  ";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    // verify support for the new replacement delimiter for currency override '^'
    symbol = "GIL.F^EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA:GIL.F^EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA:GIL^EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    // mangled cases
    symbol = "GIL.F^";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA\t:  GIL .F    ^EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "\t: \n GIL .^EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );
    symbol = "FRA:   .F^EUR";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Blank test: " + ((data != null) ? "FAIL" : "pass"));
    symbol = "COS-UN ^CAD  ";
    security.setTickerSymbol(symbol);
    data = parseTickerSymbol(security);
    System.err.println("Symbol '" + symbol + "' ="
            + "  prefix: " + ((data.prefix == null) ? "(null)" : "'"+data.prefix+"'")
            + "  suffix: " + ((data.suffix == null) ? "(null)" : "'"+data.suffix+"'")
            + "  symbol: " + ((data.symbol == null) ? "(null)" : "'"+data.symbol+"'")
            + "  currency: " + ((data.currencyCode == null) ? "(null)" : "'"+data.currencyCode+"'")
    );

  }

}
