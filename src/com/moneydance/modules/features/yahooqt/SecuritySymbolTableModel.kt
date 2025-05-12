/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.AccountIterator
import com.infinitekind.moneydance.model.CurrencyType
import com.moneydance.apps.md.controller.UserPreferences
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.modules.features.yahooqt.SQUtil.areEqual
import com.moneydance.modules.features.yahooqt.SQUtil.getLabelText
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import com.moneydance.modules.features.yahooqt.SQUtil.parseTickerSymbol
import com.moneydance.util.UiUtil
import java.awt.event.KeyEvent
import java.text.MessageFormat
import java.util.*
import javax.swing.KeyStroke
import javax.swing.UIManager
import javax.swing.table.AbstractTableModel

/**
 * Table model that stores a security and its information about the currency. In this table the
 * user can quickly get at the trading symbol, assign a stock exchange, and test whether the
 * settings are functional.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class SecuritySymbolTableModel
internal constructor(private val _model: StockQuotesModel) : AbstractTableModel() {
  private var _dec = '.'
  private val _data: MutableList<SecurityEntry> = ArrayList()
  
  private var _showZeroBalance = false
  
  fun initialize(preferences: UserPreferences) {
    _dec = preferences.decimalChar
  }
  
  fun load() {
    _data.clear()
    if (_model.rootAccount == null) return
    val iter: Iterator<Account> = AccountIterator(_model.rootAccount)
    while (iter.hasNext()) {
      val account = iter.next()
      if (account.getAccountType() == Account.AccountType.SECURITY) {
        addAccount(account)
      }
    }
    
    for (currency in _model.book!!.currencies) {
      if (currency.currencyType != CurrencyType.Type.SECURITY) continue
      addSecurity(null, currency)
    }
    
    // sort the list alphabetically
    Collections.sort(_data)
    // reset the test results
    resetTestResults()
    // check if the user put any overrides into the symbols that could be simply replaced with an
    // existing stock exchange
    scanForSymbolOverrides()
    // notify that we've rebuilt the data
    fireTableDataChanged()
  }
  
  fun save(root: Account?) {
    if (root == null) return
    
    for (currency in root.book.currencies) {
      if (currency.currencyType != CurrencyType.Type.SECURITY) continue
      
      val entry = getEntryByCurrency(currency)
      if (entry == null) {
        // The account probably has a zero balance and is not currently shown, turn off the
        // downloading of this account. This will do nothing if not in symbol map.
        _model.symbolMap.setIsCurrencyUsed(currency, false)
      } else {
        _model.symbolMap.setIsCurrencyUsed(currency, entry.updatesEnabled)
        _model.symbolMap.setExchangeIdForCurrency(currency, entry.exchangeId)
        // if not the default exchange, store the stock exchange currency as the display currency
        updatePriceDisplayCurrency(currency, entry)
        // update the currency symbol if the user edited it
        val newSymbol = if (entry.editSymbol == null) "" else entry.editSymbol!!.trim()
        val currentSymbol = currency.getTickerSymbol()
        if (newSymbol !== currentSymbol) {
          currency.setTickerSymbol(newSymbol)
        }
      } // if a corresponding entry
    }
    
    
    //    Iterator<Account> iter = new AccountIterator(root);
//    while (iter.hasNext()) {
//      Account account = iter.next();
//      if (account.getAccountType() == Account.AccountType.SECURITY) {
//        final CurrencyType currency = account.getCurrencyType();
//        if (currency == null) continue; // nothing to do, unlikely
//        SecurityEntry entry = getEntryByCurrency(currency);
//        if (entry == null) {
//          // The account probably has a zero balance and is not currently shown, turn off the
//          // downloading of this account. This will do nothing if not in symbol map.
//          _model.getSymbolMap().setIsCurrencyUsed(currency, false);
//        } else {
//          _model.getSymbolMap().setIsCurrencyUsed(currency, entry.use);
//          _model.getSymbolMap().setExchangeIdForCurrency(currency, entry.exchangeId);
//          // if not the default exchange, store the stock exchange currency as the display currency
//          updatePriceDisplayCurrency(currency, entry);
//          // update the currency symbol if the user edited it
//          String newSymbol = entry.editSymbol == null ? "" : entry.editSymbol.trim();
//          String currentSymbol = currency.getTickerSymbol();
//          if (!SQUtil.areEqual(newSymbol, currentSymbol)) {
//            currency.setTickerSymbol(newSymbol);
//          }
//        } // if a corresponding entry
//      } // if a security account
//    } // while iter.hasNext()
  }
  
  /**
   * Historical prices are stored in the base currency, but the user may choose to display them in
   * any currency. When the user picks a stock exchange and assigns it to a security, this method
   * will automatically set the display currency to the stock exchange currency to help avoid
   * confusion.
   * @param securityCurrency The security currency.
   * @param entry            The user-defined settings for the security.
   */
  private fun updatePriceDisplayCurrency(securityCurrency: CurrencyType, entry: SecurityEntry) {
    // do nothing if it's the default exchange
    if (StockExchange.DEFAULT.exchangeId == entry.exchangeId) return
    val exchange = _model.exchangeList.getById(entry.exchangeId)
    if (exchange != null) {
      securityCurrency.setParameter(CurrencyType.TAG_RELATIVE_TO_CURR, exchange.currencyCode)
    }
  }
  
  override fun getRowCount(): Int {
    return _data.size
  }
  
  override fun getColumnCount(): Int {
    return 6
  }
  
  override fun getColumnClass(columnIndex: Int): Class<*> {
    if (columnIndex == USE_COL) return Boolean::class.java
    return String::class.java
  }
  
  override fun getColumnName(column: Int): String {
    return when (column) {
      USE_COL -> N12EStockQuotes.SPACE
      NAME_COL -> _model.gui.getStr("sec")
      SHARES_COL -> _model.gui.getStr("table_column_shares")
      SYMBOL_COL -> _model.gui.getStr("currency_ticker")
      EXCHANGE_COL -> _model.resources.getString(L10NStockQuotes.EXCHANGE_TITLE)
      TEST_COL -> _model.resources.getString(L10NStockQuotes.TEST_TITLE)
      else -> "?"
    }
  }
  
  override fun getValueAt(rowIndex: Int, columnIndex: Int): Any {
    if ((rowIndex < 0) || (rowIndex >= _data.size)) return ""
    val tableEntry = _data[rowIndex] ?: return "?"
    val result = when (columnIndex) {
      USE_COL -> return tableEntry.updatesEnabled
      NAME_COL -> {
        tableEntry.currency!!.getName()
      }
      
      SHARES_COL -> {
        tableEntry.currency!!.formatSemiFancy(tableEntry.shares, _dec)
      }
      
      SYMBOL_COL -> {
        tableEntry.editSymbol!!
      }
      
      EXCHANGE_COL -> {
        val exchange = _model.exchangeList.getById(tableEntry.exchangeId) ?: return StockExchange.DEFAULT
        // not likely because there is a default
        
        return exchange
      }
      
      TEST_COL -> {
        tableEntry.testResult!!
      }
      
      else -> return "?"
    }
    if (isBlank(result)) return ""
    return result
  }
  
  override fun setValueAt(aValue: Any, rowIndex: Int, columnIndex: Int) {
    if ((rowIndex < 0) || (rowIndex >= _data.size)) return
    val tableEntry = _data[rowIndex] ?: return
    when (columnIndex) {
      USE_COL -> {
        val original = tableEntry.updatesEnabled
        if (aValue is Boolean) {
          tableEntry.updatesEnabled = aValue
        } else if (aValue is String) {
          tableEntry.updatesEnabled = aValue.toBoolean()
        }
        if (original != tableEntry.updatesEnabled) {
          _model.setDirty()
          // force a repaint of the header
          _model.fireUpdateHeaderEvent()
        }
      }
      
      SYMBOL_COL -> {
        val original = tableEntry.editSymbol
        val newSymbol = (aValue as String).trim()
        tableEntry.editSymbol = newSymbol
        if (!areEqual(original, newSymbol)) _model.setDirty()
      }
      
      EXCHANGE_COL -> {
        if (aValue is StockExchange) {
          val original = tableEntry.exchangeId
          tableEntry.exchangeId = aValue.exchangeId
          if (!areEqual(original, tableEntry.exchangeId)) _model.setDirty()
          // check if the symbol had some overrides on it, and strip them out
          if (stripExchangeOverrides(tableEntry)) {
            refreshRow(rowIndex)
          }
        }
      }
      
      else -> {}
    }
  }
  
  fun getToolTip(rowIndex: Int, columnIndex: Int): String? {
    if ((rowIndex < 0) || (rowIndex >= _data.size)) return null
    if (_model.rootAccount == null) return null
    val tableEntry = _data[rowIndex] ?: return null
    if (columnIndex == TEST_COL) return tableEntry.toolTip
    if (columnIndex == SYMBOL_COL) {
      val exchange = _model.exchangeList.getById(tableEntry.exchangeId) ?: return null
      val connection = _model.selectedHistoryConnection ?: return null
      val parsedSymbol = parseTickerSymbol(tableEntry.editSymbol ?: return null) ?: return null
      val fullSymbol = connection.getFullTickerSymbol(parsedSymbol, exchange)
      return UiUtil.getLabelText(_model.gui.resources, "currency_ticker") + fullSymbol
    }
    if (columnIndex == EXCHANGE_COL) {
      val exchange = _model.exchangeList.getById(tableEntry.exchangeId)
      val sb = StringBuilder(N12EStockQuotes.HTML_BEGIN)
      val priceCurrency = _model.book!!.currencies.getCurrencyByIDString(exchange.currencyCode)
      if (priceCurrency != null) {
        sb.append(UiUtil.getLabelText(_model.gui, L10NStockQuotes.CURRENCY_LABEL))
        sb.append(getCurrencyAbbreviatedDisplay(priceCurrency))
        sb.append(N12EStockQuotes.COMMA_SEPARATOR)
      }
      sb.append(getLabelText(_model.resources, L10NStockQuotes.MULTIPLIER_LABEL))
      sb.append(exchange.priceMultiplier.toString())
      sb.append(N12EStockQuotes.BREAK)
      val keyText = getAcceleratorText(
        KeyStroke.getKeyStroke(
          KeyEvent.VK_E,
          MoneydanceGUI.ACCELERATOR_MASK
        )
      )
      sb.append(
        MessageFormat.format(
          _model.resources.getString(L10NStockQuotes.EXCHANGE_EDIT_TIP_FMT),
          keyText
        )
      )
      sb.append(N12EStockQuotes.HTML_END)
      return sb.toString()
    }
    return null
  }
  
  override fun isCellEditable(rowIndex: Int, columnIndex: Int): Boolean {
    return when (columnIndex) {
      USE_COL, SYMBOL_COL, EXCHANGE_COL -> {
        true
      }
      
      else -> false
    }
  }
  
  fun getEntry(rowIndex: Int): SecurityEntry {
    return _data[rowIndex]
  }
  
  fun resetTestResults() {
    for (entry in _data) entry.testResult = ""
  }
  
  fun scanForSymbolOverrides() {
    for (entry in _data) {
      val parsedSymbol = parseTickerSymbol(entry.currency)
      if ((parsedSymbol == null) || isBlank(parsedSymbol.symbol)) {
        entry.testResult = _model.resources.getString(L10NStockQuotes.INVALID_SYMBOL)
        continue
      }
      var override: StockExchange? = null
      if (!isBlank(parsedSymbol.prefix)) {
        override = _model.exchangeList.findByGooglePrefix(parsedSymbol.prefix)
      }
      if (!isBlank(parsedSymbol.suffix)) {
        override = _model.exchangeList.findByYahooSuffix(parsedSymbol.suffix)
      }
      if ((override != null) && !isBlank(parsedSymbol.currencyCode)) {
        // the user has provided a currency override, check if it matches the override exchange
        if (parsedSymbol.currencyCode.compareTo(override.currencyCode!!) != 0) {
          // not a match, ignore the exchange override and just leave the symbol as-is
          buildCurrencyMismatchMessage(entry, parsedSymbol.currencyCode, override)
          override = null
        }
      }
      if (override != null) {
        if (Main.DEBUG_YAHOOQT) {
          System.err.println(
            ("Replacing security symbol '" + entry.currency!!.getTickerSymbol()
             + "' with stripped one '" + parsedSymbol.symbol + "' and setting to exchange "
             + override.name)
          )
        }
        // set the override exchange
        entry.exchangeId = override.exchangeId
        // strip out all the extraneous stuff that isn't needed anymore
        stripExchangeOverrides(entry)
        if (isBlank(entry.testResult)) {
          // validate the currency for the override exchange
          val priceCurrency = _model.book!!.currencies.getCurrencyByIDString(override.currencyCode)
          setPriceCurrencyMessage(entry, override.currencyCode, priceCurrency)
        }
      } else {
        // validate the price currency for the assigned exchange
        var currencyCode = parsedSymbol.currencyCode
        val exchange = _model.exchangeList.getById(entry.exchangeId)
        if (isBlank(currencyCode)) {
          currencyCode = exchange?.currencyCode ?: currencyCode
        }
        val priceCurrency = if (isBlank(currencyCode)) null else _model.book!!.currencies.getCurrencyByIDString(currencyCode)
        // if the price currency is null we will display a message later
        // if the exchange is null we can't check for a currency mismatch (shouldn't happen)
        // if there isn't an overridden currency, there can't be a mismatch
        // otherwise, check if the overridden currency matches the assigned exchange or not
        if ((priceCurrency != null) && (exchange != null) && !isBlank(parsedSymbol.currencyCode) && (parsedSymbol.currencyCode != exchange.currencyCode)) {
          // the currency override does not match the assigned exchange's currency
          buildCurrencyMismatchMessage(entry, parsedSymbol.currencyCode, exchange)
        } // price currency defined
        
        // now if no other messages already exist, show the currency message
        if (isBlank(entry.testResult)) {
          setPriceCurrencyMessage(entry, currencyCode, priceCurrency)
        }
      } // no exchange override
    }
  }
  
  private fun setPriceCurrencyMessage(entry: SecurityEntry, currencyCode: String?, priceCurrency: CurrencyType?) {
    if (priceCurrency != null) {
      // show the success message and display what price currency is being used
      entry.testResult = MessageFormat.format(
        _model.resources.getString(L10NStockQuotes.PRICE_CURRENCY_FMT),
        getCurrencyAbbreviatedDisplay(priceCurrency)
      )
    } else {
      // the currency code is either invalid or blank
      buildInvalidPriceCurrencyMessage(entry, currencyCode)
    }
  }
  
  private fun buildCurrencyMismatchMessage(entry: SecurityEntry, currencyCode: String, exchange: StockExchange?) {
    val overrideCurrency = if (isBlank(currencyCode)) null else _model.book!!.currencies.getCurrencyByIDString(currencyCode)
    val exchangeCurrency = if (exchange == null) null else _model.book!!.currencies.getCurrencyByIDString(exchange.currencyCode)
    if ((overrideCurrency == null) || (exchangeCurrency == null)) {
      // missing one or both currencies, so just show the codes
      val sb = StringBuilder(N12EStockQuotes.HTML_BEGIN)
      sb.append(N12EStockQuotes.RED_FONT_BEGIN)
      sb.append(
        MessageFormat.format(
          _model.resources.getString(L10NStockQuotes.CURRENCY_CODE_MISMATCH_FMT),
          if (isBlank(currencyCode)) "''" else currencyCode,
          if (exchange == null) "''" else exchange.currencyCode
        )
      )
      sb.append(N12EStockQuotes.FONT_END)
      sb.append(N12EStockQuotes.HTML_END)
      entry.testResult = sb.toString()
    } else {
      // we can display both currencies
      val sb = StringBuilder(N12EStockQuotes.HTML_BEGIN)
      sb.append(N12EStockQuotes.RED_FONT_BEGIN)
      sb.append(
        MessageFormat.format(
          _model.resources.getString(L10NStockQuotes.CURRENCY_MISMATCH_FMT),
          getCurrencyAbbreviatedDisplay(overrideCurrency),
          getCurrencyAbbreviatedDisplay(exchangeCurrency)
        )
      )
      sb.append(N12EStockQuotes.FONT_END)
      sb.append(N12EStockQuotes.HTML_END)
      entry.testResult = sb.toString()
    }
  }
  
  private fun buildInvalidPriceCurrencyMessage(entry: SecurityEntry, currencyCode: String?) {
    if (isBlank(currencyCode)) {
      // the currency code isn't specified
      val sb = StringBuilder(N12EStockQuotes.HTML_BEGIN)
      sb.append(N12EStockQuotes.RED_FONT_BEGIN)
      sb.append(_model.resources.getString(L10NStockQuotes.CURRENCY_UNDEFINED))
      sb.append(N12EStockQuotes.FONT_END)
      sb.append(N12EStockQuotes.HTML_END)
      entry.testResult = sb.toString()
    } else {
      // we have a currency code but it isn't defined in the data file
      val sb = StringBuilder(N12EStockQuotes.HTML_BEGIN)
      sb.append(N12EStockQuotes.RED_FONT_BEGIN)
      sb.append(
        MessageFormat.format(
          _model.resources.getString(L10NStockQuotes.CURRENCY_NOT_FOUND_FMT),
          currencyCode
        )
      )
      sb.append(N12EStockQuotes.FONT_END)
      sb.append(N12EStockQuotes.HTML_END)
      entry.testResult = sb.toString()
    }
  }
  
  fun getEntryByCurrency(currency: CurrencyType): SecurityEntry? {
    for (entry in _data) {
      if (currency.equals(entry.currency)) return entry
    }
    return null
  }
  
  
  private fun addAccount(account: Account) {
    val currency = account.currencyType ?: return
    // should never happen
    
    addSecurity(account, currency)
  }
  
  private fun addSecurity(account: Account?, currency: CurrencyType) {
    _model.addSecurity(account, currency)
    var entry = getEntryByCurrency(currency)
    
    val balance = account?.balance ?: 0
    if ((balance == 0L) && !_showZeroBalance) return  // nothing to do
    
    if (entry == null) {
      entry = SecurityEntry()
      entry.currency = currency
      entry.editSymbol = currency.getTickerSymbol()
      // build or rebuild the symbol map if there is no match
      if (_model.symbolMap.hasCurrency(currency)) {
        entry.exchangeId = _model.symbolMap.getExchangeIdForCurrency(currency)
        entry.updatesEnabled = _model.symbolMap.getIsCurrencyUsed(currency)
      } else {
        // add a new security to the map, clearing the 'use' flag if it is zero balance
        entry.exchangeId = _model.symbolMap.addCurrency(currency)
        entry.updatesEnabled = (balance != 0L) && _model.symbolMap.getIsCurrencyUsed(currency)
      }
      _data.add(entry)
    }
    entry.shares += balance
  }
  
  var showZeroBalance: Boolean
    get() = _showZeroBalance
    set(showZeroBalance) {
      _showZeroBalance = showZeroBalance
      load()
    }
  
  /**
   * Refresh a single row in the table, or refresh all rows, on the Event Data/UI Thread.
   * @param rowIndex The row to update, or -1 to update all rows.
   */
  fun refreshRow(rowIndex: Int) {
    UiUtil.runOnUIThread {
      if (rowIndex < 0) {
        fireTableDataChanged()
      } else {
        fireTableRowsUpdated(rowIndex, rowIndex)
      }
    }
  }
  
  fun allSymbolsEnabled(): Boolean {
    for (entry in _data) {
      if (!entry.updatesEnabled) return false
    }
    return true
  }
  
  fun anySymbolEnabled(): Boolean {
    for (entry in _data) {
      if (entry.updatesEnabled) return true
    }
    return false
  }
  
  fun enableAllSymbols(use: Boolean) {
    for (entry in _data) {
      if (entry.updatesEnabled != use) _model.setDirty()
      entry.updatesEnabled = use
    }
    fireTableDataChanged()
  }
  
  fun batchChangeExchange(newExchange: StockExchange?) {
    if (newExchange == null) return
    val exchangeId = newExchange.exchangeId
    if (isBlank(exchangeId)) return
    for (entry in _data) {
      if (exchangeId != entry.exchangeId) _model.setDirty()
      entry.exchangeId = exchangeId
      stripExchangeOverrides(entry)
    }
    fireTableDataChanged()
  }
  
  /**
   * See if the symbol has any overrides for the exchange and/or currency and remove them, leaving
   * only the symbol itself.
   * @param entry Table entry to check for overrides.
   * @return True if the ticker symbol has changed, false if it was left the same.
   */
  private fun stripExchangeOverrides(entry: SecurityEntry): Boolean {
    val parsedSymbol = parseTickerSymbol(entry.currency)
    if ((parsedSymbol == null) || isBlank(parsedSymbol.symbol)) {
      entry.testResult = _model.resources.getString(L10NStockQuotes.INVALID_SYMBOL)
      return false
    }
    val changed = (parsedSymbol.symbol.compareTo(entry.editSymbol!!) != 0)
    if (changed) {
      entry.editSymbol = parsedSymbol.symbol
      entry.testResult = _model.resources.getString(L10NStockQuotes.MODIFIED)
    }
    return changed
  }
  
  fun registerTestResults(downloadInfo: DownloadInfo) {
    for (index in _data.indices.reversed()) {
      val entry = _data[index]
      if (entry.currency === downloadInfo.security) {
        entry.testResult = downloadInfo.resultText
        entry.toolTip = downloadInfo.toolTip
        refreshRow(index)
        break
      }
    }
  }
  
  inner class SecurityEntry : Comparable<SecurityEntry> {
    var currency: CurrencyType? = null
    var shares: Long = 0
    var updatesEnabled: Boolean = true
    var editSymbol: String? = null
    var exchangeId: String? = null
    var testResult: String? = null
    var toolTip: String? = null
    
    /**
     * Sort alphabetically by the display name of the currency.
     * @param other The other object to compare to.
     * @return Less than zero if less than, zero if equal, greater than zero if greater than other.
     */
    override fun compareTo(other: SecurityEntry): Int {
      return currency!!.getName().compareTo(other.currency!!.getName())
    }
  }
  
  companion object {
    const val USE_COL: Int = 0
    const val NAME_COL: Int = 1
    const val SYMBOL_COL: Int = 2
    const val EXCHANGE_COL: Int = 3
    const val TEST_COL: Int = 4
    
    // hidden column
    const val SHARES_COL: Int = 5
    
    /**
     * Show the accelerator key text. Adapted from BasicMenuItemUI.java.
     * @param accelerator The keypress to generate text for.
     * @return The resulting text representing the key press.
     */
    private fun getAcceleratorText(accelerator: KeyStroke?): String {
      val acceleratorDelimiter = UIManager.getString("MenuItem.acceleratorDelimiter")
      var acceleratorText = ""
      if (accelerator != null) {
        val modifiers = accelerator.modifiers
        if (modifiers > 0) {
          acceleratorText = KeyEvent.getKeyModifiersText(modifiers)
          if (acceleratorDelimiter != null) acceleratorText += acceleratorDelimiter
        }
        val keyCode = accelerator.keyCode
        if (keyCode != 0) {
          acceleratorText += KeyEvent.getKeyText(keyCode)
        } else {
          acceleratorText += accelerator.keyChar
        }
      }
      return acceleratorText
    }
    
    private fun getCurrencyAbbreviatedDisplay(currencyType: CurrencyType): String {
      var result = currencyType.getPrefix()
      if (!isBlank(result)) return result
      result = currencyType.getSuffix()
      if (!isBlank(result)) return result
      return currencyType.idString
    }
  }
}
