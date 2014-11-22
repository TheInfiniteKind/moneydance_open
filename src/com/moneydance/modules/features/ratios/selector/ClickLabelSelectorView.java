/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios.selector;

import com.moneydance.util.UiUtil;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.UIManager;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.Shape;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.RoundRectangle2D;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.List;

/**
 * The view for a selector that allows you to click on a label to select an item.
 */
class ClickLabelSelectorView
    extends JPanel
    implements PropertyChangeListener {
  private static final int BETWEEN_ITEM_GAP = 20;
  private static final int VERTICAL_GAP = 4;
  private static final int HORZ_MARGIN = 4;
  private static final Dimension DEFAULT_SIZE = new Dimension(100, 17);

  private final ClickLabelSelectorController _controller;

  private Dimension _cellSize = DEFAULT_SIZE;
  private Dimension _preferredComponentSize = null;

  private Color _selectedBackground = UIManager.getColor("textHighlight");
  private Color _selectedForeground = UIManager.getColor("textHighlightText");
  private Color _normalForeground = UIManager.getColor("controlText");

  ClickLabelSelectorView(final ClickLabelSelectorController controller) {
    super(new GridLayout(1, 1));
    setOpaque(true);
    _controller = controller;
    setFocusable(true);
    addMouseListener(new PanelClickListener());
  }

  void setSelectionBackground(final Color color) {
    _selectedBackground = color;
    repaint();
  }

  void setSelectionForeground(final Color color) {
    _selectedForeground = color;
    repaint();
  }

  @Override
  public Dimension getPreferredSize() {
    final Graphics graphics = getGraphics();
    if (graphics == null) return DEFAULT_SIZE; // punt
    return calculateSize(graphics);
  }

  public Dimension getMinimumSize() {
    return getPreferredSize();
  }

  public void propertyChange(PropertyChangeEvent event) {
    final String eventName = event.getPropertyName();
    if (ClickLabelSelectorModel.SELECTION_CHANGE.equals(eventName)) {
      // new selection
      repaint();
    }
  }

  public void setForeground(Color color) {
    super.setForeground(color);
    _normalForeground = color;
    repaint();
  }

  protected void paintComponent(Graphics g) {
    Graphics2D g2 = (Graphics2D) g;

    // fill entire background
    Rectangle oldClip = g2.getClipBounds();
    final Insets insets = getInsets();
    Rectangle drawBounds = new Rectangle(insets.left, insets.top,
                                   getWidth() - insets.left - insets.right,
                                   getHeight() - insets.top - insets.bottom);
    g2.clip(drawBounds);
    g2.setPaint(getBackground());
    g2.fill(drawBounds);
    // fill item that is selected
    paintSelectionBackground(g2, drawBounds);
    // draw the text on the top
    drawText(g2, _controller.getItemList(), drawBounds);
    // restore previous clip
    g2.setClip(oldClip);
  }

  private void paintSelectionBackground(final Graphics2D g2, final Rectangle drawBounds) {
    // turning antialiasing on early helps because the .fill() methods use antialiasing for a
    // nice appearance without resorting to a border line
    Object oldHint = g2.getRenderingHint(RenderingHints.KEY_ANTIALIASING);
    g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

    // highlight area itself - labels will be centered in bounds, center the highlight on the label
    // Subtract 1 to leave an extra gap at the top of the line
    float arcRadius = (float)drawBounds.getHeight() - 1f;
    int index = _controller.getSelectedIndex();
    if (index < 0) return; // nothing is selected
    final double labelWidth = drawBounds.getWidth() / _controller.getItemCount();
    float labelCenter = (float)(labelWidth * index + (labelWidth / 2.0));
    float left = Math.max((float)drawBounds.getX(), (labelCenter - (_cellSize.width / 2.0f)));
    Shape thermo = new RoundRectangle2D.Float(left,
                                              (float)drawBounds.getY() + 1, // add a gap to the top
                                              _cellSize.width - 2.0f, // allow for extra arc width
                                              arcRadius,           // height is same as radius
                                              arcRadius + 1.0f,    // arc width
                                              arcRadius);          // arc height
    g2.setPaint(_selectedBackground);
    g2.fill(thermo);

    // clean up
    g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, oldHint);
  }

  private void drawText(Graphics2D g2, List<String> labels, final Rectangle drawBounds) {
    Object oldHint = g2.getRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING);
    g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, UiUtil.TEXT_ANTIALIAS_HINT);
    final int selectedIndex = _controller.getSelectedIndex();

    FontMetrics fontSizer = g2.getFontMetrics();
    // center the text on the centerline, then add the amount needed to go to the baseline.
    // Subtract 1 to bump the text up a bit.
    float toBaseline = Math.max(0, fontSizer.getHeight() / 2f - fontSizer.getDescent() - 1f);
    final float y = (float)drawBounds.getHeight() / 2f + toBaseline;
    final int count = labels.size();
    final double labelWidth = drawBounds.getWidth() / count;
    for (int index = 0; index < count; index++) {
      g2.setPaint((index == selectedIndex) ? _selectedForeground : _normalForeground);
      final String label = labels.get(index);
      float labelCenter = (float)(labelWidth * index + (labelWidth / 2.0));
      float x = labelCenter - fontSizer.stringWidth(label) / 2.0f;
      g2.drawString(label, x, y);
    }

    // clean up
    g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, oldHint);
  }

  private Dimension calculateSize(final Graphics graphics) {
    List<String> itemList = _controller.getItemList();
    if (itemList.isEmpty()) return DEFAULT_SIZE;
    // have we already computed the size?
    if ((_preferredComponentSize != null) && (getComponentCount() == itemList.size())) {
      return _preferredComponentSize;
    }
    // calculate the size
    final FontMetrics fontMetrics = graphics.getFontMetrics();
    final int height = fontMetrics.getHeight() + VERTICAL_GAP;
    int maxWidth = 0;
    for (final String item : itemList) maxWidth = Math.max(maxWidth, fontMetrics.stringWidth(item));
    // add an extra margin for antialiasing
    maxWidth += HORZ_MARGIN;
    // each item will be in a cell with space between
    _cellSize = new Dimension(maxWidth + BETWEEN_ITEM_GAP, height);
//    // re-add the labels
//    layoutUI(itemList);
    _preferredComponentSize = new Dimension(_cellSize.width * itemList.size(), height);
    return _preferredComponentSize;
  }

  private class PanelClickListener extends MouseAdapter {
    public void mouseReleased(MouseEvent e) {
      double width = ClickLabelSelectorView.this.getBounds().getWidth();
      int index = (int)Math.floor(e.getX() / (width / _controller.getItemCount()));
      _controller.setSelectedIndex(index);
    }
  }
}
