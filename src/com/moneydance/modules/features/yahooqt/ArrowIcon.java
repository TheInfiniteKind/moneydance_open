/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import javax.swing.Icon;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import java.awt.Color;
import java.awt.Component;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.Point2D;

/**
 * <p>ArrowIcon is an icon with given arrow shape, defined by the direction, enable status, and
 * size (length and width).</p>
 *
 * <p>Here's a diagram:</p>
 * <pre>
 *      A
 *      |\
 *      | \
 *      C--E
 *      | /
 *      |/
 *      B
 * </pre>
 * <p>where distance C - E is the length of the arrow, while distance A - B is the width of the
 * arrow. A width of zero is not allowed, but a length of zero is allowed and creates a bar of
 * the specified width.</p>
 *
 * <p>When a triangle shape is selected, the {@link ArrowHead} class is used to draw the
 * triangle.</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class ArrowIcon implements Icon
{
    /** Property to read from the UI manager for color. */
    private static final String BUTTON_TEXT_PROPERTY = "Button.foreground";
    /** Property to read from the UI manager for disabled color. */
    private static final String BUTTON_TEXT_DISABLED_PROPERTY = "Button.disabledText";

    /**
     * The length of the arrow icon.
     */
    private static final int DEFAULT_ICON_LENGTH = 9;

    /**
     * The width of the arrow icon.
     */
    private static final int DEFAULT_ICON_WIDTH = 9;

    /**
     * The arrow should point to the south.
     */
    public static final int SOUTH = SwingConstants.SOUTH;

    /**
     * The arrow should point to the north.
     */
    public static final int NORTH = SwingConstants.NORTH;

    /**
     * The arrow should point to the east.
     */
    public static final int EAST = SwingConstants.EAST;

    /**
     * The arrow should point to the west.
     */
    public static final int WEST = SwingConstants.WEST;

    /**
     * Width of the arrow icon, with respect to the point of the arrow.
     */
    private final int _width;
    /**
     * Length of the arrow icon, with respect to the point of the arrow.
     */
    private final int _length;

    /**
     * Direction of the icon. Could be SwingConstants.SOUTH, SwingConstants.NORTH,
     * SwingConstants.EAST, or SwingConstants.WEST.
     */
    private final int _direction;

    /**
     * Enable status of the arrow icon.
     */
    private boolean _isEnabled;

    /**
     * The graphical shape object to draw when using a triangle shape.
     */
    private final ArrowHead _triangleShape;

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Construction
    //////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Create an ArrowIcon with the given direction and enablement status and the default size and
     * length.
     *
     * @param direction Direction of the arrow, could be SwingConstants.SOUTH, SwingConstants.NORTH,
     *                  SwingConstants.EAST, or SwingConstants.WEST
     * @param isEnabled Represents the enable status of the ArrowIcon. Paint in foreground text
     *                  color if true, or disabled color if false.
     */
    public ArrowIcon( final int direction, final boolean isEnabled )
    {
        this( direction, isEnabled, DEFAULT_ICON_LENGTH, DEFAULT_ICON_WIDTH );
    }

    /**
     * <p>Create an ArrowIcon with given direction, enable status, shape, and size.
     * To get the real height and width of the icon need to use {@link #getIconHeight} and
     * {@link #getIconWidth}. </p>
     *
     * @param direction direction of the arrow, could be SwingConstants.SOUTH, SwingConstants.NORTH,
     * SwingConstants.EAST, or SwingConstants.WEST
     * @param isEnabled Represents the enable status of the ArrowIcon. Paint in foreground
     * text color if true, or disabled color if false.
     * @param length The length of the icon, see the {@link ArrowIcon class notes}. If less than
     * zero, length is set to zero.
     * @param width The width of the icon, see the {@link ArrowIcon class notes}. If less than one,
     * width is set to one.
     */
    public ArrowIcon( final int direction, final boolean isEnabled, final int length,
                      final int width )
    {
        _direction = direction;
        _isEnabled = isEnabled;
        if ( length >= 0 )
        {
            _length = length;
        }
        else
        {
            _length = 0;
        }
        if ( width >= 1 )
        {
            _width = width;
        }
        else
        {
            _width = 1;
        }

        _triangleShape = buildTriangleShape();
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Icon Interface
    //////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Draw the icon.
     *
     * @param comp Component parameter.
     * @param graphics Graphics.
     * @param xValue Left position.
     * @param yValue Top position.
     */
    public void paintIcon(final Component comp,
                          final Graphics graphics,
                          final int xValue,
                          final int yValue)
    {
        Graphics2D g2d = (Graphics2D)graphics.create();
        paintTriangle(g2d, xValue, yValue);
        g2d.dispose();
    }

    /**
     * Returns the icon's width.
     *
     * @return an int specifying the fixed width of the icon.
     */
    public int getIconWidth()
    {
        int width = 0;

        if (_direction == SwingConstants.SOUTH || _direction == SwingConstants.NORTH)
        {
            // vertical orientation, the width is the width of the arrow
            width = _width;
        }
        else if (_direction == SwingConstants.EAST || _direction == SwingConstants.WEST)
        {
            // horizontal orientation, the width is the length of the arrow, plus one
            // because a length of zero is a bar
            width = _length + 1;
        }

        return width;
    }

    /**
     * Returns the icon's height.
     *
     * @return an int specifying the fixed height of the icon.
     */
    public int getIconHeight()
    {
        int result = 0;

        if (_direction == SwingConstants.SOUTH || _direction == SwingConstants.NORTH)
        {
            // vertical orientation, the height is the length, plus one since length of
            // zero means the arrow is a bar
            result = _length + 1;
        }
        else if (_direction == SwingConstants.EAST || _direction == SwingConstants.WEST)
        {
            // horizontal orientation, the height is the width
            result = _width;
        }

        return result;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Public Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Get the arrow icon direction.
     *
     * @return arrow direction. SwingConstants.SOUTH, SwingConstants.NORTH, SwingConstants.EAST,
     * or SwingConstants.WEST.
     */
    public int getDirection()
    {
        return _direction;
    }

    /**
     * Set the enable status.
     *
     * @param isEnabled true if enabled, false otherwise.
     */
    public void setEnabled(final boolean isEnabled)
    {
        _isEnabled = isEnabled;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Private Methods
    //////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * @return A triangle shape of the right size and orientation.
     */
    private ArrowHead buildTriangleShape()
    {
        final ArrowHead triangleShape;

        // The length and width are subtracted by 1 because experimentally this produced the
        // correct results
        double length = _length - 1.0;
        if ( length <= 0.0 )
        {
            length = 1.0;
        }
        double span = _width - 1.0;
        if ( span <= 0.0 )
        {
            span = 1.0;
        }

        switch (_direction)
        {
            case SwingConstants.NORTH:
                // points upward, length (C-E) is vertical and width (A-B) is horizontal
                triangleShape =
                        new ArrowHead(new Point2D.Double(_width / 2.0, _length), // point C
                                new Point2D.Double(_width / 2.0, 0.0),           // point E
                                span, length, true);
                break;

            case SwingConstants.EAST:
                // points to the right, length is horizontal and width is vertical
                triangleShape =
                        new ArrowHead(new Point2D.Double(0.0, _width / 2.0),    // point C
                                new Point2D.Double(_length, _width / 2.0),      // point E
                                span, length, true);
                break;

            case SwingConstants.WEST:
                // points to the left, length is horizontal and width is vertical
                triangleShape =
                        new ArrowHead(new Point2D.Double(_length, _width / 2.0), // point C
                                new Point2D.Double(0.0, _width / 2.0),           // point E
                                span, length, true);
                break;

            case SwingConstants.SOUTH:
                // points downward, length is vertical and width is horizontal
                triangleShape =
                        new ArrowHead(new Point2D.Double(_width / 2.0, 0.0),     // point C
                                new Point2D.Double(_width / 2.0, _length),       // point E
                                span, length, true);
                break;

            default:
                triangleShape = null;
                break;
        } // switch

        return triangleShape;
    } // buildTriangleShape()

    /**
     * Paint the triangle arrow of the button.
     *
     * @param graphics Graphics.
     * @param left left of the icon.
     * @param top top of the icon.
     */
    private void paintTriangle(final Graphics2D graphics, final int left, final int top)
    {
        if (_width < 1)
        {
            // should never happen
            return;
        }

        final Color oldColor = graphics.getColor();
        graphics.translate(left, top);
        if(_isEnabled)
        {
            graphics.setColor( UIManager.getColor( BUTTON_TEXT_PROPERTY ) );
        }
        else
        {
            graphics.setColor( UIManager.getColor( BUTTON_TEXT_DISABLED_PROPERTY) );
        }

        if ( _triangleShape != null )
        {
            _triangleShape.draw(graphics);
        }

        graphics.translate(-left, -top);
        graphics.setColor(oldColor);
    }

}
