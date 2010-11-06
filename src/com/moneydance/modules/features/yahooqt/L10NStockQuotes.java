/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

/**
 * <p>Localizable string keys to look up in resources. Keeping all of these keys in one place
 * helps simplify tracking localized resources. It also helps when it comes time to audit for
 * unused strings.</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class L10NStockQuotes
{
  static final String TITLE = "title.text"; // Yahoo!® Finance Synchronizer

  // main configuration dialog
  static final String SETTINGS_TITLE = "settings.title";
  static final String RATES_CONNECTION = "ratesConnection";
  static final String HISTORY_CONNECTION = "historyConnection";
  static final String CURRENT_CONNECTION = "currentConnection";
  static final String FREQUENCY_LABEL = "frequency";
  static final String NEXT_DATE_LABEL = "nextDate";
  static final String SAVE_CURRENT_OPTION = "saveCurrHistory";
  static final String TEST = "test";
  static final String EXCHANGE_TITLE = "exchangeColumn.title";
  static final String TEST_TITLE = "testColumn.title";
  static final String ERROR_DEFAULT_NOT_EDITABLE = "errDefaultEdit";
  static final String SHOW_OWNED = "showOwnedOnly";
  static final String UPDATE_NOW = "updateNow";
  static final String LAST_UPDATE_FMT = "lastUpdate.fmt";
  static final String NEVER = "never";
  static final String HIDE_TEST = "hideTest.tip";
  static final String SHOW_TEST = "showTest.tip";
  static final String EXCHANGE_EDIT_TIP_FMT = "editExchange.tip"; // Right click or press {0} to edit

  // other strings
  /** Text that follows a label. Some locales prefer ' : ', others prefer ': '.  */
  static final String LABEL_COLON = "labelColon";
  static final String YAHOO_USA = "yahooUSA";
  static final String YAHOO_UK = "yahooUK";
  static final String YAHOO_RATES = "yahooUSAexchangeRates";
  static final String GOOGLE = "google";
  static final String TEST_NOTSTARTED = "downloading";
  static final String TEST_EXCLUDED = "skipped";
  static final String TEST_ERR_SETUP = "error.setup";
  static final String NO_CONNECTION = "notUsed";
  static final String QUOTES = "quotes";
  static final String RATES = "exchangeRates";
  static final String ERROR_NO_CONNECTION = "error.no_connection";
  static final String NO_UPDATE = "no_update";
  static final String ERROR_NO_SYMBOL = "error.no_symbol";
  static final String HISTORY = "history";
  static final String QUOTE = "quote";
  static final String BASIC = "basic";
  static final String ADVANCED = "advanced";
  static final String CURRENCY_UNDEFINED = "error.curr_undefined"; // Price currency not defined
  static final String CURRENCY_NOT_FOUND_FMT = "curr_not_found.fmt"; // Price currency {0} not found
  static final String PRICE_CURRENCY_FMT = "price_currency.fmt"; // Prices in {0}
  static final String CURRENCY_MISMATCH_FMT = "error.curr_mismatch.fmt"; // Currency {0} does not match exchange currency {1}</entry>
  static final String CURRENCY_CODE_MISMATCH_FMT = "error.curr_code_mismatch.fmt"; // Currency code {0} does not match {1}</entry>

  // Import errors
  /** {0} = the currency ID that is supposed to be used for price updates, but doesn't exist. */
  static final String ERROR_PRICE_CURRENCY_FMT = "error.price_currency.fmt"; // Price currency ID not found: {0}
  static final String ERROR_HISTORY_NOT_SUPPORTED = "error.history.not_supported"; // History is not supported by this connection
  static final String ERROR_CURRENT_NOT_SUPPORTED = "error.current.not_supported"; // Current price is not supported by this connection
  static final String IMPORT_ERROR_NO_INPUT_STREAM = "error.import.no_input"; // Could not open input data.
  static final String IMPORT_ERROR_READ_INPUT = "error.import.read_input"; // Could not read input data.
  static final String IMPORT_ERROR_NO_DATA = "error.import.no_data"; // No data found.
  static final String IMPORT_ERROR_READING_DATA = "error.import.while.read";// Error while reading data.
  static final String IMPORT_ERROR_NO_VALID_DATA = "error.import.no_valid_data"; // No valid data found.
  static final String IMPORT_ERROR_NOT_TEXT_DATA = "error.import.not_text"; // Input data was not text.
  static final String IMPORT_ERROR_NO_COLUMNS = "error.import.no_columns"; // Input data was not separated into columns.
  static final String IMPORT_ERROR_MALFORMED_TEXT = "error.import.malformed"; // Input data was malformed.
  static final String IMPORT_ERROR_NO_HEADER = "error.import.no_header"; // No header found.
  static final String IMPORT_ERROR_OTHER = "error.import.other"; // Unexpected error during import.
  static final String IMPORT_ERROR_COMM = "error.import.communication"; // Communication
  static final String IMPORT_ERROR_NUMBER = "error.import.invalid_number"; // Invalid Number
  /** {0} = the error received, {1} = response message text. */
  static final String IMPORT_ERROR_URL_FMT = "error.url.fmt";
  /** {0} = the code received, {1} = response message text. */
  static final String IMPORT_ERROR_URL_CODE_FMT = "error.url_code.fmt";
  static final String INVALID_SYMBOL = "error.invalid_symbol"; // Invalid Symbol
  static final String MODIFIED = "modified"; // Modified

  // status messages
  static final String EXCHANGE_RATES_BEGIN = "status.exchangeRates.start.fmt";
  /** {0} = item being downloaded, {1} = text of error. */
  static final String ERROR_DOWNLOADING_FMT = "error.download.fmt";
  /** {0} = item completed downloading */
  static final String FINISHED_DOWNLOADING_FMT = "finished.download.fmt";
  /** {0} = number skipped, {1} = number of errors, {2} = number of successful quotes. */
  static final String QUOTES_DONE_FMT = "quotes.done.fmt";
  /** {0} = name of security, {1} = date, {2} = price */
  static final String SECURITY_PRICE_DISPLAY_FMT = "priceAsOfDate.fmt";
  /** {0} = from currency, {1} = to currency, {2} = date: {3} = rate */
  static final String EXCHANGE_RATE_DISPLAY_FMT = "exchangeRateAsOfDate.fmt";
  /** {0} = from currency, {1} = to currency */
  static final String ERROR_EXCHANGE_RATE_FMT = "error.exchangeRate.fmt";
  /** {0} = name of security, {1} error text */
  static final String ERROR_HISTORY_FMT = "error.history.fmt";
  /** {0} = name of security, {1} error text */
  static final String ERROR_CURRENT_FMT = "error.current.fmt";
  /**  {0} = number of successful records, {1} error count */
  static final String TEST_SOME_SUCCESS_FMT = "test.some_success.fmt";
  /**  {0} = number of successful records */
  static final String TEST_SUCCESS_FMT = "test.success.fmt";
  /**  {0} = number of errors */
  static final String TEST_ERROR_FMT = "test.error.fmt";
  static final String TEST_NO_DATA = "test.no_records";
  /** {0} = date, {1} = price  */
  static final String TEST_PRICE_SUCCESS_FMT = "test.current.fmt";

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
}
