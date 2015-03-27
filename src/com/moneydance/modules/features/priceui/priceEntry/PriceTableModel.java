/*

Class: PriceTableModel

 Created: 2008-06-27

Modified: 2011-11-14
 
 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 * 
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 * 
*/


package com.moneydance.modules.features.priceui.priceEntry;

import javax.swing.table.AbstractTableModel;


/**
 * Defines the "table model" from which the JTable in PriceEntryScreen
 * will get its data.
 *
 * @author Tom Edelson
 * 
 */

public class PriceTableModel extends AbstractTableModel {
    
/*
 * This is not "model" code in the MVC sense; it's really part of the view.
 * It's a model of what will be displayed on the screen, not of the underlying
 * data.  Note that this class knows nothing about the particular application
 * whose data are being displayed (and updated).
 * 
 */
    
    private Class [] colClasses = new Class [columnCount];
    
    static final int columnCount = 3;
    
    static final int currentPriceColumn = 1;
    
    private Object [] [] data;
    
    private String [] headings = {"Security", "Current Price", "New Price"};
    
    static final int nameColumn = 0;
    
    static final int newPriceColumn = 2;
    
    private int rowCount;
  
    
    /**
     * Initializes information about the data types to be displayed in the
     * table, by column number.
     * 
     * Must be called before this table model is bound to its 
     * corresponding JTable.
     * 
     * Called by: method initializeData of class PriceEntryExec.
     * 
        */
   
    public void init() {
        
        /*
         * Things we can do before we have any information from the data source:
         * namely, initialize the classes for the columns in our table.
         * 
         */
        
        Class stringClass = new String().getClass();
        Class doubleClass = new Double(0).getClass();
        colClasses[nameColumn] = stringClass;
        colClasses[currentPriceColumn] = stringClass;
        colClasses[newPriceColumn] = doubleClass;
        
    } // end method init
   
    
    /**
     * Initializes information about the number of rows in the table ...
     * and then, given that and the number of columns (supplied when "init"
     * was called), initializes the table itself.
     * 
     * Must be called before "populateNames" or "populatePrices".
     * 
     * Call this when you know how many securities are in the data source,
     * and thus, how many rows there will be in the table.
     * 
     * @param numberOfRows the number of distinct securities in the data store ...
     * and thus, the number of rows in our table.
     * 
     */

    void allocate (int numberOfRows) {
        rowCount = numberOfRows;
        data = new Object [rowCount] [columnCount];
    }
    
    
    /* dumpData: used for debugging only
     * Not currently used at all.
     */
    
    void dumpData() {
        System.out.println();
        for (Object [] row: data) {
            String name = (String) row [nameColumn];
            System.out.println(name);
            String currPrice = (String) row [currentPriceColumn];
            System.out.print ("  " + currPrice + "\n\n");
            }
    }

   
    /** 
     * 
     * @return the number of rows in the table
     * 
     */
    
    public int getRowCount() {
        return rowCount;
    }

    
    /** 
     * 
     * @return the number of columns in the table
     * 
     */
    
    public int getColumnCount() {
        return columnCount;
    }
    

    /**
     * 
     * @param column the table column for which the caller wants to know the
     * heading
     * 
     * @return the column heading to be displayed for the column
     * 
     */
    
    @Override
    
    public String getColumnName (int column) {
        return headings [column];
    }
    
    
    /**
     * 
     * @param column the table column for which the caller wants to know the 
     * class
     * 
     * @return the class of the objects stored in this column of the table
     * 
     */
    
    @Override
    
    public Class getColumnClass (int column) {
        return colClasses [column];
    }

    
    /*
     * Get all the price data entered by the user in the "New Price" column
     * (since the last time the "Apply" button was pressed).
     * 
     * Called by: method applyPrices of class PriceEntryExec
     * 
     * @return an array containing all the numbers that have been entered
     * by the user into the "New Price" column, with nulls for rows where no
     * value has been entered.
     * 
     */
    
    Double [] getNewPrices() {
        Double [] result = new Double [rowCount];
        for (int index = 0; index < rowCount; index++) {
            Object dataPoint = data [index] [newPriceColumn];
            if (dataPoint == null)
                result [index] = null;
            else
                result [index] = (Double) dataPoint;
        }
        return result;
    }
    

    /**
     * Get the data represented in any one cell of the table, given the 
     * row number and column number.  Used only by Swing.
     * 
     * @param row the row number of the desired cell
     * 
     * @param column the column number of the desired cell
     * 
     * @return the data from the specified cell.  It is returned as an Object,
     * but one should be able to cast it to the type (the Class) returned by the
     * "getColumnClass" method for the specified column number.
     * 
     */
    
    public Object getValueAt(int row, int column) {
        return data [row] [column];
    }
    
    
    /*
     * Clear (erase from the display) any data previously entered by the user
     * in the "New Price" column of the table.
     * 
     * Called by: method applyPrices of class PriceEntryExec
     * 
     */
    
    void clearNewPrices() {
        for (int index = 0; index < rowCount; index++) {
            data [index] [newPriceColumn] = null;
            // fireTableCellUpdated (index, newPriceColumn);
        }
    }
    
    
    /**
     * Used by JTable to determine whether a given table cell
     * should be made editable or not.
     * 
     * Returns "true" if and only if the cell in question is
     * in the "New Price" column.
     * 
     * @param row row number of cell for which information is desired.
     * 
     * @param column column number of cell for which information is desired.
     * 
     * @return true if the cell should be editable, false if not.
     * 
     */
    
    @Override
    
    public boolean isCellEditable (int row, int column) {
        return (column == newPriceColumn);
    }
    
    
    /*
     * Called by method initializeData of class PriceEntryExec, 
     * to put the security names where the PriceEntryScreen
     * will be able to find them.
     * 
     * @param names String array containing the names of all of the securities
     * which are to be displayed.
     * 
     */
    
    void populateNames(String [] names) {
        for (int index = 0; index < rowCount; index++) {
            data [index] [nameColumn] = names [index];
        }
    }
    
    
    /*
     * Puts the "current" security prices where the PriceEntryScreen
     * will be able to find them.
     * 
     * Called during initialization, and may be called again, after the user
     * has entered new prices, which should (if the user so chose)
     * now be displayed as "current".  In other words, a price displayed in the
     * "Current Price" column may be either [1] a value read from the Moneydance
     * data store, when this window was initialized; or [2] a value previously
     * entered by the user in the "New Price" column, if [a] the "Apply"
     * button has been pressed since that price was entered and [b] the user has
     * indicated that the prices he enters should be considered the 
     * "current" prices.
     * 
     * Called by: method initializePrices of class PriceEntryExec.
     *
     * @param prices String array containing (formatted) "current" prices 
     * for the securities.
     * 
     */
    
    void populatePrices(String [] prices) {
        for (int index = 0; index < rowCount; index++) {
            data [index] [currentPriceColumn] = prices [index];
            }
    }
    
    
    /*
     * Let Swing know that the data in the table model has changed,
     * so that it will redraw that data on the screen.
     * 
     * Called by: method "applyPrices()" of class PriceEntryExec.
     * 
     */
    
    void refreshView() {
        fireTableDataChanged();
    }
    
    
    /**
     * Called by JTable when a table cell has been edited, to let this
     * "table model" object know the new value, so that it may store that value.
     * 
     * @param value the value to be stored
     * 
     * @param row the row in the table whose value this is
     * 
     * @param col the column in the table whose value this is
     * 
     */
    
    @Override
    
    public void setValueAt (Object value, int row, int col) {
        if (col == newPriceColumn) {
            data [row] [col] = value;
            fireTableCellUpdated (row, col);
        }
        else {
            throw new ArrayIndexOutOfBoundsException
                    ("Trying to update wrong column in PriceTableModel\n");
        }
    } // end method setValueAt
    

} // end class PriceTableModel
