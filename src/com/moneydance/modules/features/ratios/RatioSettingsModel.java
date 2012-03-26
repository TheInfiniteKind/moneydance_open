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

import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.util.BasePropertyChangeReporter;

import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;

/**
 * <p>The model for the ratio settings edit dialog.</p>
 *
 * @author Kevin Menningen
 */
class RatioSettingsModel
    extends BasePropertyChangeReporter
    implements PropertyChangeListener {
  private final RootAccount _data;
  private final RatioSettings _actualSettings;
  private final RatioSettings _editSettings;

  private final RatioTableModel _tableModel;

  public RatioSettingsModel(RootAccount data, RatiosExtensionModel mainModel,
                            RatioSettings settings, ResourceProvider resources) {
    _data = data;
    _actualSettings = settings;
    _editSettings = new RatioSettings(_actualSettings);
    _editSettings.addPropertyChangeListener(this);
    _tableModel = new RatioTableModel(resources.getString(L10NRatios.COLUMN_LABEL));
    for (int index = 0; index < mainModel.getRatioCount(); index++) {
      _tableModel.add(index, mainModel.getRatioItem(index), false);
    }
  }

  public void apply() {
    // commit user settings to the model in preparation for save.
    // copy all settings from the editing settings to the actual one
    _actualSettings.suspendNotifications(true);
    _editSettings.copyTo(_actualSettings);
    _actualSettings.suspendNotifications(false);
  }

  public void refresh() {
    // generic update to get the view to refresh
    notifyAllListeners();
  }

  public RatioSettings getEditingSettings() {
    return _editSettings;
  }

  public RatioSettings getActualSettings() {
    return _actualSettings;
  }

  //////////////////////////////////////////////////////////////////////////////////////////////
  //  Private Methods
  //////////////////////////////////////////////////////////////////////////////////////////////

  RatioTableModel getTableModel() {
    return _tableModel;
  }

  public RootAccount getData() {
    return _data;
  }

  public void propertyChange(PropertyChangeEvent event) {
    // a setting has changed, parrot it
    _eventNotify.firePropertyChange(event);
  }


  public void cleanUp() {
    _editSettings.removePropertyChangeListener(this);
  }


}