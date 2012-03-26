/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

/**
 * Supplies localized strings and other information.
 *
 * @author Kevin Menningen
 */
public interface ResourceProvider {
  /**
   * Given a lookup key, return a string resource from an appropriate resource bundle.
   * @param key The key to use for the lookup.
   * @return The corresponding string, a blank if no resource bundle is available, or
   * <code>null</code> if not found in the current bundle.
   */
  String getString(final String key);
}
