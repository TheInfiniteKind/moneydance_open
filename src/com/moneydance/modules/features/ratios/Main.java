/*
 * ************************************************************************
 * Copyright (C) 2012-2015 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

// UPDATED BY STUART BEESLEY - StuWareSoftSystems - August 2023
// Build: 1037 - Fix/correct for MD2023.2(5008+) AcctFilter changes (and correct build 1036 issue with IK fix)...
//               Added .unload() (and also a redirect from .cleanup())
// Build: 1038 - Fix numerator issue - refer: https://infinitekind.tenderapp.com/discussions/problems/92963-ratios-extension
//               Disabled help guide button(s) as the server with the help file is not available....
// Build: 1039 - Never actually released... Bumping build number....
// Build: 1040 - Fix negative issue caused by 1038 fix - refer: https://infinitekind.tenderapp.com/discussions/problems/97947-ratios-extension-1038-broke-transfers-difference-feature-shows-random-negative-values

package com.moneydance.modules.features.ratios;

import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.PreferencesListener;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.AwtUtil;
import com.infinitekind.util.StringUtils;

import javax.swing.SwingUtilities;
import java.awt.Component;
import java.awt.Image;
import java.awt.Toolkit;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.text.MessageFormat;
import java.util.Locale;
import java.util.ResourceBundle;

/**
 * Compute ratios of values, where the numerator and the denominator can be defined
 * separately and in different ways.
 * Display the ratio list on the home page.
 * Show a report for a particular ratio.
 *
 * @author Kevin Menningen
 */

// Builds 1038-1040 address several issues mentioned here:
// https://infinitekind.tenderapp.com/discussions/problems/92963-ratios-extension
// https://infinitekind.tenderapp.com/discussions/problems/97947-ratios-extension-1038-broke-transfers-difference-feature-shows-random-negative-values
// Build 1041 implements own version of: BasePropertyChangeReporter
// Build 1042 handle the nuked setSuppressMessageDialogs() method for 2024.2(515x)
// Build 1044 handle the renamed generate() method for MD2024.3(5173)

public class Main extends FeatureModule implements ResourceProvider {

    private final PreferencesListener _prefListener = new RatiosPreferencesListener();
    private final RatiosExtensionModel _model;
    private RatiosHomeView _homePageView = null;
    private ResourceBundle _resources;

    public static Main THIS_EXTENSION_CONTEXT;

    public static boolean DEBUG = false;
    public static boolean PREVIEW_BUILD = false;
    public static com.moneydance.apps.md.controller.Main MD_REF;

    public static final String EXTN_ID = "ratios";
    public static final String EXTN_NAME = "Ratio Calculator";

    public Main() {
        _model = new RatiosExtensionModel();
    }

    public void init() {

        // if moneydance was launched with -d or the system property is set.....
        Main.DEBUG = (com.moneydance.apps.md.controller.Main.DEBUG || Boolean.getBoolean("moneydance.debug"));
        Util.logConsole(true, "** DEBUG IS ON **");

        THIS_EXTENSION_CONTEXT = this;

        // the first thing we will do is register this module to be invoked
        // via the application toolbar
        FeatureModuleContext context = getContext();
        MD_REF = (com.moneydance.apps.md.controller.Main) context;

        loadResources();
        _model.setResources(this);
        context.registerFeature(this, N12ERatios.SHOW_DIALOG_COMMAND, getIcon(N12ERatios.EXTENSION_ICON), getName());
        addPreferencesListener();
        MoneydanceGUI mdGUI = (MoneydanceGUI) ((com.moneydance.apps.md.controller.Main) context).getUI();
        _model.initialize(mdGUI);
        final AccountBook book = getContext().getCurrentAccountBook();
        // If book is null, then we'll just wait for the MD_OPEN_EVENT_ID event. When the plugin
        // is first installed, the book should be non-null. When MD starts up, it is likely to be null
        // until the file is opened.
        if (book != null) _model.setData(book);
        // setup the home page view
        _homePageView = new RatiosHomeView(this, _model);
        getContext().registerHomePageView(this, _homePageView);
        Logger.log(String.format("Initialized build %s ok", getVersionString()));
    }

    public static com.moneydance.apps.md.controller.Main getMDMain() {
        return MD_REF;
    }

    public static FeatureModuleContext getUnprotectedContext() {
        return getMDMain();
    }

    public static Main getExtensionContext() { return THIS_EXTENSION_CONTEXT; }

    public static MoneydanceGUI getMDGUI() {
        return (MoneydanceGUI) getMDMain().getUI();
    }

    public void cleanup() {
        // I don't this this is ever called by Moneydance!?
        Util.logConsole(true, ".cleanup() called (will pass onto .unload()....)...");
        unload();
    }

    @Override
    public void unload() {
        Util.logConsole(true, ".unload() called....");
        removePreferencesListener();
        _model.cleanUp();
    }

    public static String getVersionString() {
        return "Build " + getExtensionContext().getBuild();
    }

    public String getString(final String key) {
        if (_resources == null) return "";
        return _resources.getString(key);
    }

    static Image getIcon(final String imageUri) {
        try {
            ClassLoader cl = Main.class.getClassLoader();
            java.io.InputStream in = cl.getResourceAsStream(imageUri);
            if (in != null) {
                ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
                byte[] buf = new byte[256];
                int n;
                while ((n = in.read(buf, 0, buf.length)) >= 0)
                    bout.write(buf, 0, n);
                return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
            }
        } catch (Throwable ignored) {
        }
        return null;
    }

    @Override
    public void handleEvent(String s) {
        super.handleEvent(s);
        if (N12ERatios.MD_OPEN_EVENT_ID.equals(s)) {
            _model.setData(getContext().getCurrentAccountBook());
        } else if (N12ERatios.MD_CLOSING_EVENT_ID.equals(s) ||
                N12ERatios.MD_EXITING_EVENT_ID.equals(s)) {
            _model.setData(null);
        }
    }

    /**
     * Process an invocation of this module with the given URI
     */
    public void invoke(String uri) {
        String command = uri;
        int colonIdx = uri.indexOf(':');
        if (colonIdx >= 0) {
            command = uri.substring(0, colonIdx);
        }

        if (N12ERatios.SHOW_DIALOG_COMMAND.equals(command)) {
            // should invoke later so this can be returned to its thread
            SwingUtilities.invokeLater(() -> {
                Component parent = null;
                final AccountBook rootAccount = _model.getRootAccount();
                if (_homePageView != null) {
                    parent = _homePageView.getGUIView(rootAccount);
                }
                RatioSettingsDialog dialog = new RatioSettingsDialog(_model.getGUI(), AwtUtil.getFrame(parent),
                        _model.getResources(),
                        _model, rootAccount, _model.getSettings());
                dialog.loadData();
                dialog.setVisible(true);
            });
        }
    }

    public String getName() {
        String name = getString(L10NRatios.TITLE);
        if (StringUtils.isBlank(name)) {
            name = N12ERatios.TITLE;
        }
        return name;
    }

    private void loadResources() {
        Locale locale = ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences().getLocale();
        String englishFile = N12ERatios.ENGLISH_PROPERTIES_FILE;
        InputStream englishInputStream = Main.class.getClassLoader().getResourceAsStream(englishFile);
        try {
            XmlResourceBundle englishBundle = new XmlResourceBundle(englishInputStream);
            if (!locale.equals(Locale.US)) {
                // load the localized file and set US English as its parent
                String localizedFile = MessageFormat.format(N12ERatios.PROPERTIES_FILE_FMT,
                        locale.toString());
                InputStream targetInputStream = Main.class.getClassLoader().getResourceAsStream(localizedFile);
                if (targetInputStream == null) {
                    // try just the language
                    localizedFile = MessageFormat.format(N12ERatios.PROPERTIES_FILE_FMT,
                            locale.getLanguage());
                    targetInputStream = Main.class.getClassLoader().getResourceAsStream(localizedFile);
                }
                if (targetInputStream != null) {
                    _resources = new XmlResourceBundle(targetInputStream, englishBundle);
                } else {
                    // could not find a match, default to English
                    _resources = englishBundle;
                }
            } else {
                _resources = englishBundle;
            }
        } catch (Exception error) {
            Logger.log(N12ERatios.XML_RESOURCE_LOAD_FAIL);
            error.printStackTrace();
        }
    }

    private void addPreferencesListener() {
        if (getContext() != null) {
            ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences()
                    .addListener(_prefListener);
        }
    }

    private void removePreferencesListener() {
        if (getContext() != null) {
            ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences()
                    .removeListener(_prefListener);
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Inner Classes
    ///////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Listen for changes in the locale and reload everything in the new locale.
     */
    private class RatiosPreferencesListener
            implements PreferencesListener {
        public void preferencesUpdated() {
            // reload
            loadResources();
            if (_homePageView != null) _homePageView.refresh();
        }
    }
}

