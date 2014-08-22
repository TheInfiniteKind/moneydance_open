/*
 * ************************************************************************
 * Copyright (C) 2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import javax.swing.AbstractListModel;
import javax.swing.ComboBoxModel;
import java.util.ArrayList;
import java.util.List;

/**
 * Combo box selection model containing the various kinds of transaction matches or balance types to use.
 */
public class MatchSelectorModel extends AbstractListModel
  implements ComboBoxModel {
  private final List<MatchEntry> _items = new ArrayList<MatchEntry>(6);
  private MatchEntry _selected = null;

  public MatchSelectorModel(ResourceProvider resources) {
    _items.add(new MatchEntry(TxnMatchLogic.IN, resources.getString(L10NRatios.TXN_INTO)));
    _items.add(new MatchEntry(TxnMatchLogic.OUT, resources.getString(L10NRatios.TXN_OUT_OF)));
    _items.add(new MatchEntry(TxnMatchLogic.BOTH, resources.getString(L10NRatios.TXN_BOTH)));
    _items.add(new MatchEntry(TxnMatchLogic.BEGIN_BALANCE, resources.getString(L10NRatios.START_BALANCE)));
    _items.add(new MatchEntry(TxnMatchLogic.AVERAGE_BALANCE, resources.getString(L10NRatios.AVERAGE_BALANCE)));
    _items.add(new MatchEntry(TxnMatchLogic.END_BALANCE, resources.getString(L10NRatios.END_BALANCE)));
    _items.add(new MatchEntry(TxnMatchLogic.CONSTANT, resources.getString(L10NRatios.CONSTANT)));
    _items.add(new MatchEntry(TxnMatchLogic.DAYS_IN_PERIOD, resources.getString(L10NRatios.DAYS_IN_PERIOD)));
  }

  public void setSelectedItem(Object anItem) {
    _selected = (MatchEntry)anItem;
    fireContentsChanged(this, -1, -1);
  }

  public Object getSelectedItem() {
    return _selected;
  }

  public int getSize() {
    return _items.size();
  }

  public Object getElementAt(int index) {
    return _items.get(index);
  }

  public TxnMatchLogic getSelectedMatchLogic() {
    if (_selected == null) return TxnMatchLogic.DEFAULT;
    return _selected.getMatchLogic();
  }

  public void setSelectedMatchLogic(TxnMatchLogic logic) {
    for (MatchEntry entry : _items) {
      if (entry.getMatchLogic().equals(logic)) {
        setSelectedItem(entry);
        break;
      }
    }
  }

  /**
   * A single item in the selection combo box for the type of transaction or balance to compute.
   */
  class MatchEntry
  {
    private final TxnMatchLogic _logic;
    private final String _displayText;

    MatchEntry(TxnMatchLogic logic, String display) {
      _logic = logic;
      _displayText = display;
    }

    TxnMatchLogic getMatchLogic() { return _logic; }

    @Override
    public String toString() { return _displayText; }

  }
}
