/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/


package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.Common;
import com.moneydance.util.StreamTable;
import com.moneydance.util.StreamVector;
import com.moneydance.util.StringEncodingException;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Lists the stock market exchanges, their identifiers and currencies. Most of the information is
 * derived from <a href="http://www.wikinvest.com/wiki/List_of_Stock_Exchanges">
 * http://www.wikinvest.com/wiki/List_of_Stock_Exchanges</a> or
 * <a href="http://en.wikipedia.org/wiki/List_of_stock_exchanges">
 * http://en.wikipedia.org/wiki/List_of_stock_exchanges</a>.
 * <p/>
 * Yahoo exchange list is currently here: <a href="https://finance.yahoo.com/exchanges">
 * https://finance.yahoo.com/exchanges</a>. Some stuff was found for Google here:
 * <a href="http://directory.google.com/Top/Business/Investing/Stocks_and_Bonds/Exchanges/">
 * http://directory.google.com/Top/Business/Investing/Stocks_and_Bonds/Exchanges/</a>, however
 * in general it is hard to find good information from Google Finance currently.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class StockExchangeList {
  /** Settings key for loading/saving the list of stock exchanges in settings. */
  public static final String STOCK_EXCHANGES_KEY = "exchangeList";
  private File _configFile = null;
  /**
   * Map of unique key name of exchange (exchange ID) to exchange definition.
   */
  private final Map<String, StockExchange> _exchangeList = new TreeMap<String, StockExchange>();
  
  void load() {
    clear();
    if (getConfigFile()) {
      if (!loadFromFile()) {
        clear();
        getDefaultExchangeTable(); 
      }
    } else {
      getDefaultExchangeTable();
      saveToFile();
    }
  }

  boolean save() {
    boolean success = getConfigFile();
    if (success) success = saveToFile();
    return success;
  }

  boolean contains(final String exchangeId) {
    return _exchangeList.containsKey(exchangeId);
  }

  StockExchange getById(final String exchangeId) {
    StockExchange exchange = _exchangeList.get(exchangeId);
    if (exchange == null) {
      return StockExchange.DEFAULT;
    }
    return exchange;
  }

  List<StockExchange> getFullList() {
    final ArrayList<StockExchange> sortedList = new ArrayList<StockExchange>(_exchangeList.values());
    Collections.sort(sortedList);
    return Collections.unmodifiableList(sortedList);
  }

  StockExchange findByGooglePrefix(String prefix) {
    if (SQUtil.isBlank(prefix)) return null;
    List<StockExchange> matches = new ArrayList<StockExchange>();
    for (StockExchange exchange : _exchangeList.values()) {
      if (prefix.compareTo(exchange.getSymbolGoogle()) == 0) matches.add(exchange);
    }
    if (matches.isEmpty()) return null; // not found
    // if there is more than one match, favor the one that has a price multiplier that is not 1.
    for (StockExchange candidate : matches) {
      if (candidate.getPriceMultiplier() != 1.0) return candidate;
    }
    return matches.get(0);
  }

  StockExchange findByYahooSuffix(String suffix) {
    if (SQUtil.isBlank(suffix)) return null;
    List<StockExchange> matches = new ArrayList<StockExchange>();
    for (StockExchange exchange : _exchangeList.values()) {
      if (suffix.compareTo(exchange.getSymbolYahoo()) == 0) matches.add(exchange);
    }
    if (matches.isEmpty()) return null; // not found
    // if there is more than one match, favor the one that has a price multiplier that is not 1.
    // This makes the .L suffix default to the London Pence exchange, which is more prevalent than
    // the London GBP exchange. If the user really wants London GBP (for example for the symbol
    // SLXX.L), then they will need to specify an exchange instead of relying on a default one
    // using the .L override
    for (StockExchange candidate : matches) {
      if (candidate.getPriceMultiplier() != 1.0) return candidate;
    }
    return matches.get(0);
  }

  /** Remove all stock exchange definitions from memory. */
  private void clear() { _exchangeList.clear(); }

  /**
   * Get a reference to the configuration file storing the list of stock exchange definitions.
   * @return True if the file was successfully opened, false otherwise.
   */
  private boolean getConfigFile() {
    if (_configFile == null) {
      _configFile = new File(Common.getDataRootDirectory(), "stockExchanges.dict");
    }
    return _configFile.exists();
  }

  /**
   * Attempt to save the list of exchanges to the configuration file. This only needs to be done
   * once.
   * @return True if the save succeeded, false otherwise.
   */
  private boolean saveToFile() {
    boolean success = false;
    StreamTable settings = new StreamTable();
    StreamVector exchangeList = new StreamVector();
    for (final StockExchange exchange : _exchangeList.values()) {
      exchangeList.add(exchange.saveToSettings());  
    }
    settings.put(STOCK_EXCHANGES_KEY, exchangeList);
    try {
      settings.writeToFile(_configFile);
      success = true;
    } catch (StringEncodingException e) {
      System.err.println("Stock quote plugin unexpected error writing exchange list file: " +
                         _configFile.getAbsolutePath());
      e.printStackTrace();
    } catch (IOException e) {
      System.err.println("Stock quote synchronizer plugin error writing to file: " +
                         _configFile.getAbsolutePath());
      e.printStackTrace();
    }
    return success;
  }
  
  private boolean loadFromFile() {
    StreamTable settings = new StreamTable();
    try {
      settings.readFromFile(_configFile);
      Object value = settings.get(STOCK_EXCHANGES_KEY);
      if ((value == null) || !(value instanceof StreamVector)) return false;
      StreamVector exchanges = (StreamVector)value;
      if (exchanges.isEmpty()) return false;
      for (Object exchangeSetting : exchanges) {
        if (!(exchangeSetting instanceof StreamTable)) continue;
        StockExchange exchange = new StockExchange();
        exchange.loadFromSettings((StreamTable)exchangeSetting);
        if (_exchangeList.containsKey(exchange.getExchangeId())) {
          System.err.println("Stock quote synchronizer plugin found duplicate stock exchange " +
                             "entry name: "+exchange.getName()+" in file: "+_configFile.getAbsolutePath());
        } else {
          _exchangeList.put(exchange.getExchangeId(), exchange);
        }
      }
      return true;
    } catch (StringEncodingException e) {
      System.err.println("Stock quote synchronizer plugin error reading exchange list file: " +
        _configFile.getAbsolutePath());
    } catch (IOException e) {
      System.err.println("Stock quote synchronizer plugin error reading exchange list file: " +
        _configFile.getAbsolutePath());
    }
    return false;
  }
  
  /**
   * Load a hard-coded list of exchanges because the file doesn't exist. The point of having a file
   * is the user can make edits and things can change in the future. So we build a hard-coded list
   * as of May 2010 but commit it to a file so edits can be made in the future.
   */
  private void getDefaultExchangeTable() {
    final List<StockExchange> exchanges = new ArrayList<StockExchange>();
    // this data is a processed and edited list based upon the www.wikinvest.com page
    exchanges.add(StockExchange.createFromCSV("American Stock Exchange,USD,AMEX,,A,1.0,U.S. Dollar,United States,Eastern Standard Time (EST),-5,,09:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("Amman Stock Exchange,JOD,AFM,,AJ,1.0,Jordanian Dinar,Jordan,Eastern European Time (EET),2,09:30 - 10:00,10:00 - 12:00,12:00 - 12:15"));
    exchanges.add(StockExchange.createFromCSV("Athens Exchange,EUR,ATH,,AT,1.0,Euro,Greece,Eastern European Time (EET),2,,10:00 - 17:20,"));
    exchanges.add(StockExchange.createFromCSV("Australian Securities Exchange,AUD,ASX,.AX,AU,1.0,Australian Dollar,Australia,Australian Eastern Standard Time (AEST),10,07:00 - 10:00,10:00 - 16:00,16:00 - 19:00"));
    exchanges.add(StockExchange.createFromCSV("Bahrain Stock Exchange,BHD,BSH,,BH,1.0,Bahraini Dinar,Bahrain,Arabia Standard Time (AST),3,09:15 - 09:30,09:30 - 12:30,"));
    exchanges.add(StockExchange.createFromCSV("Barcelona Stock Exchange,EUR,BCN,.BC,BC,1.0,Euro,Spain,Central European Time (CET),1,08:30 - 09:00,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Beirut Stock Exchange,LBP,BEY,,LE,1.0,Lebanese Pound,Lebanon,Eastern European Time (EET),2,09:00 - 09:30,09:30 - 12:30,"));
    exchanges.add(StockExchange.createFromCSV("Berlin Stock Exchange,EUR,BER,.BE,BE,1.0,Euro,Germany,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Bermuda Stock Exchange,BMD,BSX,,HM,1.0,Bermudian Dollar,Bermuda,Atlantic Standard Time Zone (AST),-4,08:30 - 09:00,09:00 - 15:30,"));
    exchanges.add(StockExchange.createFromCSV("Berne eXchange,CHF,BRN,,BN,1.0,Swiss Franc,Switzerland,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Bilbao Stock Exchange,EUR,,.BI,,1.0,Euro,Spain,Central European Time (CET),1,08:30 - 09:00,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Bombay Stock Exchange,INR,BOM,.BO,BY,1.0,Indian Rupee,India,Indian Standard Time (IST),+5.5,,09:00 - 15:30,"));
    exchanges.add(StockExchange.createFromCSV("Botswana Stock Exchange,BWP,BOT,,GB,1.0,Botswana Pula,Botswana,Central Africa Time (CAT),2,,09:30 - 10:30,"));
    exchanges.add(StockExchange.createFromCSV("BOVESPA - Sao Paolo Stock Exchange,BRL,SAO,.SA,BR,1.0,Brazilian Real,Brazil,Brasilia Time (BRT),-3,09:45 - 10:00,10:00 - 17:00,17:30 - 19:00"));
    exchanges.add(StockExchange.createFromCSV("Bratislava Stock Exchange,SKK,,,BS,1.0,Slovak Koruna,Slovakia,Central European Time (CET),1,10:30 - 10:50,11:00 - 14:00,"));
    exchanges.add(StockExchange.createFromCSV("Bremen Stock Exchange,EUR,,.BM,,1.0,Euro,Germany,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Bucharest Stock Exchange,RON,BSE,,RO,1.0,Romanian Leu,Romania,Eastern European Time (EET),2,09:30 - 10:00,10:00 - 16:30,"));
    exchanges.add(StockExchange.createFromCSV("Budapest Stock Exchange,HUF,BDP,,BU,1.0,Hungarian Forint,Hungary,Central European Time (CET),1,08:30 - 09:00,09:00 - 16:30,16:30 - 16:35"));
    exchanges.add(StockExchange.createFromCSV("Buenos Aires Stock Exchange,ARS,BUE,.BA,BA,1.0,Argentina Pesos,Argentina,Argentina Time (ART),-3,,,"));
    exchanges.add(StockExchange.createFromCSV("Bulgarian Stock Exchange,BGN,BUL,,BG,1.0,Bulgarian Lev,Bulgaria,Eastern European Time (EET),2,09:00 - 09:20,09:20 - 13:45,13:45 - 16:00"));
    exchanges.add(StockExchange.createFromCSV("Canada National Stock Exchange,CAD,CNQ,,L,1.0,Canadian Dollar,Canada,Eastern Standard Time (EST),-5,,09:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("Caracas Stock Exchange,VEF,CLS,,CA,1.0,Venezuelan Bolivar Fuerte,Venezuela,Venezuela Time (VET),-4.5,,,"));
    exchanges.add(StockExchange.createFromCSV("Casablanca Stock Exchange,MAD,CAS,,CL,1.0,Moroccan Dirham,Morocco,Greenwich Mean Time (GMT),0,,,"));
    exchanges.add(StockExchange.createFromCSV("Chicago Board of Trade,USD,,.CBT,,1.0,U.S. Dollar,United States,Central Standard Time (CST),-6,,08:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("Chicago Mercantile Exchange,USD,,.CME,,1.0,U.S. Dollar,United States,Central Standard Time (CST),-6,,08:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("Chicago Stock Exchange,USD,,,M,1.0,U.S. Dollar,United States,Central Standard Time (CST),-6,,08:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("Colombia Stock Exchange,COP,CLB,,BO,1.0,Colombian Peso,Colombia,,-5,,,"));
    exchanges.add(StockExchange.createFromCSV("Colombo Stock Exchange,LKR,COL,,SL,1.0,Sri Lankan Rupee,Sri Lanka,Indian Standard Time (IST),+5.5,09:00 - 09:30,09:30 - 14:30,"));
    exchanges.add(StockExchange.createFromCSV("Copenhagen Stock Exchange,DKK,,.CO,,1.0,Danish Krone,Denmark,Central European Time (CET),1,,09:00 - 17:00,"));
    exchanges.add(StockExchange.createFromCSV("Cyprus Stock Exchange,EUR,CSE,,CP,1.0,Euro,Cyprus,Eastern European Time (EET),2,,10:00 - 17:00,"));
    exchanges.add(StockExchange.createFromCSV("Damascus Securities Exchange,SYP,DSE,,DSE,1.0,Syrian Pound,Syria,,2,,,"));
    exchanges.add(StockExchange.createFromCSV("Dhaka Stock Exchange,BDT,,,DH,1.0,Bangladeshi Taka,Bangladesh,Bangladesh Time (BDT),6,,10:00 - 14:00,"));
    exchanges.add(StockExchange.createFromCSV("Dusseldorf Stock Exchange,EUR,,.DU,DU,1.0,Euro,Germany,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Egyptian Stock Exchange,EGP,CAI,,CI,1.0,Egyptian Pound,Egypt,Eastern European Time (EET),2,,10:30 - 14:30,"));
    exchanges.add(StockExchange.createFromCSV("Euronext,EUR,,.NX,,1.0,Euro,France,Central European Time (CET),1,,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Euronext - Amsterdam,EUR,AMS,.AS,AE,1.0,Euro,Holland,Central European Time (CET),1,,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Euronext - Brussels,EUR,EBR,.BR,BT,1.0,Euro,Belgium,Central European Time (CET),1,,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Euronext - Lisbon,EUR,ELI,.LS,LB,1.0,Euro,Portugal,Central European Time (CET),1,,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Euronext - Paris,EUR,EPA,.PA,FR,1.0,Euro,France,Central European Time (CET),1,,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Frankfurt Stock Exchange,EUR,FRA,.F,FF,1.0,Euro,Germany,Central European Time (CET),1,,09:00 - 20:00,"));
    exchanges.add(StockExchange.createFromCSV("Fukuoka Stock Exchange,JPY,FUK,,FU,1.0,Japanese Yen,Japan,Japan Standard Time (JST),9,,,"));
    exchanges.add(StockExchange.createFromCSV("Ghana Stock Exchange,GHS,GHA,,GH,1.0,Ghanaian Cedi,Ghana,Greenwich Mean Time (GMT),0,09:30 - 10:00,10:00 - 12:00,"));
    exchanges.add(StockExchange.createFromCSV("GreTai Securities Market,TWD,,,OT,1.0,Taiwan Dollar,Taiwan,China Standard Time (CST),8,,09:00 - 14:00,14:00 - 14:30"));
    exchanges.add(StockExchange.createFromCSV("Guayaquil Stock Exchange,USD,,,GU,1.0,U.S. Dollar,Ecuador,Ecuador Time (ECT),-5,,,"));
    exchanges.add(StockExchange.createFromCSV("Hamburg Stock Exchange,EUR,,.HM,,1.0,Euro,Germany,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Hanover Stock Exchange,EUR,,.HA,,1.0,Euro,Germany,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Hercules Stock Exchange,JPY,NJM,,HQ,1.0,Japanese Yen,Japan,Japan Standard Time (JST),9,,,"));
    exchanges.add(StockExchange.createFromCSV("Hong Kong Stock Exchange,HKD,HKG,.HK,HK,1.0,Hong Kong Dollar,China,Hong Kong Time (HKT),8,09:30 - 10:00,10:00 - 16:00,Cancelled"));
    exchanges.add(StockExchange.createFromCSV("Irish Stock Exchange,EUR,ISE,.IR,DB,1.0,Euro,Ireland,Central European Time (CET),1,06:30 - 07:50,07:50 - 16:30,16:30 - 17:15"));
    exchanges.add(StockExchange.createFromCSV("Istanbul Stock Exchange,TRY,IST,,IS,1.0,Turkish New Lira,Turkey,Eastern European Time (EET),2,,09:30 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Jakarta Stock Exchange,IDR,JAK,.JK,JK,1.0,Indonesian Rupiah,Indonesia,Indonesian Western Standard Time (WIB),7,09:10 - 09:29,09:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("JASDAQ Securities Exchange,JPY,JSD,,JA,1.0,Japanese Yen,Japan,Japan Standard Time (JST),9,08:00 - 09:00,09:00 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("JSE Securities Exchange,ZAR,JNB,,JO,1.0,South African Rand,South Africa,South African Standard Time (SAST),2,,09:00 - 17:00,"));
    exchanges.add(StockExchange.createFromCSV("Karachi Stock Exchange,PKR,KAR,,KA,1.0,Pakistani Rupee,Pakistan,Pakistan Standard Time (PST),5,09:15 - 09:45,09:45 - 14:15,"));
    exchanges.add(StockExchange.createFromCSV("Korea Exchange,KRW,SEO,.KS,SE,1.0,Korean Won,Korea,Korea Standard Time (KST),9,,08:00 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("KOSDAQ,KRW,KDQ,.KQ,KQ,1.0,Korean Won,Korea,Korea Standard Time (KST),9,,,"));
    exchanges.add(StockExchange.createFromCSV("Lahore Stock Exchange,PKR,Lah,,Lah,1.0,Pakistani Rupee,Pakistan,Pakistan Standard Time (PST),5,09:15 - 09:45,09:45 - 14:15,"));
    exchanges.add(StockExchange.createFromCSV("Lima Stock Exchange,PEN,,,VL,1.0,Peruvian Nuevo Sol,Peru,Peru Time (PET),-5,,,"));
    exchanges.add(StockExchange.createFromCSV("Ljubljana Stock Exchange,EUR,LJE,,LJ,1.0,Euro,Slovenia,Central European Time (CET),1,08:00 - 09:30,09:30 - 13:00,"));
    exchanges.add(StockExchange.createFromCSV("London Exchange (Pence),GBP,LON,.L,LN,0.01,British Pound,United Kingdom,Greenwich Mean Time (GMT),0,,08:00 - 16:30,", "lp-ln-lon"));
    exchanges.add(StockExchange.createFromCSV("London Exchange (GBP),GBP,LON,.L,LN,1.0,British Pound,United Kingdom,Greenwich Mean Time (GMT),0,,08:00 - 16:30,", "lg-ln-lon"));
    exchanges.add(StockExchange.createFromCSV("Lusaka Stock Exchange,ZMK,LUS,,LZ,1.0,Zambian Kwacha,Zambia,Central Africa Time (CAT),2,,,"));
    exchanges.add(StockExchange.createFromCSV("Luxembourg Stock Exchange,EUR,LUX,,LU,1.0,Euro,Luxembourg,Central European Time (CET),1,07:15 - 09:00,09:00 - 17:40,"));
    exchanges.add(StockExchange.createFromCSV("Macedonian Stock Exchange,MKD,MSE,,MN,1.0,Macedonian Denar,Macedonia,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Madrid Fixed Income Market,EUR,,.MF,,1.0,Euro,Spain,Central European Time (CET),1,08:30 - 09:00,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Madrid SE C.A.T.S.,EUR,,.MC,,1.0,Euro,Spain,Central European Time (CET),1,08:30 - 09:00,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Madrid Stock Exchange,EUR,MCE,.MA,MD,1.0,Euro,Spain,Central European Time (CET),1,08:30 - 09:00,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Malawi Stock Exchange,MWK,MAL,,MV,1.0,Kwacha,Malawi,Central Africa Time (CAT),2,,,"));
    exchanges.add(StockExchange.createFromCSV("Malaysia Exchange,MYR,KUL,.KL,KU,1.0,Malaysian Ringgit,Malaysia,Malaysia Standard Time (MST),8,,09:00 - 17:00,"));
    exchanges.add(StockExchange.createFromCSV("Mexican Stock Exchange,MXN,MXK,.MX,MX,1.0,Mexican Peso,Mexico,Central Standard Time (CST),-6,,08:30 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("Milan Stock Exchange,EUR,BIT,.MI,MI,1.0,Euro,Italy,Central European Time (CET),1,08:00 - 09:05,09:05 - 17:35,18:00 - 20:30"));
    exchanges.add(StockExchange.createFromCSV("Montevideo Stock Exchange,UYU,,,MV,1.0,Uruguayan Peso,Uruguay,Uruguay Time (UYT),-3,,,"));
    exchanges.add(StockExchange.createFromCSV("Munich Stock Exchange,EUR,,.MU,MU,1.0,Euro,Germany,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Nagoya Stock Exchange,JPY,NAG,,NY,1.0,Japanese Yen,Japan,Japan Standard Time (JST),9,,09:00 - 15:30,"));
    exchanges.add(StockExchange.createFromCSV("Nairobi Stock Exchange,KES,NBO,,NR,1.0,Kenyan Shilling,Kenya,East Africa Time (EAT),3,09:00 - 09:30,09:30 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("NASDAQ,USD,NASDAQ,,O,1.0,U.S. Dollar,United States,Eastern Standard Time (EST),-5,07:00 - 09:30,09:30 - 16:00,16:00 - 20:00"));
    exchanges.add(StockExchange.createFromCSV("NASDAQ Dubai,AED,DFM,,,1.0,U.A.E. Dirham,United Arab Emirates,United Arab Emirates Standard Time,4,,11:45 - 17:00,"));
    exchanges.add(StockExchange.createFromCSV("NASDAQ OMX BX,USD,NASDAQ,,B,1.0,U.S. Dollar,United States,Eastern Standard Time (EST),-5,,08:00 - 19:00,"));
    exchanges.add(StockExchange.createFromCSV("NASDAQ OMX PHLX,USD,NASDAQ,NASDAQ,X,1.0,U.S. Dollar,United States,Eastern Standard Time (EST),-5,,08:00 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("National Stock Exchange,USD,,,C,1.0,U.S. Dollar,United States,Central Standard Time (CST),-6,,08:30 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("National Stock Exchange of India,INR,NSE,.NS,IN,1.0,Indian Rupee,India,Indian Standard Time (IST),+5.5,,09:00 - 15:30,15:50 - 16:00"));
    exchanges.add(StockExchange.createFromCSV("New York Board of Trade,USD,,.NYB,,1.0,U.S. Dollar,United States,Eastern Standard Time (EST),-5,,09:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("New York Commodities Exchange,USD,,.CMX,,1.0,U.S. Dollar,United States of America,Eastern Standard Time (EST),-5,,,"));
    exchanges.add(StockExchange.createFromCSV("New York Mercantile Exchange,USD,,.NYM,,1.0,U.S. Dollar,United States of America,Eastern Standard Time (EST),-5,,,"));
    exchanges.add(StockExchange.createFromCSV("New York Stock Exchange,USD,NYSE,,N,1.0,U.S. Dollar,United States,Eastern Standard Time (EST),-5,,09:30 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("New Zealand Exchange,NZD,NZE,.NZ,NZ,1.0,New Zealand Dollar,New Zealand,New Zealand Standard Time (NZST),12,08:00 - 10:00,10:00 - 17:00,17:00 - 17:30"));
    exchanges.add(StockExchange.createFromCSV("Nigerian Stock Exchange,NGN,NIG,,LA,1.0,Nigerian Naira,Nigeria,West Africa Time (WAT),1,,,"));
    exchanges.add(StockExchange.createFromCSV("OMX Baltic Exchange - Riga,LVL,RSE,,RG,1.0,Latvian Lats,Latvia,Eastern European Time (EET),2,08:30 - 10:00,10:00 - 14:00,14:00 - 14:30"));
    exchanges.add(StockExchange.createFromCSV("OMX Baltic Exchange - Tallinn,EUR,TAL,,ET,1.0,Euro,Estonia,Eastern European Time (EET),2,08:30 - 10:00,10:00 - 14:00,14:00 - 14:30"));
    exchanges.add(StockExchange.createFromCSV("OMX Baltic Exchange - Vilnius,LTL,VSE,,LV,1.0,Lithuanian Litas,Lithuania,Eastern European Time (EET),2,08:30 - 10:00,10:00 - 14:00,14:00 - 14:30"));
    exchanges.add(StockExchange.createFromCSV("OMX Nordic Exchange - Copenhagen,DKK,CPH,,KO,1.0,Danish Krone,Denmark,Central European Time (CET),1,,09:00 - 17:00,"));
    exchanges.add(StockExchange.createFromCSV("OMX Nordic Exchange - Helsinki,EUR,HEL,,HE,1.0,Euro,Finland,Eastern European Time (EET),2,,10:00 - 18:30,"));
    exchanges.add(StockExchange.createFromCSV("OMX Nordic Exchange - Stockholm,SEK,STO,.ST,SK,1.0,Swedish Krona,Sweden,Central European Time (CET),1,,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Osaka Securities Exchange,JPY,OSA,,OK,1.0,Japanese Yen,Japan,Japan Standard Time (JST),9,,09:00 - 15:10,"));
    exchanges.add(StockExchange.createFromCSV("Oslo Stock Exchange,NOK,OSL,.OL,OS,1.0,Norwegian Krone,Norway,Central European Time (CET),1,08:15 - 09:00,09:00 - 17:30,17:40 - 18:00"));
    exchanges.add(StockExchange.createFromCSV("OTC Bulletin Board Market,USD,,.OB,,1.0,U.S. Dollar,United States of America,Eastern Standard Time (EST),-5,,,"));
    exchanges.add(StockExchange.createFromCSV("Palestine Securities Exchange,JOD,PAS,,PL,1.0,Jordanian Dinar,Palestine,,2,,,"));
    exchanges.add(StockExchange.createFromCSV("Philippine Stock Exchange,PHP,PSE,,PH,1.0,Philippine Peso,Philippines,Philippine Standard Time (PST),8,,09:30 - 12:10,"));
    exchanges.add(StockExchange.createFromCSV("Pink Sheets,USD,,.PK,,1.0,U.S. Dollar,United States of America,Eastern Standard Time (EST),-5,,,"));
    exchanges.add(StockExchange.createFromCSV("PLUS Markets Group,GBP,OFEX,,PZ,1.0,British Pound,United Kingdom,Greenwich Mean Time (GMT),0,,08:00 - 16:30,"));
    exchanges.add(StockExchange.createFromCSV("Prague Stock Exchange,CZK,PRG,,PR,1.0,Czech Koruna,Czech Republic,Central European Time (CET),1,,09:15 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("Quito Stock Exchange,USD,,,QT,1.0,U.S. Dollar,Ecuador,Ecuador Time (ECT),-5,,,"));
    exchanges.add(StockExchange.createFromCSV("Russian Trading System,USD,RTC,,RS,1.0,U.S. Dollar,Russia,Moscow Standard Time (MSK),3,,10:30 - 19:00,"));
    exchanges.add(StockExchange.createFromCSV("Santiago Stock Exchange,CLP,SCL,.SN,SN,1.0,Chilean Peso,Chile,,-4,,,"));
    exchanges.add(StockExchange.createFromCSV("Sapporo Securities Exchange,JPY,,,SO,1.0,Japanese Yen,Japan,Japan Standard Time (JST),9,,,"));
    exchanges.add(StockExchange.createFromCSV("Shanghai Stock Exchange,CNY,SHA,.SS,SH,1.0,Chinese Renminbi,China,China Standard Time (CST),8,09:15 - 09:25,09:30 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("Shenzhen Stock Exchange,CNY,SHE,.SZ,SZ,1.0,Chinese Renminbi,China,China Standard Time (CST),8,09:15 - 09:25,09:30 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("Singapore Exchange,SGD,SIN,.SI,SG,1.0,Singapore Dollar,Singapore,Singapore Standard Time (SST),8,08:30 - 09:00,09:00 - 17:00,"));
    exchanges.add(StockExchange.createFromCSV("SIX Swiss Exchange,CHF,VTX,.SW,EB,1.0,Swiss Franc,Switzerland,Central European Time (CET),1,,09:00 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Stock Exchange of Thailand,THB,BAK,,TH,1.0,Thai Baht,Thailand,,7,,9:30 - 14:30,"));
    exchanges.add(StockExchange.createFromCSV("Stuttgart Stock Exchange,EUR,STU,.SG,ST,1.0,Euro,Germany,Central European Time (CET),1,,09:00 - 20:00,"));
    exchanges.add(StockExchange.createFromCSV("Taiwan OTC Exchange,TWD,,.TWO,,1.0,Taiwan Dollar,Taiwan,China Standard Time (CST),8,,09:00 - 13:30,"));
    exchanges.add(StockExchange.createFromCSV("Taiwan Stock Exchange,TWD,TPE,.TW,TW,1.0,Taiwan Dollar,Taiwan,China Standard Time (CST),8,,09:00 - 13:30,14:00 - 14:30"));
    exchanges.add(StockExchange.createFromCSV("Tel Aviv Stock Exchange,ILS,TLV,.TA,TV,1.0,Israeli New Sheqel,Israel,Israel Standard Time (IST),2,08:30 - 09:00,09:30 - 17:30,"));
    exchanges.add(StockExchange.createFromCSV("Tokyo Stock Exchange,JPY,TYO,,TO,1.0,Japanese Yen,Japan,Japan Standard Time (JST),9,,09:00 - 15:00,"));
    exchanges.add(StockExchange.createFromCSV("Toronto Stock Exchange,CAD,TSE,.TO,T,1.0,Canadian Dollar,Canada,Eastern Standard Time (EST),-5,,09:30 - 16:00,16:15 - 17:00"));
    exchanges.add(StockExchange.createFromCSV("TSX Venture Exchange,CAD,CVE,.V,V,1.0,Canadian Dollar,Canada,Eastern Standard Time (EST),-5,,09:30 - 16:00,16:15 - 17:00"));
    exchanges.add(StockExchange.createFromCSV("Vienna Stock Exchange,EUR,WBAG,.VI,VI,1.0,Euro,Austria,Central European Time (CET),1,,09:15 - 17:35,"));
    exchanges.add(StockExchange.createFromCSV("Warsaw Stock Exchange,PLN,WAR,,WA,1.0,Polish Zloty,Poland,Central European Time (CET),1,08:00 - 09:00,09:00 - 16:20,16:20 - 16:30"));
    exchanges.add(StockExchange.createFromCSV("XETRA,EUR,ETR,.DE,,1.0,Euro,Germany,Central European Time (CET),1,,,"));
    exchanges.add(StockExchange.createFromCSV("Zagreb Stock Exchange,HRK,ZSE,,ZG,1.0,Croatian Kuna,Croatia,Central European Time (CET),1,09:00 - 10:00,10:00 - 16:00,"));
    exchanges.add(StockExchange.createFromCSV("Zimbabwe Stock Exchange,ZWD,ZIM,,ZB,1.0,Zimbabwean Dollar,Zimbabwe,Central Africa Time (CAT),2,,,"));
    _exchangeList.clear();
    for (StockExchange exchange : exchanges) {
      _exchangeList.put(exchange.getExchangeId(), exchange);
    }
  }
}
