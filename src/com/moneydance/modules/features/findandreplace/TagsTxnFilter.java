/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.TxnTagSet;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.TxnTag;

/**
 * <p>Filters transactions based upon what tags they have assigned to them. Only splits can
 * have tags, parent transactions do not.</p>
 * 
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TagsTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final TxnTag[] _includedTags;
    private final TxnTag[] _excludedTags;
    private final TagLogic _combineLogic;

    TagsTxnFilter(final TxnTag[] included, final TxnTag[] excluded, final TagLogic combine,
                  final boolean required)
    {
        super(required);
        _includedTags = included;
        _excludedTags = excluded;
        _combineLogic = combine;
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        // tags can be on both parents and splits, but currently only split tags are supported
        if ((txn == null) || !(txn instanceof SplitTxn))
        {
            // no match
            return false;
        }

        boolean contained;
        final SplitTxn split = (SplitTxn)txn;
        if (TagLogic.EXACT.equals(_combineLogic))
        {
            contained = isExactMatch(split);
        }
        else if (TagLogic.AND.equals(_combineLogic))
        {
            contained = hasAllMatch(split);
        }
        else
        {
            contained = hasAnyMatch(split);
        }

        if (contained && (_excludedTags != null) && (_excludedTags.length > 0))
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
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private boolean isExactMatch(SplitTxn split)
    {
        boolean contained = true;
        // this will be a '|' delimited list of user-defined tag IDs for the transaction
        final String tagStr = split.getTag(TxnTagSet.TXN_TAG_KEY, null);
        if ((_includedTags != null) && (_includedTags.length > 0))
        {
            // All tags defined in the split must be in the included tags. We can't do an exact
            // comparison for two reasons: the split's tags will contain null or empty strings,
            // and the lists could be in a different order.
            if ((tagStr == null) || (tagStr.length() == 0))
            {
                // can't be an exact match, included tags are defined and the split doesn't have any
                return false;
            }
            
            String[] tagText = tagStr.split("\\|");
            String[] includedTagIDs = new String[_includedTags.length];
            int index = 0;
            for (final TxnTag includedTag : _includedTags)
            {
                includedTagIDs[index++] = includedTag.getID();
            }

            // check that all included tags are in the split
            for (String tagName : includedTagIDs)
            {
                contained = findStringInList(tagName, tagText);
                if (!contained) break;
            }

            if (contained)
            {
                // check that all split tags are contained in the included list
                for (String tagName : tagText)
                {
                    contained = findStringInList(tagName, includedTagIDs);
                    if (!contained) break;
                }
            }
        }
        else
        {
            // no tags defined, see if this transaction has no tags
            contained = ((tagStr == null) || (tagStr.length() == 0));
        }
        return contained;
    }

    private static boolean findStringInList(String searchStr, String[] stringList)
    {
        if ((searchStr == null) || (searchStr.length() == 0))
        {
            // null is always found - handles split's tags that might contain blanks
            return true;
        }
        boolean found = false;
        for (String includedName : stringList)
        {
            if (searchStr.equals(includedName))
            {
                found = true;
                break;
            }
        }
        return found;
    }

    private boolean hasAllMatch(final SplitTxn split)
    {
        boolean contained = true;

        if ((_includedTags != null) && (_includedTags.length > 0))
        {
            for (final TxnTag includedTag : _includedTags)
            {
                if (!TxnTagSet.txnContainsTag(split, includedTag))
                {
                    contained = false;
                    break;
                }
            }
        }
        else
        {
            // if the included tags are blank, that effectively disables the inclusion
            // criteria and all transactions should match
            contained = true;
        }

        return contained;
    }

    private boolean hasAnyMatch(final SplitTxn split)
    {
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
        else
        {
            // if the included tags are blank, that effectively disables the inclusion
            // criteria and all transactions should match
            contained = true;
        }

        return contained;
    }
}