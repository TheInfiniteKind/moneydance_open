package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.awt.GridC;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class YahooDialog extends JDialog {
  private static final String SIZE_KEY = "yahooqt.size";
  private static final String LOCATION_KEY = "yahooqt.location";

  private JPanel contentPane = new JPanel(new BorderLayout(5, 5));
  private JButton buttonOK = new JButton("OK");
  private JButton buttonCancel = new JButton("Cancel");
  private JButton buttonNow = new JButton("Update Now");
  private UserPreferences preferences;
  private JCheckBox doQuotesField = new JCheckBox();
  private JCheckBox doRatesField = new JCheckBox();
  private JSpinner numUnitsField = new JSpinner(new SpinnerNumberModel(1, 1, 50, 1));
  private JComboBox unitField = new JComboBox(TimeUnit.STANDARD_UNITS);

  public YahooDialog(final FeatureModuleContext context) {
    super();
    this.preferences = ((com.moneydance.apps.md.controller.Main) context).getPreferences();
    initUI();
    setContentPane(contentPane);
    setModal(true);
    getRootPane().setDefaultButton(buttonOK);
    Dimension size = preferences.getSizeSetting(SIZE_KEY);
    if (size.width == 0) {
      pack();
    } else {
      setSize(size);
    }
    Point location = preferences.getXYSetting(LOCATION_KEY, -1, -1);
    if (location.x == -1) {
      Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
      location.x = (screenSize.width - getWidth()) / 2;
      location.y = (screenSize.height - getHeight()) / 2;
    }
    setLocation(location);

    buttonNow.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        context.showURL("moneydance:fmodule:yahooqt:update");
      }
    });
    buttonOK.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        onOK();
      }
    });

    buttonCancel.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        dispose();
      }
    });
  }

  private void initUI() {
    JPanel fieldPanel = new JPanel(new GridBagLayout());
    fieldPanel.add(new JLabel("Update Stocks:"), GridC.getc(0, 0).label());
    doQuotesField.setSelected(preferences.getBoolSetting(Main.DOWNLOAD_QUOTES_KEY, true));
    fieldPanel.add(doQuotesField, GridC.getc(1, 0).west());
    fieldPanel.add(new JLabel("Update Exchange Rates:"), GridC.getc(0, 1).label());
    fieldPanel.add(doRatesField, GridC.getc(1, 1).west());
    doRatesField.setSelected(preferences.getBoolSetting(Main.DOWNLOAD_RATES_KEY, true));
    fieldPanel.add(new JLabel("Update Frequency:"), GridC.getc(0, 2).label());
    fieldPanel.add(numUnitsField, GridC.getc(1, 2).field().wx(0));
    numUnitsField.addChangeListener(new ChangeListener() {
      public void stateChanged(ChangeEvent e) {
        unitField.repaint();
      }
    });
    fieldPanel.add(unitField, GridC.getc(2, 2).field().wx(0));
    unitField.setRenderer(new GenericListCellRenderer() {
      protected String getText(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
        if (value instanceof TimeUnit) {
          TimeUnit unit = (TimeUnit) value;
          return numUnitsField.getValue().toString().equals("1") ? unit.getSingularName() : unit.getPluralName();
        } else {
          return super.getText(list, value, index, selected, cellHasFocus);
        }
      }
    });
    try {
      SimpleFrequency freq = SimpleFrequency.fromString(preferences.getSetting(Main.UPDATE_FREQUENCY_KEY, ""));
      numUnitsField.setValue(new Integer(freq.getNumberOfUnits()));
      unitField.setSelectedItem(freq.getUnit());
    } catch (IllegalArgumentException ignored) {
    }
    fieldPanel.add(new JPanel(), GridC.getc(3, 2).fillx().wx(1.0f)); // spring
    fieldPanel.add(new JPanel(), GridC.getc(0, 3).filly().wy(1.0f)); // spring

    contentPane.add(fieldPanel, BorderLayout.CENTER);

    JPanel buttonPanel = new JPanel(new FlowLayout());
    buttonPanel.add(buttonNow);
    buttonPanel.add(buttonOK);
    buttonPanel.add(buttonCancel);
    contentPane.add(buttonPanel, BorderLayout.SOUTH);
  }

  private void onOK() {
    preferences.setSetting(Main.AUTO_UPDATE_KEY, doQuotesField.isSelected() || doRatesField.isSelected());
    preferences.setSetting(Main.DOWNLOAD_QUOTES_KEY, doQuotesField.isSelected());
    preferences.setSetting(Main.DOWNLOAD_RATES_KEY, doRatesField.isSelected());
    TimeUnit unit = (TimeUnit) unitField.getSelectedItem();
    int num = ((Number) numUnitsField.getValue()).intValue();
    SimpleFrequency freq = new SimpleFrequency(unit, num);
    preferences.setSetting(Main.UPDATE_FREQUENCY_KEY, freq.toString());
    dispose();
  }

  public void dispose() {
    super.dispose();    //To change body of overridden methods use File | Settings | File Templates.
    preferences.setXYSetting(LOCATION_KEY, getLocation());
    preferences.setSizeSetting(SIZE_KEY, getSize());
  }

  public static class GenericListCellRenderer extends DefaultListCellRenderer {
    public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
      setComponentOrientation(list.getComponentOrientation());
      setBackground(getBackground(list, value, index, isSelected, cellHasFocus));
      setForeground(getForeground(list, value, index, isSelected, cellHasFocus));
      setIcon(getIcon(list, value, index, isSelected, cellHasFocus));
      setText(getText(list, value, index, isSelected, cellHasFocus));
      setEnabled(isEnabled(list, value, index, isSelected, cellHasFocus));
      setFont(getFont(list, value, index, isSelected, cellHasFocus));
      setBorder(getBorder(list, value, index, isSelected, cellHasFocus));
      return this;
    }

    protected String getText(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return value instanceof Icon || value == null ? "" : value.toString();
    }

    protected Icon getIcon(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return value instanceof Icon ? (Icon) value : null;
    }

    protected Border getBorder(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return cellHasFocus ? UIManager.getBorder("List.focusCellHighlightBorder") : noFocusBorder;
    }

    protected Font getFont(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return list.getFont();
    }

    protected boolean isEnabled(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return list.isEnabled();
    }

    protected Color getBackground(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return selected ? list.getSelectionBackground() : list.getBackground();
    }

    protected Color getForeground(JList list, Object value, int index, boolean selected, boolean cellHasFocus) {
      return selected ? list.getSelectionForeground() : list.getForeground();
    }
  }
}
