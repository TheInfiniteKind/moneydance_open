/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import java.awt.Image;

/**
 * <p>Provides localized resources.</p>
 * 
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
public interface IResourceProvider
{
    /**
     * Obtain the given string from the resource bundle.
     * @param resourceKey The key to look up the resources.
     * @return The associated string, or <code>null</code> if the key is not found.
     */
    public String getString(final String resourceKey);

    /**
     * Obtain the given image from the resource bundle. The key specifies an image URL.
     * @param resourceKey The key to look up the resources with.
     * @return The associated image, or <code>null</code> if the key is not found or the image
     * could not be loaded.
     */
    public Image getImage(final String resourceKey);
}