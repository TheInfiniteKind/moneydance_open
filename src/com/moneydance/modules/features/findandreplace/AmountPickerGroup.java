/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.awt.JCurrencyField;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.model.CurrencyTable;

import javax.swing.JComboBox;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.event.DocumentListener;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;


/**
 * <p>Two amount pickers, one 'from amount' and one 'to amount', combined, with currency selector.</p>
 *
 * @author Kevin Menningen
 * @version 1.60
 * @since 1.0
 */
class AmountPickerGroup extends JPanel
{
    private final JCurrencyField _from;
    private final JCurrencyField _to;
    private final JComboBox _currencyPicker;
    private final AmountCurrencyModel _currencyModel;
    private final FarController _controller;
    /**
     * Constructor with needed information to create the view
     * @param controller Controller for preference information and resources
     */
    AmountPickerGroup(final FarController controller)
    {
        _controller = controller;
        final CurrencyType currencyType = _controller.getCurrencyType();
        final CurrencyTable currencyTable = _controller.getCurrencyTable();
        final char decimalChar = controller.getDecimalChar();
        final char commaChar = controller.getCommaChar();
        _from = new JCurrencyField(currencyType, currencyTable, decimalChar, commaChar);
        _to =  new JCurrencyField(currencyType, currencyTable, decimalChar, commaChar);
        final String sharesDisplay = controller.getString(L10NFindAndReplace.CURRENCY_SHARES);
        _currencyModel = new AmountCurrencyModel(currencyTable, sharesDisplay);
        _currencyPicker = new JComboBox(_currencyModel);
        setupCurrencySelector(currencyType);
        layoutUI(controller);
        _from.addFocusListener(new FocusAdapter()
        {
            @Override
            public void focusLost(FocusEvent e)
            {
                long toValue = _to.getValue();
                if ((_from.getValue() != toValue) && (toValue == 0))
                {
                    // blow in the from value to make it easy
                    _to.setValue(_from.getValue());
                }
            }
        });
    }

    JCurrencyField getFromAmountPicker()
    {
        return _from;
    }

    JCurrencyField getToAmountPicker()
    {
        return _to;
    }

    void cleanUp()
    {
        _currencyModel.cleanUp();
    }

    void addChangeListener(final DocumentListener changeListener)
    {
        _from.getDocument().addDocumentListener(changeListener);
        _to.getDocument().addDocumentListener(changeListener);
    }

    public void addFocusListener(final FocusListener listener)
    {
        _from.addFocusListener(listener);
        _to.addFocusListener(listener);
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void setupCurrencySelector(CurrencyType currencyType) {
        if (currencyType != null)
        {
            _currencyPicker.setSelectedItem(currencyType);
        }
        else
        {
            _currencyPicker.setSelectedIndex(0);
        }
        _currencyPicker.addActionListener(new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                JComboBox cb = (JComboBox)e.getSource();
                CurrencyType currency = (CurrencyType)cb.getSelectedItem();
                handleCurrencyChange(currency);
            }
        });
    }

    private void handleCurrencyChange(final CurrencyType newCurrency)
    {
        _from.setCurrencyType(newCurrency);
        _to.setCurrencyType(newCurrency);
        _controller.setAmountCurrency(newCurrency, _currencyModel.isSharesCurrency(newCurrency));
    }

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
                UiUtil.HGAP,
                TableLayout.FILL       // currency
            },

            // rows
            { TableLayout.PREFERRED }
        };

        setLayout(new TableLayout(sizes));
        setOpaque(false);
        final JLabel labelFrom = new JLabel(resources.getString(L10NFindAndReplace.FIND_BETWEEN));
        add(labelFrom, new TableLayoutConstraints( 0, 0 ));
        add(_from,  new TableLayoutConstraints( 2, 0 ));
        final JLabel labelTo = new JLabel(resources.getString(L10NFindAndReplace.FIND_AND));
        add(labelTo, new TableLayoutConstraints( 4, 0 ));
        add(_to, new TableLayoutConstraints( 6, 0 ));
        add(_currencyPicker, new TableLayoutConstraints( 8, 0 ));
    }
}
