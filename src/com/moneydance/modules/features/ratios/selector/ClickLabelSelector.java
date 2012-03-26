/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package  com.moneydance.modules.features.ratios.selector;

import javax.swing.JPanel;
import java.awt.Color;
import java.awt.Component;
import java.beans.PropertyChangeListener;
import java.util.List;

/**
 * This UI object allows the user to click on one of a list of several labels, and shows
 * which label is currently selected.
 */
class ClickLabelSelector {
  private final ClickLabelSelectorView _view;
  private final ClickLabelSelectorModel _model;

  public ClickLabelSelector(final List<String> items, final int defaultIndex) {
    _model = new ClickLabelSelectorModel(items, defaultIndex);
    ClickLabelSelectorController controller = new ClickLabelSelectorController(_model);
    _view = new ClickLabelSelectorView(controller);
    _model.addPropertyChangeListener(_view);
  }

  public int getSelectedIndex() {
    return _model.getSelectedIndex();
  }

  public void setSelectedIndex(final int index) {
    _model.setSelectedIndex(index);
  }

  public void setEnabled(final boolean enabled) {
    _view.setEnabled(enabled);
  }

  public void setBackground(final Color color) {
    _view.setBackground(color);
  }

  public void setForeground(final Color color) {
    _view.setForeground(color);
  }

  public void setSelectionBackground(final Color color) {
    _view.setSelectionBackground(color);
  }

  public void setSelectionForeground(final Color color) {
    _view.setSelectionForeground(color);
  }

  public JPanel getView() {
    return _view;
  }

  void addPropertyChangeListener(final PropertyChangeListener listener) {
    _model.addPropertyChangeListener(listener);
  }

  void removePropertyChangeListener(final PropertyChangeListener listener) {
    _model.removePropertyChangeListener(listener);
  }
}
