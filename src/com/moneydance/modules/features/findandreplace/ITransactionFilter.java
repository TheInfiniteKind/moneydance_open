/**
 * @author Kevin Menningen
 * Created: Mar 24, 2008 5:49:39 AM
 */

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.TxnFilter;

/**
 * <p>Filter out transactions from the full list.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
public interface ITransactionFilter extends TxnFilter
{
    /**
     * @return True if this filter must be met in order for the transaction to match, or false
     * if other filters can be tested if this one fails.
     */
    public boolean isRequired();
}
