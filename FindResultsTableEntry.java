package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.ParentTxn;

import java.util.Set;
import java.util.HashSet;

/**
 * <p>Single row in the find results table.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FindResultsTableEntry
{
    private final SplitTxn _split;
    private final ParentTxn _parent;
    private boolean _useInReplace;
    private boolean _applied;
    private final boolean _isSplitPrimary;
    private final Set<Integer> _modifiedColumns = new HashSet<Integer>();

    FindResultsTableEntry(final AbstractTxn txn)
    {
        this(txn, true);
    }

    FindResultsTableEntry(final AbstractTxn txn, final boolean useInReplace)
    {
        if (txn instanceof SplitTxn)
        {
            _isSplitPrimary = true;
            _split = (SplitTxn)txn;
            _parent = _split.getParentTxn();
        }
        else if (txn instanceof ParentTxn)
        {
            _isSplitPrimary = false;
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

    /** @return True if this entry came from a split transaction, false if it came from a parent. */
    boolean isSplitPrimary()
    {
        return _isSplitPrimary;
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
}
