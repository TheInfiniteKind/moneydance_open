/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.CurrencyType;

/**
 * An exception encountered while downloading data.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class DownloadException extends Exception {
  private final CurrencyType _currency;

  DownloadException(final CurrencyType currency, final String reason) {
    super(reason);
    _currency = currency;
  }

  DownloadException(final CurrencyType currency, final String reason, final Throwable cause) {
    super(reason, cause);
    _currency = currency;
  }

  public CurrencyType getCurrency() {
    return _currency;
  }
}
