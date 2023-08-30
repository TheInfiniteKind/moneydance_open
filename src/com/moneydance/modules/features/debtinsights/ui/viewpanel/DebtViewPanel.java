/*
 * DebtViewPanel.java
 *
 * Created on Sep 9, 2013
 * Last Modified: 30th March 2023
 * Last Modified By: Stuart Beesley
 *
 *
 */

package com.moneydance.modules.features.debtinsights.ui.viewpanel;

import java.awt.Color;
import java.awt.Container;
import java.awt.Font;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.InputEvent;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.util.ArrayList;
import java.util.List;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;

import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.controller.BalanceType;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JLinkListener;
import com.moneydance.modules.features.debtinsights.DebtAmountWrapper;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.ui.MyJLinkLabel;
import com.moneydance.modules.features.debtinsights.ui.acctview.DebtAccountView;
import com.moneydance.modules.features.debtinsights.ui.acctview.HierarchyView;
import com.moneydance.apps.md.view.resources.Resources;



public class DebtViewPanel extends JPanel implements JLinkListener, CurrencyListener, AccountListener, MouseListener {
    public boolean fromHomePageWidget;

    public DebtAccountView acctView;

    protected static final String THREE_SPACE = "   ";
    protected static final String SINGLE_SPACE = " ";

    protected JPanel listPanel;
    protected MyJLinkLabel headerLabel;
    protected MyJLinkLabel footerLabel;
    protected JLabel balTypeLabel;
    protected JLabel totalValLabel;
    private BalanceType balanceType = BalanceType.CURRENT_BALANCE;  // Initial default, gets populated from Preferences...
    protected int currentRow = 0;
    private AccountExpander expander = null;
    protected boolean expanded = true;
    protected char dec;
    public UserPreferences prefs;
    private boolean tooManyAccounts = false;

    private static final String EXPANDED = "/com/moneydance/apps/md/view/gui/glyphs/glyph_triangle_down.png";
    private static final String COLLAPSED = "/com/moneydance/apps/md/view/gui/glyphs/glyph_triangle_right.png";
    protected static final String SELECTOR = "/com/moneydance/apps/md/view/gui/glyphs/selector_sm.png";

//	private static final String EXPANDED = "/com/moneydance/apps/md/view/gui/icons/down_triangle.png";
//	private static final String COLLAPSED = "/com/moneydance/apps/md/view/gui/icons/right_triangle.png";
//	protected static final String SELECTOR = "/com/moneydance/apps/md/view/gui/icons/selector_sm.png";

    public static final Border nameBorder = new EmptyBorder(3, 14, 3, 5);
    public static final Border amountBorder = new EmptyBorder(3, 0, 3, 14);
    public static final Border sharesBorder = new EmptyBorder(3, 3, 3, 3);
    public static final Border expandLinkBorder = new EmptyBorder(3, 6, 3, 0);

    public DebtViewPanel(boolean fromHomePageWidget, DebtAccountView betterAccountView, Account.AccountType... acctTypes) {
        this.acctView = betterAccountView;
        this.fromHomePageWidget = fromHomePageWidget;
        init();
    }

    protected AccountBook getRoot() {
        return this.acctView.getMDGUI().getCurrentBook();
    }

    protected void init() {
        this.prefs = this.acctView.getMDGUI().getPreferences();

        setBalanceType(BalanceType.fromInt(prefs
                .getIntSetting(this.acctView.getBalanceTypePref(), BalanceType.CURRENT_BALANCE.ordinal())));
//                .getIntSetting(this.acctView.getBalanceTypePref(), BalanceType.BALANCE.ordinal())));

        this.expanded = this.prefs.getBoolSetting(this.acctView.getSectionExpandedPref(), true);
        Util.logConsole(true, "///DVP.init() expanded is: " + this.expanded);

        this.dec = this.prefs.getDecimalChar();

        GridBagLayout gridbag = new GridBagLayout();
        setLayout(gridbag);
        setOpaque(false);

        this.listPanel = new JPanel(gridbag);

        add(this.listPanel, GridC.getc().xy(0, 0).wx(1.0F).fillboth());

        add(Box.createVerticalStrut(2), GridC.getc().xy(0, 4).wy(1.0F));

        this.listPanel.setOpaque(false);

    }

    protected void addHeaderRow(JPanel listPanel) {
        this.headerLabel = new MyJLinkLabel(" ", Main.EXTN_CMD, SwingConstants.LEFT);
        this.headerLabel.setDrawUnderline(false);
//        this.headerLabel.addLinkListener(this);   // Can't add this for now as it also activates on the collapse / expand icon...! :-<
        this.headerLabel.addMouseListener(this);
        this.headerLabel.setFont(this.acctView.getMDGUI().getFonts().header);
        this.headerLabel.setForeground(this.acctView.getMDGUI().getColors().secondaryTextFG);
        this.headerLabel.setBorder(nameBorder);

        this.balTypeLabel = new JLabel(" ", SwingConstants.RIGHT);
        this.balTypeLabel.setFont(this.acctView.getMDGUI().getFonts().defaultText);
        this.balTypeLabel.setBorder(amountBorder);
        this.balTypeLabel.setForeground(this.acctView.getMDGUI().getColors().secondaryTextFG);
        this.balTypeLabel.setHorizontalTextPosition(SwingConstants.RIGHT);
        this.balTypeLabel.setIcon(this.acctView.getMDGUI().getImages().getIcon(SELECTOR));
        this.balTypeLabel.addMouseListener(this);

        addLabelsToHeader();
        this.currentRow++;
    }

    protected void addLabelsToHeader() {
        listPanel.add(this.headerLabel, GridC.getc().xy(0, 0).wx(1.0F).fillx().west());
        listPanel.add(this.balTypeLabel, GridC.getc().xy(1, 0));
        this.currentRow++;
    }

    protected void addTotalsRow(JPanel totalPanel, CurrencyType base, DebtAmountWrapper aw) {

        Util.logConsole(true, "Widget: addTotalsRow()");

        Font normal = this.acctView.getMDGUI().getFonts().defaultText;
        Font numbers = this.acctView.getMDGUI().getFonts().mono;

        int fontIncSize = 1;

        Font totalsFont = normal.deriveFont(normal.getStyle(), normal.getSize() + fontIncSize);
        Font numbersTotalFont = numbers.deriveFont(numbers.getStyle(), numbers.getSize() + fontIncSize);

        JLabel totalLabel = new JLabel("", SwingConstants.LEFT);        // HomePageView widget TOTAL row...
        totalLabel.setFont(totalsFont);
        totalLabel.setForeground(this.acctView.getMDGUI().getColors().secondaryTextFG);

        JLabel accountSpecificTypeLabel = getAccountTypeSpecificLabel();

        if (accountSpecificTypeLabel != null) {
            accountSpecificTypeLabel.setFont(numbersTotalFont);
            accountSpecificTypeLabel.setBorder(amountBorder);
            Util.logConsole(true, "** accountSpecificTypeLabel:" + accountSpecificTypeLabel.getText());
        }

        this.totalValLabel = new JLabel(" ", SwingConstants.RIGHT);
        this.totalValLabel.setFont(numbersTotalFont);
        this.totalValLabel.setBorder(amountBorder);

        JLabel[] labels = {totalLabel, accountSpecificTypeLabel, this.totalValLabel};
        for (int i = 0; i < labels.length; i++) {
            if (labels[i] != null) {
                totalPanel.add(labels[i], GridC.getc().xy(i, this.currentRow + 1).wx(1.0F).colspan(2).fillx());
            }

        }
        this.currentRow++;
    }

    protected JLabel getAccountTypeSpecificLabel() {
        return new JLabel(" ", SwingConstants.RIGHT);
    }

    synchronized AccountExpander getExpander() {
        if (this.expander == null) {
            this.expander = new AccountExpander();
        }
        return this.expander;
    }

    public void activate() {
        getRoot().addAccountListener(this);
        CurrencyTable ct = getRoot().getCurrencies();
        if (ct != null) {
            ct.addCurrencyListener(this);
        }
        Main.lastRefreshTriggerWasAccountListener = false;
//        this.acctView.refresh();
         refresh();
    }

    public void deactivate() {
        getRoot().removeAccountListener(this);
        getRoot().getCurrencies().removeCurrencyListener(this);
    }

    public void toggleShowHierarchy(JLabel source) {
        this.acctView.setHierarchyView(this.acctView.getHierarchyView().getNextState());

        switch (this.acctView.getHierarchyView()) {
            case EXPAND_ALL:
                this.acctView.setAcctComparator(null);
                Util.logConsole(true, "toggleShowHierarchy() EXPAND_ALL");
                setAllExpanded(getRoot().getRootAccount(), true);
                break;
            case COLLAPSE_ALL:
                this.acctView.setAcctComparator(null);
                Util.logConsole(true, "toggleShowHierarchy() COLLAPSE_ALL");
                setAllExpanded(getRoot().getRootAccount(), false);
                break;
            case FLATTEN:
                Util.logConsole(true, "toggleShowHierarchy() FLATTEN");
        }
        Main.lastRefreshTriggerWasAccountListener = false;
//        this.acctView.refresh();
         refresh();
    }

//    public void setAllExpanded(Account account, boolean expand) {
    private void setAllExpanded(Account account, boolean expand) {
        if (account.getSubAccountCount() > 0) {
            if (isDebtAccount(account)) {
//                account.setPreference(Main.EXPAND_SUBS_KEY, expand);
                account.setPreference(getSubAcctExpansionKey(), expand);
            }
            for (Account sub : account.getSubAccounts()) {
                setAllExpanded(sub, expand);
            }
        }
    }

    private boolean isDebtAccount(Account acct) {
        switch (acct.getAccountType()) {
            case CREDIT_CARD:
            case LOAN:
                return true;
            default:
                return false;
        }
    }

    public void refresh() {
        Util.logConsole(true, "DVP Widget:refresh() - lastRefreshTriggerWasAccountListener: " + Main.lastRefreshTriggerWasAccountListener);

        boolean fromAccountListener = Main.lastRefreshTriggerWasAccountListener;
        if (fromAccountListener) {
            Util.logConsole(true, "... resetting lastRefreshTriggerWasAccountListener to false...");
            Main.lastRefreshTriggerWasAccountListener = false;
        }
        // todo - do something with lastRefreshTriggerWasAccountModified

        if (this.acctView.getMDGUI().getSuspendRefreshes()){
            Util.logConsole(true, "... ignoring refresh as getSuspendRefreshes() is true...");
            return;
        }

        this.listPanel.removeAll();

        if (getRoot() == null)
            return;

        this.dec = this.acctView.getMDGUI().getMain().getPreferences().getDecimalChar();

        CurrencyType base = getRoot().getCurrencies().getBaseType();
        DebtAmountWrapper amountWrapper = new DebtAmountWrapper();          // Holds the total(s)
        this.currentRow = 0;

        String iconPath = COLLAPSED;
        if (this.expanded) iconPath = EXPANDED;

        addHeaderRow(listPanel);
        this.headerLabel.setIcon(this.acctView.getMDGUI().getImages().getIcon(iconPath));

        this.tooManyAccounts = false;
        Util.logConsole(true, "!! DVP.refresh() - Hierarchy: " + this.acctView.getHierarchyView());
        if (this.acctView.getHierarchyView() == HierarchyView.FLATTEN || this.acctView.getAcctComparator() != null) {
            addAccounts(this.acctView.getAccounts(getRoot().getRootAccount()), amountWrapper);
        } else {
            addAccounts(this.getRoot().getRootAccount(), amountWrapper, true, this.expanded, this.acctView.getAccountTypes());
        }
        addTotalsRow(listPanel, base, amountWrapper);

        if (this.tooManyAccounts) {
            this.listPanel.add(
                    new JLabel(this.acctView.getMDGUI().getStr("too_many_accts_wtype")),
                    GridC.getc().xy(1, this.currentRow++).wx(1.0F).colspan(2).fillboth());
        }

        if (!(amountWrapper.hasValidAccts)) {
            setVisible(false);
        } else {
            setHeaderLabels(base, amountWrapper);
            if (this.expanded)
                addFooterLabels(listPanel);
        }

        Container child = this;
        Container parent = getParent();
        int counter = 0;
        while ((counter++ < 1) && (parent != null)) {
            child = parent;
            parent = child.getParent();
        }
        child.validate();
        repaint();
    }

    protected void addFooterLabels(JPanel footerPanel) {
        String previewTxt = Main.getPreviewBuild() ? "*PREVIEW BUILD* " : "";
        String debugTxt = Main.getDebug() ? "*DEBUG: ON* " : "";
        String enhColors = Main.getWidgetEnhancedColors() && Main.getDebug() ? "*Enh Colors: ON* " : "";
        String lineBreakTxt = Main.getDebug() || Main.getPreviewBuild() ? "<BR>" : "";
        String calcTxt = Main.getWidgetOverridePaymentPlanBalance() ? "*Override MD Pmt Plan calcs to BALANCE: ON* " : "";
        String balanceTxt = (Main.getWidgetCalculationBalanceTypeChoice() == Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN)
                ? (Main.getDebug() ? "* DYNAMIC calcs: ON * " : "")
                : String.format("* Calcs FIXED to: '%s'* ", Main.getMDGUI().getResources().getBalanceType(Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()));

        String baseCurrStr = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType().getIDString();
        String convertToBaseTxt = Main.getDebug() && Main.getWidgetForceValuesBaseCurrency() ? String.format("*Conv values to: %s* ", baseCurrStr) : "";

        Color smallCol = Main.getMDGUI().getColors().tertiaryTextFG;
        String _smallColorHex = String.format("%02x%02x%02x", smallCol.getRed(), smallCol.getGreen(), smallCol.getBlue());
        String bigText = "";
        String smallText = previewTxt + debugTxt + enhColors + lineBreakTxt + calcTxt + balanceTxt + convertToBaseTxt;
        String outputText = String.format("<html>%s<small><font color=#%s>%s</font></small></html>", bigText, _smallColorHex, smallText);

        this.footerLabel = new MyJLinkLabel(outputText, Main.EXTN_CMD, SwingConstants.LEFT);
        this.footerLabel.setDrawUnderline(false);
        this.footerLabel.addLinkListener(this);   // Can't add this for now as it also activates on the collapse / expand icon...! :-<
        //        this.footerLabel.addMouseListener(this);
        //        this.footerLabel.setFont(this.acctView.getMDGUI().getFonts().defaultText);
        //        this.footerLabel.setForeground(this.acctView.getMDGUI().getColors().tertiaryTextFG);
        this.footerLabel.setBorder(nameBorder);
        footerPanel.add(this.footerLabel, GridC.getc().xy(0, this.currentRow + 1).wx(1.0F).colspan(4).fillx());
        this.currentRow++;
    }

    protected void setHeaderLabels(CurrencyType base, DebtAmountWrapper amountWrapper) {
        Util.logConsole(true, "Widget: setHeaderLabels()...");
        setVisible(true);

        this.headerLabel.setText(this.acctView.toString());
        this.balTypeLabel.setText(this.acctView.getMDGUI().getStr(getBalanceType().getResourceKey()));

        if (this.expanded) {
            this.listPanel.add(Box.createVerticalStrut(10), GridC.getc().xy(0, this.currentRow));
        }

        this.totalValLabel.setText(base.formatFancy(amountWrapper.getAmount(), this.dec));
        if (amountWrapper.getAmount() < 0L)
            this.totalValLabel.setForeground(this.acctView.getMDGUI().getColors().negativeBalFG);
        else {
            Color col = Main.getWidgetEnhancedColors() ? Util.getPositiveGreen() : this.acctView.getMDGUI().getColors().positiveBalFG;
            this.totalValLabel.setForeground(col);
        }
    }

    protected void addAcctRow(Account target, String sharesLabel, String balLabel, long amt, long balanceForCreditComponent) {
        String acctLabel = target.getAccountName();
        int indentDepth = target.getDepth();
		StringBuilder sb = new StringBuilder();
		for (int i = 1; i < indentDepth; ++i)
			sb.append(THREE_SPACE);
        sb.append(acctLabel);
        if (sb.length() <= 0) sb.append(SINGLE_SPACE);
        acctLabel = sb.toString();

        MyJLinkLabel label1 = new MyJLinkLabel(acctLabel, target, SwingConstants.LEFT);
        MyJLinkLabel label2 = (sharesLabel != null) ? new MyJLinkLabel(sharesLabel, target, SwingConstants.RIGHT) : null;
        MyJLinkLabel label3 = new MyJLinkLabel(balLabel, target, SwingConstants.RIGHT);

        label1.addLinkListener(this);
        if (label2 != null) label2.addLinkListener(this);
        label3.addLinkListener(this);

        if (amt < 0L) {
            Color negFGColor = this.acctView.getMDGUI().getColors().negativeBalFG;
            if (label2 != null) label2.setForeground(negFGColor);
            label3.setForeground(negFGColor);
        }

        if (this.currentRow % 2 == 0) {
            Color bg = this.acctView.getMDGUI().getColors().homePageAltBG;
            label1.setOpaque(true);
            if (label2 != null) label2.setOpaque(true);
            label3.setOpaque(true);

            label1.setBackground(bg);
            if (label2 != null) label2.setBackground(bg);
            label3.setBackground(bg);
        }

        label1.setDrawUnderline(false);
        if (label2 != null) label2.setDrawUnderline(false);
        label3.setDrawUnderline(false);

        label1.setBorder(nameBorder);
        if (label2 != null) label2.setBorder(sharesBorder);
        label3.setBorder(amountBorder);
        if (label2 != null) {
            this.listPanel.add(label1, GridC.getc(1, this.currentRow).wx(1.0F).fillboth());
            this.listPanel.add(label2, GridC.getc(2, this.currentRow).fillboth());
            this.listPanel.add(label3, GridC.getc(3, this.currentRow).fillboth());
        } else {
            this.listPanel.add(label1, GridC.getc(1, this.currentRow).wx(1.0F).fillboth().colspan(2));
            this.listPanel.add(label3, GridC.getc(3, this.currentRow).fillboth());
        }
        this.currentRow += 1;
    }

    private double getRate(Account account) {
        switch (account.getAccountType()) {
            case CREDIT_CARD:
                return account.getAPRPercent();
            case LOAN:
                return account.getInterestRate();
            default:
                return 0;
        }
    }

    private void addAccounts(Account parentAcct,
                             DebtAmountWrapper aw,
                             boolean filter,
                             boolean showIt,
                             List<Account.AccountType> acctTypes) {

        Util.logConsole(true, "Widget: addAccounts() 5 params");
        ArrayList<Account> subAccounts = new ArrayList<>(parentAcct.getSubAccounts());

        CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();

        for (Account account : subAccounts) {
            boolean showAccount = showIt;

            if (filter && !acctTypes.contains(account.getAccountType())) {
                continue;
            }

            CurrencyType currency = account.getCurrencyType();
            long totalBal = getAccountValue(account, currency, null);     // gets recursive balance ignoring inactives....
            long totalBalForCreditDisplay = getAccountValue(account, currency, Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType());
            Util.logConsole(true, "... addAccounts: Acct: " + account + " totalBal: " + totalBal + " forCreditDisplay: " + totalBalForCreditDisplay);
            if (aw != null) {
//                long getBal = DebtAccountView.getBalance(getBalanceType(), account);
                long getBal = DebtAccountView.getBalance(
                        this.fromHomePageWidget ? getBalanceType() : Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType(),
                        account);
                long convertedBal = CurrencyTable.convertValue(getBal, currency, base);     // Convert Totals back to base rate..!
//                aw.add(convertedBal, getRate(account));
                aw.add(convertedBal, getRate(account));
                Util.logConsole(true, "... ... getBalance: " + getBal + " getRate: " + getRate(account) + " converted: " + convertedBal);
                aw.scannedAccount(account);
            }

            this.tooManyAccounts = ((this.tooManyAccounts) || (this.currentRow > 150));

            if (((totalBal == 0L) && (account.getHideOnHomePage())) || (account.getAccountOrParentIsInactive())) {
                showAccount = false;
            }
            if ((showAccount) && (!(this.tooManyAccounts))) {
                String sharesStr = null;
                String amtStr;
                if (this.fromHomePageWidget && Main.getWidgetForceValuesBaseCurrency()) {
                    amtStr = Main.getWidgetValueConversionCurrencyType(currency).formatFancy(CurrencyUtil.convertValue(totalBal, currency, Main.getWidgetValueConversionCurrencyType(currency)), this.dec);
                } else{
                    amtStr = currency.formatFancy(totalBal, this.dec);
                }
//                if (currency.getCurrencyType() == CurrencyType.Type.SECURITY) {
//                    sharesStr = amtStr;
//                    CurrencyType relCurr = AccountUtils.getRelCurrency(currency, parentAcct);
//                    long value = CurrencyUtil.convertValue(totalBal, currency, relCurr);
//                    amtStr = relCurr.formatFancy(value, this.dec);
//                }

                addAcctRow(account, sharesStr, amtStr, totalBal, totalBalForCreditDisplay);
                Util.logConsole(true, ".... addAcctRow: amtStr: " + amtStr + " totalBal: " + totalBal);
                Util.logConsole(true, "total: " + aw.getAmount());
            }

            int origRow = this.currentRow;
            boolean showSubAccounts = account.getPreferenceBoolean(getSubAcctExpansionKey(), true);

            MyJLinkLabel acctExpandLabel = null;

            addAccounts(account, aw, false, (showIt && showSubAccounts), acctTypes);

            if (showSubAccounts) {
                if (showAccount && this.currentRow != origRow && !(this.tooManyAccounts))
                    acctExpandLabel = new MyJLinkLabel("- ", account, SwingConstants.LEFT);
            } else if (showAccount && !this.tooManyAccounts) {
                acctExpandLabel = new MyJLinkLabel("+ ", account, SwingConstants.LEFT);
            }

            if (acctExpandLabel != null) {
                acctExpandLabel.setDrawUnderline(false);
                acctExpandLabel.addLinkListener(getExpander());
                acctExpandLabel.setBorder(expandLinkBorder);
                acctExpandLabel.setBorder(nameBorder);

                this.listPanel.add(acctExpandLabel, GridC.getc().xy(0, origRow - 1));
            }
        }
    }

    private void addAccounts(List<Account> subAccounts, DebtAmountWrapper aw) {
        Util.logConsole(true, "******************* Widget: addAccounts() 2 params");

        for (Account account : subAccounts) {

            CurrencyType currency = account.getCurrencyType();
            long totalBal = getAccountValue(account, currency, null);
            long totalBalForCreditDisplay = getAccountValue(account, currency, Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType());

            if (aw != null) {
                aw.add(CurrencyTable.convertValue(
                        DebtAccountView.getBalance(this.fromHomePageWidget ? getBalanceType() : Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType(),
                                account), currency, currency), getRate(account));
                aw.scannedAccount(account);
            }

            this.tooManyAccounts = ((this.tooManyAccounts) || (this.currentRow > 150));

            if (((totalBal == 0L) && (account.getHideOnHomePage()))
                    || (account.getAccountOrParentIsInactive())) {
                continue;
            }
            if (!(this.tooManyAccounts)) {
                String sharesStr = null;
                String amtStr = currency.formatFancy(totalBal, this.dec);
//                if (currency.getCurrencyType() == CurrencyType.Type.SECURITY) {
//                    sharesStr = amtStr;
//                    CurrencyType relCurr = AccountUtils.getRelCurrency(currency, account.getParentAccount());
//                    long value = CurrencyUtil.convertValue(totalBal, currency, relCurr);
//                    amtStr = relCurr.formatFancy(value, this.dec);
//                }

                addAcctRow(account, sharesStr, amtStr, totalBal, totalBalForCreditDisplay);
            }

        }
    }

    public final long getAccountValue(Account account, CurrencyType currency, BalanceType forceBalType) {
        CurrencyType currency2 = account.getCurrencyType();
        BalanceType balType = forceBalType == null
                ? (this.fromHomePageWidget ? getBalanceType() : Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType())
                : forceBalType;
        long realBalance = 0L;
        if (!account.getAccountOrParentIsInactive()) {
            realBalance += CurrencyTable.convertValue(
//                    DebtAccountView.getBalance(getBalanceType(), account),
                    DebtAccountView.getBalance(balType, account),
                    currency2, currency);
        }

        for (Account sub : account.getSubAccounts()) {
            if (!sub.getAccountOrParentIsInactive()) {
                realBalance += getAccountValue(sub, currency, forceBalType);
            }
        }
        return realBalance;
    }

    @Override
    public void linkActivated(Object link, InputEvent evt) {
        Util.logConsole(true, ">> Link clicked: " + link);
        if (link instanceof Account) {
            if ((evt.getModifiersEx() & MoneydanceGUI.ACCELERATOR_MASK) != 0)
                this.acctView.getMDGUI().selectAccountNewWindow((Account) link);
            else
                this.acctView.getMDGUI().selectAccount((Account) link);
        } else if (link instanceof String) {
            Main.getMDMain().showURL("moneydance:fmodule:" + Main.EXTN_ID + ":" + link);
        }
    }

    @Override
    public void mousePressed(MouseEvent evt) {
        if (evt.getSource() == this.balTypeLabel) showBalanceTypePopup();
    }

    @Override
    public void mouseReleased(MouseEvent evt) {
    }

    @Override
    public void mouseExited(MouseEvent evt) {
    }

    @Override
    public void mouseEntered(MouseEvent evt) {
    }

    @Override
    public void mouseClicked(MouseEvent evt) {
        Util.logConsole(true, "Inside DVP.mouseClicked()");
        Object src = evt.getSource();
        if (src == this.headerLabel) {
            Util.logConsole(true, "... triggering .toggleSectionExpanded()");
            toggleSectionExpanded();
        }
    }

    protected void showBalanceTypePopup() {
        Resources res = this.acctView.getMDGUI().getResources();
        JPopupMenu btMenu = new JPopupMenu();
        BalanceType[] balanceTypes = {BalanceType.BALANCE, BalanceType.CURRENT_BALANCE, BalanceType.CLEARED_BALANCE};
        for (BalanceType type : balanceTypes) {
            final BalanceType balType = type;
            btMenu.add(new AbstractAction(res.getBalanceType(type)) {
                public void actionPerformed(ActionEvent evt) {
                    boolean different = (balType != getBalanceType());
//                    prefs.setSetting(acctView.getBalanceTypePref(), balType.ordinal());
                    Main.setMDCCBalanceTypeSetting(balType.ordinal());
                    prefs.setSetting(acctView.getBalanceTypePref(), balType.ordinal());
                    if (!(different)) return;
                    setBalanceType(balType);
                    Main.lastRefreshTriggerWasAccountListener = false;
//                    DebtViewPanel.this.acctView.refresh();
                     refresh();
                }
            });
        }

        btMenu.show(this.balTypeLabel, 0, this.headerLabel.getHeight());
    }

    private void toggleSectionExpanded() {
        Util.logConsole(true, "DVP.toggleSectionExpanded() expanded was: " + this.expanded + " flipping to: " + !this.expanded);
        this.expanded = (!(this.expanded));
        this.prefs.setSetting(this.acctView.getSectionExpandedPref(), this.expanded);
        Main.lastRefreshTriggerWasAccountListener = false;
//        this.acctView.refresh();
         refresh();
    }

    @Override
    public void currencyTableModified(CurrencyTable currencyTable) {
        Main.lastRefreshTriggerWasAccountListener = false;
        this.acctView.refresh();
        // refresh();
    }

    @Override
    public void accountModified(Account account) {
        if (this.acctView.includes(account.getAccountType())) // == this.acctView.getAccountType())
            Main.lastRefreshTriggerWasAccountListener = true;
            this.acctView.refresh();
            // refresh();
    }

    @Override
    public void accountBalanceChanged(Account account) {
        if (account.getAccountType() == this.acctView.getAccountType())
            Main.lastRefreshTriggerWasAccountListener = true;
            this.acctView.refresh();
            // refresh();
    }

    @Override
    public void accountDeleted(Account parentAccount, Account deletedAccount) {
        Account.AccountType acctType = this.acctView.getAccountType();
        if ((parentAccount.getAccountType() != acctType)
                && (deletedAccount.getAccountType() != acctType)) return;
            Main.lastRefreshTriggerWasAccountListener = true;
        this.acctView.refresh();
        // refresh();
    }

    @Override
    public void accountAdded(Account parentAccount, Account newAccount) {
        Account.AccountType acctType = this.acctView.getAccountType();
        if ((parentAccount.getAccountType() != acctType)
                && (newAccount.getAccountType() != acctType)) return;
        Main.lastRefreshTriggerWasAccountListener = true;
        this.acctView.refresh();
        // refresh();
    }

    private class AccountExpander implements JLinkListener {

        public AccountExpander() {
            super();
        }

        @Override
        public void linkActivated(Object link, InputEvent evt) {
            Util.logConsole(true, "inside expand icon link listener... *** " + link + " key: " + getSubAcctExpansionKey());
            Account acct = (Account) link;

            if (acct.getPreferenceBoolean(getSubAcctExpansionKey(), true)) {
                acct.setPreference(getSubAcctExpansionKey(), false);
                Util.logConsole(true, "... was 'true', set to 'false'");
            }
            else {
                acct.setPreference(getSubAcctExpansionKey(), true);
                Util.logConsole(true, "... was 'false', set to 'true'");
            }
            Main.lastRefreshTriggerWasAccountListener = false;
            DebtViewPanel.this.refresh();
        }
    }


    /**
     * @return the dec
     */
    public char getDec() {
        return dec;
    }


    /**
     * @param dec the dec to set
     */
    public void setDec(char dec) {
        this.dec = dec;
    }


    /**
     * @return the acctView
     */
    public DebtAccountView getAcctView() {
        return acctView;
    }

    public String getSubAcctExpansionKey() {
        Util.logConsole(true, "^^ DVP.getSubAcctExpansionKey() returning: " + Main.EXPAND_SUBS_KEY);
        return Main.EXPAND_SUBS_KEY;
    }


    /**
     * @return the balanceType
     */
    public BalanceType getBalanceType() {
        return balanceType;
    }


    /**
     * @param balanceType the balanceType to set
     */
    public void setBalanceType(BalanceType balanceType) {
        this.balanceType = balanceType;
    }
}