/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.yahooqt.tdameritrade.Candle;
import com.moneydance.modules.features.yahooqt.tdameritrade.History;

import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

/**
 * Stores the result of an attempt to retrieve information for a security or currency
 */
public class DownloadInfo {
  CurrencyType security;
  CurrencyType relativeCurrency; // the currency in which prices are specified by the source
  String fullTickerSymbol;
  StockExchange exchange;
  double priceMultiplier = 1;
  boolean isValidForDownload = false;
  
  boolean skipped = false;
  
  private double rate = 0.0;
  private long dateTimeStamp = 0;
  
  private String testMessage = "";
  String logMessage;
  
  String toolTip;
  String resultText;
  
  List<DownloadException> errors = new ArrayList<>();
  private List<StockRecord> history = new ArrayList<>();
  
  DownloadInfo(CurrencyType security, BaseConnection connection) {
    this.security = security;
    if(connection==null) {
      this.skipped = true;
      return;
    }
    if (security.getCurrencyType() == CurrencyType.Type.SECURITY) {
      initFromSecurity(connection);
    } else {
      initFromCurrency(connection);
    }
  }
  
  private void initFromSecurity(BaseConnection connection) {
    SymbolData symbolData = SQUtil.parseTickerSymbol(security);
    if(symbolData==null) {
      isValidForDownload = false;
      recordError("No ticker symbol for: '" + security);
      return;
    }
    
    exchange = connection.getExchangeForSecurity(symbolData, security);
    if (exchange != null) {
      priceMultiplier = exchange.getPriceMultiplier();
    }
    
    fullTickerSymbol = connection.getFullTickerSymbol(symbolData, exchange);
    if(fullTickerSymbol==null) {
      isValidForDownload = false;
      recordError("No ticker symbol for: '" + security);
      return;
    }
    
    // check for a relative currency embedded in the symbol
    relativeCurrency = security.getBook().getCurrencies().getCurrencyByIDString(symbolData.currencyCode);
    
    // check for a relative currency that is specific to the provider/exchange
    if (relativeCurrency == null) {
      String currID = connection.getCurrencyCodeForQuote(security.getTickerSymbol(), exchange);
      if (!SQUtil.isBlank(currID)) {
        relativeCurrency = security.getBook().getCurrencies().getCurrencyByIDString(currID);
      }
    }
    
    // if there is still no relative currency, look for USD
    if (relativeCurrency == null) {
      relativeCurrency = security.getBook().getCurrencies().getCurrencyByIDString("USD");
    }
    
    // if there is still no relative currency, fail
    if(relativeCurrency==null) {
      isValidForDownload = false;
      recordError("No base currency found for: '" + fullTickerSymbol + "' ");
      return;
    }
    
    // if we're here then we must have a valid symbol
    isValidForDownload = true;
  }

  
  private void initFromCurrency(BaseConnection connection) {
    fullTickerSymbol = security.getIDString();
    relativeCurrency = security.getBook().getCurrencies().getBaseType();
    isValidForDownload = fullTickerSymbol.length()==3 && relativeCurrency.getIDString().length()==3;
    
    if(fullTickerSymbol.equals(relativeCurrency.getIDString())) { // the base currency is always 1.0
      isValidForDownload = false;
      this.rate = 1.0;
      recordError("Base currency rate is a constant 1.0");
    } else if(!isValidForDownload) {
      recordError("Invalid currency symbol: '"+fullTickerSymbol
                  +"' or '"+relativeCurrency.getIDString()+"'");
    }
  }

  void apply() {
    // apply any historical prices
    for (StockRecord record : history) {
      record.apply(security, relativeCurrency);
    }
    
    int dateStampInt = DateUtil.convertLongDateToInt(dateTimeStamp);
    StockRecord mostRecentRecord = findMostRecentValidRecord();
    long localUpdateDate = security.getLongParameter("price_date", 0);
    // apply the current rate, or pull it from the most recent historical price:
    if(rate > 0) {
      security.setUserRate(rate, relativeCurrency);
      security.setParameter("price_date", dateTimeStamp);
      security.syncItem();
      
      if(history.size()<=0) { // if there isn't a history, add one entry with the date of this rate
        double newRate = relativeCurrency.getUserRateByDateInt(dateStampInt)*rate;
        CurrencySnapshot result = security.setSnapshotInt(dateStampInt, newRate);
        //result.setUserDailyHigh(relativeCurrency.getUserRateByDateInt(dateStampInt)*newRate);
        //result.setUserDailyLow(relativeCurrency.getUserRateByDateInt(dateStampInt)*newRate);
        //result.setDailyVolume(volume);
        result.syncItem();
      }
    } else {
      // update the current price if possible and if there are no more recent prices/rates
      if(mostRecentRecord!=null) { // && mostRecentRecord.dateTimeGMT > lastUpdateDate) {
        // the user rate should be stored in terms of the base currency, just like the snapshots
        security.setUserRate(mostRecentRecord.closeRate, relativeCurrency);
        security.setParameter("price_date", mostRecentRecord.dateTimeGMT);
        security.syncItem();
      }
    }
    
    if (!SQUtil.isBlank(logMessage)) {
      // the historical price has a log message already, so just dump the current price update
      // log message now
      if(Main.DEBUG_YAHOOQT) {
        System.err.println("applied updates to "+security);
      }
    }
    
  }
  
  public String toString() { return security.getName(); }
  
  public void setRate(double rate, long dateTimeStamp) { 
    this.rate = rate;
    if(dateTimeStamp<=0) {
      this.dateTimeStamp = DateUtil.firstMinuteInDay(new Date()).getTime();
    } else {
      this.dateTimeStamp = dateTimeStamp;
    }
  }
  
  public double getRate() {
    return this.rate;
  }

  public String getTestMessage() {
    return testMessage;
  }

  public void setTestMessage(String testMessage) {
    this.testMessage = testMessage;
  }

  
  public void addHistoryRecords(List<StockRecord> snapshots) {
    this.history.addAll(snapshots);
  }
  
  public int getHistoryCount() {
    return this.history.size();
  }
  
  public StockRecord findMostRecentValidRecord() {
    Collections.sort(history);
    for (int index = history.size() - 1; index >= 0; index--) {
      StockRecord record = history.get(index);
      if (record.closeRate != 0.0)
        return record;
    }
    return null;
  }
  
  public void buildPriceDisplay(CurrencyType priceCurrency, char decimal) {
    if (history != null) {
      for (StockRecord record : history) {
        record.updatePriceDisplay(priceCurrency, decimal);
      }
    }
  }
  
  public String buildRateDisplayText(StockQuotesModel model) {
    String format = model.getResources().getString(L10NStockQuotes.EXCHANGE_RATE_DISPLAY_FMT);
    // get the currency that the prices are specified in
    long amount = (rate == 0.0) ? 0 : security.getLongValue(1.0 / rate);
    final char decimal = model.getDecimalDisplayChar();
    String priceDisplay = security.formatFancy(amount, decimal);
    String asofDate = model.getUIDateFormat().format(DateUtil.getStrippedDateInt());
    return MessageFormat.format(format, security.getIDString(), relativeCurrency.getIDString(),
                                asofDate, priceDisplay);
  }


  
  public String buildRateLogText(StockQuotesModel model) {
    long amount = (rate == 0.0) ? 0 : security.getLongValue(1.0 / rate);
    String priceDisplay = security.formatFancy(amount, '.');
    String asofDate = model.getUIDateFormat().format(DateUtil.getStrippedDateInt());
    String messageKey = security.getCurrencyType() == CurrencyType.Type.CURRENCY ? 
                        L10NStockQuotes.EXCHANGE_RATE_DISPLAY_FMT :
                        L10NStockQuotes.SECURITY_PRICE_DISPLAY_FMT;
    return MessageFormat.format(model.getResources().getString(messageKey),
                                security.getIDString(),
                                relativeCurrency.getIDString(),
                                asofDate,
                                priceDisplay);
  }
  
  
  public void recordError(String message) {
    errors.add(new DownloadException(this, message));
    if (SQUtil.isBlank(logMessage)) {
      logMessage = message;
    }
  }
  
  
  public boolean wasSuccess() {
    return errors.size()<=0 && (getRate()>0 || history.size()>0); 
  }
  
  /** Create a test result object based on the download result for a security download */
  public void updateResultSummary(StockQuotesModel model) {
    if (skipped) {
      toolTip = "";
      resultText = model.getResources().getString(L10NStockQuotes.TEST_EXCLUDED);
    } else if(security.getCurrencyType() == CurrencyType.Type.CURRENCY) {
      toolTip = "<html><pre>" + getTestMessage() + "</pre></html>";
      StringBuilder sb = new StringBuilder("<html>");
      sb.append(getSuccessIcon(errors.size()<=0)).append(' ');
      sb.append(model.getResources().getString(L10NStockQuotes.HISTORY));
      sb.append("</html>");
      resultText = sb.toString();
    } else { // it's a security
      // we're just counting the number of successful symbols
      
      StringBuilder sb = new StringBuilder("<html><p>");
      sb.append(logMessage);
      sb.append("</p></html>");
      toolTip = sb.toString();
      
      sb = new StringBuilder();
      sb.append("<html>");
      sb.append(getSuccessIcon(wasSuccess()));
      sb.append(" ");
      StockRecord latest = findMostRecentValidRecord();
      if (latest != null) {
        sb.append("latest close: ").append(latest.closeRate);
        sb.append(" on ").append(model.getUIDateFormat().format(latest.date));
      } else {
        sb.append("No history records returned for security ").append(security.getName());
      }
      if (history.size() > 0) {
        sb.append("(");
        sb.append(history.size());
        sb.append(")");
      }
      sb.append("</html>");
      resultText = sb.toString();
    }
  }


  String buildPriceDisplayText(StockQuotesModel model) {
    for (StockRecord record : history) {
      long amount = (record.closeRate == 0.0) ? 0 : relativeCurrency.getLongValue(1.0 / record.closeRate);
      record.priceDisplay = relativeCurrency.formatFancy(amount, model.getDecimalDisplayChar());
    }
    StockRecord latest = findMostRecentValidRecord();
    return MessageFormat.format(model.getResources().getString(L10NStockQuotes.SECURITY_PRICE_DISPLAY_FMT),
                                security.getName(),
                                model.getUIDateFormat().format(DateUtil.getStrippedDateInt()),
                                latest.priceDisplay);
  }
  
  String buildPriceLogText(StockQuotesModel model) {
    boolean haveCurrent = getRate() > 0;
    String asofDate;
    String format;
    double displayRate;
    if (haveCurrent) {
      // the current price can be intra-day, so log the date and time of the price update.
      asofDate = model.getUIDateTimeFormat().format(new Date(dateTimeStamp));
      format = "Current price for {0} as of {1}: {2}";
      displayRate = rate;
    } else {
      asofDate = "?";
      format = "Latest historical price for {0} as of {1}: {2}";
      displayRate = 0.0;
      StockRecord snap = findMostRecentValidRecord();
      if(snap!=null) {
        displayRate = snap.closeRate;
        asofDate = model.getUIDateFormat().format(new Date(snap.dateTimeGMT));
      }
    }
    long amount = (displayRate == 0.0) ? 0 : relativeCurrency.getLongValue(1.0 / displayRate);
    String priceDisplay = relativeCurrency.formatFancy(amount, '.');

    return MessageFormat.format(format, security.getName(), asofDate, priceDisplay);
  }
  
  
  
  public static String getSuccessIcon(boolean success) {
    if (success) {
      return N12EStockQuotes.GREEN_FONT_BEGIN + "&#x2714;" + N12EStockQuotes.FONT_END;
    } else {
      return N12EStockQuotes.RED_FONT_BEGIN + "&#x2716;" + N12EStockQuotes.FONT_END;
    }
  }
  
  public void addHistory(History history)
  {
  	if (history.candles != null)
	{
		history.candles.stream().forEach(candle -> addDayOfData(candle));
	}
  }
  
  private void addDayOfData(Candle candle)
  {
  	history.add(new StockRecord(candle, priceMultiplier));
  }
}
