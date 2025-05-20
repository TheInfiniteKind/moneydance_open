/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.util.DateUtil.incrementDate
import com.infinitekind.util.DateUtil
import com.infinitekind.util.StringUtils.fieldIndex
import com.infinitekind.util.StringUtils.isEmpty
import com.infinitekind.util.StringUtils.parseRate
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import org.jsoup.Jsoup
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.regex.Pattern
import kotlin.math.max

/**
 * Class for downloading security prices from FT
 */
class FTConnection private constructor(model: StockQuotesModel) : BaseConnection("ft", model, HISTORY_SUPPORT) {
  override fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String? {
    if ((parsedSymbol == null) || isBlank(parsedSymbol.symbol)) return null
    // check if the exchange was already added on, which will override the selected exchange
    if (!isBlank(parsedSymbol.suffix)) {
      return parsedSymbol.symbol + parsedSymbol.suffix
    }
    // Check if the selected exchange has a Yahoo suffix or not. If it does, add it.
    val suffix = exchange?.symbolYahoo
    if (suffix==null || isBlank(suffix)) return parsedSymbol.symbol
    return parsedSymbol.symbol + suffix
  }
  
  override fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange?): String? {
    if (isBlank(rawTickerSymbol)) return null
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
  
  override fun updateExchangeRate(downloadInfo: DownloadInfo) {
    downloadInfo.recordError("Implementation error: FT does not offer exchange rates")
  }
  
  
  override fun updateSecurities(securitiesToUpdate: List<DownloadInfo>): Boolean {
    // TODO: if there's any initialisation step, that goes here before updateSecurity() is invoked for each individual security
    
    return super.updateSecurities(securitiesToUpdate)
  }
  
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  public override fun updateSecurity(downloadInfo: DownloadInfo) {
    QER_LOG.log("ft: updating security: " + downloadInfo.fullTickerSymbol)
    val today = DateUtil.strippedDateInt
    val history = downloadInfo.security.snapshots
    var firstDate = incrementDate(today, 0, -6, -0)
    if (history.size > 0) {
      firstDate = max(history[history.size - 1].dateInt, firstDate)
    }
    
    val decimal: Char = model.preferences.getDecimalChar()
    
    val urlStr = ftSecURL + "?s=" + downloadInfo.fullTickerSymbol
    try {
      val connection = URL(urlStr.trim()).openConnection()
      if (connection is HttpURLConnection) {
        val httpConn = connection
        val responseCode = httpConn.responseCode
        if (responseCode >= 200 && responseCode < 300) {
          analyseResponse(httpConn, downloadInfo)
        } else {
          downloadInfo.recordError("Unsuccessful response from FT server: " + responseCode + " " + httpConn.responseMessage)
          return
        }
      } else {
        downloadInfo.recordError("Unexpected connection type $connection")
        return
      }
    } catch (e: IOException) {
      downloadInfo.recordError("Error connectiong to FT: $e")
      return
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
  
  @Throws(IOException::class)
  private fun analyseResponse(response: HttpURLConnection, downloadInfo: DownloadInfo) {
    val results: List<StockRecord> = ArrayList()
    
    try {
      val stream = response.inputStream
      val doc = Jsoup.parse(stream, "UTF-8", "http://localhost")
      
      val crntLoc = doc.selectFirst("div.mod-tearsheet-overview__header")
      val headerItem = crntLoc.select("h1")[0]
      val quoteSection = doc.selectFirst("div.mod-tearsheet-overview__quote")
      
      val listItems = quoteSection.select("li")
      for (item in listItems) {
        // <span class="mod-ui-data-list__label">Price (ccc)</span>
        val cssQueryLabel = "span.mod-ui-data-list__label"
        val label = item.selectFirst(cssQueryLabel) ?: throw IOException("Cannot find $cssQueryLabel")
        var labelText = label.text()
        
        // <span class="mod-ui-data-list__value">price</span>
        val cssQueryValue = "span.mod-ui-data-list__value"
        val value = item.selectFirst(cssQueryValue) ?: throw IOException("Cannot find $cssQueryValue")
        val valueText = value.text()
        
        if (!isEmpty(labelText)) {
          labelText = labelText.trim()
          if (labelText.trim().startsWith("Price")) {
            setPriceAndCurrency(labelText, valueText, downloadInfo)
          } else if (labelText.startsWith("Shares traded")) {
            System.err.println("shares traded: $valueText")
            //setVolume(labelText, valueText, downloadInfo);
          }
        }
      }
      
      
      //findPrice(crntLoc, quotePrice);
      //findDate(crntLoc, quotePrice);
      System.err.println("downloaded record $downloadInfo results: $results")
      
      return
    } catch (e: IOException) {
      throw IOException("Cannot parse FT response for " + downloadInfo + ": " + e.message, e)
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
  
  
  private fun setPriceAndCurrency(labelText: String, valueText: String?, downloadInfo: DownloadInfo) {
    // Price (USD)
    var valueText = valueText
    val patternString = "\\((.*)\\)"
    val pattern = Pattern.compile(patternString)
    val matcher = pattern.matcher(labelText)
    var currencyID: String? = null
    while (matcher.find()) {
      if (currencyID != null) continue
      
      currencyID = matcher.group(1)
      
      val relativeCurrency = downloadInfo.security.book.currencies.getCurrencyByIDString(currencyID)
      if (relativeCurrency != null) {
        downloadInfo.relativeCurrency = relativeCurrency
      }
    }
    
    if (valueText != null) {
      valueText = valueText.trim()
      // FT price is ALWAYS in English format
      System.err.println("FT prices: rate text: '$valueText'")
      val parsedRate = parseRate(valueText, -1.0, '.')
      if (parsedRate > 0) {
        downloadInfo.setRate(parsedRate, System.currentTimeMillis())
      } else {
        downloadInfo.testMessage = "Unable to parse rate: $valueText"
      }
    } else {
      downloadInfo.testMessage = "No price found"
    }
  }
  
  
  private fun setVolume(labelText: String, valueText: String, downloadInfo: DownloadInfo) {
    var multi = 1
    var number = valueText
    if (valueText.endsWith("k")) {
      multi = 1000
      number = valueText.substring(0, valueText.length - 1)
    }
    if (valueText.endsWith("m")) {
      multi = 1000000
      number = valueText.substring(0, valueText.length - 1)
    }
    var tradeVolume = try {
      number.toDouble()
    } catch (e: NullPointerException) {
      0.0
    } catch (e: NumberFormatException) {
      0.0
    }
    val tradeVolumeLong = Math.round(tradeVolume * multi)
    System.err.println("Parsed trade volume/shares to $tradeVolumeLong")
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
  override fun toString(): String {
    return model.resources.getString(connectionID) ?: "??"
  }
  
  companion object {
    private val SNAPSHOT_DATE_FORMAT = SimpleDateFormat("yyyy-MM-dd")
    
    fun getDefaultConnection(model: StockQuotesModel): FTConnection {
      return FTConnection(model)
    }
    
    private const val ftCurrURL = "https://markets.ft.com/data/currencies/tearsheet/summary?"
    private const val ftSecURL = "https://markets.ft.com/data/etfs/tearsheet/historical"
  }
}
