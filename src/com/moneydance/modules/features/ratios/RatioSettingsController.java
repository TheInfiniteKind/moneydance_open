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
import com.moneydance.util.StreamTable;
import com.moneydance.util.StringEncodingException;

import javax.swing.table.TableModel;

/**
 * <p>Controller for the dialog that shows account or category selection.</p>
 *
 * @author Kevin Menningen
 */
public class RatioSettingsController
    implements ResourceProvider {
  private final RatioSettingsModel _settingsModel;
  private final ResourceProvider _resources;
  private final RatiosExtensionModel _extensionModel;

  /**
   * Constructor. This object acts as a resource provider in order to preserve design
   * consistency with the main feature controller.
   *
   * @param settingsModel  The settings data model for the ratios.
   * @param mainController The main controller for the feature.
   * @param extensionModel The data model for the extension.
   */
  public RatioSettingsController(final RatioSettingsModel settingsModel,
                                 final ResourceProvider mainController,
                                 final RatiosExtensionModel extensionModel) {
    _settingsModel = settingsModel;
    _resources = mainController;
    _extensionModel = extensionModel;
  }

  public void apply() {
    // copy edited settings to actual settings
    _settingsModel.apply();
    // store the settings in the data file
    RootAccount root = getData();
    if (root != null) {
      final RatioSettings updatedSettings = _settingsModel.getActualSettings();
      updatedSettings.saveToSettings(root);

      // reload
      _extensionModel.setSettings(updatedSettings);

      // ensure file is marked dirty
      root.accountModified(root);
    }
  }


  /**
   * Obtain the given string from the resource bundle.
   *
   * @param resourceKey The key to look up the resources.
   * @return The associated string, or <code>null</code> if the key is not found.
   */
  public String getString(final String resourceKey) {
    return _resources.getString(resourceKey);
  }

  RootAccount getData() {
    return _settingsModel.getData();
  }

  public RatioSettings getSettings() {
    return _settingsModel.getEditingSettings();
  }

  public TableModel getTableModel() {
    return _settingsModel.getTableModel();
  }

  public void insertAt(int rowIndex) {
    _settingsModel.getTableModel().add(rowIndex, new RatioEntry(), true);
  }

  public int copyItem(int rowIndex) {
    final RatioEntry source = _settingsModel.getTableModel().getRatioEntry(rowIndex);
    StreamTable settingTable = new StreamTable();
    RatioEntry target = null;
    try {
      settingTable.readFrom(source.getSettingsString());
      target = new RatioEntry(settingTable, _extensionModel.getGUI());
    } catch (StringEncodingException e) {
      System.err.println("ratios: Error copying ratio entry settings: " + e.getMessage());
      target = new RatioEntry();
    }
    target.setName(getCopyName(source.getName()));
    int newIndex = rowIndex + 1;
    _settingsModel.getTableModel().add(newIndex, target, true);
    return newIndex;
  }

  private String getCopyName(String name) {
    int copyNum = 1;
    final String copySuffix = ' ' + getString(L10NRatios.COPY_SUFFIX);
    StringBuilder sb = new StringBuilder();
    String candidate = null;
    do {
      sb.setLength(0);
      sb.append(name);
      sb.append(copySuffix);
      sb.append(' ');
      sb.append(Integer.toString(copyNum));
      ++copyNum;
      candidate = sb.toString();
    } while (nameAlreadyExists(candidate));
    return candidate;
  }

  private boolean nameAlreadyExists(String candidate) {
    RatioTableModel tableModel = _settingsModel.getTableModel();
    for (int index = 0; index < tableModel.getRowCount(); index++) {
      String itemName = (String)tableModel.getValueAt(index, 0);
      if (RatiosUtil.areEqual(itemName, candidate)) return true;
    }
    return false;
  }

  public void deleteItem(int rowIndex) {
    _settingsModel.getTableModel().delete(rowIndex);
  }

  public int moveItemUp(final int index) {
    int newIndex = index - 1;
    if (newIndex < 0) return -1;
    RatioEntry previousItem = _settingsModel.getTableModel().getRatioEntry(newIndex);
    RatioEntry selectedItem = _settingsModel.getTableModel().getRatioEntry(index);
    if ((previousItem == null) || (selectedItem == null)) return -1;
    _settingsModel.getTableModel().swap(newIndex, index);
    final int tempIndex = previousItem.getIndex();
    previousItem.setIndex(selectedItem.getIndex());
    selectedItem.setIndex(tempIndex);
    return newIndex;
  }

  public int moveItemDown(final int index) {
    final int newIndex = index + 1;
    if (newIndex >= _settingsModel.getTableModel().getRowCount()) return -1;
    RatioEntry nextItem = _settingsModel.getTableModel().getRatioEntry(newIndex);
    RatioEntry selectedItem = _settingsModel.getTableModel().getRatioEntry(index);
    if ((nextItem == null) || (selectedItem == null)) return -1;
    _settingsModel.getTableModel().swap(newIndex, index);
    final int tempIndex = nextItem.getIndex();
    nextItem.setIndex(selectedItem.getIndex());
    selectedItem.setIndex(tempIndex);
    return newIndex;
  }

  public void updateItem(int index, String editedText) {
    _settingsModel.getTableModel().setValueAt(editedText, index, 0);
  }
}