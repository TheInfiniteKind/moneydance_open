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

import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.apps.md.controller.time.DateRangeOption;
import com.infinitekind.moneydance.model.RootAccount;
import com.moneydance.apps.md.view.HomePageView;
import com.moneydance.apps.md.view.gui.DateRangeChooser;
import com.moneydance.apps.md.view.gui.MDAction;
import com.moneydance.apps.md.view.gui.MDImages;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;
import com.moneydance.apps.md.view.gui.OKButtonListener;
import com.moneydance.apps.md.view.gui.OKButtonPanel;
import com.moneydance.apps.md.view.gui.OKButtonWindow;
import com.moneydance.awt.GridC;
import com.infinitekind.util.CustomDateFormat;
import com.infinitekind.util.UiUtil;

import javax.swing.AbstractAction;
import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Container;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Image;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.List;

/**
 * A home page view that displays the ratios list and the results, along with report links.
 *
 * @author Kevin Menningen
 */
class RatiosHomeView
    implements HomePageView, PropertyChangeListener {
  private final ResourceProvider _resources;
  private final RatiosExtensionModel _mainModel;
  private RatiosHomePage _view = null;

  RatiosHomeView(final ResourceProvider resources, final RatiosExtensionModel model) {
    _resources = resources;
    _mainModel = model;
    _mainModel.addPropertyChangeListener(this);
  }

  public String getID() {
    return N12ERatios.HOME_PAGE_ID;
  }

  public JComponent getGUIView(RootAccount rootAccount) {
    _mainModel.setData(rootAccount);
    if (_view == null) {
      _view = new RatiosHomePage(_resources, _mainModel.getGUI());
      _view.layoutUI();
    }
    return _view;
  }

  public void setActive(boolean active) {
    if (_view != null) {
      _view.setVisible(active);
    }
  }

  public void refresh() {
    _mainModel.getGUI();
    if (_view != null) {
      _view.refresh();
    }
  }

  public void reset() {
    // no listeners to clean up
    _view = null;
  }

  public String toString() {
    return _resources.getString(L10NRatios.TITLE);
  }

  public void propertyChange(PropertyChangeEvent event) {
    final String eventName = event.getPropertyName();
    if (N12ERatios.SETTINGS_CHANGE.equals(eventName)) {
      // complete revamp
      if (_view != null) _view.refresh();
    } else if (N12ERatios.DATE_RANGE_OPTION.equals(eventName)
        || N12ERatios.RECALCULATE.equals(eventName)) {
      // recalculation has already taken place
      if (_view != null) _view.refresh();
    }
  }


  /////////////////////////////////////////////////////////////////////////////////////////
  // Private Methods
  /////////////////////////////////////////////////////////////////////////////////////////


  /////////////////////////////////////////////////////////////////////////////////////////
  // Inner Classes
  /////////////////////////////////////////////////////////////////////////////////////////

  private class RatiosHomePage
      extends JPanel {
    private final ResourceProvider _resources;
    private final MoneydanceGUI _mdGui;
    private JPanel _titlePanel;
    private JPanel _listPanel;
    private JLabel _title;
    private JLabel _dateRangeLabel;

    RatiosHomePage(ResourceProvider resources, MoneydanceGUI mdGui) {
      _resources = resources;
      _mdGui = mdGui;
      createControls();
    }

    /**
     * Refresh or lay out the controls. This should only be called on the UI thread.
     */
    void layoutUI() {
      // remove any existing controls
      remove(_titlePanel);
      remove(_listPanel);

      // update and add the fixed panel at the top
      // these strings come from the main Moneydance resources
      _dateRangeLabel.setText(getDateRangeDisplay());
      _title.setText(RatiosUtil.getLabelText(_resources, L10NRatios.HOME_PAGE_LABEL));
      add(_titlePanel, BorderLayout.NORTH);

      // now build (or rebuild) the panel of ratio items
      int rows = _mainModel.getRatioCount();

      // clean up and regenerate
      _listPanel.removeAll();
      _listPanel.setLayout(new GridLayout(rows, 1, UiUtil.HGAP, 0));
      for (int index = 0; index < rows; index++) {
        RatioView view = _mainModel.getRatioView(index);
        if (view != null) {
          view.layoutUI(_mainModel.getDecimalPlaces(), getAlternateColor());
          _listPanel.add(view, index);
        }
      }
      add(_listPanel, BorderLayout.CENTER);

      // components were added or removed, re-layout
      forceRepaint();
    }

    /**
     * Get the home page item to be redrawn. This should only be called on the UI thread.
     */
    private void forceRepaint() {
      validate();
      Container parent = getParent();
      if (parent != null) {
        parent.validate();
      }
      repaint();
    }

    /**
     * Get the alternate background color for home page items.
     * @return The alternate home page background color.
     */
    private Color getAlternateColor() {
      return _mainModel.getGUI().getColors().homePageAltBG;
    }

    private String getDateRangeDisplay() {
      final String optionKey = getDateRangeOptionKey();
      if (N12ERatios.CUSTOM_DATE_KEY.equals(optionKey)) {
        DateRange dateRange = _mainModel.getSettings().getDateRange();
        if (dateRange == null) return _resources.getString(L10NRatios.CUSTOM_DATE_MENU);
        CustomDateFormat dateFormat = _mainModel.getGUI().getPreferences().getShortDateFormatter();
        return dateRange.format(dateFormat);
      }
      return _mainModel.getGUI().getStr(optionKey);
    }

    private String getDateRangeOptionKey() {
      final RatioSettings settings = _mainModel.getSettings();
      if (settings == null) return DateRangeOption.DEFAULT.getResourceKey();
      if (settings.getIsCustomDate()) return N12ERatios.CUSTOM_DATE_KEY;
      return settings.getDateRangeOption();
    }

    private void createControls() {
      setLayout(new BorderLayout());
      // give consistent appearance with other home page views
      setOpaque(false);
      setBorder(MoneydanceLAF.homePageBorder);

      // top line is the label and the button
      _titlePanel = new JPanel(new BorderLayout());
      _titlePanel.setOpaque(false);
      _title = new JLabel(RatiosUtil.getLabelText(_resources, L10NRatios.HOME_PAGE_LABEL));
      _title.setOpaque(false);
      _titlePanel.add(_title, BorderLayout.WEST);
      String dateRange = getDateRangeDisplay();
      _dateRangeLabel = new JLabel(dateRange);
      _dateRangeLabel.setOpaque(false);

      Image image = _mainModel.getGUI().getImage(MDImages.SELECTOR_SMALL);
      ImageIcon icon = new ImageIcon(image);
      _dateRangeLabel.setIcon(icon);
      final JComponent dateParent = _dateRangeLabel;
      _dateRangeLabel.addMouseListener(new MouseAdapter() {
        @Override
        public void mouseClicked(MouseEvent e) {
          showDateRangeMenu(dateParent);
        }
      });
      _dateRangeLabel.setBorder(BorderFactory.createEmptyBorder(0, UiUtil.HGAP, 0, 0));
      _titlePanel.add(_dateRangeLabel, BorderLayout.CENTER);

      final MoneydanceGUI mdGui = _mainModel.getGUI();
      MDAction settingsAction = new MDAction(mdGui, L10NRatios.SETTINGS_LABEL, new ActionListener() {
        public void actionPerformed(ActionEvent e) {
          mdGui.getMain().showURL(N12ERatios.INVOKE_URL_PREFIX + N12ERatios.SHOW_DIALOG_COMMAND);
        }
      });

      final JButton button;
      if(MoneydanceGUI.isMac) {
        button = new JButton(settingsAction);
        button.putClientProperty("JButton.buttonType", "roundRect");
      } else {
        button = mdGui.makeButtonBarButton(settingsAction);
      }
      _titlePanel.add(button, BorderLayout.EAST);
      add(_titlePanel, BorderLayout.NORTH);

      // now add the list of ratios
      _listPanel = new JPanel();
      _listPanel.setOpaque(false);
    }

    public void refresh() {
      if (_mdGui.getSuspendRefreshes()) return;
      UiUtil.runOnUIThread(new Runnable() {
        public void run() {
          layoutUI();
        }
      });
    }


    private void showDateRangeMenu(final JComponent dateParent) {
      JPopupMenu menu = new JPopupMenu();

      // build the indices in exactly the same order as in the model
      final List<String> keys = _mainModel.getSettings().getDateRangeChoiceKeys();
      for (final String key : keys) {
        JMenuItem item = new JMenuItem(new DateRangeAction(_mainModel.getGUI(), _mainModel, key));
        menu.add(item);
      }
      // tack on the custom range
      menu.addSeparator();
      menu.add(new JMenuItem(new DateRangeAction(_mainModel)));
      Rectangle bounds = dateParent.getBounds();
      menu.show(dateParent, 0, (int) bounds.getHeight());
    }

  } // class RatiosHomePage

  private void showCustomDateRange() {
    MoneydanceGUI mdGUI = _mainModel.getGUI();
    JPanel panel = new JPanel(new GridBagLayout());

    int y = 0;
    final DateRangeChooser dateRanger = new DateRangeChooser(mdGUI);
    // start with the currently selected date range
    dateRanger.setOption(_mainModel.getSettings().getDateRangeOption());
    // add the full panel for keyboard shortcuts
    panel.add(dateRanger.getChoiceLabel(), GridC.getc(0, y).label());
    panel.add(dateRanger.getChoice(), GridC.getc(1, y++).field());

    panel.add(dateRanger.getStartLabel(), GridC.getc(0, y).label());
    panel.add(dateRanger.getStartField(), GridC.getc(1, y++).field());
    dateRanger.getStartField().requestFocusInWindow();

    panel.add(dateRanger.getEndLabel(), GridC.getc(0, y).label());
    panel.add(dateRanger.getEndField(), GridC.getc(1, y++).field());
    panel.add(Box.createHorizontalStrut(120), GridC.getc(0, y).colspan(2));

    OKButtonListener listener = new OKButtonListener() {
      public void buttonPressed(int nButton) {
        if (nButton == OKButtonPanel.ANSWER_OK) {
          _mainModel.setCustomDateRange(dateRanger.getDateRange());
        }
      }
    };
    OKButtonWindow dialog = new OKButtonWindow(mdGUI, _view,
                                               _resources.getString(L10NRatios.CUSTOM_DATE_TITLE),
                                               listener, OKButtonPanel.QUESTION_OK_CANCEL);
    dialog.setInputPanel(panel);
    dialog.setVisible(true);
  }

  /**
   * Action for selecting a date range, used by the ratios home page. There is one of these actions for each of the date range
   * options in the picker menu.
   * <p/>
   * This class is immutable.
   */
  private class DateRangeAction
      extends AbstractAction {
    /**
     * The date range the user is selecting when firing this action.
     */
    private final String _dateRangeOption;
    /**
     * Controller to change to the new date range.
     */
    private final RatiosExtensionModel _model;

    /**
     * Constructor for custom date range, to allow all fields to be immutable.
     *
     * @param model         The date range the user is selecting when firing this action.
     */
    public DateRangeAction(final RatiosExtensionModel model) {
      super(model.getResources().getString(L10NRatios.CUSTOM_DATE_MENU));
      _dateRangeOption = N12ERatios.CUSTOM_DATE_KEY;
      _model = model;
    }

    /**
     * Constructor for standard date ranges, to allow all fields to be immutable.
     *
     * @param mdGui         The user interface resources for Moneydance.
     * @param model         Settings object to change to the new date range.
     * @param dateOptionKey The date range key the user is selecting when firing this action.
     */
    public DateRangeAction(final MoneydanceGUI mdGui, final RatiosExtensionModel model, final String dateOptionKey) {
      super(mdGui.getStr(dateOptionKey));
      _dateRangeOption = dateOptionKey;
      _model = model;
    }

    /**
     * {@inheritDoc}
     *
     * @param event {@inheritDoc}
     */
    public void actionPerformed(ActionEvent event) {
      if (N12ERatios.CUSTOM_DATE_KEY.equals(_dateRangeOption)) {
        showCustomDateRange();
        return;
      }
      // standard date ranges can be set from the key
      _model.setDateRangeOption(_dateRangeOption);
    }
  }
}
