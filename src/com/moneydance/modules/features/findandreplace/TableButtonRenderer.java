/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import javax.swing.table.TableCellRenderer;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.JButton;
import javax.swing.JTable;
import javax.swing.UIManager;
import javax.swing.JToggleButton;
import javax.swing.border.Border;
import java.awt.Component;
import java.awt.Color;

/**
 * <p>Table renderer for a button column.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TableButtonRenderer extends DefaultTableCellRenderer implements TableCellRenderer
{

    public TableButtonRenderer()
    {
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus, int row, int column)
    {
        setText(Integer.toString(row + 1));
        if (isSelected)
        {
            setForeground(table.getSelectionForeground());
            setBackground(table.getSelectionBackground());
        }
        else
        {
            setForeground(UIManager.getColor("TableHeader.foreground"));
            setBackground(UIManager.getColor("TableHeader.background"));
        }

        setFont(UIManager.getFont("TableHeader.font"));

        if (hasFocus)
        {
            setBorder(UIManager.getBorder("TableHeader.focusCellBorder"));

            if (!isSelected && table.isCellEditable(row, column))
            {
                Color col;
                col = UIManager.getColor("TableHeader.focusCellForeground");
                if (col != null)
                {
                    super.setForeground(col);
                }
                col = UIManager.getColor("TableHeader.focusCellBackground");
                if (col != null)
                {
                    super.setBackground(col);
                }
            }
        }
        else
        {
            setBorder(UIManager.getBorder("TableHeader.cellBorder"));
        }

        setValue(value);

        return this;
    }
}
