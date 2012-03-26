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

import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.OKButtonListener;
import com.moneydance.apps.md.view.gui.OKButtonPanel;
import com.moneydance.apps.md.view.gui.SecondaryDialog;
import com.moneydance.modules.features.ratios.L10NRatios;
import com.moneydance.modules.features.ratios.Main;
import com.moneydance.modules.features.ratios.RatiosUtil;
import com.moneydance.modules.features.ratios.ResourceProvider;
import com.moneydance.util.UiUtil;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Frame;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/**
 * <p>Dialog that shows a table of all accounts with a dual selector control for each.</p>
 *
 * @author Kevin Menningen
 */
class AccountFilterSelectDialog
    extends SecondaryDialog
    implements OKButtonListener
{
  private static final int MIN_WIDTH = 500;

  private final AccountFilterSelectListModel _actualModel;
  private final AccountFilterSelectList _view;
  private final String _userGuideLabel;

  /**
   * Creates a modal dialog with the specified title and
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
   * @param mdGui       Moneydance UI object.
   * @param owner       The <code>Frame</code> from which the dialog is displayed
   * @param resources   Internationalization resource provider.
   * @param actualModel The current selection model, before the user makes changes.
   * @throws java.awt.HeadlessException if <code>GraphicsEnvironment.isHeadless()</code>
   *                                    returns <code>true</code>.
   * @see java.awt.GraphicsEnvironment#isHeadless
   * @see javax.swing.JComponent#getDefaultLocale
   */
  public AccountFilterSelectDialog(MoneydanceGUI mdGui, Frame owner,
                                   ResourceProvider resources,
                                   AccountFilterSelectListModel actualModel) {
    super(mdGui, owner, resources.getString(L10NRatios.SELECT_ACCOUNTS_TITLE), true);

    _view = new AccountFilterSelectList(resources, mdGui);
    _actualModel = actualModel;
    _userGuideLabel = resources.getString(L10NRatios.USER_GUIDE);
    buildMainPanel();

    _view.setAccountFilters(_actualModel.getRequiredAccountFilter(), _actualModel.getDisallowedAccountFilter());
    _view.setAutoSelectChildAccounts(true);

    // if previous location was saved, go back to it
    setRememberSizeLocationKeys(N12ESelector.SIZE_KEY, N12ESelector.LOCATION_KEY,
                                new Dimension(750, 600));
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

  @Override
  public boolean goingAway() {
    // avoid the lapsed listener problem
//    _actualModel.removePropertyChangeListener(_view);
//    _actualModel.cleanUp();
    return true;
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  ///////////////////////////////////////////////////////////////////////////////////////////////

  private void buildMainPanel() {
    // setup the main view
    _view.layoutComponentUI();

    // for convenience, setLayout() and add() are overridden to go to the content pane
    setLayout(new BorderLayout());

    add(_view.getView(), BorderLayout.CENTER);
    add(buildButtonPanel(), BorderLayout.SOUTH);

    pack();

    // This code only works the first time, before the size and position of the window is set
    // in the preferences. The preferences settings override.
    Dimension newSize = getPreferredSize();
    if (newSize.getWidth() < MIN_WIDTH) {
      newSize = new Dimension(MIN_WIDTH, (int) newSize.getHeight());
      setMinimumSize(newSize);
      setPreferredSize(newSize);
    }
  }

  private JPanel buildButtonPanel() {
    final OKButtonPanel okPanel = new OKButtonPanel(mdGUI, this, OKButtonPanel.QUESTION_OK_CANCEL);

    JLabel version = new JLabel(Main.VERSION); // version number
    version.setOpaque(false);
    version.setHorizontalAlignment(JLabel.LEFT);
    version.setVerticalAlignment(JLabel.BOTTOM);
    Font smallFont = version.getFont().deriveFont(version.getFont().getSize() - 2f);
    version.setFont(smallFont);
    version.setEnabled(false);

    // link to the help on the web
    JButton userGuide = new JButton(_userGuideLabel);
    userGuide.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent event) {
        RatiosUtil.launchUserGuide();
      }
    });
    mdGUI.applyFilterBarProperties(userGuide);
    // gap to avoid overcrowded appearance
    JLabel gap = new JLabel();
    gap.setBorder(BorderFactory.createEmptyBorder(0, UiUtil.DLG_HGAP, 0, 0));
    gap.setOpaque(false);
    okPanel.setExtraButtons(new JComponent[] { version, gap, userGuide });

    // pad the dialog on the outside
    okPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.DLG_VGAP, UiUtil.DLG_HGAP * 2,
                                                          UiUtil.DLG_VGAP, UiUtil.DLG_HGAP * 2));
    return okPanel;
  }

  public void goneAway() {
    super.goneAway();
    _view.cleanUp();
  }

  private void onOk() {
    _view.saveControlsToData();
    _actualModel.setRequiredAccountFilter(_view.getRequiredAccountFilter());
    _actualModel.setDisallowedAccountFilter(_view.getDisallowedAccountFilter());
    goAway();
  }

  private void onCancel() {
    goAway();
  }
}