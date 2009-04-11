package com.moneydance.modules.features.findandreplace;

import javax.swing.event.SwingPropertyChangeSupport;
import java.beans.PropertyChangeListener;

/**
 * <p>Class to provide simple property change reporter support.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public class BasePropertyChangeReporter
{
    /** The encapsulated notification object. */
    final SwingPropertyChangeSupport _eventNotify;

    BasePropertyChangeReporter()
    {
        _eventNotify = new SwingPropertyChangeSupport( this );
    }

    /**
     * Add a PropertyChangeListener to the listener list. The listener is registered for all
     * properties. The same listener object may be added more than once, and will be called as
     * many times as it is added. If listener is null, no exception is thrown and no action is
     * taken.
     * @param listener The PropertyChangeListener to be added
     */
    void addPropertyChangeListener(PropertyChangeListener listener)
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
    void removePropertyChangeListener(PropertyChangeListener listener)
    {
        _eventNotify.removePropertyChangeListener( listener );
    }

    /**
     * Send a generic property change notification to all listeners.
     */
    void notifyAllListeners()
    {
        _eventNotify.firePropertyChange(N12EFindAndReplace.ALL_PROPERTIES, null, null);
    }
}
