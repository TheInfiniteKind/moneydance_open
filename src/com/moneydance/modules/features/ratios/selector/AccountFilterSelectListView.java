/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios.selector;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.AccountTreeCellRenderer;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.*;
import com.moneydance.modules.features.ratios.L10NRatios;
import com.moneydance.modules.features.ratios.ResourceProvider;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.table.*;
import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.GridBagLayout;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;
import java.util.ArrayList;
import java.util.List;


/**
 * <p>View for a control that allows the user to select one or more accounts and shows the selected
 * accounts in a table.</p>
 * <p/>
 * <p>This control has a special selector control with a comma-separated list of clickable shortcuts
 * for quickly selecting accounts, plus a table of accounts.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class AccountFilterSelectListView
    extends JPanel
    implements PropertyChangeListener {
  private final AccountFilterSelectListController _controller;

  private JTable _table;

  AccountFilterSelectListView(final AccountFilterSelectListController controller) {
    setLayout(new GridBagLayout());
    _controller = controller;
  }

  public void layoutViewUI() {
    setupTable();
    setupTableColumns();
    add(new JScrollPane(_table, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                        JScrollPane.HORIZONTAL_SCROLLBAR_NEVER),
        GridC.getc(0, 1).wxy(1, 1).fillboth());
  }


  @Override
  public void setVisible(boolean isVisible) {
    if (isVisible) setupTableColumns();
    super.setVisible(isVisible);
  }


  @Override
  public void setEnabled(boolean enabled) {
    super.setEnabled(enabled);

    // enable individually so the scroll bar does not become disabled, allowing the user to
    // scroll through the list even if it is disabled
    enableTable(enabled);

    // this doesn't really work currently but doesn't hurt either
    if (_table.getTableHeader() != null) {
      recurseEnable(_table.getTableHeader(), enabled);
    }
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Interface PropertyChangeListener
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * This method gets called when a bound property is changed.
   *
   * @param event A PropertyChangeEvent object describing the event source
   *              and the property that has changed.
   */
  public void propertyChange(PropertyChangeEvent event) {
    final String eventId = event.getPropertyName();
//        if (N12ESelector.FILTER_CHANGE.equals(eventId))
//        {
//            updateModeLabel();
//        }
//        if (N12ESelector.SELECTION_MODE_CHANGE.equals(eventId))
//        {
//            updateModeLabel();
//        }
  }


  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Private Methods
  //////////////////////////////////////////////////////////////////////////////////////////////

  private void enableTable(final boolean enabled) {
    recurseEnable(_table, enabled);
  }

  /**
   * Enable or disable a component and all of its children, grandchildren, etc.
   *
   * @param parent  The parent component to enable or disable.
   * @param enabled True to enable, false to disable.
   */
  private static void recurseEnable(final Component parent, final boolean enabled) {
    parent.setEnabled(enabled);

    if (parent instanceof Container) {
      for (final Component child : ((Container) parent).getComponents()) {
        recurseEnable(child, enabled);
      }
    }
  }

  private void setupTable() {
    TableColumnModel columnModel = new DefaultTableColumnModel();
    final ResourceProvider resources = _controller.getResourceProvider();

    TableColumn column = new TableColumn(AccountFilterSelectListTableModel.NAME_INDEX);
    columnModel.addColumn(column);

    final SelectCellEditor selectColumnEditor = new SelectCellEditor(resources, _controller.getMDGUI());
    column = new TableColumn(AccountFilterSelectListTableModel.SEL_INDEX);
//    column = new TableColumn(AccountSelectListTableModel.SEL_INDEX, 300,
//                             new SelectCellRenderer(resources),
//                             selectColumnEditor);
    columnModel.addColumn(column);

    _table = new JTable();
    final AccountTableCellRenderer defaultRenderer = new AccountTableCellRenderer(
        _controller.getMDGUI());
    final SelectCellRenderer selectColumnRenderer = new SelectCellRenderer(resources, _controller.getMDGUI());
    _table.setDefaultRenderer(String.class, defaultRenderer);
    _table.setDefaultRenderer(FilterSelection.class, selectColumnRenderer);
    _table.setDefaultEditor(FilterSelection.class, selectColumnEditor);
    _table.setColumnModel(columnModel);

    // ensure the text is not cut off
    FontMetrics fm = defaultRenderer.getFontMetrics(_table.getFont());
    _table.setRowHeight(fm.getHeight());

    AccountFilterSelectListTableModel tableModel = new AccountFilterSelectListTableModel(_controller);
    _controller.setTableModel(tableModel);
    _table.setModel(tableModel);

    // initial load
    _controller.loadData();

    // turn off line drawing in the table and don't show a header
    _table.setShowGrid(false);
    _table.setRowMargin(0);
    _table.setTableHeader(null); // turn off the header
    _table.setCellSelectionEnabled(false);

  }

  private void setupTableColumns() {
    // these column widths are experimentally derived from the default size of the graph window
    _table.getColumnModel().getColumn(AccountFilterSelectListTableModel.NAME_INDEX).setPreferredWidth(250);
    _table.getColumnModel().getColumn(AccountFilterSelectListTableModel.SEL_INDEX).setPreferredWidth(300);
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Inner Classes
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * Cell renderer for the list, colors items that are in-use. This renderer is very similar to
   * the stock Moneydance AccountTreeCellRenderer, except that it gives more control over the
   * background color, does not display the account type (we've added header rows for that)
   * and uses the JLabel control for rendering the text and icon.
   */
  private class AccountTableCellRenderer
      extends DefaultTableCellRenderer {
    private static final int INDENT_SHIFT = 14;

    private final AccountTreeCellRenderer _defaultRenderer;
    private final Color _normalBackColor;
    private final Color _headerBackColor;
    private final Border[] _indentBorders;
    private final String _inactiveTooltip;
    private Font _normalFont = null;
    private Font _smallFont = null;
    private Font _boldFont = null;

    AccountTableCellRenderer(final MoneydanceGUI mdGUI) {
      _defaultRenderer = new AccountTreeCellRenderer(mdGUI);
      _normalBackColor = mdGUI.getColors().homePageBG;
      _headerBackColor = mdGUI.getColors().headerBG;
      _inactiveTooltip = mdGUI.getStr(L10NRatios.ACCOUNT_INACTIVE);
      setHorizontalTextPosition(JLabel.RIGHT);
      setVerticalTextPosition(JLabel.CENTER);
      int maxDepth = getMaxDepth(mdGUI.getCurrentAccount()) + 1; // add one for root
      _indentBorders = new Border[maxDepth];
      for (int depth = 0; depth < maxDepth; depth++) {
        _indentBorders[depth] = BorderFactory.createEmptyBorder(0, depth*INDENT_SHIFT, 0, 0);
      }
    }

    private int getMaxDepth(Account root) {
      int result = 0;
      AccountIterator iterator = new AccountIterator(root);
      while (iterator.hasNext()) {
        result = Math.max(result, iterator.next().getDepth());
      }
      return result;
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
      JLabel result = (JLabel) super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
      initFonts(result.getFont());
      final AccountFilterSelectListTableEntry entry = ((AccountFilterSelectListTableModel) table.getModel()).getEntry(row);
      boolean enabled = table.isEnabled();
      if (entry.isHeader()) {
        // header
        result.setBackground(_headerBackColor);
        result.setIcon(null);
        result.setFont(_boldFont);
      } else {
        result.setBackground(_normalBackColor);
        final Account account = (Account) value;
        result.setText(account.getAccountName());
        result.setIcon(_defaultRenderer.getIconForAccount(account));
        result.setToolTipText(_controller.getTooltip(row));
        result.setBorder(_indentBorders[account.getDepth()]);
        if (account.getAccountOrParentIsInactive()) {
          enabled = false;
          result.setToolTipText(_inactiveTooltip);
        }
        result.setFont((account.getDepth() > 1) ? _smallFont : _normalFont);
      }
      result.setEnabled(enabled);
      return result;
    }

    private void initFonts(Font font) {
      if (_normalFont == null) {
        _normalFont = UIManager.getFont("ComboBox.font");
        if (_normalFont == null) _normalFont = font;
        _smallFont = new Font(_normalFont.getName(), Font.PLAIN, _normalFont.getSize() - 1);
        _boldFont = _normalFont.deriveFont(Font.BOLD);
      }
    }

  }

  /**
   * Acts as a common renderer for both the table cell renderer and the table cell editor,
   * so as to have a consistent appearance for both.
   */
  static class DualAccountSelectorRenderer {
    private final ClickLabelSelector _control;
    private final Color _normalBackground;
    private final Color _normalForeground;
    private final Color _normalSelectedBackground = UIManager.getColor("textHighlight");
    private final Color _normalSelectedForeground = UIManager.getColor("textHighlightText");
    private final Color _headerBackground;
    private final Color _headerForeground;
    private final Color _headerSelectedBackground = Color.DARK_GRAY;
    private final Color _headerSelectedForeground = Color.WHITE;


    DualAccountSelectorRenderer(final ResourceProvider resources, final MoneydanceGUI mdGUI) {
      _normalBackground = mdGUI.getColors().homePageBG;
      _normalForeground = mdGUI.getColors().homePageFG;
      _headerBackground = mdGUI.getColors().headerBG;
      // same foreground for header items, headerFG color is not used anywhere in MD
      _headerForeground = mdGUI.getColors().homePageFG;
      final List<String> items = new ArrayList<String>();
      items.add(resources.getString(FilterSelection.REQUIRED.getResourceKey()));
      items.add(resources.getString(FilterSelection.ALLOWED.getResourceKey()));
      items.add(resources.getString(FilterSelection.DISALLOWED.getResourceKey()));
      _control = new ClickLabelSelector(items, 1);
    }

    ClickLabelSelector getControl() {
      return _control;
    }

    JPanel getView() {
      return _control.getView();
    }

    void setupRenderer(final JTable table, final int rowIndex, final FilterSelection filterSelection) {
      final boolean enabled = table.isEnabled();
      _control.setEnabled(enabled);

      _control.setForeground(table.getForeground());
      final AccountFilterSelectListTableEntry entry = ((AccountFilterSelectListTableModel) table.getModel()).getEntry(rowIndex);
      if (entry.isHeader()) {
        // header
        _control.setBackground(_headerBackground);
        _control.setForeground(_headerForeground);
        _control.setSelectionBackground(_headerSelectedBackground);
        _control.setSelectionForeground(_headerSelectedForeground);
      } else {
        _control.setBackground(_normalBackground);
        _control.setForeground(_normalForeground);
        _control.setSelectionBackground(_normalSelectedBackground);
        _control.setSelectionForeground(_normalSelectedForeground);
      }
      if (filterSelection != null) {
        if (FilterSelection.REQUIRED.equals(filterSelection)) {
          _control.setSelectedIndex(0);
        } else if (FilterSelection.DISALLOWED.equals(filterSelection)) {
          _control.setSelectedIndex(2);
        } else {
          _control.setSelectedIndex(1);
        }
      } else {
        // nothing is selected
        _control.setSelectedIndex(-1);
      }
    }
  }

  /**
   * Renderer for the table cell that allows the user to pick whether an account or account type
   * is required, disallowed, or allowed.
   */
  static class SelectCellRenderer
      implements TableCellRenderer {
    private final DualAccountSelectorRenderer _renderer;

    public SelectCellRenderer(final ResourceProvider resources, final MoneydanceGUI mdGUI) {
      super();
      _renderer = new DualAccountSelectorRenderer(resources, mdGUI);
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus,
                                                   int row, int column) {
      _renderer.setupRenderer(table, row, (FilterSelection)value);
      return _renderer.getView();
    }
  }

  /**
   * Editor for the table cell that allows the user to pick whether an account or account type
   * is required, disallowed, or allowed.
   */
  static class SelectCellEditor
      extends AbstractCellEditor
      implements TableCellEditor, PropertyChangeListener {
    private final DualAccountSelectorRenderer _renderer;

    public SelectCellEditor(final ResourceProvider resources, final MoneydanceGUI mdGUI) {
      super();
      _renderer = new DualAccountSelectorRenderer(resources, mdGUI);
      // listen for when the user changes the filter
      _renderer.getControl().addPropertyChangeListener(this);
    }

    /**
     * The user changed the value of the editor, so we stop editing to save the value
     * @param event Event information
     */
    public void propertyChange(PropertyChangeEvent event) {
      final String eventName = event.getPropertyName();
      if (ClickLabelSelectorModel.SELECTION_CHANGE.equals(eventName)) {
        // new selection, the editor is done editing, store value and update
        stopCellEditing();
      }
    }

    public Object getCellEditorValue() {
      final int index = _renderer.getControl().getSelectedIndex();
      if (index == 0) return FilterSelection.REQUIRED;
      if (index == 1) return FilterSelection.ALLOWED;
      if (index == 2) return FilterSelection.DISALLOWED;
      return null;
    }

    public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) {
      _renderer.setupRenderer(table, row, (FilterSelection)value);
      return _renderer.getView();
    }
  }
}
