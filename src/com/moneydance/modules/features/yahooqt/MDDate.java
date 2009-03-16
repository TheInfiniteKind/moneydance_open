/************************************************************\
 *      Copyright (C) 2009 Reilly Technologies, L.L.C.      *
 \************************************************************/
package com.moneydance.modules.features.yahooqt;

import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;

/**
 * TODO: Add Javadoc here
 *
 * @author Jay Detwiler
 */
public class MDDate implements Stringifyable {
  int day; // 1-31
  int month; // 1-12
  int year; // 4 digit

  /**
   * Create an <code>MDDate</code> for today.
   */
  public MDDate() {
    this(new Date());
  }

  /**
   * Create an <code>MDDate</code> from the given <code>Date</code>.
   *
   * @param date a <code>Date</code>
   */
  public MDDate(Date date) {
    year = (date.getYear() + 1900);
    month = (date.getMonth() + 1);
    day = date.getDate();
  }

  /**
   * Create an <code>MDDate</code> from the given <code>Calendar</code>.
   *
   * @param calendar a <code>Calendar</code>
   */
  MDDate(Calendar calendar) {
    this.day = calendar.get(GregorianCalendar.DAY_OF_MONTH);
    this.month = calendar.get(GregorianCalendar.MONTH) + 1;
    this.year = calendar.get(GregorianCalendar.YEAR);
  }

  /**
   * Create an <code>MDDate</code> from the given <code>int</code> representation.
   *
   * @param value an <code>int</code> representation of a date
   * @throws IllegalArgumentException if the given <code>int</code> is not a valid date
   * @see #toInt()
   */
  public MDDate(int value) throws IllegalArgumentException {
    if (isValidDate(value)) {
      year = value / 10000;          // year
      month = (value / 100) % 100;  // month
      day = value % 100;            // day
    } else {
      throw new IllegalArgumentException("Value was not a valid date, '" + value + "'");
    }
  }

  /**
   * Create an <code>MDDate</code> with the given day, month and year.  Unlike {@link MDDate#MDDate(int)}, this
   * constructor is lenient and will compute a valid date from the integer valus given.  For example, the argument list
   * <code>32,1,2000</code> would give an <code>MDDate</code> with the value of Ferbuary 1st, 2000.
   *
   * @param day   a day value with 1 meaning the first of the month
   * @param month a month value with 1 meaning January
   * @param year  a year value taken as the exact value (ie not a two digit year 09 meaning 2009)
   */
  public MDDate(int day, int month, int year) {
    this(new GregorianCalendar(year, month - 1, day));
  }

  /**
   * Returns <code>true</code> if the given <code>int</code> is a valid date representation.  The integer value must
   * have a valid day (1-31, depending on the month) in the tens/ones positions, a valid month (1-12) in the
   * thousands/hundreds positions and a valid year (greater than 1900) in the ten millions through ten thousands
   * positions.
   *
   * @param value an <code>int</code> representation of a date
   * @return <code>true</code> if the given <code>int</code> is a valid date representation.
   */
  public static boolean isValidDate(int value) {
    int year = value / 10000;          // year
    int month = (value / 100) % 100;  // month
    int day = value % 100;            // day
    GregorianCalendar gc = new GregorianCalendar(year, month - 1, day);
    return gc.get(GregorianCalendar.DAY_OF_MONTH) == day &&
        gc.get(GregorianCalendar.MONTH) == month - 1 &&
        gc.get(GregorianCalendar.YEAR) == year;
  }

  /**
   * Returns this date as an <code>int</code> where the integer value is an eight digit number with the digits put
   * together as YYYYMMDD.
   *
   * @return this date as an <code>int</code>
   */
  public int toInt() {
    return day + month * 100 + year * 10000;
  }

  /**
   * Returns this date as a <code>Date</code> with the time set to noon.
   *
   * @return this date as a <code>Date</code>.
   */
  public Date toDate() {
    return new GregorianCalendar(year, month - 1, day, 12, 0, 0).getTime();
  }

  public String toString() {
    return "" + toInt();
  }

  public static MDDate fromString(String string) throws IllegalArgumentException {
    try {
      return new MDDate(Integer.parseInt(string));
    } catch (NumberFormatException e) {
      throw new IllegalArgumentException("Value could not be parsed, '" + string + "'");
    }
  }

  public boolean isBefore(MDDate date) {
    if (year < date.year) {
      return true;
    } else if (year == date.year) {
      if (month < date.month) {
        return true;
      } else if (month == date.month) {
        if (day < date.day) {
          return true;
        }
      }
    }
    return false;
  }

  public boolean isAfter(MDDate date) {
    return date.isBefore(this);
  }

  public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;

    MDDate date = (MDDate) o;

    return day == date.day && month == date.month && year == date.year;
  }

  public int hashCode() {
    int result = day;
    result = 31 * result + month;
    result = 31 * result + year;
    return result;
  }
}
