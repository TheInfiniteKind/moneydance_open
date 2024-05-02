/*
 * Class: Main
 *
 * Created: 2008-07-16
 * Modified: 2011-10-24
 * Updated: May 2024 - Stuart Beesley - allow price edits to auto move down to next row for quick entry
 *
 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 *
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software (www.songline-software.com).
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 */


package com.moneydance.modules.features.priceui;


import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.infinitekind.moneydance.model.*;

import com.moneydance.modules.features.priceui.access.CurrencyTableSource;
import com.moneydance.modules.features.priceui.priceEntry.PriceEntryExec;
import com.moneydance.modules.features.priceui.utils.IconSource;
import com.moneydance.modules.features.priceui.tools.TestingAndDebugging;

import java.awt.Image;


/**
 * This class provides the interface between Moneydance itself, and the other
 * classes which implement the functionality of "security price entry", allowing
 * the latter to be run as a Moneydance extension.
 * <p>
 * The "init" method in this class is the entry point to the extension, since
 * it is the first code in the extension to be called by Moneydance.  This
 * happens while Moneydance itself is starting up, assuming that the extension
 * has previously been "installed" into this copy of Moneydance.
 *
 * @author Tom Edelson
 */

public class Main extends FeatureModule
        implements CurrencyTableSource {


    private static boolean debugFlag = (com.moneydance.apps.md.controller.Main.DEBUG || Boolean.getBoolean("moneydance.debug"));

    private FeatureModuleContext context;

    private PriceEntryExec executor;

    private final String iconPath = "/com/moneydance/modules/features/priceui/dollar.gif";


    /**
     * Called by Moneydance when a data set is closed.
     * Delegates to the "executor" object, which was created when our "init"
     * method was called.
     */
    @Override
    public void cleanup() {
        executor.cleanup();
        executor = null;
    }

    @Override
    public void unload() {
        cleanup();
    }


    /**
     * Allows methods in other classes to determine whether the extension
     * is running in "debug mode"
     *
     * @return a boolean which is true if the "debug mode" has been turned on
     */
    public static boolean getDebugFlag() {
        return debugFlag;
    }


    /**
     * Called by Moneydance when it wants a string that it can display
     * in order to identify this extension to the user
     *
     * @return a constant String which contains the name of this extension
     */
    public String getName() {
        return "Security Price Entry";
    }

    /**
     * Provides access to the Moneydance currency table
     * to other classes within the extension
     *
     * @return the CurrencyTable for the currently open data set
     */
    public CurrencyTable getUnitsOfValue() {
        AccountBook book = context.getCurrentAccountBook();
        return book.getCurrencies();
    }

    /**
     * Called by Moneydance during application startup.  All other methods
     * in this class require that this one have been called first.
     */
    @Override
    public void init() {
        debugFlag = TestingAndDebugging.calcDebugFlag("PriceEntryDebug");
        if (debugFlag)
            System.out.print("\nEntered init method for Security Price Entry.\n\n");
        context = getContext();
        String actionName = "priceEntry";
        IconSource imageMaker = new IconSource();
        Image icon = imageMaker.getIcon(iconPath);
        String name = getName();
        context.registerFeature(this, actionName, icon, name);
    }


    /**
     * Called by Moneydance when the user directs the application
     * to activate this extension.  For example, the user might have selected it
     * from the Extensions menu.
     *
     * @param uri not used in this extension
     */
    public void invoke(String uri) {
        executor = new PriceEntryExec(this);
        executor.go();
    }


} // end class Main
