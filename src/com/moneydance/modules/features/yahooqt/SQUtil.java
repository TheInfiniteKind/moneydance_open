package com.moneydance.modules.features.yahooqt;

import javax.swing.SwingUtilities;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

/**
 * Stock Quote Utility methods. Most are copied from MD2010 StringUtils or UiUtil, but this plugin is being
 * is being kept compatible with MD2008 for the time being.
 * <p/>
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
final class SQUtil {
  /**
   * Horizontal gap between components/controls.
   */
  public static final int HGAP = 6;
  /**
   * Vertical gap between components/controls.
   */
  public static final int VGAP = 4;
  /**
   * Horizontal gap between content and dialog border.
   */
  public static final int DLG_HGAP = 10;
  /**
   * Vertical gap between content and dialog border.
   */
  public static final int DLG_VGAP = 8;
  /**
   * Text that follows a label. Some locales prefer ' : ', others prefer ': '.
   */
  public static final String LABEL_COLON = "labelColon";


  /**
   * Runs the specified code on the Event Dispatch thread (the UI thread).
   *
   * @param runnable Code to run on the UI thread.
   */
  public static void runOnUIThread(final Runnable runnable) {
    if (!SwingUtilities.isEventDispatchThread()) {
      SwingUtilities.invokeLater(runnable);
    } else {
      runnable.run();
    }
  }
  
  /**
   * Determine if two objects of the same type are equal or not.
   * @param object1 Left hand side object.
   * @param object2 Right hand side object.
   * @param <T> The type of object being compared.
   * @return True if the objects are equal, false otherwise.
   */
  public static <T> boolean isEqual(T object1, T object2) {
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
  public static boolean isEmpty(String candidate) {
    return candidate == null || candidate.length() == 0;
  }

  /**
   * Null safe check for a String with nothing but whitespace characters.
   *
   * @param candidate the String to evaluate.
   * @return true if the candidate is null or all whitespace.
   */
  public static boolean isBlank(String candidate) {
    boolean isBlank = isEmpty(candidate);

    if (!isBlank) {
      for (int index = candidate.length() - 1; index >= 0; index--) {
        isBlank = Character.isWhitespace(candidate.charAt(index));
        if (!isBlank) {
          break; // non-whitespace character found, don't bother checking the remainder
        }
      }
    }
    return isBlank;
  }

  /**
   * Get a label from resources, and if it does not have a colon, add it. Also adds a space at
   * the end for better spacing in the UI layout.
   *
   * @param resources Resource provider.
   * @param key       String key to look up in the resources
   * @return A string with a colon at the end.
   */
  public static String getLabelText(final ResourceProvider resources, final String key) {
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
  public static String addLabelSuffix(final ResourceProvider resources, final String label) {
    StringBuffer result = new StringBuffer(label);
    if ((result.length() > 0) && (result.charAt(result.length() - 1)) != ':') {
      result.append(resources.getString(LABEL_COLON));
    }
    result.append(' ');
    return result.toString();
  }

  public static String urlEncode(final String toEncode) {
    String result;
    try {
      result = URLEncoder.encode(toEncode, N12EStockQuotes.URL_ENC);
    } catch (UnsupportedEncodingException e) {
      result = toEncode;
    }
    return result;
  }

  /**
   * Static utilities only - do not instantiate.
   */
  private SQUtil() {}
}
