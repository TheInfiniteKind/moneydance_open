package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.TxnTag;
import com.moneydance.apps.md.model.TxnTagSet;

import java.awt.Point;

/**
 * <p>Utility methods for extracting information from transactions. Many of these could be useful
 * in other plugins.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.2
 * @since 1.0
 */
final class FarUtil
{
    static Account getTransactionAccount(final AbstractTxn txn)
    {
        final Account result;
        if (txn instanceof SplitTxn)
        {
            result = txn.getParentTxn().getAccount();
        }
        else
        {
            result = txn.getAccount();
        }
        return result;
    }

    static String getTransactionAccountName(final AbstractTxn txn)
    {
        return getTransactionAccount(txn).getAccountName();
    }

    static int getTransactionDate(final AbstractTxn txn)
    {
        final ParentTxn dateTxn;
        if (txn instanceof ParentTxn)
        {
            dateTxn = (ParentTxn)txn;
        }
        else if (txn instanceof SplitTxn)
        {
            dateTxn = txn.getParentTxn();
        }
        else
        {
            return -1;
        }

        return dateTxn.getDateInt(); // YYYYMMDD
    }

    static Account getTransactionCategory(final AbstractTxn txn)
    {
        if (txn instanceof SplitTxn)
        {
            return txn.getAccount();
        }
        else if (txn instanceof ParentTxn)
        {
            // for the parent, check if we have only 1 split. If we do, use that. If we have more,
            // show the words '- N splits -'
            final ParentTxn parent = (ParentTxn)txn;
            int numSplits = parent.getSplitCount();
            if (numSplits == 1)
            {
                return parent.getSplit(0).getAccount();
            }
        }

        // multiple splits or some other type of transaction
        return null;
    }

    static String getTransactionMemo(final AbstractTxn txn)
    {
        final String memo;
        if (txn instanceof ParentTxn)
        {
            memo = ((ParentTxn)txn).getMemo();
        }
        else if (txn instanceof SplitTxn)
        {
            memo = txn.getParentTxn().getMemo();
        }
        else
        {
            memo = null;
        }
        return memo;
    }

    static String getTransactionCheckNo(final AbstractTxn txn)
    {
        final String memo;
        if (txn instanceof ParentTxn)
        {
            memo = txn.getCheckNumber();
        }
        else if (txn instanceof SplitTxn)
        {
            memo = txn.getParentTxn().getCheckNumber();
        }
        else
        {
            memo = null;
        }
        return memo;
    }

    static TxnTag[] getTransactionTags(final AbstractTxn txn, final TxnTagSet tagSet)
    {
        // user tags are associated with splits only
        final SplitTxn split;
        if (txn instanceof SplitTxn)
        {
            split = (SplitTxn)txn;
        }
        else if ((txn instanceof ParentTxn) && (((ParentTxn)txn).getSplitCount() == 1))
        {
            // get the first split only
            split = ((ParentTxn)txn).getSplit(0);
        }
        else
        {
            // no tags associated with parent transactions with more than one split
            return new TxnTag[0];
        }

        if (tagSet == null)
        {
            // enforce the use of the API method
            return new TxnTag[0];
        }

        return tagSet.getTagsForTxn(split);
    }

    static boolean hasRegularExpression(final String freeTextSearch)
    {
        return ((freeTextSearch != null) && (freeTextSearch.length() > 1)
                && freeTextSearch.startsWith("=")
                && !freeTextSearch.startsWith("=="));
    }

    /**
     * Return the portion of the regular expression after the leading '='.
     * @param freeTextSearch Text entered by the user.
     * @return A regular expression string ready for Pattern and Matcher.
     */
    static String createRegularExpression(final String freeTextSearch)
    {
        if (!hasRegularExpression(freeTextSearch))
        {
            return N12EFindAndReplace.EMPTY;
        }
        return freeTextSearch.substring(1, freeTextSearch.length());
    }

    /**
     * Get a label from resources, and if it does not have a colon, add it.
     * @param resources Resource provider.
     * @param key String key to look up in the resources
     * @return A string with a colon at the end.
     */
    static String getLabelText(final IResourceProvider resources, final String key)
    {
        StringBuffer label = new StringBuffer(resources.getString(key));
        if ((label.length() > 0) &&
                (label.charAt(label.length() - 1)) != N12EFindAndReplace.COLON.charAt(0))
        {
            label.append(resources.getString(L10NFindAndReplace.LABEL_COLON));
        }
        return label.toString();
    }

    public static Point pointFromSettingsString(final String settings)
    {
        if (settings == null)
        {
            return null;
        }
        String[] values = settings.split(N12EFindAndReplace.SETTINGS_PT_DELIMITER);
        if (values.length == 2)
        {
            return new Point(Integer.parseInt(values[0]), Integer.parseInt(values[1]));
        }
        return null;
    }

    public static String settingsStringFromPoint(final Point point)
    {
        final StringBuffer result = new StringBuffer(Integer.toString(point.x));
        result.append(N12EFindAndReplace.SETTINGS_PT_DELIMITER);
        result.append(Integer.toString(point.y));
        return result.toString();
    }

    /**
     * Static utilities, do not instantiate.
     */
    private FarUtil()
    {

    }
}
