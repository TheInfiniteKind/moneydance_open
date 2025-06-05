package com.moneydance.modules.features.budgetgen;

import java.awt.Component;

import javax.swing.DefaultCellEditor;
import javax.swing.JTable;

import com.moneydance.awt.JDateField;

public class MyDateEditor extends DefaultCellEditor { 
	private static final long serialVersionUID = 1L;
	private JDateField ftf;
	
	@SuppressWarnings({"serial" })
	public MyDateEditor(BudgetParameters objParamsp) {
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
