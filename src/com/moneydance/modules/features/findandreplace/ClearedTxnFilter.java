/**
 * @author Kevin Menningen
 * Created: Mar 24, 2008 7:34:42 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.ParentTxn;

import java.util.regex.Pattern;

/**
 * <p>Filter to determine if a transaction's cleared status meets search criteria.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.1
 * @since 1.1
 */
class ClearedTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final boolean _allowCleared;
    private final boolean _allowReconciling;
    private final boolean _allowUncleared;

    ClearedTxnFilter(final boolean allowCleared,
                      final boolean allowReconciling,  final boolean allowUncleared,
                      final boolean required)
    {
        super(required);

        _allowCleared = allowCleared;
        _allowReconciling = allowReconciling;
        _allowUncleared = allowUncleared;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        final ParentTxn parent = txn.getParentTxn();
        byte clearedStatus = parent.getStatus();
        if (_allowCleared && (AbstractTxn.STATUS_CLEARED == clearedStatus))
        {
            return true;
        }
        if (_allowReconciling && (AbstractTxn.STATUS_RECONCILING == clearedStatus))
        {
            return true;
        }
        if (_allowUncleared && (AbstractTxn.STATUS_UNRECONCILED == clearedStatus))
        {
            return true;
        }
        return false;
    }


}