/**
 * @author Kevin Menningen
 * Created: Mar 24, 2008 7:34:42 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.controller.DateRange;

/**
 * <p>Filters transactions based upon whether they are within a specified date range.<p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.4
 * @since 1.0
 */
class DateRangeTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final DateRange _dateRange;
    private final boolean _useTaxDate;

    DateRangeTxnFilter(final int minimum, final int maximum, final boolean useTaxDate,
                       final boolean required)
    {
        super(required);
        int min = Math.min(minimum, maximum);
        int max = Math.max(minimum, maximum);
        _dateRange = new DateRange(min, max);
        _useTaxDate = useTaxDate;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        // just use what's built in
        if (txn != null)
        {
            if (_useTaxDate)
            {
                return _dateRange.containsInt(txn.getTaxDateInt());
            }
            return _dateRange.containsInt(txn.getDateInt());
        } // if txn
        return false;
    }

}