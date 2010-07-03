package com.moneydance.modules.features.yahooqt;

import java.beans.PropertyChangeEvent;

/**
 * <p>Non-localizable (N12E) string statics. Keeping all strings out of the Java code makes it
 * much easier to know that everything is localized. Additionally, it forces the developer to
 * decide when they write a string constant: 'Will this be displayed to the user, or will it not?
 * Can this string be localized, or would localizing it break the software?'</p>
 * <p/>
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 *
 * @author Kevin Menningen
 */
class N12EStockQuotes {
  /**
   * The name of the resource bundle file.
   */
  static final String RESOURCES = "com.moneydance.modules.features.yahooqt.StockQuotes";
  /**
   * Empty string.
   */
  static final String EMPTY = "";
  /**
   * Separate strings, as in a list of tags.
   */
  static final String COMMA_SEPARATOR = ", ";
  /**
   * Separate strings.
   */
  static final String SPACE = " ";
  /**
   * Indentation in a list.
   */
  static final String INDENT = "     ";
  static final String COLON = ":";

  /**
   * The title of the extension, if unavailable from resources.
   */
  static final String TITLE = "Stock Quote Synchronizer";

  /**
   * The character set to encode web URLs in. Per
   * <a href="http://www.ietf.org/rfc/rfc1738.txt">RFC 1738</a>, "URLs are written only with the
   * graphic printable characters of the US-ASCII coded character set." However, the Javadoc for
   * {@link java.net.URLEncoder} specifies that the W3C states that UTF-8 be used. Since UTF-8 is
   * one of the standard character sets that must be defined by every Java implementation, we simply
   * select it for encoding the URLs. See "Standard charsets" under
   * {@link java.nio.charset.Charset}.
   */
  static final String URL_ENC = "UTF-8";

  /**
   * Delimiter in settings strings for x/y or width/height settings.
   */
  static final String SETTINGS_PT_DELIMITER = "x";
  /**
   * Settings key in the Moneydance config.dict file for the last dialog location.
   */
  static final String SETTINGS_DLG_LOCATION_SETTING = "gui.findandreplace_location";
  /**
   * Settings key in the Moneydance config.dict file for the last dialog size.
   */
  static final String SETTINGS_DLG_SIZE_SETTING = "gui.findandreplace_size";

  /**
   * Event fired when a new file is opened.
   */
  static final String MD_OPEN_EVENT_ID = "md:file:opened";

  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Properties for Property Change Notifications
  //////////////////////////////////////////////////////////////////////////////////////////////
  static final String STATUS_UPDATE = "testStatus";
  static final String DOWNLOAD_BEGIN = "downloadTestBegin";
  static final String DOWNLOAD_END = "downloadTestEnd";
  static final String HEADER_UPDATE = "updateHeader";

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // HTML
  ///////////////////////////////////////////////////////////////////////////////////////////////


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // XML Resource Files
  ///////////////////////////////////////////////////////////////////////////////////////////////
  static final String FORMAT_XML_SUFFIX = "properties.xml";
  static final String FORMAT_XML = "java." + FORMAT_XML_SUFFIX;

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Logging and Errors
  ///////////////////////////////////////////////////////////////////////////////////////////////
  static final String XML_RESOURCE_LOAD_FAIL = "Unable to load an XML resource bundle: ";


  /**
   * Do not instantiate, static properties only
   */
  private N12EStockQuotes() {
  }
}
