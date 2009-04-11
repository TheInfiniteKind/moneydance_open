/**
 * @author Kevin Menningen
 * Created: Mar 24, 2008 7:34:42 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.model.SplitTxn;

/**
 * <p>Filters out transactions that are filtered by an account filter. An
 * {@link AccountFilter account filter} is capable of checking if the account is contained in a
 * list of one or more accounts.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class AccountTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final AccountFilter _accountFilter;

    AccountTxnFilter(final AccountFilter accountFilter, final boolean required)
    {
        super(required);
        _accountFilter = accountFilter;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        if (txn != null)
        {
            // parent transactions can be tested immediately
            if (txn instanceof ParentTxn)
            {
                return _accountFilter.filter(txn.getAccount());
            }

            // split transactions need to check their parents to see if they are in the right
            // account or not
            if (txn instanceof SplitTxn)
            {
                final SplitTxn split = (SplitTxn)txn;
                final ParentTxn parent = split.getParentTxn();
                if (parent != null)
                {
                    return _accountFilter.filter(parent.getAccount());
                }
            }
        }
        return false;
    }

}
