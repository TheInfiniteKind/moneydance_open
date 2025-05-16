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

import java.awt.Component;

import javax.swing.DefaultCellEditor;
import javax.swing.JTable;
import javax.swing.table.TableModel;

import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;

public class MyDateEditor extends DefaultCellEditor { 
	private static final long serialVersionUID = 1L;
	private JDateField ftf;
	
	public MyDateEditor( Parameters objParamsp) {
	      super(new JDateField(Main.cdate));
	      ftf = (JDateField)getComponent();
	  }
	
	  //Override to invoke setValue on the formatted text field.
	  @Override
	public Component getTableCellEditorComponent(JTable table,
	          Object value, boolean isSelected,
	          int row, int column) {
		 JDateField ftf = (JDateField)super.getTableCellEditorComponent(
  	                table, value, isSelected, row, column);
		 if (value==null||(value instanceof String && ((String)value).isEmpty()))
			ftf.gotoToday();
		 else
			 ftf.setDateInt(ftf.getDateIntFromString((String)value));
		 
		 return ftf;
	  }
	

	  @Override
	public Object getCellEditorValue() {
	      ftf = (JDateField)getComponent();
	      return ftf.getText();
	  }
	
	  //Override to check whether the edit is valid,
	  //setting the value if it is and complaining if
	  //it isn't.  If it's OK for the editor to go
	  //away, we need to invoke the superclass's version 
	  //of this method so that everything gets cleaned up.
	@Override
	public boolean stopCellEditing() {
	      JDateField ftf = (JDateField)getComponent();
	      ftf.selectAll();
	      return super.stopCellEditing();
	}
}
