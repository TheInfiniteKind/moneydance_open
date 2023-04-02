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
import com.infinitekind.util.StringUtils;
import org.jsoup.Jsoup;
import org.jsoup.nodes.*;
import org.jsoup.select.Elements;

import java.io.*;
import java.net.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


/**
 * Class for downloading security prices from FT
 */
public class FTConnection extends BaseConnection {
  
  private static final SimpleDateFormat SNAPSHOT_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
  

  private FTConnection(StockQuotesModel model) {
    super("ft", model, HISTORY_SUPPORT);
  }
  
  public static FTConnection getDefaultConnection(StockQuotesModel model) {
    return new FTConnection(model);
  }
  
  public String getFullTickerSymbol(SymbolData parsedSymbol, StockExchange exchange) {
    if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) return null;
    // check if the exchange was already added on, which will override the selected exchange
    if (!SQUtil.isBlank(parsedSymbol.suffix)) {
      return parsedSymbol.symbol + parsedSymbol.suffix;
    }
    // Check if the selected exchange has a Yahoo suffix or not. If it does, add it.
    String suffix = exchange.getSymbolYahoo();
    if (SQUtil.isBlank(suffix)) return parsedSymbol.symbol;
    return parsedSymbol.symbol + suffix;
  }
  
  public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange) {
    if (SQUtil.isBlank(rawTickerSymbol)) return null;
    // check if this symbol overrides the exchange and the currency code
    int periodIdx = rawTickerSymbol.lastIndexOf('.');
    if(periodIdx>0) {
      String marketID = rawTickerSymbol.substring(periodIdx+1);
      if(marketID.indexOf("-")>=0) {
        // the currency ID was encoded along with the market ID
        return StringUtils.fieldIndex(marketID, '-', 1);
      }
    }
    return exchange.getCurrencyCode();
  }

  @Override
  public void updateExchangeRate(DownloadInfo downloadInfo) {
    downloadInfo.recordError("Implementation error: FT does not offer exchange rates");
  }


  @Override
  public boolean updateSecurities(List<DownloadInfo> securitiesToUpdate) {
    
    // TODO: if there's any initialisation step, that goes here before updateSecurity() is invoked for each individual security
    
    return super.updateSecurities(securitiesToUpdate);
  }
  
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  @Override
  public void updateSecurity(DownloadInfo downloadInfo) {
    System.err.println("ft: updating security: "+downloadInfo.fullTickerSymbol);
    int today = DateUtil.getStrippedDateInt();
    List<CurrencySnapshot> history = downloadInfo.security.getSnapshots();
    int firstDate = DateUtil.incrementDate(today, 0, -6, -0);
    if(history!=null && history.size()>0) {
      firstDate = Math.max(history.get(history.size()-1).getDateInt(), firstDate);
    }
    
    char decimal = model.getPreferences().getDecimalChar();
    
    String urlStr = ftSecURL+"s="+downloadInfo.fullTickerSymbol;
    try {
      URLConnection connection = new URL(urlStr.trim()).openConnection();
      if(connection instanceof HttpURLConnection) {
        HttpURLConnection httpConn = (HttpURLConnection)connection;
        int responseCode = httpConn.getResponseCode();
        if(responseCode >= 200 && responseCode < 300) {
          analyseResponse(httpConn, downloadInfo);
        } else {
          downloadInfo.recordError("Unsuccessful response from FT server: "+responseCode+" "+httpConn.getResponseMessage());
          return;
        }
      } else {
        downloadInfo.recordError("Unexpected connection type "+connection);
        return;
      }
      
      
    } catch (IOException e) {
      downloadInfo.recordError("Error connectiong to FT: "+e);
      return;
    }

//    quotePrice=null;
//    if (response.getStatusLine().getStatusCode() == HttpStatus.SC_OK) {
//      try {
//        quotePrice = analyseResponse(response);
//        String doneUrl ="moneydance:fmodule:" + Constants.PROGRAMNAME + ":"+Constants.LOADPRICECMD+"?"+Constants.TIDCMD+"="+tid+"&";
//        if (tickerType == Constants.STOCKTYPE)
//          doneUrl+=Constants.STOCKTYPE;
//        else
//          doneUrl+=Constants.CURRENCYTYPE;
//        doneUrl += "="+ticker+"&p="+String.format("%.8f",quotePrice.getPrice());
//        doneUrl += "&"+Constants.TRADEDATETYPE+"="+quotePrice.getTradeDate();
//        doneUrl += "&"+Constants.TRADECURRTYPE+"="+quotePrice.getCurrency();
//        doneUrl += "&"+Constants.VOLUMETYPE+"="+quotePrice.getVolume();
//        Main.context.showURL(doneUrl);
//        listener.doneReturned(ticker);
//      }
//      catch (IOException e) {
//        debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "error analysing reply "+e.getMessage());
//        sendError();
//      }
//    }
//    else {
//      debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "error returned "+response.getStatusLine().getStatusCode());
//      sendError();
//    }
//
  }

  private static String ftSecURL = "https://markets.ft.com/data/equities/tearsheet/summary?";
  private static String ftCurrURL = "https://markets.ft.com/data/currencies/tearsheet/summary?";
  
  private void analyseResponse(HttpURLConnection response, DownloadInfo downloadInfo)
    throws IOException
  {
    List<StockRecord> results = new ArrayList<>();
    
    try {
      InputStream stream = response.getInputStream();
      Document doc = Jsoup.parse(stream, "UTF-8", "http://localhost");
      
      Element crntLoc = doc.selectFirst("div.mod-tearsheet-overview__header");
      Element headerItem = crntLoc.select("h1").get(0);
      Element quoteSection = doc.selectFirst("div.mod-tearsheet-overview__quote");
      
      Elements listItems = quoteSection.select("li");
      for (Element item : listItems) {
        // <span class="mod-ui-data-list__label">Price (ccc)</span>
        String cssQueryLabel = "span.mod-ui-data-list__label";
        Element label = item.selectFirst(cssQueryLabel);
        if (label == null) {
          throw new IOException("Cannot find " + cssQueryLabel);
        }
        String labelText = label.text();

        // <span class="mod-ui-data-list__value">price</span>
        String cssQueryValue = "span.mod-ui-data-list__value";
        Element value = item.selectFirst(cssQueryValue);
        if (value == null) {
          throw new IOException("Cannot find " + cssQueryValue);
        }
        String valueText = value.text();

        if ( !StringUtils.isEmpty(labelText) ) {
          labelText = labelText.trim();
          if(labelText.trim().startsWith("Price") ) {
            setPriceAndCurrency(labelText, valueText, downloadInfo);
          } else if(labelText.startsWith("Shares traded")) {
            System.err.println("shares traded: "+valueText);
            //setVolume(labelText, valueText, downloadInfo);
          }
        }
      }
      
      //findPrice(crntLoc, quotePrice);
      //findDate(crntLoc, quotePrice);

      System.err.println("downloaded record "+downloadInfo+" results: "+results);
      
      return;
      } catch (IOException e) {
        throw new IOException("Cannot parse FT response for " + downloadInfo +": "+ e.getMessage(), e);
      }

    
    
    
//    
//      Node baseNode = xpath.evaluateExpression("//ul[@class='mod-tearsheet-overview__quote__bar']",
//                                               doc, Node.class);
//      String priceLabel = xpath.evaluateExpression("li[0]/span/[@class='class=mod-ui-data-list__label']",
//                                                   baseNode, String.class);
//      String priceString = xpath.evaluateExpression("li[0]/span/[@class='class=mod-ui-data-list__value']",
//                                                    baseNode, String.class);
//      
//      if(!StringUtils.isEmpty(priceLabel) && !StringUtils.isEmpty(priceString) && priceLabel.strip().equalsIgnoreCase("Price")) {
//        downloadInfo.setRate(StringUtils.parseDouble(priceString.strip(), '.'), DateUtil.getStrippedDate());
//      }
//      
//      String volumeLabel = xpath.evaluateExpression("li[2]/span/[@class='class=mod-ui-data-list__label']",
//                                                    baseNode, String.class);
//      String volumeString = xpath.evaluateExpression("li[2]/span/[@class='class=mod-ui-data-list__value']",
//                                                     baseNode, String.class);
    
      /*
      
      price is parsed from:
       css: div.mod-tearsheet-overview__header
       -> h1
        -> 
      
      
      date is parsed from:
      div.mod-tearsheet-overview__quote
      
       */
      
//    if (recordList.isEmpty()) {
//        DownloadException de = buildDownloadException(downloadInfo, SnapshotImporter.ERROR_NO_DATA);
//        downloadInfo.errors.add(de);
//        return;
//      }
//
//      downloadInfo.addHistoryRecords(recordList);
  }


  private void setPriceAndCurrency(String labelText, String valueText, DownloadInfo downloadInfo) {
    // Price (USD)
    String patternString = "\\((.*)\\)";
    Pattern pattern = Pattern.compile(patternString);
    Matcher matcher = pattern.matcher(labelText);
    String currencyID = null;
    while (matcher.find()) {
      if (currencyID != null) continue;
      
      currencyID = matcher.group(1);
      
      CurrencyType relativeCurrency = downloadInfo.security.getBook().getCurrencies().getCurrencyByIDString(currencyID);
      if(relativeCurrency!=null) {
        downloadInfo.relativeCurrency = relativeCurrency;
      }
    }
    
    if (valueText != null) {
      valueText = valueText.trim();
      // FT price is ALWAYS in English format
      System.err.println("FT prices: rate text: '"+valueText+"'");
      double parsedRate = StringUtils.parseRate(valueText, -1.0, '.');
      if(parsedRate > 0) {
        downloadInfo.setRate(parsedRate, System.currentTimeMillis());
      } else {
        downloadInfo.setTestMessage("Unable to parse rate: "+valueText);
      }
    } else {
      downloadInfo.setTestMessage("No price found");
    }
  }


  private void setVolume(String labelText, String valueText, DownloadInfo downloadInfo) {
    Integer multi=1;
    String number=valueText;
    if (valueText.endsWith("k")) {
      multi = 1000;
      number = valueText.substring(0,valueText.length()-1);
    }
    if (valueText.endsWith("m")) {
      multi = 1000000;
      number = valueText.substring(0,valueText.length()-1);
    }
    double tradeVolume;
    try {
      tradeVolume = Double.parseDouble(number);
    } catch (NullPointerException | NumberFormatException e) {
      tradeVolume = 0.0d;
    }
    long tradeVolumeLong = Math.round(tradeVolume * multi);
    System.err.println("Parsed trade volume/shares to "+tradeVolumeLong);
    //downloadInfo.setVolume(tradeVolumeLong);
  }
  



  //private void findPrice(Element topDiv, QuotePrice quotePrice) throws IOException {
//
//          }

//    private void setVolume(String labelText, String valueText, QuotePrice quotePrice) {
//      Integer multi=1;
//      String number=valueText;
//      if (valueText.endsWith("k")) {
//        multi = 1000;
//        number = valueText.substring(0,valueText.length()-1);
//      }
//      if (valueText.endsWith("m")) {
//        multi = 1000000;
//        number = valueText.substring(0,valueText.length()-1);
//      }
//      Double tradeVolume;
//      try {
//        tradeVolume = Double.parseDouble(number);
//      }
//      catch (NullPointerException | NumberFormatException e) {
//        tradeVolume = 0.0d;
//      }
//      Long tradeVolumeLong = Math.round(tradeVolume * multi);
//      quotePrice.setVolume(tradeVolumeLong);
//    }
//    
//    private void parseDate(Element topDiv, QuotePrice quotePrice) throws IOException {
//      String cssQuery;
//      Date date;
//      cssQuery = "div.mod-disclaimer";
//      Elements dateElement = topDiv.select(cssQuery);
//      if (dateElement == null) {
//        throw new IOException("Cannot find " + cssQuery);
//      }
//      String dateText = dateElement.text();
//      int asof = dateText.indexOf("as of ");
//      if (asof < 0) {
//        throw new IOException("Cannot find 'as of'");
//      }
//      asof += 6;   // length 'as of '
//      String dateString = dateText.substring(asof);
//      SimpleDateFormat simpleFormat = new SimpleDateFormat("MMM dd yyyy HH:ss z");
//      try {
//        date=simpleFormat.parse(dateString);
//      }
//      catch (ParseException e) {
//        simpleFormat = new SimpleDateFormat("MMM dd yyyy'.'");
//        try {
//          date=simpleFormat.parse(dateString);
//        }
//        catch (ParseException e2) {
//          throw new IOException("Trade Date parse error "+e2.getMessage());
//        }
//      }
//      simpleFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssZ");
//      quotePrice.setTradeDate(simpleFormat.format(date));
//    }
  
  public String toString() {
    DownloadModel model = getModel();
    return model==null ? "??" : model.getResources().getString(getConnectionID());
  }
  
}
