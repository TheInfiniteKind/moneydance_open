/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.*;
import java.util.*;

/**
 * <p>Filters transactions based upon what tags they have assigned to them. Only splits can
 * have tags, parent transactions do not.</p>
 * 
 * @author Kevin Menningen
 * @version Build 83
 * @since 1.0
 */
class TagsTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final List<String> _includedTags;
    private final List<String> _excludedTags;
    private final TagLogic _combineLogic;

    TagsTxnFilter(final List<String> included, final List<String> excluded, final TagLogic combine,
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

        if (contained && (_excludedTags != null) && (_excludedTags.size() > 0))
        {
            for (final String excludedTag : _excludedTags)
            {
                if (split.getKeywords().contains(excludedTag))
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
        final List<String> splitTags = split.getKeywords();
        if ((_includedTags != null) && (_includedTags.size() > 0))
        {
            // All tags defined in the split must be in the included tags, and the two lists must
            // be the same size
            if (splitTags.size() != _includedTags.size())
            {
                // can't be an exact match, included tags are defined and the split doesn't have any
                return false;
            }

            contained = _includedTags.containsAll(splitTags);
        }
        else
        {
            // no tags defined, see if this transaction has no tags
            contained = splitTags.size()==0;
        }
        return contained;
    }

    private boolean hasAllMatch(final SplitTxn split)
    {
        boolean contained = true;

        if ((_includedTags != null) && (_includedTags.size() > 0))
        {
            // the split can have a different number of tags, but must have all of the tags the
            // user has included
            List<String> splitTags = split.getKeywords();
            contained = splitTags.containsAll(_includedTags);
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

        if ((_includedTags != null) && (_includedTags.size() > 0))
        {
            // the split must have at least one of the tags the user has chosen in order to match
            List<String> splitTags = split.getKeywords();
            for (final String includedTag : _includedTags)
            {
                if (splitTags.contains(includedTag))
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