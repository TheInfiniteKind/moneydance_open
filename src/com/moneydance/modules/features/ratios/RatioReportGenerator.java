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
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.CurrencyUtil;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.moneydance.model.ParentTxn;
import com.infinitekind.moneydance.model.ReportSpec;
import com.infinitekind.moneydance.model.SplitTxn;
import com.infinitekind.moneydance.model.Txn;
import com.infinitekind.tiksync.SyncRecord;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.view.gui.reporttool.RecordRow;
import com.moneydance.apps.md.view.gui.reporttool.Report;
import com.moneydance.apps.md.view.gui.reporttool.ReportGenerator;

import javax.swing.JPanel;
import java.awt.FontMetrics;
import java.awt.Graphics2D;
import java.util.List;

/**
 * Build a report showing exactly how the given percentage / ratio was arrived at.
 *
 * @author Kevin Menningen
 */
class RatioReportGenerator extends ReportGenerator {
  private static final int NUM_COLUMNS = 5;
  private final RatiosExtensionModel _mainModel;
  private final RatioEntry _ratio;
  private final Graphics2D _graphics;
  private final RatioCompute _computer;
  private IRatioReporting _reporting;

  public RatioReportGenerator(final RatiosExtensionModel mainModel, final RatioEntry ratio, final Graphics2D graphics) {
    _mainModel = mainModel;
    _ratio = ratio;
    _graphics = graphics;
    setGUI(_mainModel.getGUI());

    // todo - need to set any of these properties?
    ReportSpec reportSpec = new ReportSpec(_mainModel.getRootAccount());
    reportSpec.setMemorized(false);
    setInfo(reportSpec);
    _computer = new RatioCompute(_mainModel.getRootAccount(), _mainModel.getGUI().getPreferences().getDecimalChar());
  }

  public String getName() {
    return getReportName();
  }

  protected JPanel getConfigPanel(final boolean reset) {
    // do nothing - no configuration is available for this report
    return null;
  }

  public void setParameters(SyncRecord syncRecord) {
    // do nothing - we get our own data
  }

  public Object generate() {
    loadSettingsFromPreferences();
    boolean fullName = mdGUI.getPreferences().getBoolSetting(UserPreferences.SHOW_FULL_ACCT_PATH, true);
    Report report = new Report(new String[] { 
        mdGUI.getStr("table_column_account"),
        mdGUI.getStr("table_column_category"),
        mdGUI.getStr("table_column_date"),
        mdGUI.getStr("table_column_description"),
        mdGUI.getStr("table_column_amount"),
    } );
    report.setTitle(getReportName());
    report.setSubTitle(_mainModel.getSettings().getDateRange().format(_dateFormat));

    final FontMetrics fm = _graphics.getFontMetrics();
    int widths[] = new int[NUM_COLUMNS];
    for (int column = 0; column < NUM_COLUMNS; column++) {
      widths[column] = measureStringWidth(report.getColumnName(column), _graphics, fm);
    }
    final DateRange dateRange = _mainModel.getSettings().getDateRange();
    final CurrencyType baseCurrency = book.getCurrencies().getBaseType();
    _reporting = new RatioReportingHandler(this, report, fullName, baseCurrency, widths);
    final String nanString = _mainModel.getResources().getString(L10NRatios.NAN);

    // numerator
    report.addRow(RecordRow.BLANK_ROW);
    addTitleRow(report, L10NRatios.NUMERATOR, _ratio.getNumeratorLabel());
    if (_ratio.isNumeratorAccountBalances()) {
      addSubtitleRow(report, mdGUI.getStr("accounts"));
      boolean useDailyAverage = _ratio.getNumeratorAverageBalance();
      boolean useStartBalance = _ratio.getNumeratorBeginningBalance();
      addBalanceRows(baseCurrency, _ratio.getNumeratorRequiredAccountList(), dateRange, useDailyAverage, useStartBalance, true);
    } else if (_ratio.isNumeratorConstant()) {
      addConstantRow(report, _ratio.getNumeratorConstant(), _ratio.getNumeratorLabel(), 0.0, _ratio.getNumeratorDaysInPeriod(), dateRange, widths);
    } else {
      addSubtitleRow(report, mdGUI.getStr("report_transactions"));
      addTransactionRows(dateRange, true);
    }
    addSubtotalRow(report, L10NRatios.NUMERATOR, _ratio.getNumeratorLabel(), baseCurrency, _ratio.getNumeratorValue(),
                   _ratio.isNumeratorConstant(), nanString, fm, widths);

    // denominator
    report.addRow(RecordRow.BLANK_ROW);
    addTitleRow(report, L10NRatios.DENOMINATOR, _ratio.getDenominatorLabel());
    if (_ratio.isDenominatorAccountBalances()) {
      addSubtitleRow(report, mdGUI.getStr("accounts"));
      boolean useDailyAverage = _ratio.getDenominatorAverageBalance();
      boolean useStartBalance = _ratio.getDenominatorBeginningBalance();
      addBalanceRows(baseCurrency, _ratio.getDenominatorRequiredAccountList(), dateRange, useDailyAverage, useStartBalance, false);
    } else if (_ratio.isDenominatorConstant()) {
      addConstantRow(report,_ratio.getDenominatorConstant(), _ratio.getDenominatorLabel(), 1.0, _ratio.getDenominatorDaysInPeriod(), dateRange, widths);
    } else {
      addSubtitleRow(report, mdGUI.getStr("report_transactions"));
      addTransactionRows(dateRange, false);
    }
    addSubtotalRow(report, L10NRatios.DENOMINATOR, _ratio.getDenominatorLabel(), baseCurrency, _ratio.getDenominatorValue(),
                   _ratio.isDenominatorConstant(), nanString, fm, widths);

    // final result
    RatioCompute.computeFinalRatio(_ratio);
    report.addRow(RecordRow.BLANK_ROW);
    addResultRow(report, baseCurrency, nanString, fm, widths);

    final String notes = _ratio.getNotes();
    if (!StringUtils.isBlank(notes)) {
      report.addRow(RecordRow.BLANK_ROW);
      report.addRow(RecordRow.BLANK_ROW);
      addNotes(report, notes, widths);
    }
    adjustColumnWeights(widths); // give the widest column extra space
    for (int column = 0; column < NUM_COLUMNS; column++) report.setColumnWeight(column, widths[column]);
    return report;
  }

  private void addConstantRow(Report report, boolean isConstant, String constant, double defaultConstant, boolean isDaysInPeriod, DateRange dateRange, int[] widths) {
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);
    FontMetrics fontMetrics = _graphics.getFontMetrics();

    // Account
    labels[0] = _mainModel.getResources().getString(isConstant ? L10NRatios.CONSTANT : L10NRatios.DAYS_IN_PERIOD);
    widths[0] = Math.max(widths[0], measureStringWidth(labels[0], _graphics, fontMetrics));
    style[0] = RecordRow.STYLE_PLAIN;
    align[0] = RecordRow.ALIGN_LEFT;

    // Category
    labels[1] = " ";

    // Date
    labels[2] = " ";

    // Description
    final boolean allowZero = defaultConstant == 0.0;
    boolean isError = false;
    if (isDaysInPeriod) {
      labels[3] = dateRange.format(_dateFormat);
      widths[3] = Math.max(widths[3], measureStringWidth(labels[3], _graphics, fontMetrics));
    } else {
      isError = RatiosUtil.getConstantError(constant, dec, allowZero);
      final String display;
      if (isError) {
        display = RatiosUtil.getLabelText(_mainModel.getResources(), L10NRatios.INVALID_CONSTANT) + ' ' + constant;
      } else {
        display = N12ERatios.EMPTY;
      }
      labels[3] = display;
    }
    style[3] = RecordRow.STYLE_PLAIN;
    align[3] = RecordRow.ALIGN_LEFT;

    // Amount - ending balance
    final double value;
    if (isConstant) {
      value = isError ? defaultConstant : RatiosUtil.getConstantValue(constant, dec, allowZero, defaultConstant);
    } else {
      value = RatioCompute.getDaysInPeriod(dateRange);
    }
    labels[4] = StringUtils.formatRate(value, dec);
    widths[4] = Math.max(widths[4], measureStringWidth(labels[4], _graphics, fontMetrics));
    style[4] = RecordRow.STYLE_PLAIN;
    align[4] = RecordRow.ALIGN_RIGHT;
    color[4] = (value < 0.0) ? RecordRow.COLOR_RED : RecordRow.COLOR_BLACK;

    report.addRow(row);
  }

  private void addSubtotalRow(Report report, String typeKey, String userLabel, CurrencyType baseCurrency, double value, boolean isConstant,
                              String nanString, FontMetrics fontMetrics, int[] widths) {
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);

    // Account
    StringBuilder sb = new StringBuilder(mdGUI.getStr(L10NRatios.REPORT_TOTAL));
    sb.append(" - ");
    sb.append(_mainModel.getResources().getString(typeKey));
    labels[0] = sb.toString();
    widths[0] = Math.max(widths[0], measureStringWidth(labels[0], _graphics, fontMetrics));
    style[0] = RecordRow.STYLE_BOLD;
    align[0] = RecordRow.ALIGN_LEFT;
    totals[0] = RecordRow.TOTAL_SUBTOTAL;

    // Category
    labels[1] = " ";
    totals[1] = RecordRow.TOTAL_SUBTOTAL;

    // Date
    labels[2] = " ";
    totals[2] = RecordRow.TOTAL_SUBTOTAL;

    // Description
    labels[3] = userLabel;
    widths[3] = Math.max(widths[3], measureStringWidth(labels[3], _graphics, fontMetrics));
    style[3] = RecordRow.STYLE_BOLD;
    align[3] = RecordRow.ALIGN_LEFT;
    totals[3] = RecordRow.TOTAL_SUBTOTAL;

    // Amount
    labels[4] = formatRatioPartValue(baseCurrency, value, dec, nanString, isConstant);
    widths[4] = Math.max(widths[4], measureStringWidth(labels[4], _graphics, fontMetrics));
    style[4] = RecordRow.STYLE_BOLD;
    align[4] = RecordRow.ALIGN_RIGHT;
    color[4] = (value < 0) ? RecordRow.COLOR_RED : RecordRow.COLOR_BLACK;
    totals[4] = RecordRow.TOTAL_SUBTOTAL;

    report.addRow(row);
  }

  private void addNotes(Report report, String notes, int[] widths) {
    // find the widest column and use that one
    int columnIndex = -1;
    int maxWidth = -1;
    for (int index = 0; index < NUM_COLUMNS; index++) {
      if (widths[index] > maxWidth) {
        maxWidth = widths[index];
        columnIndex = index;
      }
    }

    String[] noteLines = notes.split(N12ERatios.LINEEND_REGEX);
    for (String noteLine : noteLines) {
      final String[] labels = new String[NUM_COLUMNS];
      final byte[] align = new byte[NUM_COLUMNS];
      final byte[] color = new byte[NUM_COLUMNS];
      final byte[] style = new byte[NUM_COLUMNS];
      final byte[] totals = new byte[NUM_COLUMNS];
      labels[columnIndex] = noteLine;
      style[columnIndex] = RecordRow.STYLE_PLAIN;
      align[columnIndex] = RecordRow.ALIGN_LEFT;
      report.addRow(new RecordRow(labels, align, color, style, totals));
    }
  }

  private void addResultRow(final Report report, final CurrencyType baseCurrency, final String nanString,
                            final FontMetrics fontMetrics, final int[] widths) {
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);

    // Account
    String ratioLabel = _mainModel.getResources().getString(L10NRatios.REPORT_LABEL).toUpperCase();
    labels[0] = ratioLabel;
    widths[0] = Math.max(widths[0], measureStringWidth(labels[0], _graphics, fontMetrics));
    style[0] = RecordRow.STYLE_BOLD;
    align[0] = RecordRow.ALIGN_LEFT;
    totals[0] = RecordRow.TOTAL_GRANDTOTAL;

    // Category
    labels[1] = " ";
    totals[1] = RecordRow.TOTAL_GRANDTOTAL;
    
    // Date
    labels[2] = " ";
    totals[2] = RecordRow.TOTAL_GRANDTOTAL;

    // Description
    StringBuilder sb = new StringBuilder();
    sb.append(formatRatioPartValue(baseCurrency, _ratio.getNumeratorValue(), dec, nanString, _ratio.isNumeratorConstant()));
    sb.append(" / ");
    sb.append(formatRatioPartValue(baseCurrency, _ratio.getDenominatorValue(), dec, nanString, _ratio.isDenominatorConstant()));
    labels[3] = sb.toString();
    widths[3] = Math.max(widths[3], measureStringWidth(labels[3], _graphics, fontMetrics));
    style[3] = RecordRow.STYLE_BOLD;
    align[3] = RecordRow.ALIGN_LEFT;
    totals[3] = RecordRow.TOTAL_GRANDTOTAL;

    // Amount
    final double value = _ratio.getValue();
    labels[4] = RatiosUtil.formatRatioValue(value, dec, _mainModel.getDecimalPlaces(), nanString, _ratio.getShowPercent());
    widths[4] = Math.max(widths[4], measureStringWidth(labels[4], _graphics, fontMetrics));
    style[4] = RecordRow.STYLE_BOLD;
    align[4] = RecordRow.ALIGN_RIGHT;
    color[4] = (!Double.isNaN(value) && !Double.isInfinite(value) && (value < 0)) ? RecordRow.COLOR_RED : RecordRow.COLOR_BLACK;
    totals[4] = RecordRow.TOTAL_GRANDTOTAL;

    report.addRow(row);
  }

  private String formatRatioPartValue(CurrencyType baseCurrency, final double value, final char decimal, final String nanString, boolean isConstant) {
    if (Double.isInfinite(value) || Double.isNaN(value)) return nanString;
    if (isConstant) return StringUtils.formatRate(value, decimal);
    return baseCurrency.formatFancy(baseCurrency.getLongValue(value), decimal);
  }

  private void addTransactionRows(final DateRange dateRange, final boolean isNumerator) {
    _reporting.startReportSection();
    // the result will be set to either the numerator or the denominator value automatically
    _computer.computeTransactionResult(_ratio, dateRange, isNumerator, _reporting);
    _reporting.endReportTxnSection();
  }

  private void addBalanceRows(final CurrencyType baseCurrency, final List<Account> accountList, final DateRange dateRange,
                              final boolean useDailyAverage, final boolean useStartBalance,
                              final boolean isNumerator) {
    _reporting.startReportSection();
    // For now we compute both starting and ending balance, and just use the end balance, later we may use both
    // of them as a different mode. This does not appreciably slow down the calculation.
    final long result = _computer.computeBalanceResult(dateRange, baseCurrency, accountList, useDailyAverage, useStartBalance, _reporting);
    if (isNumerator) {
      _ratio.setNumeratorValue(baseCurrency.getDoubleValue(result));
    } else {
      _ratio.setDenominatorValue(baseCurrency.getDoubleValue(result));
    }
    _reporting.endReportAccountSection();
  }

  private void addSubtitleRow(Report rpt, String subtitle) {
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);

    labels[0] = subtitle;
    align[0] = RecordRow.ALIGN_LEFT;

    for (int index = 1; index < NUM_COLUMNS; index++) {
      align[index] = RecordRow.ALIGN_RIGHT;
    }
    rpt.addRow(row);
  }

  private void addTitleRow(Report rpt, String titleKey, String extraInfo) {
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);

    StringBuilder sb = new StringBuilder(_mainModel.getResources().getString(titleKey));
    if (!StringUtils.isBlank(extraInfo)) {
      sb.append(" - ");
      sb.append(extraInfo);
    }
    labels[0] = sb.toString();
    style[0] = RecordRow.STYLE_BOLD;
    align[0] = RecordRow.ALIGN_LEFT;

    for (int index = 1; index < NUM_COLUMNS; index++) {
      style[index] = RecordRow.STYLE_BOLD;
      align[index] = RecordRow.ALIGN_RIGHT;
    }
    rpt.addRow(row);
  }

  void addAccountTypeRow(Report rpt, Account.AccountType accountType, boolean isAverageBalance, boolean isStartBalance, boolean showAmountTitle) {
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);

    labels[0] = RatiosUtil.getAccountTypeNameAllCaps(mdGUI, accountType.code());
    if (showAmountTitle && isAverageBalance) {
      labels[4] = _mainModel.getResources().getString(L10NRatios.AVERAGE_BALANCE);
    } else if (showAmountTitle) {
      labels[4] = isStartBalance ?
                  _mainModel.getResources().getString(L10NRatios.START_BALANCE) :
                  _mainModel.getResources().getString(L10NRatios.END_BALANCE);
    }
    style[0] = RecordRow.STYLE_PLAIN;
    align[0] = RecordRow.ALIGN_LEFT;
    for (int index = 1; index < NUM_COLUMNS; index++) {
      style[index] = RecordRow.STYLE_PLAIN;
      align[index] = RecordRow.ALIGN_RIGHT;
    }
    rpt.addRow(RecordRow.BLANK_ROW);
    rpt.addRow(row);
  }

  void addAccountTypeSubtotalRow(Report report, Account.AccountType accountType, CurrencyType baseCurrency, long subtotal,
                                 boolean isAverageBalance, int endingDate) {
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);

    // Account
    StringBuilder sb = new StringBuilder(mdGUI.getStr(L10NRatios.REPORT_TOTAL));
    sb.append(" - ");
    sb.append(RatiosUtil.getAccountTypeNameAllCaps(mdGUI, accountType.code()));
    labels[0] = sb.toString();
    style[0] = RecordRow.STYLE_PLAIN;
    align[0] = RecordRow.ALIGN_LEFT;
    totals[0] = RecordRow.TOTAL_SUBTOTAL;

    // Category
    labels[1] = " ";
    totals[1] = RecordRow.TOTAL_SUBTOTAL;

    // Date
    labels[2] = (isAverageBalance || (endingDate == 0)) ? " " : _dateFormat.format(endingDate);
    totals[2] = RecordRow.TOTAL_SUBTOTAL;

    // Description
    labels[3] = " ";
    style[3] = RecordRow.STYLE_PLAIN;
    align[3] = RecordRow.ALIGN_LEFT;
    totals[3] = RecordRow.TOTAL_SUBTOTAL;

    // Amount
    labels[4] = baseCurrency.formatFancy(subtotal, dec);
    style[4] = RecordRow.STYLE_PLAIN;
    align[4] = RecordRow.ALIGN_RIGHT;
    color[4] = (subtotal < 0) ? RecordRow.COLOR_RED : RecordRow.COLOR_BLACK;
    totals[4] = RecordRow.TOTAL_SUBTOTAL;

    report.addRow(row);
  }

  RecordRow createAccountReportRow(BalanceHolder accountResult, boolean showFullAccountName,
                                   CurrencyType baseCurrency, int[] widths) {
    final long accountBalance =
      accountResult.isAverageBalanceComputed() ?
        accountResult.getAverageBalance() :
      (accountResult.isStartBalanceUsed() ? accountResult.getStartBalance() : accountResult.getEndBalance());

    // do not show zero balance accounts - currently only checking the end balance since that is all we use
    if (accountBalance == 0) return null;

    final Account account = accountResult.getAccount();
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);
    FontMetrics fontMetrics = _graphics.getFontMetrics();
    // Account
    if ((account.getAccountType() != Account.AccountType.INCOME) &&
        (account.getAccountType() != Account.AccountType.EXPENSE)) {
      labels[0] = showFullAccountName ? account.getFullAccountName() : account.getAccountName();
      widths[0] = Math.max(widths[0], measureStringWidth(labels[0], _graphics, fontMetrics));
      style[0] = RecordRow.STYLE_PLAIN;
      align[0] = RecordRow.ALIGN_LEFT;
    } else {
      // Category
      labels[1] = showFullAccountName ? account.getFullAccountName() : account.getAccountName();
      widths[1] = Math.max(widths[1], measureStringWidth(labels[1], _graphics, fontMetrics));
      style[1] = RecordRow.STYLE_PLAIN;
      align[1] = RecordRow.ALIGN_LEFT;
    }

    // Date
    // Description - put in the balance in the account's currency, if different
    //               Another possible use of description would be if you used balance difference, you could show the end balance
    //               and the start balance.
    if (!baseCurrency.equals(account.getCurrencyType())) {
      CurrencyType accountCurrency = account.getCurrencyType();
      long displayBalance = CurrencyUtil.convertValue(accountBalance,
                                                      baseCurrency, accountCurrency,
                                                      accountResult.getEndDate());
      labels[3] = accountCurrency.formatFancy(displayBalance, dec);
      widths[3] = Math.max(widths[3], measureStringWidth(labels[3], _graphics, fontMetrics));
    } else {
      labels[3] = N12ERatios.EMPTY;
    }
    style[3] = RecordRow.STYLE_PLAIN;
    align[3] = RecordRow.ALIGN_LEFT;

    // Amount - ending balance
    labels[4] = baseCurrency.formatFancy(accountBalance, dec);
    widths[4] = Math.max(widths[4], measureStringWidth(labels[4], _graphics, fontMetrics));
    style[4] = RecordRow.STYLE_PLAIN;
    align[4] = RecordRow.ALIGN_RIGHT;
    color[4] = (accountBalance < 0) ? RecordRow.COLOR_RED : RecordRow.COLOR_BLACK;

    return row;
  } // createAccountReportRow()

  RecordRow createTxnReportRow(Txn txn, TxnReportInfo info, boolean showFullAccountName,
                               CurrencyType baseCurrency, int[] widths) {
    Account account = txn.getAccount();
    Account category = txn.getOtherTxn(0).getAccount();
    // Should we flip? we keep categories on the right side (column 2). We don't need to
    // negate the value because the algorithm in RatioPart.accumulateTxn() has already
    // done so.
    if (RatioCompute.shouldFlipTxn(account, category, info.isSourceRequired, info.isTargetRequired)) {
      Account temp = account;
      account = category;
      category = temp;
    }
    final String[] labels = new String[NUM_COLUMNS];
    final byte[] align = new byte[NUM_COLUMNS];
    final byte[] color = new byte[NUM_COLUMNS];
    final byte[] style = new byte[NUM_COLUMNS];
    final byte[] totals = new byte[NUM_COLUMNS];
    RecordRow row = new RecordRow(labels, align, color, style, totals);
    FontMetrics fontMetrics = _graphics.getFontMetrics();

    // Account
    labels[0] = showFullAccountName ? account.getFullAccountName() : account.getAccountName();
    widths[0] = Math.max(widths[0], measureStringWidth(labels[0], _graphics, fontMetrics));
    style[0] = RecordRow.STYLE_PLAIN;
    align[0] = RecordRow.ALIGN_LEFT;

    // Category
    labels[1] = showFullAccountName ? category.getFullAccountName() : category.getAccountName();
    widths[1] = Math.max(widths[1], measureStringWidth(labels[1], _graphics, fontMetrics));
    style[1] = RecordRow.STYLE_PLAIN;
    align[1] = RecordRow.ALIGN_LEFT;

    // Date
    labels[2] = _dateFormat.format(txn.getDateInt());
    widths[2] = Math.max(widths[2], measureStringWidth(labels[2], _graphics, fontMetrics));
    style[2] = RecordRow.STYLE_PLAIN;
    align[2] = RecordRow.ALIGN_LEFT;

    // Description
    labels[3] = getTxnDescription(txn);
    widths[3] = Math.max(widths[3], measureStringWidth(labels[3], _graphics, fontMetrics));
    style[3] = RecordRow.STYLE_PLAIN;
    align[3] = RecordRow.ALIGN_LEFT;

    // Amount
    final long result = info.convertedValue;
    labels[4] = baseCurrency.formatFancy(result, dec);
    widths[4] = Math.max(widths[4], measureStringWidth(labels[4], _graphics, fontMetrics));
    style[4] = RecordRow.STYLE_PLAIN;
    align[4] = RecordRow.ALIGN_RIGHT;
    color[4] = (result < 0) ? RecordRow.COLOR_RED : RecordRow.COLOR_BLACK;

    return row;
  }

  private String getTxnDescription(final Txn txn) {
    if (txn instanceof ParentTxn) return txn.getDescription();
    if (!(txn instanceof SplitTxn)) return txn.getDescription();
    final SplitTxn split = (SplitTxn)txn;
    final ParentTxn ptxn = split.getParentTxn();
    if (StringUtils.isBlank(split.getDescription())) {
      if (StringUtils.isBlank(ptxn.getDescription())) {
        return "";
      } else {
        return "["+ptxn.getDescription()+"]";
      }
    }
    return split.getDescription();
  }

  boolean getUseTaxDate() {
    return _ratio.getUseTaxDate();
  }

  private String getReportName() {
    final String itemName = _ratio.getName();
    if (StringUtils.isBlank(itemName)) {
      return _mainModel.getResources().getString(L10NRatios.REPORT_TITLE);
    }
    return RatiosUtil.getLabelText(_mainModel.getResources(), L10NRatios.REPORT_TITLE) + itemName;
  }

  /**
   * When expanding the report, the system adds equal space to each column. So by adding an additional
   * 1/2 report width to the widest column, we effectively weight that column more and trick the system
   * into expanding that column more than the others.
   * @param widths The measured weights after adding all the rows.
   */
  private static void adjustColumnWeights(int[] widths) {
    int maxWidthIndex = -1;
    int maxWidth = -1;
    int sum = 0;
    for (int index = 0; index < widths.length; index++) {
      if (widths[index] > maxWidth) {
        maxWidth = widths[index];
        maxWidthIndex = index;
      }
      sum += widths[index];
    }
    if (maxWidthIndex < 0) return;
    // now expand the whole report by half, giving the widest column 3/4 of that space and all
    // the other columns 1/4 of the space divided evenly (at least 4 pixels ).
    int widthToAdd = sum / 2;
    int largePart = widthToAdd * 3 / 4;
    int smallPart = Math.max(4, (widthToAdd - largePart) / (widths.length - 1));
    for (int index = 0; index < widths.length; index++) {
      if (index == maxWidthIndex) {
        widths[index] += largePart;
      } else {
        widths[index] += smallPart;
      }
    }
  }

  private static int measureStringWidth(String text, Graphics2D graphics, FontMetrics fm) {
    return (int) fm.getStringBounds(text, graphics).getWidth();
  }

}
