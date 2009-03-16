/************************************************************\
 *      Copyright (C) 2009 Reilly Technologies, L.L.C.      *
 \************************************************************/
package com.moneydance.modules.features.yahooqt;

import java.util.Calendar;
import java.util.GregorianCalendar;

/**
 * The <code>MDTimeUnit</code> class is the Moneydance representation of a base time unit.
 * <p/>
 * This class is immutable.
 *
 * @author Jay Detwiler
 */
public class TimeUnit implements Frequency, Stringifyable {
  protected int calendarField;
  protected int numUnits;
  private String singularName;
  private String pluralName;

  /**
   * Creates a base <code>MDTimeUnit</code> from {@link java.util.Calendar} fields.  This constructor is only used
   * internally to create constant values.
   *
   * @param calendarField a <code>Calendar</code> field
   * @param numUnits      the number of <code>Calendar</code> units in this time unit
   * @param singularName  a human readable string for a single unit
   * @param pluralName    a human readable string for multiple units
   * @see java.util.Calendar#set(int, int)
   */
  private TimeUnit(int calendarField, int numUnits, String singularName, String pluralName) {
    if (numUnits < 1) {
      throw new IllegalArgumentException("Number of units must be greater than 0");
    }
    if (calendarField < 0 || calendarField > Calendar.FIELD_COUNT) {
      throw new IllegalArgumentException("Calendar field must be valid");
    }
    this.calendarField = calendarField;
    this.numUnits = numUnits;
    this.singularName = singularName;
    this.pluralName = pluralName;
  }

  public String getSingularName() {
    return singularName;
  }

  public String getPluralName() {
    return pluralName;
  }

  /**
   * Returns the next date in the sequency based on this frequency.
   *
   * @param date the initial <code>MDDate</code>
   * @return the next date in the sequency based on this frequency.
   */
  public MDDate next(MDDate date) {
    GregorianCalendar gc = new GregorianCalendar(date.year, date.month - 1, date.day, 12, 0, 0);
    gc.add(calendarField, numUnits);
    return new MDDate(gc);
  }

  /**
   * Returns the previous date in the sequency based on this frequency.
   *
   * @param date the initial <code>MDDate</code>
   * @return the previous date in the sequency based on this frequency
   */
  public MDDate previous(MDDate date) {
    GregorianCalendar gc = new GregorianCalendar(date.year, date.month - 1, date.day, 12, 0, 0);
    gc.add(calendarField, -numUnits);
    return new MDDate(gc);
  }

  public String getDescription() {
    return singularName;
  }

  public String toString() {
    return calendarField + "," + numUnits;
  }

  public static TimeUnit fromString(String string) {
    String[] strings = string.split(",");
    if (strings.length < 2) {
      throw new IllegalArgumentException("String, " + string + ", is not a valid TimeUnit");
    }
    try {
      int calendarField = Integer.parseInt(strings[0]);
      int numUnits = Integer.parseInt(strings[1]);
      for (int i = 0; i < STANDARD_UNITS.length; i++) {
        TimeUnit unit = STANDARD_UNITS[i];
        if (unit.calendarField == calendarField &&
            unit.numUnits == numUnits) {
          return unit;
        }
      }
      throw new IllegalArgumentException("String, " + string + ", is not a valid TimeUnit");
    } catch (NumberFormatException e) {
      throw new IllegalArgumentException("String, " + string + ", is not a valid TimeUnit");
    }
  }

  public boolean equals(Object o) {
    return this == o;
  }

  public int hashCode() {
    int result = calendarField;
    result = 31 * result + numUnits;
    return result;
  }

  public static final TimeUnit DAY = new TimeUnit(Calendar.DAY_OF_MONTH, 1, "Day", "Days");
  public static final TimeUnit WEEK = new TimeUnit(Calendar.DAY_OF_MONTH, 7, "Week", "Weeks");
  public static final TimeUnit MONTH = new TimeUnit(Calendar.MONTH, 1, "Month", "Months");
  public static final TimeUnit QUARTER = new TimeUnit(Calendar.MONTH, 3, "Quarter", "Quarters");
  public static final TimeUnit YEAR = new TimeUnit(Calendar.YEAR, 1, "Year", "Years");
  public static final TimeUnit[] STANDARD_UNITS = {DAY, WEEK, MONTH, QUARTER, YEAR};

}
