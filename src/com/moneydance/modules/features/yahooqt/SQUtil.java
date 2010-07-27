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
 * Stock Quote Utility methods. Most are copied from MD2010 StringUtils or UiUtil, but this plugin is being
 * is being kept compatible with MD2008 for the time being.
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
   * Static utilities only - do not instantiate.
   */
  private SQUtil() { }
}
