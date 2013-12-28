/*************************************************************************\
 * Copyright (C) 2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 \*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.CurrencyType;

/**
 * Group together a value and the currency type assigned to that value, for clarity. The date is
 * also included so that when any conversion happens between this value's currency and another
 * currency, the appropriate date can be used for the conversion.
 *
 * @author Kevin Menningen
 * @version Build 94
 * @since Build 94
 */
public final class TxnValue
{
    public final long value;
    public final CurrencyType currency;
    public final int date;

    public TxnValue(final long txnValue, final CurrencyType txnCurrency, final int txnDateInt)
    {
        value = txnValue;
        currency = txnCurrency;
        date = txnDateInt;
    }
}
