package com.moneydance.modules.features.budgetgen;


//import java.awt.Component;

//import javax.swing.DefaultCellEditor;
//import javax.swing.JCheckBox;
//import javax.swing.JComponent;

import java.awt.Color;
import java.awt.Component;
import java.awt.Point;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableColumn;


public class GenerateTable extends JTable {
	private MyCurrencyEditor objCurrencyEdit;
	/*
	 * pop up menu items
	 */
	private JPopupMenu menAmount;
	private JMenuItem mitBudget;
	private JMenuItem mitActuals;
	private JMenuItem mitCopy;
	private BudgetParameters objParams;
	private GenerateTableModel objModel;
    public class CustomTableCellRenderer extends DefaultTableCellRenderer
    {
         @Override
        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
            Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
            if (row % 2 == 0) {
                if (isSelected) 
            	    c.setBackground(Constants.SELECTEDCLR);
            	else
                    c.setBackground(Constants.ALTERNATECLR);
            }
            else
               c.setBackground(Color.WHITE);
            c.setForeground(Color.BLACK);
       return c;   
      }     
    }
	public GenerateTable(GenerateTableModel model, BudgetParameters objParamsp) {
		super(model);
		objModel = model;
		objParams = objParamsp;
		objCurrencyEdit = new MyCurrencyEditor(objParams,Constants.GENWINDOW);
		this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		this.setCellSelectionEnabled(true);
		/*
		 * Select
		 */
		TableColumn colSelect = this.getColumnModel().getColumn(0);

		/*
		 * Amount values
		 */
		for (int i=0;i<model.getColumnCount();i++) {
			colSelect = this.getColumnModel().getColumn(i);
			colSelect.setPreferredWidth(Constants.GENAMOUNTWIDTH);
			colSelect.setMinWidth(Constants.GENAMOUNTWIDTH);
			colSelect.setResizable(false);
			colSelect.setCellEditor(objCurrencyEdit);
			colSelect.setCellRenderer(new CustomTableCellRenderer());
		}
		setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
		/*
		 * pop up menu
		 */
		ActionListener mitListener = new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent aeEvent) {
				String strAction = aeEvent.getActionCommand();
				int iRow = GenerateTable.this.getSelectedRow();
				int iCol= GenerateTable.this.getSelectedColumn();
				if (strAction.contains("Budget")){
					objModel.setValueAt(objModel.getPreviousBudget(iRow, iCol), iRow, iCol);
				}
				if (strAction.contains("Actuals")){
					objModel.setValueAt(objModel.getPreviousActuals(iRow, iCol), iRow, iCol);					
				}
				if (strAction.contains("Copy")){
					String strAmt = (String) GenerateTable.this.objModel.getValueAt(iRow,  iCol); 
					for (int i = iCol+1;i<GenerateTable.this.objModel.getColumnCount();i++) {
						GenerateTable.this.objModel.setValueAt(strAmt, iRow, i);
					};					
				}
				GenerateTable.this.objModel.fireTableDataChanged();
			}
		};
		menAmount = new JPopupMenu();
		mitBudget = new JMenuItem();
		mitBudget.addActionListener(mitListener);
		mitActuals = new JMenuItem();
		mitActuals.addActionListener(mitListener);
		mitCopy = new JMenuItem();
		mitCopy.addActionListener(mitListener);
		menAmount.add(mitBudget);
		menAmount.add(mitActuals);
		menAmount.add(mitCopy);
		addMouseListener(new MouseAdapter() {
			@Override
			public void mousePressed(MouseEvent me) {
				showPopup(me);
			}

			@Override
			public void mouseReleased(MouseEvent me) {
				showPopup(me);
			}
		});	
	}
	/*
	 * popup menu
	 */
	private void showPopup(MouseEvent me) {
		// is this event a popup trigger?
		if (menAmount.isPopupTrigger(me)) {
			Point p = me.getPoint();
			int iRow = rowAtPoint(p);
			int iCol = columnAtPoint(p);
			// if we've clicked on a row in the amount col
			if (iRow != -1 &&
				(iRow & 1) == 0) {
				mitBudget.setText("Use previous period Budget ("+objModel.getPreviousBudget(iRow, iCol)+")");
				mitActuals.setText("Use previous period Actuals ("+objModel.getPreviousActuals(iRow, iCol)+")");
				mitCopy.setText("Copy Value to end of period");
				menAmount.show(me.getComponent(), me.getX(), me.getY());
			}
		}
	}
}
