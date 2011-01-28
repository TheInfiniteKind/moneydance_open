/**
 * @author Kevin Menningen
 * Created: Mar 24, 2008 7:20:55 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;

import java.util.LinkedList;
import java.util.ListIterator;

/**
 * <p>Runs transactions through a list of filters. This is where the boolean AND and OR criteria
 * are applied. The individual transaction filters do the filtering itself.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class FilterGroup implements ITransactionFilter
{
    private final LinkedList<ITransactionFilter> _filterList;
    private boolean _hasRequiredFilters;

    FilterGroup()
    {
        _filterList = new LinkedList<ITransactionFilter>();
        _hasRequiredFilters = false;
    }

    void addFilter(final ITransactionFilter filter)
    {
        _filterList.add(filter);
        if (filter.isRequired())
        {
            _hasRequiredFilters = true;
        }
    }

    /**
     * Decide if a transaction matches this filter's criterion or not.
     * @param txn The transaction to test.
     * @return True if the transaction matches, false if it does not.
     */
    public boolean containsTxn(final AbstractTxn txn)
    {
        if ((_filterList == null) || _filterList.isEmpty())
        {
            // nothing to do
            return false;

        }

        if (_hasRequiredFilters)
        {
            // required filters dominate
            return checkRequiredFilters(txn);
        }

        return checkOptionalFilters(txn);
    }

    private boolean checkRequiredFilters(AbstractTxn txn)
    {
        boolean matches = true;

        ListIterator<ITransactionFilter> iter = _filterList.listIterator();
        while (iter.hasNext() && matches)
        {
            final ITransactionFilter filter = iter.next();
            if (!filter.isRequired())
            {
                // only check those filters that are required (AND'ed)
                continue;
            }

            matches = filter.containsTxn(txn);
            if (!matches)
            {
                // definitely not a match, the filter is AND'ed and didn't match which means this
                // txn is definitely excluded
                return matches;
            }

            // the transaction matched and is required, so we move on to the next filter in the list
        }

        return matches;
    } // checkRequiredFilters()


    private boolean checkOptionalFilters(AbstractTxn txn)
    {
        ListIterator<ITransactionFilter> iter = _filterList.listIterator();
        while (iter.hasNext())
        {
            final ITransactionFilter filter = iter.next();
            if (filter.isRequired())
            {
                // only check those filters that are not required (OR'ed)
                continue;
            }

            if (filter.containsTxn(txn))
            {
                // definitely a match, the filter is OR'ed and matched which means this
                // txn is definitely included
                return true;
            }

            // the transaction didn't match but is not required, so we move on to the next filter
        }

        return false;
    } // checkOptionalFilters()

    /**
     * @return True if this filter must be met in order for the transaction to match, or false
     * if other filters can be tested if this one fails.
     */
    public boolean isRequired()
    {
        // not used
        return false;
    }

}
