/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.view.gui.budgetbars.controller.ITransactionFilter;

import java.util.regex.Pattern;

/**
 * <p>Filter to find text in the description, memo or check # fields.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class FreeTextTxnFilter extends TransactionFilterBase implements ITransactionFilter
{
    private final boolean _searchDescription;
    private final boolean _searchMemo;
    private final boolean _searchCheck;
    private final boolean _includeSplits;
    private final Pattern _pattern;

    FreeTextTxnFilter(final String textMatch, final boolean searchDescription,
                      final boolean searchMemo,  final boolean searchCheck,
                      final boolean includeSplits, final boolean required)
    {
        super(required);

        _searchDescription = searchDescription;
        _searchMemo = searchMemo;
        _searchCheck = searchCheck;
        _includeSplits = includeSplits;

        // build the regular expression pattern to search with
        if (FarUtil.hasRegularExpression(textMatch))
        {
            String regex = FarUtil.createRegularExpression(textMatch);
            _pattern = Pattern.compile(regex);
        }
        else
        {
            final StringBuffer buffer = new StringBuffer(N12EFindAndReplace.REGEX_PREFIX);
            buffer.append(textMatch);
            buffer.append(N12EFindAndReplace.REGEX_SUFFIX);
            _pattern = Pattern.compile(buffer.toString());
        }
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     *
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        boolean result = false;

        // text filtering is simply a pattern match on a string.
        if (txn != null)
        {
            result = searchTransaction(txn);
            if (!result && _includeSplits && (txn instanceof SplitTxn))
            {
                final ParentTxn parent = txn.getParentTxn();
                result = searchTransaction(parent);
            }
        } // if txn

        return result;
    }

    private boolean searchTransaction(AbstractTxn txn)
    {
        boolean result = false;
        if (_searchDescription)
        {
            final String description = txn.getDescription();
            if ((description != null) && !description.isEmpty())
            {
                result = _pattern.matcher(description).find();
            }
        }
        if (!result && _searchMemo)
        {
            // memo text is only in parent transactions, splits only have descriptions not memos
            final String memo = FarUtil.getTransactionMemo(txn);
            if ((memo != null) && !memo.isEmpty())
            {
                result = _pattern.matcher(memo).find();
            }
        }
        if (!result && _searchCheck)
        {
            final String checkNumber = FarUtil.getTransactionCheckNo(txn);
            if ((checkNumber != null) && !checkNumber.isEmpty())
            {
                result = _pattern.matcher(checkNumber).find();
            }
        }

        return result;
    }
}