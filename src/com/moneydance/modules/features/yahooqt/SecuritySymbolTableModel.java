/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.UserPreferences;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.util.UiUtil;

import javax.swing.KeyStroke;
import javax.swing.UIManager;
import javax.swing.table.AbstractTableModel;
import java.awt.event.KeyEvent;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

/**
 * Table model that stores a security and its information about the currency. In this table the
 * user can quickly get at the trading symbol, assign a stock exchange, and test whether the
 * settings are functional.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class SecuritySymbolTableModel extends AbstractTableModel
{
  static final int USE_COL = 0;
  static final int NAME_COL = 1;
  static final int SYMBOL_COL = 2;
  static final int EXCHANGE_COL = 3;
  static final int TEST_COL = 4;
  // hidden column
  static final int SHARES_COL = 5;

  private char _dec = '.';
  private final List<SecurityEntry> _data = new ArrayList<SecurityEntry>();

  private final StockQuotesModel _model;
  private boolean _showZeroBalance = false;

  SecuritySymbolTableModel(StockQuotesModel model) {
    _model = model;
  }

  void initialize(UserPreferences preferences) {
    _dec = preferences.getDecimalChar();
  }

  void load() {
    _data.clear();
    if (_model.getRootAccount() == null) return;
    Iterator<Account> iter = new AccountIterator(_model.getRootAccount());
    while (iter.hasNext()) {
      Account account = iter.next();
      if (account.getAccountType() == Account.AccountType.SECURITY) {
        addAccount(account);
      }
    }
    // sort the list alphabetically
    Collections.sort(_data);
    // reset the test results
    resetTestResults();
    // check if the user put any overrides into the symbols that could be simply replaced with an
    // existing stock exchange
    scanForSymbolOverrides();
    // notify that we've rebuilt the data
    fireTableDataChanged();
  }

  void save() {
    if (_model.getRootAccount() == null) return;
    Iterator<Account> iter = new AccountIterator(_model.getRootAccount());
    while (iter.hasNext()) {
      Account account = iter.next();
      if (account.getAccountType() == Account.AccountType.SECURITY) {
        final CurrencyType currency = account.getCurrencyType();
        if (currency == null) continue; // nothing to do, unlikely
        SecurityEntry entry = getEntryByCurrency(currency);
        if (entry == null) {
          // The account probably has a zero balance and is not currently shown, turn off the
          // downloading of this account. This will do nothing if not in symbol map.
          _model.getSymbolMap().setIsCurrencyUsed(currency, false);
        } else {
          _model.getSymbolMap().setIsCurrencyUsed(currency, entry.use);
          _model.getSymbolMap().setExchangeIdForCurrency(currency, entry.exchangeId);
          // if not the default exchange, store the stock exchange currency as the display currency
          updatePriceDisplayCurrency(currency, entry);
          // update the currency symbol if the user edited it
          String newSymbol = entry.editSymbol == null ? "" : entry.editSymbol.trim();
          String currentSymbol = currency.getTickerSymbol();
          if (!SQUtil.areEqual(newSymbol, currentSymbol)) {
            currency.setTickerSymbol(newSymbol);
          }
        } // if a corresponding entry
      } // if a security account
    } // while iter.hasNext()
  }

  /**
   * Historical prices are stored in the base currency, but the user may choose to display them in
   * any currency. When the user picks a stock exchange and assigns it to a security, this method
   * will automatically set the display currency to the stock exchange currency to help avoid
   * confusion.
   * @param securityCurrency The security currency.
   * @param entry            The user-defined settings for the security.
   */
  private void updatePriceDisplayCurrency(CurrencyType securityCurrency, SecurityEntry entry) {
    // do nothing if it's the default exchange
    if (StockExchange.DEFAULT.getExchangeId().equals(entry.exchangeId)) return;
    final StockExchange exchange = _model.getExchangeList().getById(entry.exchangeId);
    if (exchange != null) {
      securityCurrency.setParameter(CurrencyType.TAG_RELATIVE_TO_CURR, exchange.getCurrencyCode());
    }
  }

  public int getRowCount() {
    return _data.size();
  }

  public int getColumnCount() {
    return 6;
  }

  @Override
  public Class<?> getColumnClass(int columnIndex) {
    if (columnIndex == USE_COL) return Boolean.class;
    return String.class;
  }

  @Override
  public String getColumnName(int column) {
    switch(column) {
      case USE_COL: return N12EStockQuotes.SPACE;
      case NAME_COL: return _model.getGUI().getStr("sec");
      case SHARES_COL: return _model.getGUI().getStr("table_column_shares");
      case SYMBOL_COL: return _model.getGUI().getStr("currency_ticker");
      case EXCHANGE_COL: return _model.getResources().getString(L10NStockQuotes.EXCHANGE_TITLE);
      case TEST_COL: return _model.getResources().getString(L10NStockQuotes.TEST_TITLE);
      default:
        return "?";
    }
  }

  public Object getValueAt(int rowIndex, int columnIndex) {
    if ((rowIndex < 0) || (rowIndex >= _data.size())) return "";
    final SecurityEntry tableEntry = _data.get(rowIndex);
    if (tableEntry == null) return "?";
    String result;
    switch(columnIndex) {
      case USE_COL: return Boolean.valueOf(tableEntry.use);
      case NAME_COL: {
        result = tableEntry.currency.getName();
        break;
      }
      case SHARES_COL: {
        result = tableEntry.currency.formatSemiFancy(tableEntry.shares, _dec);
        break;
      }
      case SYMBOL_COL: {
        result = tableEntry.editSymbol;
        break;
      }
      case EXCHANGE_COL: {
        final StockExchange exchange = _model.getExchangeList().getById(tableEntry.exchangeId);
        if (exchange == null) return StockExchange.DEFAULT; // not likely because there is a default
        return exchange;
      }
      case TEST_COL: {
        result = tableEntry.testResult;
        break;
      }
      default:
        return "?";
    }
    if (SQUtil.isBlank(result)) return "";
    return result;
  }

  @Override
  public void setValueAt(Object aValue, int rowIndex, int columnIndex) {
    if ((rowIndex < 0) || (rowIndex >= _data.size())) return;
    final SecurityEntry tableEntry = _data.get(rowIndex);
    if (tableEntry == null) return;
    switch(columnIndex) {
      case USE_COL: {
        final boolean original = tableEntry.use;
        if (aValue instanceof Boolean) {
          tableEntry.use = ((Boolean)aValue).booleanValue();
        } else if (aValue instanceof String) {
          tableEntry.use = Boolean.valueOf((String)aValue).booleanValue();
        }
        if (original != tableEntry.use) {
          _model.setDirty();
          // force a repaint of the header
          _model.fireUpdateHeaderEvent();
        }
        break;
      }
      case SYMBOL_COL: {
        final String original = tableEntry.editSymbol;
        final String newSymbol = ((String)aValue).trim();
        tableEntry.editSymbol = newSymbol;
        if (!SQUtil.areEqual(original, newSymbol)) _model.setDirty();
        break;
      }
      case EXCHANGE_COL: {
        if (aValue instanceof StockExchange) {
          final String original = tableEntry.exchangeId;
          tableEntry.exchangeId = ((StockExchange)aValue).getExchangeId();
          if (!SQUtil.areEqual(original, tableEntry.exchangeId)) _model.setDirty();
          // check if the symbol had some overrides on it, and strip them out
          if (stripExchangeOverrides(tableEntry)) {
            refreshRow(rowIndex);
          }
        }
        break;
      }
      default: // no other columns editable
    }
  }

  String getToolTip(int rowIndex, int columnIndex) {
    if ((rowIndex < 0) || (rowIndex >= _data.size())) return null;
    if (_model.getRootAccount() == null) return null;
    final SecurityEntry tableEntry = _data.get(rowIndex);
    if (tableEntry == null) return null;
    if (columnIndex == TEST_COL) return tableEntry.toolTip;
    if (columnIndex == SYMBOL_COL) {
      StockExchange exchange = _model.getExchangeList().getById(tableEntry.exchangeId);
      if (exchange == null) return null;
      BaseConnection connection = _model.getSelectedHistoryConnection();
      if (connection == null) return null;
      SymbolData parsedSymbol = SQUtil.parseTickerSymbol(tableEntry.editSymbol);
      String fullSymbol = connection.getFullTickerSymbol(parsedSymbol, exchange);
      return UiUtil.getLabelText(_model.getGUI().getResources(), "currency_ticker") + fullSymbol;
    }
    if (columnIndex == EXCHANGE_COL) {
      StockExchange exchange = _model.getExchangeList().getById(tableEntry.exchangeId);
      StringBuilder sb = new StringBuilder(N12EStockQuotes.HTML_BEGIN);
      CurrencyType priceCurrency =  _model.getBook().getCurrencies().getCurrencyByIDString(exchange.getCurrencyCode());
      if (priceCurrency != null) {
        sb.append(UiUtil.getLabelText(_model.getGUI(), L10NStockQuotes.CURRENCY_LABEL));
        sb.append(getCurrencyAbbreviatedDisplay(priceCurrency));
        sb.append(N12EStockQuotes.COMMA_SEPARATOR);
      }
      sb.append(SQUtil.getLabelText(_model.getResources(), L10NStockQuotes.MULTIPLIER_LABEL));
      sb.append(Double.toString(exchange.getPriceMultiplier()));
      sb.append(N12EStockQuotes.BREAK);
      final String keyText = getAcceleratorText(KeyStroke.getKeyStroke(KeyEvent.VK_E,
            MoneydanceGUI.ACCELERATOR_MASK));
      sb.append(MessageFormat.format(_model.getResources().getString(L10NStockQuotes.EXCHANGE_EDIT_TIP_FMT),
              keyText));
      sb.append(N12EStockQuotes.HTML_END);
      return sb.toString();
    }
    return null;
  }

  /**
   * Show the accelerator key text. Adapted from BasicMenuItemUI.java.
   * @param accelerator The keypress to generate text for.
   * @return The resulting text representing the key press.
   */
  private static String getAcceleratorText(KeyStroke accelerator) {
    String acceleratorDelimiter = UIManager.getString("MenuItem.acceleratorDelimiter");
    String acceleratorText = "";
    if (accelerator != null) {
      int modifiers = accelerator.getModifiers();
      if (modifiers > 0) {
        acceleratorText = KeyEvent.getKeyModifiersText(modifiers);
        if (acceleratorDelimiter != null) acceleratorText += acceleratorDelimiter;
      }
      int keyCode = accelerator.getKeyCode();
      if (keyCode != 0) {
        acceleratorText += KeyEvent.getKeyText(keyCode);
      } else {
        acceleratorText += accelerator.getKeyChar();
      }
    }
    return acceleratorText;
  }

  @Override
  public boolean isCellEditable(int rowIndex, int columnIndex) {
    switch(columnIndex) {
      case USE_COL:
      case SYMBOL_COL:
      case EXCHANGE_COL: {
        return true;
      }
      default:
        return false;
    }
  }

  SecurityEntry getEntry(final int rowIndex) {
    return _data.get(rowIndex);
  }

  void resetTestResults() {
    for (SecurityEntry entry : _data) entry.testResult = "";
  }

  void scanForSymbolOverrides() {
    for (SecurityEntry entry : _data) {
      SymbolData parsedSymbol = SQUtil.parseTickerSymbol(entry.currency);
      if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) {
        entry.testResult = _model.getResources().getString(L10NStockQuotes.INVALID_SYMBOL);
        continue;
      }
      StockExchange override = null;
      if (!SQUtil.isBlank(parsedSymbol.prefix)) {
        override = _model.getExchangeList().findByGooglePrefix(parsedSymbol.prefix);
      }
      if (!SQUtil.isBlank(parsedSymbol.suffix)) {
        override = _model.getExchangeList().findByYahooSuffix(parsedSymbol.suffix);
      }
      if ((override != null) && !SQUtil.isBlank(parsedSymbol.currencyCode)) {
        // the user has provided a currency override, check if it matches the override exchange
        if (parsedSymbol.currencyCode.compareTo(override.getCurrencyCode()) != 0) {
          // not a match, ignore the exchange override and just leave the symbol as-is
          buildCurrencyMismatchMessage(entry, parsedSymbol.currencyCode, override);
          override = null;
        }
      }
      if (override != null) {
        if(Main.DEBUG_YAHOOQT) {
          System.err.println("Replacing security symbol '" + entry.currency.getTickerSymbol()
                             + "' with stripped one '" + parsedSymbol.symbol + "' and setting to exchange "
                             + override.getName());
        }
        // set the override exchange
        entry.exchangeId = override.getExchangeId();
        // strip out all the extraneous stuff that isn't needed anymore
        stripExchangeOverrides(entry);
        if (SQUtil.isBlank(entry.testResult)) {
          // validate the currency for the override exchange
          CurrencyType priceCurrency = _model.getBook().getCurrencies().getCurrencyByIDString(override.getCurrencyCode());
          setPriceCurrencyMessage(entry, override.getCurrencyCode(), priceCurrency);
        }
      } else {
        // validate the price currency for the assigned exchange
        String currencyCode = parsedSymbol.currencyCode;
        StockExchange exchange = _model.getExchangeList().getById(entry.exchangeId);
        if (SQUtil.isBlank(currencyCode) && (exchange != null)) {
          currencyCode = exchange.getCurrencyCode();
        }
        CurrencyType priceCurrency = SQUtil.isBlank(currencyCode) ? null :
                                     _model.getBook().getCurrencies().getCurrencyByIDString(currencyCode);
        // if the price currency is null we will display a message later
        // if the exchange is null we can't check for a currency mismatch (shouldn't happen)
        // if there isn't an overridden currency, there can't be a mismatch
        // otherwise, check if the overridden currency matches the assigned exchange or not
        if ((priceCurrency != null) && (exchange != null) &&
                !SQUtil.isBlank(parsedSymbol.currencyCode) &&
                !parsedSymbol.currencyCode.equals(exchange.getCurrencyCode())) {
          // the currency override does not match the assigned exchange's currency
          buildCurrencyMismatchMessage(entry, parsedSymbol.currencyCode, exchange);
        } // price currency defined
        // now if no other messages already exist, show the currency message
        if (SQUtil.isBlank(entry.testResult)) {
          setPriceCurrencyMessage(entry, currencyCode, priceCurrency);
        }
      } // no exchange override
    }
  }

  private void setPriceCurrencyMessage(SecurityEntry entry, String currencyCode, CurrencyType priceCurrency) {
    if (priceCurrency != null) {
      // show the success message and display what price currency is being used
      entry.testResult = MessageFormat.format(
              _model.getResources().getString(L10NStockQuotes.PRICE_CURRENCY_FMT),
              getCurrencyAbbreviatedDisplay(priceCurrency));
    } else {
      // the currency code is either invalid or blank
      buildInvalidPriceCurrencyMessage(entry, currencyCode);
    }
  }

  private void buildCurrencyMismatchMessage(SecurityEntry entry, String currencyCode, StockExchange exchange) {
    CurrencyType overrideCurrency = SQUtil.isBlank(currencyCode) ? null :
            _model.getBook().getCurrencies().getCurrencyByIDString(currencyCode);
    CurrencyType exchangeCurrency = (exchange == null) ? null :
            _model.getBook().getCurrencies().getCurrencyByIDString(exchange.getCurrencyCode());
    if ((overrideCurrency == null) || (exchangeCurrency == null)) {
      // missing one or both currencies, so just show the codes
      StringBuilder sb = new StringBuilder(N12EStockQuotes.HTML_BEGIN);
      sb.append(N12EStockQuotes.RED_FONT_BEGIN);
      sb.append(MessageFormat.format(
              _model.getResources().getString(L10NStockQuotes.CURRENCY_CODE_MISMATCH_FMT),
              SQUtil.isBlank(currencyCode) ? "''" : currencyCode,
              (exchange == null) ? "''" : exchange.getCurrencyCode()));
      sb.append(N12EStockQuotes.FONT_END);
      sb.append(N12EStockQuotes.HTML_END);
      entry.testResult = sb.toString();
    } else {
      // we can display both currencies
      StringBuilder sb = new StringBuilder(N12EStockQuotes.HTML_BEGIN);
      sb.append(N12EStockQuotes.RED_FONT_BEGIN);
      sb.append(MessageFormat.format(
              _model.getResources().getString(L10NStockQuotes.CURRENCY_MISMATCH_FMT),
              getCurrencyAbbreviatedDisplay(overrideCurrency),
              getCurrencyAbbreviatedDisplay(exchangeCurrency)));
      sb.append(N12EStockQuotes.FONT_END);
      sb.append(N12EStockQuotes.HTML_END);
      entry.testResult = sb.toString();
    }
  }

  private void buildInvalidPriceCurrencyMessage(SecurityEntry entry, String currencyCode) {
    if (SQUtil.isBlank(currencyCode)) {
      // the currency code isn't specified
      StringBuilder sb = new StringBuilder(N12EStockQuotes.HTML_BEGIN);
      sb.append(N12EStockQuotes.RED_FONT_BEGIN);
      sb.append(_model.getResources().getString(L10NStockQuotes.CURRENCY_UNDEFINED));
      sb.append(N12EStockQuotes.FONT_END);
      sb.append(N12EStockQuotes.HTML_END);
      entry.testResult = sb.toString();
    } else {
      // we have a currency code but it isn't defined in the data file
      StringBuilder sb = new StringBuilder(N12EStockQuotes.HTML_BEGIN);
      sb.append(N12EStockQuotes.RED_FONT_BEGIN);
      sb.append(MessageFormat.format(
              _model.getResources().getString(L10NStockQuotes.CURRENCY_NOT_FOUND_FMT),
              currencyCode));
      sb.append(N12EStockQuotes.FONT_END);
      sb.append(N12EStockQuotes.HTML_END);
      entry.testResult = sb.toString();
    }
  }

  private static String getCurrencyAbbreviatedDisplay(CurrencyType currencyType) {
    String result = currencyType.getPrefix();
    if (!SQUtil.isBlank(result)) return result;
    result = currencyType.getSuffix();
    if (!SQUtil.isBlank(result)) return result;
    return currencyType.getIDString();
  }

  private SecurityEntry getEntryByCurrency(final CurrencyType currency) {
    for (SecurityEntry entry : _data) {
      if (currency.equals(entry.currency)) return entry;
    }
    return null;
  }

  private void addAccount(Account account) {
    final CurrencyType currency = account.getCurrencyType();
    if (currency == null) return; // nothing to do
    _model.addSecurity(account, currency);
    SecurityEntry entry = getEntryByCurrency(currency);
    long balance = account.getBalance();
    if ((balance == 0) && !_showZeroBalance) return; // nothing to do
    if (entry == null) {
      entry = new SecurityEntry();
      entry.currency = currency;
      entry.editSymbol = currency.getTickerSymbol();
      // build or rebuild the symbol map if there is no match
      if (_model.getSymbolMap().hasCurrency(currency)) {
        entry.exchangeId = _model.getSymbolMap().getExchangeIdForCurrency(currency);
        entry.use = _model.getSymbolMap().getIsCurrencyUsed(currency);
      } else {
        // add a new security to the map, clearing the 'use' flag if it is zero balance
        entry.exchangeId = _model.getSymbolMap().addCurrency(currency);
        entry.use = (balance != 0) && _model.getSymbolMap().getIsCurrencyUsed(currency);
      }
      _data.add(entry);
    }
    entry.shares += balance;
  }

  void setShowZeroBalance(boolean showZeroBalance) {
    _showZeroBalance = showZeroBalance;
    load();
  }

  boolean getShowZeroBalance() {
    return _showZeroBalance;
  }

  /**
   * Refresh a single row in the table, or refresh all rows, on the Event Data/UI Thread.
   * @param rowIndex The row to update, or -1 to update all rows.
   */
  void refreshRow(final int rowIndex) {
    UiUtil.runOnUIThread(new Runnable() {
      public void run() {
        if (rowIndex < 0) {
          fireTableDataChanged();
        } else {
          fireTableRowsUpdated(rowIndex, rowIndex);
        }
      }
    });
  }

  boolean allSymbolsEnabled() {
    for (final SecurityEntry entry : _data) {
      if (!entry.use) return false;
    }
    return true;
  }

  boolean anySymbolEnabled() {
    for (final SecurityEntry entry : _data) {
      if (entry.use) return true;
    }
    return false;
  }

  void enableAllSymbols(final boolean use) {
    for (final SecurityEntry entry : _data) {
      if (entry.use != use) _model.setDirty();
      entry.use = use;
    }
    fireTableDataChanged();
  }

  void batchChangeExchange(final StockExchange newExchange) {
    if (newExchange == null) return;
    final String exchangeId = newExchange.getExchangeId();
    if (SQUtil.isBlank(exchangeId)) return;
    for (final SecurityEntry entry : _data) {
      if (!exchangeId.equals(entry.exchangeId)) _model.setDirty();
      entry.exchangeId = exchangeId;
      stripExchangeOverrides(entry);
    }
    fireTableDataChanged();
  }

  /**
   * See if the symbol has any overrides for the exchange and/or currency and remove them, leaving
   * only the symbol itself. 
   * @param entry Table entry to check for overrides.
   * @return True if the ticker symbol has changed, false if it was left the same.
   */
  private boolean stripExchangeOverrides(SecurityEntry entry) {
    SymbolData parsedSymbol = SQUtil.parseTickerSymbol(entry.currency);
    if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) {
      entry.testResult = _model.getResources().getString(L10NStockQuotes.INVALID_SYMBOL);
      return false;
    }
    boolean changed = (parsedSymbol.symbol.compareTo(entry.editSymbol) != 0);
    if (changed) {
      entry.editSymbol = parsedSymbol.symbol;
      entry.testResult = _model.getResources().getString(L10NStockQuotes.MODIFIED);
    }
    return changed;
  }

  class SecurityEntry implements Comparable<SecurityEntry> {
    CurrencyType currency;
    long shares = 0;
    boolean use = true;
    String editSymbol;
    String exchangeId;
    String testResult;
    String toolTip;

    /**
     * Sort alphabetically by the display name of the currency.
     * @param other The other object to compare to.
     * @return Less than zero if less than, zero if equal, greater than zero if greater than other.
     */
    public int compareTo(SecurityEntry other) {
      return currency.getName().compareTo(other.currency.getName());
    }
  }

}
