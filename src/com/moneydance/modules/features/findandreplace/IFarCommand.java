package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.TxnTag;

/**
 * <p>Commands specific to Find and Replace.</p>
 *  
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.3
 * @since 1.0
 */
public interface IFarCommand extends ICommand
{
    void setTransactionEntry(final FindResultsTableEntry entry);
    
    Account getPreviewCategory();
    Long getPreviewAmount();
    String getPreviewDescription();
    String getPreviewMemo();
    TxnTag[] getPreviewTags();
}
