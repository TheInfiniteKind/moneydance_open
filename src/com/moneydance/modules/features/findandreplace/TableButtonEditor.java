/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import javax.swing.JToggleButton;
import javax.swing.JOptionPane;
import javax.swing.DefaultCellEditor;
import javax.swing.JCheckBox;
import javax.swing.JTable;
import javax.swing.table.JTableHeader;
import javax.swing.border.Border;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.Component;
import java.awt.Insets;

/**
 * <p>A class that allows a sticky button as a cell editor. Used for row selection.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TableButtonEditor extends DefaultCellEditor
{
    private final JToggleButton _button;
    private String _label;
    private int _row;

    TableButtonEditor()
    {
        this(new JCheckBox());
    }

    private TableButtonEditor(final JCheckBox checkBox)
    {
        super(checkBox);
        _button = new JToggleButton();
        _button.setOpaque(true);
        _button.setBorder(null);
        _button.setContentAreaFilled(false);

        _button.addActionListener(new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                fireEditingStopped();
            }
        });
        _row = -1;
    }

    public int getRow()
    {
        return _row;
    }

    public boolean getSelected()
    {
        return _button.isSelected();
    }

    public Component getTableCellEditorComponent(JTable table, Object value,
                                                 boolean isSelected, int row, int column)
    {
        if (isSelected)
        {
            _button.setForeground(table.getSelectionForeground());
            _button.setBackground(table.getSelectionBackground());
        }
        else
        {
            _button.setForeground(table.getForeground());
            _button.setBackground(table.getBackground());
        }
        _label = Integer.toString(row + 1);
        _button.setText(_label);
        _button.setSelected(isSelected);
        _row = row;
        return _button;
    }

    public Object getCellEditorValue()
    {
        return _label;
    }


}
