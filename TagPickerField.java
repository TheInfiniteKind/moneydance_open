package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.txnreg.TxnTagsField;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.model.RootAccount;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.util.List;
import java.util.ArrayList;

/**
 * <p>Extension of the tag picker control to listen for change events.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class TagPickerField extends TxnTagsField
{
    private final List<ActionListener> _selectionListeners = new ArrayList<ActionListener>();

    public TagPickerField(MoneydanceGUI moneydanceGUI, RootAccount rootAccount)
    {
        super(moneydanceGUI, rootAccount);
    }


    @Override
    public synchronized void selectorButtonPressed()
    {
        super.selectorButtonPressed();

        for (final ActionListener listener : _selectionListeners)
        {
            listener.actionPerformed(new ActionEvent(this, 0, N12EFindAndReplace.SELECT_TAG));
        }
    }

    void addSelectionListener(final ActionListener listener)
    {
        _selectionListeners.add(listener);
    }

    void removeSelectionListener(final ActionListener listener)
    {
        _selectionListeners.remove(listener);
    }
}
