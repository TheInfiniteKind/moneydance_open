/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.txnreg.TxnTagsField;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.infinitekind.moneydance.model.*;

import javax.swing.JButton;
import javax.swing.JComponent;
import java.awt.Component;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.FocusListener;
import java.util.List;
import java.util.ArrayList;


/**
 * <p>Extension of the tag picker control to listen for change events.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TagPickerField extends TxnTagsField
{
    private final List<ActionListener> _selectionListeners = new ArrayList<ActionListener>();
    private ColoredParentFocusAdapter _parentFocusListener = null;
    private TagPickerController _controller;

    public TagPickerField(MoneydanceGUI moneydanceGUI, AccountBook book)
    {
        super(moneydanceGUI, book);
        for (Component child : getComponents())
        {
            if (child instanceof JComponent)
            {
                ((JComponent)child).setOpaque(false);
            }

            // show a popup window when clicking the button
            if (child instanceof JButton)
            {
                JButton selectorButton = (JButton)child;
                selectorButton.addActionListener(new ActionListener()
                {
                    public void actionPerformed(ActionEvent e)
                    {
                        fireTagSelectEvent(N12EFindAndReplace.SELECT_TAG_LIST);
                    }
                });
            }
        }
    }

    @Override
    public void addFocusListener(FocusListener listener)
    {
        super.addFocusListener(listener);
        if ((listener instanceof ColoredParentFocusAdapter) && (_parentFocusListener == null))
        {
            _parentFocusListener = (ColoredParentFocusAdapter)listener;
        }
    }

    @Override
    public synchronized void selectorButtonPressed()
    {
        // focus has not been lost, it is just shifting to the popup
        if (_parentFocusListener != null)
        {
            _parentFocusListener.disableColorChange();
        }

        super.selectorButtonPressed();
        fireTagSelectEvent(N12EFindAndReplace.SELECT_TAG);
    }

    private void fireTagSelectEvent(final String eventName)
    {
        _controller.updateFromView();
        for (final ActionListener listener : _selectionListeners)
        {
            listener.actionPerformed(new ActionEvent(this, 0, eventName));
        }
    }

    void setController(TagPickerController controller) { _controller = controller; }

    void addSelectionListener(final ActionListener listener)
    {
        _selectionListeners.add(listener);
    }

    void removeSelectionListener(final ActionListener listener)
    {
        _selectionListeners.remove(listener);
    }
}
