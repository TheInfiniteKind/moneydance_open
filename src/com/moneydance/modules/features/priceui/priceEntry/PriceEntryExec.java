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

import com.infinitekind.moneydance.model.*;

import com.infinitekind.util.CustomDateFormat;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.modules.features.priceui.Main;

import com.moneydance.modules.features.priceui.access.CurrencyTableSource;
import com.moneydance.modules.features.priceui.access.Datastore;
import com.moneydance.modules.features.priceui.utils.MoneyFormatter;

import java.util.*;


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
    
    private CurrencyType[] allSecurities;
    
    private CurrencyType baseCurrency;
    
    private boolean debugFlag;
    
    private MoneyFormatter formatter;
    
    private int numberOfSecurities;
    
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
        formatter = null;
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
        
        CurrencyTable valueTypeList = mdData.getUnitsOfValue();
   
        baseCurrency = valueTypeList.getBaseType();
        formatter = new MoneyFormatter(baseCurrency);
       
        tableModel = new PriceTableModel();
        initializeData (valueTypeList);
        
        initializeWindow();
        
    } // end method go
    
    
    /*
     * Routines used during initialization
     * (called, directly or indirectly, from "go":
     * 
     */
    
  
    /*
     * initializeData
     * 
     * Gets list of securities (stocks, bonds, mutual funds, etc.) known in this
     * Moneydance store.
     * 
     * Gets the names of those securities into the PriceTableModel object,
     * from whence they are displayed.
     * 
     * Then calls initializePrices, which will do the same for the current
     * prices of those securities.  ("Current" prices, here, means those most
     * recently recorded as such in the Moneydance data store.)
     * 
     */
    
    private void initializeData 
            (CurrencyTable allUnits) {
    
        tableModel.init();
        
        List<CurrencyType> allTypes = allUnits.getAllCurrencies();
        List<CurrencyType> securitiesOnly = new LinkedList<CurrencyType>();
        for (CurrencyType unit: allTypes) {
            if (unit.getCurrencyType() == CurrencyType.Type.SECURITY) {
                securitiesOnly.add(unit);
            }
        } // end for
        Collections.sort(securitiesOnly, new Comparator<CurrencyType>() {
            @Override
            public int compare(CurrencyType o1, CurrencyType o2) {
                return o1.getName().compareTo(o2.getName());
            }
        });
        numberOfSecurities = securitiesOnly.size();
        tableModel.allocate(numberOfSecurities);
  
        allSecurities = new CurrencyType [numberOfSecurities];
        for (int index = 0; index < numberOfSecurities; index++) {
            allSecurities [index] = securitiesOnly.get(index);
        }
       
        String [] securityNames = new String [numberOfSecurities];
        for (int index = 0; index < numberOfSecurities; index++) {
             securityNames[index] = allSecurities[index].getName();
        }
        tableModel.populateNames (securityNames);
        
        initializePrices();
    
    } // end method initializeData
    
    
    /* 
     * initializePrices
     *
     * This is a separate method because, unlike the other things done in
     * initializeData, these may need to be done again.  Namely, after
     * the user has entered new prices and applied them to the data store,
     * we want those new prices to be shown in the "current price" column
     * of our window.
     * 
     */
    
    private void initializePrices() {
        String [] currentPrices = new String [numberOfSecurities];
        for (int index = 0; index < numberOfSecurities; index++) {
            CurrencyType sec = allSecurities[index];
            double price = 1 / sec.getUserRate();
            currentPrices[index] = formatter.formatDouble(price);
        } // end for
        tableModel.populatePrices (currentPrices);
    } // end method initializePrices
   
    
    /*
     * initializeWindow
     * 
     * This gets our "Security Prices" window created and displayed.
     * 
     */
    
    private void initializeWindow() {
        screen = new PriceEntryScreen (tableModel, this);
        java.awt.EventQueue.invokeLater (new Runnable() {
          public void run() {
             screen.setVisible(true);
          }
        });
    } // end method initializeWindow
    
    
    /* -------------------------------------------------------------------------
     * 
     * Methods called in response to GUI events (i.e. called, directly or
     * indirectly, feom PriceEntryScreen):
     * 
     */
    
    
    /*
     * applyPrices
     * 
     * Called by: applyButtonActionPerformed, in PriceEntryScreen
     * 
     */
    
    /**
     * Takes the prices (and other information) entered by the user, and 
     * applies them to (enters them into) the Moneydance data store.
     * 
     */
    
    public void applyPrices() {
        
        int effectiveDate = screen.getAsOfDate();
        
        boolean makeCurrentFlag = screen.getMakeCurrentFlag();
        
        Double [] newPrices = tableModel.getNewPrices();
        
        if (debugFlag) {
            dumpData (effectiveDate, makeCurrentFlag, newPrices);
        }
        
        int count = 0; // How many new prices were entered?
        
        for (int index = 0; index < numberOfSecurities; index++) {
            Double price = newPrices [index];
            if (price != null && price.doubleValue()!=0) {
                applyPrice (price, index, effectiveDate, makeCurrentFlag);
                count++;
            }
        }
        
        /*
         * If any new prices were entered, and we marked them as "current",
         * then refresh the "Current price" column on the screen.  And if new
         * prices were entered, we want to clear them now from the "New price"
         * column of the form, whether they were designated "current" or not.
         * 
         */
        
        if (count > 0) {
            tableModel.clearNewPrices();
            if (makeCurrentFlag) {
                initializePrices();
            }
            tableModel.refreshView();
        }

    } // end method applyPrices

    
    private void applyPrice 
            (double price, int securityIndex, 
             int asOfDate, boolean makeCurrent) {
        CurrencyType security = allSecurities [securityIndex];
        double rate = 1 / Util.safeRate(price);
        security.setSnapshotInt (asOfDate, rate).syncItem();
        if (makeCurrent) {
            security.setUserRate(rate);
            security.syncItem();
        }
    }
    
    
    // Used only for debugging:
    
    private void dumpData (Integer effDate, boolean makeCurrFlag,
            Double [] prices) {

        if (effDate == null) {
            System.out.print("\nEffective date not set yet.\n\n");
        } else {
            System.out.print("Effective date: " + effDate.toString() + "\n\n");
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
    
    
} // end class PriceEntryExec
