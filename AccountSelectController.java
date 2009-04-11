/*
 * AccountSelectController.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Feb 17, 2008
 * Time: 6:29:02 AM
 */


package com.moneydance.modules.features.findandreplace;

import java.awt.Image;

/**
 * <p>Controller for the dialog that shows account or category selection.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public class AccountSelectController implements IResourceProvider
{
    private final AccountSelectModel _model;
    private final IResourceProvider _resources;

    /**
     * Constructor. This object acts as a resource provider in order to preserve design
     * consistency with the main feature controller.
     * @param model The data model for selecting accounts.
     * @param resources The resource provider from FindAndReplace component, which is encapsulated
     * by this object.
     */
    AccountSelectController(final AccountSelectModel model, final IResourceProvider resources)
    {
        _model = model;
        _resources = resources;
    }

    void apply()
    {
        _model.apply();
    }

    void moveToIncluded(final int[] indices) throws Exception
    {
        _model.moveToIncluded(indices);
    }

    void moveToExcluded(final int[] indices) throws Exception
    {
        _model.moveToExcluded(indices);
    }

    void includeExcept(final int[] indices) throws Exception
    {
        _model.includeExcept(indices);
    }

    void excludeExcept(final int[] indices) throws Exception
    {
        _model.excludeExcept(indices);
    }

    void includeAll() throws Exception
    {
        _model.includeAll();
    }

    void excludeAll() throws Exception
    {
        _model.excludeAll();
    }

    /**
     * Obtain the given string from the resource bundle.
     *
     * @param resourceKey The key to look up the resources.
     * @return The associated string, or <code>null</code> if the key is not found.
     */
    public String getString(final String resourceKey)
    {
        return _resources.getString(resourceKey);
    }
    /**
     * Obtain the given image from the resource bundle. The key specifies an image URL.
     * @param resourceKey The key to look up the resources with.
     * @return The associated image, or <code>null</code> if the key is not found or the image
     * could not be loaded.
     */
    public Image getImage(final String resourceKey)
    {
        return _resources.getImage(resourceKey);
    }
}
