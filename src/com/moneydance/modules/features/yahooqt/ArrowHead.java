/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import java.awt.Polygon;
import java.awt.Point;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.geom.Point2D;

/**
 * Class capable of drawing an arrow head. See {@link ArrowIcon} for more information. Note that
 * the color or opacity of the arrow head (or antialiasing, etc.) is not defined by this class, it
 * simply draws the polygon and fills it if requested.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class ArrowHead
{
    private final Polygon arrowHead;
    private final boolean _filled;

    /**
     * Constructor to allow immutability. See {@link ArrowIcon} for a description of the meaning
     * of the parameters.
     *
     * @param lineStart  The start of the line specifying the arrow's direction.
     * @param lineEnd    The end of the line specifying the arrow's direction (arrow's tip).
     * @param width      The width of the arrow.
     * @param height     The height/length of the arrow.
     * @param filled     True to fill the arrow head, false to draw it as an outline.
     */
    public ArrowHead(final Point2D lineStart, final Point2D lineEnd, final double width,
                     final double height, final boolean filled)
    {
        _filled = filled;

        // determine how to rotate the arrow head from the line direction
        double direction = Math.atan2(lineEnd.getY() - lineStart.getY(),
                lineEnd.getX() - lineStart.getX());
        arrowHead = new Polygon();

        // start at the tip
        arrowHead.addPoint(0, 0);
        // right point
        Point p1 = _rotate(width / 2.0, height, direction);
        arrowHead.addPoint(p1.x, p1.y);
        // left point
        Point p2 = _rotate(-width / 2.0, height, direction);
        arrowHead.addPoint(p2.x, p2.y);
        // back to the tip to close the polygon
        arrowHead.addPoint(0, 0);
        arrowHead.translate((int)lineEnd.getX(), (int)lineEnd.getY());
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Public Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    public void draw(Graphics2D g)
    {
        final Object oldHint = g.getRenderingHint(RenderingHints.KEY_ANTIALIASING);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.drawPolygon(arrowHead);
        if (_filled)
        {
            g.fillPolygon(arrowHead);
        }
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, oldHint);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private Point _rotate(double x, double y, double dir)
    {
        Point p = new Point();

        final double radius = Math.sqrt(x * x + y * y);
        final double inner = Math.atan2(y, x) + dir + Math.PI / 2.0;
        p.setLocation(radius * Math.cos(inner), radius * Math.sin(inner));
        return p;
    }
}
