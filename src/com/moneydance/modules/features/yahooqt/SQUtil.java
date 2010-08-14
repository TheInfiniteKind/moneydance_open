/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.Util;
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
   * Static utilities only - do not instantiate.
   */
  private SQUtil() { }
}
