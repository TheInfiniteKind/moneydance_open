/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;


import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;

/**
 * <p>Non-localizable (N12E) string statics. Keeping all strings out of the Java code makes it
 * much easier to know that everything is localized. Additionally, it forces the developer to
 * decide when they write a string constant: 'Will this be displayed to the user, or will it not?
 * Can this string be localized, or would localizing it break the software?'</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class N12EStockQuotes {
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
  static final String ERROR = "(!)";

  /**
   * The title of the extension, if unavailable from resources.
   */
  static final String TITLE = "Stock Quote Synchronizer";

  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Settings Keys
  //////////////////////////////////////////////////////////////////////////////////////////////

  /** Stores the size of the main configuration dialog. */
  static final String SIZE_KEY = "yahooqt.size";
  /** Stores the window location of the main configuration dialog. */
  static final String LOCATION_KEY = "yahooqt.location";

  /** Event fired when a new file is opened.   */
  static final String MD_OPEN_EVENT_ID = "md:file:opened";
  /** Event fired when a file is being closed.   */
  static final String MD_CLOSING_EVENT_ID = "md:file:closing";
  /** Event fired when the application is exiting completely.   */
  static final String MD_EXITING_EVENT_ID = "md:app:exiting";

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
  static final String HTML_BEGIN = "<html>";
  static final String HTML_END = "</html>";
  static final String PARA_BEGIN = "<p>";
  static final String BREAK = "<br/>";
  static final String RED_FONT_BEGIN = "<font color=\"red\">";
  static final String GREEN_FONT_BEGIN = "<font color=\"green\">";
  static final String FONT_END = "</font>";

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // XML Resource Files
  ///////////////////////////////////////////////////////////////////////////////////////////////
  /** The name of the English (default) resource bundle file.  */
  static final String ENGLISH_PROPERTIES_FILE =
          "/com/moneydance/modules/features/yahooqt/StockQuotes.properties.xml";
  /**
   * The template for a non-English resource bundle file.
   * 0 = language and country code
   */
  static final String PROPERTIES_FILE_FMT =
          "/com/moneydance/modules/features/yahooqt/StockQuotes_{0}.properties.xml";

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
