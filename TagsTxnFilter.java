/**
 * @author Kevin Menningen
 * Created: Mar 24, 2008 7:34:42 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.TxnTagSet;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.TxnTag;

/**
 * <p>Filters transactions based upon what tags they have assigned to them. Only splits can
 * have tags, parent transactions do not.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class TagsTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final TxnTag[] _includedTags;
    private final TxnTag[] _excludedTags;

    TagsTxnFilter(final TxnTag[] included, final TxnTag[] excluded, final boolean required)
    {
        super(required);
        _includedTags = included;
        _excludedTags = excluded;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        // tags are on split transactions only
        if ((txn != null) && (txn instanceof SplitTxn))
        {
            final SplitTxn split = (SplitTxn)txn;
            boolean contained = false;
            if ((_includedTags != null) && (_includedTags.length > 0))
            {
                for (final TxnTag includedTag : _includedTags)
                {
                    if (TxnTagSet.txnContainsTag(split, includedTag))
                    {
                        contained = true;
                        break;
                    }
                }
            }

            if ((_excludedTags != null) && (_excludedTags.length > 0))
            {
                for (final TxnTag excludedTag : _excludedTags)
                {
                    if (TxnTagSet.txnContainsTag(split, excludedTag))
                    {
                        contained = false;
                        break;
                    }
                }
            }

            return contained;
        } // if txn
        
        return false;
    }

}