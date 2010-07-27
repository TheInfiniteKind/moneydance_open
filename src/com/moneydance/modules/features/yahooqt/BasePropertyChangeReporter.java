package com.moneydance.modules.features.yahooqt;

import javax.swing.event.SwingPropertyChangeSupport;
import java.beans.PropertyChangeListener;

/**
 * <p>Class to provide simple property change reporter support.</p>

 * @author Kevin Menningen
 */
public class BasePropertyChangeReporter
{
    public static final String ALL_PROPERTIES = "UpdateAll";

    /** The encapsulated notification object. */
    protected final SwingPropertyChangeSupport _eventNotify;

    public BasePropertyChangeReporter()
    {
        this(false);
    }

    public BasePropertyChangeReporter(boolean notifyOnEDT)
    {
        _eventNotify = new SwingPropertyChangeSupport( this, notifyOnEDT );
    }

    /**
     * Add a PropertyChangeListener to the listener list. The listener is registered for all
     * properties. The same listener object may be added more than once, and will be called as
     * many times as it is added. If listener is null, no exception is thrown and no action is
     * taken.
     * @param listener The PropertyChangeListener to be added
     */
    public void addPropertyChangeListener(PropertyChangeListener listener)
    {
        _eventNotify.addPropertyChangeListener( listener );
    }

    /**
     * Remove a PropertyChangeListener from the listener list. This removes a
     * PropertyChangeListener that was registered for all properties. If listener was added more
     * than once to the same event source, it will be notified one less time after being removed.
     * If listener is null, or was never added, no exception is thrown and no action is taken.
     * @param listener The PropertyChangeListener to be removed
     */
    public void removePropertyChangeListener(PropertyChangeListener listener)
    {
        _eventNotify.removePropertyChangeListener( listener );
    }

    /**
     * Send a generic property change notification to all listeners.
     */
    public void notifyAllListeners()
    {
        _eventNotify.firePropertyChange(ALL_PROPERTIES, null, null);
    }
}
