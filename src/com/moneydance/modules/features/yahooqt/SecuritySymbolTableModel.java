package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.AccountIterator;
import com.moneydance.apps.md.model.AccountUtil;
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.SecurityAccount;

import javax.swing.table.AbstractTableModel;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

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
  static final int SHARES_COL = 2;
  static final int SYMBOL_COL = 3;
  static final int EXCHANGE_COL = 4;
  static final int TEST_COL = 5;

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
    AccountIterator iter = new AccountIterator(_model.getRootAccount());
    while (iter.hasNext()) {
      Account account = iter.next();
      if (account.getAccountType() == Account.ACCOUNT_TYPE_SECURITY) {
        addAccount((SecurityAccount)account);
      }
    }
    // sort the list alphabetically
    Collections.sort(_data);
    // remove any pre-existing test results and replace with any currency mismatch warnings
    validateCurrencies();
    // notify that we've rebuilt the data
    fireTableDataChanged();
  }

  void save() {
    if (_model.getRootAccount() == null) return;
    AccountIterator iter = new AccountIterator(_model.getRootAccount());
    while (iter.hasNext()) {
      Account account = iter.next();
      if (account.getAccountType() == Account.ACCOUNT_TYPE_SECURITY) {
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
          // update the currency symbol if the user edited it
          String newSymbol = entry.editSymbol == null ? "" : entry.editSymbol.trim();
          String currentSymbol = currency.getTickerSymbol();
          if (!SQUtil.isEqual(newSymbol, currentSymbol)) {
            currency.setTickerSymbol(newSymbol);
          }
        } // if a corresponding entry
      } // if a security account
    } // while iter.hasNext()
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
      case USE_COL: return " ";
      case NAME_COL: return "Security";
      case SHARES_COL: return "Shares";
      case SYMBOL_COL: return "Symbol";
      case EXCHANGE_COL: return "Stock Exchange";
      case TEST_COL: return "Test Result";
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
        if (!SQUtil.isEqual(original, newSymbol)) _model.setDirty();
        break;
      }
      case EXCHANGE_COL: {
        if (aValue instanceof StockExchange) {
          final String original = tableEntry.exchangeId;
          tableEntry.exchangeId = ((StockExchange)aValue).getExchangeId();
          if (!SQUtil.isEqual(original, tableEntry.exchangeId)) _model.setDirty();
        }
        break;
      }
      default: // no other columns editable
    }
  }

  String getToolTip(int rowIndex, int columnIndex) {
    if ((rowIndex < 0) || (rowIndex >= _data.size())) return null;
    final SecurityEntry tableEntry = _data.get(rowIndex);
    if (tableEntry == null) return null;
    if (columnIndex == TEST_COL) return tableEntry.toolTip;
    if (columnIndex == SYMBOL_COL) {
      StockExchange exchange = _model.getExchangeList().getById(tableEntry.exchangeId);
      if (exchange == null) return null;
      BaseConnection connection = _model.getSelectedConnection();
      if (connection == null) return null;
      String fullSymbol = connection.getFullTickerSymbol(tableEntry.editSymbol, exchange);
      return "Symbol: "+fullSymbol; // TODO: translate
    }
    return null;
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

  void validateCurrencies() {
    // reset the test results
    resetTestResults();
    final CurrencyTable currencyTable = _model.getRootAccount().getCurrencyTable();
    for (SecurityEntry entry : _data) {
      StockExchange exchange = _model.getExchangeList().getById(entry.exchangeId);
      if (exchange == null) continue;
      CurrencyType downloadCurrency = currencyTable.getCurrencyByIDString(exchange.getCurrencyCode());
      if (downloadCurrency == null) continue;
      List<Account> unmatchedAccounts = new ArrayList<Account>();
      Set<Account> accountSet = _model.getSecurityAccountSet(entry.currency);
      for (Account investAccount : accountSet) {
        if (!downloadCurrency.equals(investAccount.getCurrencyType())) {
          unmatchedAccounts.add(investAccount);
        }
      }
      // output any warnings
      if (!unmatchedAccounts.isEmpty()) addCurrencyWarning(entry, downloadCurrency, unmatchedAccounts);
    }
  }

  private void addCurrencyWarning(SecurityEntry entry, CurrencyType downloadCurrency,
                                  List<Account> unmatchedAccounts) {
    // build succinct message
    Set<CurrencyType> unmatchedCurrencies = new HashSet<CurrencyType>();
    for (Account investAccount : unmatchedAccounts) unmatchedCurrencies.add(investAccount.getCurrencyType());
    StringBuilder sbMessage = new StringBuilder("<html><font color=\"red\">");
    boolean isFirstInList = true;
    for (CurrencyType unmatchedCurrency : unmatchedCurrencies) {
      if (isFirstInList) {
        isFirstInList = false;
      } else {
        sbMessage.append(", ");
      }
      sbMessage.append(getCurrencyAbbreviatedDisplay(downloadCurrency));
      sbMessage.append(" &#x2260 "); // not equal sign
      sbMessage.append(getCurrencyAbbreviatedDisplay(unmatchedCurrency));
    }
    sbMessage.append("</font></html>");
    entry.testResult = sbMessage.toString();
    // build a tooltip
    StringBuilder sbToolTip = new StringBuilder("<html>");
    String messageFormat = _model.getResources().getString(L10NStockQuotes.CURRENCY_MISMATCH_FMT);
    sbToolTip.append(MessageFormat.format(messageFormat, downloadCurrency.getName()));
    sbToolTip.append("<ul>");
    // comparator available in MD2010 and beyond
    Collections.sort(unmatchedAccounts, AccountUtil.ACCOUNT_NAME_COMPARATOR);
    for (Account account : unmatchedAccounts) {
      sbToolTip.append("<li>");
      sbToolTip.append(account.getFullAccountName());
      sbToolTip.append(" ('");
      sbToolTip.append(account.getCurrencyType().getName());
      sbToolTip.append("')");
      sbToolTip.append("</li>");
    }
    sbToolTip.append("</ul>");
    sbToolTip.append("</html>");
    entry.toolTip = sbToolTip.toString();
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

  private void addAccount(SecurityAccount account) {
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

  /**
   * Refresh a single row in the table, or refresh all rows, on the Event Data/UI Thread.
   * @param rowIndex The row to update, or -1 to update all rows.
   */
  void refreshRow(final int rowIndex) {
    SQUtil.runOnUIThread(new Runnable() {
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
    }
    fireTableDataChanged();
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
