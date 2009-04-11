package com.moneydance.modules.features.findandreplace;

import java.awt.Image;

/**
 * <p>This is the main find-and-replace component class. It has a model, view and controller class.
 * This glues the Find and Replace dialog to the feature.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FindAndReplace
{
    private final Main _extension;
    private final FarModel _model;
    private final FarView _view;
    private final FarController _controller;

    public static IFindAndReplaceController getInstance(Main extension)
    {
        // I tried unsuccessfully to get a JUnit test working. We need a FeatureContext that can
        // be instantiated outside of Moneydance to make JUnits a possibility.
        return getTestInstance(extension).getController();
    }
    
    private static FindAndReplace getTestInstance(Main extension)
    {
        FarModel model = new FarModel();
        FarView view = new FarView(model);
        FarController controller = new FarController(model, view);

        // hook up listeners
        view.setController(controller);
        model.addPropertyChangeListener( view );
        
        return new FindAndReplace(extension, model, view, controller);
    }

    private FindAndReplace(final Main extension, final FarModel model, final FarView view, final FarController controller)
    {
        _extension = extension;
        _model = model;
        _view = view;
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


    void cleanUp()
    {
        _view.setController( null );
        _model.removePropertyChangeListener( _view );
        _extension.cleanupFarComponent();
    }
}
