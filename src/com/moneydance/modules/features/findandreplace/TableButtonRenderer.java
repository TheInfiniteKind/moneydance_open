/*************************************************************************\
 * Copyright (C) 2009-2015 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 \*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MDColors;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.*;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.DefaultTableCellRenderer;
import java.awt.*;

/**
 * <p>Table renderer for a button column.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TableButtonRenderer extends DefaultTableCellRenderer implements TableCellRenderer {

  protected MDColors colors;

  public TableButtonRenderer(MoneydanceGUI mdGUI) {
    super();
    this.colors = mdGUI.getColors();
  }

  @Override
  public void updateUI() {
    super.updateUI();
    //setOpaque(false);
  }

  public Component getTableCellRendererComponent(JTable table, Object value,
                                                 boolean isSelected, boolean hasFocus, int row, int column) {
    setText(Integer.toString(row + 1));

    final JComponent result = (JComponent) super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

    //here
    if (isSelected) {
      // make cell opaque only when selected
      result.setOpaque(true);
      setBackground(colors.registerSelectedBG);

      // FlatDark needs explicit foreground
      setForeground(colors.registerSelectedFG);

    } else {
      // transparent for unselected
      result.setOpaque(false);
      setForeground(colors.defaultTextForeground);
    }

    setValue(value);

    return this;
  }

}
