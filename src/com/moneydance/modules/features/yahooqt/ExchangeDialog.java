/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.model.CurrencyTable;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.view.gui.CurrencyModel;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.OKButtonListener;
import com.moneydance.apps.md.view.gui.OKButtonPanel;
import com.moneydance.awt.GridC;
import com.moneydance.util.UiUtil;

import javax.swing.BorderFactory;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import java.awt.BorderLayout;
import java.awt.Container;
import java.awt.GridBagLayout;

/**
 * Dialog that edits a Stock Exchange definition.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class ExchangeDialog extends JDialog {
  private final StockExchange _exchange;
  private final StockExchangeList _exchangeList;
  private final MoneydanceGUI _mdGui;
  private final ResourceProvider _resources;
  private JTextField _name;
  private JTextField _yahooSuffix;
  private JTextField _googlePrefix;
  private JTextField _multiplier;
  private JComboBox _currencyChoice;
  private JLabel _errorText;

  ExchangeDialog(final JDialog owner,
                 final MoneydanceGUI mdGUI, ResourceProvider resources,
                 final StockExchange exchange,
                 final StockExchangeList exchangeList)
  {
    super(owner, resources.getString(L10NStockQuotes.EDIT_EXCHANGE_TITLE), true);
    _exchange = exchange;
    _exchangeList = exchangeList;
    _mdGui = mdGUI;
    _resources = resources;
    initUI();
    setLocationRelativeTo(owner);
  }

  private void initUI() {
    setLayout(new BorderLayout());
//    setIconImage(Main.getIcon()); // available in Java 1.6 only
    Container contentPane = getContentPane();
    JPanel fieldPanel = new JPanel(new GridBagLayout());
    fieldPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.HGAP,
            UiUtil.VGAP, UiUtil.HGAP));
    // name
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.EXCHANGE_LABEL)),
            GridC.getc(0, 0).label());
    _name = new JTextField(_exchange.getName().trim());
    fieldPanel.add(_name, GridC.getc(1, 0).field());
    // currency (label text is in the standard Moneydance resources)
    setupCurrencySelector();
    fieldPanel.add(new JLabel(SQUtil.addLabelSuffix(_resources,
            _mdGui.getStr(L10NStockQuotes.CURRENCY_LABEL))), GridC.getc(0, 1).label());
    fieldPanel.add(_currencyChoice, GridC.getc(1, 1).field());
    // Yahoo suffix
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.YAHOO_SUFFIX_LABEL)),
            GridC.getc(0, 2).label());
    _yahooSuffix = new JTextField(_exchange.getSymbolYahoo());
    fieldPanel.add(_yahooSuffix, GridC.getc(1, 2).field());
    // Google prefix
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.GOOGLE_PREFIX_LABEL)),
            GridC.getc(0, 3).label());
    _googlePrefix = new JTextField(_exchange.getSymbolGoogle());
    fieldPanel.add(_googlePrefix, GridC.getc(1, 3).field());
    // price multiplier
    fieldPanel.add(new JLabel(SQUtil.getLabelText(_resources, L10NStockQuotes.MULTIPLIER_LABEL)),
            GridC.getc(0, 4).label());
    _multiplier = new JTextField(Double.toString(_exchange.getPriceMultiplier()));
    fieldPanel.add(_multiplier, GridC.getc(1, 4).field());
    // error text
    _errorText = new JLabel();
    fieldPanel.add(_errorText, GridC.getc(0, 5).colspan(2).fillx().insets(UiUtil.DLG_VGAP, 0,
            UiUtil.DLG_VGAP, 0));

    fieldPanel.setBorder(BorderFactory.createEmptyBorder(UiUtil.DLG_VGAP, UiUtil.DLG_HGAP,
            0, UiUtil.DLG_HGAP));
    contentPane.add(fieldPanel, BorderLayout.CENTER);

    OKButtonPanel okButtons = new OKButtonPanel(_mdGui, new OKButtonListener() {
      public void buttonPressed(int buttonId) {
        if (buttonId == OKButtonPanel.ANSWER_OK) {
          onOK();
        } else {
          dispose();
        }
      }
    },OKButtonPanel.QUESTION_OK_CANCEL);
    okButtons.setBorder(BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.DLG_HGAP,
            UiUtil.DLG_VGAP, UiUtil.DLG_HGAP));
    contentPane.add(okButtons, BorderLayout.SOUTH);
    pack();
  }

  private void setupCurrencySelector() {
    CurrencyTable currencyTable = _mdGui.getCurrentAccount().getCurrencyTable();
    CurrencyModel currencyModel = new CurrencyModel(currencyTable, CurrencyType.CURRTYPE_CURRENCY);
    _currencyChoice = new JComboBox(currencyModel);
    CurrencyType currency = currencyTable.getCurrencyByIDString(_exchange.getCurrencyCode());
    if (currency == null) currency = currencyTable.getBaseType();
    currencyModel.setSelectedItem(currency);
  }

  private void showError(String resourceKey) {
    if (resourceKey == null) {
      _errorText.setText(null);
      return;
    }
    StringBuilder message = new StringBuilder();
    message.append(N12EStockQuotes.HTML_BEGIN);
    message.append(N12EStockQuotes.RED_FONT_BEGIN);
    message.append(_resources.getString(resourceKey));
    message.append(N12EStockQuotes.FONT_END);
    message.append(N12EStockQuotes.HTML_END);
    _errorText.setText(message.toString());
  }

  private void onOK() {
    // save what we have in the edit windows
    String candidate = _name.getText().trim();
    if (SQUtil.isBlank(candidate)) {
      showError(L10NStockQuotes.ERROR_NAME_BLANK);
      return;
    }
    double multiplier;
    try {
      multiplier = Double.parseDouble(_multiplier.getText().trim());
    } catch (NumberFormatException nfex) {
      showError(L10NStockQuotes.ERROR_MULTIPLIER);
      return;
    }
    if (multiplier < 0.0) {
      // negative multipliers are not valid
      showError(L10NStockQuotes.ERROR_MULTIPLIER);
      return;
    }
    // everything is valid, save
    _exchange.setName(candidate);
    _exchange.setCurrency((CurrencyType)_currencyChoice.getSelectedItem());
    _exchange.setSymbolYahoo(_yahooSuffix.getText().trim());
    _exchange.setSymbolGoogle(_googlePrefix.getText().trim());
    _exchange.setPriceMultiplier(multiplier);
    final boolean success = _exchangeList.save();
    if (!success) {
      _mdGui.showErrorMessage(this, _resources.getString(L10NStockQuotes.ERROR_SAVE));
    }
    dispose();
  }
}
