package com.moneydance.modules.features.yahooqt;

/**
 * <p>Localizable string keys to look up in resources. Keeping all of these keys in one place
 * helps simplify tracking localized resources. It also helps when it comes time to audit for
 * unused strings.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.4
 * @since 1.0
 */
class L10NStockQuotes
{
    public static final String LABEL_COLON = "labelColon";
    public static final String TITLE = "title.text"; // Find and Replace
    public static final String VERSION_FMT = "version.format"; //Version V (Build B)

    // Stuff copied from the Moneydance resources
    public static final String OK = "ok";
    public static final String CANCEL = "cancel";

  static final String YAHOO_USA = "yahooUSA";
  static final String YAHOO_UK = "yahooUK";
  static final String GOOGLE = "google";
  static final String CONNECTION = "connection";
  static final String TEST = "test";
  static final String TEST_NOTSTARTED = "downloading";
  static final String TEST_EXCLUDED = "skipped";
  static final String TEST_ERR_SETUP = "error.setup";
  static final String CURRENCY_MISMATCH_FMT = "warn.currencyMismatch";

  // exchange edit dialog
  static final String EDIT_EXCHANGE_TITLE = "editExchangeTitle";
  static final String EXCHANGE_LABEL = "exchangeName";
  static final String YAHOO_SUFFIX_LABEL = "yahooSuffix";
  static final String GOOGLE_PREFIX_LABEL = "googlePrefix";
  static final String CURRENCY_LABEL = "currency";
  static final String MULTIPLIER_LABEL = "multiplier";
  static final String ERROR_NAME_BLANK = "errNameBlank";
  static final String ERROR_MULTIPLIER = "errMultiplier";
  static final String ERROR_SAVE = "errSave";
  static final String ERROR_DEFAULT_NOT_EDITABLE = "errDefaultEdit";
}
