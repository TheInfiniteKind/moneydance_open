/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.moneydance.apps.md.controller.time.TimeInterval
import com.moneydance.apps.md.view.resources.MDResourceProvider
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import javax.swing.JComboBox

/**
 * A combo box that can choose a time interval. Although related to the interval chooser of the
 * same name in the main code, this one will display a different string to the user -- instead of
 * either 'Group By {interval}' or 'Subtotal By {interval}', this displays the time span represented
 * by the interval (the 'divisor') as 'Days', 'Weeks', 'Months', etc.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class IntervalChooser private constructor(resources: MDResourceProvider, items: Array<TimeInterval>, defaultIndex: Int) : JComboBox<Any?>() {
  /**
   * Constructor for ease of use in objects that had duplicate code.
   *
   * @param resources    Resource provider for localized strings.
   */
  constructor(resources: MDResourceProvider) : this(resources, INTERVAL_LIST, 0)
  
  init {
    for (interval in items) {
      // Graphs show data in intervals, reports subtotal after intervals
      val display = resources.getStr(if (interval == null) "" else interval.divisorResourceKey)
      addItem(ListItem(interval, display))
    }
    selectedIndex = defaultIndex
  }
  
  val selectedInterval: TimeInterval
    get() = (selectedItem as ListItem)._interval
  
  fun selectFromParams(paramStr: String) {
    if (!isBlank(paramStr)) {
      val interval = TimeInterval.fromChar(paramStr[0])
      
      for (index in 0..<itemCount) {
        val item = getItemAt(index) as ListItem?
        if (interval == item!!._interval) {
          selectedIndex = index
          return
        }
      }
    }
    
    // just select the first
    selectedIndex = 0
  }
  
  
  /**
   * Immutable holder of a time interval and the display string it happens to use.
   */
  private inner class ListItem(val _interval: TimeInterval, private val _displayString: String) {
    override fun toString(): String {
      return _displayString
    }
    
    override fun hashCode(): Int {
      return _interval.hashCode()
    }
    
    override fun equals(other: Any?): Boolean {
      if (other === this) {
        return true
      }
      if (other is ListItem) {
        return _interval == other._interval
      }
      if (other is TimeInterval) {
        return _interval == other
      }
      return false
    }
  }
  
  companion object {
    /**
     * Default list of intervals for graphing.
     */
    private val INTERVAL_LIST = arrayOf(
      TimeInterval.DAY,
      TimeInterval.WEEK,
      TimeInterval.MONTH,
      TimeInterval.QUARTER,
      TimeInterval.YEAR
    )
  }
}