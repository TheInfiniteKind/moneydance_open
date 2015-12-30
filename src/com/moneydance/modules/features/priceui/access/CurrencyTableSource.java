/*
 * CurrencyTableSource.java
 * 
 *  Created 2008-07-14
 * 
 * Modified 2011-10-24
 * 
 * This interface is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
 */

package com.moneydance.modules.features.priceui.access;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.CustomDateFormat;

/**
 * A class which implements this interface provides a way to get the 
 * CurrencyTable object for a Moneydance datastore.
 *
 * @author Tom Edelson
 * 
 */

public interface CurrencyTableSource {
    
    
    /**
     * Gets the CurrencyTable object for the Moneydance datastore 
     * (Moneydance file) currently in use.  The CurrencyTable lists not only
     * the currencies, but also the securities (stocks, bonds, etc.)
     * known in this datastore, which is why the method's name uses
     * the more general term "units of value".
     * 
     * @return the currency table
     * 
     */
    
    public CurrencyTable getUnitsOfValue ();

} // end interface CurrencyTableSource
