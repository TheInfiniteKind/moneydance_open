package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.modules.features.moneyPie.UnsafeAccessor;

/**
 * The DownloadModel is where we handle common functions such as parsing ticker symbols and other
 * things that are common to most currency or security downloads but can be tweaked by specific 
 * connections.
 */
public class DownloadModel {
  
  private final StockQuotesModel model;
  private final BaseConnection connection;
  
  DownloadModel(StockQuotesModel model, BaseConnection connection) {
    this.model = model;
    this.connection = connection;
  }

  StockQuotesModel getQuotesModel() {
    return model;
  }
  
  /** Get the AccountBook containing the securities and currencies to update. */
  public AccountBook getBook() {
    return model.getBook();
  }
  
  /** Get available resources - strings, images, etc */
  public ResourceProvider getResources() {
    return model.getResources();
  }
  
  
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
  public StockExchange getExchangeForSecurity(SymbolData symbol, CurrencyType securityCurrency) {
    if (!SQUtil.isBlank(symbol.prefix)) {
      // check for a Google prefix override
      StockExchange result = model.getExchangeList().findByGooglePrefix(symbol.prefix);
      if (result != null) return result;
    }
    if (!SQUtil.isBlank(symbol.suffix)) {
      // check for a Yahoo exchange suffix override
      StockExchange result = model.getExchangeList().findByYahooSuffix(symbol.suffix);
      if (result != null) return result;
    }
    // go with the exchange the user assigned to the security
    return model.getSymbolMap().getExchangeForCurrency(securityCurrency);
  }


  public String getFullTickerSymbol(SymbolData symbolData, StockExchange exchange) {
    return connection.getFullTickerSymbol(symbolData, exchange);
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
  public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange) {
    if (SQUtil.isBlank(rawTickerSymbol)) return null;

    String connectionSpecificCode = connection.getCurrencyCodeForQuote(rawTickerSymbol, exchange);
    if (!SQUtil.isBlank(connectionSpecificCode)) return connectionSpecificCode;
    
    if (SQUtil.isBlank(rawTickerSymbol)) return null;
    // check if this symbol overrides the exchange and the currency code
    int periodIdx = rawTickerSymbol.lastIndexOf('.');
    if(periodIdx>0) {
      String marketID = rawTickerSymbol.substring(periodIdx+1);
      if(marketID.contains("-")) {
        // the currency ID was encoded along with the market ID
        return StringUtils.fieldIndex(marketID, '-', 1);
      }
    }
    return exchange.getCurrencyCode();
  }


  public UserPreferences getPreferences() {
    return model.getPreferences();
  }

  public char getDecimalDisplayChar() {
    return model.getDecimalDisplayChar();
  }

  public void showURL(String urlString) {
    model.showURL(urlString);
  }

  public void beep() {
    try {
      model.getGUI().beep();
    } catch (Throwable t) {
      System.err.println("BEEP!");
    }
  }
  
  public void showProgress(float progressPercent, String message) {
    model.showProgress(progressPercent, message);
  }
}
