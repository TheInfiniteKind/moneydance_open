/*
 * ************************************************************************
 * Copyright (C) 2012-2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.moneydance.apps.md.view.gui.OKButtonListener;
import com.moneydance.apps.md.view.gui.OKButtonPanel;

import javax.swing.*;
import java.awt.Frame;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.view.gui.SecondaryDialog;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.util.UiUtil;

/**
 * <p>Dialog that allows the user to change Ratios settings.</p>
 *
 * @author Kevin Menningen
 */
class RatioSettingsDialog
    extends SecondaryDialog
    implements OKButtonListener
{
  private static final int DEFAULT_WIDTH = 1130;
  private static final int DEFAULT_HEIGHT = 790;

  private final RatioSettingsModel _model;
  private final RatioSettingsController _controller;
  private final RatioSettingsView _view;

  /**
   * Creates a modeless dialog with the specified title and
   * with the specified owner frame.  If <code>owner</code>
   * is <code>null</code>, a shared, hidden frame will be set as the
   * owner of the dialog.
   * <p/>
   * This constructor sets the component's locale property to the value
   * returned by <code>JComponent.getDefaultLocale</code>.
   * <p/>
   * NOTE: This constructor does not allow you to create an unowned
   * <code>JDialog</code>. To create an unowned <code>JDialog</code>
   * you must use either the <code>JDialog(Window)</code> or
   * <code>JDialog(Dialog)</code> constructor with an argument of
   * <code>null</code>.
   *
   *
   * @param mdGui     Moneydance UI object.
   * @param owner     The <code>Frame</code> from which the dialog is displayed
   * @param resources Internationalization resource provider.
   * @param mainModel The extension data model.
   * @param data      Root account providing access to all data.
   * @param settings  The settings to be edited.
   * @throws java.awt.HeadlessException if <code>GraphicsEnvironment.isHeadless()</code>
   *                                    returns <code>true</code>.
   * @see java.awt.GraphicsEnvironment#isHeadless
   * @see javax.swing.JComponent#getDefaultLocale
   */
  public RatioSettingsDialog(MoneydanceGUI mdGui, Frame owner,
                             ResourceProvider resources,
                             RatiosExtensionModel mainModel,
                             RootAccount data,
                             RatioSettings settings) {
    super(mdGui, owner, resources.getString(L10NRatios.SETTINGS_TITLE), false);

    _model = new RatioSettingsModel(data, mainModel, settings, resources);
    _view = new RatioSettingsView(mdGui, _model, resources);
    _controller = new RatioSettingsController(_model, resources, mainModel);
    _view.setController(_controller);

    // hook up listeners
    _model.addPropertyChangeListener(_view);

    buildMainPanel();
    // if previous location was saved, go back to it
    setRememberSizeLocationKeys(N12ERatios.SIZE_KEY, N12ERatios.LOCATION_KEY,
                                new Dimension(DEFAULT_WIDTH, DEFAULT_HEIGHT));

    // this is a temporary dialog, but we need to get the result of the dialog
  }


  /**
   * OKButtonListener
   * Respond to OKButtonPanel callback.
   * @param buttonId Identifier of the button the user clicked or activated.
   */
  public void buttonPressed(final int buttonId) {
    if (buttonId == OKButtonPanel.ANSWER_CANCEL) {
      onCancel();
    } else if (buttonId == OKButtonPanel.ANSWER_OK) {
      onOk();
    }
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Package Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  void loadData() {
    _model.refresh();
    _view.loadControlsFromData(true);
  }

  @Override
  public boolean goingAway() {
    // avoid the lapsed listener problem
    _model.removePropertyChangeListener(_view);
    _model.cleanUp();
    return true;
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private void buildMainPanel() {
    // setup the main view
    _view.layoutUI();

    // for convenience, setLayout() and add() are overridden to go to the content pane
    setLayout(new BorderLayout());

    add(_view, BorderLayout.CENTER);
    add(buildButtonPanel(), BorderLayout.SOUTH);

    pack();

    // This code only works the first time, before the size and position of the window is set
    // in the preferences. The preferences settings override.
    Dimension newSize = getPreferredSize();
    if (newSize.getWidth() < DEFAULT_WIDTH) {
      newSize = new Dimension(DEFAULT_WIDTH, (int) newSize.getHeight());
      setMinimumSize(newSize);
      setPreferredSize(newSize);
    }
  }

  private JPanel buildButtonPanel() {
    final OKButtonPanel okPanel = new OKButtonPanel(mdGUI, this, OKButtonPanel.QUESTION_OK_CANCEL);

    JLabel version = new JLabel(Main.getVersionString()); // version number
    version.setOpaque(false);
    version.setHorizontalAlignment(JLabel.LEFT);
    version.setVerticalAlignment(JLabel.BOTTOM);
    Font smallFont = version.getFont().deriveFont(version.getFont().getSize() - 2f);
    version.setFont(smallFont);
    version.setEnabled(false);

    // link to the help on the web
    JButton userGuide = new JButton(_controller.getString(L10NRatios.USER_GUIDE));
    userGuide.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent event) {
        RatiosUtil.launchUserGuide();
      }
    });
    mdGUI.applyFilterBarProperties(userGuide);
    JButton reset = new JButton(mdGUI.getStr("reset"));
    reset.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent event) {
        resetToFactory();
      }
    });
    mdGUI.applyFilterBarProperties(reset);
    // gap to avoid overcrowded appearance
    JLabel gap = new JLabel();
    gap.setBorder(BorderFactory.createEmptyBorder(0, UiUtil.DLG_HGAP, 0, 0));
    gap.setOpaque(false);
    JLabel gap2 = new JLabel();
    gap2.setBorder(BorderFactory.createEmptyBorder(0, UiUtil.DLG_HGAP, 0, 0));
    gap2.setOpaque(false);
    okPanel.setExtraButtons(new JComponent[] { version, gap, userGuide, gap2, reset });

    // pad the dialog on the outside
    okPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.DLG_VGAP, UiUtil.DLG_HGAP * 2,
                                                          UiUtil.DLG_VGAP, UiUtil.DLG_HGAP * 2));
    return okPanel;
  }

  private void resetToFactory() {
    if (mdGUI.askQuestion(_view, "Reset to factory defaults?")) {
      _controller.resetToFactory();
    }
  }

  private void onOk() {
    _view.saveControlsToData();
    _controller.apply();
    goAway();
  }

  private void onCancel() {
    goAway();
  }
}