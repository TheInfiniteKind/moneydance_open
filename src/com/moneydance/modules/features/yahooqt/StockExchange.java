/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.util.StreamTable;
import com.moneydance.util.StringUtils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * A stock exchange definition.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class StockExchange implements Comparable<StockExchange> {
  /**
   * Default exchange. This default will not make any changes to the stock symbol being looked up,
   * so the assumption is that the stock can be looked up for a quote without any additional
   * information. For U.S. stocks this is typically true.
   */
  static final StockExchange DEFAULT = StockExchange.createFromCSV("Default,USD,,,,1.0"+
          ",U.S. Dollar,United States,Eastern Standard Time (EST),-5,,,", "DEFAULT");

  private static final String ID_KEY = "id";
  private static final String NAME_KEY = "name";
  private static final String CURRCODE_KEY = "curr_id";
  private static final String GOOGLE_KEY = "google_id";
  private static final String YAHOO_KEY = "yahoo_id";
  private static final String THOMSON_KEY = "thomson_id";
  private static final String MULTIPLIER_KEY = "price_multiplier";
  private static final String CURRNAME_KEY = "curr_name";
  private static final String COUNTRY_KEY = "country";
  private static final String TIMEZONE_KEY = "time_zone";
  private static final String GMT_DIFF_KEY = "gmt_diff";
  private static final String PRE_MTR_KEY = "pre_mtr";
  private static final String MTR_KEY = "mtr";
  private static final String POST_MTR_KEY = "post_mtr";

  // Fields
  private String _id;
  private String _name;
  private String _country;
  private String _symGoogle;
  private String _symYahoo;
  private String _symThomsonReuters;
  private double _priceMultiplier;
  private String _timeZone;
  private float _gmtDiff;
  private String _timePreMarket;
  private String _timeMarket;
  private String _timePostMarket;
  private String _currencyName;
  private String _currencyCode;

  /**
   * Generate a stock exchange entry and auto-generate the unique key for it.
   * @see StockExchange#createFromCSV(String, String)
   *
   * @param csvEntry The comma-separated values for the entry.
   * @return A stock exchange entry, with an auto-generated unique key.
   */
  public static StockExchange createFromCSV(String csvEntry) {
    return createFromCSV(csvEntry, null);
  }

  /**
   * Generate a single stock exchange definition entry via a Comma Separated Value string. The
   * columns are defined thus:
   * <ol>
   * <li>Exchange Name</li>
   * <li>Currency Code</li>
   * <li>Google Finance Symbol</li>
   * <li>Yahoo! Finance Symbol</li>
   * <li>Thomson Reuters Symbol</li>
   * <li>Currency Name</li>
   * <li>Country</li>
   * <li>Time Zone</li>
   * <li>GMT ± (integer)</li>
   * <li>Pre-Market Time Range</li>
   * <li>Market Session Time Range</li>
   * <li>Post-Market Time Range</li>
   * </ol>
   * The first 6 columns need to be defined.
   * @param csvEntry String defining one stock exchange entity.
   * @param id The identifier to use, if <code>null</code> an identifier is auto-generated from
   * the symbols.
   * @return The stock exchange object with properties defined by <code>csvEntry</code>, or
   * <code>null</code> if an entry could not be created.
   */
  public static StockExchange createFromCSV(String csvEntry, String id) {
    if (StockUtil.isBlank(csvEntry)) return null;
    String[] segments  = csvEntry.split(",");
    StockExchange result = new StockExchange();
    result._name = getCSVEntry(segments[0]);
    if (segments.length > 1) result._currencyCode = getCSVEntry(segments[1]);
    if (segments.length > 2) result._symGoogle = getCSVEntry(segments[2]);
    if (segments.length > 3) result._symYahoo = getCSVEntry(segments[3]);
    if (segments.length > 4) result._symThomsonReuters = getCSVEntry(segments[4]);
    try {
      if (segments.length > 5) {
        result._priceMultiplier = Double.valueOf(getCSVEntry(segments[5])).doubleValue();
      }
    } catch (NumberFormatException nfex) {
      System.err.println("Quote sync error parsing price multiplier for stock exchange: "+result._name);
      result._priceMultiplier = 1.0;
    }
    if (segments.length > 6) result._currencyName = getCSVEntry(segments[6]);
    if (segments.length > 7) result._country = getCSVEntry(segments[7]);
    if (segments.length > 8) result._timeZone = getCSVEntry(segments[8]);
    // the India exchanges are +5:30 or +5.5 so we support floating point values
    try {
      if (segments.length > 9) {
        result._gmtDiff = Float.valueOf(getCSVEntry(segments[9])).floatValue();
      }
    } catch (NumberFormatException nfex) {
      System.err.println("Quote sync error parsing GMT difference for stock exchange: "+result._name);
      result._gmtDiff = 0.0f;
    }
    if (segments.length > 10) result._timePreMarket = getCSVEntry(segments[10]);
    if (segments.length > 11) result._timeMarket = getCSVEntry(segments[11]);
    if (segments.length > 12) result._timePostMarket = getCSVEntry(segments[12]);
    result._id = (id != null) ? id : createIdFromEntry(result);
    return result;
  }

  private static String createIdFromEntry(StockExchange result) {
    StringBuilder key = new StringBuilder();
    List<String> codes = new ArrayList<String>(3);
    codes.add(getIdCode(result.getSymbolYahoo()));
    codes.add(getIdCode(result.getSymbolGoogle()));
    codes.add(getIdCode(result.getSymbolThomsonReuters()));
    Collections.sort(codes);
    key.append(codes.get(2));
    key.append("-");
    key.append(codes.get(1));
    key.append("-");
    key.append(codes.get(0));
    return key.toString();
  }

  private static String getIdCode(String symbol) {
    if (StockUtil.isBlank(symbol)) return "0";
    String result = symbol.toLowerCase();
    return (result.indexOf('.') == 0) ? result.substring(1) : result;
  }

  private static String getCSVEntry(final String rawText) {
    if (StockUtil.isBlank(rawText)) return "";
    return rawText.trim();
  }

  public String getExchangeId() {
    return _id;
  }

  public String getName() {
    return _name;
  }
  void setName(final String name) {
    _name = name;
  }

  public String getCountry() {
    return _country;
  }

  public String getSymbolGoogle() {
    return _symGoogle;
  }
  public void setSymbolGoogle(final String symbol) {
    _symGoogle = symbol;
  }

  public String getSymbolYahoo() {
    return _symYahoo;
  }
  public void setSymbolYahoo(final String symbol) {
    _symYahoo = symbol;
  }

  public String getSymbolThomsonReuters() {
    return _symThomsonReuters;
  }

  public double getPriceMultiplier() {
    return _priceMultiplier;
  }
  public void setPriceMultiplier(final double multiplier) {
    _priceMultiplier = multiplier;
  }

  public String getTimeZone() {
    return _timeZone;
  }

  public float getGMTDiff() {
    return _gmtDiff;
  }

  public String getTimeRangePreMarket() {
    return _timePreMarket;
  }

  public String getTimeRangeMarket() {
    return _timeMarket;
  }

  public String getTimeRangePostMarket() {
    return _timePostMarket;
  }

  public String getCurrencyName() {
    return _currencyName;
  }

  public String getCurrencyCode() {
    return _currencyCode;
  }

  public void setCurrency(CurrencyType currency) {
    _currencyName = currency.getName();
    _currencyCode = currency.getIDString();
  }
  
  public void loadFromSettings(final StreamTable settings) {
    if (settings == null) return;
    _id = settings.getStr(ID_KEY, "-");
    _name = settings.getStr(NAME_KEY, "?");
    _currencyCode = settings.getStr(CURRCODE_KEY, "USD");
    _symGoogle = settings.getStr(GOOGLE_KEY, "");
    _symYahoo = settings.getStr(YAHOO_KEY, "");
    _symThomsonReuters = settings.getStr(THOMSON_KEY, "");
    try {
      _priceMultiplier = Double.valueOf(settings.getStr(MULTIPLIER_KEY, "1.0")).doubleValue();
    } catch (NumberFormatException nfex) {
      System.err.println("Error parsing price multiplier for stock exchange: "+_name);
      _priceMultiplier = 1.0;
    }
    _currencyName = settings.getStr(CURRNAME_KEY, "U.S. Dollar");
    _country = settings.getStr(COUNTRY_KEY, "");
    _timeZone = settings.getStr(TIMEZONE_KEY, "?");
    _gmtDiff = settings.getInt(GMT_DIFF_KEY, 0) / 10.0f;
    _timePreMarket = settings.getStr(PRE_MTR_KEY, "");
    _timeMarket = settings.getStr(MTR_KEY, "");
    _timePostMarket = settings.getStr(POST_MTR_KEY, "");
    if (StockUtil.isBlank(_id) || ("-".equals(_id))) _id = createIdFromEntry(this);
  }
  
  StreamTable saveToSettings() {
    StreamTable settings = new StreamTable();
    settings.put(ID_KEY, _id);
    settings.put(NAME_KEY, _name);
    settings.put(CURRCODE_KEY, _currencyCode);
    settings.put(GOOGLE_KEY, _symGoogle);
    settings.put(YAHOO_KEY, _symYahoo);
    settings.put(THOMSON_KEY, _symThomsonReuters);
    settings.put(MULTIPLIER_KEY, Double.toString(_priceMultiplier));
    settings.put(CURRNAME_KEY, _currencyName);
    settings.put(COUNTRY_KEY, _country);
    settings.put(TIMEZONE_KEY, _timeZone);
    settings.put(GMT_DIFF_KEY, Integer.valueOf(Math.round(_gmtDiff * 10.0f)));
    settings.put(PRE_MTR_KEY, _timePreMarket);
    settings.put(MTR_KEY,_timeMarket);
    settings.put(POST_MTR_KEY, _timePostMarket);
    return settings;
  }

  @Override
  public String toString() {
    return _name;
  }

  public int compareTo(StockExchange o) {
    if (o == null) return 1;
    String otherName = o.getName();
    if (otherName == null) {
      if (_name == null) return 0;
      return 1;
    }
    if (_name == null) return -1;
    return _name.compareTo(otherName);
  }
}
