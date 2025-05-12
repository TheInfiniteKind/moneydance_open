/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

/**
 * Supplies localized strings and other information. This could be replaced by MDResourceProvider
 * once MD 2008 is no longer supported.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
interface ResourceProvider {
  /**
   * Given a lookup key, return a string resource from an appropriate resource bundle.
   * @param key The key to use for the lookup.
   * @return The corresponding string, a blank if no resource bundle is available, or
   * `null` if not found in the current bundle.
   */
  fun getString(key: String): String
}
