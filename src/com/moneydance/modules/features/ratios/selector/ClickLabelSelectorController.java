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

import java.util.List;

/**
 * Controller for the UI widget that allows the user to pick one of a list of labels,
 * and show which one is selected.
 */
class ClickLabelSelectorController {
  private final ClickLabelSelectorModel _model;

  ClickLabelSelectorController(final ClickLabelSelectorModel model) {
    _model = model;
  }

  public List<String> getItemList() {
    return _model.getItemList();
  }

  public int getSelectedIndex() {
    return _model.getSelectedIndex();
  }

  public void setSelectedIndex(final int index) {
    _model.setSelectedIndex(index);
  }

  public int getItemCount() {
    return _model.getItemCount();
  }
}
