package com.moneydance.modules.features.findandreplace;

import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.JTable;
import java.awt.Component;
import java.awt.Font;
import java.awt.Color;

/**
 * <p>Displays cells in the find results table with special decoration.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.1
 * @since 1.0
 */
class FindResultsTableCellRenderer extends DefaultTableCellRenderer
{

    // implements javax.swing.table.TableCellRenderer
    @Override
    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected,
                                                   boolean hasFocus, int row, int column)
    {
        final Component result = super.getTableCellRendererComponent(table, value, isSelected,
                hasFocus, row, column);

        if (table.getModel() instanceof FindResultsTableModel)
        {
            int modelIndex = table.convertRowIndexToModel(row);
            final FindResultsTableModel tableModel = (FindResultsTableModel)table.getModel();
            final FindResultsTableEntry entry = tableModel.getEntry(modelIndex);
            if (!isSelected && entry.isApplied() && entry.isColumnModified(column))
            {
                final Font boldFont = result.getFont().deriveFont(Font.BOLD);
                result.setFont(boldFont);

                result.setForeground(Color.BLUE);
            }
            else
            {
                result.setForeground(getNormalForeground(tableModel, modelIndex));
            }

            setToolTipText(tableModel.getToolTipText(modelIndex));
        }

        return result;
    }

    Color getNormalForeground(FindResultsTableModel tableModel, int modelIndex)
    {
        return Color.BLACK;
    }
}
