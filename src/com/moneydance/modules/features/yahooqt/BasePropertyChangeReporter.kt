package com.moneydance.modules.features.yahooqt

import java.beans.PropertyChangeListener
import javax.swing.event.SwingPropertyChangeSupport

open class BasePropertyChangeReporter {
  protected val eventNotify: SwingPropertyChangeSupport = SwingPropertyChangeSupport(this)
  
  fun addPropertyChangeListener(listener: PropertyChangeListener?) {
    eventNotify.addPropertyChangeListener(listener)
  }
  
  fun removePropertyChangeListener(listener: PropertyChangeListener?) {
    eventNotify.removePropertyChangeListener(listener)
  }
  
  protected fun notifyPropertyChanged(propertyName: String?, oldValue: Any?, newValue: Any?) {
    eventNotify.firePropertyChange(propertyName, oldValue, newValue)
  }
  
  fun notifyAllListeners() {
    eventNotify.firePropertyChange("UpdateAll", null as Any?, null as Any?)
  }
  
  companion object {
    const val ALL_PROPERTIES: String = "UpdateAll"
  }
}
