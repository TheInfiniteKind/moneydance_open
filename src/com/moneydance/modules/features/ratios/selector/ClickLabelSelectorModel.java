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

import javax.swing.event.SwingPropertyChangeSupport;
import java.beans.PropertyChangeListener;
import java.util.Collections;
import java.util.List;

/**
 * Model for the UI widget that allows the user to pick one of a list of labels,
 * and show which one is selected.
 */
class ClickLabelSelectorModel {
  final static String SELECTION_CHANGE = "selectIndexChange";
  private final List<String> _items;
  private final SwingPropertyChangeSupport eventNotify = new SwingPropertyChangeSupport(this, true);
  private int _selectedIndex;

  ClickLabelSelectorModel(final List<String> items, int defaultIndex) {
    _items = Collections.unmodifiableList(items);
    _selectedIndex = defaultIndex;
  }

  List<String> getItemList() {
    return _items;
  }

  int getItemCount() {
    return _items.size();
  }

  String getItem(final int index) {
    return _items.get(index);
  }

  int getSelectedIndex() {
    return _selectedIndex;
  }

  void setSelectedIndex(final int selectedIndex) {
    if (_selectedIndex != selectedIndex) {
      final int oldIndex = _selectedIndex;
      _selectedIndex = selectedIndex;
      eventNotify.firePropertyChange(SELECTION_CHANGE, oldIndex, selectedIndex);
    }
  }

  void addPropertyChangeListener(final PropertyChangeListener listener) {
    eventNotify.addPropertyChangeListener(listener);
  }

  void removePropertyChangeListener(final PropertyChangeListener listener) {
    eventNotify.removePropertyChangeListener(listener);
  }
}
