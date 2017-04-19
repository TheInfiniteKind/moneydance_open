package com.moneydance.modules.features.yahoofx;

import com.infinitekind.util.*;
import java.net.*;
import java.io.*;
import java.util.*;

/** Class used to download currency histories via HTTP using the
    same spreadsheet format as at finance.yahoo.com. */
public class FXConnection {
  private static final String CURRENT_BASE_URL = "https://download.finance.yahoo.com/d/quotes.csv";
  
  // the rest of it: ?s=USDEUR=X&f=sl1d1t1c1ohgv&e=.csv"
  
  private static final String NEWLINE = "\r\n";
  private static final Hashtable MONTH_TABLE = new Hashtable();
  static {
    int month = 0;
    MONTH_TABLE.put("JAN", new Integer(month++));
    MONTH_TABLE.put("FEB", new Integer(month++));
    MONTH_TABLE.put("MAR", new Integer(month++));
    MONTH_TABLE.put("APR", new Integer(month++));
    MONTH_TABLE.put("MAY", new Integer(month++));
    MONTH_TABLE.put("JUN", new Integer(month++));
    MONTH_TABLE.put("JUL", new Integer(month++));
    MONTH_TABLE.put("AUG", new Integer(month++));
    MONTH_TABLE.put("SEP", new Integer(month++));
    MONTH_TABLE.put("OCT", new Integer(month++));
    MONTH_TABLE.put("NOV", new Integer(month++));
    MONTH_TABLE.put("DEC", new Integer(month++));
  }
  
  /** Create a connection object that can retrieve exchange rates */
  public FXConnection() {
  }

  /** Retrieve the current information for the given stock ticker symbol.
  */
  public ExchangeRate getCurrentRate(String currencyID, String baseCurrencyID)
    throws Exception
  {
    currencyID = currencyID.toUpperCase().trim();
    baseCurrencyID = baseCurrencyID.toUpperCase().trim();
    if(currencyID.length()!=3 || baseCurrencyID.length()!=3)
      return null;
    
    String urlStr = CURRENT_BASE_URL +'?';
    urlStr += "s="+URLEncoder.encode(baseCurrencyID + currencyID) + "=X"; // symbol
    urlStr += "&f=sl1d1t1c1ohgv";  // format of each line
    urlStr += "&e=.csv";  // response format

    URL url = new URL(urlStr);
    
    BufferedReader in =
      new BufferedReader(new InputStreamReader(url.openStream(), "ASCII"));

    // read the message...
    Vector records = new Vector();
    double rate = -1;
    while(true) {
      String line = in.readLine();
      if(line==null)
        break;
      line = line.trim();

      String rateStr = StringUtils.fieldIndex(line,',',1).trim();

      if(rateStr.length()>0)
        rate = StringUtils.parseRate(rateStr, '.');
    }
    return new ExchangeRate(currencyID, rate);
  }
  
  public class ExchangeRate {
    private String currencyID;
    private double rate;

    ExchangeRate(String currencyID, double rate) {
      this.currencyID = currencyID;
      this.rate = rate;
    }

    public String getCurrency() {
      return this.currencyID;
    }
    
    public double getRate() {
      return this.rate;
    }
  }

}





