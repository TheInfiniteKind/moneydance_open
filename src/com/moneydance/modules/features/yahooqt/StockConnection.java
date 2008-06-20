package com.moneydance.modules.features.yahooqt;

import com.moneydance.util.*;
import java.net.*;
import java.io.*;
import java.util.*;

/** Class used to download currency histories via HTTP using the
    same spreadsheet format as at chart.yahoo.com. */
public class StockConnection {
  //private static final String HISTORY_BASE_URL = "http://table.finance.yahoo.com/table.csv";
  private static final String HISTORY_BASE_URL = "http://ichart.finance.yahoo.com/table.csv";
  // history query string: s=AAPL&d=2&e=28&f=2007&g=d&a=6&b=9&c=1986&ignore=.csv
  
  //private static final String CURRENT_BASE_URL = "http://quote.yahoo.com/d/quotes.csv";
  private static final String CURRENT_BASE_URL = "http://finance.yahoo.com/d/quotes.csv";
  
  private static final String NEWLINE = "\r\n";
  private static final Hashtable MONTH_TABLE = new Hashtable();
  private static final Hashtable MKT_CURR_TABLE = new Hashtable();
  static boolean DEBUG = false;
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

    // from http://help.yahoo.com/help/us/fin/quote/quote-19.html
    MKT_CURR_TABLE.put("A", "USD"); // usa
    MKT_CURR_TABLE.put("B", "USD");
    MKT_CURR_TABLE.put("O", "USD");
    MKT_CURR_TABLE.put("N", "USD");
    MKT_CURR_TABLE.put("OB", "USD");
    MKT_CURR_TABLE.put("L", "GBP"); // great britain
    MKT_CURR_TABLE.put("VI", "EUR"); // austria
    MKT_CURR_TABLE.put("AX", "AUD"); // australia
    MKT_CURR_TABLE.put("M", "CAD"); // canada
    MKT_CURR_TABLE.put("TO", "CAD");
    MKT_CURR_TABLE.put("V", "CAD"); 
    MKT_CURR_TABLE.put("SS", "CNY"); // china
    MKT_CURR_TABLE.put("SZ", "CNY");
    MKT_CURR_TABLE.put("CO", "DKK"); // denmark 
    MKT_CURR_TABLE.put("PA", "EUR");
    MKT_CURR_TABLE.put("BE", "EUR"); // germany
    MKT_CURR_TABLE.put("BM", "EUR");
    MKT_CURR_TABLE.put("D", "EUR");
    MKT_CURR_TABLE.put("F", "EUR");
    MKT_CURR_TABLE.put("H", "EUR");
    MKT_CURR_TABLE.put("HA", "EUR");
    MKT_CURR_TABLE.put("HK", "HKD");
    MKT_CURR_TABLE.put("MU", "EUR");
    MKT_CURR_TABLE.put("SG", "EUR");
    MKT_CURR_TABLE.put("DE", "EUR");
    MKT_CURR_TABLE.put("BR", "EUR");  // Brussels
    MKT_CURR_TABLE.put("AS", "EUR");  // Amsterdam

    MKT_CURR_TABLE.put("MI", "EUR"); // italy
    MKT_CURR_TABLE.put("MX", "MXP"); // mexico
    MKT_CURR_TABLE.put("NZ", "NZD"); // new zealand
    MKT_CURR_TABLE.put("OL", "NOK"); // norway
    MKT_CURR_TABLE.put("BC", "EUR"); // spain
    MKT_CURR_TABLE.put("BI", "EUR");
    MKT_CURR_TABLE.put("MF", "EUR");
    MKT_CURR_TABLE.put("MC", "EUR");
    MKT_CURR_TABLE.put("MA", "EUR");
    MKT_CURR_TABLE.put("ST", "SEK"); // sweden
    MKT_CURR_TABLE.put("TWO", "TWD"); // taiwan
    MKT_CURR_TABLE.put("TW", "TWD");
    MKT_CURR_TABLE.put("BK", "THB"); // thailand
    MKT_CURR_TABLE.put("CR", "VEB"); // venezuela
    MKT_CURR_TABLE.put("SA", "BRL"); // Brazil
    MKT_CURR_TABLE.put("NS", "INR"); // India - National Stock Exchange
    MKT_CURR_TABLE.put("BO", "INR"); // India - Bombay Stock Exchange
    MKT_CURR_TABLE.put("CL", "INR"); // India - Calcutta Stock Exchange
    /* Euro countries
         Belgium
         Greece
         Spain
         France
         Ireland
         Italy
         Luxembourg
         The Netherlands
         Austria
         Portugal
         Finland
    */
  }
  
  private static final String getYahooSymbol(String tickerSymbol) {
    int periodIdx = tickerSymbol.lastIndexOf('.');
    if(periodIdx>0) {
      int dashIdx = tickerSymbol.indexOf('-', periodIdx);
      if(dashIdx>0) {
        return tickerSymbol.substring(0, dashIdx);
      }
    }
    return tickerSymbol;
  }
  
  private static final String getCurrencyForSymbol(String tickerSymbol) {
    int periodIdx = tickerSymbol.lastIndexOf('.');
    String market = null;
    if(periodIdx>0) {
      String marketID = tickerSymbol.substring(periodIdx+1);
      String currID = "USD";
      if(marketID.indexOf("-")>=0) {
        // the currency ID was encoded along with the market ID
        return StringUtils.fieldIndex(marketID, '-', 1);
      }
      Object currObj = MKT_CURR_TABLE.get(marketID);
      if(currObj!=null)
        return (String)currObj;
      return currID;
    }
    return "USD";
  }
  
  private static final double getMultiplierForSymbol(String tickerSymbol) {
    if(tickerSymbol.endsWith(".L")) {
      return 0.01;
    }
    return 1.0;
  }
  
  /** Retrieve the history for the given stock ticker.  The history
    * ends on the given date and includes the previous numDays days. */
  public StockHistory getHistory(String tickerSymbol, long endDate, int numDays)
    throws Exception
  {
    if(tickerSymbol==null) return null;
    tickerSymbol = tickerSymbol.toUpperCase().trim();
    if(tickerSymbol.length()<=0) return null;
    
    String currency = getCurrencyForSymbol(tickerSymbol);
    tickerSymbol = getYahooSymbol(tickerSymbol);
    double priceMultiplier = getMultiplierForSymbol(tickerSymbol);

    Calendar cal = Calendar.getInstance();
    cal.setTime(new Date(endDate));
    int ed = cal.get(Calendar.DAY_OF_MONTH);
    int em = cal.get(Calendar.MONTH);
    int ey = cal.get(Calendar.YEAR);
    cal.add(Calendar.DATE, -numDays);
    int sd = cal.get(Calendar.DAY_OF_MONTH);
    int sm = cal.get(Calendar.MONTH);
    int sy = cal.get(Calendar.YEAR);

    // s=AAPL&d=2&e=28&f=2007&g=d&a=6&b=9&c=1986&ignore=.csv (new)
    // s=AAPL&a=03&b=7&c=2004&d=04&e=10&f=2004&g=d&ignore=.csv
    String urlStr = HISTORY_BASE_URL +'?';
    urlStr += "s="+URLEncoder.encode(tickerSymbol); // symbol
    urlStr += "&d="+em;  // ending month
    urlStr += "&e="+ed;  // ending day
    urlStr += "&f="+ey;  // ending year
    urlStr += "&g=d";  // interval (d=daily, w=weekly, m=monthly, d=dividends(?)
    urlStr += "&a="+sm;  // starting month
    urlStr += "&b="+sd;  // starting day
    urlStr += "&c="+sy;  // starting year
    urlStr += "&ignore=.csv"; // response format
    
    if(DEBUG) System.err.println("history: "+urlStr);
    URL url = new URL(urlStr);
    HttpURLConnection urlConn = (HttpURLConnection)url.openConnection();
    int respCode = urlConn.getResponseCode();
    if(respCode<200 || respCode >= 300) {
      throw new Exception("Received response code "+respCode+" and message '"+
                          urlConn.getResponseMessage()+"' when querying "+
                          tickerSymbol);
    }
    
    //System.err.println("Sending request: "+urlStr);
    BufferedReader in =
      new BufferedReader(new InputStreamReader(url.openStream(), "UTF8"));
    
    // read the message...
    boolean gotLine = false;
    Vector records = new Vector();
    while(true) {
      String line = in.readLine();
      if(line==null)
        break;
      if(!gotLine) { // this is the header/title line...
        gotLine = true;
        continue;
      }
      line = line.trim();
      if(line.startsWith("<!--")) continue;
      if(line.endsWith("-->")) continue;
      if(line.startsWith("Date,Open")) continue;

      if(DEBUG) System.err.println(">yahooqt>"+tickerSymbol+">: "+line);

      String dtStr = StringUtils.fieldIndex(line,',',0).trim();
      String openStr = StringUtils.fieldIndex(line,',',1).trim();
      String highStr = StringUtils.fieldIndex(line,',',2).trim();
      String lowStr = StringUtils.fieldIndex(line,',',3).trim();
      String closeStr = StringUtils.fieldIndex(line,',',4).trim();
      String volumeStr = StringUtils.fieldIndex(line,',',5).trim();
      
      char dtDelim = '-';
      if(dtStr.indexOf('-')>0)
        dtDelim = '-';
      else if(dtStr.indexOf('/')>0)
        dtDelim = '/';
      else if(dtStr.indexOf('.')>0)
        dtDelim = '.';
      String yearStr = StringUtils.fieldIndex(dtStr,dtDelim,0).trim();
      String monthStr = StringUtils.fieldIndex(dtStr,dtDelim,1).trim();
      String dayStr = StringUtils.fieldIndex(dtStr,dtDelim,2).trim();
      
      if(closeStr.length()<=0) {
        closeStr = StringUtils.fieldIndex(line,',',1).trim();
      }

      try {
        StockRecord record = new StockRecord();
        cal.set(Calendar.DAY_OF_MONTH, Integer.parseInt(dayStr));
        cal.set(Calendar.MONTH, Integer.parseInt(monthStr)-1);
        int year = Integer.parseInt(yearStr);
        if(year<50)
          year += 2000;
        else if(year<200)
          year += 1900;
        cal.set(Calendar.YEAR, year);
        
        if(highStr.trim().endsWith("%") || openStr.trim().endsWith("%") ||
           lowStr.trim().endsWith("%") || closeStr.trim().endsWith("%")) {
          // ignore bond/MMkt percentages
          continue;
        }
        
        record.date = cal.getTime().getTime();
        if(volumeStr.length()>0)
          record.volume = Long.parseLong(volumeStr);
        if(highStr.length()>0)
          record.high = priceMultiplier * StringUtils.parseRate(highStr, '.');
        if(lowStr.length()>0)
          record.low = priceMultiplier * StringUtils.parseRate(lowStr, '.');
        if(openStr.length()>0)
          record.open = priceMultiplier * StringUtils.parseRate(openStr, '.');
        if(closeStr.length()>0)
          record.close = priceMultiplier * StringUtils.parseRate(closeStr, '.');
        if(record.close!=0)
          records.addElement(record);
      } catch (Exception e) {
        //System.err.println("Error parsing line: "+e);
      }
    }

    StockRecord recordArray[] = new StockRecord[records.size()];
    for(int i=0; i<recordArray.length; i++)
      recordArray[i] = (StockRecord)records.elementAt(i);

    return new StockHistory(currency, recordArray);
  }
  
  /** Retrieve the current information for the given stock ticker symbol.
  */
  public StockPrice getCurrentPrice(String tickerSymbol)
    throws Exception
  {
    tickerSymbol = tickerSymbol.toUpperCase().trim();
    if(tickerSymbol.length()<=0) return null;
    
    String currency = getCurrencyForSymbol(tickerSymbol);
    tickerSymbol = getYahooSymbol(tickerSymbol);
    double priceMultiplier = getMultiplierForSymbol(tickerSymbol);

    String urlStr = CURRENT_BASE_URL +'?';
    urlStr += "s="+URLEncoder.encode(tickerSymbol); // symbol
    urlStr += "&f=sl1d1t1c1ohgv";  // format of each line
    urlStr += "&e=.csv";  // response format

    if(DEBUG) System.err.println("current: "+urlStr);
    URL url = new URL(urlStr);
    
    BufferedReader in =
      new BufferedReader(new InputStreamReader(url.openStream(),"UTF8"));

    // read the message...
    Calendar cal = Calendar.getInstance();
    Vector records = new Vector();
    double price = -1;
    StockPrice record = null;
    while(true) {
      String line = in.readLine();
      if(line==null)
        break;
      line = line.trim();

      String closeStr = StringUtils.fieldIndex(line,',',1).trim();

      if(closeStr.endsWith("%")) //no value provided, but there is a percentage (mutual funds)
        continue;
      if(closeStr.length()>0)
        price = StringUtils.parseRate(closeStr, '.');
      if(price!=1.0)
        price *= priceMultiplier;
      
      if(DEBUG) System.err.println(">>yahooqt>"+tickerSymbol+">"+closeStr+">"+price);

      record = new StockPrice(currency, price);
      
      String dtStr = StringUtils.fieldIndex(line,',',2).trim();
      while(dtStr.endsWith("\""))  dtStr = dtStr.substring(0, dtStr.length()-1);
      while(dtStr.startsWith("\"")) dtStr = dtStr.substring(1);
      char dtDelim = '-';
      if(dtStr.indexOf('-')>0)
        dtDelim = '-';
      else if(dtStr.indexOf('/')>0)
        dtDelim = '/';
      else if(dtStr.indexOf('.')>0)
        dtDelim = '.';

      try {
        String monthStr = StringUtils.fieldIndex(dtStr,dtDelim,0).trim();
        String dayStr = StringUtils.fieldIndex(dtStr,dtDelim,1).trim();
        String yearStr = StringUtils.fieldIndex(dtStr,dtDelim,2).trim();
        cal.set(Calendar.DAY_OF_MONTH, Integer.parseInt(dayStr));
        cal.set(Calendar.MONTH, Integer.parseInt(monthStr)-1);
        int year = Integer.parseInt(yearStr);
        if(year<50)
          year += 2000;
        else if(year<200)
          year += 1900;
        cal.set(Calendar.YEAR, year);
        record.date = cal.getTime().getTime();
      } catch (Exception e) {
        System.err.println("Error parsing price date: "+e);
      }
    }
    return record;
  }
  
  public class StockHistory {
    private String baseCurrency;
    private StockRecord records[];

    StockHistory(String baseCurrency, StockRecord records[]) {
      this.baseCurrency = baseCurrency;
      this.records = records;
    }

    public String getCurrency() {
      return this.baseCurrency;
    }
    
    public int getRecordCount() {
      return records==null ? 0 : records.length;
    }

    public StockRecord getRecord(int i) {
      return records[i];
    }
  }

  public class StockPrice {
    private String baseCurrency;
    private double price;
    private long date = 0;

    StockPrice(String baseCurrency, double price) {
      this.baseCurrency = baseCurrency;
      this.price = price;
    }

    public String getCurrency() {
      return this.baseCurrency;
    }
    
    public double getPrice() {
      return this.price;
    }

    public long getDate() {
      return this.date;
    }
    
    public String toString() {
      return ""+price+" "+baseCurrency+" "+(new Date(date));
    }
  }

  public class StockRecord {
    public long date = 0;
    public long volume = 0;
    public double high = -1.0;
    public double low = -1.0;
    public double open = -1.0;
    public double close = -1.0;

    public String toString() {
      return "close="+close+"; volume="+volume+"; high="+high+"; low="+low+"; date="+(new Date(date));
    }
  }
  
  
  public static void main(String argv[])
    throws Exception
  {
    StockConnection.DEBUG = true;
    StockConnection c = new StockConnection();
    
    for(int i=0; i<argv.length; i++) {
      System.err.println("\n\nGetting rate for: "+argv[i]);
      StockHistory history = c.getHistory(argv[i], System.currentTimeMillis(), 60);
      for(int j=0; history!=null && j<history.getRecordCount(); j++) {
        System.err.println(" >> "+history.getRecord(j));
      }
      
      System.err.println("current: "+c.getCurrentPrice(argv[i]));
    }
  }

  

}





