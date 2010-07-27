/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import javax.swing.border.AbstractBorder;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import java.awt.Insets;
import java.awt.Component;
import java.awt.Graphics;
import java.awt.Color;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * A border that draws an arrow for a cell in a table.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class ArrowBorder extends AbstractBorder {
  /**
   * The enabled arrow icon.
   */
  private final ArrowIcon _enabledIcon;

  /**
   * The disabled arrow icon.
   */
  private final ArrowIcon _disableIcon;

  /**
   * True to display the arrow, false to hide it.
   */
  private final AtomicBoolean _arrowVisible = new AtomicBoolean(true);

  /**
   * The border insets.
   */
  private final Insets _insets;

  /**
   * The width of the border line in addition to the arrow, or 0 for no line.
   */
  private final int _borderSize;

  /**
   * The arrow icon padding.
   */
  public static final int ICON_PADDING = 3;
  /**
   * The length of the arrow icon.
   */
  public static final int ICON_LENGTH = 5;
  /**
   * The width of the arrow icon.
   */
  public static final int ICON_WIDTH = 9;

  /**
   * Initialize the arrow border using the default length, width and padding. The arrow is shown
   * by default and there is no line around the rectangle.
   */
  public ArrowBorder() {
    this(ICON_LENGTH, ICON_WIDTH, ICON_PADDING, true, 0);
  }

  /**
   * Initialize the arrow border using the given length, width and padding.
   *
   * @param iconLength   The length of the arrow (back of the arrow to tip).
   * @param iconWidth    The width of the arrow (orthogonal to length).
   * @param iconPadding  The padding space to put around the arrow icon.
   * @param arrowVisible True to draw the arrow, false to not draw the arrow.
   * @param borderSize   Size in pixels of a border line in addition to the arrow, or 0 if no
   *                     additional border should be drawn.
   */
  public ArrowBorder(final int iconLength, final int iconWidth, final int iconPadding,
                     final boolean arrowVisible, final int borderSize) {
    _enabledIcon = new ArrowIcon(SwingConstants.SOUTH, true, iconLength, iconWidth);
    _disableIcon = new ArrowIcon(SwingConstants.SOUTH, false, iconLength, iconWidth);
    _insets = new Insets(0, 6, 0, iconWidth + iconPadding * 2);
    _arrowVisible.set(arrowVisible);
    _borderSize = borderSize;
  }

  /**
   * {@inheritDoc}
   */
  @Override
  public Insets getBorderInsets(final Component component) {
    return new Insets(_insets.top, _insets.left, _insets.bottom, _insets.right);
  }

  /**
   * {@inheritDoc}
   */
  @Override
  public Insets getBorderInsets(final Component component, final Insets insets) {
    insets.top = _insets.top;
    insets.left = _insets.left;
    insets.bottom = _insets.bottom;
    insets.right = _insets.right;
    return insets;
  }

  /**
   * {@inheritDoc}
   */
  @Override
  public void paintBorder(final Component component,
                          final Graphics g2d,
                          final int xLoc,
                          final int yLoc,
                          final int width,
                          final int height) {
    // the enabled and disabled icons have the same height
    final int yStart = height / 2 - _enabledIcon.getIconHeight() / 2;

    if (isArrowVisible()) {
      if (component.isEnabled()) {
        _enabledIcon.paintIcon(component, g2d, width - _insets.right, yStart);
      } else {
        _disableIcon.paintIcon(component, g2d, width - _insets.right, yStart);
      }
    }

    if (_borderSize > 0) {
      final Color oldColor = g2d.getColor();

      if (component.isEnabled()) {
        g2d.setColor(UIManager.getColor("Label.foreground"));
      } else {
        g2d.setColor(UIManager.getColor("Label.disabledForeground"));
      }

      for (int pixel = 0; pixel < _borderSize; pixel++) {
        g2d.drawRect(xLoc + pixel, yLoc + pixel,
                width - pixel - pixel - 1,
                height - pixel - pixel - 1);
      }
      g2d.setColor(oldColor);
    }
  }

  /**
   * @return True if the arrow should be visible, false if it should be hidden.
   */
  public boolean isArrowVisible() {
    return _arrowVisible.get();
  }

  /**
   * Define whether to draw the arrow or not.
   *
   * @param arrowVisible True if the arrow should be visible, false if it should be hidden.
   */
  public void setArrowVisible(boolean arrowVisible) {
    _arrowVisible.set(arrowVisible);
  }
}
