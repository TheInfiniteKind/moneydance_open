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

import java.awt.Color;
import java.awt.Component;
import java.awt.Point;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.BorderFactory;
import javax.swing.DefaultCellEditor;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.border.Border;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;

public class MyTable extends JTable {
	/*
	 * Renderer for rollup column
	 */
	private class RenderSelect extends JComponent implements TableCellRenderer {

		@Override
		public Component getTableCellRendererComponent(JTable table,
				Object value, boolean isSelected, boolean hasFocus, int row,
				int column) {
			BudgetLine objLine = objParams.getLines().get(row);
			if (objLine.getType() == Constants.PARENT_LINE) {
				JCheckBox boxTemp = new JCheckBox();
	            if (row % 2 == 0) {
	                boxTemp.setBackground(Constants.ALTERNATECLR);
	            }
	            else {
	                boxTemp.setBackground(Color.WHITE);
	            }
	            boxTemp.setForeground(Color.BLACK);
				boxTemp.setSelected((boolean) value);
				return boxTemp;
			} else {
				JTextField txtField = new JTextField(" ");
				Border empty = BorderFactory.createEmptyBorder();
	            if (row % 2 == 0) {
	                txtField.setBackground(Constants.ALTERNATECLR);
	            }
	            else {
	                txtField.setBackground(Color.WHITE);
	            }
				txtField.setBorder(empty);
				return txtField;
			}
		}

	}
	/*
	 * Renderer for select column
	 */

	private class SelectSelect extends JComponent implements TableCellRenderer {

		@Override
		public Component getTableCellRendererComponent(JTable table,
				Object value, boolean isSelected, boolean hasFocus, int row,
				int column) {
			JCheckBox boxTemp = new JCheckBox();
	        if (row % 2 == 0) {
                boxTemp.setBackground(Constants.ALTERNATECLR);
	        }
	        else {
	            boxTemp.setBackground(Color.WHITE);
	        }
	        boxTemp.setForeground(Color.BLACK);
	        boxTemp.setSelected((boolean) value);
			return boxTemp;
		}

	}
	/*
	 * Renderer for columns where the user can change data
	 */
    public class SelectedCellRenderer extends DefaultTableCellRenderer
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
            else {
                if (isSelected) 
            	    c.setBackground(Constants.SELECTEDCLR);
            	else
                    c.setBackground(Color.WHITE);
            }
            c.setForeground(Color.BLACK);
       return c;   
      }     
    }
    /*
     * Renderer for columns where the user can not change data
     */
    public class NonSelectedCellRenderer extends DefaultTableCellRenderer
    {
         @Override
        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
            Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
            if (row % 2 == 0) {
                c.setBackground(Constants.ALTERNATECLR);
            }
            else {
                c.setBackground(Color.WHITE);
            }
            c.setForeground(Color.BLACK);
       return c;   
      }     
    }
    private RenderSelect objRollupRender = new RenderSelect();
    private SelectSelect objSelectRender = new SelectSelect();
	private MyPercentRender objPerc = new MyPercentRender();
	private MyCurrencyEditor objCurrencyEdit;
	private SelectedCellRenderer objSelRender = new SelectedCellRenderer();
	private NonSelectedCellRenderer objNonSelRender = new NonSelectedCellRenderer();
	private BudgetParameters objParams;
	private JCheckBox boxRollup = new JCheckBox();
	MyTableModel objModel;
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	@SuppressWarnings({ "rawtypes", "unchecked" })
	private DefaultCellEditor objEdit = new DefaultCellEditor(new JComboBox(
			Constants.arrPeriod));
	/*
	 * pop up menu items
	 */
	private JPopupMenu menAmount;
	private JMenuItem mitBudget;
	private JMenuItem mitActuals;

	public MyTable(MyTableModel model, BudgetParameters objParamsp) {
		super(model);
		objParams = objParamsp;
		objCurrencyEdit = new MyCurrencyEditor(objParams,Constants.VALUESWINDOW);
		objModel = model;
		this.setFillsViewportHeight(true);
		this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		this.setCellSelectionEnabled(true);
		/*
		 * Select
		 */
		TableColumn colSelect = this.getColumnModel().getColumn(0);
		colSelect.setPreferredWidth(40);
		colSelect.setCellRenderer(objSelectRender);
		/*
		 * category
		 */
		this.getColumnModel().getColumn(1).setResizable(false);
		this.getColumnModel().getColumn(1).setPreferredWidth(200);
		this.getColumnModel().getColumn(1).setCellRenderer(objNonSelRender);
		/*
		 * Rollup
		 */
		TableColumn colRollup = this.getColumnModel().getColumn(2);
		colRollup.setCellEditor(new DefaultCellEditor(boxRollup));
		colRollup.setCellRenderer(objRollupRender);
		colRollup.setPreferredWidth(60);
		/*
		 * Amount
		 */
		colSelect = this.getColumnModel().getColumn(3);
		colSelect.setResizable(false);
		colSelect.setPreferredWidth(100);
		colSelect.setCellEditor(objCurrencyEdit);
		colSelect.setCellRenderer(objSelRender);
		/*
		 * Period
		 */
		colSelect = this.getColumnModel().getColumn(4);
		colSelect.setCellEditor(objEdit);
		colSelect.setResizable(false);
		colSelect.setPreferredWidth(100);
		colSelect.setCellRenderer(objNonSelRender);
		/*
		 * Start Date
		 */
		colSelect = this.getColumnModel().getColumn(5);
		this.setRowHeight(20);
		colSelect.setCellEditor(new MyDateEditor(objParams));
		colSelect.setPreferredWidth(100);
		colSelect.setCellRenderer(objSelRender);
		/*
		 * RPI
		 */
		colSelect = this.getColumnModel().getColumn(6);
		colSelect.setPreferredWidth(100);
		colSelect.setCellRenderer(objPerc);
		/*
		 * Year 1 amount
		 */
		colSelect = this.getColumnModel().getColumn(7);
		colSelect.setPreferredWidth(100);
		colSelect.setCellRenderer(objNonSelRender);
		this.setShowGrid(false);
		/*
		 * pop up menu
		 */
		ActionListener mitListener = new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent aeEvent) {
				String strAction = aeEvent.getActionCommand();
				int iRow = MyTable.this.getSelectedRow();
				if (strAction.contains("Budget")){
					objModel.setValueAt(objModel.getPreviousBudget(iRow), iRow, 3);
				}
				if (strAction.contains("Actuals")){
					objModel.setValueAt(objModel.getPreviousActuals(iRow), iRow, 3);					
				}
			}
		};
		menAmount = new JPopupMenu();
		mitBudget = new JMenuItem();
		mitBudget.addActionListener(mitListener);
		mitActuals = new JMenuItem();
		mitActuals.addActionListener(mitListener);
		menAmount.add(mitBudget);
		menAmount.add(mitActuals);
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
			if (iRow != -1 && iCol == 3) {
				mitBudget.setText("Use previous period Budget ("+objModel.getPreviousBudget(iRow)+")");
				mitActuals.setText("Use previous period Actuals ("+objModel.getPreviousActuals(iRow)+")");
				menAmount.show(me.getComponent(), me.getX(), me.getY());
			}
		}
	} 
	/*
	 * reset the table after size changed
	 */

	public void resetCombo(int iYears) {
		/*
		 * Select
		 */
		TableColumn colSelect = this.getColumnModel().getColumn(0);
		colSelect.setPreferredWidth(40);
		colSelect.setCellRenderer(objSelectRender);
		/*
		 * category
		 */
		this.getColumnModel().getColumn(1).setResizable(false);
		this.getColumnModel().getColumn(1).setPreferredWidth(200);
		this.getColumnModel().getColumn(1).setCellRenderer(objNonSelRender);
		/*
		 * Rollup
		 */
		colSelect = this.getColumnModel().getColumn(2);
		colSelect.setPreferredWidth(40);
		colSelect.setCellRenderer(objRollupRender);
		/*
		 * Amount
		 */
		colSelect = this.getColumnModel().getColumn(3);
		colSelect.setCellEditor(objCurrencyEdit);
		colSelect.setCellRenderer(objSelRender);
		/*
		 * Period
		 */
		colSelect = this.getColumnModel().getColumn(4);
		colSelect.setCellEditor(objEdit);
		colSelect.setResizable(false);
		colSelect.setPreferredWidth(100);
		colSelect.setCellRenderer(objSelRender);
		/*
		 * Date
		 */
		colSelect = this.getColumnModel().getColumn(5);
		colSelect.setCellEditor(new MyDateEditor(objParams));
		colSelect.setPreferredWidth(100);
		colSelect.setCellRenderer(objSelRender);
		/*
		 * RPI
		 */
		colSelect = this.getColumnModel().getColumn(6);
		colSelect.setPreferredWidth(100);
		colSelect.setCellRenderer(objPerc);
		/*
		 * Amounts
		 */
		for (int i=7;i<iYears+7;i++){
			colSelect = this.getColumnModel().getColumn(i);
			colSelect.setPreferredWidth(100);
			colSelect.setCellRenderer(objNonSelRender);
			
		}
	}


	@Override
	public String getToolTipText(MouseEvent e){
        String strTip = null;
        java.awt.Point p = e.getPoint();
        int iRow = rowAtPoint(p);
        int iCol = columnAtPoint(p);

        try {
            strTip = getValueAt(iRow, iCol).toString();
            switch (iCol) {
            case 0:
            	strTip = "Click to select line";
            	break;
            case 2:
            	strTip = "<html>If the line is a parent of other lines you can select Roll-up";
            	strTip += "<br>When selected budget figures from the Child lines will be added to this line</html>";
            	break;
            case 3:
            	strTip = "<html>Enter the amount you require on each occurance.";
            	strTip += "<br>The generator will create an amount for each period as defined by the period";
            	strTip += "<br>The amounts will be totaled together into budget items inline with the period for the Budget";
            	strTip += "<br>Right click to use previous budget or actuals amount</html>";
            	break;
            case 4:
            	strTip = "<html>Select the occurance of the expenditure/income";
            	strTip += "<br>Weekly = every 7 days";
            	strTip += "<br>Bi-Weekly = every 14 days";
            	strTip += "<br>Monthly = every month";
            	strTip += "<br>10 Month = every month for the first 10 months of the year";
            	strTip += "<br>Quarterly = every 3 months";
            	strTip += "<br>Annual = once a year</html>";
            	break;
            case 5:
            	strTip = "Enter a start date if different than the overall start date";
            	break;
            case 6:
            	strTip = "<html>Enter an extra Retail Price Index.";
            	strTip += "<br>This will be added to the RPI at the top of the screen";
            	strTip += "<br>Used to calculate Year 2 and Year 3 amounts</html>";
            }
        } catch (RuntimeException e1) {
            //catch null pointer exception if mouse is over an empty line
        }

        return strTip;
	}
}
