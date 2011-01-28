/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;

/**
 * <p>Filters transactions on whether they are within a specified amount range.</p>
 *  
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class AmountTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final long _minimum;
    private final long _maximum;

    AmountTxnFilter(final long minimum, final long maximum, final boolean required)
    {
        super(required);
        _minimum = minimum;
        _maximum = maximum;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        // for amount filtering, we assume the user doesn't care if it is positive or negative,
        // and we look for matching amounts in both parents and splits
        if (txn != null)
        {
            // if a split, check account for a match. If a parent, ignore because first split...
            final long searchAmount = Math.abs(txn.getValue());
            if ((searchAmount >= _minimum) && (searchAmount <= _maximum))
            {
                return true;
            }
        } // if txn
        return false;
    }

}