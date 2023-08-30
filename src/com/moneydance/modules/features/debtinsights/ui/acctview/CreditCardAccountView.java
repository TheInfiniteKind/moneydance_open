package com.moneydance.modules.features.debtinsights.ui.acctview;

import javax.swing.*;

import com.infinitekind.moneydance.model.Account;
import com.moneydance.apps.md.controller.UserPreferences;
import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.CreditCardViewPanel;

public class CreditCardAccountView extends GenericDebtAccountView {
    public Main extnContext;

    public CreditCardAccountView(Main context) {
        this(Main.getMDGUI());
        extnContext = context;
    }

    public CreditCardAccountView(MoneydanceGUI mdGUI) {
        super(mdGUI, "internal.cc_accts",
                Account.AccountType.CREDIT_CARD, "home_cc_balances", UserPreferences.GUI_HOME_CC_BAL,
                UserPreferences.GUI_HOME_CC_EXP);
    }


    @Override
    public JComponent getGUIView(AccountBook book) {

        Util.logConsole(true, ".getGUIView() called (book: " + book + ")");
        if (book == null){
            return null;
        }
        if (this.debtView != null) return this.debtView;
        synchronized (this) {
            if (this.debtView == null) {
                this.debtView = new CreditCardViewPanel(this, getAccountType());
                //                this.debtView.setBorder(BorderFactory.createCompoundBorder(MoneydanceLAF.homePageBorder,
                //                BorderFactory.createEmptyBorder(0, 10, 0, 10)));;;;
                this.debtView.setBorder(MoneydanceLAF.homePageBorder);
            }
            return this.debtView;
        }
    }

    @Override
    public void setActive(boolean active) {
        if (extnContext.killSwitch){
            Util.logConsole(true, ".setActive(" + active + "): ignoring as killSwitch set....");
            return;
        }
        super.setActive(active);
    }

    @Override
    public void refresh() {
        Util.logConsole(true, "CCAV.refresh()");
        if (extnContext.killSwitch){
            Util.logConsole(true, "CCAV.refresh(): ignoring as killSwitch set....");
            return;
        }
        super.refresh();
    }

    @Override
    public synchronized void reset() {
        super.reset();
    }

    @Override
    public String getID() { return Main.EXTN_WIDGET_ID; }

    @Override
    public String toString() {
        return Main.getWidgetName();
    }
}
