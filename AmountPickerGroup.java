package com.moneydance.modules.features.findandreplace;

import com.moneydance.awt.JCurrencyField;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.CurrencyTable;

import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.event.DocumentListener;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

/**
 * <p>Two date pickers, one 'include tags' and one 'exclude tags', combined.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class AmountPickerGroup extends JPanel
{
    private final JCurrencyField _from;
    private final JCurrencyField _to;

    /**
     * Constructor with needed information to create the view
     * @param controller Controller for preference information and resources
     */
    AmountPickerGroup(final FarController controller)
    {
        final CurrencyType currencyType = controller.getCurrencyType();
        final CurrencyTable currencyTable = controller.getCurrencyTable();
        final char decimalChar = controller.getDecimalChar();
        final char commaChar = controller.getCommaChar();
        _from = new JCurrencyField(currencyType, currencyTable, decimalChar, commaChar);
        _to =  new JCurrencyField(currencyType, currencyTable, decimalChar, commaChar);
        layoutUI(controller);
    }

    JCurrencyField getFromAmountPicker()
    {
        return _from;
    }

    JCurrencyField getToAmountPicker()
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
