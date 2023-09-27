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

import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.ratios.selector.AccountFilterSelectLabel;
import com.moneydance.modules.features.ratios.selector.RatioAccountSelector;
import com.infinitekind.util.StringUtils;
import com.moneydance.util.UiUtil;

import javax.swing.*;
import java.awt.Color;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;

/**
 * Displays a UI to edit a ratio specification.
 *
 * @author Kevin Menningen
 */
class RatioEntryEditorView extends JPanel {
  private final ResourceProvider _resources;
  private final MoneydanceGUI _mdGui;
  private final char _decimal;
  private final Color _errorBackground = new Color(240, 140, 140);
  private final Color _normalBackground = UIManager.getColor("TextField.background");

  private JCheckBox _showPercent;
  private JCheckBox _alwaysPositive;
  private JCheckBox _useTaxDate;

  private MatchSelectorModel _numeratorMatchModel;
  private JComboBox _numeratorMatchSelector;
  private JLabel _numeratorLabelLabel;
  private JTextField _numeratorLabelField;
  private AccountFilterSelectLabel _numeratorDualAcctSelector;
  private TxnTagFilterView _numeratorTagsView;

  private MatchSelectorModel _denominatorMatchModel;
  private JComboBox _denominatorMatchSelector;
  private JLabel _denominatorLabelLabel;
  private JTextField _denominatorLabelField;
  private AccountFilterSelectLabel _denominatorDualAcctSelector;
  private TxnTagFilterView _denominatorTagsView;

  private JTextArea _notesField;

  private RatioEntry _editingRatio = null;

  RatioEntryEditorView(ResourceProvider resources, MoneydanceGUI mdGui) {
    _resources = resources;
    _mdGui = mdGui;
    _decimal = mdGui.getPreferences().getDecimalChar();
  }

  void layoutUI() {
    setLayout(new GridBagLayout());
    setBorder(BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.HGAP,
                                              UiUtil.VGAP, UiUtil.HGAP));
    setOpaque(true);

    setupAccountSelectors();
    setupTagFilters();

    int y = 0;
    // options
    JPanel optionPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, UiUtil.DLG_HGAP * 2, 0));
    optionPanel.setOpaque(false);
    _showPercent = new JCheckBox(_resources.getString(L10NRatios.SHOW_PERCENT));
    _showPercent.setOpaque(false);
    optionPanel.add(_showPercent);
    _alwaysPositive = new JCheckBox(_resources.getString(L10NRatios.ALWAYS_POSITIVE));
    _alwaysPositive.setOpaque(false);
    optionPanel.add(_alwaysPositive);
    _useTaxDate = new JCheckBox(_mdGui.getStr(L10NRatios.USE_TAX_DATE));
    _useTaxDate.setOpaque(false);
    optionPanel.add(_useTaxDate);
    add(optionPanel, GridC.getc(1, y++));
    add(new JSeparator(), GridC.getc(1, y).fillx());
    add(Box.createVerticalStrut(UiUtil.DLG_VGAP), GridC.getc(0, y++));

    // numerator and denominator - share 1/2 width with a gap in between
    JPanel split50 = new JPanel(new GridLayout(1, 2, UiUtil.DLG_HGAP * 2, 0));
    split50.setOpaque(false);
    JPanel numeratorPanel = createNumeratorPanel();
    JPanel denominatorPanel = createDenominatorPanel();
    split50.add(numeratorPanel);
    split50.add(denominatorPanel);
    add(split50, GridC.getc(0, y++).colspan(2).wxy(1, 1).fillboth());

    // extra space before notes
    add(Box.createVerticalStrut(UiUtil.DLG_VGAP), GridC.getc(0, y++));
    add(new JLabel(UiUtil.getLabelText(_mdGui, L10NRatios.NOTES)), GridC.getc(0, y++).west());
    // force the notes field to be 4 rows tall
    _notesField = new JTextArea(4, 10);
    int height = _notesField.getPreferredSize().height + 4; // add 4 for the border
    add(Box.createVerticalStrut(height), GridC.getc(2, y));
    add(new JScrollPane(_notesField, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                        JScrollPane.HORIZONTAL_SCROLLBAR_NEVER),
        GridC.getc(0, y).colspan(2).rowspan(3).wy(1).fillboth());
    addEventListeners();
  }

  private JPanel createNumeratorPanel() {
    int y = 0;
    JPanel numeratorPanel = new JPanel(new GridBagLayout());
    numeratorPanel.setOpaque(false);
    JLabel label = new JLabel(_resources.getString(L10NRatios.NUMERATOR));
    Font boldFont = label.getFont().deriveFont(Font.BOLD);
    label.setFont(boldFont);
    numeratorPanel.add(label, GridC.getc(1, y++).west());
    numeratorPanel.add(Box.createVerticalStrut(UiUtil.VGAP), GridC.getc(1, y++));
    _numeratorLabelLabel = new JLabel(RatiosUtil.getLabelText(_resources, L10NRatios.LABEL));
    numeratorPanel.add(_numeratorLabelLabel, GridC.getc(1, y).label());
    _numeratorLabelField = new JTextField();
    numeratorPanel.add(_numeratorLabelField, GridC.getc(3, y++).field());
    // account filtering
    numeratorPanel.add(new JLabel(UiUtil.getLabelText(_mdGui, L10NRatios.ACCOUNTS)), GridC.getc(1, y).label());
    _numeratorDualAcctSelector.layoutUI();
    numeratorPanel.add(_numeratorDualAcctSelector, GridC.getc(3, y++).field());
    // transaction filtering
    numeratorPanel.add(new JLabel(RatiosUtil.getLabelText(_resources, L10NRatios.TXN_MATCH)), GridC.getc(1, y).label().insets(
      GridC.TOP_FIELD_INSET, 0, GridC.BOTTOM_FIELD_INSET + UiUtil.DLG_VGAP, 0));
    _numeratorMatchModel = new MatchSelectorModel(_resources);
    _numeratorMatchSelector = new JComboBox(_numeratorMatchModel);
    numeratorPanel.add(_numeratorMatchSelector, GridC.getc(3, y++).wx(1).fillx().insets(
        GridC.TOP_FIELD_INSET, 0,  GridC.BOTTOM_FIELD_INSET + UiUtil.DLG_VGAP, 0));
    // tag filtering
    numeratorPanel.add(new JLabel(UiUtil.getLabelText(_mdGui, L10NRatios.FILTER_BY_TAG)), GridC.getc(1, y).label().north());
    numeratorPanel.add(_numeratorTagsView, GridC.getc(3, y++).field());
    return numeratorPanel;
  }

  private JPanel createDenominatorPanel() {
    int y = 0;
    JPanel denominatorPanel = new JPanel(new GridBagLayout());
    denominatorPanel.setOpaque(false);
    JLabel label = new JLabel(_resources.getString(L10NRatios.DENOMINATOR));
    Font boldFont = label.getFont().deriveFont(Font.BOLD);
    label.setFont(boldFont);
    denominatorPanel.add(label, GridC.getc(1, y++).west());
    denominatorPanel.add(Box.createVerticalStrut(UiUtil.VGAP), GridC.getc(1, y++));
    _denominatorLabelLabel = new JLabel(RatiosUtil.getLabelText(_resources, L10NRatios.LABEL));
    denominatorPanel.add(_denominatorLabelLabel, GridC.getc(1, y).label());
    _denominatorLabelField = new JTextField();
    denominatorPanel.add(_denominatorLabelField, GridC.getc(3, y++).field());
    // account filtering
    denominatorPanel.add(new JLabel(UiUtil.getLabelText(_mdGui, L10NRatios.ACCOUNTS)), GridC.getc(1, y).label());
    _denominatorDualAcctSelector.layoutUI();
    denominatorPanel.add(_denominatorDualAcctSelector, GridC.getc(3, y++).field());
    // transaction filtering
    denominatorPanel.add(new JLabel(RatiosUtil.getLabelText(_resources, L10NRatios.TXN_MATCH)), GridC.getc(1, y).label().insets(
      GridC.TOP_FIELD_INSET, 0, GridC.BOTTOM_FIELD_INSET + UiUtil.DLG_VGAP, 0));
    _denominatorMatchModel = new MatchSelectorModel(_resources);
    _denominatorMatchSelector = new JComboBox(_denominatorMatchModel);
    denominatorPanel.add(_denominatorMatchSelector, GridC.getc(3, y++).wx(1).fillx().insets(
        GridC.TOP_FIELD_INSET, 0, GridC.BOTTOM_FIELD_INSET + UiUtil.DLG_VGAP, 0));
    // tag filtering
    denominatorPanel.add(new JLabel(UiUtil.getLabelText(_mdGui, L10NRatios.FILTER_BY_TAG)), GridC.getc(1, y).label().north());
    denominatorPanel.add(_denominatorTagsView, GridC.getc(3, y++).field());
    return denominatorPanel;
  }

  private void addEventListeners() {
    final ItemListener numeratorListener = new ItemListener() {
      public void itemStateChanged(ItemEvent e) {
        enableNumeratorControls();
      }
    };
    _numeratorMatchSelector.addItemListener(numeratorListener);
    _numeratorLabelField.addFocusListener(new FocusAdapter() {
      public void focusLost(FocusEvent e) {
        validateNumeratorLabel();
      }
    });

    final ItemListener denominatorListener = new ItemListener() {
      public void itemStateChanged(ItemEvent e) {
        enableDenominatorControls();
      }
    };
    _denominatorMatchSelector.addItemListener(denominatorListener);
    _denominatorLabelField.addFocusListener(new FocusAdapter() {
      public void focusLost(FocusEvent e) {
        validateDenominatorLabel();
      }
    });
  }

  private void validateDenominatorLabel() {
    TxnMatchLogic logic = _denominatorMatchModel.getSelectedMatchLogic();
    if (TxnMatchLogic.CONSTANT.equals(logic)) {
      String text = _denominatorLabelField.getText().trim();
      boolean isError = StringUtils.isBlank(text);
      if (!isError) {
        isError = RatiosUtil.getConstantError(text, _decimal, false);
        if (isError) {
          _denominatorLabelField.setBackground(_errorBackground);
        } else {
          _denominatorLabelField.setBackground(_normalBackground);
          _denominatorLabelField.setText(StringUtils.formatRate(RatiosUtil.getConstantValue(text, _decimal, false, 1.0), _decimal));
        }
      } else {
        _denominatorLabelField.setBackground(_errorBackground);
      }
    } else {
      _denominatorLabelField.setBackground(_normalBackground);
    }
  }

  private void validateNumeratorLabel() {
    TxnMatchLogic logic = _numeratorMatchModel.getSelectedMatchLogic();
    if (TxnMatchLogic.CONSTANT.equals(logic)) {
      String text = _numeratorLabelField.getText().trim();
      boolean isError = StringUtils.isBlank(text);
      if (!isError) {
        isError = RatiosUtil.getConstantError(text, _decimal, true);
        if (isError) {
          _numeratorLabelField.setBackground(_errorBackground);
        } else {
          _numeratorLabelField.setBackground(_normalBackground);
          _numeratorLabelField.setText(StringUtils.formatRate(RatiosUtil.getConstantValue(text, _decimal, true, 0.0), _decimal));
        }
      } else {
        _numeratorLabelField.setBackground(_errorBackground);
      }
    } else {
      _numeratorLabelField.setBackground(_normalBackground);
    }
  }

  private void enableNumeratorControls() {
    TxnMatchLogic logic = _numeratorMatchModel.getSelectedMatchLogic();
    final boolean enabled = !RatiosUtil.isAccountBalanceType(logic) && !TxnMatchLogic.CONSTANT.equals(logic);
    _numeratorTagsView.setEnabled(enabled);
    // if both parts are using balances, tax date is useless
    if (!enabled && RatiosUtil.isAccountBalanceType(_denominatorMatchModel.getSelectedMatchLogic())) {
      _useTaxDate.setEnabled(false);
    } else {
      _useTaxDate.setEnabled(true);
    }
    if (TxnMatchLogic.CONSTANT.equals(logic)) {
      _numeratorLabelLabel.setText(RatiosUtil.getLabelText(_resources, L10NRatios.CONSTANT));
    } else {
      _numeratorLabelLabel.setText(RatiosUtil.getLabelText(_resources, L10NRatios.LABEL));
    }
    validateNumeratorLabel();
  }

  private void enableDenominatorControls() {
    TxnMatchLogic logic = _denominatorMatchModel.getSelectedMatchLogic();
    final boolean enabled = !RatiosUtil.isAccountBalanceType(logic) && !TxnMatchLogic.CONSTANT.equals(logic);
    _denominatorTagsView.setEnabled(enabled);
    // if both parts are using balances, tax date is useless
    if (!enabled && RatiosUtil.isAccountBalanceType(_numeratorMatchModel.getSelectedMatchLogic())) {
      _useTaxDate.setEnabled(false);
    } else {
      _useTaxDate.setEnabled(true);
    }
    if (TxnMatchLogic.CONSTANT.equals(logic)) {
      _denominatorLabelLabel.setText(RatiosUtil.getLabelText(_resources, L10NRatios.CONSTANT));
    } else {
      _denominatorLabelLabel.setText(RatiosUtil.getLabelText(_resources, L10NRatios.LABEL));
    }
    validateDenominatorLabel();
  }

  void setRatio(RatioEntry ratio) {
    // first save current settings back to the previous entry
    saveControlsToData();
    if ((ratio != null) && ratio.equals(_editingRatio)) return;
    _editingRatio = ratio;
    // then reload with the new stuff
    loadControlsFromData();
  }

  void saveControlsToData() {
    if (_editingRatio == null) return;
    _editingRatio.setShowPercent(_showPercent.isSelected());
    _editingRatio.setAlwaysPositive(_alwaysPositive.isSelected());
    _editingRatio.setUseTaxDate(_useTaxDate.isSelected());
    _editingRatio.setNumeratorMatchingLogic(_numeratorMatchModel.getSelectedMatchLogic());
    _editingRatio.setDenominatorMatchingLogic(_denominatorMatchModel.getSelectedMatchLogic());
    _editingRatio.setNumeratorLabel(_numeratorLabelField.getText());
    _editingRatio.setDenominatorLabel(_denominatorLabelField.getText());
    _editingRatio.setNumeratorRequiredAccounts(_numeratorDualAcctSelector.getRequiredAccountFilter(), _mdGui.getCurrentBook());
    _editingRatio.setNumeratorDisallowedAccounts(_numeratorDualAcctSelector.getDisallowedAccountFilter(), _mdGui.getCurrentBook());
    _editingRatio.setDenominatorRequiredAccounts(_denominatorDualAcctSelector.getRequiredAccountFilter(), _mdGui.getCurrentBook());
    _editingRatio.setDenominatorDisallowedAccounts(_denominatorDualAcctSelector.getDisallowedAccountFilter(), _mdGui.getCurrentBook());
    _editingRatio.setNumeratorTags(_numeratorTagsView.getSelectedTags());
    _editingRatio.setNumeratorTagLogic(_numeratorTagsView.getTagLogic());
    _editingRatio.setDenominatorTags(_denominatorTagsView.getSelectedTags());
    _editingRatio.setDenominatorTagLogic(_denominatorTagsView.getTagLogic());
    _editingRatio.setNotes(_notesField.getText());
  }

  private void loadControlsFromData() {
    if (_editingRatio == null) {
      // reset to the defaults
      _showPercent.setSelected(true);
      _alwaysPositive.setSelected(true);
      _useTaxDate.setSelected(false);
      // since we use a button group we only need to set the radio button that is on
      _numeratorMatchModel.setSelectedMatchLogic(TxnMatchLogic.DEFAULT);
      _denominatorMatchModel.setSelectedMatchLogic(TxnMatchLogic.DEFAULT);
      _numeratorLabelField.setText(N12ERatios.EMPTY);
      _denominatorLabelField.setText(N12ERatios.EMPTY);
      _numeratorDualAcctSelector.setRequiredAccountFilter(RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
      _denominatorDualAcctSelector.setRequiredAccountFilter(RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
      _numeratorDualAcctSelector.setDisallowedAccountFilter(RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
      _denominatorDualAcctSelector.setDisallowedAccountFilter(RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
      _numeratorTagsView.reset();
      _denominatorTagsView.reset();
      _notesField.setText(N12ERatios.EMPTY);
      return;
    }
    _showPercent.setSelected(_editingRatio.getShowPercent());
    _alwaysPositive.setSelected(_editingRatio.getAlwaysPositive());
    _useTaxDate.setSelected(_editingRatio.getUseTaxDate());
    _numeratorMatchModel.setSelectedMatchLogic(_editingRatio.getNumeratorMatchingLogic());
    _denominatorMatchModel.setSelectedMatchLogic(_editingRatio.getDenominatorMatchingLogic());
    _numeratorLabelField.setText(_editingRatio.getNumeratorLabel());
    _denominatorLabelField.setText(_editingRatio.getDenominatorLabel());

    // use the object that supports IAccountSelector to re-use common code for loading an account list
    RatioAccountSelector accountSelector = createAccountSelector(_mdGui.getCurrentBook());
    _numeratorDualAcctSelector.setRequiredAccountFilter(
      accountSelector.selectFromEncodedString(_editingRatio.getNumeratorEncodedRequiredAccounts()));
    _numeratorDualAcctSelector.setDisallowedAccountFilter(accountSelector.selectFromEncodedString(
      _editingRatio.getNumeratorEncodedDisallowedAccounts()));
    _denominatorDualAcctSelector.setRequiredAccountFilter(accountSelector.selectFromEncodedString(
      _editingRatio.getDenominatorEncodedRequiredAccounts()));
    _denominatorDualAcctSelector.setDisallowedAccountFilter(accountSelector.selectFromEncodedString(
      _editingRatio.getDenominatorEncodedDisallowedAccounts()));

    _numeratorTagsView.setSelectedTags(_editingRatio.getNumeratorTags(), _editingRatio.getNumeratorTagLogic());
    _denominatorTagsView.setSelectedTags(_editingRatio.getDenominatorTags(), _editingRatio.getDenominatorTagLogic());
    _notesField.setText(_editingRatio.getNotes());
    validateNumeratorLabel();
    validateDenominatorLabel();
  }

  static RatioAccountSelector createAccountSelector(final AccountBook rootAccount) {
    return new RatioAccountSelector(rootAccount);
  }

  private void setupAccountSelectors() {
    _numeratorDualAcctSelector = new AccountFilterSelectLabel(_mdGui, _resources);
    _numeratorDualAcctSelector.setRequiredAccountFilter(
        RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
    _numeratorDualAcctSelector.setDisallowedAccountFilter(
        RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
    _denominatorDualAcctSelector = new AccountFilterSelectLabel(_mdGui, _resources);
    _denominatorDualAcctSelector.setRequiredAccountFilter(
        RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
    _denominatorDualAcctSelector.setDisallowedAccountFilter(
        RatioAccountSelector.buildAccountFilter(_mdGui.getCurrentBook()));
  }


  private void setupTagFilters() {
    _numeratorTagsView = new TxnTagFilterView(_mdGui);
    _numeratorTagsView.layoutUI();
    _numeratorTagsView.setOpaque(false);
    _denominatorTagsView = new TxnTagFilterView(_mdGui);
    _denominatorTagsView.layoutUI();
    _denominatorTagsView.setOpaque(false);
  }
}
