package com.moneydance.modules.features.budgetgen;

import java.awt.Color;
import java.awt.Component;

import javax.swing.BorderFactory;
import javax.swing.DefaultCellEditor;
import javax.swing.JCheckBox;
import javax.swing.JComponent;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.border.Border;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;


public class GenerateTableHeader extends JTable {
    Color alternate = new Color(0xC0, 0xC0, 0xF0);
	private class RenderSelect extends JComponent implements TableCellRenderer {

		@Override
		public Component getTableCellRendererComponent(JTable table,
				Object value, boolean isSelected, boolean hasFocus, int row,
				int column) {
			if ((row & 1)==0) {
				JCheckBox boxTemp = new JCheckBox();
				boxTemp.setSelected((boolean)value);
				return boxTemp;
			}
			else {
				JTextField txtField =  new JTextField(" ");
				Border empty = BorderFactory.createEmptyBorder();
				txtField.setBorder(empty);
				return txtField;
			}
		}
		
	}
	RenderSelect objRender = new RenderSelect();
	public GenerateTableHeader(GenerateTableHeaderModel model) {
		super(model);
		this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		/*
		 * Select
		 */
		TableColumn colSelect = this.getColumnModel().getColumn(0);
		colSelect.setPreferredWidth(Constants.GENSELECTPREFWIDTH);
		colSelect.setMinWidth(Constants.GENSELECTMINWIDTH);
		colSelect.setCellRenderer(objRender);
		colSelect.setCellEditor(new DefaultCellEditor(new JCheckBox()));
		/*
		 * category
		 */
//		this.getColumnModel().getColumn(1).setResizable(false);
		this.getColumnModel().getColumn(1).setPreferredWidth(Constants.GENCATPREFWIDTH);
		this.getColumnModel().getColumn(1).setMinWidth(Constants.GENCATMINWIDTH);
		setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
	}
   @Override
public Component prepareRenderer(TableCellRenderer renderer, int row, int column) {
        Component stamp = super.prepareRenderer(renderer, row, column);
        if (row % 2 == 0)
            stamp.setBackground(Constants.ALTERNATECLR);
        else
            stamp.setBackground(this.getBackground());
        return stamp;
    }

}
