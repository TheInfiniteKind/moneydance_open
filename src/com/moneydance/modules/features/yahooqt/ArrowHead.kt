/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import java.awt.Graphics2D
import java.awt.Point
import java.awt.Polygon
import java.awt.RenderingHints
import java.awt.geom.Point2D
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * Class capable of drawing an arrow head. See [ArrowIcon] for more information. Note that
 * the color or opacity of the arrow head (or antialiasing, etc.) is not defined by this class, it
 * simply draws the polygon and fills it if requested.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class ArrowHead
  (lineStart: Point2D, lineEnd: Point2D, width: Double,
   height: Double, private val _filled: Boolean) {
  private val arrowHead: Polygon
  
  /**
   * Constructor to allow immutability. See [ArrowIcon] for a description of the meaning
   * of the parameters.
   *
   * @param lineStart  The start of the line specifying the arrow's direction.
   * @param lineEnd    The end of the line specifying the arrow's direction (arrow's tip).
   * @param width      The width of the arrow.
   * @param height     The height/length of the arrow.
   * @param filled     True to fill the arrow head, false to draw it as an outline.
   */
  init {
    // determine how to rotate the arrow head from the line direction
    val direction = atan2(
      lineEnd.y - lineStart.y,
      lineEnd.x - lineStart.x
    )
    arrowHead = Polygon()
    
    // start at the tip
    arrowHead.addPoint(0, 0)
    // right point
    val p1 = _rotate(width / 2.0, height, direction)
    arrowHead.addPoint(p1.x, p1.y)
    // left point
    val p2 = _rotate(-width / 2.0, height, direction)
    arrowHead.addPoint(p2.x, p2.y)
    // back to the tip to close the polygon
    arrowHead.addPoint(0, 0)
    arrowHead.translate(lineEnd.x.toInt(), lineEnd.y.toInt())
  }
  
  
  /**//////////////////////////////////////////////////////////////////////////////////////////// */ // Public Methods
  /**//////////////////////////////////////////////////////////////////////////////////////////// */
  fun draw(g: Graphics2D) {
    val oldHint = g.getRenderingHint(RenderingHints.KEY_ANTIALIASING)
    g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
    g.drawPolygon(arrowHead)
    if (_filled) {
      g.fillPolygon(arrowHead)
    }
    g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, oldHint)
  }
  
  /**//////////////////////////////////////////////////////////////////////////////////////////// */ // Private Methods
  /**//////////////////////////////////////////////////////////////////////////////////////////// */
  private fun _rotate(x: Double, y: Double, dir: Double): Point {
    val p = Point()
    
    val radius = sqrt(x * x + y * y)
    val inner = atan2(y, x) + dir + Math.PI / 2.0
    p.setLocation(radius * cos(inner), radius * sin(inner))
    return p
  }
}
