/*
 * AlternateRowTableDecorator.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 16, 2008
 * Time: 7:44:40 PM
 */


package com.moneydance.modules.features.findandreplace;

import javax.swing.UIManager;
import java.awt.Color;
import java.awt.Component;

/**
 * <p>Colors rows in a table in two alternating background colors.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public class AlternateRowTableDecorator implements IDecorator
{
    /**
     * The background color for odd rows in the table.
     */
    private final Color _oddColor;

    /**
     * The background color for event rows in the table.
     */
    private final Color _evenColor;

    /**
     * Initialize the default alternating row decorator.
     */
    public AlternateRowTableDecorator()
    {
        this( UIManager.getColor( N12EFindAndReplace.TABLE_ODD_BACKGROUND ),
              UIManager.getColor( N12EFindAndReplace.TABLE_EVEN_BACKGROUND ) );
    }

    /**
     * Initialize the default alternating row decorator.
     *
     * @param odd          The odd color.
     * @param even         The even color.
     */
    private AlternateRowTableDecorator( final Color odd, final Color even )
    {
        _oddColor = odd;
        _evenColor = even;
    }

    /**
     * {@inheritDoc}
     */
    public Component apply( final Component component, final DecoratorComponentModel model )
    {
        if ( model.editing )
        {
            return component;
        }

        if ( model.row % 2 == 1 )
        {
            if ( !model.isSelected() )
            {
                component.setBackground( _oddColor );
            }
        }
        else
        {
            if ( !model.isSelected() )
            {
                component.setBackground( _evenColor );
            }
        }
        return component;
    }
}
