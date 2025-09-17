/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.CurrencyType
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import com.moneydance.modules.features.yahooqt.SQUtil.addLabelSuffix
import com.moneydance.modules.features.yahooqt.SQUtil.getLabelText
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import com.moneydance.util.UiUtil
import java.awt.BorderLayout
import java.awt.GridBagLayout
import javax.swing.*

/**
 * Dialog that edits a Stock Exchange definition.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class ExchangeDialog internal constructor(owner: JDialog?,
                                          private val _mdGui: MoneydanceGUI, private val _resources: ResourceProvider,
                                          private val _exchange: StockExchange,
                                          private val _exchangeList: StockExchangeList) : JDialog(owner, _resources.getString(L10NStockQuotes.EDIT_EXCHANGE_TITLE), true) {
  private var _name: JTextField? = null
  private var _yahooSuffix: JTextField? = null
  private var _googlePrefix: JTextField? = null
  private var _multiplier: JTextField? = null
  private var _currencyChoice: JComboBox<*>? = null
  private var _errorText: JLabel? = null
  
  init {
    initUI()
    setLocationRelativeTo(owner)
  }
  
  private fun initUI() {
    layout = BorderLayout()
    //    setIconImage(Main.getIcon()); // available in Java 1.6 only
    val contentPane = contentPane
    val fieldPanel = JPanel(GridBagLayout())
    fieldPanel.border = BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.HGAP,
                                                        UiUtil.VGAP, UiUtil.HGAP)
    // name
    fieldPanel.add(JLabel(getLabelText(_resources, L10NStockQuotes.EXCHANGE_LABEL)),
                   GridC.getc(0, 0).label())
    _name = JTextField(_exchange.name!!.trim())
    fieldPanel.add(_name, GridC.getc(1, 0).field())
    // currency (label text is in the standard Moneydance resources)
    setupCurrencySelector()
    fieldPanel.add(
      JLabel(
        addLabelSuffix(
          _resources,
          _mdGui.getStr(L10NStockQuotes.CURRENCY_LABEL)
        )
      ), GridC.getc(0, 1).label()
    )
    fieldPanel.add(_currencyChoice, GridC.getc(1, 1).field())
    // Yahoo suffix
    fieldPanel.add(JLabel(getLabelText(_resources, L10NStockQuotes.YAHOO_SUFFIX_LABEL)),
                   GridC.getc(0, 2).label())
    _yahooSuffix = JTextField(_exchange.symbolYahoo)
    fieldPanel.add(_yahooSuffix, GridC.getc(1, 2).field())
    // Google prefix
    fieldPanel.add(JLabel(getLabelText(_resources, L10NStockQuotes.GOOGLE_PREFIX_LABEL)),
                   GridC.getc(0, 3).label())
    _googlePrefix = JTextField(_exchange.symbolGoogle)
    fieldPanel.add(_googlePrefix, GridC.getc(1, 3).field())
    // price multiplier
    fieldPanel.add(JLabel(getLabelText(_resources, L10NStockQuotes.MULTIPLIER_LABEL)),
                   GridC.getc(0, 4).label())
    _multiplier = JTextField(_exchange.priceMultiplier.toString())
    fieldPanel.add(_multiplier, GridC.getc(1, 4).field())
    // error text
    _errorText = JLabel()
    fieldPanel.add(_errorText, GridC.getc(0, 5).colspan(2).fillx().insets(UiUtil.DLG_VGAP, 0,
                                                                          UiUtil.DLG_VGAP, 0))
    
    fieldPanel.border = BorderFactory.createEmptyBorder(UiUtil.DLG_VGAP, UiUtil.DLG_HGAP, 0, UiUtil.DLG_HGAP)
    contentPane.add(fieldPanel, BorderLayout.CENTER)
    
    val okButtons = OKButtonPanel(_mdGui, { buttonId ->
      if (buttonId == OKButtonPanel.ANSWER_OK) {
        onOK()
      } else {
        isVisible = false
      }
    }, OKButtonPanel.QUESTION_OK_CANCEL)
    okButtons.border = BorderFactory.createEmptyBorder(UiUtil.VGAP, UiUtil.DLG_HGAP,
                                                       UiUtil.DLG_VGAP, UiUtil.DLG_HGAP)
    contentPane.add(okButtons, BorderLayout.SOUTH)
    pack()
  }
  
  private fun setupCurrencySelector() {
    val currencyTable = _mdGui.currentBook!!.currencies
    val currencyModel = CustomCurrencyModel(currencyTable, CurrencyType.Type.CURRENCY)
    _currencyChoice = JComboBox(currencyModel)
    var currency = currencyTable.getCurrencyByIDString(_exchange.currencyCode)
    if (currency == null) currency = currencyTable.baseType
    currencyModel.selectedItem = currency
  }
  
  private fun showError(resourceKey: String?) {
    if (resourceKey == null) {
      _errorText!!.text = null
      return
    }
    val message = StringBuilder()
    message.append(N12EStockQuotes.HTML_BEGIN)
    message.append(N12EStockQuotes.RED_FONT_BEGIN)
    message.append(_resources.getString(resourceKey))
    message.append(N12EStockQuotes.FONT_END)
    message.append(N12EStockQuotes.HTML_END)
    _errorText!!.text = message.toString()
  }
  
  private fun onOK() {
    // save what we have in the edit windows
    val candidate = _name!!.text.trim()
    if (isBlank(candidate)) {
      showError(L10NStockQuotes.ERROR_NAME_BLANK)
      return
    }
    val multiplier: Double
    try {
      multiplier = _multiplier!!.text.trim().toDouble()
    } catch (nfex: NumberFormatException) {
      showError(L10NStockQuotes.ERROR_MULTIPLIER)
      return
    }
    if (multiplier < 0.0) {
      // negative multipliers are not valid
      showError(L10NStockQuotes.ERROR_MULTIPLIER)
      return
    }
    // everything is valid, save
    _exchange.name = candidate
    _exchange.setCurrency((_currencyChoice!!.selectedItem as CurrencyType))
    _exchange.symbolYahoo = _yahooSuffix!!.text.trim()
    _exchange.symbolGoogle = _googlePrefix!!.text.trim()
    _exchange.priceMultiplier = multiplier
    val success = _exchangeList.save()
    if (!success) {
      _mdGui.showErrorMessage(this, _resources.getString(L10NStockQuotes.ERROR_SAVE))
    }
    isVisible = false
  }
}
