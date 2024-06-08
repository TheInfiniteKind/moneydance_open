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
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.select.ClickLabelListPanel;
import com.moneydance.apps.md.view.resources.MDResourceProvider;
import com.moneydance.awt.GridC;
import com.moneydance.util.UiUtil;

import javax.swing.ButtonGroup;
import javax.swing.JCheckBox;
import javax.swing.JDialog;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import java.awt.Color;
import java.awt.FlowLayout;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.List;

/**
 * A tag filtering UI panel.
 *
 * @author Kevin Menningen
 */
class TxnTagFilterView extends JPanel {
  private final MoneydanceGUI _mdGui;
  private JCheckBox _useTagFilter;
  private SearchTxnTagsField _tagField;
  private JRadioButton _tagsAnd;
  private JRadioButton _tagsExact;
  private JRadioButton _tagsOr;
  private ClickLabelListPanel _buttonPanel;
  private Color _focusColor;

  TxnTagFilterView(MoneydanceGUI mdGui) {
    _mdGui = mdGui;
  }

  public void setEnabled(boolean enabled) {
    super.setEnabled(enabled);
    _useTagFilter.setEnabled(enabled);
    _tagField.setEnabled(enabled);
    _tagsAnd.setEnabled(enabled);
    _tagsExact.setEnabled(enabled);
    _tagsOr.setEnabled(enabled);
    _buttonPanel.setEnabled(enabled);
  }

  void layoutUI() {
    setLayout(new GridBagLayout());
    setOpaque(false);

    _focusColor = new Color(255, 255, 180); // light yellow
    _useTagFilter = new JCheckBox();
    _useTagFilter.setOpaque(false);
//    _useTagFilter.setHorizontalAlignment(SwingConstants.RIGHT);
//    _useTagFilter.setHorizontalTextPosition(SwingConstants.LEFT);
    _tagField = new SearchTxnTagsField(this, _mdGui);
    final JPanel tagLogicPanel = buildTagsPanel(_mdGui);
    tagLogicPanel.setOpaque(false);

    add(_useTagFilter, GridC.getc(0, 0).label());
    // no bottom inset because the one below 'belongs' to it
    add(_tagField, GridC.getc(1,0).wx(1).fillx().insets(
            GridC.TOP_FIELD_INSET, GridC.LEFT_FIELD_INSET, 0, GridC.RIGHT_FIELD_INSET));
    // no top inset because it 'belongs' to the field above it
    add(tagLogicPanel, GridC.getc(1,1).wx(1).fillx().insets(
            0, GridC.LEFT_FIELD_INSET, GridC.BOTTOM_FIELD_INSET, GridC.RIGHT_FIELD_INSET));

    // initial conditions
    reset();

    // add listener
    _tagField.addSelectionListener(new ActionListener() {
      public void actionPerformed(final ActionEvent event) {
        if (N12ERatios.SELECT_TAG_LIST.equals(event.getActionCommand())) {
          showTagsPopup();
        }
        // notify that tags will be used
        selectUseTags();
      }
    });

  }

  void reset() {
    _useTagFilter.setSelected(false);
    _tagsOr.setSelected(true);
    _tagField.selectNone();
  }

  /**
   * @return The 'glue' logic to use while searching for transactions that match given tags.
   */
  TagLogic getTagLogic() {
    if (!_useTagFilter.isSelected()) return TagLogic.OR;
    if (_tagsExact.isSelected()) {
      return TagLogic.EXACT;
    } else if (_tagsAnd.isSelected()) {
      return TagLogic.AND;
    }
    return TagLogic.OR;
  }

  List<String> getSelectedTags() {
    if (_useTagFilter.isSelected()) {
      return _tagField.getSelectedTags();
    }
    return null;
  }

  void selectUseTags() {
    _useTagFilter.setSelected(true);
  }

  void setSelectedTags(final List<String> tags, final TagLogic tagLogic) {
    if ((tags == null) || tags.isEmpty()) {
      // tags not used
      reset();
      return;
    }
    _tagField.setSelectedTags(tags);
    if (TagLogic.AND.equals(tagLogic)) {
      _tagsAnd.setSelected(true);
    } else if (TagLogic.EXACT.equals(tagLogic)) {
      _tagsExact.setSelected(true);
    } else {
      _tagsOr.setSelected(true);
    }
    selectUseTags();
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  /**
   * @param resources Object capable of loading strings and other localizable resources.
   * @return Settings for the transaction tags search criteria.
   */
  private JPanel buildTagsPanel(final MDResourceProvider resources)
  {
    final JPanel supportPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, UiUtil.HGAP * 2, 0));
    supportPanel.setOpaque(false);
    _buttonPanel = new ClickLabelListPanel();
    _buttonPanel.setOpaque(false);

    MDAction selectAll = MDAction.makeKeyedAction(_mdGui, "accountfilter.all", "accountfilter.all", new ActionListener() {
      public void actionPerformed(ActionEvent evt) {
        _tagField.selectAll();
        _useTagFilter.setSelected(true);
      }
    });
    _buttonPanel.addLabel(selectAll);

    MDAction selectNone = MDAction.makeKeyedAction(_mdGui, "none", "accountfilter.none", new ActionListener() {
      public void actionPerformed(ActionEvent evt) {
        _tagField.selectNone();
        _useTagFilter.setSelected(true);
      }
    });
    _buttonPanel.addLabel(selectNone);
    _buttonPanel.layoutUI();
    supportPanel.add(_buttonPanel);

    _tagsAnd = new JRadioButton(resources.getStr("findAnd.text"));
    _tagsAnd.setOpaque(false);
    _tagsOr = new JRadioButton(resources.getStr("findOr.text"));
    _tagsOr.setOpaque(false);
    _tagsExact = new JRadioButton(resources.getStr("findExact.text"));
    _tagsExact.setOpaque(false);
    supportPanel.add(_tagsAnd);
    supportPanel.add(_tagsOr);
    supportPanel.add(_tagsExact);

    ButtonGroup tagBoolean = new ButtonGroup();
    tagBoolean.add(_tagsAnd);
    tagBoolean.add(_tagsOr);
    tagBoolean.add(_tagsExact);
    tagBoolean.setSelected(_tagsOr.getModel(), true);

    return supportPanel;
  }

  private void showTagsPopup() {
    final JDialog popup = new TagSelectPopup(com.moneydance.awt.AwtUtil.getWindow(this), _tagField, _focusColor);
    popup.setVisible(true);
  }
}
