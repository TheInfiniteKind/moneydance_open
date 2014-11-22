/*
 * ************************************************************************
 * Copyright (C) 2012-2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.PreferencesListener;
import com.infinitekind.moneydance.model.*;
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
public class Main
    extends FeatureModule
    implements ResourceProvider {
  private static final String VERSION = "Build 26"; // should match meta_info.dict
  private final PreferencesListener _prefListener = new RatiosPreferencesListener();
  private final RatiosExtensionModel _model;
  private RatiosHomeView _homePageView = null;
  private ResourceBundle _resources;

  public Main() {
    _model = new RatiosExtensionModel();
  }

  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    loadResources();
    _model.setResources(this);
    context.registerFeature(this, N12ERatios.SHOW_DIALOG_COMMAND, getIcon(N12ERatios.EXTENSION_ICON), getName());
    addPreferencesListener();
    MoneydanceGUI mdGUI = (MoneydanceGUI) ((com.moneydance.apps.md.controller.Main) context).getUI();
    _model.initialize(mdGUI);
    final AccountBook book = getContext().getCurrentAccountBook();
    // If root is null, then we'll just wait for the MD_OPEN_EVENT_ID event. When the plugin
    // is first installed, the root should be non-null. When MD starts up, it is likely to be null
    // until the file is opened.
    if (book != null) _model.setData(book);
    // setup the home page view
    _homePageView = new RatiosHomeView(this, _model);
    getContext().registerHomePageView(this, _homePageView);
  }

  public void cleanup() {
    removePreferencesListener();
    _model.cleanUp();
  }

  public static String getVersionString() {
    return VERSION;
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
        byte buf[] = new byte[256];
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
      SwingUtilities.invokeLater(new Runnable() {
        public void run() {
          Component parent = null;
          final AccountBook book = _model.getRootAccount();
          if (_homePageView != null) {
            parent = _homePageView.getGUIView(book);
          }
          RatioSettingsDialog dialog = new RatioSettingsDialog(_model.getGUI(), AwtUtil.getFrame(parent),
                                                               _model.getResources(),
                                                               _model, book, _model.getSettings());
          dialog.loadData();
          dialog.setVisible(true);
        }
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
    Locale locale = ((com.moneydance.apps.md.controller.Main) getContext())
        .getPreferences().getLocale();
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
      System.err.println(N12ERatios.XML_RESOURCE_LOAD_FAIL);
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

