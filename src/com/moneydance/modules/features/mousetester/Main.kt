/**
 * MouseTester: Simple java extension to test mouse clicks
 * Originally Java >> Kotlin'ized September 2024
 * @author Stuart Beesley August-September 2024
 */
package com.moneydance.modules.features.mousetester

import com.moneydance.apps.md.controller.FeatureModule
import com.moneydance.apps.md.controller.FeatureModuleContext
import com.moneydance.apps.md.controller.PreferencesListener
import com.moneydance.apps.md.view.gui.MoneydanceGUI

class Main : FeatureModule(), PreferencesListener {

    override fun init() {
        // if moneydance was launched with -d or the system property is set.....

        DEBUG = (com.moneydance.apps.md.controller.Main.DEBUG || java.lang.Boolean.getBoolean("moneydance.debug"))
        Util.logConsole(true, "$EXTN_ID: ** DEBUG IS ON **")

        extensionContext = this

        // the first thing we will do is register this module to be invoked via the application toolbar
        val context = context
        mdMain = context as com.moneydance.apps.md.controller.Main

        addPreferencesListener()

        // setup the home page view
        this.context!!.registerHomePageView(this, MouseTesterView())
        Util.logConsole("Initialized (Kotlin) build - $versionString ${if (PREVIEW_BUILD) "(PREVIEW) " else ""}")
    }

    override fun cleanup() {
        // I don't this this is ever called by Moneydance!?
        Util.logConsole(".cleanup() called (will pass onto .unload()....)...")
        unload()
    }

    override fun unload() {
        Util.logConsole(".unload() called....")
        removePreferencesListener()
    }

    override fun handleEvent(appEvent: String) {
        Util.logConsole(true, "MouseTester::handleEvent($appEvent) doing nothing")
        //if (eventStr.equalsIgnoreCase(AppEventManager.FILE_OPENED)) {
        //    // do stuff with dataset here....
        //}
    }

    /** Process an invocation of this module with the given URI  */
    override fun invoke(uri: String) {
        var command = uri
        val colonIdx = uri.indexOf(':')
        if (colonIdx >= 0) {
            command = uri.substring(0, colonIdx)
        }
        Util.logConsole("MouseTester::invoke($uri) - command: '$command' - doing nothing")
    }

    override fun getName(): String { return EXTN_NAME }

    private fun addPreferencesListener() {
        if (context != null) {
            (context as com.moneydance.apps.md.controller.Main).preferences.addListener(this)
        }
    }

    private fun removePreferencesListener() {
        if (context != null) {
            (context as com.moneydance.apps.md.controller.Main).preferences.removeListener(this)
        }
    }

    override fun preferencesUpdated() {
        Util.logConsole(true, "MouseTester::preferencesUpdated() called - doing nothing")
    }

    companion object {
        const val EXTN_ID: String = "mousetester"
        const val EXTN_NAME: String = "Mouse Tester"

        @JvmStatic var DEBUG: Boolean = false

        var extensionContext: Main? = null
        var PREVIEW_BUILD: Boolean = true
        var mdMain: com.moneydance.apps.md.controller.Main? = null

        val unprotectedContext: FeatureModuleContext? get() = mdMain
        val mdGUI: MoneydanceGUI get() = mdMain?.ui as MoneydanceGUI
        val versionString: String get() = "Build ${extensionContext?.build ?: "???"}"
    }
}

