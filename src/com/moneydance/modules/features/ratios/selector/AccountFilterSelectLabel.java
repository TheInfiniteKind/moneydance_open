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

import com.moneydance.apps.md.controller.AccountFilter;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.AwtUtil;
import com.moneydance.modules.features.ratios.L10NRatios;
import com.moneydance.modules.features.ratios.RatiosUtil;
import com.moneydance.modules.features.ratios.ResourceProvider;
import com.moneydance.util.StringUtils;

import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.GridLayout;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

/**
 * Label that shows the selected accounts. Clicking on the label will bring up
 * the selection window.
 */
public class AccountFilterSelectLabel
    extends JPanel
    implements PropertyChangeListener {
  private final MoneydanceGUI _mdGui;
  private final AccountFilterSelectListModel _model;
  private final ResourceProvider _resources;
  private final String _requiredLabel;
  private final String _disallowedLabel;
  private final JLabel _required = new JLabel();
  private final JLabel _disallowed = new JLabel();


  public AccountFilterSelectLabel(final MoneydanceGUI mdGui, final ResourceProvider resources) {
    _mdGui = mdGui;
    _model = new AccountFilterSelectListModel();
    _resources = resources;
    _requiredLabel = RatiosUtil.getLabelText(resources, L10NRatios.REQUIRED);
    _disallowedLabel = RatiosUtil.getLabelText(resources, L10NRatios.DISALLOWED);

    setOpaque(false);
    _required.setOpaque(false);
    _disallowed.setOpaque(false);

    layoutUI();
    MouseListener listener = new MouseAdapter() {
      public void mouseReleased(MouseEvent e) {
        showSelector();
      }
    };
    _required.addMouseListener(listener);
    _disallowed.addMouseListener(listener);
    _model.addPropertyChangeListener(this);
  }

  public void layoutUI() {
    removeAll();
    setLayout(new GridLayout(2, 1));
    add(_required);
    add(_disallowed);
    validate();
  }

  public AccountFilter getRequiredAccountFilter() {
    return _model.getRequiredAccountFilter();
  }

  public void setRequiredAccountFilter(final AccountFilter filter) {
    _model.setRequiredAccountFilter(filter);
  }

  public AccountFilter getDisallowedAccountFilter() {
    return _model.getDisallowedAccountFilter();
  }

  public void setDisallowedAccountFilter(final AccountFilter filter) {
    _model.setDisallowedAccountFilter(filter);
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

  public void propertyChange(final PropertyChangeEvent event) {
    final String eventName = event.getPropertyName();
    // either a new filter was defined or the user picked new accounts
    if (N12ESelector.ACCOUNTS_CHANGE.equals(eventName) ||
        N12ESelector.FILTER_CHANGE.equals(eventName)) {
      updateAccountText();
    }
  }

  private void updateAccountText() {
    final String requiredText = getRequiredAccountList();
    _required.setText(_requiredLabel + requiredText);
    _required.setToolTipText(getDisplayToolTipText(requiredText));
    final String disallowedText = getDisallowedAccountList();
    _disallowed.setText(_disallowedLabel + disallowedText);
    _disallowed.setToolTipText(getDisplayToolTipText(disallowedText));
  }

  private String getRequiredAccountList() {
    final AccountFilter requiredFilter = _model.getRequiredAccountFilter();
    if (requiredFilter == null) {
      return _mdGui.getStr(L10NRatios.NONE);
    }
    return requiredFilter.getDisplayString(_mdGui.getCurrentAccount(), _mdGui);
  }

  private String getDisallowedAccountList() {
    final AccountFilter disallowedFilter = _model.getDisallowedAccountFilter();
    if (disallowedFilter == null) {
      return _mdGui.getStr(L10NRatios.NONE);
    }
    return disallowedFilter.getDisplayString(_mdGui.getCurrentAccount(), _mdGui);
  }

  /**
   * Build the tooltip text which should clearly show the entire list, even if the one-line text
   * in the label is cut off.
   * @param displayText The text to display in the tooltip.
   * @return A tooltip to show, broken up into rows of 5 comma-delimited sections
   */
  private String getDisplayToolTipText(String displayText)
  {
    // the list of items will be comma-delimited
    final int numSections = StringUtils.countFields(displayText, ',');
    if (numSections <= 5) return String.format("<html><p>%s</p></html>", displayText);
    // break up the text into rows of 5 sections
    StringBuilder sb = new StringBuilder("<html><p>");
    for (int section = 0; section < numSections; section++) {
      if ((section != 0) && ((section % 5) == 0)) sb.append("<br/>");
      sb.append(StringUtils.fieldIndex(displayText, ',', section));
      if ((section + 1) < numSections) sb.append(", ");
    }
    sb.append("</p></html>");
    return sb.toString();
  }

  private void showSelector() {
    AccountFilterSelectDialog dialog = new AccountFilterSelectDialog(_mdGui, AwtUtil.getFrame(this), _resources, _model);
    dialog.setVisible(true);
  }

}
