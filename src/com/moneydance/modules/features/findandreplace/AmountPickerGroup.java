/*************************************************************************\
* Copyright (C) 2009-2013 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.awt.JCurrencyField;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.CurrencyTable;

import javax.swing.JComboBox;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.event.DocumentListener;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;


/**
 * <p>Two amount pickers, one 'from amount' and one 'to amount', combined, with currency selector.
 * Also has a mode where only the 'to amount' is shown, plus a currency selector.</p>
 *
 * @author Kevin Menningen
 * @version Build 94
 * @since 1.0
 */
class AmountPickerGroup extends JPanel
{
    private final JCurrencyField _from;
    private final JCurrencyField _to;
    private final JComboBox _currencyPicker;
    private final AmountCurrencyModel _currencyModel;

    /**
     * Constructor with needed information to create the view
     * @param controller Controller for preference information and resources
     * @param showFromAndTo True if both the From and the To fields are displayed
     */
    AmountPickerGroup(final FarController controller, final boolean showFromAndTo, final boolean addSharesCurrency)
    {
        final CurrencyType currencyType = controller.getCurrencyType();
        final CurrencyTable currencyTable = controller.getCurrencyTable();
        final char decimalChar = controller.getDecimalChar();
        final char commaChar = controller.getCommaChar();
        _from = showFromAndTo ? new JCurrencyField(currencyType, currencyTable, decimalChar, commaChar) : null;
        _to =  new JCurrencyField(currencyType, currencyTable, decimalChar, commaChar);
        final String sharesDisplay = controller.getString(L10NFindAndReplace.CURRENCY_SHARES);
        _currencyModel = new AmountCurrencyModel(currencyTable, sharesDisplay, addSharesCurrency);
        _currencyPicker = new JComboBox(_currencyModel);
        setupCurrencySelector(currencyType);
        layoutUI(controller, showFromAndTo);
        if (showFromAndTo)
        {
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
        if (_from != null) _from.getDocument().addDocumentListener(changeListener);
        _to.getDocument().addDocumentListener(changeListener);
    }

    public void addFocusListener(final FocusListener listener)
    {
        if (_from != null) _from.addFocusListener(listener);
        _to.addFocusListener(listener);
    }

    CurrencyType getCurrencyType()
    {
        return (CurrencyType)_currencyModel.getSelectedItem();
    }

    void setCurrencyType(CurrencyType currencyType)
    {
        if (_to != null) _to.setCurrencyType(currencyType);
        if (_from != null) _from.setCurrencyType(currencyType);
        _currencyModel.setSelectedItem(currencyType);
    }

    boolean isSharesCurrency(final CurrencyType currency)
    {
        return _currencyModel.isSharesCurrency(currency);
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
        if (_from != null) _from.setCurrencyType(newCurrency);
        _to.setCurrencyType(newCurrency);
    }

    private void layoutUI(final IResourceProvider resources, final boolean showFromAndTo)
    {
        if (showFromAndTo)
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
        else
        {
            setLayout(new BorderLayout(UiUtil.HGAP, 0));
            setOpaque(false);
            add(_to, BorderLayout.CENTER);
            add(_currencyPicker, BorderLayout.EAST);
        }
    }
}
