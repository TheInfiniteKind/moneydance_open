/*
 * TableDecorator.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 16, 2008
 * Time: 7:52:26 PM
 */


package com.moneydance.modules.features.findandreplace;

import java.awt.Component;
import java.util.List;
import java.util.ArrayList;

/**
 * <p>Maintains a list of decorators for a table.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
final class TableDecorator
{
    /**
     * List of the currently installed decorators.
     */
    private final List<IDecorator> _decorators;

    /**
     * Initialize the decoration process with an empty list of decorators.
     */
    public TableDecorator()
    {
        _decorators = new ArrayList<IDecorator>();
    }

    /**
     * Add a decorator to the end of the decorator list. Null values are ignored.
     *
     * @param decorator The decorator to add to the list.
     */
    public void addDecorator( final IDecorator decorator )
    {
        if ( !_decorators.contains( decorator ) )
        {
            _decorators.add( decorator );
        }
    }

    /**
     * Removes a decorator from the list of decorators. Null values are ignored.
     *
     * @param decorator The decorator to remove.
     */
    public void removeDecorator( final IDecorator decorator )
    {
        _decorators.remove( decorator );
    }

    /**
     * Decorate the component with the decorators. Note: a decorators decorations maybe overwritten
     * by a later decorators decorations, the order of decorators in the list does matter.
     *
     * @param component The component to decorate.
     * @param model     The component model for the components parent.
     * @return The decorated component.
     * @see DecoratorComponentModel
     */
    public Component decorate( final Component component,
                               final DecoratorComponentModel model )
    {
        Component decorated = component;
        if ( decorated != null )
        {
            for ( final IDecorator decorator : _decorators )
            {
                decorated = decorator.apply( component, model );
            }
        }
        return decorated;
    }
}
