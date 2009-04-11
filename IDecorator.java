/*
 * IDecorator.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 16, 2008
 * Time: 7:46:31 PM
 */

package com.moneydance.modules.features.findandreplace;

import java.awt.Component;

/**
 * <p>Decoration support for a component.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
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