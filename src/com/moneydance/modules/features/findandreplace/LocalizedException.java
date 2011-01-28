/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;


/**
 * <p>Exception that can load in a localized message.</p>
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class LocalizedException extends Exception
{
    private final IResourceProvider _resources;

    LocalizedException(final String resourceKey, final IResourceProvider resources)
    {
        super(resourceKey);
        _resources = resources;
    }


    @Override
    public String getLocalizedMessage()
    {
        if (_resources != null)
        {
            return _resources.getString(getMessage());
        }
        return getMessage();
    }
}
