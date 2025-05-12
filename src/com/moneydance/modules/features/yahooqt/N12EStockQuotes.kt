/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt


/**
 *
 * Non-localizable (N12E) string statics. Keeping all strings out of the Java code makes it
 * much easier to know that everything is localized. Additionally, it forces the developer to
 * decide when they write a string constant: 'Will this be displayed to the user, or will it not?
 * Can this string be localized, or would localizing it break the software?'
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
internal object N12EStockQuotes {
  /**
   * Empty string.
   */
  const val EMPTY: String = ""
  
  /**
   * Separate strings, as in a list of tags.
   */
  const val COMMA_SEPARATOR: String = ", "
  
  /**
   * Separate strings.
   */
  const val SPACE: String = " "
  const val ERROR: String = "(!)"
  
  /**
   * The title of the extension, if unavailable from resources.
   */
  const val TITLE: String = "Quotes and Exchange Rates"
  
  /**/////////////////////////////////////////////////////////////////////////////////////////// */ //  Settings Keys
  /**/////////////////////////////////////////////////////////////////////////////////////////// */ /** Stores the size of the main configuration dialog.  */
  const val SIZE_KEY: String = "yahooqt.size"
  
  /** Stores the window location of the main configuration dialog.  */
  const val LOCATION_KEY: String = "yahooqt.location"
  
  /** Event fired when a new file is opened.    */
  const val MD_OPEN_EVENT_ID: String = "md:file:opened"
  
  /** Event fired when a file is being closed.    */
  const val MD_CLOSING_EVENT_ID: String = "md:file:closing"
  
  /** Event fired when the application is exiting completely.    */
  const val MD_EXITING_EVENT_ID: String = "md:app:exiting"
  
  /**/////////////////////////////////////////////////////////////////////////////////////////// */ //  Properties for Property Change Notifications
  /**/////////////////////////////////////////////////////////////////////////////////////////// */
  const val STATUS_UPDATE: String = "testStatus"
  const val DOWNLOAD_BEGIN: String = "downloadTestBegin"
  const val DOWNLOAD_END: String = "downloadTestEnd"
  const val HEADER_UPDATE: String = "updateHeader"
  
  /**//////////////////////////////////////////////////////////////////////////////////////////// */ // HTML
  /**//////////////////////////////////////////////////////////////////////////////////////////// */
  const val HTML_BEGIN: String = "<html>"
  const val HTML_END: String = "</html>"
  const val PARA_BEGIN: String = "<p>"
  const val BREAK: String = "<br/>"
  const val RED_FONT_BEGIN: String = "<font color=\"red\">"
  const val GREEN_FONT_BEGIN: String = "<font color=\"green\">"
  const val FONT_END: String = "</font>"
  
  /**//////////////////////////////////////////////////////////////////////////////////////////// */ // XML Resource Files
  /**//////////////////////////////////////////////////////////////////////////////////////////// */ /** The name of the English (default) resource bundle file.   */
  const val ENGLISH_PROPERTIES_FILE: String = "/com/moneydance/modules/features/yahooqt/StockQuotes.properties.xml"
  
  /**
   * The template for a non-English resource bundle file.
   * 0 = language and country code
   */
  const val PROPERTIES_FILE_FMT: String = "/com/moneydance/modules/features/yahooqt/StockQuotes_{0}.properties.xml"
  
  /**//////////////////////////////////////////////////////////////////////////////////////////// */ // Logging and Errors
  /**//////////////////////////////////////////////////////////////////////////////////////////// */
  const val XML_RESOURCE_LOAD_FAIL: String = "Unable to load an XML resource bundle: "
}
