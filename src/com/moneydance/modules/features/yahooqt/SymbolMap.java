/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.util.StreamTable;
import com.moneydance.util.StreamVector;
import com.moneydance.util.StringEncodingException;
import com.moneydance.util.StringUtils;

import java.util.HashMap;
import java.util.Map;

/**
 * Maps a list of currency/security types (each of which has a trading symbol) to their respective
 * stock exchange ID. This map is stored in the data file parameters, because the currency list
 * comes from the currency table, and the table is stored in the data file. Thus each data file
 * can have its own currency list. The symbol-to-exchange map should stay with the currency table.
 * <p/>
 * We do not store this per account, because multiple accounts can link back to the same security,
 * so the stock exchange would have to be a duplicated setting in each account. So we keep the
 * stock exchange setting with the currency which can potentially span accounts.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class SymbolMap {
  private static final String EXCHANGE_MAP_KEY = "symbolExchangeMap";
  private static final String EXCHANGE_LIST_KEY = "exchangeList";
  private static final String CURRENCY_ID_KEY = "currId";
  private static final String EXCHANGE_ID_KEY = "exchId";
  private static final String USE_SYMBOL_KEY = "use";
  private static final boolean DEFAULT_USE = true;
  private static final String DEFAULT_EXCHANGE_ID = StockExchange.DEFAULT.getExchangeId();

  /**
   * The map of CurrencyType.id (kept unique) to a stock exchange ID and whether to download it.
   */
  private final Map<Integer, CurrencyData> _symbolMap = new HashMap<Integer, CurrencyData>();
  /**
   * The catalog of possible stock exchange definitions.
   */
  private final StockExchangeList _exchangeList;

  SymbolMap(final StockExchangeList exchangeList) {
    _exchangeList = exchangeList;
  }

  /**
   * Save the map of currency IDs to the stock exchange in the data file.
   * @param rootAccount The data file root account.
   */
  void saveToFile(RootAccount rootAccount) {
    if (rootAccount == null) return;
    StreamVector exchangeList = new StreamVector();
    for (Integer currencyId : _symbolMap.keySet()) {
      String exchangeId = _symbolMap.get(currencyId).exchangeId;
      if (StockUtil.isBlank(exchangeId) || !_exchangeList.contains(exchangeId)) {
        exchangeId = StockExchange.DEFAULT.getExchangeId();
      }
      StreamTable settings = new StreamTable();
      settings.put(CURRENCY_ID_KEY, currencyId.intValue());
      settings.put(EXCHANGE_ID_KEY, exchangeId);
      settings.put(USE_SYMBOL_KEY, _symbolMap.get(currencyId).use);
      exchangeList.add(settings);
    }
    StreamTable table = new StreamTable();
    table.put(EXCHANGE_LIST_KEY, exchangeList);
    rootAccount.setParameter(EXCHANGE_MAP_KEY, table.writeToString());
  }

  void clear() { _symbolMap.clear(); }
  /**
   * Load the map of currencyIDs to stock exchange from the data file.
   * @param rootAccount The data file root account.
   */
  void loadFromFile(RootAccount rootAccount) {
    if (rootAccount == null) return;
    clear();
    String settings = rootAccount.getParameter(EXCHANGE_MAP_KEY);
    if (StockUtil.isBlank(settings)) return;
    try {
      StreamTable table = new StreamTable();
      table.readFrom(settings);
      StreamVector settingsList = (StreamVector)table.get(EXCHANGE_LIST_KEY);
      if (settingsList == null) {
        System.err.println("Stock quote synchronizer plugin no symbol map found.");
        return;
      }
      for (Object mapPair : settingsList) {
        if (!(mapPair instanceof StreamTable)) continue;
        StreamTable pairTable = (StreamTable)mapPair;
        int currencyId = pairTable.getInt(CURRENCY_ID_KEY, -1);
        if (isValidCurrency(rootAccount, currencyId)) {
          String exchangeId = pairTable.getStr(EXCHANGE_ID_KEY, DEFAULT_EXCHANGE_ID);
          boolean use = pairTable.getBoolean(USE_SYMBOL_KEY, DEFAULT_USE);
          _symbolMap.put(Integer.valueOf(currencyId), new CurrencyData(exchangeId, use));
        }
      }
    } catch (StringEncodingException e) {
      System.err.println("Stock quote synchronizer plugin error reading security to exchange Id map");
    }
  }

  String getExchangeIdForCurrency(CurrencyType currency) {
    final CurrencyData data = _symbolMap.get(Integer.valueOf(currency.getID()));
    if (data == null) return StockExchange.DEFAULT.getExchangeId();
    String exchangeId = data.exchangeId;
    if (StockUtil.isBlank(exchangeId)) return StockExchange.DEFAULT.getExchangeId();
    return exchangeId;
  }

  StockExchange getExchangeForCurrency(CurrencyType currency) {
    final CurrencyData data = _symbolMap.get(Integer.valueOf(currency.getID()));
    if (data == null) return StockExchange.DEFAULT;
    String exchangeId = data.exchangeId;
    if (StockUtil.isBlank(exchangeId)) return StockExchange.DEFAULT;
    return _exchangeList.getById(exchangeId);
  }

  void setExchangeIdForCurrency(CurrencyType currency, String exchangeId) {
    final CurrencyData data = _symbolMap.get(Integer.valueOf(currency.getID()));
    if (data == null) return;
    data.exchangeId = exchangeId;
  }

  boolean getIsCurrencyUsed(CurrencyType currency) {
    final CurrencyData data = _symbolMap.get(Integer.valueOf(currency.getID()));
    if (data == null) return false;
    return data.use;
  }

  void setIsCurrencyUsed(CurrencyType currency, boolean useForDownload) {
    final CurrencyData data = _symbolMap.get(Integer.valueOf(currency.getID()));
    if (data == null) return;
    data.use = useForDownload;
  }

  boolean hasCurrency(CurrencyType currency) {
    return _symbolMap.containsKey(Integer.valueOf(currency.getID()));
  }

  String addCurrency(CurrencyType currency) {
    // assume the currency is valid
    final Integer currencyId = Integer.valueOf(currency.getID());
    _symbolMap.put(currencyId, new CurrencyData(DEFAULT_EXCHANGE_ID, DEFAULT_USE));
    return DEFAULT_EXCHANGE_ID;
  }

  private boolean isValidCurrency(RootAccount rootAccount, int currencyId) {
    CurrencyTable currencyTable = rootAccount.getCurrencyTable();
    if (currencyTable == null) return false;
    return (currencyTable.getCurrencyByID(currencyId) != null);
  }


  private class CurrencyData {
    private String exchangeId = null;
    private boolean use = DEFAULT_USE;

    CurrencyData(String exchangeId, boolean use) {
      this.exchangeId = exchangeId;
      this.use = use;
    }
  }
}
