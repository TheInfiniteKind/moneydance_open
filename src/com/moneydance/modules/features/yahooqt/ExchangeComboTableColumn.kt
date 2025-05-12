/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.moneydance.apps.md.view.gui.MoneydanceGUI
import java.awt.Color
import java.awt.Component
import java.awt.Insets
import java.awt.event.ActionEvent
import java.awt.event.ActionListener
import java.awt.event.MouseAdapter
import java.awt.event.MouseEvent
import javax.swing.*
import javax.swing.border.Border
import javax.swing.plaf.metal.MetalComboBoxUI
import javax.swing.table.DefaultTableCellRenderer
import javax.swing.table.TableColumn

/**
 * This class is responsible for building, displaying and handling validation for a combobox based
 * table column.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class ExchangeComboTableColumn(mdGui: MoneydanceGUI, modelIndex: Int, width: Int, items: List<StockExchange>,
                               /**
                                * Editing interface to edit a stock exchange.
                                */
                               private val _exchangeEditor: IExchangeEditor)
  : TableColumn(modelIndex, width) {
  /**
   * Initialize the combo column with the type and items for the combo box. You can specify
   * whether to show a dropdown arrow or not.
   *
   * @param mdGui      The main application UI object.
   * @param modelIndex Column index in the column model.
   * @param width      Preferred width in pixels.
   * @param items      The items to add to the combo box.
   * @param exchangeEditor Callback interface for editing an individual exchange.
   */
  init {
    setCellRenderer(ComboCellRenderer(mdGui))
    setCellEditor(ComboCellEditor(items))
    val renderer = ComboCellRenderer(mdGui)
    renderer.setIsHeaderCell(true)
    setHeaderRenderer(renderer)
  }
  
  /**
   * The combo box cell renderer used to render the cell when the table is not in edit mode.
   */
  private inner class ComboCellRenderer
  /**
   * Initialize the combo box renderer and set up the cell to have the same look and feel as
   * the rest of the table.
   * @param mdGui The main application UI object.
   */(
    /** The UI object to get colors from.  */
    private val _mdGui: MoneydanceGUI) : DefaultTableCellRenderer() {
    /** True if this cell is in the header of the table.  */
    private var _isHeaderCell = false
    
    override fun getTableCellRendererComponent(table: JTable?, value: Any, isSelected: Boolean,
                                               hasFocus: Boolean, row: Int, column: Int): Component {
      val result = super.getTableCellRendererComponent(
        table, value, isSelected,
        hasFocus, row, column
      ) as JLabel
      result.border = getComponentBorder(false, hasFocus)
      if (table == null) return result // skip further configuration if table==null (ie the scrollpane is calculating sizes)
      
      if (_isHeaderCell) {
        val header = table.tableHeader
        if (header != null) {
          result.foreground = header.foreground
          result.background = header.background
          result.font = header.font
        }
        result.horizontalAlignment = CENTER
        result.icon = ARROW_ICON
        result.horizontalTextPosition = LEFT
      } else {
        if (isSelected) {
          result.foreground = table.selectionForeground
          result.background = table.selectionBackground
        } else {
          result.foreground = table.foreground
          if (row % 2 == 0) {
            result.background = _mdGui.colors.homePageBG
          } else {
            result.background = _mdGui.colors.homePageAltBG
          }
        }
        val model = table.model as SecuritySymbolTableModel
        result.toolTipText = model.getToolTip(row, column)
      } // if not the header
      
      return result
    }
    
    /**
     * Return the border to display around the component, according to the given properties.
     *
     * @param drawingForEditor If this renderer is drawing on the screen for the editor.
     * @param hasFocus         If keyboard focus is on the cell.
     * @return The border object for drawing the border
     */
    fun getComponentBorder(drawingForEditor: Boolean, hasFocus: Boolean): Border {
      if (_isHeaderCell) return UIManager.getBorder("TableHeader.cellBorder")
      if (drawingForEditor || hasFocus) {
        return FOCUS_ARROW_BORDER
      }
      return ARROW_BORDER
    }
    
    fun setIsHeaderCell(isHeader: Boolean) {
      _isHeaderCell = isHeader
    }
  }
  
  /**
   * The cell editor used to display the combo box when the table cell is in edit mode.
   */
  private inner class ComboCellEditor(items: List<StockExchange>) : DefaultCellEditor(JComboBox(ComboListModel(items))), ActionListener {
    /** The component to display in the cells.   */
    private val _comboBox = editorComponent as JComboBox<*>
    
    /**
     * Initialize the combo box editor and sets up the cell to have the same look and feel as
     * the rest of the table and adds the appropriate action listeners to handle combo box
     * actions and validation.
     *
     * @param items The items to add to the combo box.
     */
    init {
      _comboBox.isOpaque = false
      // Java 1.5 does not handle the replacement UI correctly, it stretches the arrow button
      // opaque background across the entire cell, obscuring the text
      if ((_comboBox.ui is MetalComboBoxUI) && (MoneydanceGUI.javaVersion >= 100600000)) {
        _comboBox.setUI(MetalTableComboBoxUI())
      }
      _comboBox.renderer = ComboBoxCellRenderer()
      
      // set this property so that the action event is only fired when a new
      // selection is finally made by clicking on it, or hitting the enter key.
      // if you do not set this, and user is traversing the combo with the arrows,
      // each time a selection is highlighted in the dropdown, the action event occurs.
      _comboBox.putClientProperty("JComboBox.isTableCellEditor", java.lang.Boolean.TRUE)
      
      // must listen for the action event so we can hide the popup menu and fireEditingStopped
      _comboBox.addActionListener(this)
      
      _comboBox.addMouseListener(object : MouseAdapter() {
        override fun mouseClicked(event: MouseEvent) {
          if (SwingUtilities.isRightMouseButton(event) ||
              (SwingUtilities.isLeftMouseButton(event) && (event.clickCount > 1))
          ) {
            event.consume()
            showExchangeEditDialog()
          }
        }
      })
    }
    
    fun showExchangeEditDialog() {
      val exchange = _comboBox.selectedItem as StockExchange
      _exchangeEditor.edit(exchange)
    }
    
    /**
     * Returns the value contained in the editor.
     *
     * @return the value contained in the editor
     */
    override fun getCellEditorValue(): Any? {
      return _comboBox.selectedItem
    }
    
    /**
     * Invoked when an action occurs.
     *
     * @param event The action event.
     */
    override fun actionPerformed(event: ActionEvent) {
      _comboBox.hidePopup()
      stopCellEditing()
    }
  }
  
  /**
   * ComboBoxUI to integrate the the table style into the combobox. Sets an empty border and
   * paints the appropriate colors when the box is disabled.
   */
  private class MetalTableComboBoxUI : MetalComboBoxUI() {
    /**
     * {@inheritDoc}
     */
    override fun createArrowButton(): JButton {
      val button: JButton = object : JButton() {
        override fun isFocusable(): Boolean {
          return false
        }
        
        override fun setEnabled(enabled: Boolean) {
          super.setEnabled(enabled)
          
          // Set the background and foreground to the combobox colors.
          if (!enabled) {
            background = BACKGROUND_DISABLED
            foreground = FOREGROUND_DISABLED
          }
        }
      }
      button.margin = Insets(0, 1, 1, 3)
      button.border = BorderFactory.createEmptyBorder()
      return button
    }
  }
  
  /**
   * The column combo box list renderer.
   */
  private inner class ComboBoxCellRenderer : DefaultListCellRenderer() {
    /**
     * {@inheritDoc}
     *
     * @param list         {@inheritDoc}
     * @param value        {@inheritDoc}
     * @param index        {@inheritDoc}
     * @param isSelected   {@inheritDoc}
     * @param cellHasFocus {@inheritDoc}
     * @return {@inheritDoc}
     */
    override fun getListCellRendererComponent(list: JList<*>?,
                                              value: Any,
                                              index: Int,
                                              isSelected: Boolean,
                                              cellHasFocus: Boolean): Component {
      val result = super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus) as JLabel
      result.text = value.toString() ?: N12EStockQuotes.EMPTY
      result.border = BorderFactory.createEmptyBorder(0, 4, 0, 0)
      return result
    }
  }
  
  /**
   * Combo box model that provides a set method to decrease the number of events on clear/set.
   */
  internal class ComboListModel<T>(private val _items: List<T>) : AbstractListModel<T>(), ComboBoxModel<T> {
    /**
     * The selected object.
     */
    private var _selectedObject: T? = null
    
    /**
     * Returns the length of the list.
     *
     * @return the length of the list
     */
    override fun getSize(): Int {
      return _items.size
    }
    
    /**
     * Returns the value at the specified index.
     *
     * @param index the requested index
     * @return the value at `index`
     */
    override fun getElementAt(index: Int): T {
      return _items[index]
    }
    
    /**
     * Set the selected item. The implementation of this  method should notify all registered
     * `ListDataListener`s that the contents have changed.
     *
     * @param anObject the list object to select or `null` to clear the selection
     */
    override fun setSelectedItem(anObject: Any?) {
      if (_selectedObject != null && _selectedObject != anObject || _selectedObject == null && anObject != null) {
        _selectedObject = anObject as? T
        fireContentsChanged(this, -1, -1)
      }
    }
    
    /**
     * Returns the selected item
     *
     * @return The selected item or `null` if there is no selection
     */
    override fun getSelectedItem(): Any? {
      return _selectedObject
    }
  }
  
  companion object {
    /**
     * Background color for disabled combo boxes. This makes the combo box look like the reset of
     * the cells in the table.
     */
    private val BACKGROUND_DISABLED: Color = UIManager.getColor("window")
    
    /**
     * Foreground color for disabled combo boxes. This makes the combo box look like the rest of the
     * cells in the table.
     */
    private val FOREGROUND_DISABLED: Color = UIManager.getColor("textInactiveText")
    
    /**
     * The size of the focus border for consistency with the focus border. Otherwise you'll get
     * a 'waggle' in placement of the checkbox, where the in-focus checkbox is slightly offset.
     */
    private const val FOCUS_BORDER_SIZE = 1
    
    /**
     * A line border with an arrow when there is focus.
     */
    private val FOCUS_ARROW_BORDER: Border = ArrowBorder(
      ArrowBorder.ICON_LENGTH, ArrowBorder.ICON_WIDTH,
      ArrowBorder.ICON_PADDING, true, FOCUS_BORDER_SIZE
    )
    
    /**
     * The arrow icon for the header cell.
     */
    val ARROW_ICON: ArrowIcon = ArrowIcon(
      SwingConstants.SOUTH, true,
      ArrowBorder.ICON_LENGTH, ArrowBorder.ICON_WIDTH
    )
    
    /**
     * An arrow border when keyboard focus is not on the cell.
     */
    private val ARROW_BORDER: Border = ArrowBorder(
      ArrowBorder.ICON_LENGTH,
      ArrowBorder.ICON_WIDTH, ArrowBorder.ICON_PADDING, true, 0
    )
  }
}
