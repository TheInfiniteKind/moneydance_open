/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
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
 * 
 */
package com.moneydance.modules.features.securityquoteload.view;
/*
 * Cell Editor for Currency Amounts
 * 
 * Uses the CurrencyType of the line to determine a valid amount field
 */
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.AbstractAction;
import javax.swing.DefaultCellEditor;
import javax.swing.JFormattedTextField;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.KeyStroke;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;

public class MyCurrencyEditor extends DefaultCellEditor {

	  /**
	 * 
	 */
	private MRBDebug debugInst = Main.debugInst;
	private static final long serialVersionUID = 1L;
	private Parameters params;
	  private MyTextField ftf;
   @SuppressWarnings({"serial" })
	public MyCurrencyEditor(Parameters paramsp) {
	        super(new MyTextField());
	        params = paramsp;
	        ftf = (MyTextField)getComponent();
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
	    	        debugInst.debug("MyCurrencyEditor","getActionMap",MRBDebug.DETAILED,"");
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
            MyTextField ftf =
	            (MyTextField)super.getTableCellEditorComponent(
	                table, value, isSelected, row, column);
 	        ftf.setValue(value);
	        debugInst.debug("MyCurrencyEditor","getTableCellEditorComponent",MRBDebug.DETAILED,"value="+value);
	        return ftf;
	    }

	    /*
	     * Override to ensure that the value remains a valid currency value based on
	     * Row currency type
	     */
	    @Override
		public Object getCellEditorValue() {
	        MyTextField ftf = (MyTextField)getComponent();
	        debugInst.debug("MyCurrencyEditor","getCellEditorValue",MRBDebug.DETAILED,"value="+ftf.getValue());
	        return ftf.getValue();
	    }

	    //Override to check whether the edit is valid,
	    //setting the value if it is and complaining if
	    //it isn't.  If it's OK for the editor to go
	    //away, we need to invoke the superclass's version 
	    //of this method so that everything gets cleaned up.
	    //if decimal character set to ',' change to '.' before validating
	    //then change back
	    @Override
		public boolean stopCellEditing() {
	        MyTextField ftf = (MyTextField)getComponent();
	        debugInst.debug("MyCurrencyEditor","stopCellEditing",MRBDebug.DETAILED,"");
	        if (Main.decimalChar == ','){
	        	String tempValue = ftf.getText();
	        	if (tempValue.indexOf('.') != -1)
	        		return false;
	        	tempValue.replace(',', '.');
	        	ftf.setText(tempValue);
	        }
	        if (validateCurrency(ftf)) {
	            try {
	                ftf.commitEdit();
	            } catch (java.text.ParseException exc) {
	            	if (Main.decimalChar == ',') {
	            		String tempValue = ftf.getText();
	    	        	tempValue.replace('.', ',');
	    	        	ftf.setText(tempValue);
	            	}
	            	return false;
	            }
		    
	        } else { //text is invalid
            	if (Main.decimalChar == ',') {
            		String tempValue = ftf.getText();
    	        	tempValue.replace('.', ',');
    	        	ftf.setText(tempValue);
            	}
		        return false; //don't let the editor go away
		    } 
        	if (Main.decimalChar == ',') {
        		String tempValue = ftf.getText();
	        	tempValue.replace('.', ',');
	        	ftf.setText(tempValue);
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
	        String strValue = ftf.getText();
	        debugInst.debug("MyCurrencyEditor","validateCurrency",MRBDebug.DETAILED,"value="+strValue);
        
	        strValue = strValue.trim();
	        /*
	         * construct numeric format for parsing
	         * 
	         * First parse for integer, if fails parse for decimal
	         */
	        String strFormat = "^\\d+$";
	        debugInst.debug("MyCurrencyEditor","validateCurrency",MRBDebug.DETAILED,"value="+strValue);
	        if (strValue.matches(strFormat)) {
		        debugInst.debug("MyCurrencyEditor","validateCurrency",MRBDebug.DETAILED,"matches"+strFormat);
	        	return true;
	        }
	        int iDecimal = Parameters.decimals[params.getDecimal()-2];
	        if (Main.decimalChar==',')
		        strFormat = "^\\d+,\\d{1,"+iDecimal+"}$";
	        else
	        	strFormat = "^\\d+\\.\\d{1,"+iDecimal+"}$";
	        if (strValue.matches(strFormat)) {
		        debugInst.debug("MyCurrencyEditor","validateCurrency",MRBDebug.DETAILED,"matches"+strFormat);
	        	return true;
	        }
	        else {
		        debugInst.debug("MyCurrencyEditor","validateCurrency",MRBDebug.DETAILED,"no match");
	        	return false;
	        }
	    }
}	    
	    

