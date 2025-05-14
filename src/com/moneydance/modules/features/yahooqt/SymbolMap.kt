/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.AccountBook
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.util.StreamTable
import com.infinitekind.util.StreamVector
import com.infinitekind.util.StringEncodingException
import com.moneydance.modules.features.yahooqt.SQUtil.getCurrencyWithID
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank

/**
 * Maps a list of currency/security types (each of which has a trading symbol) to their respective
 * stock exchange ID. This map is stored in the data file parameters, because the currency list
 * comes from the currency table, and the table is stored in the data file. Thus each data file
 * can have its own currency list. The symbol-to-exchange map should stay with the currency table.
 *
 *
 * We do not store this per account, because multiple accounts can link back to the same security,
 * so the stock exchange would have to be a duplicated setting in each account. So we keep the
 * stock exchange setting with the currency which can potentially span accounts.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class SymbolMap internal constructor(
  /**
   * The catalog of possible stock exchange definitions.
   */
  private val _exchangeList: StockExchangeList) {
  /**
   * The map of CurrencyType.id (kept unique) to a stock exchange ID and whether to download it.
   */
  private val _symbolMap = mutableMapOf<String, CurrencyData>()
  
  /**
   * Save the map of currency IDs to the stock exchange in the data file.
   * @param root the root account in the data file where the symbol map is stored
   */
  fun saveToFile(root: Account?) {
    if (root == null) return
    val exchangeList = StreamVector()
    for (currencyID in _symbolMap.keys) {
      val data = _symbolMap[currencyID]
      var exchangeId = data!!.exchangeId
      if (isBlank(exchangeId) || !_exchangeList.contains(exchangeId)) {
        exchangeId = StockExchange.DEFAULT.exchangeId
      }
      val settings = StreamTable()
      settings.put(CURRENCY_ID_KEY, currencyID)
      settings.put(EXCHANGE_ID_KEY, exchangeId)
      settings.put(USE_SYMBOL_KEY, data.use)
      exchangeList.add(settings)
    }
    val table = StreamTable()
    table[EXCHANGE_LIST_KEY] = exchangeList
    root.setParameter(EXCHANGE_MAP_KEY, table.writeToString())
  }
  
  fun clear() {
    _symbolMap.clear()
  }
  
  /**
   * Load the map of currencyIDs to stock exchange from the data file.
   * @param book The main data structure
   */
  fun loadFromFile(book: AccountBook?) {
    if (book == null) return
    clear()
    val settings = book.getRootAccount().getParameter(EXCHANGE_MAP_KEY)
    if (isBlank(settings)) return
    try {
      val table = StreamTable()
      table.readFrom(settings)
      val settingsList = table[EXCHANGE_LIST_KEY] as StreamVector?
      if (settingsList == null) {
        QER_DLOG.log { "Quotes and Exchange Rates plugin no symbol map found." }
        return
      }
      for (mapPair in settingsList) {
        if (mapPair !is StreamTable) continue
        val pairTable = mapPair
        val currencyID = pairTable.getStr(CURRENCY_UUID_KEY, pairTable.getStr(CURRENCY_ID_KEY, null))
        val currency = getCurrencyWithID(book, currencyID!!)
        if (currency != null) {
          val exchangeId = pairTable.getStr(EXCHANGE_ID_KEY, DEFAULT_EXCHANGE_ID)
          val use = pairTable.getBoolean(USE_SYMBOL_KEY, DEFAULT_USE)
          _symbolMap[currency.UUID] = CurrencyData(exchangeId, use)
        }
      }
    } catch (e: StringEncodingException) {
      System.err.println("Quotes and Exchange Rates plugin error reading security to exchange Id map")
    }
  }
  
  fun getExchangeIdForCurrency(currency: CurrencyType): String? {
    val data = _symbolMap[currency.UUID] ?: return StockExchange.DEFAULT.exchangeId
    val exchangeId = data.exchangeId
    if (isBlank(exchangeId)) return StockExchange.DEFAULT.exchangeId
    return exchangeId
  }
  
  fun getExchangeForCurrency(currency: CurrencyType): StockExchange {
    val data = _symbolMap[currency.UUID] ?: return StockExchange.DEFAULT
    val exchangeId = data.exchangeId
    if (isBlank(exchangeId)) return StockExchange.DEFAULT
    return _exchangeList.getById(exchangeId)
  }
  
  fun setExchangeIdForCurrency(currency: CurrencyType, exchangeId: String?) {
    val data = _symbolMap[currency.UUID] ?: return
    data.exchangeId = exchangeId
  }
  
  fun getIsCurrencyUsed(currency: CurrencyType): Boolean {
    val data = _symbolMap[currency.UUID] ?: return false
    return data.use
  }
  
  fun setIsCurrencyUsed(currency: CurrencyType, useForDownload: Boolean) {
    val data = _symbolMap[currency.UUID] ?: return
    data.use = useForDownload
  }
  
  fun hasCurrency(currency: CurrencyType): Boolean {
    return _symbolMap.containsKey(currency.UUID)
  }
  
  fun addCurrency(currency: CurrencyType): String? {
    // assume the currency is valid
    _symbolMap[currency.UUID] = CurrencyData(DEFAULT_EXCHANGE_ID, DEFAULT_USE)
    return DEFAULT_EXCHANGE_ID
  }
  
  private fun isValidCurrency(book: AccountBook, currencyID: String): Boolean {
    return getCurrencyWithID(book, currencyID) != null
  }
  
  private inner class CurrencyData(exchangeId: String?, use: Boolean) {
    var exchangeId: String? = null
    var use: Boolean = DEFAULT_USE
    
    init {
      this.exchangeId = exchangeId
      this.use = use
    }
  }
  
  companion object {
    private const val EXCHANGE_MAP_KEY = "symbolExchangeMap"
    private const val EXCHANGE_LIST_KEY = "exchangeList"
    private const val CURRENCY_ID_KEY = "currId"
    private const val CURRENCY_UUID_KEY = "currUUID"
    private const val EXCHANGE_ID_KEY = "exchId"
    private const val USE_SYMBOL_KEY = "use"
    private const val DEFAULT_USE = true
    private val DEFAULT_EXCHANGE_ID = StockExchange.DEFAULT.exchangeId
  }
}
