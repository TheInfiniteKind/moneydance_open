/*************************************************************************\
 * Copyright (C) 2009-2011 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 \*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MDColors;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.*;
import javax.swing.table.DefaultTableCellRenderer;
import java.awt.*;

/**
 * <p>Displays cells in the find results table with special decoration.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class FindResultsTableCellRenderer
  extends DefaultTableCellRenderer {
  protected MDColors colors;

  FindResultsTableCellRenderer(MoneydanceGUI mdGUI) {
    this.colors = mdGUI.getColors();
  }

  @Override
  public void updateUI() {
    super.updateUI();
    //setOpaque(false);
  }

  // implements javax.swing.table.TableCellRenderer
  @Override
  public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {

    final JComponent result = (JComponent) super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

    if (table.getModel() instanceof FindResultsTableModel tableModel) {
      int modelIndex = table.convertRowIndexToModel(row);
      final FindResultsTableEntry entry = tableModel.getEntry(modelIndex);

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

      if (!isSelected && entry.isApplied() && entry.isColumnModified(column)) {
        final Font boldFont = result.getFont().deriveFont(Font.BOLD);
        result.setFont(boldFont);
        result.setForeground(colors.secondaryTextFG);
      }

      setToolTipText(tableModel.getToolTipText(row));
      setHorizontalAlignment(getTextAlignment());
    }

    return result;
  }

  Color getNormalForeground(FindResultsTableModel tableModel, int index) {
    return colors.registerTextFG;
  }

  int getTextAlignment() {
    return SwingConstants.LEFT;
  }
}
