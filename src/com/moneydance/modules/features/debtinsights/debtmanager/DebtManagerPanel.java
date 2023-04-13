/*
 * DebtManagerPanel.java
 *
 * Created on Oct 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 *
 *
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.awt.Color;
import java.awt.Font;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingConstants;
import javax.swing.border.BevelBorder;
import javax.swing.border.Border;
import javax.swing.border.CompoundBorder;
import javax.swing.border.EmptyBorder;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.MDColors;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.modules.features.debtinsights.*;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.model.DebtAccount;
import com.moneydance.modules.features.debtinsights.ui.acctview.DebtAccountView;
import com.moneydance.modules.features.debtinsights.ui.acctview.HierarchyView;
import com.moneydance.modules.features.debtinsights.ui.acctview.IconToggle;
import com.moneydance.modules.features.debtinsights.ui.acctview.SortView;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class DebtManagerPanel extends DebtViewPanel {
    private MDColors colors;
    private static final CreditLimitType creditLimitType = CreditLimitType.CREDIT_LIMIT;
    private static final Account.AccountType[] acctTypes = {Account.AccountType.CREDIT_CARD, Account.AccountType.LOAN};

    public DebtManagerPanel(DebtAccountView ccAccountView) {
        super(false, ccAccountView, acctTypes);
        setBorder(new CompoundBorder(new BevelBorder(BevelBorder.LOWERED),
                new EmptyBorder(12, 12, 12, 12)));
        setBackground(colors.homePageBG);
        setOpaque(true);
        activate();

    }

    @Override
    protected void init() {
        super.init();
        this.colors = this.acctView.getMDGUI().getColors();
    }

    @Override
    protected void addAcctRow(Account account, String sharesStr, String balanceStr, long amt, long balanceForCreditComponent) {
        switch (account.getAccountType()) {
            case CREDIT_CARD:
            case LOAN:
                addAcctRow(account, amt);
            default:
        }
    }

    @Override
    public String getSubAcctExpansionKey() {
        Util.logConsole(true, "^^ DMP.getSubAcctExpansionKey() returning: " + Main.EXPAND_SUBS_POPUP_KEY);
        return Main.EXPAND_SUBS_POPUP_KEY;
    }



//	private enum COL { LABEL, CARD_NUM, PMT, PMT_FLAG, INT_PMT, AMT, AMT_FLAG, LIMIT, APR, APR_FLAG; }

    private void addAcctRow(Account acct, long amt) {
        String acctLabel = acct.getAccountName();

        CurrencyType base = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType();

        Util.logConsole(true, "!! DMP.addAcctRow() - Hierarchy: " + this.acctView.getHierarchyView());
        if (this.acctView.getHierarchyView() != HierarchyView.FLATTEN && this.acctView.getAcctComparator() == null) {
            int indentDepth = acct.getDepth();

            StringBuilder sb = new StringBuilder();
            for (int i = 1; i < indentDepth; ++i)
                sb.append(THREE_SPACE);
            sb.append(acctLabel);
            if (sb.length() <= 0) sb.append(SINGLE_SPACE);
            acctLabel = sb.toString();
        }

        CurrencyType currency = acct.getCurrencyType();
//		CurrencyType relCurr = AccountUtils.getRelCurrency(currency, acct.getParentAccount());
        CurrencyType relCurr = base;        // Convert all numbers back to Base Currency

        long pmt = CurrencyUtil.convertValue(DebtAccount.getNextPayment(acct), currency, relCurr);
        long intPmt = CurrencyUtil.convertValue(DebtAccount.getInterestPayment(acct), currency, relCurr);
        Long limit = null;
        String cardNumber = null;

        long convertedAmt = CurrencyUtil.convertValue(amt, currency, base);

        //		Name	Acct #	Payment		Interest 	Balance		Limit	APR		When
        Object[] labels = {null, acctLabel, cardNumber, pmt, null, intPmt, convertedAmt, null, limit, DebtAccount.getAPR(acct), null};
        Map<Header, Object> valMap = getValueMap(acct, labels, currency, relCurr);

        int i = 0;
        for (Header col : Header.values()) {
            if (i == 0) {
                i++;
                continue;
            }
            Object label = valMap.get(col);
            if (label == null || label.toString().length() == 0) label = " ";

            Color bg = (this.currentRow % 2 == 0 ? this.colors.registerBG2 : this.colors.registerBG1);

            JLabel jLbl;

            if (label instanceof JLabel) {
                jLbl = (JLabel) label;
                jLbl.setBackground(bg);
            } else {
                jLbl = makeJLinkLabel(label, acct, relCurr, bg, col.border);
            }

            if (label instanceof Long) {        // LOAN accounts will return null in Credit Limit
                switch (col) {
                    case LIMIT:
                    case BALANCE: {
                        if ((long) label < 0) {
                            jLbl.setForeground(this.colors.negativeBalFG);
                        }
                        if (Main.getWidgetEnhancedColors() && (long) label > 0L) {
                            jLbl.setForeground(Util.getPositiveGreen());
                        }
                    }
                }
            }

            Util.logConsole(true, "ROW: text: " + jLbl.getText());
            GridC gridC = GridC.getc().xy(i++, this.currentRow).wx(1f).fillx();
            gridC = (label instanceof String ? gridC.west() : gridC.east());

            this.listPanel.add(jLbl, gridC);
        }

        this.currentRow++;
    }

    private static final long days90 = 90L * 24L * 3600L * 1000L;

    private Map<Header, Object> getValueMap(Account acct, Object[] labels, CurrencyType currency, CurrencyType relCurr) {
        Map<Header, Object> map = new HashMap<Header, Object>();

        for (int i = 0; i < labels.length; i++) {
            map.put(Header.values()[i], labels[i]);
        }

        map.put(Header.PMT_FLG, (Math.abs((Long) map.get(Header.PAYMENT)) < Math.abs((Long) map.get(Header.INTEREST)) ? Flag.RED.makeFlag("Payment is less than accruing interest") : null));
        if (acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
            map.put(Header.LIMIT, CurrencyUtil.convertValue(BetterCreditCardAccount.getCreditLimit(acct), currency, relCurr));
            map.put(Header.ACCT_NUM, acct.getCardNumber());

            float halfLimit = -CurrencyUtil.convertValue(BetterCreditCardAccount.getCreditLimit(acct), currency, relCurr) / 2f;
            map.put(Header.BAL_FLG, ((Long) map.get(Header.BALANCE) < halfLimit ? Flag.YELLOW.makeFlag("Credit used is more than 50% of credit Limit") : null));

            Date changeDate = BetterCreditCardAccount.getRateChangeDate(acct);
            if (changeDate != null && changeDate.getTime() > 0) {
                long t = new Date().getTime();
                long cd = changeDate.getTime();
                boolean aprChange = cd > t && cd - t < days90;
                map.put(Header.APR_FLG, (aprChange ? Flag.YELLOW.makeFlag("APR will change on " + changeDate) : null));
            }
        }

        if (acct.getAccountType() == Account.AccountType.LOAN) {
        }

        return map;
    }

    private JLinkLabel makeJLinkLabel(Object value, Account acct, CurrencyType relCurr, Color bg, Border border) {
        String valStr = value.toString();
        int align = (value instanceof String ? SwingConstants.LEFT : SwingConstants.RIGHT);
        Color fgColor = Color.black;

        if (value instanceof Long) {
            valStr = relCurr.formatFancy((Long) value, this.dec);

            if ((Long) value < 0) {
                fgColor = this.colors.negativeBalFG;
            }
        } else if (value instanceof Double || value instanceof Float) {
            valStr += "%";
        }
        JLinkLabel lbl = new JLinkLabel(valStr, acct, align);
        lbl.setForeground(fgColor);
        lbl.setBorder(border);
        lbl.addLinkListener(this);
        lbl.setDrawUnderline(false);
        lbl.setOpaque(true);
        lbl.setBackground(bg);

        if (hasSubAccounts(acct)) {
//			Font f = lbl.getFont();
//			lbl.setFont(f.deriveFont(Font.BOLD, f.getSize()+1));
        }

        return lbl;
    }

    private boolean hasSubAccounts(Account acct) {
        return acct.getSubAccountCount() > 0;
    }

    @Override
    protected void addLabelsToHeader() {
//		-  U+2796
//		+  U+2795	
//		0  U+20E0
//		String[] headers = {"\u20E0", "Name","Acct #","Payment","Interest", "Balance","Limit","APR"}; //,"When"};
//		int[] align = {SwingConstants.CENTER, SwingConstants.LEFT,SwingConstants.LEFT,SwingConstants.RIGHT,SwingConstants.RIGHT,SwingConstants.RIGHT,SwingConstants.RIGHT};
        Font font = getFont();
        font = new Font(font.getName(), Font.BOLD, font.getSize() + 2);

        Header sortHeader = (acctView.getAcctComparator() != null ? acctView.getAcctComparator().getHeader() : null);

        int i = 0;
        for (Header header : Header.values()) {
            IconToggle toggle = (IconToggle) header.icon;
            toggle = (toggle != null ? toggle.getState(acctView) : null);
            String sortLbl = (toggle != null ? ((IconToggle) toggle.getNextState()).getLabel() : Strings.BLANK);

            String labelStr;
            if (header == Header.BALANCE) {
                labelStr = this.acctView.getMDGUI().getResources()
                        .getBalanceType(Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType()) + sortLbl;
            } else {
                labelStr = header.label + sortLbl;
            }

            JLabel lbl = new JLabel(labelStr, header.align);
            if (toggle != null && (header == sortHeader || !(toggle instanceof SortView))) {
                if (toggle.getIcon().getIconHeight() <= 0 || toggle.getIcon().getIconWidth() <= 0) {
                    Util.logConsole("WARNING >> toggle icon size is < 0? (ignoring)");
                } else {
                    if (header != Header.HIERARCHY) {
                        lbl.setIcon(toggle.getIcon());
                        lbl.setHorizontalTextPosition(SwingConstants.LEADING);
                    } else {
                    }
                }
            }
            lbl.setFont(font);
            lbl.setBorder(header.border);
            lbl.addMouseListener(header.getListener(lbl, header, this));
            lbl.setToolTipText(header.tooltip);

            listPanel.add(lbl, GridC.getc().xy(i++, 0).fillx());
        }

        this.currentRow++;
    }

    @Override
    protected void setHeaderLabels(CurrencyType base,
                                   DebtAmountWrapper amountWrapper) {
    }

    @Override
    protected void addTotalsRow(JPanel totalPanel, CurrencyType base, DebtAmountWrapper totalDebt) {
        Util.logConsole(true, "DebtManager: addTotalsRow() base: " + base + " totalDebt: " + totalDebt.getAmount());
        Font font = getFont();
        font = new Font(font.getName(), Font.BOLD, font.getSize() + 2);

        int i = 0;
        for (Header header : Header.values()) {
            JLabel lbl = getValueFor(header.totAccessor, base, totalDebt, header, font);        // This is where the total is returned (as a String)
            listPanel.add(lbl, GridC.getc().xy(i++, this.currentRow).fillx());
        }
    }

    private static final Class<?>[] params = {AccountBook.class, DebtAmountWrapper.class};

    private JLabel getValueFor(String methodName, CurrencyType base, DebtAmountWrapper totalDebt, Header header, Font font) {
        try {
            Method m = AccountUtils.class.getMethod(methodName, params);
            Object[] args = {getRoot(), totalDebt};
            Object o = m.invoke(null, args);
            String valueStr = "ERROR";
            Color negColor = Main.getMDGUI().getColors().negativeBalFG;
            Color posColor = Main.getWidgetEnhancedColors() ? Util.getPositiveGreen() : Main.getMDGUI().getColors().defaultTextForeground;
            Color color = Main.getMDGUI().getColors().defaultTextForeground;
            if (o instanceof Long) {
                long value = (Long) o;
                valueStr = base.formatFancy(value, this.dec);
                if (value < 0) color = negColor;
                if (value > 0) color = posColor;
            } else if (o instanceof Double || o instanceof Float) {
                if (o instanceof Double) {
                    double value = (Double) o;
                    if (value < 0) color = negColor;
                    if (value > 0) color = posColor;
                } else {
                    float value = (Float) o;
                    if (value < 0) color = negColor;
                    if (value > 0) color = posColor;
                }
                valueStr = o.toString() + "%";
            }
            JLabel lbl = new JLabel(valueStr, header.align);
            lbl.setFont(font);
            lbl.setBorder(header.border);
            switch (header) {
                case PAYMENT:
                case INTEREST:
                case BALANCE:
                case LIMIT: {
                    lbl.setForeground(color);
                    break;
                }

            }
            return lbl;

        } catch (SecurityException | IllegalArgumentException | InvocationTargetException | IllegalAccessException e) {
            Util.logConsole("Error: " + e);
        } catch (NoSuchMethodException e) {
        }
        return new JLabel(methodName);
    }

    @Override
    protected JLabel getAccountTypeSpecificLabel() {
        if (DebtManagerPanel.creditLimitType != null)
            return DebtManagerPanel.creditLimitType.getTotal(this, getRoot());

        return new JLabel(" ");
    }


    /**
     * @return the creditlimittype
     */
    public static CreditLimitType getCreditLimitType() {
        return creditLimitType;
    }
}
