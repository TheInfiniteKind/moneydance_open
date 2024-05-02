/*

Class: PriceEntryExec

 Created: 2008-06-27

Modified: 2011-11-11
 
 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 *
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
*/

package com.moneydance.modules.features.priceui.priceEntry;

import com.moneydance.modules.features.priceui.Main;

import com.moneydance.modules.features.priceui.access.CurrencyTableSource;
import com.moneydance.modules.features.priceui.access.Datastore;

/**
 * This is the "unofficial main" class of the "security prices data entry" 
 * extension for Moneydance.  Methods in this class construct and display
 * the extension's data entry window, and "apply" any changed prices
 * (copy them back into the Moneydance data store).
 *
 * @author Tom Edelson
 * 
 */

public class PriceEntryExec {
    
/*
 * This class contains most of the "model" code 
 * (in the sense of Model-View-Controller)
 * for the app, and (I think) most of the 
 * "controller" code as well.
 * 
 * Note that the PriceTableModel class knows nothing about Moneydance,
 * and should be able to be used with another personal finance package.
 * The same should be true of the PriceEntryScreen class.
 * 
 * However, if one actually wanted to use PriceEntryScreen 
 * and PriceTableModel with a different personal finance program,
 * then further decoupling would be called for.  Those classes should
 * then be moved into a different package.
 * 
 * And PriceEntryScreen shouldn't even know that the "responder" object,
 * to which it delegates responding to significant GUI events,
 * is an instance of this class; it should know it only as implementing
 * an interface, which should live in the same package where it does:
 * "PriceEntryResponder"?
 * 
 * The "main" method of this class, the one which gets everything
 * going, is, um, "go".  It, and the private "initialize*" methods (which it 
 * calls, directly or indirectly) cause the necessary model data to be 
 * fetched from Moneydance, and then cause the "Security Prices" window to be
 * initialized and displayed.
 * 
 * The various "action routines" in the window class, PriceEntryScreen,
 * delegate to methods in this class:
 * 
 * - closeWindow()
 * 
 * - applyPrices()
 * 
 */
    
    private CurrencyTableSource mdData;
    private boolean debugFlag;
    private PriceEntryScreen screen;
    private PriceTableModel tableModel;
    
    
    public PriceEntryExec() {
        // Nothing to do.
    }
    
    
    public PriceEntryExec (CurrencyTableSource cts) {
        mdData = cts;
    }
    
    
     /**
      * Called by the "cleanup" method of the "offical main" class
      * 
      *     (com.moneydance.modules.features.priceui.Main)
      * 
      * -- and thus, indirectly, by Moneydance itself -- 
      * when a data store is closed.
      * 
      */
    
    public void cleanup() {
        screen.setVisible(false);
        screen.dispose();
        screen = null;
        mdData = null;
        tableModel = null;
    } // end method cleanup

    
    /**
     * This does our initialization, up to and including displaying the
     * "Security Price Data Entry" window.
     * 
     */
   
    public void go() {
        
        debugFlag = Main.getDebugFlag();
   
        if (mdData == null) {
            Datastore md = new Datastore();
            md.init();
            mdData = md;
        }
        
        tableModel = new PriceTableModel(mdData.getUnitsOfValue());
        
        initializeWindow();
        
    } // end method go
    
    
    /*
     * Routines used during initialization
     * (called, directly or indirectly, from "go":
     * 
     */
    
  
    /*
     * initializeWindow
     * 
     * This gets our "Security Prices" window created and displayed.
     * 
     */
    
    private void initializeWindow() {
        screen = new PriceEntryScreen (tableModel, this);
        java.awt.EventQueue.invokeLater (() -> screen.setVisible(true));
    } // end method initializeWindow
    
    
    /* -------------------------------------------------------------------------
     * 
     * Methods called in response to GUI events (i.e. called, directly or
     * indirectly, from PriceEntryScreen):
     * 
     */
    
    
    // Used only for debugging:
    
    private void dumpData (Integer effDate, boolean makeCurrFlag,
            Double [] prices) {

        if (effDate == null) {
            System.out.print("\nEffective date not set yet.\n\n");
        } else {
            System.out.print("Effective date: " + effDate + "\n\n");
        }

        System.out.print("\"Make current\" box is " 
                + (makeCurrFlag ? "" : "not ") + "selected\n\n");
        
        int howmany = prices.length;
        
        for (Double price: prices) {
            if (price != null) {
                System.out.println (price);
            }
        }
        
        System.out.println();

    } // end method dumpData


  /**
   * Takes the prices (and other information) entered by the user, and 
   * applies them to (enters them into) the Moneydance data store.
   */
  public void applyPrices() {
    tableModel.applyPrices(screen.getAsOfDate(), screen.getMakeCurrentFlag());

  }
  
} // end class PriceEntryExec
