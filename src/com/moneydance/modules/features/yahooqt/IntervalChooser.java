/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.model.time.TimeInterval;
import com.moneydance.apps.md.view.resources.MDResourceProvider;

import javax.swing.JComboBox;

/**
 * A combo box that can choose a time interval. Although related to the interval chooser of the
 * same name in the main code, this one will display a different string to the user -- instead of
 * either 'Group By {interval}' or 'Subtotal By {interval}', this displays the time span represented
 * by the interval (the 'divisor') as 'Days', 'Weeks', 'Months', etc.

 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class IntervalChooser extends JComboBox {
  /**
   * Default list of intervals for graphing.
   */
  private static final TimeInterval[] INTERVAL_LIST = {
    TimeInterval.DAY,
    TimeInterval.WEEK,
    TimeInterval.MONTH,
    TimeInterval.QUARTER };

  /**
   * Constructor for ease of use in objects that had duplicate code.
   *
   * @param resources    Resource provider for localized strings.
   */
  public IntervalChooser(MDResourceProvider resources) {
    this(resources, INTERVAL_LIST, 0);
  }

  private IntervalChooser(MDResourceProvider resources, TimeInterval[] items, int defaultIndex) {
    for (TimeInterval interval : items) {
      // Graphs show data in intervals, reports subtotal after intervals
      final String display = resources.getStr(interval.getDivisorResourceKey());
      addItem(new ListItem(interval, display));
    }
    setSelectedIndex(defaultIndex);
  }

  public TimeInterval getSelectedInterval() {
    return ((ListItem) getSelectedItem())._interval;
  }

  public void selectFromParams(final String paramStr) {
    if (!SQUtil.isBlank(paramStr)) {
      final TimeInterval interval = TimeInterval.fromChar(paramStr.charAt(0));

      for (int index = 0; index < getItemCount(); index++) {
        ListItem item = (ListItem) getItemAt(index);
        if (interval.equals(item._interval)) {
          setSelectedIndex(index);
          return;
        }
      }
    }

    // just select the first
    setSelectedIndex(0);
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Inner Classes
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * Immutable holder of a time interval and the display string it happens to use.
   */
  private class ListItem {
    private final TimeInterval _interval;
    private final String _displayString;

    ListItem(TimeInterval interval, String display) {
      _interval = interval;
      _displayString = display;
    }

    @Override
    public String toString() {
      return _displayString;
    }

    @Override
    public int hashCode() {
      return _interval.hashCode();
    }

    @Override
    public boolean equals(Object other) {
      if (other == this) {
        return true;
      }
      if (other instanceof ListItem) {
        return _interval.equals(((ListItem) other)._interval);
      }
      if (other instanceof TimeInterval) {
        return _interval.equals(other);
      }
      return false;
    }
  }
}