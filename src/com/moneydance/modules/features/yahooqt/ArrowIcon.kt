/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import java.awt.Component
import java.awt.Graphics
import java.awt.Graphics2D
import java.awt.geom.Point2D
import javax.swing.Icon
import javax.swing.SwingConstants
import javax.swing.UIManager

/**
 *
 * ArrowIcon is an icon with given arrow shape, defined by the direction, enable status, and
 * size (length and width).
 *
 *
 * Here's a diagram:
 * <pre>
 * A
 * |\
 * | \
 * C--E
 * | /
 * |/
 * B
</pre> *
 *
 * where distance C - E is the length of the arrow, while distance A - B is the width of the
 * arrow. A width of zero is not allowed, but a length of zero is allowed and creates a bar of
 * the specified width.
 *
 *
 * When a triangle shape is selected, the [ArrowHead] class is used to draw the
 * triangle.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class ArrowIcon @JvmOverloads constructor(
  /**
   * Direction of the icon. Could be SwingConstants.SOUTH, SwingConstants.NORTH,
   * SwingConstants.EAST, or SwingConstants.WEST.
   */
  val direction: Int,
  /**
   * Enable status of the arrow icon.
   */
  private var _isEnabled: Boolean, length: Int = DEFAULT_ICON_LENGTH,
  width: Int = DEFAULT_ICON_WIDTH) : Icon {
  /**
   * Width of the arrow icon, with respect to the point of the arrow.
   */
  private val _width = if (width >= 1) {
    width
  } else {
    1
  }
  
  /**
   * Length of the arrow icon, with respect to the point of the arrow.
   */
  private val _length = if (length >= 0) {
    length
  } else {
    0
  }
  
  /**
   * The graphical shape object to draw when using a triangle shape.
   */
  private val _triangleShape: ArrowHead?
  
  /**
   *
   * Create an ArrowIcon with given direction, enable status, shape, and size.
   * To get the real height and width of the icon need to use [.getIconHeight] and
   * [.getIconWidth].
   *
   * @param direction direction of the arrow, could be SwingConstants.SOUTH, SwingConstants.NORTH,
   * SwingConstants.EAST, or SwingConstants.WEST
   * @param _isEnabled Represents the enable status of the ArrowIcon. Paint in foreground
   * text color if true, or disabled color if false.
   * @param length The length of the icon, see the [class notes][ArrowIcon]. If less than
   * zero, length is set to zero.
   * @param width The width of the icon, see the [class notes][ArrowIcon]. If less than one,
   * width is set to one.
   */
  init {
    _triangleShape = buildTriangleShape()
  }
  
  /**
  * Draw the icon.
  *
  * @param comp Component parameter.
  * @param graphics Graphics.
  * @param xValue Left position.
  * @param yValue Top position.
  */
  override fun paintIcon(comp: Component,
                         graphics: Graphics,
                         xValue: Int,
                         yValue: Int) {
    val g2d = graphics.create() as Graphics2D
    paintTriangle(g2d, xValue, yValue)
    g2d.dispose()
  }
  
  /**
   * Returns the icon's width.
   *
   * @return an int specifying the fixed width of the icon.
   */
  override fun getIconWidth(): Int {
    var width = 0
    
    if (direction == SwingConstants.SOUTH || direction == SwingConstants.NORTH) {
      // vertical orientation, the width is the width of the arrow
      width = _width
    } else if (direction == SwingConstants.EAST || direction == SwingConstants.WEST) {
      // horizontal orientation, the width is the length of the arrow, plus one
      // because a length of zero is a bar
      width = _length + 1
    }
    
    return width
  }
  
  /**
   * Returns the icon's height.
   *
   * @return an int specifying the fixed height of the icon.
   */
  override fun getIconHeight(): Int {
    var result = 0
    
    if (direction == SwingConstants.SOUTH || direction == SwingConstants.NORTH) {
      // vertical orientation, the height is the length, plus one since length of
      // zero means the arrow is a bar
      result = _length + 1
    } else if (direction == SwingConstants.EAST || direction == SwingConstants.WEST) {
      // horizontal orientation, the height is the width
      result = _width
    }
    
    return result
  }
  
  
  /**
   * Set the enable status.
   *
   * @param isEnabled true if enabled, false otherwise.
   */
  fun setEnabled(isEnabled: Boolean) {
    _isEnabled = isEnabled
  }
  
  
  /**
   * @ return A triangle shape of the right size and orientation.
  */
  private fun buildTriangleShape(): ArrowHead? {
    val triangleShape: ArrowHead?
    
    // The length and width are subtracted by 1 because experimentally this produced the
    // correct results
    var length = _length - 1.0
    if (length <= 0.0) {
      length = 1.0
    }
    var span = _width - 1.0
    if (span <= 0.0) {
      span = 1.0
    }
    
    triangleShape = when (direction) {
      SwingConstants.NORTH ->                 // points upward, length (C-E) is vertical and width (A-B) is horizontal
        ArrowHead(
          Point2D.Double(_width / 2.0, _length.toDouble()),  // point C
          Point2D.Double(_width / 2.0, 0.0),  // point E
          span, length, true
        )
      
      SwingConstants.EAST ->                 // points to the right, length is horizontal and width is vertical
        ArrowHead(
          Point2D.Double(0.0, _width / 2.0),  // point C
          Point2D.Double(_length.toDouble(), _width / 2.0),  // point E
          span, length, true
        )
      
      SwingConstants.WEST ->                 // points to the left, length is horizontal and width is vertical
        ArrowHead(
          Point2D.Double(_length.toDouble(), _width / 2.0),  // point C
          Point2D.Double(0.0, _width / 2.0),  // point E
          span, length, true
        )
      
      SwingConstants.SOUTH ->                 // points downward, length is vertical and width is horizontal
        ArrowHead(
          Point2D.Double(_width / 2.0, 0.0),  // point C
          Point2D.Double(_width / 2.0, _length.toDouble()),  // point E
          span, length, true
        )
      
      else -> null
    } // switch
    
    return triangleShape
  }
  
  /**
   * Paint the triangle arrow of the button.
   *
   * @param graphics Graphics.
   * @param left left of the icon.
   * @param top top of the icon.
   */
  private fun paintTriangle(graphics: Graphics2D, left: Int, top: Int) {
    if (_width < 1) {
      // should never happen
      return
    }
    
    val oldColor = graphics.color
    graphics.translate(left, top)
    if (_isEnabled) {
      graphics.color = UIManager.getColor(BUTTON_TEXT_PROPERTY)
    } else {
      graphics.color = UIManager.getColor(BUTTON_TEXT_DISABLED_PROPERTY)
    }
    
    _triangleShape?.draw(graphics)
    
    graphics.translate(-left, -top)
    graphics.color = oldColor
  }
  
  companion object {
    /** Property to read from the UI manager for color.  */
    private const val BUTTON_TEXT_PROPERTY = "Button.foreground"
    
    /** Property to read from the UI manager for disabled color.  */
    private const val BUTTON_TEXT_DISABLED_PROPERTY = "Button.disabledText"
    
    /**
     * The length of the arrow icon.
     */
    private const val DEFAULT_ICON_LENGTH = 9
    
    /**
     * The width of the arrow icon.
     */
    private const val DEFAULT_ICON_WIDTH = 9
    
    /**
     * The arrow should point to the south.
     */
    const val SOUTH: Int = SwingConstants.SOUTH
    
    /**
     * The arrow should point to the north.
     */
    const val NORTH: Int = SwingConstants.NORTH
    
    /**
     * The arrow should point to the east.
     */
    const val EAST: Int = SwingConstants.EAST
    
    /**
     * The arrow should point to the west.
     */
    const val WEST: Int = SwingConstants.WEST
  }
}
