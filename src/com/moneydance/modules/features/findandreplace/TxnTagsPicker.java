package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.model.RootAccount;

import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;

/**
 * <p>Component that allows picking one or more transaction tags.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.3
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
    TxnTagsPicker(final MoneydanceGUI mdGui, final RootAccount data)
    {
        _view = new TagPickerField(mdGui, data);
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
        _controller.updateFromModel();
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

}
