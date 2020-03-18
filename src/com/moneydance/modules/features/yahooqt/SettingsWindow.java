/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.controller.Util;
import com.moneydance.apps.md.controller.time.TimeInterval;
import com.moneydance.apps.md.view.gui.MDColors;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.OKButtonListener;
import com.moneydance.apps.md.view.gui.OKButtonPanel;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.util.UiUtil;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.HyperlinkListener;
import javax.swing.event.MouseInputAdapter;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import java.awt.*;
import java.awt.event.*;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;

/**
 * Main settings configuration dialog for the quotes and rates updater extension
 */
public class SettingsWindow
  extends JDialog
  implements PropertyChangeListener
{
  private final JPanel contentPane = new JPanel(new BorderLayout(5, 5));
  private final JTable _table = new JTable();
  /** This contains the table model as well as other data that is edited in this dialog. */
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private final IExchangeEditor _exchangeEditor = new ExchangeEditor();
  private FeatureModuleContext context;
  
  private JComboBox<BaseConnection> _historyConnectionSelect;
  private JComboBox<BaseConnection> _ratesConnectionSelect;
  private Action setAPIKeyAction;
  private Action downloadAction;
  private Action testAction;
  private JButton testButton;
  private JButton _apiKeyButton;
  
  private IntervalChooser _intervalSelect;
  private JDateField _nextDate;
  private JLabel _showTestLabel = new JLabel();
  private TableColumn _testColumn = null;
  private boolean _showingTestInfo = false;
  private ItemListCellRenderer _tableRenderer;
  private final JCheckBox _showOwnedOnly = new JCheckBox();
  private final JEditorPane statusSummaryPanel = new JEditorPane();
  private boolean _okButtonPressed = false;

  public SettingsWindow(final FeatureModuleContext context, final ResourceProvider resources,
                        final StockQuotesModel model) {
    super();
    this.context = context;
    
    _model = model;
    _model.addPropertyChangeListener(this);
    _resources = resources;
    initUI(context);
    setContentPane(contentPane);
    setModal(true);
    setTitle(resources.getString(L10NStockQuotes.SETTINGS_TITLE));
//    setIconImage(Main.getIcon()); // available in Java 1.6 only
    Dimension size = _model.getPreferences().getSizeSetting(N12EStockQuotes.SIZE_KEY);
    if (size.width == 0) {
      pack();
    } else {
      setSize(size);
    }
    Point location = _model.getPreferences().getXYSetting(N12EStockQuotes.LOCATION_KEY, -1, -1);
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
      // display the last update date in the test status area
      updateStatusBlurb();
      validate();
    }
    super.setVisible(visible);
  }
  
  public boolean userAcceptedChanges() { return _okButtonPressed; }
  
  private void initUI(final FeatureModuleContext context) {
    JPanel fieldPanel = new JPanel(new GridBagLayout());
    fieldPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.DLG_VGAP, UiUtil.DLG_HGAP,
                                                         UiUtil.DLG_VGAP, UiUtil.DLG_HGAP));
    // pick which URL schemes to connect to (or no connection to disable the download)
    // stock historical quotes
    _historyConnectionSelect = new JComboBox<>(_model.getConnectionList(BaseConnection.HISTORY_SUPPORT));
    _historyConnectionSelect.setSelectedItem(_model.getSelectedHistoryConnection());
    _historyConnectionSelect.addItemListener(new ItemListener() {
		public void itemStateChanged(ItemEvent arg0)
		{
			BaseConnection bc = (BaseConnection) _historyConnectionSelect.getModel().getSelectedItem();
			if (bc instanceof APIKeyConnection)
			{
				_apiKeyButton.setVisible(true);
			}
			else
			{
				_apiKeyButton.setVisible(false);
			}
		}
	});
    // currency exchange rates
    _ratesConnectionSelect = new JComboBox<>(_model.getConnectionList(BaseConnection.EXCHANGE_RATES_SUPPORT));
    _ratesConnectionSelect.setSelectedItem(_model.getSelectedExchangeRatesConnection());

    
    setAPIKeyAction = new AbstractAction() {
      @Override
      public void actionPerformed(ActionEvent e)
	  {
	  	BaseConnection bc = (BaseConnection) _historyConnectionSelect.getModel().getSelectedItem();
	  	if (bc instanceof  APIKeyConnection)
		{
			((APIKeyConnection) bc).getAPIKey(_model, true);
		}
      }
    };
    setAPIKeyAction.putValue(Action.NAME, _resources.getString(L10NStockQuotes.SET_API_KEY));

    downloadAction = new AbstractAction() {
      @Override
      public void actionPerformed(ActionEvent e) {
        // Store what we have in the dialog - same as OK. We need to do this because the main app
        // update is called, which reads these settings from preferences or the data file.
        saveControlsToSettings();
        // listen for events so our status updates just like the main application's
        _model.addPropertyChangeListener(SettingsWindow.this);
        // call the main update method
        context.showURL("moneydance:fmodule:yahooqt:update");
      }
    };

    statusSummaryPanel.setEditable(false);
    statusSummaryPanel.addHyperlinkListener(new HyperlinkListener() {
      @Override
      public void hyperlinkUpdate(HyperlinkEvent event) {
        if (event.getEventType() == HyperlinkEvent.EventType.ACTIVATED &&
            event.getURL() != null) {
          if (java.awt.Desktop.isDesktopSupported()) {
            try {
              java.awt.Desktop.getDesktop().browse(event.getURL().toURI());
            } catch (Exception ex) {
              System.err.println("Error opening URL " + ex);
            }
          }
        }
      }
    });


    testAction = new AbstractAction() {
      @Override
      public void actionPerformed(ActionEvent e) {
        Account root = _model.getRootAccount();
        if(root==null) return;

        // save the selected connections into our model
        saveSelectedConnections();
        // store what we have into the symbol map
        _model.getTableModel().save(root);
        // listen for update events
        _model.addPropertyChangeListener(SettingsWindow.this);
        _model.runDownloadTest();
      }
    };
    testAction.putValue(Action.NAME, _resources.getString(L10NStockQuotes.TEST));
    
    downloadAction.putValue(Action.NAME,_resources.getString(L10NStockQuotes.UPDATE_NOW));
    
    _intervalSelect = new IntervalChooser(_model.getGUI());
    final String paramStr = _model.getPreferences().getSetting(Main.UPDATE_INTERVAL_KEY, "");
    _intervalSelect.selectFromParams(paramStr);
    _nextDate = new JDateField(_model.getPreferences().getShortDateFormatter());
    loadNextDate();
    
    // first column
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.RATES_CONNECTION)),
                   GridC.getc(0, 0).label());
    fieldPanel.add(_ratesConnectionSelect,   GridC.getc(1, 0).field());
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.SECURITIES_CONNECTION)),
                   GridC.getc(0, 1).label());
    fieldPanel.add(_historyConnectionSelect, GridC.getc(1, 1).field());
    
    _apiKeyButton = new JButton(setAPIKeyAction);
    fieldPanel.add(_apiKeyButton, GridC.getc(1, 2).field());
    
    // gap in middle
    fieldPanel.add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), GridC.getc(2, 0));
    
    
    // second column
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.FREQUENCY_LABEL)),
                   GridC.getc(3, 0).label());
    fieldPanel.add(_intervalSelect, GridC.getc(4, 0).field());
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.NEXT_DATE_LABEL)),
                   GridC.getc(3, 1).label());
    fieldPanel.add(_nextDate, GridC.getc(4, 1).field());
    _showTestLabel.setHorizontalAlignment(JLabel.RIGHT);
    // add the toggle for the testing mode on/off
    final JPanel testPanel = new JPanel(new BorderLayout());
    testPanel.add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), BorderLayout.CENTER);
    testPanel.add(_showTestLabel, BorderLayout.EAST);
    fieldPanel.add(testPanel, GridC.getc(4, 2).field().east());
    // gap between the fields and the table
    fieldPanel.add(Box.createVerticalStrut(UiUtil.VGAP), GridC.getc(0, 3));
    // setup the table
    JScrollPane tableHost = setupSecurityTable();
    fieldPanel.add(tableHost, GridC.getc(0, 4).colspan(5).wxy(1,1).fillboth());
    _showOwnedOnly.setText(_resources.getString(L10NStockQuotes.SHOW_OWNED));
    _showOwnedOnly.setSelected(!_model.getTableModel().getShowZeroBalance());
    fieldPanel.add(_showOwnedOnly, GridC.getc(0, 5).colspan(5).field());
    statusSummaryPanel.setText(" ");
    fieldPanel.add(statusSummaryPanel, GridC.getc(0, 6).colspan(5).field());
    fieldPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.DLG_VGAP, UiUtil.DLG_HGAP,
                                                         0, UiUtil.DLG_HGAP));
    contentPane.add(fieldPanel, BorderLayout.CENTER);
    // buttons at bottom
    testButton = new JButton(testAction);
    testButton.setVisible(_showingTestInfo);
    JPanel extraButtonPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, UiUtil.HGAP, UiUtil.VGAP));
    extraButtonPanel.add(testButton);
    extraButtonPanel.add(new JButton(downloadAction));
    
    // the built-in OK/Cancel buttons
    OKButtonPanel okButtons = new OKButtonPanel(_model.getGUI(), new DialogOKButtonListener(),
                                                OKButtonPanel.QUESTION_OK_CANCEL);
    JPanel bottomPanel = new JPanel(new BorderLayout());
    bottomPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.DLG_HGAP,
                                                          UiUtil.DLG_VGAP, UiUtil.DLG_HGAP));
    bottomPanel.add(extraButtonPanel, BorderLayout.WEST);
    bottomPanel.add(okButtons, BorderLayout.CENTER);
    contentPane.add(bottomPanel, BorderLayout.SOUTH);
    setupTestControls();
    // setup actions for the controls
    addActions(context);
  }

  private void setupTestControls() {
    if (_showingTestInfo) {
      _showTestLabel.setText(_resources.getString(L10NStockQuotes.BASIC));
      _showTestLabel.setToolTipText(_resources.getString(L10NStockQuotes.HIDE_TEST));
      testButton.setVisible(true);
      _table.getColumnModel().addColumn(_testColumn);
    } else {
      _showTestLabel.setText(_resources.getString(L10NStockQuotes.ADVANCED));
      _showTestLabel.setToolTipText(_resources.getString(L10NStockQuotes.SHOW_TEST));
      testButton.setVisible(false);
      _table.getColumnModel().removeColumn(_testColumn);
    }
  }
  

  private void updateStatusBlurb() {
    StringBuilder msg = new StringBuilder("<html><body style=\"text-align:center; font: sans;\">");
    if (_model.getRootAccount() != null) {
      String messageFormat = _resources.getString(L10NStockQuotes.LAST_UPDATE_FMT);
      int lastRateDate = _model.getRatesLastUpdateDate();
      String rateText = getDateText(lastRateDate);
      int lastQuoteDate = _model.getQuotesLastUpdateDate();
      String quoteText = getDateText(lastQuoteDate);
      msg.append("<p>").append(MessageFormat.format(messageFormat, rateText, quoteText)).append("</p>");
    }
    BaseConnection securityConn = _model.getSelectedHistoryConnection();
    if(securityConn!=null && securityConn instanceof IEXConnection) {
      msg.append("<p>Data provided for free by IEX. View IEX’s <a href=\"https://iextrading.com/api-exhibit-a\">Terms of Use.</a></p>");
    }
    msg.append("</body></html>");
    
    statusSummaryPanel.setContentType("text/html");
    statusSummaryPanel.setText(msg.toString());
  }

  private String getDateText(final int date) {
    if (date <= 0) {
      return _resources.getString(L10NStockQuotes.NEVER);
    }
    return _model.getPreferences().getShortDateFormatter().format(date);
  }
  
  private void addActions(final FeatureModuleContext context) {
    _showOwnedOnly.addItemListener(new ItemListener() {
      public void itemStateChanged(ItemEvent e) {
        // show zero balance only if 'show only that I own' is deselected
        _model.getTableModel().setShowZeroBalance(e.getStateChange() == ItemEvent.DESELECTED);
      }
    });
    final MouseInputAdapter mouseInputListener = new MouseInputAdapter() {
      @Override
      public void mouseClicked(MouseEvent e) {
        if (SwingUtilities.isLeftMouseButton(e)) {
          _showingTestInfo = !_showingTestInfo;
          if (_showingTestInfo) {
            // update the currency and other status messages with the latest edits
            _model.getTableModel().scanForSymbolOverrides();
          }
          setupTestControls();
          setSecurityTableColumnSizes();
          validate();
        }
      }
      @Override
      public void mouseEntered(MouseEvent event) {
        setCursor(new Cursor(Cursor.HAND_CURSOR));
      }
      @Override
      public void mouseExited(MouseEvent event) {
        setCursor(new Cursor(Cursor.DEFAULT_CURSOR));
      }
    };
    _showTestLabel.addMouseListener(mouseInputListener);
    _showTestLabel.addMouseMotionListener(mouseInputListener);
  }

  private void loadNextDate() {
    int lastDate = _model.getRootAccount().getIntParameter(Main.QUOTE_LAST_UPDATE_KEY, 0);
    final int nextDate;
    if (lastDate == 0) {
      nextDate = Util.getStrippedDateInt(); // today
    } else {
      TimeInterval frequency = Main.getUpdateFrequency(_model.getPreferences());
      nextDate = SQUtil.getNextDate(lastDate, frequency);
    }
    _nextDate.setDateInt(nextDate);
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
    _table.setDragEnabled(false);
//    _table.setFillsViewportHeight(true); // available in Java 1.6 only
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
          // we know the renderer for this column is a JComponent
          showIncludeMenu(header);
        } else if (column == SecuritySymbolTableModel.EXCHANGE_COL) {
          batchChangeExchange();
        }
      }
    });
    tableHeader.setReorderingAllowed(false);
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
            p.add(Box.createVerticalStrut(UiUtil.VGAP),  GridC.getc(0, 1));
            p.add(new JLabel(message), GridC.getc(0, 2));
            JOptionPane.showMessageDialog(SettingsWindow.this, p);
          }
        } else if ((column == SecuritySymbolTableModel.EXCHANGE_COL) &&
                SwingUtilities.isRightMouseButton(event)) {
          // edit the exchange
          showExchangeEditDialog(row);
        }
      }
    });
    // add hot key
    _table.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_E,
            MoneydanceGUI.ACCELERATOR_MASK), "editExchange");
    _table.getActionMap().put("editExchange", new AbstractAction() {
      public void actionPerformed(final ActionEvent event) {
        final int selectedRow = _table.getSelectedRow();
        if (selectedRow >= 0) {
          showExchangeEditDialog(selectedRow);
        }
      }
    });
    return host;
  }

  private void showExchangeEditDialog(final int row) {
    final StockExchange exchange = (StockExchange)_model.getTableModel().getValueAt(
            row, SecuritySymbolTableModel.EXCHANGE_COL);
    _exchangeEditor.edit(exchange);
  }

  private void includeAll(final boolean include) {
    _model.getTableModel().enableAllSymbols(include);
    _table.getTableHeader().repaint();
  }

  private void showIncludeMenu(final JComponent parent) {
    JPopupMenu menu = new JPopupMenu();
    JMenuItem menuItem = new JMenuItem(_model.getGUI().getStr("accountfilter.all"));
    menuItem.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        includeAll(true);
      }
    });
    menu.add(menuItem);
    menuItem = new JMenuItem(_model.getGUI().getStr("none"));
    menuItem.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        includeAll(false);
      }
    });
    menu.add(menuItem);
    menu.show(parent, 0, parent.getHeight());
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
    String fieldName = _resources.getString(L10NStockQuotes.EXCHANGE_TITLE);
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

    // select security for download column
    TableColumn col;
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.USE_COL, 20,
            new UseColumnRenderer(_model.getGUI()), new UseColumnEditor()));
    // special renderer allows the header to act like a checkbox to select all / deselect all
    UseColumnHeaderRenderer useHeaderRenderer = new UseColumnHeaderRenderer();
    col.setHeaderRenderer(useHeaderRenderer);
    col.setHeaderValue(" ");

    // name and number of shares
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.NAME_COL, 150,
												new SecurityNameCellRenderer(_model.getGUI()), null));
    col.setHeaderValue(_model.getGUI().getStr("curr_type_sec"));
    columnModel.addColumn(col = new TableColumn(SecuritySymbolTableModel.SYMBOL_COL, 40,
                                                _tableRenderer,
                                                new TickerColumnEditor()));
    col.setHeaderValue(_model.getGUI().getStr("currency_ticker"));

    // the stock exchange picker
    ExchangeComboTableColumn exchangeColumn =
            new ExchangeComboTableColumn(_model.getGUI(),
                                         SecuritySymbolTableModel.EXCHANGE_COL, 60,
                                         getExchangeItems(), _exchangeEditor);
    columnModel.addColumn(exchangeColumn);
    exchangeColumn.setHeaderValue(_resources.getString(L10NStockQuotes.EXCHANGE_TITLE));
    // testing column
    _testColumn = new TableColumn(SecuritySymbolTableModel.TEST_COL, 40, _tableRenderer, null);
    if (_showingTestInfo) {
      columnModel.addColumn(_testColumn);
    }
    _testColumn.setHeaderValue(_resources.getString(L10NStockQuotes.TEST_TITLE));

    return columnModel;
  }

  private StockExchange[] getExchangeItems() {
    // set the name to a displayable localized string
    StockExchange.DEFAULT.setName(_model.getGUI().getStr("default"));
    // find all of the stock exchange items that have a currency that exists in the data file
    List<StockExchange> items = new ArrayList<StockExchange>();
    items.add(StockExchange.DEFAULT);
    final CurrencyTable ctable = _model.getBook().getCurrencies();
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
    // find the maximum width of the columns - there may be more columns in the model than in the view
    final int viewColumnCount = _table.getColumnModel().getColumnCount();
    int[] widths = new int[viewColumnCount];
    for (int column = 0; column < viewColumnCount; column++) {
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
    widths[viewColumnCount - 1] = maxWidth;
    final TableColumnModel columnModel = _table.getColumnModel();
    for (int column = 0; column < widths.length; column++) {
      columnModel.getColumn(column).setPreferredWidth(widths[column]);
    }
  }

  private void onOK() {
    saveControlsToSettings();
    
    _okButtonPressed = true;
    setVisible(false);
    
    context.showURL("moneydance:fmodule:yahooqt:update"); // kick off an update, if needed
  }
  
  private void saveControlsToSettings() {
    Account root = _model.getRootAccount();
    if (root == null) return;
    
    saveSelectedConnections();
    
    // these are stored in preferences and are not file-specific
    UserPreferences prefs = _model.getPreferences();
    prefs.setSetting(Main.AUTO_UPDATE_KEY, isAnyConnectionSelected());
    prefs.setSetting(Main.UPDATE_INTERVAL_KEY, _intervalSelect.getSelectedInterval().getConfigKey());
    
    // save the date of the next update
    int nextDate = _nextDate.getDateInt();
    
    // work backwards to get the calculated 'last update date'
    TimeInterval frequency = _intervalSelect.getSelectedInterval();
    _model.setHistoryDaysFromFrequency(frequency);
    int lastDate = SQUtil.getPreviousDate(nextDate, frequency);
    int currentQuoteDate = _model.getQuotesLastUpdateDate();
    
    if (_model.isStockPriceSelected() && (currentQuoteDate != lastDate)) {
      if(Main.DEBUG_YAHOOQT) {
        System.err.println("Changing last quote update date from " +
                           currentQuoteDate + " to " + lastDate + " per user selection");
      }
      _model.saveLastQuoteUpdateDate(lastDate);
    }
    int currentRatesDate = _model.getRatesLastUpdateDate();
    if (_model.isExchangeRateSelected() && (currentRatesDate != lastDate)) {
      if(Main.DEBUG_YAHOOQT) {
        System.err.println("Changing last exchange rates update date from " +
                           currentRatesDate + " to " + lastDate + " per user selection");
      }
      _model.saveLastExchangeRatesUpdateDate(lastDate);
    }




    // check if any of the settings that are stored in the specific data file have been changed
    if (_model.isDirty()) {
      _model.saveSettings(root);
    }
  }

  private void saveSelectedConnections() {
    _model.setSelectedHistoryConnection((BaseConnection)_historyConnectionSelect.getSelectedItem());
    _model.setSelectedExchangeRatesConnection((BaseConnection)_ratesConnectionSelect.getSelectedItem());
  }

  private boolean isAnyConnectionSelected() {
    return _model.isStockPriceSelected() || _model.isExchangeRateSelected();
  }

  public void dispose() {
    _model.removePropertyChangeListener(this);
    _model.getPreferences().setXYSetting(N12EStockQuotes.LOCATION_KEY, getLocation());
    _model.getPreferences().setSizeSetting(N12EStockQuotes.SIZE_KEY, getSize());
    super.dispose();
  }

  public void propertyChange(PropertyChangeEvent event) {
    final String name = event.getPropertyName();
    if (N12EStockQuotes.STATUS_UPDATE.equals(name)) {
      final String status = (String) event.getNewValue();
      statusSummaryPanel.setText(status == null ? " " : status);
    } else if (N12EStockQuotes.DOWNLOAD_BEGIN.equals(name)) {
      final String text = _model.getGUI().getStr("cancel");
      UiUtil.runOnUIThread(new Runnable() {
        public void run() {
          testAction.putValue(Action.NAME, text);
        }
      });
    } else if (N12EStockQuotes.DOWNLOAD_END.equals(name)) {
      final String text = _resources.getString(L10NStockQuotes.TEST);
      UiUtil.runOnUIThread(new Runnable() {
        public void run() {
          testAction.putValue(Action.NAME, text);
          // the next update date may have changed now
          loadNextDate();
        }
      });
      // we're done listening for results
      _model.removePropertyChangeListener(this);
    } else if (N12EStockQuotes.HEADER_UPDATE.equals(name)) {
      _table.getTableHeader().repaint();
    }

  }

  private static class UseColumnRenderer extends JCheckBox implements TableCellRenderer {
    private static final Border noFocusBorder = new EmptyBorder(1, 1, 1, 1);
    private final MoneydanceGUI _mdGui;

    public UseColumnRenderer(final MoneydanceGUI mdGui) {
      super();
      _mdGui = mdGui;
      setHorizontalAlignment(JLabel.CENTER);
      setBorderPainted(true);
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus,
                                                   int row, int column) {
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
      return this;
    }
  }

  private static class UseColumnHeaderRenderer extends JCheckBox implements TableCellRenderer {
    private final JPanel _renderer = new JPanel(new FlowLayout(FlowLayout.CENTER, 2, 0));

    public UseColumnHeaderRenderer() {
      super();
      setHorizontalAlignment(JLabel.CENTER);
      setBorderPainted(false);
      _renderer.add(this);
      JLabel arrow = new JLabel();
      arrow.setIcon(ExchangeComboTableColumn.ARROW_ICON);
      _renderer.add(arrow);
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus,
                                                   int row, int column) {
      final JTableHeader header = table.getTableHeader();
      if (header != null) {
        setForeground(header.getForeground());
        setBackground(header.getBackground());
        setFont(header.getFont());
      }
      _renderer.setBorder(UIManager.getBorder("TableHeader.cellBorder"));
      // show a checkbox that is enabled and off if all are off, enabled and on if all are on,
      // or disabled and on if some are enabled and some are not
      final SecuritySymbolTableModel tableModel = (SecuritySymbolTableModel) table.getModel();
      final boolean anySecuritySelected = tableModel.anySymbolEnabled();
      setSelected(anySecuritySelected);
      setEnabled(!anySecuritySelected || tableModel.allSymbolsEnabled());
      return _renderer;
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
     * {@inheritDoc}
     */
    @Override
    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus,
                                                   int row, int column) {
      JComponent result = (JComponent) super.getTableCellRendererComponent(table, value,
              isSelected, hasFocus, row, column);
      MDColors colors = _mdGui.getColors();
      // the unselected background alternates color for ease of distinction
      if (!isSelected) {
        if (row % 2 == 0) {
          setBackground(colors.homePageBG);
        } else {
          setBackground(colors.homePageAltBG);
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
   * Cell renderer for the list, colors items that are in-use.
   */
  private class SecurityNameCellRenderer extends DefaultTableCellRenderer {
    private final MoneydanceGUI _mdGui;
    private final JPanel _renderer;
    private final JLabel _shareDisplay;

    SecurityNameCellRenderer(final MoneydanceGUI mdGui) {
      _mdGui = mdGui;
      _renderer = new JPanel(new BorderLayout());
      _shareDisplay = new JLabel();
      _shareDisplay.setOpaque(true);
      _renderer.add(this, BorderLayout.CENTER);
      _renderer.add(_shareDisplay, BorderLayout.EAST);
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus,
                                                   int row, int column) {
      super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
      final String shares = (String) table.getModel().getValueAt(row, SecuritySymbolTableModel.SHARES_COL);
      MDColors colors = _mdGui.getColors();
      _shareDisplay.setText(shares + N12EStockQuotes.SPACE);
      // the unselected background alternates color for ease of distinction
      if (!isSelected) {
        if (row % 2 == 0) {
          setForeground(colors.defaultTextForeground);
          setBackground(colors.homePageBG);
          _shareDisplay.setBackground(colors.homePageBG);
        } else {
          setForeground(colors.defaultTextForeground);
          setBackground(colors.homePageAltBG);
          _shareDisplay.setBackground(colors.homePageAltBG);
        }
      } else {
        setForeground(table.getSelectionForeground());
        setBackground(table.getSelectionBackground());
        _shareDisplay.setForeground(table.getSelectionForeground());
        _shareDisplay.setBackground(table.getSelectionBackground());
      }
      _shareDisplay.setForeground(Color.GRAY); // lighter text for the share balance
      // put the border around both components
      Border border = isSelected ? getBorder() : null;
      setBorder(null);
      _renderer.setBorder(border);
      // in case the text is cut off, show complete text in a tool tip
      if (value instanceof String) {
        setToolTipText((String)value);
      }
      return _renderer;
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
  }

  private class DialogOKButtonListener implements OKButtonListener {
    public void buttonPressed(int buttonId) {
      if (buttonId == OKButtonPanel.ANSWER_OK) {
        onOK();
      } else {
        setVisible(false);
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
      final JDialog owner = SettingsWindow.this;
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
