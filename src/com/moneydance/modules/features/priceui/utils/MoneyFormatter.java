/*

Class: MoneyFormatter

 Created: 2008-07-02

Modified: 2011-11-09
  
 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 *
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
*/

package com.moneydance.modules.features.priceui.utils;

import com.infinitekind.moneydance.model.*;

/**
 * This class provides a method (formatDouble) for converting a Java double --
 * representing a security price -- to a String.
 *
 * @author Tom Edelson
 */

public class MoneyFormatter {
    
    private CurrencyType baseCurrency;
    
    private int multiplier;
    

    /**
     * @param base the "base currency" for this Moneydance data store,
     * in which security prices are to be expressed.
     * 
     */
    
    public MoneyFormatter (CurrencyType base) {
        baseCurrency = base;
        int places = baseCurrency.getDecimalPlaces();
        multiplier = intPower (10, places);
    }
    
    
    /**
     * Returns a prettier String version of a security price.
     * 
     * @param price the security's price (as a floating-point number).
     * 
     * @return a String representing this price.  Courtesy of Moneydance, this
     * will even include a currency symbol (at least for the best-known
     * currencies, such as the U.S. dollar).  Also commas, if the value
     * is big enough.
     * 
     */

    public String formatDouble (double price) {
        long scaledPrice = Math.round (price * multiplier);
        return baseCurrency.formatFancy (scaledPrice, '.');
    }
    

    private int intPower (int base, int power) {
        int result = 1;
        for (int count=0; count < power; count++) {
            result = result * base;
        }
        return result;
    }
    

} // end class MoneyFormatter
