/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios.selector;

/**
 * Non-localizable (N12E) string statics.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
final class N12ESelector {
  public static final String ACCOUNTS_CHANGE = "acctSelectComboList";

  /**
   * Stores the size of the selector window for accounts to be required, allowed or disallowed.
   */
  static final String SIZE_KEY = "threeWayAcctSelector.size";
  /**
   * Stores the window location of the selector window for accounts to be required, allowed or disallowed.
   */
  static final String LOCATION_KEY = "threeWayAcctSelector.location";

  static final String EMPTY = "";
  static final String FILTER_CHANGE = "filterChange";

  static final String INDENT = "    ";
  static final String COLON = ":";

  /**
   * Static definitions only, do not instantiate.
   */
  private N12ESelector() {
  }
}