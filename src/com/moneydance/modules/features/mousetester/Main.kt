/**
 * MouseTester: Simple java extension to test mouse clicks
 * @author Stuart Beesley August 2024
 */
package com.moneydance.modules.features.mousetester;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.PreferencesListener;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import static com.moneydance.modules.features.mousetester.Util.logConsole;

public class Main extends FeatureModule implements PreferencesListener{

    public static Main THIS_EXTENSION_CONTEXT;

    public static boolean DEBUG = false;
    public static boolean PREVIEW_BUILD = true;
    public static com.moneydance.apps.md.controller.Main MD_REF;

    public static final String EXTN_ID = "mousetester";
    public static final String EXTN_NAME = "Mouse Tester";

    public Main() {}

    public void init() {

        // if moneydance was launched with -d or the system property is set.....
        Main.DEBUG = (com.moneydance.apps.md.controller.Main.DEBUG || Boolean.getBoolean("moneydance.debug"));
        logConsole(true, Main.EXTN_ID + ": " + "** DEBUG IS ON **");

        THIS_EXTENSION_CONTEXT = this;

        // the first thing we will do is register this module to be invoked via the application toolbar
        FeatureModuleContext context = getContext();
        MD_REF = (com.moneydance.apps.md.controller.Main) context;

        addPreferencesListener();

        // setup the home page view
        assert getContext() != null;
        getContext().registerHomePageView(this, new MouseTesterView());
        logConsole(String.format("Initialized build %s %s", getVersionString(), (PREVIEW_BUILD ? "(PREVIEW) " : "")));
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
        logConsole(".cleanup() called (will pass onto .unload()....)...");
        unload();
    }

    @Override
    public void unload() {
        logConsole(".unload() called....");
        removePreferencesListener();
    }

    public static String getVersionString() {
        return "Build " + getExtensionContext().getBuild();
    }

    @Override
    public void handleEvent(String eventStr) {
        logConsole(true, "MouseTester::handleEvent(" + eventStr + ") doing nothing");
        //if (eventStr.equalsIgnoreCase(AppEventManager.FILE_OPENED)) {
        //    // do stuff with dataset here....
        //}
    }

    /** Process an invocation of this module with the given URI */
    public void invoke(String uri) {
        String command = uri;
        int colonIdx = uri.indexOf(':');
        if (colonIdx >= 0) {
            command = uri.substring(0, colonIdx);
        }
        logConsole("MouseTester::invoke(" + uri + ") - command: '"+ command + "' - doing nothing");
    }

    public String getName() {
        return EXTN_NAME;
    }

    private void addPreferencesListener() {
        if (getContext() != null) {
            ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences()
                    .addListener(this);
        }
    }

    private void removePreferencesListener() {
        if (getContext() != null) {
            ((com.moneydance.apps.md.controller.Main) getContext()).getPreferences()
                    .removeListener(this);
        }
    }

    @Override
    public void preferencesUpdated() {
        logConsole(true, "MouseTester::preferencesUpdated() called - doing nothing");
    }
}

