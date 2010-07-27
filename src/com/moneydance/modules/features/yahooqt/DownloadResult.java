/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

/**
* Stores the result of a download operation for further processing.
 * <p/>
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
*/
class DownloadResult {
  boolean skipped = false;
  String displayName;
  String historyResult;
  int historyErrorCount = 0;
  int historyRecordCount = 0;
  String currentResult;
  boolean currentError = false;
  String displayMessage;
  String logMessage;

  DownloadResult() { }
  
  DownloadResult(String message, int historyErrors) {
    displayMessage = message;
    historyErrorCount = historyErrors;
  }

  DownloadResult(String message, boolean currentPriceError, String currentPrice) {
    displayMessage = message;
    currentError = currentPriceError;
    currentResult = currentPrice;
  }
}
