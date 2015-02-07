/*
 * ************************************************************************
 * Copyright (C) 2012-2015 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;


import com.moneydance.apps.md.controller.Common;

/**
 * <p>Non-localizable (N12E) string statics. Keeping all strings out of the Java code makes it
 * much easier to know that everything is localized. Additionally, it forces the developer to
 * decide when they write a string constant: 'Will this be displayed to the user, or will it not?
 * Can this string be localized, or would localizing it break the software?'</p>
 *
 * @author Kevin Menningen
 */
class N12ERatios {
  /**
   * Empty string.
   */
  static final String EMPTY = "";
  /**
   * Separate strings.
   */
  static final String BAR = "|";
  static final String BAR_REGEX = "\\|";
  static final String COMMA_REGEX = "\\s*,\\s*";
  /**
   * Standard new line character.
   */
  static final String NEWLINE = System.getProperty("line.separator", "\n");
  /**
   * A regular expression to search for end-of-line (with {@link String#split(String)}, including
   * the system separator (on Windows '\r\n') as well as the shorthand '\n' which developers
   * typically use in string definitions.
   */
  static final String LINEEND_REGEX = NEWLINE + "|\n";

  /**
   * The title of the extension, if unavailable from resources.
   */
  static final String TITLE = "Ratios";
  static final String DEFAULT_NAME = "Ratio";
  static final String NOT_SPECIFIED = "(empty)";
  static final String HOME_PAGE_ID = "mennesoft.ratios";
  private static final String MODULE_ID = "ratios";
  static final String INVOKE_URL_PREFIX = Common.FMODULE_URI_PREFIX + MODULE_ID + ":";

  static final String JTABLE_AUTO_EDIT = "JTable.autoStartsEdit";
  static final String DELETE_ACTION_KEY = "delete";
  static final String INSERT_ACTION_KEY = "insert";
  static final String SELECT_TAG_LIST = "selectTagFromList";

  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Settings Keys
  //////////////////////////////////////////////////////////////////////////////////////////////

  /** Stores the size of the main configuration dialog. */
  static final String SIZE_KEY = "ratioSettings.size";
  /** Stores the window location of the main configuration dialog. */
  static final String LOCATION_KEY = "ratioSettings.location";

  static final String SETTINGS_ID = "mennesoft.ratios";
  // settings for all ratios collectively
  static final String DECIMALS_KEY = "digits";
  static final String DATE_RANGE_PREF_KEY = "mennesoft.ratios.dateRange";
  static final String DATE_RANGE_KEY = "dateRange";
  static final String RATIO_ENTRIES_KEY = "ratioList";

  // settings for each individual ratio entry
  static final String NAME_KEY = "nm";
  static final String INDEX_KEY = "idx";
  static final String NOTES_KEY = "nt";
  static final String SHOW_PERCENT_KEY = "pct";
  static final String ALWAYS_POSITIVE_KEY = "ap";
  static final String USE_TAX_DATE_KEY = "utd";
  static final String NUMERATOR_TXN_MATCH_KEY = "n.txnm";
  static final String DENOMINATOR_TXN_MATCH_KEY = "d.txnm";
  static final String NUMERATOR_LABEL_KEY = "n.l";
  static final String DENOMINATOR_LABEL_KEY = "d.l";
  static final String NUMERATOR_REQUIRED_LIST_KEY = "n.req.accts";
  static final String DENOMINATOR_REQUIRED_LIST_KEY = "d.req.accts";
  static final String NUMERATOR_DISALLOWED_LIST_KEY = "n.dis.accts";
  static final String DENOMINATOR_DISALLOWED_LIST_KEY = "d.dis.accts";
  static final String NUMERATOR_TAGS_KEY = "n.tags";
  static final String DENOMINATOR_TAGS_KEY = "d.tags";

  // signal to request a custom date range from the user
  static final String CUSTOM_DATE_KEY = "customDate";

  // the name of the background thread for computing ratios
  static final String RATIO_THREAD_NAME = "Ratio Calculate";

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
  static final String RATIO_LIST_CHANGE = "ratioListChange";
  static final String RATIO_LIST_RESET = "factoryReset";
  static final String DATE_RANGE_OPTION = "dateRange";
  static final String RECALCULATE = "recalculate";
  static final String DECIMALS_CHANGE = "decimalPlaces";
  static final String SETTINGS_CHANGE = "settingsChange";

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // XML Resource Files
  ///////////////////////////////////////////////////////////////////////////////////////////////
  /** The name of the English (default) resource bundle file.  */
  static final String ENGLISH_PROPERTIES_FILE =
          "com/moneydance/modules/features/ratios/Ratios.properties.xml";
  /**
   * The template for a non-English resource bundle file.
   * 0 = language and country code
   */
  static final String PROPERTIES_FILE_FMT =
          "com/moneydance/modules/features/ratios/Ratios_{0}.properties.xml";

  static final String EXTENSION_ICON =
      "com/moneydance/modules/features/ratios/ratios.png";

  static final String COPY_ICON =
      "com/moneydance/modules/features/ratios/copy.png";

  static final String ARROW_UP_ICON =
      "com/moneydance/modules/features/ratios/arrowUp.png";

  static final String ARROW_DOWN_ICON =
      "com/moneydance/modules/features/ratios/arrowDown.png";

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Logging and Errors
  ///////////////////////////////////////////////////////////////////////////////////////////////
  static final String XML_RESOURCE_LOAD_FAIL = "Unable to load an XML resource bundle: ";
  static final String SHOW_DIALOG_COMMAND = "showDialog";
  public static final String ERROR_LOADING_SETTINGS =
          "Error loading settings for Ratios extension, setting defaults.";


  /**
   * Do not instantiate, static properties only
   */
  private N12ERatios() {
  }
}
