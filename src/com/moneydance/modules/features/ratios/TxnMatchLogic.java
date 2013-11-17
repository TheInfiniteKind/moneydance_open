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

import com.moneydance.util.StringUtils;

/**
 * Defines whether we look for transactions into an account, transactions out of an account, or the sum total
 * of transactions - the change in balance of the account.
 *
 * @author Kevin Menningen
 */
public enum TxnMatchLogic {
  /**
   * Transactions into an account, which increases net worth of the account holder if it is an asset
   * account or decreases net worth if a liability.
   */
  IN('i'),
  /**
   * Transactions out of an account, which decreases net worth of the account holder if it is an asset
   * account or increases net worth if a liability.
   */
  OUT('o'),
  /**
   * Measure both transactions into and out of an account, in effect just measure the balance difference
   * over the specified time period, except you can filter by tag or use tax date.
   */
  BOTH('b'),
  /**
   * Not a transaction match, instead just compute the ending balance for the specified time period. No filtering
   * by tag or using tax date.
   */
  END_BALANCE('e'),
  /**
   * Not a transaction match, instead compute the average daily balance for the specified time period. No tag
   * filtering or using tax date.
   */
  AVERAGE_BALANCE('a');

  public static final TxnMatchLogic DEFAULT = IN;

  private final char _configKey;

  private TxnMatchLogic(final char configKey) {
    _configKey = configKey;
  }

  public String getConfigKey() {
    return String.valueOf(_configKey);
  }

  public static TxnMatchLogic fromString(final String config) {
    if (StringUtils.isBlank(config)) return DEFAULT;
    char key = Character.toLowerCase(config.charAt(0));
    if (key == 'i') return IN;
    if (key == 'b') return BOTH;
    if (key == 'e') return END_BALANCE;
    if (key == 'o') return OUT;
    if (key == 'a') return AVERAGE_BALANCE;
    return DEFAULT;
  }

}
