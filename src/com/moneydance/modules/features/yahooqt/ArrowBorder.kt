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
import java.awt.Insets
import java.util.concurrent.atomic.AtomicBoolean
import javax.swing.SwingConstants
import javax.swing.UIManager
import javax.swing.border.AbstractBorder

/**
 * A border that draws an arrow for a cell in a table.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class ArrowBorder @JvmOverloads constructor(iconLength: Int = ICON_LENGTH, iconWidth: Int = ICON_WIDTH, iconPadding: Int = ICON_PADDING,
                                            arrowVisible: Boolean = true, borderSize: Int = 0) : AbstractBorder() {
  /**
   * The enabled arrow icon.
   */
  private val _enabledIcon = ArrowIcon(SwingConstants.SOUTH, true, iconLength, iconWidth)
  
  /**
   * The disabled arrow icon.
   */
  private val _disableIcon = ArrowIcon(SwingConstants.SOUTH, false, iconLength, iconWidth)
  
  /**
   * True to display the arrow, false to hide it.
   */
  private val _arrowVisible = AtomicBoolean(true)
  
  /**
   * The border insets.
   */
  private val _insets = Insets(0, 6, 0, iconWidth + iconPadding * 2)
  
  /**
   * The width of the border line in addition to the arrow, or 0 for no line.
   */
  private val _borderSize: Int
  
  /**
   * Initialize the arrow border using the given length, width and padding.
   *
   * @param iconLength   The length of the arrow (back of the arrow to tip).
   * @param iconWidth    The width of the arrow (orthogonal to length).
   * @param iconPadding  The padding space to put around the arrow icon.
   * @param arrowVisible True to draw the arrow, false to not draw the arrow.
   * @param borderSize   Size in pixels of a border line in addition to the arrow, or 0 if no
   * additional border should be drawn.
   */
  /**
   * Initialize the arrow border using the default length, width and padding. The arrow is shown
   * by default and there is no line around the rectangle.
   */
  init {
    _arrowVisible.set(arrowVisible)
    _borderSize = borderSize
  }
  
  /**
   * {@inheritDoc}
   */
  override fun getBorderInsets(component: Component): Insets {
    return Insets(_insets.top, _insets.left, _insets.bottom, _insets.right)
  }
  
  /**
   * {@inheritDoc}
   */
  override fun getBorderInsets(component: Component, insets: Insets): Insets {
    insets.top = _insets.top
    insets.left = _insets.left
    insets.bottom = _insets.bottom
    insets.right = _insets.right
    return insets
  }
  
  /**
   * {@inheritDoc}
   */
  override fun paintBorder(component: Component,
                           g2d: Graphics,
                           xLoc: Int,
                           yLoc: Int,
                           width: Int,
                           height: Int) {
    // the enabled and disabled icons have the same height
    val yStart = height / 2 - _enabledIcon.iconHeight / 2
    
    if (isArrowVisible) {
      if (component.isEnabled) {
        _enabledIcon.paintIcon(component, g2d, width - _insets.right, yStart)
      } else {
        _disableIcon.paintIcon(component, g2d, width - _insets.right, yStart)
      }
    }
    
    if (_borderSize > 0) {
      val oldColor = g2d.color
      
      if (component.isEnabled) {
        g2d.color = UIManager.getColor("Label.foreground")
      } else {
        g2d.color = UIManager.getColor("Label.disabledForeground")
      }
      
      for (pixel in 0..<_borderSize) {
        g2d.drawRect(
          xLoc + pixel, yLoc + pixel,
          width - pixel - pixel - 1,
          height - pixel - pixel - 1
        )
      }
      g2d.color = oldColor
    }
  }
  
  var isArrowVisible: Boolean
    /**
     * @return True if the arrow should be visible, false if it should be hidden.
     */
    get() = _arrowVisible.get()
    /**
     * Define whether to draw the arrow or not.
     *
     * @param arrowVisible True if the arrow should be visible, false if it should be hidden.
     */
    set(arrowVisible) {
      _arrowVisible.set(arrowVisible)
    }
  
  companion object {
    /**
     * The arrow icon padding.
     */
    const val ICON_PADDING: Int = 3
    
    /**
     * The length of the arrow icon.
     */
    const val ICON_LENGTH: Int = 5
    
    /**
     * The width of the arrow icon.
     */
    const val ICON_WIDTH: Int = 9
  }
}
