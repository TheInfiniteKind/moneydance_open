/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

/**
 * A stock connection that means the user doesn't want to use any connection at all, which disables
 * use of that particular download type.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class NoConnection(quotesModel: StockQuotesModel) : BaseConnection(PREFS_KEY, quotesModel, ALL_SUPPORT) {
  private var _displayName = "None" // the default used if one is not set by resources
  
  override  fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String? {
    return parsedSymbol?.symbol ?: "<none>" // not used
  }
  
  override fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange?): String? {
    return exchange?.currencyCode
  }
  
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: No exchange rate connection specified")
  }
  
  override fun updateSecurity(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: No stock price connection specified")
  }
  
  override fun setDefaultCurrency() {
    // do nothing, no model is defined
  }
  
  fun setDisplayName(displayName: String) {
    this._displayName = displayName
  }
  
  override fun toString(): String {
    return _displayName
  }
  
  companion object {
    private const val PREFS_KEY = "notUsed"
  }
}
