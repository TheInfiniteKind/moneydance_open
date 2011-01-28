/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

/**
 * <p>Base class for all filters.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
abstract class TransactionFilterBase implements ITransactionFilter
{
    private final boolean _required;

    TransactionFilterBase(final boolean required)
    {
        _required = required;
    }

    /**
     * @return True if this filter must be met in order for the transaction to match, or false
     *         if other filters can be tested if this one fails.
     */
    public boolean isRequired()
    {
        return _required;
    }
}
