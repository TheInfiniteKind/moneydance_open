/**
 * @author Kevin Menningen
 * Created: Apr 24, 2008 3:09:51 PM
 */

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.TxnTagSet;
import com.moneydance.apps.md.model.TxnTag;

import javax.swing.DefaultComboBoxModel;
import java.util.List;
import java.util.ArrayList;import java.util.Arrays;

/**
 * <p>Tracks user's selections from the list of tags.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class TagPickerModel extends DefaultComboBoxModel
{
    private final TxnTagSet _fullTagSet;
    private final List<TxnTag> _selected;

    TagPickerModel(final TxnTagSet tagSet)
    {
        _fullTagSet = tagSet;

        if (_fullTagSet != null)
        {
            _selected = new ArrayList<TxnTag>(_fullTagSet.getNumTags());
        }
        else
        {
            _selected = new ArrayList<TxnTag>();
        }
    }

    TxnTag[] getSelectedTags()
    {
        final int size = _selected.size();
        return _selected.toArray(new TxnTag[size]);
    }

    void setSelectedTags(final TxnTag[] tags)
    {
        _selected.clear();
        _selected.addAll(Arrays.asList(tags));
    }

    void selectAll()
    {
        if (_fullTagSet != null)
        {
            clear();
            _selected.addAll(Arrays.asList(_fullTagSet.getSortedTags()));
        }
    }

    void clear()
    {
        _selected.clear();
    }

    
}
