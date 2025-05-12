/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.CurrencyTable
import com.infinitekind.util.StringUtils.replaceAll
import com.moneydance.apps.md.controller.FeatureModuleContext
import com.moneydance.apps.md.controller.Util
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.OKButtonListener
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import com.moneydance.awt.JDateField
import com.moneydance.modules.features.yahooqt.ExchangeComboTableColumn.ComboListModel
import com.moneydance.util.UiUtil
import java.awt.*
import java.awt.event.*
import java.beans.PropertyChangeEvent
import java.beans.PropertyChangeListener
import java.text.MessageFormat
import javax.swing.*
import javax.swing.border.Border
import javax.swing.border.EmptyBorder
import javax.swing.event.HyperlinkEvent
import javax.swing.event.MouseInputAdapter
import javax.swing.table.*
import kotlin.math.max

/**
 * Main settings configuration dialog for the quotes and rates updater extension
 */
class SettingsWindow
  (private val context: FeatureModuleContext, resources: ResourceProvider,
   /** This contains the table model as well as other data that is edited in this dialog.  */
   private val _model: StockQuotesModel) : JDialog(), PropertyChangeListener {
  private val contentPane = JPanel(BorderLayout(5, 5))
  private val _table = JTable()
  private val _resources: ResourceProvider
  private val _exchangeEditor: IExchangeEditor = ExchangeEditor()
  
  private var _historyConnectionSelect: JComboBox<BaseConnection>? = null
  private var _ratesConnectionSelect: JComboBox<BaseConnection>? = null
  private var setAPIKeyAction: Action? = null
  private var downloadAction: Action? = null
  private var testAction: Action? = null
  private var testButton: JButton? = null
  private var _apiKeyButton: JButton? = null
  
  private var _intervalSelect: IntervalChooser? = null
  private var _nextDate: JDateField? = null
  private val _showTestLabel = JLabel()
  private var _testColumn: TableColumn? = null
  private var _showingTestInfo = false
  private var _tableRenderer: ItemListCellRenderer? = null
  private val _showOwnedOnly = JCheckBox()
  private val statusSummaryPanel = JEditorPane()
  private var _okButtonPressed = false
  
  init {
    _model.addPropertyChangeListener(this)
    _resources = resources
    initUI(context)
    setContentPane(contentPane)
    isModal = true
    title = resources.getString(L10NStockQuotes.SETTINGS_TITLE)
    //    setIconImage(Main.getIcon()); // available in Java 1.6 only
    val size = _model.preferences.getSizeSetting(N12EStockQuotes.SIZE_KEY)
    if (size.width == 0) {
      pack()
    } else {
      setSize(size)
    }
    val location = _model.preferences.getXYSetting(N12EStockQuotes.LOCATION_KEY, -1, -1)
    if (location.x == -1) {
      val screenSize = Toolkit.getDefaultToolkit().screenSize
      location.x = (screenSize.width - width) / 2
      location.y = (screenSize.height - height) / 2
    }
    setLocation(location)
  }
  
  override fun setVisible(visible: Boolean) {
    if (visible) {
      _model.buildSecurityMap()
      updateAPIKeyButton()
      setSecurityTableColumnSizes()
      // display the last update date in the test status area
      updateStatusBlurb()
      validate()
    }
    super.setVisible(visible)
  }
  
  fun userAcceptedChanges(): Boolean {
    return _okButtonPressed
  }
  
  private fun initUI(context: FeatureModuleContext) {
    val fieldPanel = JPanel(GridBagLayout())
    fieldPanel.border = BorderFactory.createEmptyBorder(
      UiUtil.DLG_VGAP, UiUtil.DLG_HGAP,
      UiUtil.DLG_VGAP, UiUtil.DLG_HGAP
    )
    // pick which URL schemes to connect to (or no connection to disable the download)
    // stock historical quotes
    _historyConnectionSelect = JComboBox<BaseConnection>(_model.getConnectionList(BaseConnection.HISTORY_SUPPORT))
    _historyConnectionSelect!!.selectedItem = _model.selectedHistoryConnection
    _historyConnectionSelect!!.addItemListener { arg: ItemEvent? -> updateAPIKeyButton() }
    
    
    // currency exchange rates
    _ratesConnectionSelect = JComboBox<BaseConnection>(_model.getConnectionList(BaseConnection.EXCHANGE_RATES_SUPPORT))
    _ratesConnectionSelect!!.selectedItem = _model.selectedExchangeRatesConnection
    
    setAPIKeyAction = object : AbstractAction() {
      override fun actionPerformed(e: ActionEvent) {
        val bc = _historyConnectionSelect!!.model.selectedItem as BaseConnection
        if (bc is APIKeyConnection) {
          bc.getAPIKey(true)
        }
      }
    }.also { it.putValue(Action.NAME, _resources.getString(L10NStockQuotes.SET_API_KEY)) }
    
    downloadAction = object : AbstractAction() {
      override fun actionPerformed(e: ActionEvent) {
        // Store what we have in the dialog - same as OK. We need to do this because the main app
        // update is called, which reads these settings from preferences or the data file.
        saveControlsToSettings()
        // listen for events so our status updates just like the main application's
        _model.addPropertyChangeListener(this@SettingsWindow)
        // call the main update method
        context.showURL("moneydance:fmodule:yahooqt:update")
      }
    }.also {
      it.putValue(Action.NAME, _resources.getString(L10NStockQuotes.UPDATE_NOW))
    }
    
    statusSummaryPanel.isEditable = false
    statusSummaryPanel.isFocusable = false
    statusSummaryPanel.foreground = JLabel("x").foreground
    statusSummaryPanel.border = BorderFactory.createEmptyBorder(10, 10, 10, 10)
    statusSummaryPanel.addHyperlinkListener { event ->
      if (event.eventType == HyperlinkEvent.EventType.ACTIVATED &&
          event.url != null
      ) {
        if (Desktop.isDesktopSupported()) {
          try {
            Desktop.getDesktop().browse(event.url.toURI())
          } catch (ex: Exception) {
            System.err.println("Error opening URL $ex")
          }
        }
      }
    }
    
    
    testAction = object : AbstractAction() {
      override fun actionPerformed(e: ActionEvent) {
        val root = _model.rootAccount ?: return
        
        // save the selected connections into our model
        saveSelectedConnections()
        // store what we have into the symbol map
        _model.tableModel.save(root)
        // listen for update events
        _model.addPropertyChangeListener(this@SettingsWindow)
        _model.runDownloadTest()
      }
    }.also {
      it.putValue(Action.NAME, _resources.getString(L10NStockQuotes.TEST))
    }
    
    _intervalSelect = IntervalChooser(_model.gui)
    val paramStr = _model.preferences.getSetting(Main.UPDATE_INTERVAL_KEY, "")
    _intervalSelect!!.selectFromParams(paramStr)
    _nextDate = JDateField(_model.preferences.shortDateFormatter)
    loadNextDate()
    
    
    // first column
    fieldPanel.add(
      JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.RATES_CONNECTION)),
      GridC.getc(0, 0).label()
    )
    fieldPanel.add(_ratesConnectionSelect, GridC.getc(1, 0).field())
    fieldPanel.add(
      JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.SECURITIES_CONNECTION)),
      GridC.getc(0, 1).label()
    )
    fieldPanel.add(_historyConnectionSelect, GridC.getc(1, 1).field())
    
    _apiKeyButton = JButton(setAPIKeyAction)
    fieldPanel.add(_apiKeyButton, GridC.getc(1, 2).field())
    
    
    // gap in middle
    fieldPanel.add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), GridC.getc(2, 0))
    
    
    // second column
    fieldPanel.add(
      JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.FREQUENCY_LABEL)),
      GridC.getc(3, 0).label()
    )
    fieldPanel.add(_intervalSelect, GridC.getc(4, 0).field())
    fieldPanel.add(
      JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.NEXT_DATE_LABEL)),
      GridC.getc(3, 1).label()
    )
    fieldPanel.add(_nextDate, GridC.getc(4, 1).field())
    _showTestLabel.horizontalAlignment = JLabel.RIGHT
    // add the toggle for the testing mode on/off
    val testPanel = JPanel(BorderLayout())
    testPanel.add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), BorderLayout.CENTER)
    testPanel.add(_showTestLabel, BorderLayout.EAST)
    fieldPanel.add(testPanel, GridC.getc(4, 2).field().east())
    // gap between the fields and the table
    fieldPanel.add(Box.createVerticalStrut(UiUtil.VGAP), GridC.getc(0, 3))
    // setup the table
    val tableHost = setupSecurityTable()
    fieldPanel.add(tableHost, GridC.getc(0, 4).colspan(5).wxy(1f, 1f).fillboth())
    _showOwnedOnly.text = _resources.getString(L10NStockQuotes.SHOW_OWNED)
    _showOwnedOnly.isSelected = !_model.tableModel.showZeroBalance
    fieldPanel.add(_showOwnedOnly, GridC.getc(0, 5).colspan(5).field())
    statusSummaryPanel.text = " "
    fieldPanel.add(statusSummaryPanel, GridC.getc(0, 6).colspan(5).field())
    fieldPanel.border = BorderFactory.createEmptyBorder(
      UiUtil.DLG_VGAP, UiUtil.DLG_HGAP,
      0, UiUtil.DLG_HGAP
    )
    contentPane.add(fieldPanel, BorderLayout.CENTER)
    // buttons at bottom
    testButton = JButton(testAction)
    testButton!!.isVisible = _showingTestInfo
    val extraButtonPanel = JPanel(FlowLayout(FlowLayout.LEFT, UiUtil.HGAP, UiUtil.VGAP))
    extraButtonPanel.add(testButton)
    extraButtonPanel.add(JButton(downloadAction))
    
    
    // the built-in OK/Cancel buttons
    val okButtons = OKButtonPanel(
      _model.gui, DialogOKButtonListener(),
      OKButtonPanel.QUESTION_OK_CANCEL
    )
    val bottomPanel = JPanel(BorderLayout())
    bottomPanel.border = BorderFactory.createEmptyBorder(
      UiUtil.VGAP, UiUtil.DLG_HGAP,
      UiUtil.DLG_VGAP, UiUtil.DLG_HGAP
    )
    bottomPanel.add(extraButtonPanel, BorderLayout.WEST)
    bottomPanel.add(okButtons, BorderLayout.CENTER)
    contentPane.add(bottomPanel, BorderLayout.SOUTH)
    setupTestControls()
    // setup actions for the controls
    addActions(context)
  }
  
  private fun updateAPIKeyButton() {
    val bc = _historyConnectionSelect!!.model.selectedItem as BaseConnection
    if (bc is APIKeyConnection) {
      _apiKeyButton!!.isVisible = true
    } else {
      _apiKeyButton!!.isVisible = false
    }
  }
  
  private fun setupTestControls() {
    if (_showingTestInfo) {
      _showTestLabel.text = _resources.getString(L10NStockQuotes.BASIC)
      _showTestLabel.toolTipText = _resources.getString(L10NStockQuotes.HIDE_TEST)
      testButton!!.isVisible = true
      _table.columnModel.addColumn(_testColumn)
    } else {
      _showTestLabel.text = _resources.getString(L10NStockQuotes.ADVANCED)
      _showTestLabel.toolTipText = _resources.getString(L10NStockQuotes.SHOW_TEST)
      testButton!!.isVisible = false
      _table.columnModel.removeColumn(_testColumn)
    }
  }
  
  
  private fun updateStatusBlurb() {
    val fgColor = hexStringForColor(JLabel().foreground)
    val msg = StringBuilder("<html><body style=\"text-align:center; font: sans; color: #$fgColor;\">")
    if (_model.rootAccount != null) {
      val messageFormat = _resources.getString(L10NStockQuotes.LAST_UPDATE_FMT)
      val lastRateDate = _model.ratesLastUpdateDate
      val rateText = getDateText(lastRateDate)
      val lastQuoteDate = _model.quotesLastUpdateDate
      val quoteText = getDateText(lastQuoteDate)
      msg.append("<p>").append(MessageFormat.format(messageFormat, rateText, quoteText)).append("</p>")
    }
    val securityConn = _model.selectedHistoryConnection
    if (securityConn != null && securityConn is IEXConnection) {
      msg.append("<p>Data provided for free by IEX. View IEX’s <a href=\"https://iextrading.com/api-exhibit-a\">Terms of Use.</a></p>")
    }
    msg.append("</body></html>")
    
    statusSummaryPanel.contentType = "text/html"
    statusSummaryPanel.text = msg.toString()
    statusSummaryPanel.border = null
  }
  
  private fun getDateText(date: Int): String {
    if (date <= 0) {
      return _resources.getString(L10NStockQuotes.NEVER) ?: "NEVER"
    }
    return _model.preferences.shortDateFormatter.format(date)
  }
  
  private fun addActions(context: FeatureModuleContext) {
    _showOwnedOnly.addItemListener { e -> // show zero balance only if 'show only that I own' is deselected
      _model.tableModel.showZeroBalance = e.stateChange == ItemEvent.DESELECTED
    }
    val mouseInputListener: MouseInputAdapter = object : MouseInputAdapter() {
      override fun mouseReleased(e: MouseEvent) {
        if (SwingUtilities.isLeftMouseButton(e)) {
          _showingTestInfo = !_showingTestInfo
          if (_showingTestInfo) {
            // update the currency and other status messages with the latest edits
            _model.tableModel.scanForSymbolOverrides()
          }
          setupTestControls()
          setSecurityTableColumnSizes()
          validate()
        }
      }
      
      override fun mouseEntered(event: MouseEvent) {
        cursor = Cursor(Cursor.HAND_CURSOR)
      }
      
      override fun mouseExited(event: MouseEvent) {
        cursor = Cursor(Cursor.DEFAULT_CURSOR)
      }
    }
    _showTestLabel.addMouseListener(mouseInputListener)
    _showTestLabel.addMouseMotionListener(mouseInputListener)
  }
  
  private fun loadNextDate() {
    val lastDate = _model.rootAccount!!.getIntParameter(Main.QUOTE_LAST_UPDATE_KEY, 0)
    val nextDate: Int
    if (lastDate == 0) {
      nextDate = Util.getStrippedDateInt() // today
    } else {
      val frequency = Main.getUpdateFrequency(_model.preferences)
      nextDate = SQUtil.getNextDate(lastDate, frequency)
    }
    _nextDate!!.dateInt = nextDate
  }
  
  
  private fun setupSecurityTable(): JScrollPane {
    _table.model = _model.tableModel
    _table.border = BorderFactory.createEmptyBorder(0, UiUtil.HGAP, 0, UiUtil.HGAP)
    val host = JScrollPane(
      _table, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
      JScrollPane.HORIZONTAL_SCROLLBAR_NEVER
    )
    
    // consistent row height with other tables in the application
    _table.rowHeight = _table.rowHeight + 8
    _table.autoResizeMode = JTable.AUTO_RESIZE_LAST_COLUMN
    _table.rowSelectionAllowed = true
    _table.columnSelectionAllowed = false
    _table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
    val columnModel = createColumnModel()
    _table.columnModel = columnModel
    _table.dragEnabled = false
    //    _table.setFillsViewportHeight(true); // available in Java 1.6 only
    _table.setShowGrid(false)
    val tableHeader = JTableHeader(columnModel)
    // the only way to get mouse clicks is to attach a listener to the header
    tableHeader.addMouseListener(object : MouseAdapter() {
      override fun mouseReleased(event: MouseEvent) {
        val header = event.source as JTableHeader
        val columnModel = header.columnModel
        val viewColumn = header.columnAtPoint(event.point)
        val column = columnModel.getColumn(viewColumn).modelIndex
        if (column == SecuritySymbolTableModel.USE_COL) {
          // we know the renderer for this column is a JComponent
          showIncludeMenu(header)
        } else if (column == SecuritySymbolTableModel.EXCHANGE_COL) {
          batchChangeExchange()
        }
      }
    })
    tableHeader.reorderingAllowed = false
    _table.tableHeader = tableHeader
    _table.setDefaultRenderer(TableColumn::class.java, _tableRenderer)
    _table.addMouseListener(object : MouseAdapter() {
      override fun mouseReleased(event: MouseEvent) {
        // if the user clicks on a test result cell and there's a tooltip to show, put the tooltip
        // in a message dialog.
        val columnModel = _table.columnModel
        val viewColumn = _table.columnAtPoint(event.point)
        val column = columnModel.getColumn(viewColumn).modelIndex
        val row = _table.rowAtPoint(event.point)
        if (column == SecuritySymbolTableModel.TEST_COL) {
          val message = _model.tableModel.getToolTip(row, SecuritySymbolTableModel.TEST_COL)
          if (!SQUtil.isBlank(message)) {
            val p = JPanel(GridBagLayout())
            val symbolTip = _model.tableModel.getToolTip(row, SecuritySymbolTableModel.SYMBOL_COL)
            p.add(JLabel(symbolTip), GridC.getc(0, 0))
            p.add(Box.createVerticalStrut(UiUtil.VGAP), GridC.getc(0, 1))
            p.add(JLabel(message), GridC.getc(0, 2))
            JOptionPane.showMessageDialog(this@SettingsWindow, p)
          }
        } else if ((column == SecuritySymbolTableModel.EXCHANGE_COL) &&
                   SwingUtilities.isRightMouseButton(event)
        ) {
          // edit the exchange
          showExchangeEditDialog(row)
        }
      }
    })
    // add hot key
    _table.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(
      KeyStroke.getKeyStroke(
        KeyEvent.VK_E,
        MoneydanceGUI.ACCELERATOR_MASK
      ), "editExchange"
    )
    _table.actionMap.put("editExchange", object : AbstractAction() {
      override fun actionPerformed(event: ActionEvent) {
        val selectedRow = _table.selectedRow
        if (selectedRow >= 0) {
          showExchangeEditDialog(selectedRow)
        }
      }
    })
    return host
  }
  
  private fun showExchangeEditDialog(row: Int) {
    val exchange = _model.tableModel.getValueAt(
      row, SecuritySymbolTableModel.EXCHANGE_COL
    ) as StockExchange
    _exchangeEditor.edit(exchange)
  }
  
  private fun includeAll(include: Boolean) {
    _model.tableModel.enableAllSymbols(include)
    _table.tableHeader.repaint()
  }
  
  private fun showIncludeMenu(parent: JComponent) {
    val menu = JPopupMenu()
    var menuItem = JMenuItem("All")
    menuItem.addActionListener { includeAll(true) }
    menu.add(menuItem)
    menuItem = JMenuItem(_model.gui.getStr("none"))
    menuItem.addActionListener { includeAll(false) }
    menu.add(menuItem)
    menu.show(parent, 0, parent.height)
  }
  
  private fun batchChangeExchange() {
    val comboListModel = ComboListModel(exchangeItems)
    val exchangeCombo: JComboBox<*> = JComboBox(comboListModel)
    if (showField(exchangeCombo)) {
      val selected = exchangeCombo.selectedItem as StockExchange
      _model.tableModel.batchChangeExchange(selected)
    }
  }
  
  private fun showField(field: JComponent): Boolean {
    val p = JPanel(GridBagLayout())
    val mdGUI = _model.gui
    var msg = mdGUI.getStr("batch_msg")
    val fieldName = _resources.getString(L10NStockQuotes.EXCHANGE_TITLE)
    msg = replaceAll(msg!!, "{field}", fieldName)
    
    p.add(JLabel(UiUtil.addLabelSuffix(mdGUI, msg)), GridC.getc(0, 0))
    p.add(field, GridC.getc(1, 0).wx(1f).fillx())
    p.add(Box.createHorizontalStrut(120), GridC.getc(1, 1))
    
    // Requests focus on the combo box.
    field.addHierarchyListener { e ->
      val c = e.component
      if (c.isShowing && (e.changeFlags and
          HierarchyEvent.SHOWING_CHANGED.toLong()) != 0L
      ) {
        val toplevel = SwingUtilities.getWindowAncestor(c)
        toplevel.addWindowFocusListener(object : WindowAdapter() {
          override fun windowGainedFocus(e: WindowEvent) {
            c.requestFocusInWindow()
          }
        })
      }
    }
    
    val result = JOptionPane.showConfirmDialog(
      this, p, mdGUI.getStr("batch_change"),
      JOptionPane.OK_CANCEL_OPTION,
      JOptionPane.QUESTION_MESSAGE
    )
    
    return result == JOptionPane.OK_OPTION
  }
  
  private fun createColumnModel(): TableColumnModel {
    val columnModel = DefaultTableColumnModel()
    _tableRenderer = ItemListCellRenderer(_model.gui)
    
    // select security for download column
    var col: TableColumn
    columnModel.addColumn(
      TableColumn(
        SecuritySymbolTableModel.USE_COL, 20,
        UseColumnRenderer(_model.gui), UseColumnEditor()
      ).also { col = it })
    // special renderer allows the header to act like a checkbox to select all / deselect all
    val useHeaderRenderer = UseColumnHeaderRenderer()
    col.headerRenderer = useHeaderRenderer
    col.headerValue = " "
    
    // name and number of shares
    columnModel.addColumn(
      TableColumn(
        SecuritySymbolTableModel.NAME_COL, 150,
        SecurityNameCellRenderer(_model.gui), null
      ).also { col = it })
    col.headerValue = _model.gui.getStr("curr_type_sec")
    columnModel.addColumn(
      TableColumn(
        SecuritySymbolTableModel.SYMBOL_COL, 40,
        _tableRenderer,
        TickerColumnEditor()
      ).also { col = it })
    col.headerValue = _model.gui.getStr("currency_ticker")
    
    // the stock exchange picker
    val exchangeColumn =
      ExchangeComboTableColumn(
        _model.gui,
        SecuritySymbolTableModel.EXCHANGE_COL, 60,
        exchangeItems, _exchangeEditor
      )
    columnModel.addColumn(exchangeColumn)
    exchangeColumn.headerValue = _resources.getString(L10NStockQuotes.EXCHANGE_TITLE)
    // testing column
    _testColumn = TableColumn(SecuritySymbolTableModel.TEST_COL, 40, _tableRenderer, null)
    if (_showingTestInfo) {
      columnModel.addColumn(_testColumn)
    }
    _testColumn!!.headerValue = _resources.getString(L10NStockQuotes.TEST_TITLE)
    
    return columnModel
  }
  
  private val exchangeItems: List<StockExchange>
    get() {
      // set the name to a displayable localized string
      StockExchange.DEFAULT.name = _model.gui.getStr("default")
      // find all of the stock exchange items that have a currency that exists in the data file
      val items: MutableList<StockExchange> = ArrayList()
      items.add(StockExchange.DEFAULT)
      val ctable = _model.book!!.currencies
      for (exchange in _model.exchangeList.fullList) {
        if (isValidExchange(ctable, exchange)) items.add(exchange)
      }
      return items.toList()
    }
  
  /**
   * Define the table column sizes according to the data in them.
   */
  private fun setSecurityTableColumnSizes() {
    if ((_model.tableModel == null) || (_model.tableModel.rowCount == 0)) return  // nothing to do
    
    // find the maximum width of the columns - there may be more columns in the model than in the view
    val viewColumnCount = _table.columnModel.columnCount
    val widths = IntArray(viewColumnCount)
    widths[0] = 35
    for (column in 0..<viewColumnCount) {
      for (row in 0..<_table.rowCount) {
        val renderer = _table.getCellRenderer(row, column)
        var comp = renderer.getTableCellRendererComponent(
          _table,
          _table.getValueAt(row, column), false, false, row, column
        )
        widths[column] = max(widths[column], comp.preferredSize.width)
        if ((row == 0) && (column > 0)) {
          // include the header text too, but only for columns other than 'use'
          comp = renderer.getTableCellRendererComponent(
            _table, _model.tableModel.getColumnName(column),
            false, false, row, column
          )
          widths[column] = max(widths[column], comp.preferredSize.width)
        }
      }
    }
    
    
    // set the last column to be as big as the biggest column - all extra space should be given to
    // the last column
    var maxWidth = 0
    for (width1 in widths) maxWidth = max(width1, maxWidth)
    widths[viewColumnCount - 1] = maxWidth
    val columnModel = _table.columnModel
    for (column in widths.indices) {
      columnModel.getColumn(column).preferredWidth = widths[column]
    }
  }
  
  private fun onOK() {
    saveControlsToSettings()
    
    _okButtonPressed = true
    isVisible = false
    
    context.showURL("moneydance:fmodule:yahooqt:update") // kick off an update, if needed
  }
  
  private fun saveControlsToSettings() {
    val root = _model.rootAccount ?: return
    
    saveSelectedConnections()
    
    
    // these are stored in preferences and are not file-specific
    val prefs = _model.preferences
    prefs.setSetting(Main.AUTO_UPDATE_KEY, isAnyConnectionSelected)
    prefs.setSetting(Main.UPDATE_INTERVAL_KEY, _intervalSelect!!.selectedInterval.configKey)
    
    
    // save the date of the next update
    val nextDate = _nextDate!!.dateInt
    
    
    // work backwards to get the calculated 'last update date'
    val frequency = _intervalSelect!!.selectedInterval
    _model.setHistoryDaysFromFrequency(frequency)
    val lastDate = SQUtil.getPreviousDate(nextDate, frequency)
    val currentQuoteDate = _model.quotesLastUpdateDate
    
    if (_model.isStockPriceSelected && (currentQuoteDate != lastDate)) {
      if (Main.DEBUG_YAHOOQT) {
        System.err.println(
          "Changing last quote update date from " +
          currentQuoteDate + " to " + lastDate + " per user selection"
        )
      }
      _model.saveLastQuoteUpdateDate(lastDate)
    }
    val currentRatesDate = _model.ratesLastUpdateDate
    if (_model.isExchangeRateSelected && (currentRatesDate != lastDate)) {
      if (Main.DEBUG_YAHOOQT) {
        System.err.println(
          "Changing last exchange rates update date from " +
          currentRatesDate + " to " + lastDate + " per user selection"
        )
      }
      _model.saveLastExchangeRatesUpdateDate(lastDate)
    }
    
    
    // check if any of the settings that are stored in the specific data file have been changed
    if (_model.isDirty) {
      _model.saveSettings(root)
    }
  }
  
  private fun saveSelectedConnections() {
    _model.selectedHistoryConnection = _historyConnectionSelect!!.selectedItem as BaseConnection
    _model.selectedExchangeRatesConnection = _ratesConnectionSelect!!.selectedItem as BaseConnection
  }
  
  private val isAnyConnectionSelected: Boolean
    get() = _model.isStockPriceSelected || _model.isExchangeRateSelected
  
  override fun dispose() {
    _model.removePropertyChangeListener(this)
    _model.preferences.setXYSetting(N12EStockQuotes.LOCATION_KEY, location)
    _model.preferences.setSizeSetting(N12EStockQuotes.SIZE_KEY, size)
    super.dispose()
  }
  
  override fun propertyChange(event: PropertyChangeEvent) {
    val name = event.propertyName
    if (N12EStockQuotes.STATUS_UPDATE == name) {
      var status = event.newValue as String
      status = status ?: " "
      statusSummaryPanel.contentType = "text/plain"
      statusSummaryPanel.text = status
    } else if (N12EStockQuotes.DOWNLOAD_BEGIN == name) {
      val text = _model.gui.getStr("cancel")
      UiUtil.runOnUIThread { testAction!!.putValue(Action.NAME, text) }
    } else if (N12EStockQuotes.DOWNLOAD_END == name) {
      val text = _resources.getString(L10NStockQuotes.TEST)
      UiUtil.runOnUIThread {
        testAction!!.putValue(Action.NAME, text)
        // the next update date may have changed now
        loadNextDate()
      }
      // we're done listening for results
      _model.removePropertyChangeListener(this)
    } else if (N12EStockQuotes.HEADER_UPDATE == name) {
      _table.tableHeader.repaint()
    }
  }
  
  private class UseColumnRenderer(private val _mdGui: MoneydanceGUI) : JCheckBox(), TableCellRenderer {
    init {
      putClientProperty("JComponent.isCellEditor", true)
    }
    
    override fun getTableCellRendererComponent(table: JTable, value: Any,
                                               isSelected: Boolean, hasFocus: Boolean,
                                               row: Int, column: Int): Component {
      horizontalAlignment = CENTER
      isOpaque = false
      isBorderPainted = false
      if (isSelected) {
        foreground = table.selectionForeground
        background = table.selectionBackground
      } else {
        foreground = table.foreground
        background = if (row % 2 == 0) {
          _mdGui.colors.homePageBG
        } else {
          _mdGui.colors.homePageAltBG
        }
      }
      setSelected((value is Boolean) && value)
      border = if (hasFocus) {
        UIManager.getBorder("Table.focusCellHighlightBorder")
      } else {
        noFocusBorder
      }
      return this
    }
    
    companion object {
      private val noFocusBorder: Border = EmptyBorder(1, 1, 1, 1)
    }
  }
  
  private class UseColumnHeaderRenderer : JCheckBox(), TableCellRenderer {
    private val _renderer = JPanel(FlowLayout(FlowLayout.CENTER, 2, 0))
    
    init {
      _renderer.add(this)
      val arrow = JLabel()
      arrow.icon = ExchangeComboTableColumn.ARROW_ICON
      _renderer.add(arrow)
    }
    
    override fun getTableCellRendererComponent(table: JTable?, value: Any,
                                               isSelected: Boolean, hasFocus: Boolean,
                                               row: Int, column: Int): Component {
      horizontalAlignment = CENTER
      isBorderPainted = false
      
      
      // beware: if table==null then the vaqua scrollpane is calculating sizes
      val header = table?.tableHeader
      if (header != null) {
        foreground = header.foreground
        background = header.background
        font = header.font
      }
      _renderer.border = UIManager.getBorder("TableHeader.cellBorder")
      // show a checkbox that is enabled and off if all are off, enabled and on if all are on,
      // or disabled and on if some are enabled and some are not
      val tableModel = if (table == null) null else table.model as SecuritySymbolTableModel
      val anySecuritySelected = tableModel?.anySymbolEnabled() ?: false
      setSelected(anySecuritySelected)
      isEnabled = !anySecuritySelected || (tableModel == null || tableModel.allSymbolsEnabled())
      return _renderer
    }
  }
  
  private class UseColumnEditor : DefaultCellEditor(JCheckBox()) {
    init {
      val checkBox = component as JCheckBox
      checkBox.horizontalAlignment = JCheckBox.CENTER
    }
  }
  
  /**
   * Cell renderer for the list, colors items that are in-use.
   */
  private inner class ItemListCellRenderer(private val _mdGui: MoneydanceGUI) : DefaultTableCellRenderer() {
    /**
     * {@inheritDoc}
     */
    override fun getTableCellRendererComponent(table: JTable, value: Any,
                                               isSelected: Boolean, hasFocus: Boolean,
                                               row: Int, column: Int): Component {
      val result = super.getTableCellRendererComponent(
        table, value,
        isSelected, hasFocus, row, column
      ) as JComponent
      val colors = _mdGui.colors
      // the unselected background alternates color for ease of distinction
      if (!isSelected) {
        background = if (row % 2 == 0) {
          colors.homePageBG
        } else {
          colors.homePageAltBG
        }
      }
      
      
      // in case the text is cut off, show complete text in a tool tip
      if ((column == SecuritySymbolTableModel.SYMBOL_COL) ||
          (column == SecuritySymbolTableModel.TEST_COL)
      ) {
        result.toolTipText = _model.tableModel.getToolTip(row, column)
      } else if (value is String) {
        result.toolTipText = value
      }
      
      return result
    }
  }
  
  /**
   * Cell renderer for the list, colors items that are in-use.
   */
  private inner class SecurityNameCellRenderer(private val _mdGui: MoneydanceGUI) : DefaultTableCellRenderer() {
    private val _renderer = JPanel(BorderLayout())
    private val _shareDisplay = JLabel()
    
    init {
      _shareDisplay.isOpaque = true
      _renderer.add(this, BorderLayout.CENTER)
      _renderer.add(_shareDisplay, BorderLayout.EAST)
    }
    
    /**
     * {@inheritDoc}
     */
    override fun getTableCellRendererComponent(table: JTable, value: Any,
                                               isSelected: Boolean, hasFocus: Boolean,
                                               row: Int, column: Int): Component {
      super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column)
      val shares = table.model.getValueAt(row, SecuritySymbolTableModel.SHARES_COL) as String
      val colors = _mdGui.colors
      _shareDisplay.text = shares + N12EStockQuotes.SPACE
      // the unselected background alternates color for ease of distinction
      if (!isSelected) {
        if (row % 2 == 0) {
          foreground = colors.defaultTextForeground
          background = colors.homePageBG
          _shareDisplay.background = colors.homePageBG
        } else {
          foreground = colors.defaultTextForeground
          background = colors.homePageAltBG
          _shareDisplay.background = colors.homePageAltBG
        }
      } else {
        foreground = table.selectionForeground
        background = table.selectionBackground
        _shareDisplay.foreground = table.selectionForeground
        _shareDisplay.background = table.selectionBackground
      }
      _shareDisplay.foreground = Color.GRAY // lighter text for the share balance
      // put the border around both components
      val border = if (isSelected) border else null
      setBorder(null)
      _renderer.border = border
      // in case the text is cut off, show complete text in a tool tip
      if (value is String) {
        toolTipText = value
      }
      return _renderer
    }
  }
  
  /**
   * Cell editor for in-place editing
   */
  private inner class TickerColumnEditor : DefaultCellEditor(JTextField()) {
    private var _value: String? = null
    
    init {
      component.name = "Table.editor"
    }
    
    override fun stopCellEditing(): Boolean {
      _value = super.getCellEditorValue() as String
      return super.stopCellEditing()
    }
    
    override fun getTableCellEditorComponent(table: JTable, value: Any,
                                             isSelected: Boolean,
                                             row: Int, column: Int): Component {
      _value = null
      val editor = super.getTableCellEditorComponent(
        table, value,
        isSelected, row, column
      ) as JTextField
      editor.requestFocusInWindow()
      editor.selectAll()
      return editor
    }
    
    override fun getCellEditorValue(): Any {
      return _value!!
    }
  }
  
  private inner class DialogOKButtonListener : OKButtonListener {
    override fun buttonPressed(buttonId: Int) {
      if (buttonId == OKButtonPanel.ANSWER_OK) {
        onOK()
      } else {
        isVisible = false
      }
    }
  }
  
  private inner class ExchangeEditor : IExchangeEditor {
    override fun edit(exchange: StockExchange?): Boolean {
      exchange ?: return false
      val mdGui = _model.gui
      if (StockExchange.DEFAULT == exchange) {
        // not editable
        val message = _resources.getString(L10NStockQuotes.ERROR_DEFAULT_NOT_EDITABLE)
        SwingUtilities.invokeLater { mdGui.showErrorMessage(message) }
        return false
      }
      val exchangeList = _model.exchangeList
      val owner: JDialog = this@SettingsWindow
      SwingUtilities.invokeLater {
        val dialog = ExchangeDialog(owner, mdGui, _resources, exchange, exchangeList)
        dialog.isVisible = true
      }
      return true
    }
  }
  
  companion object {
    /**
     * Return the hex string for the given colour. This does _not_ include any 0x or # prefix
     * and is only the 6 digit hexadecimal string.
     */
    fun hexStringForColor(color: Color?): String {
      if (color == null) return ""
      return String.format("%02x%02x%02x", color.red, color.green, color.blue)
    }
    
    /**
     * Determine if we should show an exchange or not, depending upon whether the currency for that
     * exchange is defined in the data file or not.
     * @param ctable   The currency table from the data file.
     * @param exchange The stock exchange to test.
     * @return True if the stock exchange can be used, false if the currency does not exist.
     */
    private fun isValidExchange(ctable: CurrencyTable, exchange: StockExchange): Boolean {
      val currencyId = exchange.currencyCode
      return (ctable.getCurrencyByIDString(currencyId) != null)
    }
  }
}
