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
import java.awt.Dimension;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.Toolkit;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.StringSelection;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.border.LineBorder;
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
import com.moneydance.modules.features.securityquoteload.ExchangePopUp;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;
import com.moneydance.modules.features.securityquoteload.AwtUtil;

public class SecTable extends JTable {
	private static final long serialVersionUID = 1L;
	private MyCheckBox boxSelect = new MyCheckBox();
	String[] arrSources;
	private Parameters params;
	private DefaultCellEditor exchangeField;
	private DefaultTableCellRenderer rightRender;
	private BorderOnlyRenderer borderOnlyRenderer;
	private MyCurrencyEditor currencyEditor;
	private MyDateEditor dateEditor;
	private SecTable tableObj;
	private SecTableModel dm;
	private JTableHeader header;
	private MRBDebug debugInst = Main.debugInst;
	private boolean isColumnWidthChanged;
	private int[] columnWidths;
	private JPopupMenu sourcePopup;
	private JMenuItem sourceDoNotLoad;
	private JMenuItem sourceYahoo;
	private JMenuItem sourceYahooHist;
	private JMenuItem sourceFT;
	private JMenuItem sourceFTHD;
	private JMenuItem sourceMD;
	private JMenuItem sourceMDHD;
	private JMenuItem excludeSource;
	private JMenuItem sourceAlpha;
	private JComboBox<String> allSources;
	private TableCheckBox selectRenderer;
	public static int selectCol = 0;
	public static int tickerCol = 1;
	public static int altTickerCol = 2;
	public static int exchangeCol = 3;
	public static int accountCol = 4;
	public static int sourceCol = 5;
	public static int lastPriceCol = 6;
	public static int lastDateCol = 7;
	public static int newPriceCol = 8;
	public static int perChangeCol = 9;
	public static int amtChangeCol = 10;
	public static int tradeDateCol = 11;
	public static int tradeCurCol = 12;
	public static int volumeCol = 13;
	private Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
	private Double screenHeight;
	private MDColors colors = MDColors.getSingleton();
	private TableRowSorter<SecTableModel> trs;

	
	    @Override
	    public Component prepareRenderer(TableCellRenderer renderer, int rowIndex, int vColIndex){
			int modRow=tableObj.convertRowIndexToModel(rowIndex);
			Component rComp=super.prepareRenderer(renderer, rowIndex, vColIndex);
			if (vColIndex == newPriceCol || vColIndex==perChangeCol || vColIndex==amtChangeCol)
				return rComp;
	        Color c = (rowIndex %2 ==0 ? colors.registerBG2:colors.registerBG1);
               rComp.setBackground(c);
               if (vColIndex == lastDateCol && ((String)dm.getValueAt(modRow, vColIndex)).endsWith("*")) 
                     rComp.setForeground(Color.RED);
               else 
            	   rComp.setForeground(UIManager.getColor("TextField.Foreground"));
	        return rComp;
	    }

  private class BorderOnlyRenderer extends DefaultTableCellRenderer {
    private static final Border SELECTED_BORDER = new LineBorder(Color.BLUE, 1);
    private static final Border NO_BORDER = new LineBorder(new Color(0, 0, 0, 0), 1);

    @Override
    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
      super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

      setHorizontalAlignment(LEFT); // or CENTER/RIGHT as needed
      setBorder(isSelected ? SELECTED_BORDER : NO_BORDER);
      setOpaque(true);

      // Custom row striping
      Color bg = (row % 2 == 0) ? colors.registerBG2 : colors.registerBG1;
      setBackground(bg);
      setForeground(UIManager.getColor("TextField.Foreground"));
      return this;
    }
  }

	private class PriceRenderer extends DefaultTableCellRenderer {
    private static final Border SELECTED_BORDER = new LineBorder(Color.BLUE, 1);
    private static final Border NO_FOCUS_BORDER = new LineBorder(new Color(0, 0, 0, 0), 1);		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
			@SuppressWarnings("unused") Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			int modRow=tableObj.convertRowIndexToModel(row);
			String ticker = (String) ((SecTableModel) table.getModel()).getValueAt(modRow, 1);
			Integer status = dm.getTickerStatus(ticker);
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
			        Color colour = (row %2 ==0 ? colors.registerBG2:colors.registerBG1);
		               setBackground(colour);

			}
      if (isSelected) {
        setBorder(SELECTED_BORDER);
        setOpaque(false);
      } else {
        setBorder(NO_FOCUS_BORDER);
        setOpaque(true);
      }
      setHorizontalAlignment(JLabel.RIGHT);
			return this;
		}
	}
	public class SignColourRenderer extends DefaultTableCellRenderer {
    private static final Border SELECTED_BORDER = new LineBorder(Color.BLUE, 1);
    private static final Border NO_FOCUS_BORDER = new LineBorder(new Color(0, 0, 0, 0), 1);

    public Component setSelectedBorder(DefaultTableCellRenderer renderer, boolean isSelected) {
      if (isSelected) {
        renderer.setBorder(SELECTED_BORDER);
        renderer.setOpaque(false);
      } else {
        renderer.setBorder(NO_FOCUS_BORDER);
        renderer.setOpaque(true);
      }
      return renderer;
    }

		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
			@SuppressWarnings("unused") Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			int modRow=tableObj.convertRowIndexToModel(row);
			String sValue = (String) value;
			SecurityTableLine line = dm.getRowAccount(modRow);
			setHorizontalAlignment(JLabel.RIGHT);
			if (sValue.isEmpty()) {
				setOpaque(true);
				setForeground(UIManager.getColor("TextField.Foreground"));
			      Color colour = (row %2 ==0 ? colors.registerBG2:colors.registerBG1);
		             setBackground(colour);
				return setSelectedBorder(this, isSelected);
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
				setBackground(UIManager.getColor("TextField.Background"));
				return setSelectedBorder(this, isSelected);
			}
			if (dValue < 0.0) {
				setOpaque(true);
				setForeground(Color.BLACK);
				setBackground(Color.RED);
			} else {
				setOpaque(true);
				setForeground(Color.BLACK);
				setBackground(Color.GREEN);
			}
			return setSelectedBorder(this, isSelected);
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
    private static final Border SELECTED_BORDER = new LineBorder(Color.BLUE, 1);
    private static final Border NO_FOCUS_BORDER = new LineBorder(new Color(0, 0, 0, 0), 1);
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
			@SuppressWarnings("unused") Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
			String date = (String) value;
			setForeground(UIManager.getColor("TextField.Foreground"));
 			if (date.endsWith("*"))
				setForeground(Color.RED);
			setHorizontalAlignment(JLabel.RIGHT);
      if (isSelected) {
        setBorder(SELECTED_BORDER);
        setOpaque(false);
      } else {
        setBorder(NO_FOCUS_BORDER);
        setOpaque(true);
      }
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

	public SecTable(Parameters paramsp, SecTableModel dmp) {
		super(dmp);
		dm = dmp;
		tableObj = this;
		trs= new TableRowSorter<SecTableModel>(dm);
		params = paramsp;
		screenHeight = screenSize.getHeight();
		header = getTableHeader();
		header.setReorderingAllowed(false);
		header.setResizingAllowed(true);
		columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME + ".SEC." + Constants.CRNTCOLWIDTH);
		if (columnWidths == null || columnWidths.length == 0) {
			Main.preferences.put(Constants.PROGRAMNAME + ".SEC." + Constants.CRNTCOLWIDTH,
					Constants.DEFAULTCOLWIDTH);
			columnWidths = Constants.DEFAULTCOLWIDTH;
		}
		allSources = new JComboBox<String>(params.getSourceArray());
		currencyEditor = new MyCurrencyEditor(params);
		dateEditor = new MyDateEditor(params);

    rightRender = new DefaultTableCellRenderer() {
      private final Border SELECTED_BORDER = new LineBorder(Color.BLUE, 1);
      private final Border NO_FOCUS_BORDER = new LineBorder(new Color(0, 0, 0, 0), 1);

      @Override
      public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
        super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

        if (isSelected) {
          setBorder(SELECTED_BORDER);
          setOpaque(false);
        } else {
          setBorder(NO_FOCUS_BORDER);
          setOpaque(true);
          Color colour = (row % 2 == 0 ? colors.registerBG2 : colors.registerBG1);
          setBackground(colour);
        }
        setForeground(UIManager.getColor("TextField.Foreground"));
        return this;
      }
    };
		rightRender.setHorizontalAlignment(JLabel.RIGHT);

    borderOnlyRenderer = new BorderOnlyRenderer();
		selectRenderer = new TableCheckBox(this, this.getDefaultRenderer(Boolean.class),
				this.getDefaultRenderer(Object.class));
		/*
		Set up row sorter, if preferences contain saved sequence set up sequnce
		 */
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
						Main.preferences.put(Constants.PROGRAMNAME + ".SEC." + Constants.SORTCOLUMN,colSorter);
					}
				}
			}
		});

		setRowHeight(20);
		this.setFillsViewportHeight(true);
		this.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		this.setCellSelectionEnabled(true);
		this.setRowSelectionAllowed(true);
		this.setDefaultRenderer(MyCheckBox.class, new CheckBoxRenderer());
		this.getColumnModel().addColumnModelListener(new WidthListener());
		this.getTableHeader().addMouseListener(new HeaderMouseListener());
		this.addMouseListener(new TableMouseListener());
		((DefaultTableCellRenderer) this.getTableHeader().getDefaultRenderer())
				.setHorizontalAlignment(JLabel.CENTER);

    // Select column
    TableColumn colSelect = this.getColumnModel().getColumn(selectCol);
    colSelect.setCellEditor(new DefaultCellEditor(boxSelect));
    if (MRBPlatform.isFreeBSD() || MRBPlatform.isUnix())
      colSelect.setCellRenderer(new CheckBoxRenderer());
    colSelect.setCellRenderer(selectRenderer);
    trs.setSortable(selectCol, false);

    for (int col = selectCol; col <= volumeCol; col++) {
      if (col > selectCol) this.getColumnModel().getColumn(col).setResizable(true);
      this.getColumnModel().getColumn(col).setPreferredWidth(columnWidths[col]);
    }

    for (int col : new int[] {tickerCol, altTickerCol, exchangeCol, accountCol, sourceCol}) {
      this.getColumnModel().getColumn(col).setCellRenderer(borderOnlyRenderer);
    }

    for (int col : new int[] {lastPriceCol, tradeCurCol, tradeDateCol, volumeCol}) {
      this.getColumnModel().getColumn(col).setCellRenderer(rightRender);
    }

    for (int col : new int[] {perChangeCol, amtChangeCol}) {
      this.getColumnModel().getColumn(col).setCellRenderer(new SignColourRenderer());
    }

    this.getColumnModel().getColumn(lastDateCol).setCellRenderer(new DateRenderer());
    this.getColumnModel().getColumn(newPriceCol).setCellRenderer(new PriceRenderer());

    for (int col : new int[] {lastPriceCol, newPriceCol, perChangeCol, amtChangeCol}) {
  		trs.setComparator(col, new DoubleComparator());
    }

    this.getColumnModel().getColumn(exchangeCol).setCellEditor(exchangeField);
    this.getColumnModel().getColumn(newPriceCol).setCellEditor(currencyEditor);
    this.getColumnModel().getColumn(tradeDateCol).setCellEditor(dateEditor);

    trs.setComparator(lastDateCol, new DateComparator());
    trs.setComparator(tradeDateCol, new DateComparator());
    trs.setComparator(volumeCol, new IntComparator());

		/*
		 Set up sorter after columns comparators have been set
		 */
		String sortOrder = Main.preferences.getString(Constants.PROGRAMNAME + ".SEC." + Constants.SORTCOLUMN,"");
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
		ActionListener popupListener = aeEvent -> {
      String strAction = aeEvent.getActionCommand();
      if (strAction.contains("Set all to Do Not")) {
        dm.updateAllSources(0);
        return;
      }
      if (strAction.contains("Yahoo HD")) {
        dm.updateAllSources(3);
        return;
      }
      if (strAction.contains("Yahoo + TD")) {
        dm.updateAllSources(5);
        return;
      }
      if (strAction.contains("Yahoo")) {
        dm.updateAllSources(1);
        return;
      }
      if (strAction.contains("FT HD")) {
        dm.updateAllSources(4);
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
      if (strAction.contains("Market Data HD")){
        dm.updateAllSources(7);
        return;
      }
      if (strAction.contains("Market Data")){
        dm.updateAllSources(6);
        return;
      }
      if (strAction.contains("Exclude")) {
        dm.switchDisplay();
        dm.fireTableDataChanged();
        excludeSource.setText("Include 'Do not load'");
      }
      if (strAction.contains("Include")) {
        dm.switchDisplay();
        dm.fireTableDataChanged();
        excludeSource.setText("Exclude 'Do not load'");
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
		sourceFTHD = new JMenuItem();
		sourceFTHD.setText("Set all to FT HD");
		sourcePopup.add(sourceFTHD);
		sourceFTHD.addActionListener(popupListener);
		sourceAlpha = new JMenuItem();
		sourceAlpha.setText("Set all to AlphaVantage HD");
		sourcePopup.add(sourceAlpha);
		sourceAlpha.addActionListener(popupListener);
		sourceMD = new JMenuItem();
		sourceMD.setText("Set all to Market Data");
		sourcePopup.add(sourceMD);
		sourceMD.addActionListener(popupListener);
		sourceMDHD = new JMenuItem();
		sourceMDHD.setText("Set all to Market Data HD");
		sourcePopup.add(sourceMDHD);
		sourceMDHD.addActionListener(popupListener);
		excludeSource= new JMenuItem();
		excludeSource.setText("Exclude 'Do not load'");
		sourcePopup.add(excludeSource);
		excludeSource.addActionListener(popupListener);
	}

	@Override
	public TableCellEditor getCellEditor(int row, int column) {
		{
			int modelColumn = convertColumnIndexToModel(column);
			if (modelColumn == sourceCol) {
        DefaultCellEditor sourceEditor = new DefaultCellEditor(allSources);
        sourceEditor.setClickCountToStart(2);
				return sourceEditor;
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
		debugInst.debug("SecTable", "showPopup", MRBDebug.SUMMARY, "source selected " + iCol);
		if (iCol == sourceCol) {
			sourcePopup.show(header, me.getX(), me.getY());
		}
	}

	private void showExchangePopup(int row, Point p) {
		debugInst.debug("SecTable", "showExchangePopup", MRBDebug.SUMMARY, "displaying exchange popup ");
		String ticker = (String) dm.getValueAt(row, tickerCol);
		if (ticker.contains(Constants.TICKEREXTID))
			return;
		ExchangePopUp popup = new ExchangePopUp(Main.frame, row, params, dm);
		Dimension popupSize = popup.getSize();
		if (p.getY() + popupSize.getHeight() > screenHeight) {
			int dy = (int) Math.round(screenHeight - p.getY() - popupSize.getHeight() - 20);
			p.translate(0, dy);
		}
		popup.setLocation(p);
		popup.setVisible(true);
		getCellEditor(row, exchangeCol).cancelCellEditing();

	}

	private void displayExchangeTicker(int row, int selCol) {
		int modRow = tableObj.convertRowIndexToModel(row);
		debugInst.debug("SecTable", "displayExchangeTicker", MRBDebug.SUMMARY, "on row " + row+"/"+modRow);
		String origticker = (String) dm.getValueAt(modRow, tickerCol);
		String ticker = origticker;
		if (ticker.contains(Constants.TICKEREXTID))
			return;
		String exchange = (String) dm.getValueAt(modRow, exchangeCol);
		String source = (String) dm.getValueAt(modRow, sourceCol);
		String alternate = (String)dm.getValueAt(modRow, altTickerCol);
    	String nameStr = (String)dm.getValueAt(modRow, accountCol);
		int sourceid = 0;
		String tickerSource = "";
		for (int i = 0; i < Constants.SOURCELITS.length; i++) {
			if (source.equals(Constants.SOURCELITS[i])) {
				sourceid = Constants.SOURCELIST[i];
				tickerSource = Constants.SOURCES[i];
				break;
			}
		}
		if (!alternate.isBlank())
			ticker = alternate;
		if (exchange != null && !exchange.isBlank())
			ticker = params.getNewTicker(ticker, exchange, alternate,sourceid);
		Rectangle rect = this.getCellRect(row, selCol, false);
		final String tickerFinal = ticker;
		final String origTickerFinal = origticker;
		final String altTickerFinal = alternate;
		final String nameFinal = nameStr;
		final String sourceFinal = tickerSource;
		final String exchangeFinal = exchange;
		ActionListener tickerListener = aeEvent -> {
      String strAction = aeEvent.getActionCommand();
      if (strAction.equals("get-ticker")) {

SecurityTableLine secLine = dm.getRowAccount(modRow);
final Integer source1 = secLine.getSource();
        if (source1 < 1) {
          JOptionPane.showMessageDialog(Main.frame, "You must select a source before getting a single price");
          return;
        }

Integer lastPriceDate = secLine.getPriceDate();
if (lastPriceDate == null) lastPriceDate = -1;

String tradeCur = null;
if (source1.equals(Constants.ALPHAINDEX)) {
if (secLine.getExchange() != null && !secLine.getExchange().isEmpty()) {
tradeCur = params.getExchangeCurrency(secLine.getExchange());
if (tradeCur == null)
tradeCur = secLine.getRelativeCurrencyType().getIDString();
} else
tradeCur = secLine.getRelativeCurrencyType().getIDString();
} else if (source1.equals(Constants.MDINDEX) || source1.equals(Constants.MDHDINDEX) || source1.equals(Constants.MDMUINDEX)) {
// market data currently only supports US markets and prices are always USD! // todo - monitor this!
if (secLine.getExchange() != null && !secLine.getExchange().isEmpty()) {
tradeCur = params.getExchangeCurrency(secLine.getExchange());
if (tradeCur == null)
tradeCur = "USD";   // default
} else
tradeCur = "USD";     // default
}

String url = "moneydance:fmodule:" + Constants.PROGRAMNAME + ":" +Constants.GETINDIVIDUALCMD +
"?" +
Constants.SOURCETYPE + "=" + sourceFinal +
"&" + Constants.STOCKTYPE + "=" + tickerFinal +
"&" + Constants.ORIGINALTICKER + "=" + origticker +
"&" + Constants.LASTPRICEDATETYPE + "=" + lastPriceDate;

if (tradeCur != null && !tradeCur.isBlank())
url += "&" + Constants.TRADECURRTYPE + "=" + tradeCur;

Main.context.showURL(url);
      }
      if (strAction.equals("copy-derived-ticker-exchange")) {
        StringSelection stringSelection = new StringSelection(tickerFinal);
        Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(stringSelection, null);
      }
      if (strAction.equals("copy-orig-ticker")) {
        StringSelection stringSelection = new StringSelection(origTickerFinal);
        Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(stringSelection, null);
      }
      if (strAction.equals("copy-alt-ticker")) {
        StringSelection stringSelection = new StringSelection(altTickerFinal);
        Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(stringSelection, null);
      }
      if (strAction.equals("copy-name")) {
        StringSelection stringSelection = new StringSelection(nameFinal);
        Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(stringSelection, null);
      }
      if (strAction.equals("set-ex")) {
        dm.selectAllExchanges(exchangeFinal);
        dm.fireTableDataChanged();
      }
    };
		JPopupMenu menu = new JPopupMenu();

		JMenuItem getTickerMenu = new JMenuItem("Get: '" + ticker + "'");
		getTickerMenu.addActionListener(tickerListener);
    getTickerMenu.setActionCommand("get-ticker");

		JMenuItem copyDerivedTickerMenu = new JMenuItem("Copy derived ticker + exchange: '" + ticker + "'");
		copyDerivedTickerMenu.addActionListener(tickerListener);
    copyDerivedTickerMenu.setActionCommand("copy-derived-ticker-exchange");

		JMenuItem copyOrigTickerMenu = new JMenuItem("Copy ticker: '" + origticker + "'");
		copyOrigTickerMenu.addActionListener(tickerListener);
    copyOrigTickerMenu.setActionCommand("copy-orig-ticker");

		JMenuItem copyAltTickerMenu = new JMenuItem("Copy alt ticker: '" + alternate + "'");
		copyAltTickerMenu.addActionListener(tickerListener);
    copyAltTickerMenu.setActionCommand("copy-alt-ticker");

		JMenuItem copyNameMenu = new JMenuItem("Copy name: '" + nameStr + "'");
		copyNameMenu.addActionListener(tickerListener);
    copyNameMenu.setActionCommand("copy-name");

		JMenuItem setAll = new JMenuItem("Set all exchanges to: '" + exchange + "'");
		setAll.addActionListener(tickerListener);
    setAll.setActionCommand("set-ex");

    menu.add(getTickerMenu);

    if (selCol == exchangeCol && !ticker.isBlank())
      menu.add(copyDerivedTickerMenu);

    if (selCol == tickerCol && !origticker.isBlank())
      menu.add(copyOrigTickerMenu);

    if (selCol == altTickerCol && !alternate.isBlank())
      menu.add(copyAltTickerMenu);

    if (selCol == accountCol && !nameStr.isBlank())
      menu.add(copyNameMenu);

    if (selCol == exchangeCol)
      menu.add(setAll);

    menu.show(this, rect.x + (rect.width / 2), rect.y);
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
				debugInst.debug("HeaderMouseListener", "mousePressed", MRBDebug.DebugLevel.DEVELOPER, "width started ");
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

				debugInst.debug("HeaderMouseListener", "mousePressed", MRBDebug.DebugLevel.DEVELOPER, "column " + resizingColumn + " oldWidth " + oldWidth);
			}
		}

		@Override
		public void mouseReleased(MouseEvent e) {
			/* On mouse release, check if column width has changed */
			if (SwingUtilities.isRightMouseButton(e) || e.isControlDown())
				showPopup(e);
			else {
				if (tableObj.getColumnWidthChanged()) {
					debugInst.debug("HeaderMouseListener", "mouseReleased", MRBDebug.DebugLevel.DEVELOPER, "width finished ");
					if (e.getSource() instanceof JTableHeader) {
						TableColumn tc = ((JTableHeader) e.getSource()).getColumnModel().getColumn(resizingColumn);
						if (tc != null) {
							newWidth = tc.getPreferredWidth();
						} else {
							resizingColumn = -1;
							oldWidth = -1;
						}
					}
					debugInst.debug("HeaderMouseListener", "mouseReleased", MRBDebug.DebugLevel.DEVELOPER, "Column " + resizingColumn + "new width " + newWidth);
					columnWidths[resizingColumn] = newWidth;
					Main.preferences.put(Constants.PROGRAMNAME + ".SEC." + Constants.CRNTCOLWIDTH, columnWidths);
					Main.preferences.isDirty();
					// Reset the flag on the table.
					tableObj.setColumnWidthChanged(false);
					debugInst.debug("HeaderMouseListener", "mouseReleased", MRBDebug.DEVELOPER, "column " + resizingColumn + " oldWidth " + oldWidth);

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
      int col = tc.columnAtPoint(p);

      // tell Swing that the row/column have been selected
      if (row >= 0 && col >= 0) {
        tc.setRowSelectionInterval(row, row);
        tc.setColumnSelectionInterval(col, col);
      }

      int selCol = tc.getSelectedColumn();
      int modRow = -1;
      try {
        modRow = tableObj.convertRowIndexToModel(row);
      } catch (IndexOutOfBoundsException error) {
          debugInst.debug("TableMouseListener", "mouseReleased", MRBDebug.INFO, "caught IndexOutOfBoundsException for row: " + row);
        e.consume();
      }

      if (AwtUtil.isPopupTrigger(e)) {
        e.consume();
        displayExchangeTicker(row, selCol);
        return;
      }

			if (selCol == tickerCol) {
				if (e.getClickCount() == 2) {
          e.consume();
					SecurityTableLine acct = dm.getRowAccount(modRow);
					SwingUtilities.invokeLater(new Runnable() {
						@Override
						public void run() {
							Main.context.showURL(
									"moneydance:showobj?id=" + acct.getCurrencyType().getUUID());
						}
					});
				}
			}
      if (selCol == exchangeCol) {
        if (e.getClickCount() == 2) {
          e.consume();
          debugInst.debug("TableMouseListener", "exchange selected", MRBDebug.DebugLevel.DEVELOPER, "column " + exchangeCol + " row " + tc.getSelectedRow() + " mod row " + modRow);
          Rectangle rect = tc.getCellRect(tc.getSelectedRow(), exchangeCol, false);
          Point p2 = new Point(rect.x + rect.width, rect.y + rect.width);
          showExchangePopup(modRow, p2);
        }
      }

      //if (selCol == altTickerCol) {
      //  e.consume();
      //  if (e.getClickCount() == 1 && SwingUtilities.isLeftMouseButton(e)) {
      //    debugInst.debug("TableMouseListener", "altTicker edit triggered", MRBDebug.DebugLevel.DEVELOPER,  "column " + altTickerCol + " row " + tc.getSelectedRow() + " mod row " + modRow);
      //    if (!tc.isEditing()) {
      //      tc.editCellAt(row, col);
      //      Component editor = tc.getEditorComponent();
      //      if (editor != null) editor.requestFocusInWindow();
      //    }
      //  }
      //}

		}
	}
}