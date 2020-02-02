/*************************************************************************\
* Copyright (C) 2009-2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.PreferencesListener;
import com.infinitekind.moneydance.model.*;

import javax.swing.JOptionPane;
import java.io.*;
import java.util.*;
import java.awt.*;
import java.text.MessageFormat;
import java.util.List;

/**
 * <p>Pluggable module used to give users access to a Find and Replace
 * interface to Moneydance.</p>
 *
 * @author Kevin Menningen
 * @version Build 209
 * @since 1.0
 */
public class Main extends FeatureModule
{
    private final PreferencesListener _prefListener = new FarPreferencesListener();
    private final List<IFindAndReplaceController> _controllerList = new ArrayList<IFindAndReplaceController>();
    private final Object _listSync = new Object();
    private FarHomeView _homePageView = null;
    private ResourceBundle _resources;

    private boolean _testMode;
    private AccountBook _testBook;

    public String getBuildString() {
        return Integer.toString(getBuild());
    }

    public void init()
    {
        super.init();

        // the first thing we will do is register this module to be invoked
        // via the application toolbar
        FeatureModuleContext context = getContext();
        try
        {
            if ( context != null )
            {
                loadResources();
                context.registerFeature(this, N12EFindAndReplace.INVOKE_COMMAND,
                                        getIcon(),
                                        getName());

                addPreferencesListener();

                // setup the home page view
                _homePageView = new FarHomeView(this);
                getContext().registerHomePageView(this, _homePageView);
            }
            Logger.log(String.format("Initialized build %s ok", getBuildString()));
        }
        catch (Exception error)
        {
            handleException(error);
        }
    }

    public void cleanup()
    {
        cleanupFarComponent(null);
        removePreferencesListener();
    }

    void setTestMode(final boolean testing)
    {
        _testMode = testing;
    }

    void loadResources()
    {
        Locale locale = ((com.moneydance.apps.md.controller.Main) getContext())
                .getPreferences().getLocale();
        _resources = ResourceBundle.getBundle(N12EFindAndReplace.RESOURCES, locale,
                new XmlResourceControl());

    }

    void setTestData(AccountBook testBook)
    {
        _testBook = testBook;
    }

    String getString(final String key)
    {
        if (_resources == null)
        {
            return null;
        }
        return _resources.getString( key );
    }

    Image getImage(final String resourceKey)
    {
        if (_resources == null)
        {
            return null;
        }
        String urlName = _resources.getString( resourceKey );
        try
        {
            java.io.InputStream inputStream = getClass().getResourceAsStream(urlName);
            if (inputStream != null)
            {
                ByteArrayOutputStream outputStream = new ByteArrayOutputStream(1000);
                byte buffer[] = new byte[1024];
                int count;
                while ((count = inputStream.read(buffer, 0, buffer.length)) >= 0)
                {
                    outputStream.write(buffer, 0, count);
                }
                return Toolkit.getDefaultToolkit().createImage(outputStream.toByteArray());
            }
        }
        catch (IOException error)
        {
            handleException(error);
        }
        return null;
    }

    /**
     * Load an icon from resources.
     * @return The icon, or null if an error occurred.
     */
    Image getIcon()
    {
        return getImage(L10NFindAndReplace.FAR_IMAGE);
    }

    /**
     * Process an invocation of this module with the given URI
     * The format is {command}?{parameters} or {command}:
     */
    public void invoke(String uri)
    {
        String command = uri;
        int theIdx = uri.indexOf('?');
        if (theIdx >= 0)
        {
            command = uri.substring(0, theIdx);
        }
        else
        {
            theIdx = uri.indexOf(':');
            if (theIdx >= 0)
            {
                command = uri.substring(0, theIdx);
            }
        }

        if (N12EFindAndReplace.INVOKE_COMMAND.equals(command))
        {
            addNewDialog(null);
        }
    }

    public String getName()
    {
        String name = getString(L10NFindAndReplace.TITLE);
        if ((name == null) || (name.length() == 0))
        {
            name = N12EFindAndReplace.TITLE;
        }
        return name;
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////
    private void addPreferencesListener()
    {
        if (getContext() != null)
        {
            ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences()
                    .addListener(_prefListener);
        }
    }

    private void removePreferencesListener()
    {
        if (getContext() != null)
        {
            ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences()
                    .removeListener(_prefListener);
        }
    }

    void addNewDialog(final String initialText)
    {
        try
        {
            // obtain the data if possible
            FeatureModuleContext context = getUnprotectedContext();
            AccountBook book = null;
            if (context != null)
            {
                book = getUnprotectedContext().getCurrentAccountBook();
            }
            else if (_testMode)
            {
                book = _testBook;
            }

            if (book != null)
            {
                final IFindAndReplaceController controller = FindAndReplace.createInstance(this);
                controller.loadData(book);
                controller.setInitialFreeText(initialText);
                controller.show();
                synchronized (_listSync)
                {
                    _controllerList.add(controller);
                }
            }
            else
            {
                // can't show the dialog without a file (nothing to search)
                final String title = _resources.getString(L10NFindAndReplace.ERROR_TITLE);
                final String message = _resources.getString(L10NFindAndReplace.ERROR_NO_DATA);
                JOptionPane.showMessageDialog(null, message, title, JOptionPane.WARNING_MESSAGE);
            }
        }
        catch (Exception error)
        {
            handleException(error);
        }
    }


    void handleException(Exception error)
    {
        Logger.logError(N12EFindAndReplace.ERROR_LOADING, error);
        if (_resources != null)
        {
            final String title = _resources.getString(L10NFindAndReplace.ERROR_TITLE);
            final String format = _resources.getString(L10NFindAndReplace.ERROR_LOAD_FMT);
            final String message = MessageFormat.format(format, error.getLocalizedMessage());
            JOptionPane.showMessageDialog(null, message, title, JOptionPane.ERROR_MESSAGE);
        }
        else
        {
            // can't localize
            JOptionPane.showMessageDialog(null, N12EFindAndReplace.ERROR_LOADING,
                    N12EFindAndReplace.ERROR_TITLE, JOptionPane.ERROR_MESSAGE);
        }
    }


    FeatureModuleContext getUnprotectedContext()
    {
        return getContext();
    }

    /**
     * Remove a particular instance of Find and Replace. If <code>null</code> passed in, all
     * instances of Find and Replace are removed.
     * @param controller The controller instance to remove. If <code>null</code>, remove all.
     */
    void cleanupFarComponent(final IFindAndReplaceController controller)
    {
        synchronized (_listSync)
        {
            if (controller == null)
            {
                for (IFindAndReplaceController c : _controllerList)
                {
                    c.cleanUp();
                }
                _controllerList.clear();
            }
            else
            {
                controller.cleanUp();
                _controllerList.remove(controller);
            }
        }
        System.gc();
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Inner Classes
    ///////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Listen for changes in the locale and reload everything in the new locale.
     */
    private class FarPreferencesListener implements PreferencesListener
    {
        public void preferencesUpdated()
        {
            // reload
            cleanupFarComponent(null);
            loadResources();
            if (_homePageView != null)
            {
                _homePageView.refresh();
            }
        }
    }
}


