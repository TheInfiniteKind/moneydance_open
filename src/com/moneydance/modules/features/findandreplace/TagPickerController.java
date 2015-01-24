/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.txnreg.TxnTagsField;

import javax.swing.ListModel;

/**
 * <p>Mediates between view and model for the tag picker control.</p>
 * 
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TagPickerController
{
    private final TagPickerModel _model;
    private final TxnTagsField _view;
    
    TagPickerController(final TagPickerModel model, final TxnTagsField view)
    {
        _model = model;
        _view = view;
    }

    void updateFromModel()
    {
        _view.setSelectedTags(_model.getSelectedTags());
    }

    void updateFromView()
    {
        _model.setSelectedTags(_view.getSelectedTags());
    }

    void selectAll()
    {
        _model.selectAll();
        updateFromModel();
    }

    void selectNone()
    {
        _model.clear();
        updateFromModel();
    }

    public void toggle(String candidate)
    {
        _model.toggle(candidate);
        updateFromModel();
    }

    public ListModel<String> getFullTagsList()
    {
        return _model.getFullTagsList();
    }

    public boolean isTagSelected(String tag)
    {
        return _model.isTagSelected(tag);
    }
}
