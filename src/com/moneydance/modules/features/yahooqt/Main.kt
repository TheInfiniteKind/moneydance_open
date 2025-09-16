/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.util.AppDebug
import com.moneydance.apps.md.controller.FeatureModule
import com.moneydance.apps.md.controller.FeatureModuleContext
import com.moneydance.apps.md.controller.PreferencesListener
import com.moneydance.apps.md.controller.UserPreferences
import com.moneydance.apps.md.controller.time.TimeInterval
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import com.moneydance.modules.features.yahooqt.SQUtil.urlEncode
import java.awt.Image
import java.awt.Toolkit
import java.beans.PropertyChangeEvent
import java.beans.PropertyChangeListener
import java.io.ByteArrayOutputStream
import java.text.MessageFormat
import java.util.*
import javax.swing.SwingUtilities

val QER_DLOG = AppDebug.logger("QER_DEBUG").setEnabled(AppDebug.DEBUG.isEnabled)
val QER_LOG = AppDebug.ALL

/**
 * Pluggable module used to allow users to download stock quote information from quote.yahoo.com
 */
class Main
  
  : FeatureModule(), ResourceProvider {
  private val _prefListener: PreferencesListener = QuotesPreferencesListener()
  private val _progressListener: PropertyChangeListener = QuotesProgressListener()
  private var _model: StockQuotesModel? = null
  private var _resources: ResourceBundle? = null
  
  override fun init() {
    // the first thing we will do is register this module to be invoked
    // via the application toolbar
    val context = context!!
    mdMain = context as com.moneydance.apps.md.controller.Main
    _model = StockQuotesModel()
    loadResources()
    _model!!.resources = this
    context.registerFeature(this, SHOW_DIALOG_COMMAND, icon, getName())
    context.registerFeature(this, UPDATE_COMMAND, icon, _resources!!.getString("updateNowMenuTitle"))
    addPreferencesListener()
    val mdGUI = (context as com.moneydance.apps.md.controller.Main).ui as MoneydanceGUI
    _model!!.initialize(mdGUI, this)
    
    
    // If root is null, then we'll just wait for the MD_OPEN_EVENT_ID event. When the plugin
    // is first installed, the root should be non-null. When MD starts up, it is likely to be null
    // until the file is opened.
    _model!!.setData(context.currentAccountBook)
  }
  
  // never actually called by Moneydance!
  override fun cleanup() {
    removePreferencesListener()
    _model!!.cleanUp()
  }

  override fun unload() { cleanup() }
  
  fun loadResources() {
    val locale = (context as com.moneydance.apps.md.controller.Main)
      .preferences.locale
    val englishFile = N12EStockQuotes.ENGLISH_PROPERTIES_FILE
    val englishInputStream = javaClass.getResourceAsStream(englishFile)
    try {
      val englishBundle = XmlResourceBundle(englishInputStream)
      if (locale != Locale.US) {
        // load the localized file and set US English as its parent
        var localizedFile = MessageFormat.format(
          N12EStockQuotes.PROPERTIES_FILE_FMT,
          locale.toString()
        )
        var targetInputStream = javaClass.getResourceAsStream(localizedFile)
        if (targetInputStream == null) {
          // try just the language
          localizedFile = MessageFormat.format(
            N12EStockQuotes.PROPERTIES_FILE_FMT,
            locale.language
          )
          targetInputStream = javaClass.getResourceAsStream(localizedFile)
        }
        _resources = if (targetInputStream != null) {
          XmlResourceBundle(targetInputStream, englishBundle)
        } else {
          // could not find a match, default to English
          englishBundle
        }
      } else {
        _resources = englishBundle
      }
    } catch (error: Exception) {
      System.err.println(N12EStockQuotes.XML_RESOURCE_LOAD_FAIL)
      error.printStackTrace()
    }
  }
  
  override fun getString(key: String): String {
    if (_resources == null) return ""
    return _resources!!.getString(key)
  }
  
  private fun updateNow() {
    val rootAccount = _model!!.rootAccount ?: return
    // nothing to do
    
    
    // exchange rates first so that the proper exchange rates are used for security price conversions
    _model!!.downloadRatesAndPricesInBackground(_progressListener)
  }
  
  override fun handleEvent(s: String) {
    super.handleEvent(s)
    if (N12EStockQuotes.MD_OPEN_EVENT_ID == s) {
      // cancel any running update
      _model!!.cancelCurrentTask()
      _model!!.setData(context!!.currentAccountBook)
      _model!!.runUpdateIfNeeded(true, _progressListener) // delay the start of downloading a bit to allow MD to finish up loading
    } else if (N12EStockQuotes.MD_CLOSING_EVENT_ID == s ||
               N12EStockQuotes.MD_EXITING_EVENT_ID == s
    ) {
      // cancel any running update
      _model!!.cancelCurrentTask()
      _model!!.setData(null)
    }
  }
  
  /**
   * Process an invocation of this module with the given URI
   */
  override fun invoke(uri: String) {
    var command = uri
    val colonIdx = uri.indexOf(':')
    if (colonIdx >= 0) {
      command = uri.substring(0, colonIdx)
    }
    
    if (UPDATE_COMMAND == command) {
      updateNow()
    } else {
      if (SHOW_DIALOG_COMMAND == command) {
        // should invoke later so this can be returned to its thread
        SwingUtilities.invokeLater { SettingsWindow(context!!, this@Main, _model!!).isVisible = true }
      }
    }
  }
  
  override fun getName(): String {
    var name = getString(L10NStockQuotes.TITLE)
    if (isBlank(name)) {
      name = N12EStockQuotes.TITLE
    }
    return name
  }
  
  private fun showProgress(progress: Float, label: String?) {
    val sb = StringBuilder("moneydance:setprogress:meter=")
    sb.append(urlEncode(progress.toString()))
    if (label != null) {
      sb.append("&label=")
      sb.append(urlEncode(label))
    }
    context!!.showURL(sb.toString())
  }
  
  private fun addPreferencesListener() {
    if (context != null) {
      (context as com.moneydance.apps.md.controller.Main).preferences
        .addListener(_prefListener)
    }
  }
  
  private fun removePreferencesListener() {
    if (context != null) {
      (context as com.moneydance.apps.md.controller.Main).preferences
        .removeListener(_prefListener)
    }
  }
  
  /**
   * Listen for changes in the locale and reload everything in the new locale.
   */
  private inner class QuotesPreferencesListener : PreferencesListener {
    override fun preferencesUpdated() {
      // reload
      loadResources()
    }
  }
  
  private inner class QuotesProgressListener : PropertyChangeListener {
    override fun propertyChange(event: PropertyChangeEvent) {
      val name = event.propertyName
      if (N12EStockQuotes.STATUS_UPDATE == name) {
        val progress = (event.oldValue as String).toFloat()
        val status = event.newValue as String
        showProgress(progress, status)
      } // download ended
    } // propertyChange
  } // QuotesProgressListener
  
  companion object {
    
    var mdMain: com.moneydance.apps.md.controller.Main? = null
    val mdGUI: MoneydanceGUI get() = mdMain?.ui as MoneydanceGUI

    private const val SHOW_DIALOG_COMMAND = "showDialog"
    private const val UPDATE_COMMAND = "update"
    
    const val RATE_LAST_UPDATE_KEY: String = "yahooqt.rateLastUpdate"
    const val AUTO_UPDATE_KEY: String = "yahooqt.autoUpdate"
    const val UPDATE_INTERVAL_KEY: String = "yahooqt.updateInterval"
    const val QUOTE_LAST_UPDATE_KEY: String = "yahooqt.quoteLastUpdate"
    
    /** Parameters saved to the data file for which connections to use.  */
    const val HISTORY_CONNECTION_KEY: String = "yahooqt.historyConnection"
    const val EXCHANGE_RATES_CONNECTION_KEY: String = "yahooqt.exchangeRatesConnection"
    
    fun getUpdateFrequency(preferences: UserPreferences): TimeInterval {
      val paramStr = preferences.getSetting(UPDATE_INTERVAL_KEY) ?: ""
      if (isBlank(paramStr)) return TimeInterval.MONTH
      return TimeInterval.fromChar(paramStr[0])
    }
    
    val icon: Image?
      get() {
        try {
          val cl = Main::class.java.classLoader
          val `in` =
            cl.getResourceAsStream("/com/moneydance/modules/features/yahooqt/icon-yahooqt.gif")
          if (`in` != null) {
            val bout = ByteArrayOutputStream(1000)
            val buf = ByteArray(256)
            var n: Int
            while ((`in`.read(buf, 0, buf.size).also { n = it }) >= 0) bout.write(buf, 0, n)
            return Toolkit.getDefaultToolkit().createImage(bout.toByteArray())
          }
        } catch (ignored: Throwable) {
        }
        return null
      }
  }
  
}

