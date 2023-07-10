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

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.AcctFilter;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.CurrencyUtil;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.moneydance.model.Txn;
import com.infinitekind.util.StreamTable;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.AccountFilter;
import com.moneydance.apps.md.view.gui.*;
import com.moneydance.apps.md.view.gui.reporttool.GraphReportUtil;
import com.moneydance.modules.features.ratios.selector.RatioAccountSelector;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * One part of a ratio, either the numerator or the denominator.
 *
 * @author Kevin Menningen
 */
class RatioPart {
  private final List<Account> _requiredAccounts = new ArrayList<Account>();
  private final List<Account> _disallowedAccounts = new ArrayList<Account>();
  private final List<String> _tags = new ArrayList<String>();
  private String _encodedRequiredAccounts;
  private String _encodedDisallowedAccounts;
  private TagLogic _tagLogic;
  private String _label;
  private long _txnValue;
  private TxnDateSearch _dateFilter;
  private AcctFilter _requiredFilter;
  private AcctFilter _disallowedFilter;
  private TxnTagsFilter _tagFilter;
  private double _value;
  private TxnMatchLogic _txnMatchLogic = TxnMatchLogic.DEFAULT;
  private CurrencyType _baseCurrency;

  RatioPart() {
    _label = N12ERatios.EMPTY;
  }

  void loadFromSettings(final StreamTable settings, final MoneydanceGUI mdGui, final Map<Integer, String> tagMap,
                        final String txnMatchKey, final String labelKey,
                        final String requiredListKey, final String disallowedListKey,
                        final String tagsKey) {
    _txnMatchLogic = TxnMatchLogic.fromString(settings.getStr(txnMatchKey, TxnMatchLogic.DEFAULT.getConfigKey()));
    _label = settings.getStr(labelKey, N12ERatios.EMPTY);
    _encodedRequiredAccounts = settings.getStr(requiredListKey, N12ERatios.EMPTY);
    buildAccountList(mdGui, _encodedRequiredAccounts, _requiredAccounts);
    _encodedDisallowedAccounts = settings.getStr(disallowedListKey, N12ERatios.EMPTY);
    buildAccountList(mdGui, _encodedDisallowedAccounts, _disallowedAccounts);
    loadTags(settings.getStr(tagsKey, N12ERatios.EMPTY), tagMap);
  }

  void saveToSettings(final StreamTable settings,
                      final String txnMatchKey, final String labelKey,
                      final String requiredListKey, final String disallowedListKey,
                      final String tagsKey) {
    settings.put(txnMatchKey, _txnMatchLogic.getConfigKey());
    settings.put(labelKey, _label);
    settings.put(requiredListKey, _encodedRequiredAccounts);
    settings.put(disallowedListKey, _encodedDisallowedAccounts);
    settings.put(tagsKey, saveTags());
  }

  void setValue(double value) { _value = value; }
  double getValue() { return _value; }

  void setTxnMatchBoth() { _txnMatchLogic = TxnMatchLogic.BOTH; }
  boolean getTxnMatchBoth() { return TxnMatchLogic.BOTH.equals(_txnMatchLogic); }
  void setTxnMatchInto() { _txnMatchLogic = TxnMatchLogic.IN; }
  boolean getTxnMatchInto() { return TxnMatchLogic.IN.equals(_txnMatchLogic); }
  void setTxnMatchOutOf() { _txnMatchLogic = TxnMatchLogic.OUT; }
  boolean getTxnMatchOutOf() { return TxnMatchLogic.OUT.equals(_txnMatchLogic); }
  void setEndBalanceOnly() { _txnMatchLogic = TxnMatchLogic.END_BALANCE; }
  boolean getEndBalanceOnly() { return TxnMatchLogic.END_BALANCE.equals(_txnMatchLogic); }
  void setAverageBalance() { _txnMatchLogic = TxnMatchLogic.AVERAGE_BALANCE; }
  boolean getAverageBalance() { return TxnMatchLogic.AVERAGE_BALANCE.equals(_txnMatchLogic); }
  void setBeginningBalance() { _txnMatchLogic = TxnMatchLogic.BEGIN_BALANCE; }
  boolean getBeginningBalance() { return TxnMatchLogic.BEGIN_BALANCE.equals(_txnMatchLogic); }
  void setConstant() { _txnMatchLogic = TxnMatchLogic.CONSTANT; }
  boolean getConstant() { return TxnMatchLogic.CONSTANT.equals(_txnMatchLogic); }
  void setDaysInPeriod() { _txnMatchLogic = TxnMatchLogic.DAYS_IN_PERIOD; }
  boolean getDaysInPeriod() { return TxnMatchLogic.DAYS_IN_PERIOD.equals(_txnMatchLogic); }

  void setMatchingLogic(TxnMatchLogic logic) { _txnMatchLogic = logic; }
  TxnMatchLogic getMatchingLogic() { return _txnMatchLogic; }

  String getLabel() { return _label; }
  void setLabel(final String label) { _label = label; }

  void setRequiredAccounts(AccountFilter accountFilter, final AccountBook root) {
    _requiredAccounts.clear();
    _requiredAccounts.addAll(accountFilter.buildIncludedAccountList(root));
    _encodedRequiredAccounts = GraphReportUtil.encodeAcctList(accountFilter);
  }
  void setEncodedRequiredAccounts(final String encodedAccounts) { _encodedRequiredAccounts = encodedAccounts; }
  String getEncodedRequiredAccounts() { return _encodedRequiredAccounts; }
  List<Account> getRequiredAccountList() { return _requiredAccounts; }
  void setDisallowedAccounts(AccountFilter accountFilter, final AccountBook root) {
    _disallowedAccounts.clear();
    _disallowedAccounts.addAll(accountFilter.buildIncludedAccountList(root));
    _encodedDisallowedAccounts = GraphReportUtil.encodeAcctList(accountFilter);
  }
  void setEncodedDisallowedAccounts(final String encodedAccounts) { _encodedDisallowedAccounts = encodedAccounts; }
  String getEncodedDisallowedAccounts() { return _encodedDisallowedAccounts; }
  List<Account> getDisallowedAccountList() { return _disallowedAccounts; }

  void setTags(final List<String> tagList) {
    _tags.clear();
    if ((tagList != null) && !tagList.isEmpty()) _tags.addAll(tagList);
  }
  List<String> getTags() { return _tags; }
  void setTagLogic(final TagLogic tagLogic) { _tagLogic = tagLogic; }
  TagLogic getTagLogic() { return _tagLogic; }

  public boolean equals(Object object) {
    if (object == this) return true;
    if (!(object instanceof RatioPart)) return false;
    RatioPart other = (RatioPart)object;
    if (!_txnMatchLogic.equals(other._txnMatchLogic)) return false;
    if (!RatiosUtil.areEqual(_label, other._label)) return false;
    if (!RatiosUtil.areEqual(_encodedRequiredAccounts, other._encodedRequiredAccounts)) return false;
    if (!RatiosUtil.areEqual(_tags, other._tags)) return false;
    return RatiosUtil.areEqual(_tagLogic, other._tagLogic);
  }

  public int hashCode() {
    int hash = 19;
    hash = 23*hash + _txnMatchLogic.hashCode();
    if (_label != null) {
      hash = 23*hash + _label.hashCode();
    }
    if (_encodedRequiredAccounts != null) {
      hash = 23*hash + _encodedRequiredAccounts.hashCode();
    }
    if (_tags != null) {
      hash = 23*hash + _tags.hashCode();
    }
    if (_tagLogic != null) {
      hash = 23*hash + _tagLogic.hashCode();
    }
    return hash;
  }

  private void loadTags(final String settings, Map<Integer, String> tagMap) {
    if (StringUtils.isBlank(settings)) return;
    int delim = settings.lastIndexOf('+');
    TagLogic tagLogic = TagLogic.OR;
    String tagStr = settings;
    if (delim >= 0) {
      String logic = settings.substring(delim + 1);
      tagLogic = TagLogic.fromString(logic);
      tagStr = settings.substring(0, delim);
    }
    setTags(TxnTagUtils.convertTags(tagStr, tagMap));
    setTagLogic(tagLogic);
  }

  private String saveTags() {
    if (_tags.isEmpty()) return N12ERatios.EMPTY;
    return RatiosUtil.toCSV(_tags) + '+' + _tagLogic.getConfigKey();
  }


  /**
   * Create a list of accounts from an encoded account list string. The saved account IDs may or may not exist.
   *
   * @param mdGui             The main user interface object.
   * @param encodedAccountIDs The encoded string containing account IDs and account types.
   * @param accounts          An [in,out] list to receive the list of accounts as a result.
   */
  private static void buildAccountList(MoneydanceGUI mdGui, final String encodedAccountIDs, List<Account> accounts) {
    // start with nothing
    accounts.clear();
    // use an account selector so as to not duplicate code
    final AccountBook root = mdGui.getCurrentBook();
    RatioAccountSelector selector = RatioEntryEditorView.createAccountSelector(root);
    AccountFilter accountFilter = selector.selectFromEncodedString(encodedAccountIDs);
    accounts.addAll(accountFilter.buildIncludedAccountList(root));
  }

  void prepareForTxnProcessing(final AccountBook root, final DateRange dateRange, final boolean useTaxDate) {
    if (isAccountBalanceType()) return; // nothing to do
    _baseCurrency = root.getCurrencies().getBaseType();
    _txnValue = 0;
    _dateFilter = new TxnDateSearch(dateRange.getStartDateInt(), dateRange.getEndDateInt(), useTaxDate);
    DefaultAcctSearch reqFilter = new DefaultAcctSearch();
    for(Account requiredAccount : _requiredAccounts) {
      reqFilter.setShowAccount(requiredAccount, true);
    }
    _requiredFilter = reqFilter;
    
    DefaultAcctSearch disFilter = new DefaultAcctSearch();
    for(Account disallowedAccount : _disallowedAccounts) {
      disFilter.setShowAccount(disallowedAccount, true);
    }
    _disallowedFilter = disFilter;
    
    if (!_tags.isEmpty()) {
      _tagFilter = new TxnTagsFilter(_tags, _tagLogic);
    } else {
      _tagFilter = null;
    }
  }

  /**
   * The key algorithm for transaction-based computations. This method selects which transactions are
   * included or not, and the sign of the value.
   * 
   * @param txn The transaction to test for inclusion in the numerator or denominator.
   * @param reporting The reporting callback interface to add the transaction to.
   */
  void accumulateTxn(final Txn txn, final IRatioReporting reporting) {
    if (isAccountBalanceType()) return; // nothing to do
    if (!_dateFilter.matches(txn)) return; // does not match the date range
    // There is an assumption here that an account can't be simultaneously required and disallowed.
    final Account sourceAccount = txn.getAccount();
    final Account targetAccount = txn.getOtherTxn(0).getAccount();
    // If a disallowed account is on either side, then the txn is disqualified.
    if (_disallowedFilter.matches(sourceAccount) || _disallowedFilter.matches(targetAccount)) {
      // do nothing, can't use this transaction
      return;
    }
    // we do not allow security accounts either
    if ((sourceAccount.getAccountType() == Account.AccountType.SECURITY)
        || (targetAccount.getAccountType() == Account.AccountType.SECURITY)) {
      // do nothing, can't use this transaction
      return;
    }
    final boolean sourceRequired = _requiredFilter.matches(sourceAccount);
    final boolean targetRequired = _requiredFilter.matches(targetAccount);
    // if neither match, both accounts are Allowed and we ignore the transaction
    // if both match, both accounts are Required and it's an 'internal' transfer, skip
    if (sourceRequired == targetRequired) return;
    // At this point one account is Required, the other is Allowed
    // Both sides will be visited by the enumeration, we just so happen to pick the target account
    // to get the sign right.
    if (targetRequired && txnDirectionMatches(txn, targetAccount.balanceIsNegated())) {
      // we have a candidate transaction, now check both sides for a tag match if applicable
      if ((_tagFilter != null) && !_tagFilter.matches(txn)) return;
      // we have a matching transaction
      final int txnDate = txn.getDateInt();
      final long rawValue = txn.getValue();
      // transactions are specified in the currency of the source account, not the target account
      final long txnValue = sourceAccount.getCurrencyType().adjustValueForSplitsInt(txnDate, rawValue);
      // convert to the base currency for all calculations
      final long convertedValue;
      // we will flip the transaction if the category is the source and the non-category is the
      // destination
      if (RatioCompute.shouldFlipTxn(sourceAccount, targetAccount, sourceRequired, targetRequired)) {
        convertedValue = -CurrencyUtil.convertValue(txnValue, sourceAccount.getCurrencyType(),
                                                    _baseCurrency, txnDate);
      } else {
        convertedValue = CurrencyUtil.convertValue(txnValue, sourceAccount.getCurrencyType(),
                                                    _baseCurrency, txnDate);
      }
      _txnValue += convertedValue;
      if (reporting != null) {
        reporting.addTxn(txn, new TxnReportInfo(convertedValue, sourceRequired, targetRequired));
      }
    }
  }

  private boolean isAccountBalanceType() {
    return RatiosUtil.isAccountBalanceType(_txnMatchLogic);
  }

  void endTxnProcessing() {
    if (isAccountBalanceType()) return; // nothing to do
    // convert to the base currency value as a double
    setValue(_baseCurrency.getDoubleValue(_txnValue));
  }

  /**
   * Determine if the given transaction matches the criteria for the direction of the cash flow.
   * @param txn The transaction to test.
   * @param isNegated True if the balances of the account are negated, essentially if it is an Income account.
   * @return True if the transaction matches the match criterion, false if it is zero value or doesn't match.
   */
  private boolean txnDirectionMatches(final Txn txn, final boolean isNegated) {
    if (getTxnMatchBoth()) return true; // either direction is fine
    final long value = txn.getValue();
    if (isNegated) {
      if (getTxnMatchInto() && (value > 0)) return true;
      if (getTxnMatchOutOf() && (value < 0)) return true;
      return false;
    }
    // since we've chosen the other side, we expect transfers to be negative
    // if they go into the selected account. For example a transfer out of savings
    // and into Groceries expense account will be negative.
    if (getTxnMatchInto() && (value < 0)) return true;
    if (getTxnMatchOutOf() && (value > 0)) return true;
    return false;
  }

}
