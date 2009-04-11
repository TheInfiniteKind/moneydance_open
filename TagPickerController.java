package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.txnreg.TxnTagsField;
import com.moneydance.apps.md.model.TxnTag;

/**
 * <p>Mediates between view and model for the tag picker control.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
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
        for (TxnTag tag : _model.getSelectedTags())
        {
            _view.setTagSelected(tag);
        }
    }

    void updateFromView()
    {
        _model.setSelectedTags(_view.getSelectedTags());
    }
}
