/************************************************************\
 *      Copyright (C) 2009 Reilly Technologies, L.L.C.      *
 \************************************************************/
package com.moneydance.modules.features.yahooqt;

/**
 * The <code>Frequency</code> interface is an abstraction for calculating recurring dates.  Given a
 * <code>Frequency</code> instance you can get the next or previous dates in the sequence.
 * <p/>
 * Note: Because of the nature of months, frequencies based on the {@link TimeUnit#MONTH} may not always behave as
 * expected.  In particular, it cannot be guaranteed that calling {@link #next(MDDate)} followed by {@link
 * #previous(MDDate)} will return you to the original date.  Refer to the documentation of an implementor as to what
 * behavior is expected.
 *
 * @author Jay Detwiler
 */
public interface Frequency {
  /**
   * Returns the next date in the sequency based on this frequency.
   *
   * @param date the initial <code>MDDate</code>
   * @return the next date in the sequency based on this frequency.
   */
  MDDate next(MDDate date);

  /**
   * Returns the previous date in the sequency based on this frequency.
   *
   * @param date the initial <code>MDDate</code>
   * @return the previous date in the sequency based on this frequency
   */
  MDDate previous(MDDate date);

  /**
   * Returns a human readable description of the <code>Frequency</code>.
   *
   * @return a human readable description of the <code>Frequency</code>.
   */
  String getDescription();
}
