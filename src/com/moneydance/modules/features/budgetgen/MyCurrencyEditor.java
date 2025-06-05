/*
 * Copyright (c) 2014, Michael Bray. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */ 
package com.moneydance.modules.features.budgetgen;
/*
 * Cell Editor for Currency Amounts
 * 
 * Uses the CurrencyType of the line to determine a valid amount field
 */
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.util.List;

import javax.swing.AbstractAction;
import javax.swing.DefaultCellEditor;
import javax.swing.JFormattedTextField;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.KeyStroke;

import com.infinitekind.moneydance.model.CurrencyType;

public class MyCurrencyEditor extends DefaultCellEditor {

	  /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	  private MyTextField ftf;
	  private BudgetParameters objParams;
	  private CurrencyType objLocalCur;
	  private int iScreen;

    @SuppressWarnings({"serial" })
	public MyCurrencyEditor(BudgetParameters objParamsp, int iScreenp) {
	        super(new MyTextField());
	        objParams = objParamsp;
	        iScreen = iScreenp;
	        ftf = (MyTextField)getComponent();
	        objLocalCur = Main.context.getCurrentAccountBook().getCurrencies().getBaseType();


	        ftf.setHorizontalAlignment(JTextField.RIGHT);
	        ftf.setFocusLostBehavior(JFormattedTextField.PERSIST);
	        //React when the user presses Enter while the editor is
	        //active.  (Tab is handled as specified by
	        //JFormattedTextField's focusLostBehavior property.)
	        ftf.getInputMap().put(KeyStroke.getKeyStroke(
	                                        KeyEvent.VK_ENTER, 0),
	                                        "check");
	        ftf.getActionMap().put("check", new AbstractAction() {
	            @Override
				public void actionPerformed(ActionEvent e) {
	            	if (validateCurrency((MyTextField)e.getSource())){ //The text is invalid.
                    	ftf.postActionEvent(); //inform the editor
	                } else try {              //The text is valid,
	                    ftf.commitEdit();     //so use it.
	                    ftf.postActionEvent(); //stop editing
	                } catch (java.text.ParseException exc) { }
	            }
	        });
	    }

	    //Override to invoke setValue on the formatted text field.
	    @Override
		public Component getTableCellEditorComponent(JTable table,
	            Object value, boolean isSelected,
	            int row, int column) {
            CurrencyType objCur;
            MyTextField ftf =
	            (MyTextField)super.getTableCellEditorComponent(
	                table, value, isSelected, row, column);
            if (iScreen == Constants.VALUESWINDOW) {
		        List<BudgetLine> listLines =  objParams.getLines();
		        objCur=(listLines.get(row).getCategory() == null ? objLocalCur :listLines.get(row).getCategory().getCurrencyType());
            }
            else {
            	GenerateTableModel objMod = (GenerateTableModel)table.getModel();
            	objCur = objMod.getCurrency(row/2);
            }
	        ftf.setCurrency(objCur);
	        ftf.setValue(value);
	        return ftf;
	    }

	    /*
	     * Override to ensure that the value remains a valid currency value based on
	     * Row currency type
	     */
	    @Override
		public Object getCellEditorValue() {
	        MyTextField ftf = (MyTextField)getComponent();
	        return ftf.getValue();
	    }

	    //Override to check whether the edit is valid,
	    //setting the value if it is and complaining if
	    //it isn't.  If it's OK for the editor to go
	    //away, we need to invoke the superclass's version 
	    //of this method so that everything gets cleaned up.
	    @Override
		public boolean stopCellEditing() {
	        MyTextField ftf = (MyTextField)getComponent();
	        if (validateCurrency(ftf)) {
	            try {
	                ftf.commitEdit();
	            } catch (java.text.ParseException exc) {
	            	return false;
	            }
		    
	        } else { //text is invalid
		        return false; //don't let the editor go away
		    } 
	        return super.stopCellEditing();
	    }
	    /*
	     * validate text of field to determine if valid.
	     * 
	     * Field is in format {prefix}n.d{suffix}
	     * 
	     * {prefix} = prefix from CurrencyType
	     * {suffix} = suffix from CurrencyType
	     * n = integer of any number of digits (at least one)
	     * d = decimals to the number of decimal places from CurrencyType
	     */
	    private boolean validateCurrency(MyTextField ftf) {
	    	CurrencyType objCur = ftf.getCurrency();
	        String strValue = ftf.getText();
	        String strPrefix = objCur.getPrefix();
	        String strSuffix = objCur.getSuffix();
	        
	        /*
	         * Remove currency prefix
	         */
	        if (!strPrefix.equals("")) {
	        	String strLeft = strValue.substring(0, strPrefix.length());
	        	if (strLeft.equals(strPrefix)){
	        		strValue = strValue.substring(strPrefix.length());
	        	}
	        }
	        /*
	         * Remove currency suffix
	         */
	        if (!strSuffix.equals("")) {
	        	String strRight = strValue.substring(strValue.length()-strSuffix.length());
	        	if (strRight.equals(strSuffix)){
	        		strValue = strValue.substring(0,strValue.length()-strSuffix.length());
	        	}
	        }
	        strValue = strValue.trim();
	        /*
	         * construct numeric format for parsing
	         * 
	         * First parse for integer, if fails parse for decimal
	         */
	        String strFormat = "^\\d+$";
	        if (strValue.matches(strFormat))
	        	return true;
	        strFormat = "^\\d+\\.\\d{1," + objCur.getDecimalPlaces()+"}$";
	        if (strValue.matches(strFormat))
	        	return true;
	        else
	        	return false;
	    	
	    }
}	    
	    

