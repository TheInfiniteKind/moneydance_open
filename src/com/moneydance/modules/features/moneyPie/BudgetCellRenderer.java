/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import javax.swing.*;
import javax.swing.table.*;

import java.awt.*;
import java.util.Calendar;

import com.infinitekind.moneydance.model.*;


public class BudgetCellRenderer extends DefaultTableCellRenderer {
  private static final long serialVersionUID = 1L;
  private Font       boldFont;
  private Font       plainFont;
  private BudgetData data;
  private boolean    inverseColor    = false;

  BudgetCellRenderer(BudgetData data) {
	    this.data = data;

	    plainFont = getFont().deriveFont(Font.PLAIN);
	    boldFont = plainFont.deriveFont(Font.BOLD);
	    setHorizontalAlignment(LEFT);
  }

  BudgetCellRenderer(BudgetData data, boolean inverseColor) {
	  this(data);
	  this.inverseColor = inverseColor;
  }
  
  public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
	Color redColor     = new Color(250, 60, 60);
	Color lredColor    = new Color(250, 160, 160);
	Color orangeColor  = new Color(250, 160, 0);
	//Color greenColor   = new Color(60, 250, 60);
	Color lgreenColor  = new Color(160, 250, 160);
	Color blueColor    = new Color(60, 60, 250);
	Color lblueColor   = new Color(160, 160, 250);
	Color blackColor   = new Color(0, 0, 0);
	Color greyColor    = new Color(200, 200, 200);
	Color yellowColor  = new Color(250, 250, 0);
	Color lyellowColor = new Color(250, 250, 160);
	Color whiteColor   = Color.WHITE;
	
	if (value instanceof String) {
		if( ((String)value).indexOf(".") > 0 || ((String)value).indexOf(",") > 0 ){
			value = new BudgetValue(data, (String) value);
		}
	}

	boolean isNegative = false;
    if (value instanceof BudgetValue) {
      if (((BudgetValue) value).isNegative() && column >= 0) {
    	  isNegative = true;
    	  setForeground(redColor);
      } else {
        setForeground(blackColor);
      }
    }
    
    if (isSelected) {
      setFont(boldFont);
      setBackground(yellowColor);
    } else {
      setFont(plainFont);
      setBackground(whiteColor);
    }

    if (column >= 1) setHorizontalAlignment(RIGHT);
    else             setHorizontalAlignment(LEFT);

    if(row == table.getRowCount() - 1) setFont(boldFont);
    if(column == table.getColumnCount() - 1) setFont(boldFont);

    

    String acctName = (String) table.getModel().getValueAt(row, 0);
    
    if (column >= 1) {
    	if (value instanceof BudgetValue) {
        	setText( ((BudgetValue) value).toString() );
        } else {
        	setText((String) value);
        }
    } else {
    	setText(acctName);
    }

    this.setBorder(null);
    if(table.isCellEditable(row, column)){
    	double      wValue      = 0;
    	BudgetValue bValue      = new BudgetValue(data, 0);
        BudgetValue sValue      = new BudgetValue(data, 0);
        boolean isRepeatValue   = false;

        String cellType = "";
        if(table != null){
    		if(table.getModel() != null){
    		   	if(data.cellTypeData[column] != null){
    		   		if(data.cellTypeData[column].get(acctName) != null){
    		   			cellType = ((String) data.cellTypeData[column].get(acctName)).toString();
    		   			
    		   			if(cellType.equalsIgnoreCase("repeat")){
    		   				isRepeatValue = true;
    		   			} else {
    		   				if(cellType.equalsIgnoreCase("origin")){
        		   				this.setBorder(BorderFactory.createLineBorder(Color.blue));
        		   			} else {
        		   				this.setBorder(null);
        		   			}
    		   			}
    		   		}
    		   	}
    		}
    	}
        
        if(isRepeatValue){
        	if (value instanceof BudgetValue) {
        	   if (isNegative)
        	        setForeground(orangeColor);
        	   else
        	        setForeground(blueColor);
        	}
        	
        }
        
    	if(table != null){
    		if(table.getModel() != null){
    			sValue.setValue(data.getSpendingValue(acctName, column));
    		}
    	}
    	
    	if (value instanceof BudgetValue) {
        	bValue.setValue((BudgetValue)value);
        	int dayOfMonth   = Calendar.getInstance().get(Calendar.DAY_OF_MONTH);
        	int lastDate     = Calendar.getInstance().getActualMaximum(Calendar.DATE);
        	wValue = (bValue.doubleValue() * dayOfMonth) / lastDate;
        }

    	int currentMonth = Calendar.getInstance().get(Calendar.MONTH) + 1;
    	
    	if(value instanceof BudgetValue) {
	    	if(table != null){
	    		
	    		if(! data.isSpendingNull(acctName, column)){
	    			
	    			Account thisAccount = data.getAccount(acctName);
	    			if(thisAccount.getAccountType() == Account.AccountType.INCOME){
	    				inverseColor = true;
	    			} else {
	    				inverseColor = false;
	    			}
	        			
        			this.setToolTipText(sValue.toString());
        			
        			if(bValue.isNegative() && sValue.isNegative()){
        				bValue.negate();
        				sValue.negate();
        				wValue = -wValue;
        			}
        			
        			if(bValue.doubleValue() != sValue.doubleValue()){
        				if(inverseColor){
    	    				if( bValue.diff(sValue) < 0){
    	    					setBackground(lgreenColor);
    				    	} else if( currentMonth == column && (wValue - sValue.doubleValue()) > 0 ){
    				    		setBackground(lgreenColor);
    				    	} else if( bValue.diff(sValue) > 0 ){
    				    		setBackground(lredColor);
    				    		setForeground(blackColor);
    				   		}
    			    	} else {
    			    		if( bValue.diff(sValue) < 0){
    				    		setBackground(lredColor);
    				    		setForeground(blackColor);
    				    	} else if( currentMonth == column &&  (wValue - sValue.doubleValue()) < 0 ){
    				    		setBackground(lyellowColor);
    				    	} else if( bValue.diff(sValue) > 0 ){
    				   			setBackground(lgreenColor);
    				   		}
    			    	}
        			}

    		    	return this;
	    		}
	    		
	    		if(isNegative){
	    			setForeground(orangeColor);
	    		} else {
	    			if(isRepeatValue){
		    			setForeground(lblueColor);
		    		} else {
		    			setForeground(greyColor);
		    		}
	    		}

	    		this.setToolTipText("0.0");
		    	return this;
			    	
	    	}

    	} else {
    		this.setToolTipText( sValue.toString() );
    	}
    } else {
    	this.setToolTipText( null );
    }

    return this;
  }

}
