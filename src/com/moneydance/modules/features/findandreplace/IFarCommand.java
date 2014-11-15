/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.TxnTag;


/**
 * <p>Commands specific to Find and Replace.</p>
 *  
 * @author Kevin Menningen
 * @version 1.60
 * @since 1.0
 */
public interface IFarCommand extends ICommand
{
    void setTransactionEntry(final FindResultsTableEntry entry);
    
    Account getPreviewCategory();
    Long getPreviewAmount();
    String getPreviewDescription(boolean useParent);
    String getPreviewMemo();
    String getPreviewCheckNumber();
    TxnTag[] getPreviewTags();
}
