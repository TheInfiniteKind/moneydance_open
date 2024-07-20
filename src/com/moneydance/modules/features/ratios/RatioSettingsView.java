/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.moneydance.awt.GridC;
import com.moneydance.util.UiUtil;

import java.awt.GridBagLayout;
import java.awt.event.FocusListener;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;
import java.awt.Font;
import java.util.ArrayList;
import java.util.List;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;


/**
 * <p>The view for the ratios settings dialog.</p>
 *
 * @author Kevin Menningen
 */
class RatioSettingsView
    extends JPanel
    implements PropertyChangeListener {
  private final RatioSettingsModel _model;
  private final MoneydanceGUI _mdGui;
  private RatioSettingsController _controller;
  private final ResourceProvider _resources;

  // controls
  private RatioListView _list;
  private RatioEntryEditorView _editor;
  private JComboBox _decimalPlaces;

  private boolean _initialized = false;

  public RatioSettingsView(MoneydanceGUI mdGui, final RatioSettingsModel model, final ResourceProvider resources) {
    _mdGui = mdGui;
    _model = model;
    _resources = resources;
  }

  /**
   * This method gets called when a bound property is changed.
   *
   * @param event A PropertyChangeEvent object describing the event source
   *              and the property that has changed.
   */

  public void propertyChange(final PropertyChangeEvent event) {
    final String eventName = event.getPropertyName();
    final boolean all = BasePropertyChangeReporter.ALL_PROPERTIES.equals(eventName);

    // list change
    if (all || N12ERatios.RATIO_LIST_CHANGE.equals(eventName)) {
      if (_initialized) loadControlsFromData(false);
    } else if (N12ERatios.RATIO_LIST_RESET.equals(eventName)) {
      _list.selectFirstRow();
    }
    refresh();
  }


  private void refresh() {
    final Runnable repaintRunner = new Runnable() {
      /**
       * Run on a specific thread, possibly not the current one.
       * @see Thread#run()
       */
      public void run() {
        if (_initialized) {
          _editor.repaint();
          repaint();
        }
      }
    };
    UiUtil.runOnUIThread(repaintRunner);
  }

  void layoutUI() {
    setLayout(new GridBagLayout());
    setBorder(BorderFactory.createEmptyBorder(UiUtil.DLG_VGAP, UiUtil.DLG_HGAP,
                                              UiUtil.DLG_VGAP, UiUtil.DLG_HGAP));
    int y = 0;
    add(_list, GridC.getc(0,y++).wxy(1,1).colspan(3).fillboth());
    add(_editor, GridC.getc(0,y++).wx(1).colspan(3).fillx());
    add(Box.createVerticalStrut(UiUtil.DLG_VGAP), GridC.getc(0,y++));
    JLabel generalLabel = new JLabel(_resources.getString(L10NRatios.GENERAL_SETTINGS));
    generalLabel.setFont(generalLabel.getFont().deriveFont(Font.BOLD));
    add(generalLabel, GridC.getc(0, y++).west());
    add(Box.createVerticalStrut(UiUtil.VGAP), GridC.getc(0,y));
    add(Box.createHorizontalStrut(70), GridC.getc(1, y++).field());
    add(new JLabel(RatiosUtil.getLabelText(_resources, L10NRatios.DECIMALS)), GridC.getc(0, y).label());
    add(_decimalPlaces, GridC.getc(1, y).field());
    add(Box.createHorizontalStrut(UiUtil.DLG_HGAP), GridC.getc(2, y).wx(2).fillx());
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Package Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  void setController(final RatioSettingsController controller) {
    _controller = controller;

    createControls();
    _initialized = true;
  }

  void loadControlsFromData(final boolean selectFirstRow) {
    if (selectFirstRow) _list.selectFirstRow();
    _decimalPlaces.setSelectedIndex(_model.getEditingSettings().getDecimalPlaces());
  }

  void saveControlsToData() {
    // save what the user has entered now
    _list.acceptUserEdits();
    _editor.saveControlsToData();
    // save global settings
    final int decimalPlaces = Integer.valueOf((String)_decimalPlaces.getSelectedItem()).intValue();
    _model.getEditingSettings().setDecimalPlaces(decimalPlaces);
    // save the list from the table model
    final int entryCount = _model.getTableModel().getRowCount();
    final List<String> ratioSettingsList = new ArrayList<String>(entryCount);
    for (int index = 0; index < entryCount; index++) {
      RatioEntry ratio = _model.getTableModel().getRatioEntry(index);
      ratio.setIndex(index);
      ratioSettingsList.add(ratio.getSettingsString());
    }
    _model.getEditingSettings().setRatioEntryList(ratioSettingsList);
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private void createControls() {
    setupList();
    setupEditor();
    setupDecimalPlaces();
  }

  private void setupDecimalPlaces() {
    String[] decimalOptions = new String[5];
    for (int index = 0; index < 5; index++) decimalOptions[index] = Integer.toString(index);
    _decimalPlaces = new JComboBox(decimalOptions);
  }

  private void setupList() {
    _list = new RatioListView(_controller, _mdGui);
    _list.layoutUI();
    _list.addSelectionListener(new ListSelectionListener() {
      public void valueChanged(ListSelectionEvent event) {
        if (event.getValueIsAdjusting()) return;
        final int index = _list.getSelectedRow();
        if (index >= 0) {
          RatioEntry ratio = _model.getTableModel().getRatioEntry(index);
          _editor.setRatio(ratio);
        }
      }
    });
  }

  private void setupEditor() {
    _editor = new RatioEntryEditorView(_resources, _mdGui);
    _editor.layoutUI();
    final FocusListener listener = new ColoredParentFocusAdapter(_editor);
    RatiosUtil.recurseAddFocusListener(_editor, listener);
  }

}