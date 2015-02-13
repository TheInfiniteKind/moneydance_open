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

import com.moneydance.apps.md.view.gui.MDImages;
import com.moneydance.awt.AwtUtil;
import com.moneydance.awt.GridC;
import com.moneydance.util.UiUtil;

import javax.swing.BorderFactory;
import javax.swing.Icon;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.Graphics2D;
import java.awt.GridBagLayout;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

/**
 * Shows the UI representation of a single ratio in the list
 *
 * @author Kevin Menningen
 */
class RatioView extends JPanel {
  private final RatiosExtensionModel _mainModel;
  private final RatioEntry _ratio;
  private final String _nanString;
  private final JLabel _report;
  private JLabel _name;
  private JLabel _ratioValue;

  RatioView(final RatioEntry ratio, final RatiosExtensionModel mainModel) {
    super(new GridBagLayout());
    _mainModel = mainModel;
    _ratio = ratio;
    _nanString = mainModel.getResources().getString(L10NRatios.NAN);
    Icon reportImage = mainModel.getGUI().getImages().getIcon(MDImages.SB_REPORT);
    _report = new JLabel(reportImage, JLabel.CENTER);
  }

  void layoutUI(int decimalPlaces, final Color alternateColor) {
    setBorder(BorderFactory.createEmptyBorder(UiUtil.VGAP, 0, UiUtil.VGAP, 0));
    removeAll();
    _name = new JLabel(_ratio.toString());
    _name.setOpaque(false);
    final double value = _ratio.getValue();
    char decimal = _mainModel.getGUI().getPreferences().getDecimalChar();
    final String display = RatiosUtil.formatRatioValue(value, decimal, decimalPlaces, _nanString, _ratio.getShowPercent());
    _ratioValue = new JLabel(display, JLabel.RIGHT);
    if (!Double.isNaN(value) && !Double.isInfinite(value) && (value < 0)) {
      _ratioValue.setForeground(Color.RED);
    }
    _ratioValue.setOpaque(false);
    setupReportIcon();
    add(_name, GridC.getc(0, 0).wx(1).fillx());
    add(_ratioValue, GridC.getc(1, 0).east());
    add(_report, GridC.getc(2, 0).insets(0, UiUtil.DLG_HGAP, 0, 0).east());
    updateBackgroundColor(alternateColor);
    validate();
  }

  private void setupReportIcon() {
    _report.setHorizontalAlignment(JLabel.CENTER);
    _report.addMouseListener(new MouseAdapter() {
      public void mouseEntered(MouseEvent event) {
        setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
      }
      public void mouseExited(MouseEvent e) {
        setCursor(Cursor.getDefaultCursor());
      }
      public void mouseClicked(MouseEvent event) {
        // it doesn't matter if it's the right or left button, or if double clicked
        RatioReportGenerator generator = new RatioReportGenerator(_mainModel, _ratio, (Graphics2D)getGraphics());
        RatioReportWindow reportWindow = new RatioReportWindow(_mainModel.getGUI(), AwtUtil.getFrame(RatioView.this),
                                                               generator);
        reportWindow.setVisible(true);
      }
    });
  }

  private void updateBackgroundColor(final Color alternateColor) {
    if (_ratio.getIndex() % 2 == 0) {
      setOpaque(true);
      setBackground(alternateColor);
      _name.setOpaque(true);
      _name.setBackground(alternateColor);
      _ratioValue.setOpaque(true);
      _ratioValue.setBackground(alternateColor);
    } else {
      setOpaque(false);
      _name.setOpaque(false);
      _ratioValue.setOpaque(false);
    }
  }
}
