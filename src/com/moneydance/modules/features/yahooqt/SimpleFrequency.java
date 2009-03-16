/************************************************************\
 *      Copyright (C) 2009 Reilly Technologies, L.L.C.      *
 \************************************************************/
package com.moneydance.modules.features.yahooqt;

import java.util.GregorianCalendar;

/**
 * The <code>SimpleFrequency</code> class is an implementation of <code>Frequency</code> that uses a multiple of a given
 * <code>TimeUnit</code> to calculate next and previous dates.
 * <p/>
 * Note: When using {@link TimeUnit#MONTH month},{@link TimeUnit#QUARTER quarter} or {@link TimeUnit#YEAR year} time
 * units, you may not get the intended results.  Moving forward a month means moving the month portion of the date
 * forward while leaving the date the same.  Since the result won't always be a valid date, the date will be resolved in
 * the same manner as {@link java.util.GregorianCalendar#add(int, int)}.
 * <p/>
 * This class is immutable.
 *
 * @author Jay Detwiler
 */
public class SimpleFrequency implements Frequency, Stringifyable {
  private TimeUnit unit;
  private int num;

  /**
   * Creates a <code>SimpleFrequency</code> based on a single <code>TimeUnit</code>
   *
   * @param unit a TimeUnit
   */
  public SimpleFrequency(TimeUnit unit) {
    this(unit, 1);
  }

  /**
   * Creates a <code>SimpleFrequency</code> based on a multiple of a <code>TimeUnit</code>
   *
   * @param unit a TimeUnit
   * @param num  a positive number
   */
  public SimpleFrequency(TimeUnit unit, int num) {
    if (unit == null) {
      throw new NullPointerException("unit cannot be null");
    }
    if (num < 1) {
      throw new IllegalArgumentException("num cannot be less than 1");
    }
    this.unit = unit;
    this.num = num;
  }

  /**
   * Returns the next date in the sequency based on this frequency.
   *
   * @param date the initial <code>MDDate</code>
   * @return the next date in the sequency based on this frequency.
   */
  public MDDate next(MDDate date) {
    GregorianCalendar gc = new GregorianCalendar(date.year, date.month - 1, date.day, 12, 0, 0);
    gc.add(unit.calendarField, unit.numUnits * num);
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
    gc.add(unit.calendarField, -unit.numUnits * num);
    return new MDDate(gc);
  }

  public String toString() {
    return num + "," + unit;
  }

  public static SimpleFrequency fromString(String string) {
    try {
      int index = string.indexOf(",");
      int num = Integer.parseInt(string.substring(0, index));
      TimeUnit unit = TimeUnit.fromString(string.substring(index + 1));
      return new SimpleFrequency(unit, num);
    } catch (Throwable t) {
      throw new IllegalArgumentException("String, " + string + ", is not a valid SimpleFrequenct");
    }
  }

  public TimeUnit getUnit() {
    return unit;
  }

  public int getNumberOfUnits() {
    return num;
  }

  public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;

    SimpleFrequency that = (SimpleFrequency) o;

    if (num != that.num) return false;
    if (!unit.equals(that.unit)) return false;

    return true;
  }

  public int hashCode() {
    int result = unit.hashCode();
    result = 31 * result + num;
    return result;
  }

  public String getDescription() {
    return num == 1 ? unit.getSingularName() : num + " " + unit.getPluralName();
  }
}
