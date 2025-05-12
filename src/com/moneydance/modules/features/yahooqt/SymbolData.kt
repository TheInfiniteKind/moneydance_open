/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

/**
 * Class containing all the possible parts of a security symbol with various overrides.
 * The user may provide overrides in the symbol using the following syntax:
 * <pre>
 * {GooglePrefix} : Symbol . {YahooSuffix} - {CurrencyCode}
 * </pre>
 * Where only `Symbol` is required, and no spaces are expected. *
 *
 *
 * This class is immutable.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class SymbolData
/**
 * Constructor to allow all fields to be final.
 * @param prfx Google exchange prefix.
 * @param sym  Security symbol.
 * @param sfx  Yahoo exchange suffix.
 * @param curr Currency ID string or code (USD, EUR, etc.).
 */(
  /** The Google exchange prefix. Does not include the colon. Can be blank or `null`. */
  val prefix: String,
  /** The base, unadorned security symbol. Cannot be blank.  */
  val symbol: String,
  /** The Yahoo exchange suffix, including the leading period. Can be blank or `null`.  */
  val suffix: String,
  /** An override currency code. Does not include the dash. Can be blank or `null`.  */
  val currencyCode: String)
