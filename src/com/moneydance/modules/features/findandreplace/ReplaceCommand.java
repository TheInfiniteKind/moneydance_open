/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.*;

import java.util.List;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * <p>Replace data according to the user's wishes.</p>
 *
 * @author Kevin Menningen
 * @version Build 94
 * @since 1.0
 */
public class ReplaceCommand implements IFarCommand
{
    // the input is immutable
    private final Account _replaceCategory;
    private final Long _replaceAmount; // stored as object so we can use null
    private final CurrencyType _replaceCurrency;
    private final boolean _parentsOnly;
    private final String _replaceDescription;
    private final boolean _replaceFoundDescriptionOnly;
    private final String _replaceMemo;
    private final boolean _replaceFoundMemoOnly;
    private final String _replaceCheckNum;
    private final boolean _replaceFoundCheckOnly;
    private final Pattern _findPattern;
    private final ReplaceTagCommandType _replaceTagType;
    private final List<String> _replaceTagSet;
    private final List<String> _userTagSet;

    // the transaction changes as the command is applied to all selected transactions in the list
    private FindResultsTableEntry _transaction;

    ReplaceCommand(final Account category, final Long amount, final CurrencyType amountCurrency,
                   final boolean parentsOnly,
                   final String description, final boolean replaceFoundDescriptionOnly,
                   final String memo, final boolean replaceFoundMemoOnly,
                   final String check, final boolean replaceFoundCheckOnly,
                   final Pattern findPattern,
                   final ReplaceTagCommandType tagCommand, final List<String> tags,
                   final List<String> userTagSet)
    {
        _replaceCategory = category;
        _replaceAmount = amount;
        _replaceCurrency = amountCurrency;
        _parentsOnly = parentsOnly;
        _replaceDescription = description;
        _replaceFoundDescriptionOnly = replaceFoundDescriptionOnly;
        _replaceMemo = memo;
        _replaceFoundMemoOnly = replaceFoundMemoOnly;
        _replaceCheckNum = check;
        _replaceFoundCheckOnly = replaceFoundCheckOnly;
        _findPattern = findPattern;
        _replaceTagType = tagCommand;
        _replaceTagSet = tags;
        _userTagSet = userTagSet;

        _transaction = null;
    }

    public void setTransactionEntry(final FindResultsTableEntry entry)
    {
        _transaction = entry;
    }

    public Account getPreviewCategory()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        if (_parentsOnly && (_transaction.getParentTxn().getSplitCount() > 1))
        {
            // this is a parent transaction with more than one split -- no category
            return null;
        }

        // the default is to make no changes. this check is to see if any category should be
        // returned at all for the transaction type -- if not, then return nothing
        final Account category = FarUtil.getTransactionCategory(_transaction.getSplitTxn());
        if (category != null)
        {
            if (_transaction.getSplitTxn().getAccount().equals(_replaceCategory) ||
                _transaction.getParentTxn().getAccount().equals(_replaceCategory))
            {
                // The transaction cannot be replaced because either the category is already set
                // to that account, or it's the same as the other side and you shouldn't have the
                // account on both sides
                return null;
            }
            return _replaceCategory;
        }

        // something else is not right, skip the category
        return null;
    }

    public Long getPreviewAmount()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        if (_parentsOnly && (_transaction.getParentTxn().getSplitCount() > 1))
        {
            // this is a parent transaction with more than one split -- can't change amount
            return null;
        }

        return _replaceAmount;
    }

    public CurrencyType getAmountCurrency()
    {
        if (_replaceCurrency == null)
        {
            return (_transaction == null) ? null : _transaction.getCurrencyType();
        }
        return _replaceCurrency;
    }

    public String getPreviewDescription(final boolean useParent)
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        final String originalText;
        if (useParent || _parentsOnly)
        {
            originalText = _transaction.getParentTxn().getDescription();
        }
        else
        {
            originalText = _transaction.getSplitTxn().getDescription();
        }
        final String replacedText = applyTextReplace(originalText, _replaceDescription,
                                                     _replaceFoundDescriptionOnly);
        if ((originalText != null) && originalText.equals(replacedText))
        {
            // no change in the text, therefore no preview
            return null;
        }
        return replacedText;
    }

    public String getPreviewMemo()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        return applyTextReplace(_transaction.getParentTxn().getMemo(), _replaceMemo, _replaceFoundMemoOnly);
    }

    public String getPreviewCheckNumber()
    {
        if (_transaction == null)
        {
            // not applied to a transaction, no preview
            return null;
        }

        return applyTextReplace(_transaction.getParentTxn().getCheckNumber(), _replaceCheckNum, _replaceFoundCheckOnly);
    }

    public List<String> getPreviewTags()
    {
        if ((_transaction == null) || (_replaceTagSet == null))
        {
            // not applied to a transaction, no preview, or no tags replaced
            return null;
        }

        // There can be tags on both sides: split and parent. However the parent side is hard to
        // get to (Show Other Side, then edit tags) and has some UI issues for the user. Currently
        // we only support tags on the split.
        final List<String> baseTags = FarUtil.getTransactionTags(_transaction.getSplitTxn(), _userTagSet);

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

        boolean changed = false;
        Account previousCategory = null;

        // the amount or category should not be changed if Consolidate Splits is turned on and the parent transaction
        // has more than one split
        final boolean skipAmount = _parentsOnly && (_transaction.getParentTxn().getSplitCount() > 1);
        if (!skipAmount && (_replaceCategory != null))
        {
            // Only apply category replacement to splits. Do not replace if the category is already
            // the same, or if the transaction's other side is the same category (you can't have
            // the same account on both sides of a split)
            if (!_transaction.getSplitTxn().getAccount().equals(_replaceCategory) &&
                !_transaction.getParentTxn().getAccount().equals(_replaceCategory))
            {
                changed = true;
                previousCategory = _transaction.getSplitTxn().getAccount();
                _transaction.getSplitTxn().setAccount(_replaceCategory);
            }
        }

        final boolean newCategory = (previousCategory != null) && (_replaceCategory != null);
        if (!skipAmount && (_replaceAmount != null))
        {
            // only apply amount changes to splits because it is too complicated to change the
            // amount for a parent transaction with multiple splits
            // If we replace both the category AND the amount, we have to assume the user put the amount
            // in the target currency, and no conversion takes place
            final SplitTxn split = _transaction.getSplitTxn();
            //  check if the target category has changed to == new rate
            long value = _replaceAmount.longValue();
            // replacing with a negative value flips the sign
            long signFlip = (value < 0) ? -1 : 1;
            long prevSign = (split.getAmount() < 0) ? -1 : 1;
            long prevParentSign = (split.getParentAmount() < 0) ? -1 : 1;
            CurrencyType targetCurr = split.getAccount().getCurrencyType();
            CurrencyType parentCurr = _transaction.getParentTxn().getAccount().getCurrencyType();
            changed = true;
            if (newCategory) {
                targetCurr = _replaceCategory.getCurrencyType();
            }
            // convert the replacement amount into the category's currency, then set the proper sign
            long splitAmount = Math.abs(CurrencyUtil.convertValue(value, _replaceCurrency, targetCurr, split.getDateInt())) * prevSign * signFlip;
            long parentAmount = Math.abs(CurrencyUtil.convertValue(value, _replaceCurrency, parentCurr, split.getDateInt())) * prevParentSign * signFlip;
            double rate = CurrencyUtil.getRawRate(parentCurr, targetCurr, split.getDateInt());
            split.setAmount(splitAmount, rate, parentAmount);
        }
        else if (newCategory)
        {
            // we have not changed the amount, but the category has been changed, so do a currency conversion
            CurrencyType sourceCurr = previousCategory.getCurrencyType();
            CurrencyType targetCurr = _replaceCategory.getCurrencyType();
            if (!sourceCurr.equals(targetCurr))
            {
                final SplitTxn split = _transaction.getSplitTxn();
                CurrencyType parentCurr = _transaction.getParentTxn().getAccount().getCurrencyType();
                // parent amount should stay the same (or flip sign), split amount will change
                // the sign is flipped in the getParentAmount() method, so flip it again - must stay the same
                // unless we're switching from an expense category to an income one
                long parentAmount = -split.getParentAmount();
                // the rate is always a positive number, raw rate refers to actual number used to convert two longs to each other
                // whereas user rate is a display and/or editable value
                double rate = CurrencyUtil.getRawRate(parentCurr, targetCurr, split.getDateInt());
                // the parent amount has the same sign under the hood, the sign is negated in the UI only
                long splitAmount = Math.round(parentAmount * rate);
                split.setAmount(splitAmount, rate, parentAmount);
            }
        }

        if (_replaceDescription != null)
        {
            // independently replace the split and the parent description, ss long as consolidate splits is off
            if (!_parentsOnly)
            {
                final String splitDescription = _transaction.getSplitTxn().getDescription();
                if (splitDescription != null)
                {
                    String newDescription = applyTextReplace(splitDescription, _replaceDescription,
                            _replaceFoundDescriptionOnly);
                    if (!splitDescription.equals(newDescription))
                    {
                        changed = true;
                        _transaction.getSplitTxn().setDescription(newDescription);
                    }
                }
                else if (!_replaceFoundDescriptionOnly)
                {
                    // blow in the new description since it is blank
                    changed = true;
                    _transaction.getSplitTxn().setDescription(_replaceDescription);
                }
            }

            // now check the parent
            final ParentTxn parent = _transaction.getParentTxn();
            if ((parent != null) && (_parentsOnly || (parent.getSplitCount() == 1)))
            {
                final String parentDescription = _transaction.getParentTxn().getDescription();
                if (parentDescription != null)
                {
                    String newDescription = applyTextReplace(parentDescription,
                                                             _replaceDescription,
                                                             _replaceFoundDescriptionOnly);
                    if (!parentDescription.equals(newDescription))
                    {
                        changed = true;
                        _transaction.getParentTxn().setDescription(newDescription);
                    }
                }
                else if (!_replaceFoundDescriptionOnly)
                {
                    // blow in the new description since it is blank
                    changed = true;
                    _transaction.getParentTxn().setDescription(_replaceDescription);
                }
            }
        }

        if (_replaceMemo != null)
        {
            // memo only applies to parent transactions
            final ParentTxn parent = _transaction.getParentTxn();
            if (parent != null)
            {
                final String replacementText = applyTextReplace(parent.getMemo(), _replaceMemo,
                                                                _replaceFoundMemoOnly);
                if (parent.getMemo() == null)
                {
                    changed = true;
                }
                else if (!parent.getMemo().equals(replacementText))
                {
                    changed = true;
                }
                parent.setMemo(replacementText);
            }
        }

        if (_replaceCheckNum != null)
        {
            // check number only applies to parent transactions
            final ParentTxn parent = _transaction.getParentTxn();
            if (parent != null)
            {
                final String replacementText = applyTextReplace(parent.getCheckNumber(),
                                                                _replaceCheckNum,
                                                                _replaceFoundCheckOnly);
                if (parent.getCheckNumber() == null)
                {
                    changed = true;
                }
                else if (!parent.getCheckNumber().equals(replacementText))
                {
                    changed = true;
                }
                parent.setCheckNumber(replacementText);
            }
        }

        if (_replaceTagSet != null)
        {
            // There can be tags on both sides: split and parent. However the parent side is hard to
            // get to (Show Other Side, then edit tags) and has some UI issues for the user. Currently
            // we only support tags on the split.
            final SplitTxn split = _transaction.getSplitTxn();
            final List<String> existingTags = FarUtil.getTransactionTags(split, _userTagSet);
            final List<String> newTags = getChangedTagSet(existingTags);
            if (newTags != null)
            {
                if (!existingTags.equals(newTags))
                {
                    changed = true;
                }
                split.setKeywords(newTags);
            }
        }

        return changed;
    } // execute()


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Package Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    AbstractTxn getParentTransaction() {
        return _transaction.getParentTxn();
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private String applyTextReplace(final String originalText, final String replacementText,
                                    final boolean replaceFoundOnly)
    {
        if (replaceFoundOnly)
        {
            Matcher result = _findPattern.matcher(originalText);
            if (result.find())
            {
                return result.replaceAll(replacementText);
            }
            return originalText;
        }
        // replace the entire text
        return replacementText;
    }

    private List<String> getChangedTagSet(final List<String> baseTags)
    {
        if (_replaceTagSet == null)
        {
            // invalid
            return null;
        }

        final List<String> newTags;
        if (ReplaceTagCommandType.ADD.equals(_replaceTagType))
        {
            if (baseTags != null)
            {
                newTags = new ArrayList<String>(baseTags);
            }
            else
            {
                newTags = new ArrayList<String>();
            }

            for (final String addTag : _replaceTagSet)
            {
                boolean found = false;
                for (final String existing : newTags) {
                    if (existing.equals(addTag)) {
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
                newTags = new ArrayList<String>(baseTags);
            }
            else
            {
                newTags = new ArrayList<String>();
            }

            for (final String removeTag : _replaceTagSet)
            {
                String tagToDelete = null;
                for (final String existing : newTags)
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
            newTags = new ArrayList<String>(_replaceTagSet);
        }
        else
        {
            // invalid
            return null;
        }

        return newTags;
    }
}
