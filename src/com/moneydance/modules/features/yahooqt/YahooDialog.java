package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.OKButtonListener;
import com.moneydance.apps.md.view.gui.OKButtonPanel;
import com.moneydance.awt.GridC;
import com.moneydance.util.StringUtils;
import com.moneydance.util.UiUtil;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.DefaultCellEditor;
import javax.swing.DefaultListCellRenderer;
import javax.swing.Icon;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSpinner;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import javax.swing.text.JTextComponent;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagLayout;
import java.awt.Point;
import java.awt.Toolkit;
import java.awt.Window;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.HierarchyEvent;
import java.awt.event.HierarchyListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

public class YahooDialog
  extends JDialog
  implements PropertyChangeListener
{
  private static final String SIZE_KEY = "yahooqt.size";
  private static final String LOCATION_KEY = "yahooqt.location";

  private JPanel contentPane = new JPanel(new BorderLayout(5, 5));
  private JButton _buttonNow;
  private JButton _buttonTest;
  private final JTable _table = new JTable();
  /** This contains data that is edited in the table. */
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private final IExchangeEditor _exchangeEditor = new ExchangeEditor();

  private JCheckBox doQuotesField = new JCheckBox();
  private JCheckBox doRatesField = new JCheckBox();
  private JComboBox _connectionSelect;
  private JSpinner numUnitsField = new JSpinner(new SpinnerNumberModel(1, 1, 50, 1));
  private JComboBox unitField = new JComboBox(TimeUnit.STANDARD_UNITS);
  private ItemListCellRenderer _tableRenderer;
  private ExchangeComboTableColumn _exchangeColumn;
  private JCheckBox _showZeroBalance = new JCheckBox();
  private JLabel _testStatus = new JLabel();
  private boolean _okButtonPressed = false;
  private UseColumnRenderer _useHeaderRenderer;

  public YahooDialog(final FeatureModuleContext context, final ResourceProvider resources,
                     final StockQuotesModel model) {
    super();
    _model = model;
    _model.addPropertyChangeListener(this);
    _resources = resources;
    initUI(context);
    setContentPane(contentPane);
    setModal(true);
    setTitle("Stock Quotes Synchronizer Settings"); // TODO: Translate
    setIconImage(Main.getIcon());
    Dimension size = _model.getPreferences().getSizeSetting(SIZE_KEY);
    if (size.width == 0) {
      pack();
    } else {
      setSize(size);
    }
    Point location = _model.getPreferences().getXYSetting(LOCATION_KEY, -1, -1);
    if (location.x == -1) {
      Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
      location.x = (screenSize.width - getWidth()) / 2;
      location.y = (screenSize.height - getHeight()) / 2;
    }
    setLocation(location);
  }


  @Override
  public void setVisible(boolean visible) {
    if (visible) {
      _model.buildSecurityMap();
      setSecurityTableColumnSizes();
      validate();
    }
    super.setVisible(visible);
  }

  public boolean userAcceptedChanges() { return _okButtonPressed; }

  private void initUI(final FeatureModuleContext context) {
    JPanel fieldPanel = new JPanel(new GridBagLayout());
    fieldPanel.setBorder(BorderFactory.createEmptyBorder(6, 10, 6, 10));
    doQuotesField.setText("Update Stocks"); // TODO: Translate
    doQuotesField.setSelected(_model.getPreferences().getBoolSetting(Main.DOWNLOAD_QUOTES_KEY, true));
    fieldPanel.add(doQuotesField, GridC.getc(1, 0).colspan(2).field());
    doRatesField.setText("Update Exchange Rates"); // TODO: Translate
    fieldPanel.add(doRatesField, GridC.getc(1, 1).colspan(2).field());
    doRatesField.setSelected(_model.getPreferences().getBoolSetting(Main.DOWNLOAD_RATES_KEY, true));
    // pick which URL scheme to connect to 
    setupConnectionSelector();
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.CONNECTION)),
            GridC.getc(0, 2).label());
    fieldPanel.add(_connectionSelect,  GridC.getc(1, 2).field());
    fieldPanel.add(new JLabel("Update Frequency: "), GridC.getc(0, 3).label()); // TODO: Translate
    fieldPanel.add(numUnitsField, GridC.getc(1, 3).field().wx(0));
    fieldPanel.add(unitField, GridC.getc(2, 3).field().wx(0));
    try {
      SimpleFrequency freq = SimpleFrequency.fromString(_model.getPreferences().getSetting(Main.UPDATE_FREQUENCY_KEY, ""));
      numUnitsField.setValue(new Integer(freq.getNumberOfUnits()));
      unitField.setSelectedItem(freq.getUnit());
    } catch (IllegalArgumentException ignored) {
    }

//    fieldPanel.add(new JPanel(), GridC.getc(3, 2).fillx().wx(1.0f)); // spring
//    fieldPanel.add(new JPanel(), GridC.getc(0, 3).filly().wy(1.0f)); // spring
    JScrollPane tableHost = setupSecurityTable();
    fieldPanel.add(tableHost, GridC.getc(0, 4).colspan(3).wxy(1,1).fillboth());
    _showZeroBalance.setText(_model.getGUI().getStr("show_zero_bal_accts"));
    fieldPanel.add(_showZeroBalance, GridC.getc(0, 5).colspan(3).field());
    _testStatus.setHorizontalAlignment(JLabel.CENTER);
    _testStatus.setText(" ");
    fieldPanel.add(_testStatus, GridC.getc(0, 6).colspan(3).field());
    fieldPanel.setBorder(BorderFactory.createEmptyBorder(SQUtil.DLG_VGAP, SQUtil.DLG_HGAP,
            0, SQUtil.DLG_HGAP));
    contentPane.add(fieldPanel, BorderLayout.CENTER);

    _buttonNow = new JButton(_model.getGUI().getStr("update"));
    _buttonTest = new JButton(_resources.getString(L10NStockQuotes.TEST));
    OKButtonPanel okButtons = new OKButtonPanel(_model.getGUI(), new DialogOKButtonListener(),
            OKButtonPanel.QUESTION_OK_CANCEL);
    okButtons.setExtraButtons(new JButton[]{ _buttonTest, _buttonNow } );
    okButtons.setBorder(BorderFactory.createEmptyBorder(SQUtil.VGAP, SQUtil.DLG_HGAP,
            SQUtil.DLG_VGAP, SQUtil.DLG_HGAP));
    contentPane.add(okButtons, BorderLayout.SOUTH);

    addActions(context);
  }

  private void addActions(final FeatureModuleContext context) {
    unitField.setRenderer(new GenericListCellRenderer() {
      protected String getText(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
        if (value instanceof TimeUnit) {
          TimeUnit unit = (TimeUnit) value;
          return numUnitsField.getValue().toString().equals("1") ? unit.getSingularName() : unit.getPluralName();
        } else {
          return super.getText(list, value, index, selected, cellHasFocus);
        }
      }
    });
    numUnitsField.addChangeListener(new ChangeListener() {
      public void stateChanged(ChangeEvent e) {
        unitField.repaint();
      }
    });
    _showZeroBalance.addItemListener(new ItemListener() {
      public void itemStateChanged(ItemEvent e) {
        _model.getTableModel().setShowZeroBalance(e.getStateChange() == ItemEvent.SELECTED);
      }
    });
    _buttonNow.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        // Store what we have in the dialog - same as OK. We need to do this because the main app
        // update is called, which reads these settings from preferences or the data file.
        saveControlsToSettings();
        // listen for events so our status updates just like the main application's
        _model.addPropertyChangeListener(YahooDialog.this);
        // call the main update method
        context.showURL("moneydance:fmodule:yahooqt:update");
      }
    });
    _buttonTest.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        // store what we have into the symbol map
        _model.getTableModel().save();
        // listen for update events
        _model.addPropertyChangeListener(YahooDialog.this);
        _model.runDownloadTest();
      }
    });
  }

  private void setupConnectionSelector() {
    _connectionSelect = new JComboBox(_model.getConnectionList());
    _connectionSelect.setSelectedItem(_model.getSelectedConnection());
    _connectionSelect.addActionListener(new ActionListener()
    {
      public void actionPerformed(ActionEvent e) {
        JComboBox cb = (JComboBox)e.getSource();
        _model.setSelectedConnection((BaseConnection)cb.getSelectedItem());
      }
    });
  }

  private JScrollPane setupSecurityTable() {
    _table.setModel(_model.getTableModel());
    _table.setBorder(BorderFactory.createEmptyBorder(0, UiUtil.HGAP, 0, UiUtil.HGAP));
    JScrollPane host = new JScrollPane(_table, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
            JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

    // consistent row height with other tables in the application
    _table.setRowHeight(_table.getRowHeight() + 8);
    _table.setAutoResizeMode(JTable.AUTO_RESIZE_LAST_COLUMN);
    _table.setRowSelectionAllowed(true);
    _table.setColumnSelectionAllowed(false);
    _table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
    final TableColumnModel columnModel = createColumnModel();
    _table.setColumnModel(columnModel);
    _table.setFillsViewportHeight(true);
    _table.setShowGrid(false);
    final JTableHeader tableHeader = new JTableHeader(columnModel);
    // the only way to get mouse clicks is to attach a listener to the header
    tableHeader.addMouseListener(new MouseAdapter() {
      @Override
      public void mouseClicked(MouseEvent event) {
        final JTableHeader header = (JTableHeader) event.getSource();
        TableColumnModel columnModel = header.getColumnModel();
        int viewColumn = header.columnAtPoint(event.getPoint());
        int column = columnModel.getColumn(viewColumn).getModelIndex();
        if (column == SecuritySymbolTableModel.USE_COL) {
          toggleIncludeAll();
        } else if (column == SecuritySymbolTableModel.EXCHANGE_COL) {
          batchChangeExchange();
        }
      }
    });

    _table.setTableHeader(tableHeader);
    _table.setDefaultRenderer(TableColumn.class, _tableRenderer);
    _table.addMouseListener(new MouseAdapter() {
      @Override
      public void mouseClicked(MouseEvent event) {
        // if the user clicks on a test result cell and there's a tooltip to show, put the tooltip
        // in a message dialog.
        TableColumnModel columnModel = _table.getColumnModel();
        int viewColumn = _table.columnAtPoint(event.getPoint());
        int column = columnModel.getColumn(viewColumn).getModelIndex();
        int row = _table.rowAtPoint(event.getPoint());
        if (column == SecuritySymbolTableModel.TEST_COL) {
          String message = _model.getTableModel().getToolTip(row, SecuritySymbolTableModel.TEST_COL);
          if (!SQUtil.isBlank(message)) {
            JPanel p = new JPanel(new GridBagLayout());
            String symbolTip = _model.getTableModel().getToolTip(row, SecuritySymbolTableModel.SYMBOL_COL);
            p.add(new JLabel(symbolTip), GridC.getc(0, 0));
            p.add(Box.createVerticalStrut(SQUtil.VGAP),  GridC.getc(0, 1));
            p.add(new JLabel(message), GridC.getc(0, 2));
            JOptionPane.showMessageDialog(YahooDialog.this, p);
          }
        }
      }
    });
    return host;
  }

  private void toggleIncludeAll() {
    // determine if any of the 'use' values is false, and if so the action will be to turn all on
    final boolean turnAllOff = _model.getTableModel().allSymbolsEnabled();
    _model.getTableModel().enableAllSymbols(!turnAllOff);
  }

  private void batchChangeExchange() {
    final ExchangeComboTableColumn.ComboListModel comboListModel =
            new ExchangeComboTableColumn.ComboListModel(getExchangeItems());
    final JComboBox exchangeCombo = new JComboBox(comboListModel);
    if (showField(exchangeCombo)) {
      StockExchange selected = (StockExchange)exchangeCombo.getSelectedItem();
      _model.getTableModel().batchChangeExchange(selected);
    }
  }
  private boolean showField(JComponent field) {
    JPanel p = new JPanel(new GridBagLayout());
    final MoneydanceGUI mdGUI = _model.getGUI();
    String msg = mdGUI.getStr("batch_msg");
    String fieldName = "Stock Exchange"; // TODO: translate
    msg = StringUtils.replaceAll(msg, "{field}", fieldName);

    p.add(new JLabel(UiUtil.addLabelSuffix(mdGUI, msg)), GridC.getc(0,0));
    p.add(field, GridC.getc(1,0).wx(1).fillx());
    p.add(Box.createHorizontalStrut(120),  GridC.getc(1,1));

    // Requests focus on the combo box.
    field.addHierarchyListener(new HierarchyListener() {
      public void hierarchyChanged(HierarchyEvent e) {
        final Component c = e.getComponent();
        if (c.isShowing() && (e.getChangeFlags() &
        HierarchyEvent.SHOWING_CHANGED) != 0) {
          Window toplevel = SwingUtilities.getWindowAncestor(c);
          toplevel.addWindowFocusListener(new WindowAdapter() {
            public void windowGainedFocus(WindowEvent e) {
              c.requestFocusInWindow();
            }
          });
        }
      }
    });

    int result = JOptionPane.showConfirmDialog(this, p, mdGUI.getStr("batch_change"),
                                              JOptionPane.OK_CANCEL_OPTION,
                                              JOptionPane.QUESTION_MESSAGE);

    return result==JOptionPane.OK_OPTION;
  }

  private TableColumnModel createColumnModel() {
    final DefaultTableColumnModel columnModel = new DefaultTableColumnModel();
    _tableRenderer = new ItemListCellRenderer(_model.getGUI());

    TableColumn col;
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.USE_COL, 20,
            new UseColumnRenderer(_model.getGUI()), new UseColumnEditor()));
    _useHeaderRenderer = new UseColumnRenderer(_model.getGUI());
    col.setHeaderRenderer(_useHeaderRenderer);
    col.setHeaderValue(" ");
    _useHeaderRenderer.setIsHeaderCell(true);

//    col.getCellEditor().addCellEditorListener(editListener);
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.NAME_COL, 150,
            _tableRenderer, null));
    col.setHeaderValue(_model.getGUI().getStr("curr_type_sec"));
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.SHARES_COL, 40,
            _tableRenderer, null));
    col.setHeaderValue(_model.getGUI().getStr("table_column_shares"));
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.SYMBOL_COL, 40,
                                                _tableRenderer,
                                                new TickerColumnEditor()));
//    col.getCellEditor().addCellEditorListener(editListener);
    col.setHeaderValue(_model.getGUI().getStr("currency_ticker"));

    // the stock exchange picker
    _exchangeColumn = new ExchangeComboTableColumn(_model.getGUI(),
            SecuritySymbolTableModel.EXCHANGE_COL, 60, getExchangeItems(), _exchangeEditor, true);
    columnModel.addColumn(_exchangeColumn);
//    col.getCellEditor().addCellEditorListener(editListener);
    _exchangeColumn.setHeaderValue("Stock Exchange"); // TODO translate
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.TEST_COL, 40,
            _tableRenderer, null));
    col.setHeaderValue("Test Result"); // TODO translate

    return columnModel;
  }

  private StockExchange[] getExchangeItems() {
    // find all of the stock exchange items that have a symbol for the currently selected
    // stock quotes connection
    BaseConnection connection = (BaseConnection)_connectionSelect.getSelectedItem();
    if (connection == null) connection = _model.getSelectedConnection();
    if (connection == null) return new StockExchange[0];
    List<StockExchange> items = new ArrayList<StockExchange>();
    // TODO translate name
    items.add(StockExchange.DEFAULT);
    final CurrencyTable ctable = _model.getRootAccount().getCurrencyTable();
    for (StockExchange exchange : _model.getExchangeList().getFullList()) {
      if (isValidExchange(ctable, exchange)) items.add(exchange);
    }
    return items.toArray(new StockExchange[items.size()]);
  }

  /**
   * Determine if we should show an exchange or not, depending upon whether the currency for that
   * exchange is defined in the data file or not.
   * @param ctable   The currency table from the data file.
   * @param exchange The stock exchange to test.
   * @return True if the stock exchange can be used, false if the currency does not exist.
   */
  private static boolean isValidExchange(CurrencyTable ctable, StockExchange exchange) {
    final String currencyId = exchange.getCurrencyCode();
    return (ctable.getCurrencyByIDString(currencyId) != null);
  }

  /**
   * Define the table column sizes according to the data in them.
   */
  private void setSecurityTableColumnSizes()
  {
    if ((_model.getTableModel() == null) || (_model.getTableModel().getRowCount() == 0)) return; // nothing to do
    // find the maximum width of the columns
    int[] widths = new int[_model.getTableModel().getColumnCount()];
    for (int column = 0; column < _model.getTableModel().getColumnCount(); column++) {
      for (int row = 0; row < _table.getRowCount(); row++) {
        TableCellRenderer renderer = _table.getCellRenderer(row, column);
        Component comp = renderer.getTableCellRendererComponent(_table,
                _table.getValueAt(row, column), false, false, row, column);
        widths[column] = Math.max(widths[column], comp.getPreferredSize().width);
        if ((row == 0) && (column > 0)) {
          // include the header text too, but only for columns other than 'use'
          comp = renderer.getTableCellRendererComponent(_table, _model.getTableModel().getColumnName(column),
                  false, false, row, column);
          widths[column] = Math.max(widths[column], comp.getPreferredSize().width);
        }
      }
    }
    // set the last column to be as big as the biggest column - all extra space should be given to
    // the last column
    int maxWidth = 0;
    for (int width1 : widths) maxWidth = Math.max(width1, maxWidth);
    widths[SecuritySymbolTableModel.TEST_COL] = maxWidth;

//    _model.getTableModel().computeColumnWidths(fm, graphics, widths);
//    widths[0] = 20;
    final TableColumnModel columnModel = _table.getColumnModel();
    for (int column = 0; column < widths.length; column++) {
      columnModel.getColumn(column).setPreferredWidth(widths[column]);
    }
  }

  private void onOK() {
    saveControlsToSettings();

    _okButtonPressed = true;
    dispose();
  }

  private void saveControlsToSettings() {
    // these are stored in preferences and are not file-specific
    UserPreferences prefs = _model.getPreferences();
    prefs.setSetting(Main.AUTO_UPDATE_KEY, doQuotesField.isSelected() || doRatesField.isSelected());
    prefs.setSetting(Main.DOWNLOAD_QUOTES_KEY, doQuotesField.isSelected());
    prefs.setSetting(Main.DOWNLOAD_RATES_KEY, doRatesField.isSelected());
    TimeUnit unit = (TimeUnit) unitField.getSelectedItem();
    int num = ((Number) numUnitsField.getValue()).intValue();
    SimpleFrequency freq = new SimpleFrequency(unit, num);
    prefs.setSetting(Main.UPDATE_FREQUENCY_KEY, freq.toString());
    // check if any of the settings that are stored in the specific data file have been changed
    if (_model.isDirty()) {
      _model.saveSettings();
      // mark that we made changes to the file
      _model.getRootAccount().accountModified(_model.getRootAccount());
    }
  }

  public void dispose() {
    _model.removePropertyChangeListener(this);
    _model.getPreferences().setXYSetting(LOCATION_KEY, getLocation());
    _model.getPreferences().setSizeSetting(SIZE_KEY, getSize());
    super.dispose();
  }

  public void propertyChange(PropertyChangeEvent event) {
    final String name = event.getPropertyName();
    if (N12EStockQuotes.STATUS_UPDATE.equals(name)) {
      final String status = (String) event.getNewValue();
      _testStatus.setText(status == null ? " " : status);
    } else if (N12EStockQuotes.DOWNLOAD_BEGIN.equals(name)) {
      final String text = _model.getGUI().getStr(L10NStockQuotes.CANCEL);
      SQUtil.runOnUIThread(new Runnable() {
        public void run() {
          _buttonTest.setText(text);
        }
      });
    } else if (N12EStockQuotes.DOWNLOAD_END.equals(name)) {
      final String text = _resources.getString(L10NStockQuotes.TEST);
      SQUtil.runOnUIThread(new Runnable() {
        public void run() {
          _buttonTest.setText(text);
        }
      });
      // we're done listening for results
      _model.removePropertyChangeListener(this);
    } else if (N12EStockQuotes.HEADER_UPDATE.equals(name)) {
      _table.getTableHeader().repaint();
    }

  }

  public static class GenericListCellRenderer extends DefaultListCellRenderer {
    public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
      setComponentOrientation(list.getComponentOrientation());
      setBackground(getBackground(list, value, index, isSelected, cellHasFocus));
      setForeground(getForeground(list, value, index, isSelected, cellHasFocus));
      setIcon(getIcon(list, value, index, isSelected, cellHasFocus));
      setText(getText(list, value, index, isSelected, cellHasFocus));
      setEnabled(isEnabled(list, value, index, isSelected, cellHasFocus));
      setFont(getFont(list, value, index, isSelected, cellHasFocus));
      setBorder(getBorder(list, value, index, isSelected, cellHasFocus));
      return this;
    }

    protected String getText(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return value instanceof Icon || value == null ? "" : value.toString();
    }

    protected Icon getIcon(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return value instanceof Icon ? (Icon) value : null;
    }

    protected Border getBorder(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return cellHasFocus ? UIManager.getBorder("List.focusCellHighlightBorder") : noFocusBorder;
    }

    protected Font getFont(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return list.getFont();
    }

    protected boolean isEnabled(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return list.isEnabled();
    }

    protected Color getBackground(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return selected ? list.getSelectionBackground() : list.getBackground();
    }

    protected Color getForeground(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return selected ? list.getSelectionForeground() : list.getForeground();
    }
  }

  private static class UseColumnRenderer extends JCheckBox implements TableCellRenderer {
    private static final Border noFocusBorder = new EmptyBorder(1, 1, 1, 1);
    private final MoneydanceGUI _mdGui;
    private boolean _isHeaderCell = false;

    public UseColumnRenderer(final MoneydanceGUI mdGui) {
      super();
      _mdGui = mdGui;
      setHorizontalAlignment(JLabel.CENTER);
      setBorderPainted(true);
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus, int row, int column) {
      if (_isHeaderCell) {
        final JTableHeader header = table.getTableHeader();
        if (header != null) {
          setForeground(header.getForeground());
          setBackground(header.getBackground());
          setFont(header.getFont());
        }
        setBorder(UIManager.getBorder("TableHeader.cellBorder"));
        setSelected(((SecuritySymbolTableModel)table.getModel()).allSymbolsEnabled());
      } else {
        if (isSelected) {
          setForeground(table.getSelectionForeground());
          setBackground(table.getSelectionBackground());
        } else {
          setForeground(table.getForeground());
          if (row % 2 == 0) {
            setBackground(_mdGui.getColors().homePageBG);
          } else {
            setBackground(_mdGui.getColors().homePageAltBG);
          }
        }
        setSelected((value instanceof Boolean) && ((Boolean) value).booleanValue());
        if (hasFocus) {
          setBorder(UIManager.getBorder("Table.focusCellHighlightBorder"));
        } else {
          setBorder(noFocusBorder);
        }
      }
      return this;
    }

    void setIsHeaderCell(boolean isHeader) {
      _isHeaderCell = isHeader;
    }
  }

  private static class UseColumnEditor extends DefaultCellEditor {
    public UseColumnEditor() {
      super(new JCheckBox());
      JCheckBox checkBox = (JCheckBox) getComponent();
      checkBox.setHorizontalAlignment(JCheckBox.CENTER);
    }
  }

  /**
   * Cell renderer for the list, colors items that are in-use.
   */
  private class ItemListCellRenderer extends DefaultTableCellRenderer {
    private final MoneydanceGUI _mdGui;

    ItemListCellRenderer(final MoneydanceGUI mdGui) {
      _mdGui = mdGui;
    }

    /**
     * Returns the default table cell renderer.
     *
     * @param table      the <code>JTable</code>
     * @param value      the value to assign to the cell at
     *                   <code>[row, column]</code>
     * @param isSelected true if cell is selected
     * @param hasFocus   true if cell has focus
     * @param row        the row of the cell to render
     * @param column     the column of the cell to render
     * @return the default table cell renderer
     */
    @Override
    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus,
                                                   int row, int column) {
      JComponent result = (JComponent) super.getTableCellRendererComponent(table, value,
              isSelected, hasFocus, row, column);

      // the unselected background alternates color for ease of distinction
      if (!isSelected) {
        if (row % 2 == 0) {
          setBackground(_mdGui.getColors().homePageBG);
        } else {
          setBackground(_mdGui.getColors().homePageAltBG);
        }
      }

      // in case the text is cut off, show complete text in a tool tip
      if ((column == SecuritySymbolTableModel.SYMBOL_COL) ||
              (column == SecuritySymbolTableModel.TEST_COL)) {
        result.setToolTipText(_model.getTableModel().getToolTip(row, column));
      }
      else if (value instanceof String) {
        result.setToolTipText((String)value);
      }

      return result;
    }

  }

  /**
   * Cell editor for in-place editing
   */
  private class TickerColumnEditor extends DefaultCellEditor {
    private String _value;

    public TickerColumnEditor() {
      super(new JTextField());
      getComponent().setName("Table.editor");
    }

    @Override
    public boolean stopCellEditing() {
      _value = (String) super.getCellEditorValue();
      return super.stopCellEditing();
    }

    @Override
    public Component getTableCellEditorComponent(JTable table, Object value,
                                                 boolean isSelected,
                                                 int row, int column) {
      _value = null;
      JTextField editor = (JTextField) super.getTableCellEditorComponent(table, value,
              isSelected, row, column);
      editor.requestFocusInWindow();
      editor.selectAll();
      return editor;
    }

    @Override
    public Object getCellEditorValue() {
      return _value;
    }

    String getEditedText() {
      return _value;
    }
  }


  private class DialogOKButtonListener implements OKButtonListener {
    public void buttonPressed(int buttonId) {
      if (buttonId == OKButtonPanel.ANSWER_OK) {
        onOK();
      } else {
        dispose();
      }
    }
  }

  private class ExchangeEditor implements IExchangeEditor {

    public boolean edit(final StockExchange exchange) {
      final MoneydanceGUI mdGui = _model.getGUI();
      if (StockExchange.DEFAULT.equals(exchange)) {
        // not editable
        final String message = _resources.getString(L10NStockQuotes.ERROR_DEFAULT_NOT_EDITABLE);
        SwingUtilities.invokeLater(new Runnable() {
          public void run() {
            mdGui.showErrorMessage(message);
          }
        });
        return false;
      }
      final StockExchangeList exchangeList = _model.getExchangeList();
      final JDialog owner = YahooDialog.this;
      SwingUtilities.invokeLater(new Runnable() {
        public void run() {
          ExchangeDialog dialog = new ExchangeDialog(owner, mdGui, _resources, exchange,
                  exchangeList);
          dialog.setVisible(true);
        }
      });
      return true;
    }
  }
}
