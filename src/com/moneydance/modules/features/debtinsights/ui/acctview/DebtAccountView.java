package com.moneydance.modules.features.debtinsights.ui.acctview;

import java.util.*;

import javax.swing.JComponent;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.BalanceType;
import com.moneydance.apps.md.view.HomePageView;
import com.moneydance.apps.md.view.gui.DefaultAcctSearch;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.model.DebtAccountComparator;
import com.moneydance.modules.features.debtinsights.ui.MyCollapsibleRefresher;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;

public abstract class DebtAccountView implements HomePageView {
    protected DebtViewPanel debtView = null;
    private List<Account.AccountType> acctTypes;
    protected MoneydanceGUI mdGUI;
    private HierarchyView hierarchy = HierarchyView.EXPAND_ALL;
    private DebtAccountComparator acctComparator;

    private final MyCollapsibleRefresher refresher = new MyCollapsibleRefresher(() -> {
        Util.logConsole(true, "Inside MyCollapsibleRefresher::Runnable.... Calling .reallyRefresh()..");
        DebtAccountView.this.reallyRefresh();
    });

    public DebtAccountView(MoneydanceGUI mdGUI)
    {
        this.mdGUI = mdGUI;
    }

    public abstract Account.AccountType getAccountType();

    public List<Account.AccountType> getAccountTypes() {
        if (acctTypes == null) {
            acctTypes = Collections.singletonList(getAccountType());
        }
        return acctTypes;
    }

    public void setAccountTypes(List<Account.AccountType> accountTypes) {
        this.acctTypes = accountTypes;
    }

    public boolean includes(Account.AccountType accountType) {
        return getAccountTypes().contains(accountType);
    }

    public abstract String getBalanceTypePref();

    public abstract String getSectionExpandedPref();

    @Override
    public JComponent getGUIView(AccountBook book) {

        Util.logConsole(true, "DAV.getGUIView() called (book: " + book + ")");
        assert false: "I Don't really want to be called at this level!";
        return null;

//        if (book == null){
//            return null;
//        }
//        if (this.debtView != null) return this.debtView;
//        synchronized (this) {
//            if (this.debtView == null) {
//
//                this.debtView = new DebtViewPanel(true, this, getAccountType());
//                this.debtView.setBorder(MoneydanceLAF.homePageBorder);
//            }
//            return this.debtView;
//        }
    }

    public MoneydanceGUI getMDGUI() {
        return this.mdGUI;
    }

    @Override
    public void setActive(boolean active) {
        Util.logConsole(true, ".setActive(): " + active);
        if (this.debtView != null) {
            if (active)
                this.debtView.activate();
            else
                this.debtView.deactivate();
        }
    }

    @Override
    public void refresh() {
        Util.logConsole(true, "DAV.refresh()");
        if (this.mdGUI.getSuspendRefreshes())
            return;

        if (this.debtView != null) {
            Util.logConsole(true, "... calling refresher.enqueueRefresh()");
            this.refresher.enqueueRefresh();
        }
    }

    public void reallyRefresh() {
        Util.logConsole(true, "... Inside DAV.reallyRefresh() - calling debtView.refresh()");
        if (this.debtView != null) this.debtView.refresh();
    }

    @Override
    public synchronized void reset() {
        Util.logConsole(true, ".reset()");
        setActive(false);
        this.debtView = null;
    }

    public String getBalStr(int balType) {
        BalanceType type = BalanceType.fromInt(balType);
        return this.mdGUI.getStr(type.getResourceKey());
    }

    public HierarchyView getHierarchyView() {
        return hierarchy;
    }



    public List<Account> getAccounts(Account parentAccount) {
        if (parentAccount == null) return null;

        // The below changed from using AcctFilter() for MD2023.2(5008+ KOTLIN builds) onwards by IK Developer
        List<Account.AccountType> types = getAccountTypes();
        
        DefaultAcctSearch acctSearch = new DefaultAcctSearch();
        acctSearch.setShowRootAccounts(types.contains(Account.AccountType.ROOT));
        acctSearch.setShowBankAccounts(types.contains(Account.AccountType.BANK));
        acctSearch.setShowCreditCardAccounts(types.contains(Account.AccountType.CREDIT_CARD));
        acctSearch.setShowInvestAccounts(types.contains(Account.AccountType.INVESTMENT));
        acctSearch.setShowSecurityAccounts(types.contains(Account.AccountType.SECURITY));
        acctSearch.setShowAssetAccounts(types.contains(Account.AccountType.ASSET));
        acctSearch.setShowLiabilityAccounts(types.contains(Account.AccountType.LIABILITY));
        acctSearch.setShowLoanAccounts(types.contains(Account.AccountType.LOAN));
        acctSearch.setShowExpenseAccounts(types.contains(Account.AccountType.EXPENSE));
        acctSearch.setShowIncomeAccounts(types.contains(Account.AccountType.INCOME));
        
        List<Account> acctList = AccountUtil.allMatchesForSearch(Main.getMDMain().getCurrentAccountBook(), acctSearch);
        // end of AcctFilter changes ^^^^^^

        if (acctComparator != null) {
            acctList.sort(acctComparator);
        }
        return acctList;
    }


    public void setHierarchyView(HierarchyView showHierarchy) {
        this.hierarchy = showHierarchy;
    }

    public void setAcctComparator(DebtAccountComparator acctComparator) {
        this.acctComparator = acctComparator;
        Main.lastRefreshTriggerWasAccountListener = false;
        refresh();
    }

    public DebtAccountComparator getAcctComparator() {
        return this.acctComparator;
    }


	public static long getBalance(BalanceType balType, Account acct)
	{
        return AccountUtils.getActiveXBalance(acct, balType);
//	    if (acct.getAccountOrParentIsInactive()) return 0L;
//	    switch (balType) {
//	    	case CURRENT_BALANCE:
//	    		return acct.getUserCurrentBalance();
//	    	case BALANCE:
//	    		return acct.getBalance();
//	    	case CLEARED_BALANCE:
//	    		return acct.getUserClearedBalance();
//	    	default:
//	    		return acct.getUserBalance();
//	    }

  }

}