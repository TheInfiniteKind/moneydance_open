/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.CurrencyUtil;

/**
 * <p>Filters transactions on whether they are within a specified amount range.</p>
 *  
 * @author Kevin Menningen
 * @version 1.60
 * @since 1.0
 */
class AmountTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final long _minimum;
    private final long _maximum;
    private final CurrencyType _currency;
    private final boolean _isSharesCurrency;

    AmountTxnFilter(final long minimum, final long maximum, final CurrencyType currency,
                    final boolean isSharesCurrency, final boolean required)
    {
        super(required);
        _minimum = minimum;
        _maximum = maximum;
        _currency = currency;
        _isSharesCurrency = isSharesCurrency;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        if (txn == null)
        {
            return false;
        }
        final CurrencyType txnCurrency = txn.getAccount().getCurrencyType();
        // are we looking for a number of shares?
        if (_isSharesCurrency)
        {
            // check for whether this transaction is in shares of a security or not
            if (txnCurrency.getCurrencyType() == CurrencyType.Type.SECURITY)
            {
                // No conversion other than decimal places needed. The UI control has the max
                // decimal places of any security in the file. So if that currency has more decimal
                // places than the transaction currency's decimal places, we need to multiply so
                // we compare against the _minimum and _maximum correctly.
                long searchAmount = Math.abs(txn.getValue());
                int difference = _currency.getDecimalPlaces() - txnCurrency.getDecimalPlaces();
                // difference will never be negative because the UI currency has the maximum decimal
                // places of any security in the file.
                if (difference > 0)
                {
                    // _minimum and _maximum will be larger, so multiply the transaction amount
                    for (int ii = 0; ii < difference; ii++) searchAmount *= 10;
                }
                return ((searchAmount >= _minimum) && (searchAmount <= _maximum));
            }
            return false; // wrong kind of currency
        }
        // we're looking for a standard currency value
        if (txnCurrency.getCurrencyType() == CurrencyType.Type.SECURITY)
        {
            // wrong kind of currency
            return false;
        }
        // for amount filtering, we assume the user doesn't care if it is positive or negative,
        // and we look for matching amounts in both parents and splits
        final int txnDate = txn.getDateInt();
        final long searchAmount = Math.abs(CurrencyUtil.convertValue(txn.getValue(), txnCurrency,
                                                                     _currency, txnDate));
        return ((searchAmount >= _minimum) && (searchAmount <= _maximum));
    }

}