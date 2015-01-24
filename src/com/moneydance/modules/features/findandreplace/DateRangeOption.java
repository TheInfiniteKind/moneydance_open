/*************************************************************************\
 * Copyright (C) 2010-2015 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 \*************************************************************************/

package com.moneydance.modules.features.findandreplace;

/**
 * Defines the various date ranges that can be selected in reports, budgets, etc. The ordinal 
 * values are fixed to the original integers (indices) mapped to a date range, as previously defined 
 * in {@link com.moneydance.apps.md.view.gui.DateRangeChooser}:
 * <pre>
 *     DR_YEAR_TO_DATE = 0
 *     DR_QUARTER_TO_DATE = 1
 *     DR_MONTH_TO_DATE = 2
 *     DR_THIS_YEAR = 3
 *     DR_THIS_QUARTER = 4
 *     DR_THIS_MONTH = 5
 *     DR_LAST_YEAR = 6
 *     DR_LAST_QUARTER = 7
 *     DR_LAST_MONTH = 8
 *     DR_LAST_12_MONTHS = 9
 *     DR_ALL_DATES = 10
 *     DR_CUSTOM_DATE = 11
 *</pre>
 *
 * New, additional date ranges were requested for the budget system, so these are tacked on to the
 * end of the list. Because they are out-of-order for logical display purposes in a list, a sorting
 * index is assigned so that the list of date ranges may be more logically presented to the user.
 * <pre>
 *     DR_LAST_30_DAYS = 12
 *     DR_LAST_365_DAYS = 13
 *     DR_THIS_WEEK = 14
 *     DR_LAST_WEEK = 15
 * An additional request was for investment performance reports for the last day (seeing how
 * market changes in one day affected results)
 *     DR_LAST_DAY = 16
 * </pre>
 *
 * This is a stripped-down version of DateRangeOption that is available in MD2011, included here
 * to maintain compatibility with MD2010.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public enum DateRangeOption {
  
  /** Current year to today's date. */
  DR_YEAR_TO_DATE("year_to_date"), // ordinal 0
  /** Current quarter to today's date. */
  DR_QUARTER_TO_DATE("quarter_to_date"), // 1
  /** Current month to today's date. */
  DR_MONTH_TO_DATE("month_to_date"), // 2
  /** Current year from beginning to end. */
  DR_THIS_YEAR("this_year"), // 3
  /** Current fiscal year from beginning to end. */
  DR_THIS_FISCAL_YEAR("this_fiscal_year"), // 4
  /** Current quarter from beginning to end. */
  DR_THIS_QUARTER("this_quarter"), // 5
  /** Current month from beginning to end. */
  DR_THIS_MONTH("this_month"), // 6
  /** Previous year from beginning to end. */
  DR_LAST_YEAR("last_year"), // 7
  /** Last fiscal year from beginning to end. */
  DR_LAST_FISCAL_YEAR("last_fiscal_year"), // 4
  /** Previous quarter from beginning to end. */
  DR_LAST_QUARTER("last_quarter"), // 8
  /** Previous month from beginning to end. */
  DR_LAST_MONTH("last_month"), // 9
  /** Last 12 months from today's date, starting at 12 months prior to today until today's date. */
  DR_LAST_12_MONTHS("last_12_months"), // 10
  /** All dates to today's date. */
  DR_ALL_DATES("all_dates"), // 11
  /** User-defined date range. */
  DR_CUSTOM_DATE("custom_date"), // 12
  /** Current week from beginning to end. */
  DR_THIS_WEEK("this_week"), // 13
  /** Last 30 days from today's date. */
  DR_LAST_30_DAYS("last_30_days"), // 14
  /** Last 365 days from today's date. */
  DR_LAST_365_DAYS("last_365_days"), // 15
  /** Previous week from beginning to end. */
  DR_LAST_WEEK("last_week"), // 16
  /** Previous day to today. */
  DR_LAST_1_DAY("last_1_day"); // 17
  

  /**
   * The default date range to use if none is specified.
   */
  public static final DateRangeOption DEFAULT = DR_YEAR_TO_DATE;

  /**
   * The resource key for obtaining a localized display string, as well as a unique identifier
   * for storage in settings, URLs, etc.
   */
  private final String _resourceKey;


  /**
   * Constructor to accept the resource key for localization.
   *
   * @param resourceKey The resource key for obtaining a localized display string.
   *
   */
  private DateRangeOption(final String resourceKey) {
    _resourceKey = resourceKey;
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Interface DisplayableObject
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * @return The unique string key for obtaining a localized display string and as a unique
   * identifier.
   */
  public String getResourceKey() {
    return _resourceKey;
  }

}