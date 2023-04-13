/*
 * DebtManagerWindow.java
 *
 * Created on Oct 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 *
 *
 */
package com.moneydance.modules.features.debtinsights.debtmanager;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.*;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.SecondaryFrame;
import com.moneydance.apps.md.view.resources.BalanceTypeChoice;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.ui.DisplayHelp;

public class DebtManagerWindow extends SecondaryFrame implements ActionListener {
    private DebtManagerPanel view;
    private final com.moneydance.modules.features.debtinsights.Main extnContext;
    private JCheckBox jckbox;
    private JComboBox<?> balanceChoice;
    private String HelpFile;


    public DebtManagerWindow(MoneydanceGUI mdGUI, com.moneydance.modules.features.debtinsights.Main extnContext) throws HeadlessException {
        super(mdGUI, Main.EXTN_NAME + ": " + Main.EXTN_OVERVIEW_TITLE);

        this.mdGUI = mdGUI;
        this.extnContext = extnContext;

        String baseCurrStr = Main.getMDMain().getCurrentAccountBook().getCurrencies().getBaseType().getIDString();

        setUsesDataFile(true);
        setRememberSizeLocationKeys(String.format("gui.%s_size", Main.EXTN_ID), String.format("gui.%s_location", Main.EXTN_ID),
                new Dimension(1150, 350));

        getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close_window");
        getRootPane().getActionMap().put("close_window", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                goAway();
            }
        });

        if (hasDebtAccounts(mdGUI.getCurrentAccount())) {
            DMDebtAccountView ccAccountView = new DMDebtAccountView(mdGUI, Main.POPUP_GUI_HOME_CC_EXPANDED);
            Util.logConsole(true, "Inside DMW.constructor. hierarchy: " + ccAccountView.getHierarchyView());
            ccAccountView.setActive(true);

            view = new DebtManagerPanel(ccAccountView);
//            view.setAllExpanded(Main.getMDMain().getCurrentAccountBook().getRootAccount(), true); // TODO HERE;;;
            JScrollPane jsp = new JScrollPane(view);

            int onCol = 0;
            int onRow = 0;

            JPanel mainPnl = new JPanel(new GridBagLayout());
            mainPnl.add(jsp, GridC.getc(onCol++, onRow).wxy(1.0F, 1.0F).colspan(5).fillboth());

            mainPnl.add(Box.createVerticalStrut(200), GridC.getc(onCol, onRow));

            onRow++;
            onCol = 0;

            JPanel WidgetControlsPanel1 = new JPanel(new GridBagLayout());

            JButton btn;
            JButton btnHelp;

            btnHelp = new JButton("Help");
            btnHelp.setActionCommand("help");
            btnHelp.putClientProperty("JButton.buttonType", "roundRect");
            WidgetControlsPanel1.add(btnHelp, GridC.getc(onCol++, 0).insets(2, 10, 2, 5));

            btn = new JButton("Set Widget Name");
            btn.setActionCommand(Main.EXTN_WIDGET_NAME_KEY);
            btn.setToolTipText("Sets the Title / Name of the widget displayed on the MD Summary Screen");
            btn.putClientProperty("JButton.buttonType", "roundRect");
            WidgetControlsPanel1.add(btn, GridC.getc(onCol++, 0).insets(2, 10, 2, 5));

            JCheckBox toggleColors = new JCheckBox("Toggle Enhanced Colors", Main.getWidgetEnhancedColors());
            toggleColors.setActionCommand(Main.EXTN_WIDGET_ENHANCED_COLORS_KEY);
            toggleColors.setToolTipText("Allows enhanced colors (e.g. Green) on some positive values....");
            WidgetControlsPanel1.add(toggleColors, GridC.getc(onCol++, 0).insets(2, 5, 2, 10));

            JCheckBox overridePmtPlanBalance = new JCheckBox("Override MD's Payment Plan to always use Balance?", Main.getWidgetOverridePaymentPlanBalance());
            overridePmtPlanBalance.setActionCommand(Main.EXTN_WIDGET_OVERRIDE_PAYMENT_PLAN_BALANCE_KEY);
            overridePmtPlanBalance.setToolTipText("Allows you to override any MD Payment Plan set in Tools/Accounts from Current/Cleared Balance to use Balance");
            WidgetControlsPanel1.add(overridePmtPlanBalance, GridC.getc(onCol++, 0).insets(2, 5, 2, 10));

            mainPnl.add(WidgetControlsPanel1, GridC.getc(0, onRow++).colspan(5));

            onCol = 0;
            JPanel WidgetControlsPanel2 = new JPanel(new GridBagLayout());
            WidgetControlsPanel2.add(new JLabel("Credit calculations Balance Type:"), GridC.getc(onCol++, 0).insets(2, 4, 2, 5));

            this.jckbox = new JCheckBox("<< Use widget's dynamic setting", Main.getWidgetCalculationBalanceTypeChoice() == Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN);
            this.jckbox.setToolTipText("Override Avail. Credit, graphs & int calcs to always use selected Balance. Otherwise use widget's selected balance");
            this.jckbox.setActionCommand(Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY);

            WidgetControlsPanel2.add(this.jckbox, GridC.getc(onCol++, 0).insets(2, 5, 2, 10));

            WidgetControlsPanel2.add(new JLabel("...or always use>>"), GridC.getc(onCol++, 0).insets(2, 4, 2, 5).east());

            BalanceTypeChoice[] balanceTypeChoices = new BalanceTypeChoice[]
                    {new BalanceTypeChoice(mdGUI, BalanceType.CURRENT_BALANCE),
                            new BalanceTypeChoice(mdGUI, BalanceType.BALANCE),
                            new BalanceTypeChoice(mdGUI, BalanceType.CLEARED_BALANCE)};

            this.balanceChoice = new JComboBox<>(balanceTypeChoices);
            BalanceType preSelectBT = Main.getWidgetCalculationBalanceTypeChoiceAsBalanceType();
            for (BalanceTypeChoice itm : balanceTypeChoices) {
                if (itm.getValue() == preSelectBT) {
                    this.balanceChoice.setSelectedItem(itm);
                    break;
                }
            }
            this.balanceChoice.setActionCommand(Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY + "_comboBoxChanged");
            this.balanceChoice.setEnabled(!this.jckbox.isSelected());
            WidgetControlsPanel2.add(this.balanceChoice, GridC.getc(onCol++, 0).insets(2, 2, 2, 10));
            mainPnl.add(WidgetControlsPanel2, GridC.getc(0, onRow++).colspan(5));

            JPanel WidgetControlsPanel3 = new JPanel(new GridBagLayout());


            JCheckBox alwaysUseBase = new JCheckBox(String.format("Convert all Widget's values to Base currency (%s)?", baseCurrStr), Main.getWidgetForceValuesBaseCurrency());
            alwaysUseBase.setActionCommand(Main.EXTN_WIDGET_FORCE_VALUES_BASE_CURRENCY_KEY);
            alwaysUseBase.setToolTipText(String.format("Converts all values on Summary Screen widget to your base currency (%s)", baseCurrStr));
            WidgetControlsPanel3.add(alwaysUseBase, GridC.getc(onCol++, 0).insets(2, 5, 2, 10));

            JCheckBox toggleDebug = new JCheckBox("Debug", Main.getDebug());
            toggleDebug.setActionCommand(Main.EXTN_WIDGET_DEBUG_KEY);
            toggleDebug.setToolTipText("Toggles Debug messages ON/OFF in Help/Console....");
            WidgetControlsPanel3.add(toggleDebug, GridC.getc(onCol++, 0).insets(2, 5, 2, 10));

            mainPnl.add(WidgetControlsPanel3, GridC.getc(0, onRow++).colspan(5));

            btnHelp.addActionListener(this);
            btn.addActionListener(this);
            toggleColors.addActionListener(this);
            overridePmtPlanBalance.addActionListener(this);
            this.jckbox.addActionListener(this);
            this.balanceChoice.addActionListener(this);
            alwaysUseBase.addActionListener(this);
            toggleDebug.addActionListener(this);

            setContentPane(mainPnl);

//            AwtUtil.centerWindow(this);
        } else {
            JOptionPane.showMessageDialog(this, "There are no CreditCard or Loan Accounts to show.");
        }
    }

    public void actionPerformed(ActionEvent evt) {
        Util.logConsole(true, "Inside DMW.actionPerformed: evt: " + evt + "actionCommand: '" + evt.getActionCommand() + "'");

        switch (evt.getActionCommand()) {
            case "help":
                new DisplayHelp(mdGUI, this, Main.EXTN_NAME + ": Help....", false);
                return;

            case Main.EXTN_WIDGET_NAME_KEY:
                String oldWidgetName = Main.getWidgetName();
                String newWidgetName = this.mdGUI.askForInput("New widget name:",
                        "This sets the widget's name on the Summary Page", oldWidgetName, false);

                if (StringUtils.isBlank(newWidgetName) || newWidgetName.equals(oldWidgetName)) {
                    return;
                }
                Main.setWidgetName(newWidgetName);
                break;

            case Main.EXTN_WIDGET_DEBUG_KEY:
                Main.setDebug((((JCheckBox) evt.getSource()).isSelected()));
                break;

            case Main.EXTN_WIDGET_FORCE_VALUES_BASE_CURRENCY_KEY:
                Main.setWidgetForceValuesBaseCurrency((((JCheckBox) evt.getSource()).isSelected()));
                break;

            case Main.EXTN_WIDGET_ENHANCED_COLORS_KEY:
                Main.setWidgetEnhancedColors((((JCheckBox) evt.getSource()).isSelected()));
                break;

            case Main.EXTN_WIDGET_OVERRIDE_PAYMENT_PLAN_BALANCE_KEY:
                Main.setWidgetOverridePaymentPlanBalance((((JCheckBox) evt.getSource()).isSelected()));
                break;

            case Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY:
            case Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY + "_comboBoxChanged":
                this.balanceChoice.setEnabled(!this.jckbox.isSelected());
                BalanceTypeChoice selectedItem = (BalanceTypeChoice) this.balanceChoice.getSelectedItem();

                if (this.jckbox.isSelected()) {
                    this.balanceChoice.setEnabled(false);
                    Main.setWidgetCalculationBalanceTypeChoice(Main.EXTN_WIDGET_BALANCETYPE_CHOICE_KEY_PERCOLUMN);
                }else{
                    this.balanceChoice.setEnabled(true);
                    if (selectedItem != null && selectedItem.getValue() != null) {
                        Main.setWidgetCalculationBalanceTypeChoice(selectedItem.getValue().ordinal());
                    } else{
                        Util.logConsole("Warning.. Logic error... Balance Type JComboBox has no selected items...?");
                    }
                }
                break;
        }

        refresh();

        if (Main.widgetViewReference != null) {
            Main.widgetViewReference.refresh();
        }
    }

    public void goneAway() {
        Util.logConsole(true, ".goneAway() called....");
        this.extnContext.debtManagerWindow = null;
        super.goneAway();
    }

    public boolean refresh() {
        if (this.view != null) {
            Util.logConsole(true, "DMW.refresh() executing....");
            this.view.refresh();
            return true;
        }
        return false;

    }

    private boolean hasDebtAccounts(Account root) {
        if (root.getSubAccountCount() > 0) {
            for (int i = 0; i < root.getSubAccountCount(); i++) {
                if (hasDebtAccounts(root.getSubAccount(i))) {
                    return true;
                } else if (isDebtAccount(root.getSubAccount(i))) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean isDebtAccount(Account acct) {
        return acct.getAccountType() == Account.AccountType.CREDIT_CARD ||
                acct.getAccountType() == Account.AccountType.LOAN;
    }

    @Override
    public void preferencesUpdated() {
        super.preferencesUpdated();
    }
}
