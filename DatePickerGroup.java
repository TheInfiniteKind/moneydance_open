package com.moneydance.modules.features.findandreplace;

import com.moneydance.awt.JDateField;
import com.moneydance.util.CustomDateFormat;

import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.event.DocumentListener;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

/**
 * <p>Two date pickers, one 'from date' and one 'to date', combined.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class DatePickerGroup extends JPanel
{
    private final JDateField _from;
    private final JDateField _to;

    /**
     * Constructor with needed information to create the view
     * @param formatter Date formatter
     * @param resources Localization resources
     */
    DatePickerGroup(CustomDateFormat formatter, final IResourceProvider resources)
    {
        _from = new JDateField(formatter);
        _to =  new JDateField(formatter);
        layoutUI(resources);
    }

    JDateField getFromDatePicker()
    {
        return _from;
    }

    JDateField getToDatePicker()
    {
        return _to;
    }

    void addChangeListener(final DocumentListener changeListener)
    {
        _from.getDocument().addDocumentListener(changeListener);
        _to.getDocument().addDocumentListener(changeListener);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void layoutUI(final IResourceProvider resources)
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, // from label
                UiUtil.HGAP,
                TableLayout.FILL,      // include
                UiUtil.HGAP,
                TableLayout.PREFERRED, // to label
                UiUtil.HGAP,
                TableLayout.FILL,      // exclude
            },

            // rows
            { TableLayout.PREFERRED }
        };

        setLayout(new TableLayout(sizes));

        final JLabel labelFrom = new JLabel(resources.getString(L10NFindAndReplace.FIND_BETWEEN));
        add(labelFrom, new TableLayoutConstraints( 0, 0 ));
        add(_from,  new TableLayoutConstraints( 2, 0 ));
        final JLabel labelTo = new JLabel(resources.getString(L10NFindAndReplace.FIND_AND));
        add(labelTo, new TableLayoutConstraints( 4, 0 ));
        add(_to, new TableLayoutConstraints( 6, 0 ));
    }
}
