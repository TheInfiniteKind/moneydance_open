/*
 * DebtViewPanel.java
 * 
 * Created on Sep 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
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
import java.util.Collections;
import java.util.List;

import javax.swing.Box;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.SwingConstants;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;

import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.controller.BalanceType;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.MDAction;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.awt.JLinkListener;
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.DebtAmountWrapper;
import com.moneydance.modules.features.debtinsights.ui.acctview.DebtAccountView;
import com.moneydance.modules.features.debtinsights.ui.acctview.HierarchyView;

public class DebtViewPanel extends JPanel 
	implements JLinkListener, CurrencyListener, AccountListener, MouseListener
{
//	private static Logger log = LoggerFactory.getLogger(DebtViewPanel.class);
	public DebtAccountView	acctView;

	protected JPanel			listPanel;
	protected JLabel			headerLabel;
	protected JLabel			balTypeLabel;
	protected JLabel			totalValLabel;
	private BalanceType			balanceType		= BalanceType.CURRENT_BALANCE;
	protected int				currentRow		= 0;
	private AccountExpander		expander		= null;
	protected boolean				expanded		= true;
	protected char				dec;
	public UserPreferences		prefs;
	private boolean				tooManyAccounts	= false;

	private static final String EXPAND_SUBS_KEY = "debtinsights_gui_expand_subaccts";
	private static final String EXPANDED = "/com/moneydance/apps/md/view/gui/icons/down_triangle.png";
	private static final String COLLAPSED = "/com/moneydance/apps/md/view/gui/icons/right_triangle.png";
	protected static final String SELECTOR = "/com/moneydance/apps/md/view/gui/icons/selector_sm.png";
	
	protected static final String THREE_SPACE = "   ";
	protected static final String SINGLE_SPACE = " ";

	public static final Border nameBorder = new EmptyBorder(3, 6, 3, 0);
	public static final Border amountBorder = new EmptyBorder(3, 0, 3, 6);
	public static final Border sharesBorder = new EmptyBorder(3, 3, 3, 3);
	public static final Border expandLinkBorder = new EmptyBorder(3, 6, 3, 0);
	
	public DebtViewPanel(DebtAccountView betterAccountView,
											 Account.AccountType... acctTypes)
	{
		this.acctView = betterAccountView;
		
		init();
		

//		if (this.acctView.)
//		{
//			activate();
//		}
	}
	
	protected AccountBook getRoot()
	{
		return this.acctView.getMDGUI().getCurrentBook();
	}
	
	protected void init()
	{
		this.prefs = this.acctView.getMDGUI().getPreferences();
		
		setBalanceType( BalanceType.fromInt(prefs
											.getIntSetting (this.acctView.getBalanceTypePref(), BalanceType.BALANCE.ordinal())));
		
		this.expanded = this.prefs.getBoolSetting(
				this.acctView.getSectionExpandedPref(), true);

		this.dec = this.prefs.getDecimalChar();
		
		GridBagLayout gridbag = new GridBagLayout();
		setLayout(gridbag);
		setOpaque(false);

		this.listPanel = new JPanel(gridbag);

		add(this.listPanel, GridC.getc().xy(0, 0).wx(1.0F).fillboth());
		
		add(Box.createVerticalStrut(2), GridC.getc().xy(0, 4).wy(1.0F));

		this.listPanel.setOpaque(false);

	}
	
	protected void addHeaderRow(JPanel listPanel)
	{
		this.headerLabel = new JLabel(" ", 2);
//		this.headerLabel.setHorizontalTextPosition(SwingConstants.LEFT);
		Font font = getFont();
		font = new Font(font.getName(), 1, font.getSize() + 2);
		
		this.headerLabel.setFont(font);
		this.headerLabel.addMouseListener(this);

		this.balTypeLabel = new JLabel(" ", 4);
		this.balTypeLabel.setFont(font);
		this.balTypeLabel.setHorizontalTextPosition(2);
		this.balTypeLabel.setIcon(this.acctView.getMDGUI()
												.getImages()
												.getIcon(SELECTOR));
		this.balTypeLabel.addMouseListener(this);

		addLabelsToHeader();
		this.currentRow++;
	}
	
	protected void addLabelsToHeader()
	{
		listPanel.add(this.headerLabel, 
				GridC.getc().xy(0, 0).wx(1.0F).fillx().west());
		listPanel.add(this.balTypeLabel, GridC.getc().xy(1, 0));
		
		this.currentRow++;

	}
	
	protected void addTotalsRow(JPanel totalPanel, CurrencyType baseCurr, DebtAmountWrapper aw)
	{

		Font normal = getFont();
		Font totalsFont = new Font(normal.getName(), Font.BOLD, normal.getSize() + 1);
		
		JLabel totalLabel = new JLabel("TOTAL", SwingConstants.LEFT);

		this.totalValLabel = new JLabel(" ", SwingConstants.RIGHT);
		
		JLabel[] labels = {totalLabel,getAccountTypeSpecificLabel(), this.totalValLabel};
		for (int i=0; i < labels.length; i++)
		{
			if (labels[i] != null)
			{
				labels[i].setFont( totalsFont);
				totalPanel.add(labels[i],
					GridC.getc().xy(i, this.currentRow+1).wx(1.0F).colspan(2).fillx());
			}
		}
	}
	
	protected JLabel getAccountTypeSpecificLabel()
	{
		return new JLabel(" ", 4);
	}
	
	synchronized AccountExpander getExpander()
	{
		if (this.expander == null)
		{
			this.expander = new AccountExpander();
		}
		return this.expander;
	}

	public void activate()
	{
		getRoot().addAccountListener(this);
		CurrencyTable ct = getRoot().getCurrencies();
		if (ct != null) 
		{
			ct.addCurrencyListener(this);
		}
		refresh();
	}

	public void deactivate()
	{
		getRoot().removeAccountListener(this);
		getRoot().getCurrencies().removeCurrencyListener(this);
	}

	public void toggleShowHierarchy(JLabel source)
	{
		this.acctView.setHierarchyView(this.acctView.getHierarchyView().getNextState());

		switch (this.acctView.getHierarchyView())
		{
			case EXPAND_ALL:
				this.acctView.setAcctComparator(null);
				setAllExpanded(getRoot().getRootAccount(), true);
				break;
			case COLLAPSE_ALL:
				this.acctView.setAcctComparator(null);
				setAllExpanded(getRoot().getRootAccount(), false);
				break;
			case FLATTEN:
		}
		refresh();
	}
	
	private void setAllExpanded(Account account, boolean expand)
	{
		if (account.getSubAccountCount() > 0 )
		{
			if (isDebtAccount(account))
			{
				account.setPreference(EXPAND_SUBS_KEY, (expand ? "y" : "n"));
			}
			for (int i = 0; i < account.getSubAccountCount(); ++i)
			{
				setAllExpanded(account.getSubAccount(i),expand);
			}
		}
	}
	
	private boolean isDebtAccount(Account acct)
	{
		switch(acct.getAccountType()) {
			case CREDIT_CARD:
			case LOAN:
				return true;
			default:
				return false;
		}
	}
	
	public void refresh()
	{
		if (this.acctView.getMDGUI().getSuspendRefreshes()) 
			return;
		
		this.listPanel.removeAll();
		
		if (getRoot() == null) 
			return;

		this.dec = this.acctView.getMDGUI().getMain().getPreferences()
													.getDecimalChar();

		CurrencyType baseCurr = getRoot().getCurrencies().getBaseType();
		DebtAmountWrapper amountWrapper = new DebtAmountWrapper();
		this.currentRow = 0;

		String iconPath = COLLAPSED;
		if (this.expanded)
			iconPath = EXPANDED;
		
		addHeaderRow(listPanel);
		this.headerLabel.setIcon(this.acctView.getMDGUI().getImages()
														.getIcon(iconPath));

		this.tooManyAccounts = false;
		if (this.acctView.getHierarchyView() == HierarchyView.FLATTEN 
			|| this.acctView.getAcctComparator() != null)
		{
			addAccounts(this.acctView.getAccounts(getRoot().getRootAccount()), amountWrapper);

		}
		else
		{
			addAccounts(this.getRoot().getRootAccount(), amountWrapper,
									true, this.expanded, this.acctView.getAccountTypes());
		}
		addTotalsRow(listPanel, baseCurr, amountWrapper);
		
		if (this.tooManyAccounts)
		{
			this.listPanel.add(
					new JLabel(this.acctView.getMDGUI().getStr("too_many_accts_wtype")),
								GridC.getc().xy(1, this.currentRow++).wx(1.0F).colspan(2).fillboth());
		}

		if (!(amountWrapper.hasValidAccts))
		{
			setVisible(false);
		}
		else
		{
			setHeaderLabels(baseCurr, amountWrapper);
		}

		Container child = this;
		Container parent = getParent();
		int counter = 0;
		while ((counter++ < 1) && (parent != null))
		{
			child = parent;
			parent = child.getParent();
		}
		child.validate();
		repaint();
	}

	protected void setHeaderLabels(CurrencyType baseCurr, DebtAmountWrapper amountWrapper)
	{
		setVisible(true);
		this.headerLabel.setText(this.acctView.toString());
		this.balTypeLabel.setText(this.acctView.getMDGUI().getStr(getBalanceType().getResourceKey()));

		if (this.expanded)
		{
			this.listPanel.add(Box.createVerticalStrut(10), GridC.getc()
					.xy(0, this.currentRow));
		}

		this.totalValLabel.setText(baseCurr.formatFancy(
				amountWrapper.getAmount(), this.dec));
		if (amountWrapper.getAmount() < 0L)
			this.totalValLabel.setForeground(this.acctView
					.getMDGUI().getColors().negativeBalFG);
		else
		{
			this.totalValLabel.setForeground(this.acctView
					.getMDGUI().getColors().positiveBalFG);
		}
	}
	
	protected void addAcctRow(Account target, String sharesLabel,
			String balLabel, long amt)
	{
		String acctLabel = target.getAccountName();
		int indentDepth = target.getDepth();
		StringBuffer sb = new StringBuffer();
		for (int i = 1; i < indentDepth; ++i)
			sb.append("   ");
		sb.append(acctLabel);
		if (sb.length() <= 0) sb.append(" ");
		acctLabel = sb.toString();

		JLinkLabel label1 = new JLinkLabel(acctLabel, target, 2);
		JLinkLabel label2 = (sharesLabel != null) ? new JLinkLabel("  "
				+ sharesLabel, target, 4) : null;

		JLinkLabel label3 = new JLinkLabel("  " + balLabel, target, 4);

		label1.addLinkListener(this);
		if (label2 != null) label2.addLinkListener(this);
		label3.addLinkListener(this);

		if (amt < 0L)
		{
			Color negFGColor = this.acctView.getMDGUI().getColors().negativeBalFG;
			if (label2 != null) label2.setForeground(negFGColor);
			label3.setForeground(negFGColor);
		}

		if (this.currentRow % 2 == 0)
		{
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

		if (label2 != null)
		{
			this.listPanel.add(label1, GridC.getc(1, this.currentRow).wx(1.0F)
					.fillboth());

			this.listPanel.add(label2, GridC.getc(2, this.currentRow)
					.fillboth());
			this.listPanel.add(label3, GridC.getc(3, this.currentRow)
					.fillboth());
		}
		else
		{
			this.listPanel.add(label1, GridC.getc(1, this.currentRow).wx(1.0F)
					.fillboth().colspan(2));
			this.listPanel.add(label3, GridC.getc(3, this.currentRow)
					.fillboth());
		}
		this.currentRow += 1;
	}

	private double getRate(Account account)
	{
		switch(account.getAccountType()) {
			case CREDIT_CARD:
				return account.getAPRPercent();
			case LOAN:
				return account.getInterestRate();
			default:
				return 0;
		}
	}
	
	private final void addAccounts(Account parentAcct, DebtAmountWrapper aw,
			boolean filter, boolean showIt, List<Account.AccountType> acctTypes)
	{
		//Move this block to BetterInvestmentAccountsHomePageView
//		long parentBalance = DMDebtAccountView.getBalance(this.balanceType,
//				parentAcct);
//		if ((showIt) && (parentAcct.getAccountType() == 3000) //Investment
//				&& (parentBalance != 0L))
//		{
//			addAcctRow(
//					this.acctView.getMDGUI().getStr(
//							"invst_cash_balance"),
//					null,
//					parentAcct.getCurrencyType().formatFancy(parentBalance,
//							this.dec), parentBalance,
//					parentAcct.getDepth() + 1, parentAcct);
//		}

		ArrayList<Account> subAccounts = new ArrayList(parentAcct.getSubAccounts());
//		List<Integer> accountTypeList = Arrays.asList(acctTypes);
		
		for (Account account: subAccounts)
		{
			boolean showAccount = showIt;

			if (filter && !acctTypes.contains(account.getAccountType()))
			{
				continue;
			}

			CurrencyType currency = account.getCurrencyType();
			long totalBal = getAccountValue(account, currency);
			if (aw != null)
			{
				aw.add( CurrencyTable.convertValue(DebtAccountView.getBalance(getBalanceType(), account), currency,
																					 currency), getRate(account));

				aw.scannedAccount(account);
			}

			this.tooManyAccounts = ((this.tooManyAccounts) || (this.currentRow > 150));

			if (((totalBal == 0L) && (account.getHideOnHomePage()))
					|| (account.getAccountOrParentIsInactive()))
			{
				showAccount = false;
			}
			if ((showAccount) && (!(this.tooManyAccounts)))
			{
				String sharesStr = null;
				String amtStr = currency.formatFancy(totalBal, this.dec);
				if (currency.getCurrencyType() == CurrencyType.Type.SECURITY)
				{
					sharesStr = amtStr;
					CurrencyType relCurr = AccountUtils.getRelCurrency(currency, parentAcct);
					long value = CurrencyUtil.convertValue(totalBal, currency,
							relCurr);
					amtStr = relCurr.formatFancy(value, this.dec);
				}

				addAcctRow(account, sharesStr, amtStr, totalBal);
			}

			int origRow = this.currentRow;
			boolean showSubAccounts = account.getParameter(
					getSubAcctExpansionKey(), "y").equals("y");

			JLinkLabel acctExpandLabel = null;
			
			addAccounts(account, aw, false, (showIt
					&& showSubAccounts), acctTypes);
			
			if (showSubAccounts)
			{
				if (showAccount && this.currentRow != origRow
								&& !(this.tooManyAccounts))
					acctExpandLabel = new JLinkLabel("- ", account, SwingConstants.LEFT);
			}
			else if (showAccount && !this.tooManyAccounts)
			{
				acctExpandLabel = new JLinkLabel("+ ", account, SwingConstants.LEFT);
			}

			if (acctExpandLabel != null)
			{
				acctExpandLabel.setDrawUnderline(false);
				acctExpandLabel.addLinkListener(getExpander());
				acctExpandLabel.setBorder(expandLinkBorder);

				this.listPanel.add(acctExpandLabel,
						GridC.getc().xy(0, origRow - 1));
			}
		}
	}
	
	private final void addAccounts(List<Account> subAccounts, DebtAmountWrapper aw)
	{		
		for (Account account: subAccounts)
		{

			CurrencyType currency = account.getCurrencyType();
			long totalBal = getAccountValue(account, currency);
			
			if (aw != null)
			{
				aw.add(CurrencyTable.convertValue(DebtAccountView.getBalance(getBalanceType(), account), 
												currency, currency), getRate(account));

				aw.scannedAccount(account);
			}

			this.tooManyAccounts = ((this.tooManyAccounts) || (this.currentRow > 150));

			if (((totalBal == 0L) && (account.getHideOnHomePage()))
					|| (account.getAccountOrParentIsInactive()))
			{
				continue;
			}
			if (!(this.tooManyAccounts))
			{
				String sharesStr = null;
				String amtStr = currency.formatFancy(totalBal, this.dec);
				if (currency.getCurrencyType() == CurrencyType.Type.SECURITY)
				{
					sharesStr = amtStr;
					CurrencyType relCurr = AccountUtils.getRelCurrency(currency, account.getParentAccount());
					long value = CurrencyUtil.convertValue(totalBal, currency,
							relCurr);
					amtStr = relCurr.formatFancy(value, this.dec);
				}

				addAcctRow(account, sharesStr, amtStr,
						totalBal);
			}

		}
	}
	
	public final long getAccountValue(Account account, CurrencyType currency)
	{
		CurrencyType currency2 = account.getCurrencyType();
		long realBalance = CurrencyTable.convertValue(
				DebtAccountView.getBalance(getBalanceType(), account),
				currency2, currency);

		for (int i = 0; i < account.getSubAccountCount(); ++i)
		{
			realBalance += getAccountValue(account.getSubAccount(i), currency);
		}
		return realBalance;
	}

	@Override
	public void linkActivated(Object link, InputEvent evt)
	{
		if (link instanceof Account)
			if ((evt.getModifiers() & MoneydanceGUI.ACCELERATOR_MASK) != 0)
				this.acctView.getMDGUI().selectAccountNewWindow(
						(Account) link);
			else
				this.acctView.getMDGUI().selectAccount((Account) link);
	}

	@Override
	public void mousePressed(MouseEvent evt)
	{
		if (evt.getSource() == this.balTypeLabel) showBalanceTypePopup();
	}

	@Override
	public void mouseReleased(MouseEvent evt)
	{
	}

	@Override
	public void mouseExited(MouseEvent evt)
	{
	}

	@Override
	public void mouseEntered(MouseEvent evt)
	{
	}

	@Override
	public void mouseClicked(MouseEvent evt)
	{
		Object src = evt.getSource();
		if (src == this.headerLabel) toggleSectionExpanded();
	}
	
	protected void showBalanceTypePopup()
	{
		JPopupMenu btMenu = new JPopupMenu();
		BalanceType[] balanceTypes =  {BalanceType.BALANCE, BalanceType.CURRENT_BALANCE, BalanceType.CLEARED_BALANCE};
		for (BalanceType type: balanceTypes) {
			final BalanceType balType = type;
			btMenu.add(new MDAction(this.acctView.getMDGUI(), type.getResourceKey()) {
				public void actionPerformed(ActionEvent evt) {
					boolean different = (balType != getBalanceType());
					prefs.setSetting(acctView.getBalanceTypePref(), balType.ordinal());
					if (!(different)) return;
					setBalanceType(balType);
					refresh();
				}
			});
		}
		
		btMenu.show(this.balTypeLabel, 0, this.headerLabel.getHeight());
	}

	private void toggleSectionExpanded()
	{
		this.expanded = (!(this.expanded));
		this.prefs.setSetting(this.acctView.getSectionExpandedPref(),
				this.expanded);
		refresh();
	}

	@Override
	public void currencyTableModified(CurrencyTable currencyTable)
	{
		refresh();
	}

	@Override
	public void accountModified(Account account)
	{
		if (this.acctView.includes(account.getAccountType())) // == this.acctView.getAccountType())
			refresh();
	}

	@Override
	public void accountBalanceChanged(Account account)
	{
		if (account.getAccountType() == this.acctView.getAccountType())
			refresh();
	}

	@Override
	public void accountDeleted(Account parentAccount, Account deletedAccount)
	{
		Account.AccountType acctType = this.acctView.getAccountType();
		if ((parentAccount.getAccountType() != acctType)
				&& (deletedAccount.getAccountType() != acctType)) return;
		refresh();
	}

	@Override
	public void accountAdded(Account parentAccount, Account newAccount)
	{
		Account.AccountType acctType = this.acctView.getAccountType();
		if ((parentAccount.getAccountType() != acctType)
				&& (newAccount.getAccountType() != acctType)) return;
		refresh();
	}

	private class AccountExpander implements JLinkListener
	{

		public AccountExpander()
		{
			super();
		}
		
		@Override
		public void linkActivated(Object link, InputEvent evt)
		{
			Account acct = (Account) link;
			if (acct.getParameter(getSubAcctExpansionKey(), "y").equals("y"))
				acct.setPreference(getSubAcctExpansionKey(), "n");
			else
				acct.setPreference(getSubAcctExpansionKey(), "y");
			DebtViewPanel.this.refresh();
		}
	}

	
	/**
	 * @return the dec
	 */
	public char getDec()
	{
		return dec;
	}

	
	/**
	 * @param dec the dec to set
	 */
	public void setDec(char dec)
	{
		this.dec = dec;
	}

	
	/**
	 * @return the acctView
	 */
	public DebtAccountView getAcctView()
	{
		return acctView;
	}
	
	public String getSubAcctExpansionKey()
	{
		return EXPAND_SUBS_KEY;
	}

	
	/**
	 * @return the balanceType
	 */
	public BalanceType getBalanceType()
	{
		return balanceType;
	}

	
	/**
	 * @param balanceType the balanceType to set
	 */
	public void setBalanceType(BalanceType balanceType)
	{
		this.balanceType = balanceType;
	}
}