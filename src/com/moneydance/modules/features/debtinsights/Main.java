// UPDATED BY STUART BEESLEY - StuWareSoftSystems - March 2023
// Original Author: 2001 Appgen Personal Software >> Robert Schmid
// Restricted to MD2015.8(1372) onwards

// Build: 1002 - Fix Home Screen widget popup in showBalanceTypePopup() causing...:
// 			   - NullPointerException: Cannot invoke "java.io.InputStream.markSupported()" because "<parameter1>" is null
// 			   - Fix DebtManagerWindow() crashing due to icon issues (missing and size -1 in VAQua)
// 				 Exception in thread "AWT-EventQueue-0" java.lang.IllegalArgumentException: Width (-1) and height (-1) cannot be <= 0
// 			   - Changed Summary Screen widget title, Main Window title and Extension title - to make all consistent...
//             - Enhanced with necessary methods to handle unload, re-installs, handleEvent(s) etc...; refresh home screen etc...
//             - Added setup options on the popup manager window. Now allow user to fix calculations or use dynamic balances...
//             - Added help button and guidance
//             - Added options to allow user to override MD Payment Plan to Balance rather than Current/Cleared Balance
//             - Don't allow available credit to go negative; don't allow interest to go positive....
//             - Lots more to mention... A complete overhaul....! ;->
// Build: 1001 - IK updated changed the setEscapeKeyCancels() code...; also DebtAccountView use of AcctFilter...
// Build: 1002 - Updated to use CollapsibleRefresher, and fix screen updates whilst bank downloads occurring...
//               Using subclassed JLinkLabel and override .setPreferredSize() to stop constant text width changes
//               Fixed the IK fix for AcctFilter....

// todo - Replace ProgressBarUI (etc) in BarDisplay.java - so that we can use better colors on all platforms.
// todo - The popup window hierarchy toggle icon only works on first window opening.. After this, it's dead!?

package com.moneydance.modules.features.debtinsights;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.apps.md.controller.*;
import com.moneydance.apps.md.view.gui.MainFrame;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.modules.features.debtinsights.debtmanager.DebtManagerWindow;
import com.moneydance.modules.features.debtinsights.ui.acctview.CreditCardAccountView;

import javax.swing.*;

public class Main extends FeatureModule implements PreferencesListener {

    public static final int MIN_MD_BUILD = 1372;    // Runs on MD2015.8(1372) onwards...
    public static Main THIS_EXTENSION_CONTEXT;

    public static boolean DEBUG = false;
    public static boolean PREVIEW_BUILD = false;

    public static final String EXTN_ID = "debtinsights";
    public static final String EXTN_NAME = "Debt Insights";
    public static final String EXTN_WIDGET_ID = EXTN_ID + "_creditcard";  // If you change this you will loose the home screen saved location settings...
    public static com.moneydance.apps.md.controller.Main MD_REF;
    public static final String EXTN_WIDGET_NAME_KEY = EXTN_ID + "_widgetname";
    public static final String EXTN_WIDGET_ENHANCED_COLORS_KEY = EXTN_ID + "_enhancedcolors";
    public static final String EXTN_WIDGET_DEBUG_KEY = EXTN_ID + "_debug";
    public static final String EXTN_WIDGET_FORCE_VALUES_BASE_CURRENCY_KEY = EXTN_ID + "_forcebasecurrency";
    public static final String EXTN_WIDGET_OVERRIDE_PAYMENT_PLAN_BALANCE_KEY = EXTN_ID + "_overridepaymentplanbalance";
    public static final String EXTN_WIDGET_BALANCETYPE_CHOICE_KEY = EXTN_ID + "_balancetypechoice";
    public static final int EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN = -1;
    public static final String EXTN_WIDGET_NAME_DEFAULT = EXTN_NAME + ": CCards";

    public static final String EXTN_MD_CCLIMIT_PREF_KEY = "gui.home.cc_limit_type";

    public static CreditCardAccountView widgetViewReference = null;

    public boolean allowActive = true;
    public boolean killSwitch = false;

    @SuppressWarnings("unused")
    public static final int lastRefreshTimeDelayMs = 2000;

    public static boolean lastRefreshTriggerWasAccountListener = false;


    public DebtManagerWindow debtManagerWindow = null;

    public static final String EXTN_CMD = "debtoverview";
    public static final String EXTN_OVERVIEW_TITLE = "Debt Overview";
    public static final String EXPAND_SUBS_KEY = EXTN_ID + "_gui_expand_subaccts";
    public static final String EXPAND_SUBS_POPUP_KEY = EXTN_ID + "_popup_gui_expand_subaccts";

    public static final String POPUP_GUI_HOME_CC_EXPANDED = UserPreferences.GUI_HOME_CC_EXP + "_" + EXTN_ID + "_popupwindow";

    @Override
    public void init() {

        // if moneydance was launched with -d or the system property is set.....
        Main.DEBUG = (com.moneydance.apps.md.controller.Main.DEBUG || Boolean.getBoolean("moneydance.debug"));
        Util.logConsole(true, "** DEBUG IS ON **");

        // the first thing we will do is register this module to be invoked
        // via the application toolbar
        
        boolean installDetected = false;

        THIS_EXTENSION_CONTEXT = this;

        FeatureModuleContext context = getContext();
        MD_REF = (com.moneydance.apps.md.controller.Main) context;

        if (context.getBuild() < MIN_MD_BUILD) {
            Util.logConsole("ALERT: This extension/widget is only supported on MD2015.8(1372) onwards... Quitting.....");
            return;
        }

        if (SwingUtilities.isEventDispatchThread()) {
            installDetected = true;
            Util.logConsole("Detected extension install... Performing additional install/activation routines...");
            selectHomeScreen();
            getMDMain().getUI().setStatus(EXTN_NAME + " Installing.....", 0);

            if (getPreviewBuild()) {
                Util.logConsole(String.format("*** Running PREVIEW BUILD(%s) ***", getBuild()));
            }

            Util.logConsole(String.format("CONFIG: Widget Name: '%s', Enh Colors: %s, Calculation Balance Type: %s : %s, Override MD's Payment Plan x Balance to Balance: %s, Debug: %s, Convert widget values to base currency: %s",
                    getWidgetName(),
                    getWidgetEnhancedColors(),
                    getWidgetCalculationBalanceTypeChoice(),
                    (getWidgetCalculationBalanceTypeChoice() == Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN) ? "DYNAMIC PER WIDGET COLUMN" : "FIXED as '" + getMDGUI().getResources().getBalanceType(Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()) + "'",
                    getWidgetOverridePaymentPlanBalance() ? "ON" : "OFF",
                    getDebug() ? "ON" : "OFF",
                    getWidgetForceValuesBaseCurrency() ? "ON" : "OFF"));
        }

        preferencesUpdated();
        getMDMain().getPreferences().addListener(this);

        try {
            context.registerFeature(this, EXTN_CMD, null, EXTN_NAME + " (" + EXTN_OVERVIEW_TITLE + ")");

            widgetViewReference = new CreditCardAccountView(this);
            context.registerHomePageView(this, widgetViewReference);

            Util.logConsole("Initialised... Build:" + getBuild());
            Util.logConsole("... widget name set to '" + getWidgetName());
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }

        if (installDetected){
            fireMDPreferencesUpdated();
        }

    }

    public static int getMDCCBalanceTypeSetting(){
        return getMDMain().getPreferences().getIntSetting(UserPreferences.GUI_HOME_CC_BAL, BalanceType.CURRENT_BALANCE.ordinal());
    }

    public static void setMDCCBalanceTypeSetting(int newSetting){
		getMDMain().getPreferences().setSetting(UserPreferences.GUI_HOME_CC_BAL, newSetting);
        Util.logConsole(true, String.format("MD Preference '%s' set to %s", UserPreferences.GUI_HOME_CC_BAL, newSetting));
    }

    public static String getWidgetName(){
        return getMDMain().getPreferences().getSetting(Main.EXTN_WIDGET_NAME_KEY, Main.EXTN_WIDGET_NAME_DEFAULT);}

    public static void setWidgetName(String newWidgetName){
        getMDMain().getPreferences().setSetting(Main.EXTN_WIDGET_NAME_KEY, newWidgetName);
        Util.logConsole("New Summary Screen widget name: '" + newWidgetName + "'");
    }

    public static boolean getWidgetEnhancedColors(){
        return getMDMain().getPreferences().getBoolSetting(Main.EXTN_WIDGET_ENHANCED_COLORS_KEY, false);}

    public static void setWidgetEnhancedColors(boolean newSetting){
        getMDMain().getPreferences().setSetting(Main.EXTN_WIDGET_ENHANCED_COLORS_KEY, newSetting);
        Util.logConsole("Widget enhanced colors toggled: " + (Main.getWidgetEnhancedColors() ? "ON" : "OFF"));
    }

    public static boolean getWidgetForceValuesBaseCurrency(){
        return getMDMain().getPreferences().getBoolSetting(Main.EXTN_WIDGET_FORCE_VALUES_BASE_CURRENCY_KEY, false);}

    public static void setWidgetForceValuesBaseCurrency(boolean newSetting){
        getMDMain().getPreferences().setSetting(Main.EXTN_WIDGET_FORCE_VALUES_BASE_CURRENCY_KEY, newSetting);
        Util.logConsole("Convert widget values to your base currency: " + (Main.getWidgetForceValuesBaseCurrency() ? "ON" : "OFF"));
    }

    public static CurrencyType getWidgetValueConversionCurrencyType(CurrencyType defaultCurrType){
        boolean forceBase = getWidgetForceValuesBaseCurrency();
        CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();
        return (forceBase || defaultCurrType == null) ? base : defaultCurrType;
    }

    public static boolean getDebug(){
        Main.DEBUG = getMDMain().getPreferences().getBoolSetting(Main.EXTN_WIDGET_DEBUG_KEY, Main.DEBUG);
        return Main.DEBUG;
    }

    public static boolean getPreviewBuild(){return Main.PREVIEW_BUILD; }

    public static void setDebug(boolean newSetting){
        Main.DEBUG = newSetting;
        getMDMain().getPreferences().setSetting(Main.EXTN_WIDGET_DEBUG_KEY, Main.DEBUG);
        Util.logConsole("Widget DEBUG toggled: " + (Main.getDebug() ? "ON" : "OFF"));
    }

    public static boolean getWidgetOverridePaymentPlanBalance(){
        return getMDMain().getPreferences().getBoolSetting(Main.EXTN_WIDGET_OVERRIDE_PAYMENT_PLAN_BALANCE_KEY, false);}

    public static void setWidgetOverridePaymentPlanBalance(boolean newSetting){
        getMDMain().getPreferences().setSetting(Main.EXTN_WIDGET_OVERRIDE_PAYMENT_PLAN_BALANCE_KEY, newSetting);
        Util.logConsole("Widget override MD's payment plan xBalance (to always use Balance) toggled to: " + (Main.getWidgetOverridePaymentPlanBalance() ? "ON" : "OFF"));
    }

    public static int getWidgetCalculationBalanceTypeChoice(){
        return getMDMain().getPreferences().getIntSetting(EXTN_WIDGET_BALANCETYPE_CHOICE_KEY, EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN);}

    public static BalanceType getWidgetCalculationBalanceTypeChoiceAsBalanceType() {
        int balTypeChoice = getWidgetCalculationBalanceTypeChoice();
        if (balTypeChoice == EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN) {
            balTypeChoice = getMDCCBalanceTypeSetting();
        }
        return BalanceType.fromInt(balTypeChoice);
    }

    public static void setWidgetCalculationBalanceTypeChoice(int newChoice){
        getMDMain().getPreferences().setSetting(Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY, newChoice);
        Util.logConsole(String.format("Credit calculation's Balance Type set to: %s : %s",
                getWidgetCalculationBalanceTypeChoice(),
                (getWidgetCalculationBalanceTypeChoice() == Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN) ? "DYNAMIC PER WIDGET COLUMN" : "FIXED as '" + getMDGUI().getResources().getBalanceType(Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()) + "'"));

    }

    public void preferencesUpdated(){
        Util.logConsole(true, "Inside .preferencesUpdated() ...");
    }

    public void fireMDPreferencesUpdated() {
        Util.logConsole(true, "Triggering an update to the Summary/Home Page View");
        getMDMain().getPreferences().firePreferencesUpdated();
    }

    @Override
    public void cleanup() {
        // I don't this this is ever called by Moneydance!?
        Util.logConsole(true, ".cleanup() called....");
        closeConsole();
        widgetViewReference = null;
    }

    @Override
    public void unload() {
        Util.logConsole(true, ".unload() called.... Unloading and activating killSwitch...");
        killSwitch = true;
        closeConsole();
        widgetViewReference = null;
        getMDMain().getPreferences().removeListener(this);
        getMDMain().getUI().setStatus(EXTN_NAME + " unloaded...", 0);
    }

    /**
     * Process an invocation of this module with the given URI
     */
    @Override
    public void invoke(String uri) {
        String command = uri;
        int theIdx = uri.indexOf('?');
        if (theIdx >= 0) {
            command = uri.substring(0, theIdx);
        } else {
            theIdx = uri.indexOf(':');
            if (theIdx >= 0) {
                command = uri.substring(0, theIdx);
            }
        }

        if (command.equals(EXTN_CMD)) {
            creditCardReport();
        } else {
            Util.logConsole(true, "** did not process command: '" + command + "'");
        }
    }

    @Override
    public String getName() {
        return EXTN_NAME;
    }

    @SuppressWarnings("unused")
    public synchronized void creditCardReportRefresh() {
        if (this.debtManagerWindow != null) {
            Util.logConsole(true, "Inside: creditCardReportRefresh() - calling DMW.refresh()");
            this.debtManagerWindow.refresh();
        }
    }

    public synchronized void creditCardReportDispose() {
        if (this.debtManagerWindow != null) {
            Util.logConsole(true, "(indirectly called via Home Screen Popup Balance Change...) About to Frame dispose()...");
            this.debtManagerWindow.dispose();
            this.debtManagerWindow = null;
        }
    }

    private synchronized void creditCardReport() {
        if (debtManagerWindow == null) {
            Util.logConsole(true, "About to launch new frame...");
            debtManagerWindow = new DebtManagerWindow(getMDGUI(), this);
            Util.logConsole(true, "Created new frame...");
        }
        if (this.debtManagerWindow.refresh()) {
            Util.logConsole(true, "Frame inside .refresh()...");
            this.debtManagerWindow.pack();
            this.debtManagerWindow.toFront();
            this.debtManagerWindow.requestFocus();
            debtManagerWindow.setVisible(true);
            Util.logConsole(true, "AFTER .refresh()...");
        } else {
            Util.logConsole(true, "About to Frame dispose()...");
            this.debtManagerWindow.dispose();
            this.debtManagerWindow = null;
            Util.logConsole(true, "AFTER Frame dispose()...");
        }
    }

    synchronized void closeConsole() {
        Util.logConsole(true, "closeConsole() called...");
        if (debtManagerWindow != null) {
            debtManagerWindow.goAway();
            Util.logConsole(true, "... after .goAway()...");
            debtManagerWindow = null;
        }
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

    @Override
    public void handleEvent(String appEvent) {
        Util.logConsole(true, "handleEvent() - Event '" + appEvent + "'");

        if (killSwitch){
            Util.logConsole(true, ".... ignoring as killSwitch set....");
            widgetViewReference = null;
            return;
        }

        switch (appEvent) {
            case "md:file:closing":
            case "md:file:closed":
            case "md:app:exiting":
                allowActive = false;
                break;
            case "md:file:opened":
                allowActive = true;
                break;
            default:
                Util.logConsole(true, ".... ignoring: '" + appEvent + "'");
        }
        //            "md:file:opening";
        //            "md:file:presave"
        //            "md:file:postsave"
        //            "md:account:select"
        //            "md:account:root"
        //            "md:graphreport"
        //            "md:viewbudget"
        //            "md:viewreminders"
        //            "md:licenseupdated"
    }

    public void selectHomeScreen() {
        try {
            MainFrame fmf = getMDGUI().getFirstMainFrame();
            if (fmf == null) {return;}
            Account currentViewAccount = fmf.getSelectedAccount();
            if (currentViewAccount != getMDMain().getRootAccount()) {
                Util.logConsole(true, "Switched to Home Page Summary Page (from: " + currentViewAccount + ")");
                getMDGUI().getFirstMainFrame().selectAccount(getMDMain().getRootAccount());
            }
            } catch(Exception e){
                Util.logConsole("@@ Error switching to Summary Page (Home Page) - ignoring and continuing...");
                e.printStackTrace(System.err);
            }
        }
}