package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.AccountBook
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.util.StringUtils.fieldIndex
import com.moneydance.apps.md.controller.UserPreferences

/**
 * The DownloadModel is where we handle common functions such as parsing ticker symbols and other
 * things that are common to most currency or security downloads but can be tweaked by specific
 * connections.
 */
class DownloadModel internal constructor(val quotesModel: StockQuotesModel, private val connection: BaseConnection) {
  val book: AccountBook?
    /** Get the AccountBook containing the securities and currencies to update.  */
    get() = quotesModel?.book
  
  val resources: ResourceProvider
    /** Get available resources - strings, images, etc  */
    get() = quotesModel!!.resources
  
  
  /**
   * Obtain the associated stock exchange for a particular security. This method first checks if
   * the user has put any overrides in the security symbol. An override can be a Google prefix
   * (such as 'LON:') or a Yahoo suffix (such as '.L'). If an override exists and maps to an
   * exchange, then that exchange is returned. Otherwise the exchange listed in the symbol map
   * for the security is used.
   * @param symbol           The parsed symbol along with any overrides entered by the user.
   * @param securityCurrency The security currency.
   * @return The appropriate stock exchange definition to use for the given security.
   */
  fun getExchangeForSecurity(symbol: SymbolData, securityCurrency: CurrencyType): StockExchange {
    quotesModel?.let { quotesModel ->
      if (!SQUtil.isBlank(symbol.prefix)) {
        // check for a Google prefix override
        quotesModel.exchangeList.findByGooglePrefix(symbol.prefix)?.let { return it }
      }
      if (!SQUtil.isBlank(symbol.suffix)) {
        // check for a Yahoo exchange suffix override
        quotesModel.exchangeList.findByYahooSuffix(symbol.suffix)?.let { return it }
      }
    }
    // go with the exchange the user assigned to the security
    return quotesModel?.symbolMap?.getExchangeForCurrency(securityCurrency) ?: StockExchange.DEFAULT
  }
  
  
  fun getFullTickerSymbol(symbolData: SymbolData, exchange: StockExchange?): String? {
    return connection.getFullTickerSymbol(symbolData, exchange)
  }
  
  
  /**
   * Given a ticker symbol, which could have an embedded currency (typically after the '-' symbol),
   * and return the currency code for the currency that should be used to interpret prices. If a
   * the current connection returns a non-blank value from its getCurrencyCodeForQuote method then
   * that value is used.
   *
   * @param rawTickerSymbol The ticker symbol, potentially with an embedded currency.
   * @param exchange        The selected stock exchange to use.
   * @return the currency code from the ticker symbol, or if no embedded currency, the currency code
   * as specified by the given stock exchange.
   */
  fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange): String? {
    if (SQUtil.isBlank(rawTickerSymbol)) return null
    
    val connectionSpecificCode = connection.getCurrencyCodeForQuote(rawTickerSymbol, exchange)
    if (!SQUtil.isBlank(connectionSpecificCode)) return connectionSpecificCode
    
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
    return exchange.currencyCode
  }
  
  
  val preferences: UserPreferences
    get() = quotesModel.preferences
  
  val decimalDisplayChar: Char
    get() = quotesModel.decimalDisplayChar
  
  fun showURL(urlString: String?) {
    quotesModel.showURL(urlString)
  }
  
  fun beep() {
    try {
      quotesModel.gui.beep()
    } catch (t: Throwable) {
      System.err.println("BEEP!")
    }
  }
  
  fun showProgress(progressPercent: Float, message: String?) {
    quotesModel.showProgress(progressPercent, message)
  }
}
