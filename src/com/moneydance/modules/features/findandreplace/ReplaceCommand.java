package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.TxnTag;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.model.TxnTagSet;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

/**
 * <p>Replace data according to the user's wishes.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public class ReplaceCommand implements IFarCommand
{
    // the input is immutable
    private final Account _replaceCategory;
    private final Long _replaceAmount; // stored as object so we can use null
    private final String _replaceDescription;
    private final String _replaceMemo;
    private final ReplaceTagCommandType _replaceTagType;
    private final TxnTag[] _replaceTagSet;
    private final TxnTagSet _userTagSet;

    // the transaction changes as the command is applied to all selected transactions in the list
    private AbstractTxn _transaction;

    ReplaceCommand(final Account category, final Long amount, final String description,
                   final String memo, final ReplaceTagCommandType tagCommand, final TxnTag[] tags,
                   final TxnTagSet userTagSet)
    {
        _replaceCategory = category;
        _replaceAmount = amount;
        _replaceDescription = description;
        _replaceMemo = memo;
        _replaceTagType = tagCommand;
        _replaceTagSet = tags;
        _userTagSet = userTagSet;

        _transaction = null;
    }

    public void setTransaction(final AbstractTxn txn)
    {
        _transaction = txn;
    }

    public Account getPreviewCategory()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        // the default is to make no changes. this check is to see if any category should be
        // returned at all for the transaction type -- if not, then return nothing
        final Account category = FarUtil.getTransactionCategory(_transaction);
        if (category != null)
        {
            return _replaceCategory;
        }

        // this is a parent transaction with more than one split -- no category
        return null;
    }

    public Long getPreviewAmount()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        return _replaceAmount;
    }

    public String getPreviewDescription()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        return _replaceDescription;
    }

    public String getPreviewMemo()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        return _replaceMemo;
    }

    public TxnTag[] getPreviewTags()
    {
        if ((_transaction == null) || (_replaceTagSet == null))
        {
            // not applied to a transaction, no preview, or no tags replaced
            return null;
        }

        final TxnTag[] baseTags = FarUtil.getTransactionTags(_transaction, _userTagSet);

        return getChangedTagSet(baseTags);
    }

    /**
     * Actually change the transaction.
     * @return True if a change was made, false otherwise.
     */
    public boolean execute()
    {
        if (_transaction == null)
        {
            // nothing to do
            return false;
        }

        // TODO: Maybe encapsulate logic in parent-split stuff like FindResultsTableEntry
        boolean changed = false;
        if (_replaceCategory != null)
        {
            // only apply category replacement to splits
            if (_transaction instanceof SplitTxn)
            {
                if (!_transaction.getAccount().equals(_replaceCategory))
                {
                    changed = true;
                }
                _transaction.setAccount(_replaceCategory);
            }
        }

        if (_replaceAmount != null)
        {
            // only apply amount changes to splits
            if (_transaction instanceof SplitTxn)
            {
                final SplitTxn split = (SplitTxn)_transaction;

                long value = _replaceAmount.longValue();
                long diff = value - split.getAmount();
                if (diff != 0)
                {
                    changed = true;
                    final double rate = split.getRate();
                    long parentAmount = split.getParentAmount();
                    split.setAmount(value, rate, parentAmount + diff);
                }
            }
        }

        if (_replaceDescription != null)
        {
            // apply description to either type
            if (_transaction.getDescription() == null)
            {
                changed = true;
            }
            else if (!_transaction.getDescription().equals(_replaceDescription))
            {
                changed = true;
            }
            _transaction.setDescription(_replaceDescription);

            // Now FindResultsTableModel.add() screens out duplicates where we have a single split
            // and a parent transaction, to make things simpler. It keeps the split in the list and
            // throws out the parent. Here we undo that situation and replace in the parent as well
            // as the split
            final ParentTxn parent = getParentTxn();
            if (parent != null)
            {
                if ((parent.getSplitCount() == 1) &&
                        ((parent.getDescription() == null) ||
                                !parent.getDescription().equals(_replaceDescription)))
                {
                    changed = true;
                    parent.setDescription(_replaceDescription);
                }
            }            
        }

        if (_replaceMemo != null)
        {
            // memo only applies to parent transactions
            final ParentTxn parent = getParentTxn();
            if (parent != null)
            {
                if (parent.getMemo() == null)
                {
                    changed = true;
                }
                else if (!parent.getMemo().equals(_replaceMemo))
                {
                    changed = true;
                }
                parent.setMemo(_replaceMemo);
            }
        }

        if (_replaceTagSet != null)
        {
            // tags are associated with splits only
            if (_transaction instanceof SplitTxn)
            {
                final SplitTxn split = (SplitTxn)_transaction;
                final TxnTag[] existingTags = FarUtil.getTransactionTags(split, _userTagSet);
                final TxnTag[] newTags = getChangedTagSet(existingTags);
                if (newTags != null)
                {
                    if (!Arrays.equals(existingTags, newTags))
                    {
                        changed = true;
                    }
                    TxnTagSet.setTagsForTxn(split, newTags);
                }
            }
        }

        if (changed)
        {
            FarUtil.getTransactionAccount(_transaction).setDirtyFlag();
        }

        return changed;
    } // execute()

    private ParentTxn getParentTxn()
    {
        final ParentTxn parent;
        if (_transaction instanceof ParentTxn)
        {
            parent = (ParentTxn)_transaction;
        }
        else if (_transaction instanceof SplitTxn)
        {
            parent = _transaction.getParentTxn();
        }
        else
        {
            parent = null;
        }
        return parent;
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private TxnTag[] getChangedTagSet(final TxnTag[] baseTags)
    {
        if (_replaceTagSet == null)
        {
            // invalid
            return null;
        }

        final List<TxnTag> newTags;
        if (ReplaceTagCommandType.ADD.equals(_replaceTagType))
        {
            if (baseTags != null)
            {
                newTags = new ArrayList<TxnTag>(Arrays.asList(baseTags));
            }
            else
            {
                newTags = new ArrayList<TxnTag>();
            }

            for (final TxnTag addTag : _replaceTagSet)
            {
                boolean found = false;
                for (final TxnTag existing : newTags)
                {
                    if (existing.equals(addTag))
                    {
                        found = true;
                        break;
                    }
                }
                if (!found)
                {
                    // safe to add
                    newTags.add(addTag);
                }
            } // for addTag

        }
        else if (ReplaceTagCommandType.REMOVE.equals(_replaceTagType))
        {
            if (baseTags != null)
            {
                newTags = new ArrayList<TxnTag>(Arrays.asList(baseTags));
            }
            else
            {
                newTags = new ArrayList<TxnTag>();
            }

            for (final TxnTag removeTag : _replaceTagSet)
            {
                TxnTag tagToDelete = null;
                for (final TxnTag existing : newTags)
                {
                    if (existing.equals(removeTag))
                    {
                        tagToDelete = existing;
                        break;
                    }
                }

                if (tagToDelete != null)
                {
                    newTags.remove(tagToDelete);
                }

            } // for removeTag
        }
        else if (ReplaceTagCommandType.REPLACE.equals(_replaceTagType))
        {
            newTags = new ArrayList<TxnTag>(Arrays.asList(_replaceTagSet));
        }
        else
        {
            // invalid
            return null;
        }

        return newTags.toArray(new TxnTag[newTags.size()]);
    }
}
