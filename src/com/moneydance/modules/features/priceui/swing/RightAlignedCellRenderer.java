/*

Class: RightAlignedCellRenderer

 Created: 2008-07-04

Modified: 2011-11-14

 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
*/


package com.moneydance.modules.features.priceui.swing;

import javax.swing.SwingConstants;
import javax.swing.table.DefaultTableCellRenderer;


/**
 * This is a renderer for table cells which contain Strings, but are to be
 * displayed right-aligned ... for example, if they contain 
 * [formatted versions of] numeric values.
 * 
 * The only code we need to override is the default constructor.
 *
 * @author Tom Edelson
 * 
 */

public class RightAlignedCellRenderer extends DefaultTableCellRenderer {
    
    
    public RightAlignedCellRenderer() {
        
        super();
        
        setHorizontalAlignment (SwingConstants.RIGHT);
        
        /*
           ... Method "setHorizontalAlignment" is defined in JLabel
           (which is an ancestor of DefaultTableCellRenderer,
           and therefore also an ancestor of this class).
         */
        
    } // end constructor
    
    
} // end class RightAlignedCellRenderer
