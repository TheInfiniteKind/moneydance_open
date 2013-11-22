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

import com.moneydance.apps.md.controller.AccountFilter;
import com.moneydance.apps.md.controller.DateRange;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.RootAccount;
import com.moneydance.apps.md.model.Txn;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.TagLogic;
import com.moneydance.util.StreamTable;

import java.util.List;

/**
 * A definition of a ratio. Contains a numerator, a denominator, and some settings.
 *
 * @author Kevin Menningen
 */
public class RatioEntry {
  private final RatioPart _numerator = new RatioPart();
  private final RatioPart _denominator = new RatioPart();
  private String _name;
  private int _index;
  private double _value;
  private boolean _showPercent;
  private boolean _alwaysPositive;
  private boolean _useTaxDate;
  private String _notes;

  RatioEntry() {
    _name = N12ERatios.DEFAULT_NAME;
    _notes = N12ERatios.EMPTY;
    _index = -1;
  }

  RatioEntry(final StreamTable settings, final MoneydanceGUI mdGui) {
    _name = settings.getStr(N12ERatios.NAME_KEY, N12ERatios.EMPTY);
    _index = settings.getInt(N12ERatios.INDEX_KEY, -1);
    _notes = settings.getStr(N12ERatios.NOTES_KEY, N12ERatios.EMPTY);
    _showPercent = settings.getBoolean(N12ERatios.SHOW_PERCENT_KEY, true);
    _alwaysPositive = settings.getBoolean(N12ERatios.ALWAYS_POSITIVE_KEY, true);
    _useTaxDate = settings.getBoolean(N12ERatios.USE_TAX_DATE_KEY, false);
    _numerator.loadFromSettings(settings, mdGui,
                                N12ERatios.NUMERATOR_TXN_MATCH_KEY,
                                N12ERatios.NUMERATOR_LABEL_KEY,
                                N12ERatios.NUMERATOR_REQUIRED_LIST_KEY,
                                N12ERatios.NUMERATOR_DISALLOWED_LIST_KEY,
                                N12ERatios.NUMERATOR_TAGS_KEY);
    _denominator.loadFromSettings(settings, mdGui,
                                  N12ERatios.DENOMINATOR_TXN_MATCH_KEY,
                                  N12ERatios.DENOMINATOR_LABEL_KEY,
                                  N12ERatios.DENOMINATOR_REQUIRED_LIST_KEY,
                                  N12ERatios.DENOMINATOR_DISALLOWED_LIST_KEY,
                                  N12ERatios.DENOMINATOR_TAGS_KEY);
  }

  String getSettingsString() {
    final StreamTable settings = new StreamTable();
    settings.put(N12ERatios.NAME_KEY, _name);
    settings.put(N12ERatios.INDEX_KEY, _index);
    settings.put(N12ERatios.NOTES_KEY, _notes);
    settings.put(N12ERatios.SHOW_PERCENT_KEY, _showPercent);
    settings.put(N12ERatios.ALWAYS_POSITIVE_KEY, _alwaysPositive);
    settings.put(N12ERatios.USE_TAX_DATE_KEY, _useTaxDate);
    _numerator.saveToSettings(settings,
                              N12ERatios.NUMERATOR_TXN_MATCH_KEY,
                              N12ERatios.NUMERATOR_LABEL_KEY,
                              N12ERatios.NUMERATOR_REQUIRED_LIST_KEY,
                              N12ERatios.NUMERATOR_DISALLOWED_LIST_KEY,
                              N12ERatios.NUMERATOR_TAGS_KEY);
    _denominator.saveToSettings(settings,
                                N12ERatios.DENOMINATOR_TXN_MATCH_KEY,
                                N12ERatios.DENOMINATOR_LABEL_KEY,
                                N12ERatios.DENOMINATOR_REQUIRED_LIST_KEY,
                                N12ERatios.DENOMINATOR_DISALLOWED_LIST_KEY,
                                N12ERatios.DENOMINATOR_TAGS_KEY);
    return settings.writeToString();
  }

  public String toString() {
    return (_name == null) ? N12ERatios.NOT_SPECIFIED : _name;
  }

  void setIndex(int index) { _index = index; }
  int getIndex() { return _index; }
  void setNumeratorValue(double value) { _numerator.setValue(value); }
  double getNumeratorValue() { return _numerator.getValue(); }
  void setDenominatorValue(double value) { _denominator.setValue(value); }
  double getDenominatorValue() { return _denominator.getValue(); }
  void setValue(double value) { _value = value; }
  double getValue() { return _value; }
  void setShowPercent(final boolean showPercent) { _showPercent = showPercent; }
  boolean getShowPercent() { return _showPercent; }
  void setAlwaysPositive(final boolean alwaysPositive) { _alwaysPositive = alwaysPositive; }
  boolean getAlwaysPositive() { return _alwaysPositive; }
  void setUseTaxDate(final boolean useTaxDate) { _useTaxDate = useTaxDate; }
  boolean getUseTaxDate() { return _useTaxDate; }
  void setNumeratorTxnMatchBoth() { _numerator.setTxnMatchBoth(); }
  boolean getNumeratorTxnMatchBoth() { return _numerator.getTxnMatchBoth(); }
  void setDenominatorTxnMatchBoth() { _denominator.setTxnMatchBoth(); }
  boolean getDenominatorTxnMatchBoth() { return _denominator.getTxnMatchBoth(); }
  void setNumeratorTxnMatchInto() { _numerator.setTxnMatchInto(); }
  boolean getNumeratorTxnMatchInto() { return _numerator.getTxnMatchInto(); }
  void setDenominatorTxnMatchInto() { _denominator.setTxnMatchInto(); }
  boolean getDenominatorTxnMatchInto() { return _denominator.getTxnMatchInto(); }
  void setNumeratorTxnMatchOutOf() { _numerator.setTxnMatchOutOf(); }
  boolean getNumeratorTxnMatchOutOf() { return _numerator.getTxnMatchOutOf(); }
  void setDenominatorTxnMatchOutOf() { _denominator.setTxnMatchOutOf(); }
  boolean getDenominatorTxnMatchOutOf() { return _denominator.getTxnMatchOutOf(); }
  void setNumeratorEndBalanceOnly() { _numerator.setEndBalanceOnly(); }
  boolean getNumeratorEndBalanceOnly() { return _numerator.getEndBalanceOnly(); }
  void setDenominatorEndBalanceOnly() { _denominator.setEndBalanceOnly(); }
  boolean getDenominatorEndBalanceOnly() { return _denominator.getEndBalanceOnly(); }
  void setNumeratorAverageBalance() { _numerator.setAverageBalance(); }
  boolean getNumeratorAverageBalance() { return _numerator.getAverageBalance(); }
  void setDenominatorAverageBalance() { _denominator.setAverageBalance(); }
  boolean getDenominatorAverageBalance() { return _denominator.getAverageBalance(); }
  void setNumeratorBeginningBalance() { _numerator.setBeginningBalance(); }
  boolean getNumeratorBeginningBalance() { return _numerator.getBeginningBalance(); }
  void setDenominatorBeginningBalance() { _denominator.setBeginningBalance(); }
  boolean getDenominatorBeginningBalance() { return _denominator.getBeginningBalance(); }
  String getName() { return _name; }
  void setName(final String name) { _name = name; }
  String getNotes() { return _notes; }
  void setNotes(final String notes) { _notes = notes; }
  String getNumeratorLabel() { return _numerator.getLabel(); }
  void setNumeratorLabel(final String label) { _numerator.setLabel(label); }
  String getDenominatorLabel() { return _denominator.getLabel(); }
  void setDenominatorLabel(final String label) { _denominator.setLabel(label); }

  void setNumeratorRequiredAccounts(AccountFilter accountFilter, final RootAccount root) {
    _numerator.setRequiredAccounts(accountFilter, root);
  }
  void setNumeratorEncodedRequiredAccounts(final String encodedAccounts) { 
    _numerator.setEncodedRequiredAccounts(encodedAccounts); 
  }
  String getNumeratorEncodedRequiredAccounts() { return _numerator.getEncodedRequiredAccounts(); }
  List<Account> getNumeratorRequiredAccountList() { return _numerator.getRequiredAccountList(); }
  void setNumeratorDisallowedAccounts(AccountFilter accountFilter, final RootAccount root) {
    _numerator.setDisallowedAccounts(accountFilter, root);
  }
  void setNumeratorEncodedDisallowedAccounts(final String encodedAccounts) { 
    _numerator.setEncodedDisallowedAccounts(encodedAccounts); 
  }
  String getNumeratorEncodedDisallowedAccounts() { return _numerator.getEncodedDisallowedAccounts(); }
  List<Account> getNumeratorDisallowedAccountList() { return _numerator.getDisallowedAccountList(); }

  void setDenominatorRequiredAccounts(AccountFilter accountFilter, final RootAccount root) {
    _denominator.setRequiredAccounts(accountFilter, root);
  }
  void setDenominatorEncodedRequiredAccounts(final String encodedAccounts) { 
    _denominator.setEncodedRequiredAccounts(encodedAccounts); 
  }
  String getDenominatorEncodedRequiredAccounts() { return _denominator.getEncodedRequiredAccounts(); }
  List<Account> getDenominatorRequiredAccountList() { return _denominator.getRequiredAccountList(); }
  void setDenominatorDisallowedAccounts(AccountFilter accountFilter, final RootAccount root) {
    _denominator.setDisallowedAccounts(accountFilter, root);
  }
  void setDenominatorEncodedDisallowedAccounts(final String encodedAccounts) { 
    _denominator.setEncodedDisallowedAccounts(encodedAccounts); 
  }
  String getDenominatorEncodedDisallowedAccounts() { return _denominator.getEncodedDisallowedAccounts(); }
  List<Account> getDenominatorDisallowedAccountList() { return _denominator.getDisallowedAccountList(); }


  void setNumeratorTags(final String tagString) { _numerator.setTags(tagString);  }
  String getNumeratorTags() { return _numerator.getTags(); }
  void setNumeratorTagLogic(final TagLogic tagLogic) { _numerator.setTagLogic(tagLogic); }
  TagLogic getNumeratorTagLogic() { return _numerator.getTagLogic(); }
  
  void setDenominatorTags(final String tagString) {_denominator.setTags(tagString);  }
  String getDenominatorTags() { return _denominator.getTags(); }
  void setDenominatorTagLogic(final TagLogic tagLogic) { _denominator.setTagLogic(tagLogic); }
  TagLogic getDenominatorTagLogic() { return _denominator.getTagLogic(); }

  void prepareForTxnProcessing(final RootAccount root, final DateRange dateRange,
                                      final boolean isNumerator, final IRatioReporting reporting) {
    if ((reporting == null) || isNumerator) _numerator.prepareForTxnProcessing(root, dateRange, _useTaxDate);
    if ((reporting == null) || !isNumerator) _denominator.prepareForTxnProcessing(root, dateRange, _useTaxDate);
  }

  void accumulateTxn(final Txn txn, final boolean isNumerator, final IRatioReporting reporting) {
    if ((reporting == null) || isNumerator) _numerator.accumulateTxn(txn, reporting);
    if ((reporting == null) || !isNumerator) _denominator.accumulateTxn(txn, reporting);
  }

  void endTxnProcessing(final boolean isNumerator, final IRatioReporting reporting) {
    if ((reporting == null) || isNumerator) _numerator.endTxnProcessing();
    if ((reporting == null) || !isNumerator) _denominator.endTxnProcessing();
  }

  public void setNumeratorMatchingLogic(TxnMatchLogic logic) {
    _numerator.setMatchingLogic(logic);
  }
  public TxnMatchLogic getNumeratorMatchingLogic() {
    return _numerator.getMatchingLogic();
  }

  public void setDenominatorMatchingLogic(TxnMatchLogic logic) {
    _denominator.setMatchingLogic(logic);
  }
  public TxnMatchLogic getDenominatorMatchingLogic() {
    return _denominator.getMatchingLogic();
  }
}
