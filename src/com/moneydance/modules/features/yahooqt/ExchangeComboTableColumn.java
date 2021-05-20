/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.AbstractListModel;
import javax.swing.BorderFactory;
import javax.swing.ComboBoxModel;
import javax.swing.DefaultCellEditor;
import javax.swing.DefaultListCellRenderer;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import javax.swing.JTable;
import javax.swing.border.Border;
import javax.swing.plaf.metal.MetalComboBoxUI;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableColumn;
import java.awt.Color;
import java.awt.Component;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

/**
 * This class is responsible for building, displaying and handling validation for a combobox based
 * table column.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class ExchangeComboTableColumn extends TableColumn
{
  /**
   * Background color for disabled combo boxes. This makes the combo box look like the reset of
   * the cells in the table.
   */
  private static final Color BACKGROUND_DISABLED = UIManager.getColor("window");

  /**
   * Foreground color for disabled combo boxes. This makes the combo box look like the rest of the
   * cells in the table.
   */
  private static final Color FOREGROUND_DISABLED = UIManager.getColor("textInactiveText");

  /**
   * The size of the focus border for consistency with the focus border. Otherwise you'll get
   * a 'waggle' in placement of the checkbox, where the in-focus checkbox is slightly offset.
   */
  private static final int FOCUS_BORDER_SIZE = 1;
  /**
   * A line border with an arrow when there is focus.
   */
  private static final Border FOCUS_ARROW_BORDER =
          new ArrowBorder(ArrowBorder.ICON_LENGTH, ArrowBorder.ICON_WIDTH,
                  ArrowBorder.ICON_PADDING, true, FOCUS_BORDER_SIZE);
  /**
   * The arrow icon for the header cell.
   */
  static final ArrowIcon ARROW_ICON = new ArrowIcon(SwingConstants.SOUTH, true,
          ArrowBorder.ICON_LENGTH, ArrowBorder.ICON_WIDTH);

  /**
   * An arrow border when keyboard focus is not on the cell.
   */
  private static final Border ARROW_BORDER = new ArrowBorder(ArrowBorder.ICON_LENGTH,
          ArrowBorder.ICON_WIDTH, ArrowBorder.ICON_PADDING, true, 0);
  /**
   * Editing interface to edit a stock exchange.
   */
  private final IExchangeEditor _exchangeEditor;

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
  public ExchangeComboTableColumn(MoneydanceGUI mdGui, int modelIndex, int width, StockExchange[] items,
                                  IExchangeEditor exchangeEditor) {
    super(modelIndex, width);
    _exchangeEditor = exchangeEditor;

    setCellRenderer(new ComboCellRenderer(mdGui));
    setCellEditor(new ComboCellEditor(items));
    final ComboCellRenderer renderer = new ComboCellRenderer(mdGui);
    renderer.setIsHeaderCell(true);
    setHeaderRenderer(renderer);
  }

  /**
   * The combo box cell renderer used to render the cell when the table is not in edit mode.
   */
  private final class ComboCellRenderer extends DefaultTableCellRenderer {
    /** The UI object to get colors from. */
    private final MoneydanceGUI _mdGui;
    /** True if this cell is in the header of the table. */
    private boolean _isHeaderCell = false;

    /**
     * Initialize the combo box renderer and set up the cell to have the same look and feel as
     * the rest of the table.
     * @param mdGui The main application UI object.
     */
    ComboCellRenderer(MoneydanceGUI mdGui) {
      _mdGui = mdGui;
    }

    @Override
    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected,
                                                   boolean hasFocus, int row, int column) {
      JLabel result = (JLabel) super.getTableCellRendererComponent(table, value, isSelected,
              hasFocus, row, column);
      result.setBorder(getComponentBorder(false, hasFocus));
      if(table==null) return result; // skip further configuration if table==null (ie the scrollpane is calculating sizes)
      if (_isHeaderCell) {
        final JTableHeader header = table.getTableHeader();
        if (header != null) {
          result.setForeground(header.getForeground());
          result.setBackground(header.getBackground());
          result.setFont(header.getFont());
        }
        result.setHorizontalAlignment(JLabel.CENTER);
        result.setIcon(ARROW_ICON);
        result.setHorizontalTextPosition(JLabel.LEFT);
      } else {
        if (isSelected) {
          result.setForeground(table.getSelectionForeground());
          result.setBackground(table.getSelectionBackground());
        } else {
          result.setForeground(table.getForeground());
          if (row % 2 == 0) {
            result.setBackground(_mdGui.getColors().homePageBG);
          } else {
            result.setBackground(_mdGui.getColors().homePageAltBG);
          }
        }
        SecuritySymbolTableModel model = (SecuritySymbolTableModel) table.getModel();
        result.setToolTipText(model.getToolTip(row, column));
      } // if not the header
      return result;
    }

    /**
     * Return the border to display around the component, according to the given properties.
     *
     * @param drawingForEditor If this renderer is drawing on the screen for the editor.
     * @param hasFocus         If keyboard focus is on the cell.
     * @return The border object for drawing the border
     */
    Border getComponentBorder(final boolean drawingForEditor, final boolean hasFocus) {
      if (_isHeaderCell) return UIManager.getBorder("TableHeader.cellBorder");
      if (drawingForEditor || hasFocus) {
        return FOCUS_ARROW_BORDER;
      }
      return ARROW_BORDER;
    }

    void setIsHeaderCell(boolean isHeader) {
      _isHeaderCell = isHeader;
    }

  }

  /**
   * The cell editor used to display the combo box when the table cell is in edit mode.
   */
  private final class ComboCellEditor
          extends DefaultCellEditor implements ActionListener {
    /** The component to display in the cells.  */
    private final JComboBox _comboBox;

    /**
     * Initialize the combo box editor and sets up the cell to have the same look and feel as
     * the rest of the table and adds the appropriate action listeners to handle combo box
     * actions and validation.
     *
     * @param items The items to add to the combo box.
     */
    ComboCellEditor(final Object[] items) {
      super(new JComboBox(new ComboListModel(items)));
      _comboBox = (JComboBox)editorComponent;
      _comboBox.setOpaque(false);
      // Java 1.5 does not handle the replacement UI correctly, it stretches the arrow button
      // opaque background across the entire cell, obscuring the text
      if ((_comboBox.getUI() instanceof MetalComboBoxUI) && (MoneydanceGUI.javaVersion >= 100600000)) {
        _comboBox.setUI(new MetalTableComboBoxUI());
      }
      _comboBox.setRenderer(new ComboBoxCellRenderer());

      // set this property so that the action event is only fired when a new
      // selection is finally made by clicking on it, or hitting the enter key.
      // if you do not set this, and user is traversing the combo with the arrows,
      // each time a selection is highlighted in the dropdown, the action event occurs.
      _comboBox.putClientProperty("JComboBox.isTableCellEditor", Boolean.TRUE);

      // must listen for the action event so we can hide the popup menu and fireEditingStopped
      _comboBox.addActionListener(this);

      _comboBox.addMouseListener(new MouseAdapter() {
        @Override
        public void mouseClicked(MouseEvent event) {
          if (SwingUtilities.isRightMouseButton(event) ||
                  (SwingUtilities.isLeftMouseButton(event) && (event.getClickCount() > 1))) {
            event.consume();
            showExchangeEditDialog();
          }
        }
      });
    }

    private void showExchangeEditDialog() {
      final StockExchange exchange = (StockExchange)_comboBox.getSelectedItem();
      _exchangeEditor.edit(exchange);
    }

    /**
     * Returns the value contained in the editor.
     *
     * @return the value contained in the editor
     */
    public Object getCellEditorValue() {
      return _comboBox.getSelectedItem();
    }

    /**
     * Invoked when an action occurs.
     *
     * @param event The action event.
     */
    public void actionPerformed(final ActionEvent event) {
      _comboBox.hidePopup();
      stopCellEditing();
    }
  }

  /**
   * ComboBoxUI to integrate the the table style into the combobox. Sets an empty border and
   * paints the appropriate colors when the box is disabled.
   */
  private static final class MetalTableComboBoxUI extends MetalComboBoxUI {
    /**
     * {@inheritDoc}
     */
    @Override
    protected JButton createArrowButton() {
      final JButton button = new JButton() {
        @Override
        public boolean isFocusable() {
          return false;
        }

        @Override
        public void setEnabled(final boolean enabled) {
          super.setEnabled(enabled);

          // Set the background and foreground to the combobox colors.
          if (!enabled) {
            setBackground(BACKGROUND_DISABLED);
            setForeground(FOREGROUND_DISABLED);
          }
        }
      };
      button.setMargin(new Insets(0, 1, 1, 3));
      button.setBorder(BorderFactory.createEmptyBorder());
      return button;
    }
  }

  /**
   * The column combo box list renderer.
   */
  private class ComboBoxCellRenderer extends DefaultListCellRenderer {
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
    @Override
    public Component getListCellRendererComponent(final JList list,
                                                  final Object value,
                                                  final int index,
                                                  final boolean isSelected,
                                                  final boolean cellHasFocus) {
      JLabel result = (JLabel)super.getListCellRendererComponent(list, value, index,
              isSelected, cellHasFocus);
      result.setText((value == null) ? N12EStockQuotes.EMPTY : value.toString());
      result.setBorder(BorderFactory.createEmptyBorder(0, 4, 0, 0));
      return result;
    }


  }

  /**
   * Combo box model that provides a set method to decrease the number of events on clear/set.
   */
  static class ComboListModel extends AbstractListModel implements ComboBoxModel {
    /**
     * The combo box items.
     */
    private Object[] _items;

    /**
     * The selected object.
     */
    private Object _selectedObject;

    /**
     * Initialize the combo box model.
     *
     * @param items The initial set of items.
     */
    ComboListModel(final Object[] items) {
      _items = items;
    }

    /**
     * Returns the length of the list.
     *
     * @return the length of the list
     */
    public int getSize() {
      return _items.length;
    }

    /**
     * Returns the value at the specified index.
     *
     * @param index the requested index
     * @return the value at <code>index</code>
     */
    public Object getElementAt(final int index) {
      return _items[index];
    }

    /**
     * Set the selected item. The implementation of this  method should notify all registered
     * <code>ListDataListener</code>s that the contents have changed.
     *
     * @param anObject the list object to select or <code>null</code> to clear the selection
     */
    public void setSelectedItem(final Object anObject) {
      if (_selectedObject != null && !_selectedObject.equals(anObject) ||
              _selectedObject == null && anObject != null) {
        _selectedObject = anObject;
        fireContentsChanged(this, -1, -1);
      }
    }

    /**
     * Returns the selected item
     *
     * @return The selected item or <code>null</code> if there is no selection
     */
    public Object getSelectedItem() {
      return _selectedObject;
    }
  }

}
