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
 * Localizable string keys to look up in resources. Keeping all of these keys in one place
 * helps simplify tracking localized resources. It also helps when it comes time to audit for
 * unused strings.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
internal object L10NStockQuotes {
  const val TITLE: String = "title.text" // Yahoo!® Finance Synchronizer
  
  // main configuration dialog
  const val SETTINGS_TITLE: String = "settings.title"
  const val RATES_CONNECTION: String = "ratesConnection"
  const val SET_API_KEY: String = "setAPIKey"
  const val SECURITIES_CONNECTION: String = "securitiesConnection"
  const val FREQUENCY_LABEL: String = "frequency"
  const val NEXT_DATE_LABEL: String = "nextDate"
  const val SAVE_CURRENT_OPTION: String = "saveCurrHistory"
  const val TEST: String = "test"
  const val EXCHANGE_TITLE: String = "exchangeColumn.title"
  const val TEST_TITLE: String = "testColumn.title"
  const val ERROR_DEFAULT_NOT_EDITABLE: String = "errDefaultEdit"
  const val SHOW_OWNED: String = "showOwnedOnly"
  const val UPDATE_NOW: String = "updateNow"
  const val LAST_UPDATE_FMT: String = "lastUpdate.fmt"
  const val NEVER: String = "never"
  const val HIDE_TEST: String = "hideTest.tip"
  const val SHOW_TEST: String = "showTest.tip"
  const val EXCHANGE_EDIT_TIP_FMT: String = "editExchange.tip" // Right click or press {0} to edit
  
  // other strings
  /** Text that follows a label. Some locales prefer ' : ', others prefer ': '.   */
  const val LABEL_COLON: String = "labelColon"
  const val YAHOO_USA: String = "yahooUSA"
  const val YAHOO_UK: String = "yahooUK"
  const val YAHOO_RATES: String = "yahooRates"
  const val ALPHAVANTAGE: String = "alphavantage"
  const val GOOGLE: String = "google"
  const val TEST_NOTSTARTED: String = "downloading"
  const val TEST_EXCLUDED: String = "skipped"
  const val TEST_ERR_SETUP: String = "error.setup"
  const val NO_CONNECTION: String = "notUsed"
  const val QUOTES: String = "quotes"
  const val RATES: String = "exchangeRates"
  const val ERROR_NO_CONNECTION: String = "error.no_connection"
  const val NO_UPDATE: String = "no_update"
  const val ERROR_NO_SYMBOL: String = "error.no_symbol"
  const val HISTORY: String = "history"
  const val QUOTE: String = "quote"
  const val BASIC: String = "basic"
  const val ADVANCED: String = "advanced"
  const val CURRENCY_UNDEFINED: String = "error.curr_undefined" // Price currency not defined
  const val CURRENCY_NOT_FOUND_FMT: String = "curr_not_found.fmt" // Price currency {0} not found
  const val PRICE_CURRENCY_FMT: String = "price_currency.fmt" // Prices in {0}
  const val CURRENCY_MISMATCH_FMT: String = "error.curr_mismatch.fmt" // Currency {0} does not match exchange currency {1}</entry>
  const val CURRENCY_CODE_MISMATCH_FMT: String = "error.curr_code_mismatch.fmt" // Currency code {0} does not match {1}</entry>
  
  // Import errors
  /** {0} = the currency ID that is supposed to be used for price updates, but doesn't exist.  */
  const val ERROR_PRICE_CURRENCY_FMT: String = "error.price_currency.fmt" // Price currency ID not found: {0}
  const val ERROR_HISTORY_NOT_SUPPORTED: String = "error.history.not_supported" // History is not supported by this connection
  const val ERROR_CURRENT_NOT_SUPPORTED: String = "error.current.not_supported" // Current price is not supported by this connection
  const val IMPORT_ERROR_NO_INPUT_STREAM: String = "error.import.no_input" // Could not open input data.
  const val IMPORT_ERROR_READ_INPUT: String = "error.import.read_input" // Could not read input data.
  const val IMPORT_ERROR_NO_DATA: String = "error.import.no_data" // No data found.
  const val IMPORT_ERROR_READING_DATA: String = "error.import.while.read" // Error while reading data.
  const val IMPORT_ERROR_NO_VALID_DATA: String = "error.import.no_valid_data" // No valid data found.
  const val IMPORT_ERROR_NOT_TEXT_DATA: String = "error.import.not_text" // Input data was not text.
  const val IMPORT_ERROR_NO_COLUMNS: String = "error.import.no_columns" // Input data was not separated into columns.
  const val IMPORT_ERROR_MALFORMED_TEXT: String = "error.import.malformed" // Input data was malformed.
  const val IMPORT_ERROR_NO_HEADER: String = "error.import.no_header" // No header found.
  const val IMPORT_ERROR_OTHER: String = "error.import.other" // Unexpected error during import.
  const val IMPORT_ERROR_COMM: String = "error.import.communication" // Communication
  const val IMPORT_ERROR_NUMBER: String = "error.import.invalid_number" // Invalid Number
  
  /** {0} = the error received, {1} = response message text.  */
  const val IMPORT_ERROR_URL_FMT: String = "error.url.fmt"
  
  /** {0} = the code received, {1} = response message text.  */
  const val IMPORT_ERROR_URL_CODE_FMT: String = "error.url_code.fmt"
  const val INVALID_SYMBOL: String = "error.invalid_symbol" // Invalid Symbol
  const val MODIFIED: String = "modified" // Modified
  
  // status messages
  const val EXCHANGE_RATES_BEGIN: String = "status.exchangeRates.start.fmt"
  
  /** {0} = item being downloaded, {1} = text of error.  */
  const val ERROR_DOWNLOADING_FMT: String = "error.download.fmt"
  
  /** {0} = item completed downloading  */
  const val FINISHED_DOWNLOADING_FMT: String = "finished.download.fmt"
  
  /** {0} = number skipped, {1} = number of errors, {2} = number of successful quotes.  */
  const val QUOTES_DONE_FMT: String = "quotes.done.fmt"
  
  /** {0} = name of security, {1} = date, {2} = price  */
  const val SECURITY_PRICE_DISPLAY_FMT: String = "priceAsOfDate.fmt"
  
  /** {0} = from currency, {1} = to currency, {2} = date: {3} = rate  */
  const val EXCHANGE_RATE_DISPLAY_FMT: String = "exchangeRateAsOfDate.fmt"
  
  /** {0} = from currency, {1} = to currency  */
  const val ERROR_EXCHANGE_RATE_FMT: String = "error.exchangeRate.fmt"
  
  /** {0} = name of security, {1} error text  */
  const val ERROR_HISTORY_FMT: String = "error.history.fmt"
  
  /** {0} = name of security, {1} error text  */
  const val ERROR_CURRENT_FMT: String = "error.current.fmt"
  
  /**  {0} = number of successful records, {1} error count  */
  const val TEST_SOME_SUCCESS_FMT: String = "test.some_success.fmt"
  
  /**  {0} = number of successful records  */
  const val TEST_SUCCESS_FMT: String = "test.success.fmt"
  
  /**  {0} = number of errors  */
  const val TEST_ERROR_FMT: String = "test.error.fmt"
  const val TEST_NO_DATA: String = "test.no_records"
  
  /** {0} = date, {1} = price   */
  const val TEST_PRICE_SUCCESS_FMT: String = "test.current.fmt"
  
  // exchange edit dialog
  const val EDIT_EXCHANGE_TITLE: String = "editExchangeTitle"
  const val EXCHANGE_LABEL: String = "exchangeName"
  const val YAHOO_SUFFIX_LABEL: String = "yahooSuffix"
  const val GOOGLE_PREFIX_LABEL: String = "googlePrefix"
  const val CURRENCY_LABEL: String = "currency"
  const val MULTIPLIER_LABEL: String = "multiplier"
  const val ERROR_NAME_BLANK: String = "errNameBlank"
  const val ERROR_MULTIPLIER: String = "errMultiplier"
  const val ERROR_SAVE: String = "errSave"
}
