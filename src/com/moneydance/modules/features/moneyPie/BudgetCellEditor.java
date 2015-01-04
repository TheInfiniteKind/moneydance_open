package com.moneydance.modules.features.moneyPie;

import javax.swing.AbstractCellEditor;
import javax.swing.table.TableCellEditor;
import javax.swing.JTextField;
import javax.swing.JTable;
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.Font;
import java.util.EventObject;
import java.awt.event.MouseEvent;

@SuppressWarnings("serial")
public class BudgetCellEditor extends AbstractCellEditor implements TableCellEditor,  ActionListener {	
	private BudgetData  data;
	private BudgetValue currentValue;
	private JTextField  field;
	
	public BudgetCellEditor(BudgetData data) {
		currentValue = new BudgetValue(data, 0);
		this.data = data;
		
		field = new JTextField();
		field.setText(currentValue.toString());
		field.addActionListener(this);
		
		Font f = field.getFont();
		String name = f.getFontName();
		int size    = f.getSize();
		
		Font s = new Font(name, Font.PLAIN, size-2);
		field.setFont(s);
	}
	
	public boolean isCellEditable(EventObject evt) {
        if (evt instanceof MouseEvent) {
            int clickCount = 2;

            return ((MouseEvent)evt).getClickCount() >= clickCount;
        }
        return true;
    }

	
	public void actionPerformed(ActionEvent e) {
		currentValue.setValue(field.getText());
		fireEditingStopped();
	}
	
	//Implement the one CellEditor method that AbstractCellEditor doesn't.
	public Object getCellEditorValue() {
		return currentValue;
	}
	
	//Implement the one method defined by TableCellEditor.
	public Component getTableCellEditorComponent(JTable table,
	                        Object value,
	                        boolean isSelected,
	                        int row,
	                        int column) {
		
		String acctName = (String) table.getModel().getValueAt(row, 0);
		
		double actualValue = data.fetchBudgetValue(acctName, column);
		
		if(actualValue != 0){
			currentValue.setValue(actualValue);
		} else {
			if (value instanceof BudgetValue) {
				currentValue.setValue((BudgetValue)value);
			} else {
				currentValue.setValue((String)value);
			}
			
		}
		
		((BudgetTable) table).hideBalloon();
		
		field.setText(currentValue.rawString());
		return field;
	}
	
}
