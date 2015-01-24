/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import javax.swing.DefaultComboBoxModel;
import javax.swing.DefaultListModel;
import javax.swing.ListModel;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;

/**
 * <p>Tracks user's selections from the list of tags.</p>
 * 
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class TagPickerModel extends DefaultComboBoxModel
{
    private final List<String> _fullTagSet;
    private final List<String> _selected;

    TagPickerModel(final List<String> tagSet)
    {
        _fullTagSet = tagSet;

        if (_fullTagSet != null)
        {
            Collections.sort(_fullTagSet);
            _selected = new ArrayList<String>(_fullTagSet.size());
        }
        else
        {
            _selected = new ArrayList<String>();
        }
    }

    List<String> getSelectedTags()
    {
      return new ArrayList<String>(_selected);
    }

    void setSelectedTags(final List<String> tags)
    {
      _selected.clear();
      _selected.addAll(tags);
    }

    void selectAll()
    {
        if (_fullTagSet != null)
        {
            clear();
            _selected.addAll(_fullTagSet);
        }
    }

    void clear()
    {
        _selected.clear();
    }

    void toggle(String candidate)
    {
        if (_selected.contains(candidate))
        {
            _selected.remove(candidate);
        }
        else
        {
            _selected.add(candidate);
        }
    }

    public ListModel<String> getFullTagsList()
    {
        DefaultListModel<String> result = new DefaultListModel<String>();
        for (String knownTag : _fullTagSet)
        {
            result.addElement(knownTag);
        }
        return result;
    }

    public boolean isTagSelected(String tag)
    {
        return _selected.contains(tag);
    }
}
