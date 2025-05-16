package com.moneydance.modules.features.mrbutil;

import java.awt.Component;
import java.awt.Dimension;

import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;

/**
 * Overrides JTable to enable word wrap.  Uses the TableCellRender interface to 
 *  catch any update of a table cell.  Registers LineWrapCellRenderer for an Object class
 *  so all cells on the table are caught
 * @author Mike Bray
 *
 */
public class MRBTranTable extends JTable
{

	private static final long serialVersionUID = 1L;
	private int iSelectedRow;
	private MRBViewTransactions objViewTran;
	public class LineWrapCellRenderer extends JTextArea implements TableCellRenderer {
		/**
		 * 
		 */
		private static final long serialVersionUID = 1L;
		int rowHeight = 0;  // current max row height for this scan
		@Override
		public Component getTableCellRendererComponent(
		        JTable table,
		        Object value,
		        boolean isSelected,
		        boolean hasFocus,
		        int row,
		        int column)
		{
		    setText((String) value);
		    setWrapStyleWord(true);
		    setLineWrap(true);
		
		 // current table column width in pixels
		    int colWidth = table.getColumnModel().getColumn(column).getWidth();
		
		    // set the text area width (height doesn't matter here)
		    setSize(new Dimension(colWidth, 1)); 
		
		    // get the text area preferred height and add the row margin
		    int height = getPreferredSize().height + table.getRowMargin();
		    // ensure the row height fits the cell with most lines
		    if (column == 0 || height > rowHeight) {
		        table.setRowHeight(row, height);
		        rowHeight = height;
		    }
		    return this;
		}
	}
	public class RowListener implements ListSelectionListener {
        @Override
		public void valueChanged(ListSelectionEvent event) {
            if (event.getValueIsAdjusting()) {
                return;
            }
            ListSelectionModel lsm = (ListSelectionModel)event.getSource();
            iSelectedRow = lsm.getMaxSelectionIndex();
            objViewTran.displayTransaction(iSelectedRow);
         }
		
	}
	/**
	 * Create the table
	 * @param model - Table Model to be used
	 * @param objViewTranp = MRBViewTransaction instance, will be used to call displayTransaction 
	 * when user selects a transaction
	 */
	public MRBTranTable(DefaultTableModel model,MRBViewTransactions objViewTranp)
	{
		super(model);
		objViewTran = objViewTranp;
		TableColumn detailcolumn = null;
        detailcolumn = getColumnModel().getColumn(0);
         detailcolumn.setPreferredWidth(200);
        detailcolumn = getColumnModel().getColumn(1);
        detailcolumn.setPreferredWidth(300);
        detailcolumn = getColumnModel().getColumn(2);
        detailcolumn.setPreferredWidth(100);
        detailcolumn = getColumnModel().getColumn(3);
        detailcolumn.setPreferredWidth(100);
        detailcolumn = getColumnModel().getColumn(4);
        detailcolumn.setPreferredWidth(75);
        detailcolumn = getColumnModel().getColumn(5);
        detailcolumn.setPreferredWidth(20);
        detailcolumn = getColumnModel().getColumn(6);
        detailcolumn.setPreferredWidth(90);
        detailcolumn = getColumnModel().getColumn(7);
        detailcolumn.setPreferredWidth(100);
        setFillsViewportHeight(true);
		this.setDefaultRenderer(Object.class, new LineWrapCellRenderer());
		this.setAutoResizeMode(AUTO_RESIZE_OFF);
		this.setRowSelectionAllowed(true);
		this.getSelectionModel().addListSelectionListener(new RowListener());
		this.setSelectionMode(
                ListSelectionModel.SINGLE_SELECTION);
	}
}