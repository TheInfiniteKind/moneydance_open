/*************************************************************************\
* Copyright (C) 2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.CurrencyListener;
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;

import javax.swing.AbstractListModel;
import javax.swing.ComboBoxModel;
import java.util.Vector;


/**
 * Model used to represent a set of currency values that are of normal currencies, with an
 * additional generic option of "shares" for any security.
 *
 * @author Kevin Menningen
 * @version 1.60
 * @since 1.60
 */
public class AmountCurrencyModel
        extends AbstractListModel
        implements ComboBoxModel,
        CurrencyListener
{
    private final Vector<CurrencyType> _currencies = new Vector<CurrencyType>();
    private CurrencyTable _currencyTable;
    private CurrencyType _selectedType = null;
    private final CurrencyType _specialSharesType;

    public AmountCurrencyModel(CurrencyTable currencyTable, final String sharesName)
    {
        _currencyTable = currencyTable;
        // create a special type that generically represents any security "currency"
        _specialSharesType = new CurrencyType(currencyTable.getNextID(), sharesName, sharesName, 1.0,
                                              getMaxDecimalsShares(currencyTable),
                                              "", "", "", 0, CurrencyType.CURRTYPE_CURRENCY,
                                              currencyTable);
        build();
        if (!_currencies.isEmpty())
        {
            _selectedType = currencyTable.getBaseType();
            if (_selectedType == null || !_currencies.contains(_selectedType))
                _selectedType = _currencies.elementAt(0);
        }
        currencyTable.addCurrencyListener(this);
    }

    void cleanUp()
    {
        _currencyTable.removeCurrencyListener(this);
    }

    boolean isSharesCurrency(final CurrencyType candidate)
    {
        return _specialSharesType.equals(candidate);
    }

    boolean isVisible(CurrencyType c)
    {
        if (c == null) return false;
        return c.getCurrencyType() == CurrencyType.CURRTYPE_CURRENCY;
    }

    public void currencyTableModified(CurrencyTable table)
    {
        build();
    }

    public int getSize()
    {
        return _currencies.size();
    }

    public Object getElementAt(int i)
    {
        return _currencies.elementAt(i);
    }

    public void setSelectedItem(Object item)
    {
        _selectedType = (CurrencyType) item;
        fireContentsChanged(this, -1, -1);
    }

    public Object getSelectedItem()
    {
        return _selectedType;
    }

    private static int getMaxDecimalsShares(final CurrencyTable currencyTable)
    {
        int result = 0;
        for (CurrencyType curr : currencyTable.getAllCurrencies())
        {
            if (curr.getCurrencyType() == CurrencyType.CURRTYPE_SECURITY)
                result = Math.max(result, curr.getDecimalPlaces());
        }
        return result;
    }

    private synchronized void build()
    {
        CurrencyType list[] = _currencyTable.getAllCurrencies();
        _currencies.clear();
        for (CurrencyType curr : list)
        {
            if (isVisible(curr))
                _currencies.addElement(curr);
        }
        _currencies.add(_specialSharesType);
        fireContentsChanged(this, -1, -1);
    }

}
