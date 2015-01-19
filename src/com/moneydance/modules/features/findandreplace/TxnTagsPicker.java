/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.infinitekind.moneydance.model.*;

import javax.swing.ListModel;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;

/**
 * <p>Component that allows picking one or more transaction tags.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TxnTagsPicker
{
    private final TagPickerField _view;
    private TagPickerController _controller;

    /**
     * Constructor with needed information to create the view
     * @param mdGui GUI controller for Moneydance
     * @param data Datafile
     */
    TxnTagsPicker(final MoneydanceGUI mdGui, final AccountBook data)
    {
        _view = new TagPickerField(mdGui, data);
        _view.setOpaque(false);
        _view.addFocusListener(new FocusAdapter()
        {
            /**
             * Invoked when a component loses the keyboard focus.
             */
            @Override
            public void focusLost(FocusEvent e)
            {
                _controller.updateFromView();
            }
        });
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Package Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    void setModel(TagPickerModel model)
    {
        _controller = new TagPickerController(model, _view);
        _view.setController(_controller);
        _controller.updateFromModel();
    }

    void toggle(String candidate) {
        _controller.toggle(candidate);
        _view.repaint();
    }

    TagPickerField getView()
    {
        return _view;
    }

    void updateFromView()
    {
        _controller.updateFromView();
    }

    void selectAll()
    {
        _controller.selectAll();
        _view.repaint();
    }

    void selectNone()
    {
        _controller.selectNone();
        _view.repaint();
    }

    public ListModel<String> getFullTagsList()
    {
        return _controller.getFullTagsList();
    }

    public boolean isTagSelected(String tag)
    {
        return _controller.isTagSelected(tag);
    }
}
