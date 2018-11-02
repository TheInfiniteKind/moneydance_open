package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.DateUtil;
import com.moneydance.util.StringUtils;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathFactory;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;


/**
 * Connection for updating exchange rates from the European Central Bank
 */
public class ECBConnection extends BaseConnection {
  
  public static final String PREFS_KEY = "ecb";
  private static final String FXRATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml";
  
  private DateFormat dateFormat;
  
  public ECBConnection(StockQuotesModel model) {
    super(PREFS_KEY, model, EXCHANGE_RATES_SUPPORT);
    dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    dateFormat.setLenient(true);
  }
  
  /**
   * Alphavantage connections should be throttled to approximately one every 1.1 seconds
   */
  public long getPerConnectionThrottleTime() {
    return 100; // throttle only so we dont exceed 10 requests per second
  }
  

  public String toString() {
    return model==null ? "" : model.getResources().getString("ecb");
  }

  
  /** Update the currencies in the given list */
  @Override
  public boolean updateExchangeRates(List<DownloadInfo> currenciesToUpdate) {
    if(currenciesToUpdate.size()<=0) return true;
    
    // download the page of exchange rates, and update any matching items in currenciesToUpdate
    Document ratesDoc = null;
    try {
      ratesDoc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(FXRATES_URL);
    } catch (Exception e) {
      for(DownloadInfo info : currenciesToUpdate) {
        info.recordError("Enable to retrieve rates from ECB: "+e);
      }
      e.printStackTrace();
      return false;
    }
    
    class ECBRate {
      String currencyID;
      double rate;

      public ECBRate(String currencyID, double rate) {
        this.currencyID = currencyID;
        this.rate = rate;
      }
    }
    
    long rateDateTime = DateUtil.firstMinuteInDay(DateUtil.convertIntDateToLong(DateUtil.getStrippedDateInt())).getTime();
    HashMap<String, Double> rateMap = new HashMap<>();
    
    try {
      XPath xpathLocator = XPathFactory.newInstance().newXPath();
      Node rateTimeNode = (Node) xpathLocator.evaluate("//Cube[@time]", ratesDoc.getDocumentElement(), XPathConstants.NODE);
      if(rateTimeNode!=null) {
        Node dateAttNode = rateTimeNode.getAttributes().getNamedItem("time");
        if(dateAttNode!=null) {
          String dateValue = dateAttNode.getNodeValue();
          if(!StringUtils.isBlank(dateValue)) {
            rateDateTime = DateUtil.firstMinuteInDay(dateFormat.parse(dateValue)).getTime();
            System.err.println("ECB rates date stamp: '"+dateValue+"' parsed to "+(new Date(rateDateTime)));
          }
        }
      }
      NodeList rateNodes =(NodeList)xpathLocator.evaluate("//Cube[@currency]",
                                                          ratesDoc.getDocumentElement(), XPathConstants.NODESET);
      for (int i = 0; i < rateNodes.getLength(); i++) {
        Node rateNode = rateNodes.item(i);
        NamedNodeMap nodeAtts = rateNode.getAttributes();
        Node currencyAttNode = nodeAtts.getNamedItem("currency");
        Node rateAttNode = nodeAtts.getNamedItem("rate");
        if(currencyAttNode!=null && rateAttNode!=null) {
          rateMap.put(currencyAttNode.getNodeValue(), StringUtils.parseDouble(rateAttNode.getNodeValue(), '.'));
        }
      }
    } catch (Exception e) {
      for(DownloadInfo info : currenciesToUpdate) {
        info.recordError("Error parsing response from ECB: "+e);
      }
      e.printStackTrace();
      return false;
    }
    
    System.err.println("Downloaded exchange rates from ECB: "+rateMap);
    
    CurrencyTable currencies = getModel().getBook().getCurrencies();
    CurrencyType baseCurrency = currencies.getBaseType();
    Double baseRateD = rateMap.get(baseCurrency.getIDString());
    if(baseRateD==null) {
      for(DownloadInfo downloadInfo : currenciesToUpdate) {
        downloadInfo.recordError(" error: Couldn't find my base currency ("+baseCurrency.getIDString()+") in ECB exchange rate list");
      }
      return false;
    }
    
    double baseToEuroRate = baseRateD;
    for(DownloadInfo downloadInfo : currenciesToUpdate) {
      String currencyID = downloadInfo.security.getIDString();
      Double rateToEuroD = rateMap.get(currencyID);
      if(currencyID.equalsIgnoreCase("EUR")) { // the currencies are returned relative to the Euro, so this will be 1
        rateToEuroD = 1.0;
      } else if(rateToEuroD==null) {
        downloadInfo.recordError("Couldn't find currency ("+currencyID+") in ECB exchange rate list");
        continue;
      }
      double rateToBase = rateToEuroD / baseToEuroRate;
      System.err.println("new fx rate: "+currencyID+" to "+baseCurrency.getIDString()+
                         " as of "+(new Date(rateDateTime))+"; " +
                         " was "+downloadInfo.security.getUserRate()+" -> "+
                         rateToBase);
      downloadInfo.relativeCurrency = baseCurrency;
      downloadInfo.setRate(rateToBase, rateDateTime);
    }
    
    
    return true;
  }
  
  private static DownloadInfo infoForID(String idString, List<DownloadInfo> downloadInfos) {
    for(DownloadInfo info : downloadInfos) {
      if(idString.equalsIgnoreCase(info.security.getIDString())) {
        return info;
      }
    }
    return null;
  }

  @Override
  public String getFullTickerSymbol(SymbolData parsedSymbol, StockExchange exchange) {
    return null;
  }
  
  @Override
  public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange) {
    return null;
  }
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  public void updateExchangeRate(DownloadInfo downloadInfo) {
    downloadInfo.recordError("Implementation error: IEXTrading does not provide exchange rates");
  }
  
  protected void updateSecurity(DownloadInfo downloadInfo) {
    downloadInfo.recordError("Implementation error: IEXTrading connection should batch requests");
  }
  

  private static double safeInversion(double rate) {
    return rate==0.0 ? 0.0 : 1/rate;
  }


  public static void main(String[] args) throws Exception {
    ECBConnection conn = new ECBConnection(createEmptyTestModel());
    runTests(conn, null, args);
  }


}
