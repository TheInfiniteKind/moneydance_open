package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.moneydance.apps.md.controller.*
import com.moneydance.apps.md.view.gui.*
import com.moneydance.modules.features.contextmenutools.util.Util
import com.moneydance.modules.features.contextmenutools.util.Util.logConsole
import javax.swing.*

@Suppress("DuplicatedCode")

interface ContextMenuAction {
  fun getActions(context:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action>
}

/**
 * A collection of context menu (right click) tools that hook into Moneydance's context menu...
 *
 * @author Stuart Beesley - February 2026
 * @since MD2024.4(5253)
 */
class Main : FeatureModule(), PreferencesListener {
  
  override fun init() {
    EXTN_ID = moduleID

    val context = context
    mdMain = context as com.moneydance.apps.md.controller.Main  // upcast back to main to get full Moneydance capabilites
    val mdMain = mdMain!! // shadow copy and null-check once/upfront
    
    Util.APPDEBUG_ENABLED = mdMain.build >= 5100
    require(mdMain.build >= 5253) { "Sorry, this extension is only enabled for MD2024.4(5253) onwards...." }

    // if moneydance was launched with -d or the system property is set.....
    DEBUG = (com.moneydance.apps.md.controller.Main.DEBUG || java.lang.Boolean.getBoolean("moneydance.debug"))
    logConsole(true, "** DEBUG IS ON **")
    
    extensionContext = this
    
    addPreferencesListener()
    
    // register on the extensions menu
    //context.registerFeature(this, moduleID, null, "${getName()}: Context Menu Tools...")
    logConsole("Initialized (Kotlin) build: $versionString ${if (PREVIEW_BUILD) "(PREVIEW) " else ""}")
  }
  
  /**
   * Return a list of contextual actions (javax.swing.Action) that the extension can perform
   * on target objects which are given in the context parameter, along with references to the kind of context and the UI object.
   * The default implementation of this method returns an empty list. If you override it,
   * please ensure that it returns quickly so that the context menu appearance remains snappy.
   *
   * @param context Information about the context, including
   * @return a list of actions that the UI can perform on the
   *
   * @since Moneydance 2024 (build 5100)
   */
  override fun getActionsForContext(context:MDActionContext):List<Action> {

    val actions = mutableListOf<Action>()

    val listAccts = context.accounts
    val listTxns = context.items.filterIsInstance<AbstractTxn>()

    // quick do-nothing exit if there are no items/accounts to process...
    if (listTxns.isEmpty() && listAccts.isEmpty()) return actions
    
    when (context.type) {
      ActionContextType.register -> {
        actions += DuplicateTransactions().getActions(menuContext = context, listAccts = listAccts, listTxns = listTxns)
      }
      
      else -> return actions
    }
    return actions
  }
  
  override fun cleanup() {
    // never actually called by Moneydance!?
    logConsole(true, "::cleanup() called (will pass onto .unload()....)...")
    unload()
  }
  
  override fun unload() {
    // NOTE: we are using SecondaryWindow/Dialog(s), and they should auto-close/cleanup when dataset changes....
    logConsole(true, "::unload() called....")
    removePreferencesListener()

    @Suppress("UsePropertyAccessSyntax")
    val secWindows = mdGUI.getSecondaryWindows().toList()

    try {
      secWindows.forEach { win ->
        if (win is SecondaryFrame) {
          if (win.name.equals(moduleID, ignoreCase = true)) {
            logConsole(true, "... attempting to close: '${win.javaClass.simpleName}'")
            win.goAway()
          }
        } else if (win is SecondaryDialog) {
          if (win.name.equals(moduleID, ignoreCase = true)) {
            logConsole(true, "... attempting to close: '${win.javaClass.simpleName}'")
            win.goAway()
          }
        }
      }
    } catch (e: Exception) { logConsole("Error closing window: '$e'") }
  }
  
  override fun handleEvent(appEvent: String) {
    logConsole(true, "::handleEvent($appEvent) doing nothing")
    //if (eventStr.equalsIgnoreCase(AppEventManager.FILE_OPENED)) {
    //    // do stuff with dataset here....
    //}
  }
  
  /** Process an invocation of this module with the given URI  */
  override fun invoke(uri: String) {
    var command = uri
    val params: String
    val colonIdx = uri.indexOf(':')
    if (colonIdx >= 0) {
      command = uri.substring(0, colonIdx)
      params = uri.substring(colonIdx + 1)
    } else {
      params = ""
    }
    logConsole(true, "::invoke($uri) - command: '$command' params: $params")

    when (command) {
      moduleID -> { mdGUI.showInfoMessage("Context Menu Tools extension has no menu functions...") }
      else -> logConsole("::invoke($uri) - no valid id/command received >> doing nothing")
    }
  }
  
  override fun getName(): String { return getModuleMetaData().moduleName }
  
  private fun addPreferencesListener() {
    context?.let { mdMain?.preferences?.addListener(this) }
  }
  
  private fun removePreferencesListener() {
    context?.let { mdMain?.preferences?.removeListener(this)
    }
  }
  
  override fun preferencesUpdated() {
    logConsole(true, "::preferencesUpdated() called - doing nothing")
  }
  
  companion object {

    @JvmField var mdMain:com.moneydance.apps.md.controller.Main? = null
    
    val unprotectedContext:FeatureModuleContext? get() = mdMain
    val mdGUI:MoneydanceGUI get() = mdMain?.ui!! as MoneydanceGUI
    val versionString:String get() = "${extensionContext?.build ?: "???"}"

    @JvmStatic var EXTN_ID = "???"
    
    @JvmStatic var DEBUG = false
    
    var extensionContext:Main? = null
    var PREVIEW_BUILD = true            //TODO - update accordingly
    
  } // end companion object
}

