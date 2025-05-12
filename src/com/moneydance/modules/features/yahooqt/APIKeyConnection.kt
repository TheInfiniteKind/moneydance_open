package com.moneydance.modules.features.yahooqt

import com.infinitekind.util.StringUtils.fieldIndex

abstract class APIKeyConnection(connectionID: String, model: StockQuotesModel, capabilities: Int) : BaseConnection(connectionID, model, capabilities) {
  abstract fun getAPIKey(evenIfAlreadySet: Boolean): String?
  
  override fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String? {
    if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) return null
    // check if the exchange was already added on, which will override the selected exchange
    if (!SQUtil.isBlank(parsedSymbol.suffix)) {
      return parsedSymbol.symbol + parsedSymbol.suffix
    }
    // Check if the selected exchange has a Yahoo suffix or not. If it does, add it.
    val suffix = exchange?.symbolYahoo.orEmpty()
    return if(suffix.isBlank()) parsedSymbol.symbol else parsedSymbol.symbol + suffix
  }
  
  override fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange?): String? {
    if (SQUtil.isBlank(rawTickerSymbol)) return null
    // check if this symbol overrides the exchange and the currency code
    val periodIdx = rawTickerSymbol.lastIndexOf('.')
    if (periodIdx > 0) {
      val marketID = rawTickerSymbol.substring(periodIdx + 1)
      if (marketID.contains("-")) {
        // the currency ID was encoded along with the market ID
        return fieldIndex(marketID, '-', 1)
      }
    }
    return exchange?.currencyCode
  }
}
