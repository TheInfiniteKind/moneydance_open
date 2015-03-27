/*
 * Class com.songlineSoftware.moneydance.access.Datastore
 * 
 *  Created: 2008-06-25
 * 
 * Modified: 2011-10-24
 * 
 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 *
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
 */

package com.moneydance.modules.features.priceui.access;

import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.Main;
import com.infinitekind.moneydance.model.*;


/**
 * An instance of this class represents a Moneydance datastore,
 * that is, the data which has been loaded from a Moneydance
 * data file.
 *
 * @author Tom Edelson
 */

public class Datastore implements CurrencyTableSource {
    
    AccountBook mdRoot = null;
    
    CurrencyTable mdCurrencies = null;
    
    CurrencyType mdBaseCurrency = null;
    
   
    /**
     * Gets the root account of this Moneydance file.  Most of the 
     * information in the file is accessed, directly or indirectly, 
     * through the root account object.
     * 
     * @return the root account
     * 
     */
    
    public AccountBook getBook() {
        return mdRoot;
    }
    
   
    /**
     * Gets the CurrencyTable object for the Moneydance datastore 
     * currently in use.  The CurrencyTable lists not only
     * the currencies, but also the securities (stocks, bonds, etc.)
     * known in this datastore, which is why the method's name uses
     * the more general term "units of value".
     * 
     * @return the currency table
     * 
     */
    
    public CurrencyTable getUnitsOfValue() {
        return mdCurrencies;
    }
    

    /**
     * Gets the "base currency" for this Moneydance file.
     * This is the unit of value used by default for expressing prices,
     * transaction amounts, etc.
     * For a United States resident, for example, this would almost always
     * be the U.S. dollar.
     * 
     * @return the Moneydance CurrencyType object representing the base currency
     * 
     */
    
    public CurrencyType getBaseCurrency() {
        return mdBaseCurrency;
    }
    

    /**
     * Initializes the instance variables for this object, each of which
     * is a reference to an object maintained by Moneydance proper.
     * 
     * Called by: method "go" of class
     * com.songlineSoftware.moneydance.priceEntry.PriceEntryExec.
     * 
     */
    
    public void init() {
        FeatureModuleContext mdContext = Main.mainObj;
        mdRoot = mdContext.getCurrentAccountBook();
        mdCurrencies = mdRoot.getCurrencies();
        mdBaseCurrency = mdCurrencies.getBaseType();
    }


} // end class Datastore
