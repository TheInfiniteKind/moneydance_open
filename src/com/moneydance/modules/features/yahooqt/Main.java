/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.PreferencesListener;
import com.moneydance.apps.md.controller.UserPreferences;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.time.*;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.*;
import java.awt.*;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.text.MessageFormat;
import java.util.Locale;
import java.util.ResourceBundle;

/**
 * Pluggable module used to allow users to download stock quote information from quote.yahoo.com
 */
public class Main
  extends FeatureModule
  implements ResourceProvider
{
  private static final String SHOW_DIALOG_COMMAND = "showDialog";
  private static final String UPDATE_COMMAND = "update";

  public static boolean DEBUG_YAHOOQT = true;

  static final String RATE_LAST_UPDATE_KEY = "yahooqt.rateLastUpdate";
  static final String AUTO_UPDATE_KEY = "yahooqt.autoUpdate";
  static final String UPDATE_INTERVAL_KEY = "yahooqt.updateInterval";
  static final String QUOTE_LAST_UPDATE_KEY = "yahooqt.quoteLastUpdate";
  /** Parameters saved to the data file for which connections to use. */
  static final String HISTORY_CONNECTION_KEY = "yahooqt.historyConnection";
  static final String EXCHANGE_RATES_CONNECTION_KEY = "yahooqt.exchangeRatesConnection";
  
  private final PreferencesListener _prefListener = new QuotesPreferencesListener();
  private final PropertyChangeListener _progressListener = new QuotesProgressListener();
  private StockQuotesModel _model;
  private ResourceBundle _resources;
  
  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    _model = new StockQuotesModel(context);
    loadResources();
    _model.setResources(this);
    context.registerFeature(this, SHOW_DIALOG_COMMAND, getIcon(), getName());
    context.registerFeature(this, UPDATE_COMMAND, getIcon(), _resources.getString("updateNowMenuTitle"));
    addPreferencesListener();
    MoneydanceGUI mdGUI = (MoneydanceGUI)((com.moneydance.apps.md.controller.Main) context).getUI();
    _model.initialize(mdGUI, this);
    
    // If root is null, then we'll just wait for the MD_OPEN_EVENT_ID event. When the plugin
    // is first installed, the root should be non-null. When MD starts up, it is likely to be null
    // until the file is opened.
    _model.setData(getContext().getCurrentAccountBook());
  }
  
  public void cleanup() {
    removePreferencesListener();
    _model.cleanUp();
  }
  
  void loadResources() {
    Locale locale = ((com.moneydance.apps.md.controller.Main) getContext())
            .getPreferences().getLocale();
    String englishFile = N12EStockQuotes.ENGLISH_PROPERTIES_FILE;
    InputStream englishInputStream = getClass().getResourceAsStream(englishFile);
    try {
      XmlResourceBundle englishBundle = new XmlResourceBundle(englishInputStream);
      if (!locale.equals(Locale.US)) {
        // load the localized file and set US English as its parent
        String localizedFile = MessageFormat.format(N12EStockQuotes.PROPERTIES_FILE_FMT,
                locale.toString());
        InputStream targetInputStream = getClass().getResourceAsStream(localizedFile);
        if (targetInputStream == null) {
          // try just the language
          localizedFile = MessageFormat.format(N12EStockQuotes.PROPERTIES_FILE_FMT,
                  locale.getLanguage());
          targetInputStream = getClass().getResourceAsStream(localizedFile);
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
    }
    catch (Exception error) {
      System.err.println(N12EStockQuotes.XML_RESOURCE_LOAD_FAIL);
      error.printStackTrace();
    }
  }

  public String getString(final String key) {
    if (_resources == null) return "";
    return _resources.getString(key);
  }

  static TimeInterval getUpdateFrequency(UserPreferences preferences) {
    String paramStr = preferences.getSetting(UPDATE_INTERVAL_KEY, "");
    if (SQUtil.isBlank(paramStr)) return TimeInterval.MONTH;
    return TimeInterval.fromChar(paramStr.charAt(0));
  }

  private void updateNow() {
    Account rootAccount = _model.getRootAccount();
    if (rootAccount == null) return; // nothing to do
    // exchange rates first so that the proper exchange rates are used for security price conversions
    
    _model.downloadRatesAndPricesInBackground(_progressListener);
  }

  static Image getIcon() {
    try {
      ClassLoader cl = Main.class.getClassLoader();
      java.io.InputStream in =
          cl.getResourceAsStream("/com/moneydance/modules/features/yahooqt/icon-yahooqt.gif");
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
    if (N12EStockQuotes.MD_OPEN_EVENT_ID.equals(s)) {
      // cancel any running update
      _model.cancelCurrentTask();
      _model.setData(getContext().getCurrentAccountBook());
      _model.runUpdateIfNeeded(true, _progressListener);// delay the start of downloading a bit to allow MD to finish up loading
    } else if (N12EStockQuotes.MD_CLOSING_EVENT_ID.equals(s) ||
               N12EStockQuotes.MD_EXITING_EVENT_ID.equals(s)) {
      // cancel any running update
      _model.cancelCurrentTask();
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

    if (UPDATE_COMMAND.equals(command)) {
      updateNow();
    } else {
      if (SHOW_DIALOG_COMMAND.equals(command)) {
        // should invoke later so this can be returned to its thread
        SwingUtilities.invokeLater(new Runnable() {
          public void run() {
            new SettingsWindow(getContext(), Main.this, _model).setVisible(true);
          }
        });
      }
    }
  }

  public String getName() {
    String name = getString(L10NStockQuotes.TITLE);
    if (SQUtil.isBlank(name)) {
      name = N12EStockQuotes.TITLE;
    }
    return name;
  }

  private void showProgress(float progress, String label) {
    StringBuilder sb = new StringBuilder("moneydance:setprogress:meter=");
    sb.append(SQUtil.urlEncode(String.valueOf(progress)));
    if (label != null) {
      sb.append("&label=");
      sb.append(SQUtil.urlEncode(label));
    }
    getContext().showURL(sb.toString());
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
  private class QuotesPreferencesListener implements PreferencesListener {
    public void preferencesUpdated() {
      // reload
      loadResources();
    }
  }

  private class QuotesProgressListener implements PropertyChangeListener {
    public void propertyChange(PropertyChangeEvent event) {
      final String name = event.getPropertyName();
      if (N12EStockQuotes.STATUS_UPDATE.equals(name)) {
        final float progress = Float.valueOf((String)event.getOldValue()).floatValue();
        final String status = (String) event.getNewValue();
        showProgress(progress, status);
      } // download ended
    } // propertyChange
  } // QuotesProgressListener
}

