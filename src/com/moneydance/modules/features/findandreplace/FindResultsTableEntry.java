/*************************************************************************\
* Copyright (C) 2009-2013 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.SplitTxn;
import com.infinitekind.moneydance.model.ParentTxn;

import java.util.Set;
import java.util.HashSet;

/**
 * <p>Single row in the find results table.</p>
 *
 * @author Kevin Menningen
 * @version Build 94
 * @since 1.0
 */
class FindResultsTableEntry
{
    private final SplitTxn _split;
    private final ParentTxn _parent;
    private final CurrencyType _currency;
    private boolean _useInReplace;
    private boolean _applied;
    private final Set<Integer> _modifiedColumns = new HashSet<Integer>();

    FindResultsTableEntry(final AbstractTxn txn, final CurrencyType baseCurrency)
    {
        this(txn, true, baseCurrency);
    }

    FindResultsTableEntry(final AbstractTxn txn, final boolean useInReplace, final CurrencyType baseCurrency)
    {
        if (txn instanceof SplitTxn)
        {
            _split = (SplitTxn)txn;
            _parent = _split.getParentTxn();
        }
        else if (txn instanceof ParentTxn)
        {
            _parent = (ParentTxn)txn;
            if (_parent.getSplitCount() > 0)
            {
                _split = _parent.getSplit(0);
            }
            else
            {
                // probably the blank transaction
                _split = null;
            }
        }
        else
        {
            throw new IllegalArgumentException(N12EFindAndReplace.UNKNOWN_TRANSACTION);
        }
        // we'll display the values with the parent account's currency, converted as needed
        // the account could be null for the blank transaction
        _currency = (_parent.getAccount() != null) ? _parent.getAccount().getCurrencyType() : baseCurrency;
        _applied = false;
        _useInReplace = useInReplace;
    }

    void applyCommand()
    {
        _applied = true;
    }

    void resetApply()
    {
        _applied = false;
    }

    boolean isApplied()
    {
        // there's a difference between selected for replacement and actually replaced
        return _applied;
    }
    
    boolean isUseInReplace()
    {
        // there's a difference between selected for replacement and actually replaced
        return _useInReplace;
    }

    void setUseInReplace(boolean useInReplace)
    {
        _useInReplace = useInReplace;
    }

    void addModifiedColumn(final int columnIndex)
    {
        _modifiedColumns.add(Integer.valueOf(columnIndex));
    }

    boolean isColumnModified(final int columnIndex)
    {
        return _modifiedColumns.contains(Integer.valueOf(columnIndex));
    }

    SplitTxn getSplitTxn()
    {
        return _split;
    }

    ParentTxn getParentTxn()
    {
        return _parent;
    }

    CurrencyType getCurrencyType()
    {
        return _currency;
    }
}
