package com.moneydance.modules.features.yahooqt;

/**
* Created by IntelliJ IDEA.
* User: Kevin
* Date: Jun 25, 2010
* Time: 8:29:50 PM
* To change this template use File | Settings | File Templates.
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
