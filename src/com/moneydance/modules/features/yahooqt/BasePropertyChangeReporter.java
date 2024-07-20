package com.moneydance.modules.features.yahooqt;

import javax.swing.event.SwingPropertyChangeSupport;
import java.beans.PropertyChangeListener;

public class BasePropertyChangeReporter {
    public static final String ALL_PROPERTIES = "UpdateAll";
    protected final SwingPropertyChangeSupport eventNotify = new SwingPropertyChangeSupport(this);

    public BasePropertyChangeReporter() {
    }

    public void addPropertyChangeListener(PropertyChangeListener listener) {
        this.eventNotify.addPropertyChangeListener(listener);
    }

    public void removePropertyChangeListener(PropertyChangeListener listener) {
        this.eventNotify.removePropertyChangeListener(listener);
    }

    protected void notifyPropertyChanged(String propertyName, Object oldValue, Object newValue) {
        this.eventNotify.firePropertyChange(propertyName, oldValue, newValue);
    }

    public void notifyAllListeners() {
        this.eventNotify.firePropertyChange("UpdateAll", (Object)null, (Object)null);
    }
}
