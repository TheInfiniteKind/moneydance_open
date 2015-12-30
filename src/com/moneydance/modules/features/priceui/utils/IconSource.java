/*

Class: IconSource

 Created: 2008-07-16

Modified: 2011-10-27
 
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

import com.moneydance.modules.features.priceui.Main;

import java.awt.Image;
import java.awt.Toolkit;

/**
 * This class provides a method for obtaining a java.awt.Image which will be
 * used as an "icon" to identify this extension.
 *
 * @author Tom Edelson
 * 
 */

public class IconSource {

    /**
     * Reads a file representing the image which will serve as the "icon"
     * for this extension, and returns the image
     * 
     * @param iconPath the path to the file in which the icon is stored
     * @return the icon
     * 
     */
    
    public Image getIcon (String iconPath) {
        
        boolean debugFlag = Main.getDebugFlag();

        ClassLoader loader = getClass().getClassLoader();
        java.io.InputStream input = loader.getResourceAsStream (iconPath);

        if (input == null) {
            System.out.print ("Could not open icon file.\n\n");
            return null;
        }
        
        if (debugFlag)
          System.out.print ("Icon file successfully opened.\n\n");

        java.io.ByteArrayOutputStream output =
                new java.io.ByteArrayOutputStream (1000);
        byte[] buffer = new byte [256];
        int count;

        try {
            while ((count = input.read (buffer, 0, buffer.length)) >= 0) {
                output.write (buffer, 0, count);
            }
        } catch (java.io.IOException excep) {
            return null;
        }

        Toolkit maker = Toolkit.getDefaultToolkit();
        Image theIcon = maker.createImage (output.toByteArray());
        return theIcon;

    } // end method getIcon
    
} // end class IconSource
