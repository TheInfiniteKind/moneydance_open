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

import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.JTable;
import javax.swing.SwingConstants;
import java.awt.Component;
import java.awt.Font;
import java.awt.Color;

/**
 * <p>Displays cells in the find results table with special decoration.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class FindResultsTableCellRenderer 
  extends DefaultTableCellRenderer 
{
  protected MDColors colors;
  
  FindResultsTableCellRenderer(MoneydanceGUI mdGUI) {
    this.colors = mdGUI.getColors();
  }
  
    // implements javax.swing.table.TableCellRenderer
    @Override
    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected,
                                                   boolean hasFocus, int row, int column)
    {
        final Component result = super.getTableCellRendererComponent(table, value, isSelected,
                hasFocus, row, column);
      
        if (table.getModel() instanceof FindResultsTableModel) {
          int modelIndex = table.convertRowIndexToModel(row);
          final FindResultsTableModel tableModel = (FindResultsTableModel)table.getModel();
          final FindResultsTableEntry entry = tableModel.getEntry(modelIndex);
          
          if(isSelected) {
            result.setBackground(colors.registerSelectedBG);
            result.setForeground(colors.registerSelectedFG);
          } else {
            //result.setBackground(row % 2 == 0 ? colors.registerBG1 : colors.registerBG2);
            result.setBackground(Color.red);
            result.setForeground(getNormalForeground(tableModel, row));
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

    int getTextAlignment()
    {
        return SwingConstants.LEFT;
    }
}
