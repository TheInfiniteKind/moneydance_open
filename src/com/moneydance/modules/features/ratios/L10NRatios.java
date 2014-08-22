/*
 * ************************************************************************
 * Copyright (C) 2012-2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

/**
 * <p>Localizable string keys to look up in resources. Keeping all of these keys in one place
 * helps simplify tracking localized resources. It also helps when it comes time to audit for
 * unused strings.</p>
 *
 * @author Kevin Menningen
 */
public class L10NRatios
{
  static final String TITLE = "title.text"; // Ratio Calculator

  // main configuration dialog
  static final String SETTINGS_TITLE = "settings.title";

  // other strings
  /** Text that follows a label. Some locales prefer ' : ', others prefer ': '.  */
  static final String LABEL_COLON = "labelColon";

  static final String HOME_PAGE_LABEL = "homePageLabel";
  static final String REPORT_TITLE = "reportTitle";
  static final String REPORT_LABEL = "ratio";  // bottom row of report
  static final String SHOW_PERCENT = "showPercent";
  static final String ALWAYS_POSITIVE = "alwaysPositive";
  static final String TXN_MATCH = "matchLabel";
  static final String TXN_INTO = "txnInto";
  static final String TXN_OUT_OF = "txnOutOf";
  static final String TXN_BOTH = "txnBoth";
  static final String START_BALANCE = "beg_balance";
  static final String END_BALANCE = "end_balance";
  static final String AVERAGE_BALANCE = "avg_balance";
  static final String CONSTANT = "constant";
  static final String DAYS_IN_PERIOD = "days_in_period";
  static final String INVALID_CONSTANT = "invalid_constant";
  static final String NUMERATOR = "numerator";
  static final String DENOMINATOR = "denominator";
  static final String LABEL = "label";
  static final String COLUMN_LABEL = "columnLabel";
  static final String NAN = "nan";
  static final String GENERAL_SETTINGS = "generalSettings";
  static final String DECIMALS = "decimals";
  static final String CUSTOM_DATE_MENU = "customDateMenu";
  static final String CUSTOM_DATE_TITLE = "customDateTitle";
  static final String COPY_SUFFIX = "copy";

  public static final String USER_GUIDE = "userGuide.label";
  // dual account selector
  public static final String SELECT_ACCOUNTS_TITLE = "selAccountTitle";
  public static final String REQUIRED = "required";
  public static final String ALLOWED = "allowed";
  public static final String DISALLOWED = "disallowed";

  // example ratios
  static final String EXAMPLE_NOTES_1 = "exNotes1";
  static final String EXAMPLE_NOTES_2 = "exNotes2";
  static final String EXAMPLE_NOTES_3 = "exNotes3";
  static final String INCOME_NAME = "exGrossIncome";
  static final String DEBT_TO_INCOME_NAME = "exDtiName";
  static final String TOTAL_DEBT_NAME = "exDtiDebt";
  static final String DEBT_TO_INCOME_NOTES = "exDtiNotes";
  static final String SAVINGS_TO_INCOME_NOTES = "exStiNotes";
  static final String SAVINGS_TO_INCOME_NAME = "exStiName";
  static final String TOTAL_SAVINGS_NAME = "exTotalSavings";
  static final String DEBT_SERVICE_TO_INCOME_NAME = "exDstiName";
  static final String DEBT_SERVICE_NAME = "exDstiDebt";
  static final String DEBT_SERVICE_TO_INCOME_NOTES = "exDstiNotes";
  static final String SAVINGS_RATE_NAME = "exSRName";
  static final String SAVINGS_NAME = "exSRSavings";
  static final String SAVINGS_RATE_NOTES = "exSRNotes";
  static final String DEBT_TO_ASSETS_NAME = "exDtaName";
  static final String TOTAL_ASSETS_NAME = "exDtaAssets";
  static final String DEBT_TO_ASSETS_NOTES = "exDtaNotes";

  // from Moneydance
  static final String ACCOUNTS = "accounts"; // Accounts
  static final String FILTER_BY_TAG = "filter_by_tag"; // Filter by tag
  static final String ENDING_BALANCE = "rec_end_bal";
  static final String NOTES = "notes";
  static final String USE_TAX_DATE = "srch_use_tax_date";
  static final String REPORT_TOTAL = "report_total";
  static final String SETTINGS_LABEL = "settings";
  public static final String ACCOUNT_NAME = "account_name";
  public static final String ACCOUNT_INACTIVE = "account_is_inactive";
  public static final String SELECT = "select";
  public static final String NONE = "none";
}
