/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import java.awt.Component;

/**
 * <p>Decoration support for a component.</p>
 * 
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
public interface IDecorator
{
    /**
     * Decorate the component.
     *
     * @param component The component to decorate.
     * @param model     The component model for the components parent.
     * @return The decorated component.
     * @see DecoratorComponentModel
     */
    Component apply( final Component component, final DecoratorComponentModel model );
}