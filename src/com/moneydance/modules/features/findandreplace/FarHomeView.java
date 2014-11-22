/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.HomePageView;
import com.infinitekind.moneydance.model.*;

import javax.swing.JComponent;

/**
 * <p>Home page support for Find and Replace. The home page is a simple free text entry that assumes
 * all accounts and categories.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class FarHomeView implements HomePageView
{
    private FarHomePage _view = null;
    private final Main _feature;

    public FarHomeView(final Main feature)
    {
        _feature = feature;
    }

    public String getID()
    {
        return N12EFindAndReplace.HOME_PAGE_ID;
    }

    public JComponent getGUIView(AccountBook book)
    {
        if (_view == null)
        {
            _view = new FarHomePage(_feature);
            _view.layoutUI();
        }
        return _view;
    }

    public void setActive(boolean active)
    {
        if (_view != null)
        {
            _view.setVisible(active);
        }
    }

    public void refresh()
    {
        if (_view != null)
        {
            _view.refresh();
        }
    }

    public void reset()
    {
        // no listeners to clean up
        _view = null;
    }

    public String toString()
    {
        return _feature.getString(L10NFindAndReplace.TITLE);
    }
}
