/*

Class: TestingAndDebugging

 Created: 2008-07-08

Modified: 2011-11-16

 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 *
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
*/


package com.moneydance.modules.features.priceui.tools;


/**
 * A collection of miscellanous routines useful in testing and debugging.
 *
 * @author Tom Edelson
 * 
 */

public class TestingAndDebugging {
    
    
    /**
     * Returns a value suitable for use as a "debugging flag", that is, an
     * indication as to whether the user wants to run this extension
     * in "debugging mode" (thus producing extra messages).  
     * 
     * Will return true if the environment variable passed in has been set,
     *  and its value is anything but the empty string.
     *  
     * @param envVarName the name of the environment variable to be tested
     * 
     * @return true if the environment variable has a non-empty value, false
     * if it doesn't
     * 
     */
    
    public static boolean calcDebugFlag (String envVarName) {
        String envVarValue = System.getenv (envVarName);
        return ((envVarValue != null) && (envVarValue.length() != 0));
    }
    

} // end class TestingAndDebugging
