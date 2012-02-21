/*************************************************************************\
* Copyright (C) 2009-2012 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.DateRangeChooser;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.util.CustomDateFormat;

import javax.swing.Box;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.event.DocumentListener;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

import java.awt.GridBagLayout;
import java.awt.event.FocusListener;

/**
 * <p>Two date pickers, one 'from date' and one 'to date', combined.</p>
 *
 * @author Kevin Menningen
 * @version Build 83
 * @since 1.0
 */
class DatePickerGroup extends JPanel
{
    private final DateRangeChooser _dateRanger;

    /**
     * Constructor with needed information to create the view
     * @param mdGui     User interface object
     */
    DatePickerGroup(final MoneydanceGUI mdGui)
    {
        _dateRanger = new DateRangeChooser(mdGui);
        layoutUI();
    }

    String getDateRangeKey()
    {
        final int selectedIndex = ((JComboBox) _dateRanger.getChoice()).getSelectedIndex();
        return _dateRanger.getOption(selectedIndex);
    }
    void setDateRangeKey(final String dateRangeKey)
    {
        // if not custom, this will set the date range to a pre-defined range
        _dateRanger.setOption(dateRangeKey);
    }

    JDateField getFromDatePicker()
    {
        return (JDateField)_dateRanger.getStartField();
    }

    JDateField getToDatePicker()
    {
        return (JDateField)_dateRanger.getEndField();
    }

    void addChangeListener(final DocumentListener changeListener)
    {
        getFromDatePicker().getDocument().addDocumentListener(changeListener);
        getToDatePicker().getDocument().addDocumentListener(changeListener);
    }

    public void addFocusListener(final FocusListener listener)
    {
        _dateRanger.getChoice().addFocusListener(listener);
        getFromDatePicker().addFocusListener(listener);
        getToDatePicker().addFocusListener(listener);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void layoutUI()
    {
        setLayout( new GridBagLayout() );
        // give the chooser more weight than the date fields
        add(_dateRanger.getChoice(), GridC.getc(0, 0).wx(6).fillx());
        add(Box.createHorizontalStrut(UiUtil.HGAP), GridC.getc(1,0));
        add(getFromDatePicker(), GridC.getc(2, 0).wx(2).fillx());
        add(Box.createHorizontalStrut(UiUtil.HGAP), GridC.getc(3,0));
        add(getToDatePicker(), GridC.getc(4, 0).wx(2).fillx());
    }
}
