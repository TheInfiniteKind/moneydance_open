/*
 * ************************************************************************
 * Copyright (C) 2012-2015 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.moneydance.apps.md.view.gui.MDAction;
import com.moneydance.apps.md.view.gui.MDImages;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.GridC;
import com.moneydance.util.UiUtil;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.DefaultCellEditor;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.KeyStroke;
import javax.swing.ListSelectionModel;
import javax.swing.event.CellEditorListener;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableColumn;
import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

/**
 * Class to show and manage the list of ratio entries as well as the editing buttons.
 *
 * @author Kevin Menningen
 */
class RatioListView
    extends JPanel
    implements PropertyChangeListener {
  /** How tall should the list be so that this number of rows are visible? Includes header row. Contains all 6 example ratios */
  private static final int SHOW_ROWS_IN_LIST = 7;
  private final RatioSettingsController _controller;
  private final MoneydanceGUI _mdGui;

  private final JTable _table;
  private JScrollPane _includedHost;

  private final JButton _addItemButton;
  private final JButton _delItemButton;
  private final JButton _copyButton;
  private final JButton _moveUpButton;
  private final JButton _moveDownButton;
  private final JLabel _validWarning;

  private final MDAction _addAction;
  private final MDAction _deleteAction;

  /**
   * Constructor to allow many of the fields to be marked final.
   *
   * @param controller The dialog controller object to fire commands.
   * @param resources  An object capable of loading localized strings and showing dialogs.
   */
  public RatioListView(final RatioSettingsController controller, final MoneydanceGUI resources) {
    _controller = controller;
    _mdGui = resources;

    _table = new JTable();

    _addAction = MDAction.makeIconAction(_mdGui, _mdGui.getImages().getIcon(MDImages.PLUS), new ActionListener() {
      public void actionPerformed(ActionEvent evt) {
        doAddSelected();
      }
    });
    _addItemButton = new JButton(_addAction);
    _addItemButton.putClientProperty("JButton.buttonType", "segmentedTextured");
    _addItemButton.putClientProperty("JButton.segmentPosition", "first");

    _deleteAction = MDAction.makeIconAction(_mdGui, _mdGui.getImages().getIcon(MDImages.MINUS), new ActionListener() {
      public void actionPerformed(ActionEvent evt) {
        doRemoveSelected();
      }
    });
    _delItemButton = new JButton(_deleteAction);
    _delItemButton.putClientProperty("JButton.buttonType", "segmentedTextured");
    _delItemButton.putClientProperty("JButton.segmentPosition", "last");

    MDAction moveUpAction = MDAction.makeIconAction(_mdGui,
                                                    new ImageIcon(Main.getIcon(N12ERatios.ARROW_UP_ICON)),
                                                    new ActionListener() {
      public void actionPerformed(ActionEvent evt) {
        doMoveUpSelected();
      }
    });
    _moveUpButton = new JButton(moveUpAction);
    _moveUpButton.putClientProperty("JButton.buttonType", "segmentedTextured");
    _moveUpButton.putClientProperty("JButton.segmentPosition", "last");

    MDAction moveDownAction = MDAction.makeIconAction(_mdGui,
                                                      new ImageIcon(Main.getIcon(N12ERatios.ARROW_DOWN_ICON)),
                                                      new ActionListener() {
      public void actionPerformed(ActionEvent evt) {
        doMoveDownSelected();
      }
    });
    _moveDownButton = new JButton(moveDownAction);
    _moveDownButton.putClientProperty("JButton.buttonType", "segmentedTextured");
    _moveDownButton.putClientProperty("JButton.segmentPosition", "last");

    MDAction copyAction = MDAction.makeIconAction(_mdGui,
                                                  new ImageIcon(Main.getIcon(N12ERatios.COPY_ICON)),
                                                  new ActionListener() {
      public void actionPerformed(ActionEvent evt) {
        doCopySelected();
      }
    });
    _copyButton = new JButton(copyAction);
    _copyButton.putClientProperty("JButton.buttonType", "segmentedTextured");
    _copyButton.putClientProperty("JButton.segmentPosition", "last");

    _validWarning = new JLabel(N12ERatios.EMPTY);
  }

  /**
   * This method gets called when a bound property is changed.
   *
   * @param event A PropertyChangeEvent object describing the event source
   *              and the property that has changed.
   */
  public void propertyChange(final PropertyChangeEvent event) {
    refresh();
  }

  void addSelectionListener(final ListSelectionListener listener) {
    _table.getSelectionModel().addListSelectionListener(listener);
  }

  int getSelectedRow() {
    return _table.getSelectedRow();
  }

  /**
   * Setup the view window.
   */
  void layoutUI() {
    // in case we're laying out again, remove everything
    removeAll();

    setLayout(new BorderLayout(UiUtil.DLG_HGAP, UiUtil.DLG_VGAP));

    // border space around all components
    setBorder(BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.HGAP,
                                              UiUtil.DLG_VGAP*2, UiUtil.HGAP));
    // prepare the list
    setupItemsList();

    add(_includedHost, BorderLayout.CENTER);
    add(buildButtonPanel(), BorderLayout.SOUTH);
    validate();

    // the list starts with no selection, so get the rest of the UI to match
    clearSelections();

    // turn of automatic editing
    _table.putClientProperty(N12ERatios.JTABLE_AUTO_EDIT, Boolean.FALSE);

    // limit the vertical size so it doesn't initially take up so much space
    _table.setPreferredScrollableViewportSize(new Dimension(
        _table.getPreferredScrollableViewportSize().width,
        SHOW_ROWS_IN_LIST * _table.getRowHeight()));

    // setup key bindings
    _table.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(
        KeyStroke.getKeyStroke(KeyEvent.VK_DELETE, 0),
        N12ERatios.DELETE_ACTION_KEY);
    _table.getActionMap().put(N12ERatios.DELETE_ACTION_KEY, _deleteAction);
    _table.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(
        KeyStroke.getKeyStroke(KeyEvent.VK_INSERT, 0),
        N12ERatios.INSERT_ACTION_KEY);
    _table.getActionMap().put(N12ERatios.INSERT_ACTION_KEY, _addAction);
  }

  void selectFirstRow() {
    // first clear the selection so a selection change event may occur
    _table.clearSelection();
    if (_table.getRowCount() > 0) {
      _table.getSelectionModel().setSelectionInterval(0, 0);
    }
  }

  void doAddSelected() {
    // accept the current edits, otherwise they will edit the new data
    acceptUserEdits();

    int index = _table.getSelectedRow();
    if (index < 0) {
      index = _table.getModel().getRowCount();
    } else {
      // insert below
      ++index;
    }

    _controller.insertAt(index);

    // get focus back from the Add button
    _table.requestFocusInWindow();
    _table.getSelectionModel().setSelectionInterval(index, index);
    // automatically edit
    setEditingCell(index);
  }

  void doRemoveSelected() {
    // accept the current edits, otherwise they will edit the new data
    acceptUserEdits();
    // single select model
    int index = _table.getSelectedRow();
    if (index >= 0) {
      _controller.deleteItem(index);
      clearSelections();
      selectFirstRow();
    }

  }

  void doMoveUpSelected() {
    // accept the current edits, otherwise they will edit the new data
    acceptUserEdits();
    // single select model
    int index = _table.getSelectedRow();
    if (index > 0) {
      int newIndex = _controller.moveItemUp(index);
      ensureRowVisible(newIndex);
      _table.getSelectionModel().setSelectionInterval(newIndex, newIndex);
    }
  }

  void doMoveDownSelected() {
    // accept the current edits, otherwise they will edit the new data
    acceptUserEdits();
    // single select model
    int index = _table.getSelectedRow();
    if ((index >= 0) && (index < (_table.getRowCount() - 1))) {
      int newIndex = _controller.moveItemDown(index);
      ensureRowVisible(newIndex);
      _table.getSelectionModel().setSelectionInterval(newIndex, newIndex);
    }
  }

  void doCopySelected() {
    // accept the current edits, otherwise they will edit the new data
    acceptUserEdits();
    // single select model
    int index = _table.getSelectedRow();
    if (index >= 0) {
      int newIndex = _controller.copyItem(index);
      // make sure the editing row is visible
      ensureRowVisible(newIndex);
      // get focus back from the Copy button
      _table.requestFocusInWindow();
      _table.getSelectionModel().setSelectionInterval(newIndex, newIndex);
      // automatically edit
      setEditingCell(newIndex);
    }
  }

  private void ensureRowVisible(int rowIndex) {
    final Rectangle itemRect = _table.getCellRect(rowIndex, 0, true);
    _table.scrollRectToVisible(itemRect);
  }

  void acceptUserEdits() {
    if (_table.isEditing()) {
      _table.getCellEditor().stopCellEditing();
    }
  }

  void updateSelectedItem(final String editedText) {
    int index = _table.getSelectedRow();
    if (index >= 0) {
      _controller.updateItem(index, editedText);
    }
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private void refresh() {
    final Runnable repaintRunner = new Runnable() {
      /**
       * Run on a specific thread, possibly not the current one.
       * @see Thread#run()
       */
      public void run() {
        if (_includedHost != null) {
          _includedHost.repaint();
        }
        repaint();
      }
    };
    UiUtil.runOnUIThread(repaintRunner);
  }

  private void setupItemsList() {
    _table.setModel(_controller.getTableModel());
    _table.setBorder(BorderFactory.createEmptyBorder(0, UiUtil.HGAP, 0, UiUtil.HGAP));
    _includedHost = new JScrollPane(_table, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                                    JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

    // consistent row height with other tables in the application
    _table.setRowHeight(_table.getRowHeight() + 8);

    _table.setRowSelectionAllowed(true);
    _table.setColumnSelectionAllowed(false);
    _table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

    TableColumn column = _table.getColumnModel().getColumn(0);
    column.setCellRenderer(new ItemListCellRenderer(_mdGui));
    column.setCellEditor(new ItemListCellEditor());
    column.getCellEditor().addCellEditorListener(new CellEditorListener() {
      /**
       * This tells the listeners the editor has ended editing
       */
      public void editingStopped(ChangeEvent event) {
        ItemListCellEditor source = (ItemListCellEditor) event.getSource();
        updateSelectedItem(source.getEditedText());
      }

      /**
       * This tells the listeners the editor has canceled editing
       */
      public void editingCanceled(ChangeEvent event) {
        // do nothing
      }
    });
  }

  private JPanel buildButtonPanel() {
    final JPanel buttonPanel = new JPanel(new GridBagLayout());
    buttonPanel.add(_addItemButton, GridC.getc(0, 0).north());
    buttonPanel.add(_delItemButton, GridC.getc(1, 0).fillboth());
    buttonPanel.add(_copyButton, GridC.getc(2, 0).north());
    buttonPanel.add(_moveUpButton, GridC.getc(3, 0).north());
    buttonPanel.add(_moveDownButton, GridC.getc(4, 0).north());
    buttonPanel.add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), GridC.getc(5, 0).wx(1));
    buttonPanel.add(_validWarning, GridC.getc(6, 0).east());
    return buttonPanel;
  }

  void clearSelections() {
    _table.clearSelection();
    _table.requestFocusInWindow();
  }

  /**
   * Sets the editing cell in the table and sends focus to it.
   *
   * @param row The row index of the cell to start editng.
   */
  private void setEditingCell(final int row) {
    _table.editCellAt(row, 0);
    if (_table.isEditing()) {
      _table.getEditorComponent().requestFocus();
    } else {
      _table.requestFocus();
    }
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Inner Classes
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * Cell renderer for the list, colors items that are in-use.
   */
  private class ItemListCellRenderer
      extends DefaultTableCellRenderer {
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

      return result;
    }

  }

  /**
   * Cell editor for in-place editing
   */
  private class ItemListCellEditor
      extends DefaultCellEditor {
    private String _value;

    public ItemListCellEditor() {
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
}
