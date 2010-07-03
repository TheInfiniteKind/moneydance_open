/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
 \************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.PreferencesListener;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.*;
import java.awt.*;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.ByteArrayOutputStream;
import java.util.Date;
import java.util.Locale;
import java.util.ResourceBundle;

// TODO: Figure out what to do about currency - currency of stock download might not match currency of
// TODO:    the account. Currently there's just a tooltip/message that warns of the mismatch.
// TODO: There may still be issues with background updates in the settings dialog.
// TODO: When loading a file during a download (user switches files during download), download is not canceled
// TODO: Exchange rates are always updated - whether or not I set the indicator. (possibly fixed)
// TODO: NASDAQ appends a suffix for Yahoo, shouldn't (exchanges can now be edited, so this might be okay)
// TODO: Exchanges are now screened by currency - if the main file doesn't have the currency for the
// TODO:    exchange, the exchange is hidden. Find out if this is okay for the users.
// TODO: Possible blank quotes - check mark for Quote but get: "Quote: £" for symbol GB0003874798GBP
// TODO: Combine two checkboxes for downloaded quotes/exchange rates to a simpler combo box
// TODO: Change the date setting to a simple combo "Daily, Weekly, Monthly" and add a "Next date:" label
// TODO:    User clicks on date and up comes calendar to pick the next update date.
// TODO: Find all the other TODOs and address them (most of them are for language translations)
// TODO: Change messages from "Downloading {name}..." to "Downloaded {name}, current price: {price}"
// TODO: Implement better logging messages that are generated along with the display messages
// TODO: Consider recompiling with MD2008 jar and fixing issues so it runs with MD2008
// TODO: Rebuild with Java 1.5 JDK and verify it works with Java 1.5
// TODO: Remove unused code, like StockConnection and stuff that's commented out
// TODO: Update name of the extension since it is more than Yahoo now

/**
 * Pluggable module used to allow users to download stock quote information from quote.yahoo.com
 */
public class Main
  extends FeatureModule
  implements ResourceProvider
{
  private static final String SHOW_DIALOG_COMMAND = "showDialog";
  private static final String UPDATE_COMMAND = "update";

  static final String RATE_LAST_UPDATE_KEY = "yahooqt.rateLastUpdate";
  static final String AUTO_UPDATE_KEY = "yahooqt.autoUpdate";
  static final String UPDATE_FREQUENCY_KEY = "yahooqt.updateFrequency";
  static final String DOWNLOAD_QUOTES_KEY = "yahooqt.downloadQuotes";
  static final String QUOTE_LAST_UPDATE_KEY = "yahooqt.quoteLastUpdate";
  static final String DOWNLOAD_RATES_KEY = "yahooqt.downloadRates";
  /** Parameter saved to the data file for which connection to use. */
  static final String CONNECTION_KEY = "yahooqt.connection";
  static final String MD_OPEN_EVENT_ID = "md:file:opened";
  static final String MD_CLOSING_EVENT_ID = "md:file:closing";
  static final String MD_EXITING_EVENT_ID = "md:app:exiting";

  private final PreferencesListener _prefListener = new QuotesPreferencesListener();
  private final PropertyChangeListener _progressListener = new QuotesProgressListener();
  private final StockQuotesModel _model;
  private ResourceBundle _resources;

  public Main() {
    _model = new StockQuotesModel(this);
  }
  
  public void init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    FeatureModuleContext context = getContext();
    loadResources();
    context.registerFeature(this, SHOW_DIALOG_COMMAND, getIcon(), getName());
    addPreferencesListener();
    MoneydanceGUI mdGUI = (MoneydanceGUI)((com.moneydance.apps.md.controller.Main) context).getUI();
    _model.initialize(mdGUI, this);
    final RootAccount root = getContext().getRootAccount();
    // If root is null, then we'll just wait for the MD_OPEN_EVENT_ID event. When the plugin
    // is first installed, the root should be non-null. When MD starts up, it is likely to be null
    // until the file is opened.
    if (root != null) _model.setData(root);
  }

  public void cleanup() {
    removePreferencesListener();
    _model.cleanUp();
  }

  void loadResources() {
    Locale locale = ((com.moneydance.apps.md.controller.Main) getContext())
            .getPreferences().getLocale();
    _resources = ResourceBundle.getBundle(N12EStockQuotes.RESOURCES, locale,
            new XmlResourceControl());
  }

  public String getString(final String key) {
    if (_resources == null) return "";
    return _resources.getString(key);
  }

  private void updateIfNeeded() {
    RootAccount account = _model.getRootAccount();
    String name = account.getAccountName();
    UserPreferences preferences = _model.getPreferences();
    if (preferences.getBoolSetting(AUTO_UPDATE_KEY, false)) {
      Frequency frequency = getUpdateFrequency();
      MDDate today = new MDDate();

      MDDate lastUpdateDate = getQuotesLastUpdateDate(name, account);
      MDDate nextUpdateDate = frequency.next(lastUpdateDate);
      if (nextUpdateDate.equals(today) || nextUpdateDate.isBefore(today)) {
        getQuotes();
        account.setParameter(QUOTE_LAST_UPDATE_KEY, today.toString());
      }
      lastUpdateDate = getRatesLastUpdateDate(name, account);
      nextUpdateDate = frequency.next(lastUpdateDate);
      if (nextUpdateDate.equals(today) || nextUpdateDate.isBefore(today)) {
        getRates();
        account.setParameter(RATE_LAST_UPDATE_KEY, today.toString());
      }
    }
  }

  private MDDate getQuotesLastUpdateDate(String prefix, RootAccount account) {
    MDDate lastUpdateDate;
    try {
      lastUpdateDate = MDDate.fromString(account.getParameter(QUOTE_LAST_UPDATE_KEY));
    } catch (IllegalArgumentException e) {
      lastUpdateDate = new MDDate(new Date(0L));
    }
    return lastUpdateDate;
  }

  private MDDate getRatesLastUpdateDate(String prefix, RootAccount account) {
    MDDate lastUpdateDate;
    try {
      lastUpdateDate = MDDate.fromString(account.getParameter(RATE_LAST_UPDATE_KEY));
    } catch (IllegalArgumentException e) {
      lastUpdateDate = new MDDate(new Date(0L));
    }
    return lastUpdateDate;
  }

  private Frequency getUpdateFrequency() {
    Frequency frequency;
    try {
      frequency = SimpleFrequency.fromString(_model.getPreferences().getSetting(UPDATE_FREQUENCY_KEY));
    } catch (IllegalArgumentException e) {
      frequency = TimeUnit.MONTH;
    }
    return frequency;
  }

  private void update() {
    UserPreferences preferences = _model.getPreferences();
    if (preferences.getBoolSetting(DOWNLOAD_QUOTES_KEY, false)) {
      getQuotes();
    }
    if (preferences.getBoolSetting(DOWNLOAD_RATES_KEY, false)) {
      getRates();
    }
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
    if (MD_OPEN_EVENT_ID.equals(s)) {
      // cancel any running update
      _model.cancelCurrentTask();
      _model.setData(getContext().getRootAccount());
      updateIfNeeded();
    } else if (MD_CLOSING_EVENT_ID.equals(s) || MD_EXITING_EVENT_ID.equals(s)) {
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
      update();
    } else {
      if (SHOW_DIALOG_COMMAND.equals(command)) {
        // should invoke later so this can be returned to its thread
        SwingUtilities.invokeLater(new Runnable() {
          public void run() {
            YahooDialog dialog = new YahooDialog(getContext(), Main.this, _model);
            dialog.setVisible(true);
            if (dialog.userAcceptedChanges()) updateIfNeeded();
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

  private void getQuotes() {
    _model.addPropertyChangeListener(_progressListener);
    _model.runStockPriceDownload();
  }

  private void getRates() {
    _model.addPropertyChangeListener(_progressListener);
    _model.runRatesDownload();
  }

  private void showProgress(float progress, String label) {
    getContext().showURL("moneydance:setprogress:meter=" +
        SQUtil.urlEncode(String.valueOf(progress)) +
        (label == null ? "" : "&label=" + SQUtil.urlEncode(label)));
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
      } else if (N12EStockQuotes.DOWNLOAD_BEGIN.equals(name)) {
      } else if (N12EStockQuotes.DOWNLOAD_END.equals(name)) {
        _model.removePropertyChangeListener(_progressListener);
      }
    }
  }
}

