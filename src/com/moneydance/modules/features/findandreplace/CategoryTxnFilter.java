/**
 * @author Kevin Menningen
 * Created: Mar 24, 2008 7:34:42 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.SplitTxn;

/**
 * <p>Filters transactions based upon whether the associated category is filtered by a specified
 * {@link AccountFilter account filter}.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class CategoryTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final AccountFilter _categoryFilter;

    CategoryTxnFilter(final AccountFilter categoryFilter, final boolean required)
    {
        super(required);
        _categoryFilter = categoryFilter;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        // for category filtering, the assumption is that the transaction is from a normal
        // account to a category account, which occurs when a split transaction. Parent transactions
        // always have at least one split
        if ((txn != null) && (txn instanceof SplitTxn)) 
        {
            // if a split, check account for a match. If a parent, ignore because first split...
            final SplitTxn split = (SplitTxn)txn;
            if (_categoryFilter.filter(split.getAccount()))
            {
                return true;
            }
        } // if txn
        return false;
    }

}