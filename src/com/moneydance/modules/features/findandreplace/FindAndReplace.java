/*************************************************************************\
* Copyright (C) 2009-2013 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import java.awt.Image;

/**
 * <p>This is the main find-and-replace component class. It has a model, view and controller class.
 * This glues the Find and Replace dialog to the feature.</p>
 *
 * @author Kevin Menningen
 * @version Build 94
 * @since 1.0
 */
class FindAndReplace
{
    private final Main _extension;
    private final FarController _controller;

    public static IFindAndReplaceController createInstance(Main extension)
    {
        FarModel model = new FarModel();
        FarController controller = new FarController(model);
        return new FindAndReplace(extension, controller).getController();
    }

    private FindAndReplace(final Main extension, final FarController controller)
    {
        _extension = extension;
        _controller = controller;
        _controller.setHost( this );
    }

    IFindAndReplaceController getController()
    {
        return _controller;
    }

    com.moneydance.apps.md.controller.Main getMDMain()
    {
        return (com.moneydance.apps.md.controller.Main) _extension.getUnprotectedContext();
    }

    com.moneydance.apps.md.view.gui.MoneydanceGUI getMDGUI()
    {
        if (getMDMain() == null)
        {
            return null;
        }
        return (com.moneydance.apps.md.view.gui.MoneydanceGUI) getMDMain().getUI();
    }

    String getString(final String resourceKey)
    {
        return _extension.getString( resourceKey );
    }

    /**
     * Obtain the given image from the resource bundle. The key specifies an image URL.
     * @param resourceKey The key to look up the resources with.
     * @return The associated image, or <code>null</code> if the key is not found or the image
     * could not be loaded.
     */
    public Image getImage(final String resourceKey)
    {
        return _extension.getImage( resourceKey );
    }

    public String getBuildString()
    {
        return _extension.getBuildString();
    }

    void cleanUp(IFindAndReplaceController controller)
    {
        _extension.cleanupFarComponent(controller);
    }
}
