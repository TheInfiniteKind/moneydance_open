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

import java.awt.Color;
import java.awt.Component;
import java.awt.Point;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellEditor;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableRowSorter;

import com.moneydance.apps.md.view.gui.MDColors;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;

public class CurTable extends JTable {
	private MyCheckBox boxSelect = new MyCheckBox();
	String[] arrSources;
	private Parameters params;
	private DefaultTableCellRenderer rightRender;
	private MyCurrencyEditor currencyEditor;
	private MyDateEditor dateEditor;
	private CurTable tableObj;
	private CurTableModel dm;
	private JTableHeader header;
	private MRBDebug debugInst = Main.debugInst;
	private boolean isColumnWidthChanged;
	private int[] columnWidths;
	private JPopupMenu sourcePopup;
	private JMenuItem sourceDoNotLoad;
	private JMenuItem sourceYahoo;
	private JMenuItem sourceYahooTD;
	private JMenuItem sourceYahooHist;
	private JMenuItem sourceFT;
	private JMenuItem sourceAlpha;
	private JComboBox<String> currencySources;
	private TableCheckBox selectRenderer;
	public static int selectCol = 0;
	public static int tickerCol = 1;
	public static int accountCol = 2;
	public static int sourceCol = 3;
	public static int lastPriceCol = 4;
	public static int lastDateCol = 5;
	public static int newPriceCol = 6;
	public static int perChangeCol = 7;
	public static int amtChangeCol = 8;
	public static int tradeDateCol = 9;
	private MDColors colors = MDColors.getSingleton();
	private TableRowSorter<CurTableModel> trs;

	@Override
	public Component prepareRenderer(TableCellRenderer renderer, int rowIndex, int vColIndex) {
		int modRow=tableObj.convertRowIndexToModel(rowIndex);
		Component rComp = super.prepareRenderer(renderer, rowIndex, vColIndex);
		if (vColIndex == newPriceCol || vColIndex==perChangeCol || vColIndex==amtChangeCol)
			return rComp;
		Color c = (rowIndex % 2 == 0 ? colors.registerBG2 : colors.registerBG1);
		rComp.setBackground(c);
            if (vColIndex == lastDateCol && ((String)dm.getValueAt(modRow, vColIndex)).endsWith("*")) 
                  rComp.setForeground(Color.RED);
            else 
         	   rComp.setForeground(UIManager.getColor("TextField.Foreground"));
		return rComp;
	}

	public class PriceRenderer extends DefaultTableCellRenderer {
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected,
				boolean hasFocus, int row, int column) {
			Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			int modRow=tableObj.convertRowIndexToModel(row);
			CurrencyTableLine crntRow = dm.getRowCurrency(modRow);
			Integer status = crntRow.getTickerStatus();
			if (status == null)
				status = 0;
			switch (status) {
			case Constants.TASKSTARTED:
				setOpaque(true);
				setForeground(Color.BLACK);
				setBackground(Color.YELLOW);
				break;
			case Constants.TASKFAILED:
				setOpaque(true);
				setForeground(Color.BLACK);
				setBackground(Color.RED);
				break;
			case Constants.TASKCOMPLETED:
				setOpaque(true);
				setForeground(Color.BLACK);
				setBackground(Color.GREEN);
				break;
			default:
				setOpaque(true);
				setForeground(UIManager.getColor("TextField.Foreground"));
				Color colour = (row % 2 == 0 ? colors.registerBG2 : colors.registerBG1);
				c.setBackground(colour);
			}
			setHorizontalAlignment(JLabel.RIGHT);
			return this;
		}
	}

	public class SignColourRenderer extends DefaultTableCellRenderer {
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected,
				boolean hasFocus, int row, int column) {
			@SuppressWarnings("unused")
			Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			int modRow=tableObj.convertRowIndexToModel(row);
			String sValue = (String) value;
			CurrencyTableLine line = dm.getRowCurrency(modRow);
			setHorizontalAlignment(JLabel.RIGHT);
			if (sValue.isEmpty()) {
				setOpaque(true);
				setForeground(UIManager.getColor("TextField.Foreground"));
				Color colour = (row % 2 == 0 ? colors.registerBG2 : colors.registerBG1);
				setBackground(colour);
				return this;
			}
			Double dValue;
			if (column == perChangeCol)
				dValue = line.getPercentChg();
			else
				dValue = line.getAmtChg();
			double multiplier = Math.pow(10.0, Double.valueOf(params.getDecimal()));
			dValue = Math.round(dValue * multiplier) / multiplier;
			if (dValue == 0.0) {
				setOpaque(false);
				setForeground(UIManager.getColor("TextField.Foreground"));
				return this;
			}
			if (dValue < 0.0) {
				if (dValue < params.getDecimal())
					setOpaque(true);
				setForeground(Color.BLACK);
				setBackground(Color.RED);
			} else {
				setOpaque(true);
				setForeground(Color.BLACK);
				setBackground(Color.GREEN);
			}
			return this;
		}
	}

	private int getBrightness(Color c) {
		return (int) Math.sqrt(c.getRed() * c.getRed() * .241 + c.getGreen() * c.getGreen() * .691
				+ c.getBlue() * c.getBlue() * .068);
	}

	public Color getForeGroundColor(Color color) {
		if (getBrightness(color) < 130)
			return Color.white;
		else
			return Color.black;
	}

	public class DateRenderer extends DefaultTableCellRenderer {
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected,
				boolean hasFocus, int row, int column) {
			@SuppressWarnings("unused")
			Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			String date = (String) value;
			setForeground(UIManager.getColor("TextField.Foreground"));
			if (date.endsWith("*"))
				setForeground(Color.RED);
			setHorizontalAlignment(JLabel.RIGHT);
			return this;
		}
	}

	public static class CheckBoxRenderer extends DefaultTableCellRenderer {
		@Override
		public Component getTableCellRendererComponent(JTable table, Object color, boolean isSelected,
				boolean hasFocus, int row, int column) {
			JCheckBox checkBox;
			if ((boolean) table.getValueAt(row, column))
				checkBox = new JCheckBox(Main.extension.selectedIcon);
			else
				checkBox = new JCheckBox(Main.extension.unselectedIcon);
			checkBox.setHorizontalAlignment(JLabel.CENTER);
			return checkBox;
		}
	}
	public class DoubleComparator implements Comparator<String>{
		public int compare(String o1, String o2) {
			if (o1.isBlank())
				o1="-999999999.99";
			if (o2.isBlank())
				o2="-999999999.99";
			try {
			Double d1 = Double.valueOf(stripNonNum(o1));
			Double d2=Double.valueOf(stripNonNum(o2));
			return d1.compareTo(d2);
			}
			catch (NumberFormatException e) {
				return 0;
			}
		}
	}
	public class DateComparator implements Comparator<String>{
		public int compare(String o1, String o2) {
			if (o1.endsWith("++"))
				o1=o1.substring(0,o1.length()-2);
			if (o2.endsWith("++"))
				o2=o2.substring(0,o2.length()-2);
			Integer i1 = 0;
			Integer i2 = 0;;
			if (o1.isBlank())
				i1=19000101;
			else {
				i1= Main.cdate.parseInt(o1);
			}
			if (o2.isBlank())
				i2=19000101;
			else {
				i2=Main.cdate.parseInt(o2);
			}
			return i1.compareTo(i2);
		}
	}

	private String stripNonNum(String number) {
		String output="";
		for (int i=0;i<number.length();i++) {
			if (number.charAt(i)==Main.decimalChar) {
				output+=number.charAt(i);
				continue;
			}
			switch (number.charAt(i)) {
			case '0':
			case '1':
			case '2':
			case '3':
			case '4':
			case '5':
			case '6':
			case '7':
			case '8':
			case '9':
			case '-':
			case '+':
				output+=number.charAt(i);
			}
		}
		return output;
	}

	public CurTable(Parameters params, CurTableModel dm) {
		super(dm);
		this.dm = dm;
		tableObj = this;
		trs= new TableRowSorter<CurTableModel>(dm);
		this.params = params;
		header = getTableHeader();
		header.setReorderingAllowed(false);
		columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME + ".CUR." + Constants.CRNTCOLWIDTH);
		if (columnWidths.length == 0 || columnWidths.length < Constants.NUMCURTABLECOLS)
			columnWidths = Main.preferences.getIntArray(Constants.CRNTCOLWIDTH);
		if (columnWidths.length == Constants.NUMTABLECOLS - 1) {
			int[] columnWidths2 = new int[Constants.NUMTABLECOLS];
			for (int i = 0; i < 8; i++)
				columnWidths2[i] = columnWidths[i];
			columnWidths2[8] = 80;
			for (int i = 9; i < Constants.NUMTABLECOLS; i++)
				columnWidths2[i] = columnWidths[i - 1];
			columnWidths = columnWidths2;
		}
		if (columnWidths.length == 0 || columnWidths.length < Constants.NUMTABLECOLS)
			columnWidths = Constants.DEFAULTCURCOLWIDTH;
		Main.preferences.put(Constants.PROGRAMNAME + ".CUR." + Constants.CRNTCOLWIDTH, columnWidths);
		currencySources = new JComboBox<String>(params.getCurSourceArray());
		currencyEditor = new MyCurrencyEditor(params);
		dateEditor = new MyDateEditor(params);
		rightRender = new DefaultTableCellRenderer();
		rightRender.setHorizontalAlignment(JLabel.RIGHT);
		selectRenderer = new TableCheckBox(this, this.getDefaultRenderer(Boolean.class),
				this.getDefaultRenderer(Object.class));
		setRowHeight(20);
		this.setAutoCreateRowSorter(false);
		this.setRowSorter(trs);
		trs.addRowSorterListener(e->{
			if (e.getType() == RowSorterEvent.Type.SORT_ORDER_CHANGED){
				List<RowSorter.SortKey> keys = (List<RowSorter.SortKey>) e.getSource().getSortKeys();
				if (!keys.isEmpty()){
					RowSorter.SortKey key = keys.get(0);
					int col = key.getColumn();
					if (col >-1 && col < dm.getColumnCount()){
						String order = key.getSortOrder()==SortOrder.ASCENDING?"A":
								key.getSortOrder()==SortOrder.DESCENDING?"D":"U";
						String colSorter = String.valueOf(col+"/"+order);
						Main.preferences.put(Constants.PROGRAMNAME + ".CUR." + Constants.SORTCOLUMN,colSorter);
					}
				}
			}
		});
		this.setFillsViewportHeight(true);
		this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		this.setCellSelectionEnabled(true);
		this.setDefaultRenderer(MyCheckBox.class, new CheckBoxRenderer());
		this.getColumnModel().addColumnModelListener(new WidthListener());
		this.getTableHeader().addMouseListener(new HeaderMouseListener());
		this.addMouseListener(new TableMouseListener());
		((DefaultTableCellRenderer) this.getTableHeader().getDefaultRenderer())
				.setHorizontalAlignment(JLabel.CENTER);
		/*
		 * Select
		 */
		TableColumn colSelect = this.getColumnModel().getColumn(selectCol);
		colSelect.setCellEditor(new DefaultCellEditor(boxSelect));
		if (MRBPlatform.isFreeBSD() || MRBPlatform.isUnix())
			colSelect.setCellRenderer(new CheckBoxRenderer());
		colSelect.setPreferredWidth(columnWidths[selectCol]);
		colSelect.setCellRenderer(selectRenderer);
		trs.setSortable(selectCol, false);
		/*
		 * Ticker
		 */
		this.getColumnModel().getColumn(tickerCol).setResizable(true);
		this.getColumnModel().getColumn(tickerCol).setPreferredWidth(columnWidths[tickerCol]);
		/*
		 * Account
		 */
		this.getColumnModel().getColumn(accountCol).setResizable(true);
		this.getColumnModel().getColumn(accountCol).setPreferredWidth(columnWidths[accountCol]);
		/*
		 * Source
		 */
		this.getColumnModel().getColumn(sourceCol).setPreferredWidth(columnWidths[sourceCol]);
		this.getColumnModel().getColumn(sourceCol).setResizable(true);
		/*
		 * Current Price
		 */
		this.getColumnModel().getColumn(lastPriceCol).setResizable(true);
		this.getColumnModel().getColumn(lastPriceCol).setPreferredWidth(columnWidths[lastPriceCol]);
		this.getColumnModel().getColumn(lastPriceCol).setCellRenderer(rightRender);
		trs.setComparator(lastPriceCol,new DoubleComparator());
		/*
		 * Current Price Date
		 */
		this.getColumnModel().getColumn(lastDateCol).setResizable(true);
		this.getColumnModel().getColumn(lastDateCol).setPreferredWidth(columnWidths[lastDateCol]);
		this.getColumnModel().getColumn(lastDateCol).setCellRenderer(new DateRenderer());
		trs.setComparator(lastDateCol,new DateComparator());
		/*
		 * New Price
		 */
		this.getColumnModel().getColumn(newPriceCol).setResizable(true);
		this.getColumnModel().getColumn(newPriceCol).setCellEditor(currencyEditor);
		this.getColumnModel().getColumn(newPriceCol).setPreferredWidth(columnWidths[newPriceCol]);
		this.getColumnModel().getColumn(newPriceCol).setCellRenderer(new PriceRenderer());
		trs.setComparator(newPriceCol,new DoubleComparator());
		/*
		 * % change
		 */
		this.getColumnModel().getColumn(perChangeCol).setResizable(true);
		this.getColumnModel().getColumn(perChangeCol).setPreferredWidth(columnWidths[perChangeCol]);
		this.getColumnModel().getColumn(perChangeCol).setCellRenderer(new SignColourRenderer());
		trs.setComparator(perChangeCol,new DoubleComparator());
		/*
		 * amt change
		 */
		this.getColumnModel().getColumn(amtChangeCol).setResizable(true);
		this.getColumnModel().getColumn(amtChangeCol).setPreferredWidth(columnWidths[amtChangeCol]);
		this.getColumnModel().getColumn(amtChangeCol).setCellRenderer(new SignColourRenderer());
		trs.setComparator(amtChangeCol,new DoubleComparator());
	/*
		 * Trade Date
		 */
		this.getColumnModel().getColumn(tradeDateCol).setResizable(true);
		this.getColumnModel().getColumn(tradeDateCol).setCellEditor(dateEditor);
		this.getColumnModel().getColumn(tradeDateCol).setPreferredWidth(columnWidths[tradeDateCol]);
		this.getColumnModel().getColumn(tradeDateCol).setCellRenderer(rightRender);
		trs.setComparator(tradeDateCol,new DateComparator());
		/*
		 Set up sorter after columns comparators have been set
		 */
		String sortOrder = Main.preferences.getString(Constants.PROGRAMNAME + ".CUR." + Constants.SORTCOLUMN,"");
		if (!sortOrder.isEmpty()){
			Integer col = Integer.parseInt(sortOrder.substring(0,sortOrder.indexOf("/")));
			String seq = sortOrder.substring(sortOrder.indexOf("/")+1);
			SortOrder order = seq.equals("A")?SortOrder.ASCENDING: seq.equals("D")?SortOrder.DESCENDING:SortOrder.UNSORTED;
			List<RowSorter.SortKey> keys = new ArrayList<>(2);
			keys.add(new RowSorter.SortKey(col,order));
			trs.setSortKeys(keys);
		}
		/*
		 * pop up menu
		 */
		ActionListener popupListener = new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent aeEvent) {
				String strAction = aeEvent.getActionCommand();
				if (strAction.contains("Do Not")) {
					dm.updateAllSources(0);
					return;
				}
				if (strAction.contains("Yahoo HD")) {
					dm.updateAllSources(3);
					return;
				}
				if (strAction.contains("Yahoo")) {
					dm.updateAllSources(1);
					return;
				}
				if (strAction.contains("FT")) {
					dm.updateAllSources(2);
					return;
				}
				if (strAction.contains("Alpha")){
					dm.updateAllSources(5);
					return;
				}
			}
		};
		sourcePopup = new JPopupMenu();
		sourceDoNotLoad = new JMenuItem();
		sourceDoNotLoad.setText("Set all to Do Not Load");
		sourcePopup.add(sourceDoNotLoad);
		sourceDoNotLoad.addActionListener(popupListener);
		sourceYahoo = new JMenuItem();
		sourceYahoo.setText("Set all to Yahoo");
		sourcePopup.add(sourceYahoo);
		sourceYahoo.addActionListener(popupListener);
		sourceYahooHist = new JMenuItem();
		sourceYahooHist.setText("Set all to Yahoo HD");
		sourcePopup.add(sourceYahooHist);
		sourceYahooHist.addActionListener(popupListener);
		sourceFT = new JMenuItem();
		sourceFT.setText("Set all to FT");
		sourcePopup.add(sourceFT);
		sourceFT.addActionListener(popupListener);
		sourceAlpha = new JMenuItem();
		sourceAlpha.setText("Set all to AlphaVantage HD");
		sourcePopup.add(sourceAlpha);
		sourceAlpha.addActionListener(popupListener);
	}

	@Override
	public TableCellEditor getCellEditor(int row, int column) {
		{
			int modelColumn = convertColumnIndexToModel(column);
			int numAccts = dm.getNumAccounts();
			debugInst.debug("CurTable", "getCellEditor", MRBDebug.SUMMARY, "Account list " + numAccts);
			if (modelColumn == sourceCol) {
				debugInst.debug("CurTable", "getCellEditor", MRBDebug.SUMMARY, "Row " + row);
				return new DefaultCellEditor(currencySources);
			}
			return super.getCellEditor(row, column);
		}
	}

	/*
	 * popup menu
	 */
	private void showPopup(MouseEvent me) {
		// is this event a popup trigger?
		Point p = me.getPoint();
		int iCol = columnAtPoint(p);
		// if we've clicked on a row in the source col
		debugInst.debug("CurTable", "showPopup", MRBDebug.SUMMARY, "source selected " + iCol);
		if (iCol == sourceCol) {
			sourcePopup.show(header, me.getX(), me.getY());
		}
	}

	public boolean getColumnWidthChanged() {
		return isColumnWidthChanged;
	}

	public void setColumnWidthChanged(boolean widthChanged) {
		isColumnWidthChanged = widthChanged;
	}

	private class WidthListener extends MouseAdapter implements TableColumnModelListener {
		@Override
		public void columnMarginChanged(ChangeEvent e) {
			/*
			 * columnMarginChanged is called continuously as the column width is changed by
			 * dragging. Therefore, execute code below ONLY if we are not already aware of
			 * the column width having changed
			 */
			if (!tableObj.getColumnWidthChanged()) {
				/*
				 * the condition below will NOT be true if the column width is being changed by
				 * code.
				 */
				if (tableObj.getTableHeader().getResizingColumn() != null) {
					// User must have dragged column and changed width
					tableObj.setColumnWidthChanged(true);
				}
			}
		}

		// line to force save
		@Override
		public void columnMoved(TableColumnModelEvent e) {
		}

		@Override
		public void columnAdded(TableColumnModelEvent e) {
		}

		@Override
		public void columnRemoved(TableColumnModelEvent e) {
		}

		@Override
		public void columnSelectionChanged(ListSelectionEvent e) {
		}
	}

	private class HeaderMouseListener extends MouseAdapter {
		int resizingColumn = -2;
		int oldWidth = -2;
		int newWidth = -2;

		@Override
		public void mousePressed(MouseEvent e) {
			/* On mouse release, check if column width has changed */
			if (SwingUtilities.isRightMouseButton(e) || e.isControlDown())
				showPopup(e);
			else {
				debugInst.debug("MouseListener", "mousePressed", MRBDebug.DETAILED, "width started ");
				if (e.getSource() instanceof JTableHeader) {
					TableColumn tc = ((JTableHeader) e.getSource()).getResizingColumn();
					if (tc != null) {
						resizingColumn = tc.getModelIndex();
						oldWidth = tc.getPreferredWidth();
					} else {
						resizingColumn = -1;
						oldWidth = -1;
					}
				}

				debugInst.debug("MouseListener", "mousePressed", MRBDebug.DETAILED,
						"column " + resizingColumn + " oldWidth " + oldWidth);
			}
		}

		@Override
		public void mouseReleased(MouseEvent e) {
			/* On mouse release, check if column width has changed */
			if (SwingUtilities.isRightMouseButton(e) || e.isControlDown())
				showPopup(e);
			else {
				if (tableObj.getColumnWidthChanged()) {
					debugInst.debug("MouseListener", "mouseReleased", MRBDebug.DETAILED, "width finished ");
					if (e.getSource() instanceof JTableHeader) {
						TableColumn tc = ((JTableHeader) e.getSource()).getColumnModel()
								.getColumn(resizingColumn);
						if (tc != null) {
							newWidth = tc.getPreferredWidth();
						} else {
							resizingColumn = -1;
							oldWidth = -1;
						}
					}
					debugInst.debug("MouseListener", "mouseReleased", MRBDebug.DETAILED,
							"Column " + resizingColumn + "new width " + newWidth);
					columnWidths[resizingColumn] = newWidth;
					Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.CRNTCOLWIDTH, columnWidths);
					Main.preferences.isDirty();
					// Reset the flag on the table.
					tableObj.setColumnWidthChanged(false);
					debugInst.debug("MouseListener", "mouseReleased", MRBDebug.DETAILED,
							"column " + resizingColumn + " oldWidth " + oldWidth);

				}
			}
		}
	}

	private class TableMouseListener extends MouseAdapter {
		@Override
		public void mouseReleased(MouseEvent e) {
			JTable tc = (JTable) e.getSource();
			Point p = e.getPoint();
			int row = tc.rowAtPoint(p);
			if (row < 0 || row>=dm.getRowCount())
				return;
			int modRow = tableObj.convertRowIndexToModel(row);
			if (tc.getSelectedColumn() == tickerCol) {
				if (e.getClickCount() == 2) {
					CurrencyTableLine acct = dm.getRowCurrency(modRow);
					SwingUtilities.invokeLater(new Runnable() {
						@Override
						public void run() {
							Main.context.showURL(
									"moneydance:showobj?id=" + acct.getCurrencyType().getUUID());
						}
					});
				}
			}
		}
	}
}