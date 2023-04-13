/*
 * CreditCardViewPanel.java
 * 
 * Created on Sep 9, 2013
 * Last Modified: $Date: $
 * Last Modified By: $Author: $
 * 
 * 
 */

package com.moneydance.modules.features.debtinsights.ui.viewpanel;

import java.awt.Color;
import java.awt.Font;
import java.awt.event.MouseEvent;

import javax.swing.*;
import javax.swing.border.Border;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.awt.AwtUtil;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.modules.features.debtinsights.DebtAmountWrapper;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;
import com.moneydance.modules.features.debtinsights.creditcards.CreditCardLimitMenuAction;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.ui.acctview.CreditCardAccountView;
import com.moneydance.modules.features.debtinsights.ui.acctview.DebtAccountView;

public class CreditCardViewPanel extends DebtViewPanel
{
	protected JLabel creditLimitTypeLbl;
	private CreditLimitType creditLimitType; // = CreditLimitType.CREDIT_LIMIT;
	
	protected CreditCardAccountView ccAccountView;

	protected static final Border[] borders = {
			DebtViewPanel.nameBorder,
			DebtViewPanel.amountBorder,
			DebtViewPanel.amountBorder};

	public CreditCardViewPanel(DebtAccountView ccAccountView, Account.AccountType... acctTypes)							// noqa
	{
		super(true, ccAccountView);
		setBorder(MoneydanceLAF.homePageBorder);
	}

	@Override
	protected void init()
	{
		super.init();
		this.ccAccountView = (CreditCardAccountView) this.acctView;

		setCreditLimitType(CreditLimitType.fromInt(prefs.getIntSetting(Main.EXTN_MD_CCLIMIT_PREF_KEY,
				CreditLimitType.CREDIT_LIMIT.ordinal())));
	}

	@Override
	protected void addAcctRow(Account account, String sharesStr, String balanceStr, long amt, long balanceForCreditComponent)
	{
		Util.logConsole(true, "widget: addAcctRow()");

		String acctLabel = account.getAccountName();
		int indentDepth = account.getDepth();

		StringBuilder sb = new StringBuilder();
		for (int i = 1; i < indentDepth; ++i)
			sb.append(THREE_SPACE);
		sb.append(acctLabel);
		if (sb.length() <= 0) sb.append(SINGLE_SPACE);
		acctLabel = sb.toString();

		JLinkLabel nameLbl = new JLinkLabel(acctLabel, account, SwingConstants.LEFT);
		JComponent creditLimitDisplay = getCreditLimitType().getDisplayComponent(this, account, balanceForCreditComponent);
//		JComponent creditLimitDisplay = getCreditLimitType().getDisplayComponent(this, account, amt);
		if (creditLimitDisplay != null) {
			creditLimitDisplay.setFont(this.acctView.getMDGUI().getFonts().mono);
		}

		JLinkLabel balanceLbl = new JLinkLabel(balanceStr, account, SwingConstants.RIGHT);
		balanceLbl.setFont(this.acctView.getMDGUI().getFonts().mono);

		JComponent[] labels = {nameLbl, creditLimitDisplay, balanceLbl};
		
		if (amt < 0L)
		{
			Color negFGColor = this.acctView.getMDGUI().getColors().negativeBalFG;
			balanceLbl.setForeground(negFGColor);
		}
		if (amt > 0L && Main.getWidgetEnhancedColors())
		{
			Color posColor = Util.getPositiveGreen();
			balanceLbl.setForeground(posColor);
		}

		for (int i=0; i < labels.length; i++)
		{
			if (labels[i] == null) continue;
			
			if (labels[i] instanceof JLinkLabel)
			{
				((JLinkLabel) labels[i]).addLinkListener(this);
				((JLinkLabel) labels[i]).setDrawUnderline(false);
			}
//			if (this.currentRow % 2 == 0)
//			{
//				Color bg = this.acctView.getMDGUI().getColors().homePageAltBG;
//				labels[i].setOpaque(true);
//				labels[i].setBackground(bg);
//			}

			labels[i].setBorder(borders[i]);;
			
			GridC gridC = GridC.getc().xy(i+1, this.currentRow);
			if (i == 0)
				gridC = gridC.wx(0.6F).fillx().west();
			else
				gridC = gridC.wx(0.2F).fillx().east();

			this.listPanel.add(labels[i], gridC);
		}

		this.currentRow++;
	}

	
	@Override
	protected void addLabelsToHeader()
	{
		listPanel.add(this.headerLabel, GridC.getc().xy(0, 0).wx(0.6F).colspan(2).west());

		this.creditLimitTypeLbl = new JLabel(" ", SwingConstants.RIGHT);
		this.creditLimitTypeLbl = new JLabel(" ", SwingConstants.RIGHT);
		this.creditLimitTypeLbl.setFont(this.acctView.getMDGUI().getFonts().defaultText);
		this.creditLimitTypeLbl.setBorder(amountBorder);
		this.creditLimitTypeLbl.setForeground(this.acctView.getMDGUI().getColors().secondaryTextFG);
		this.creditLimitTypeLbl.setHorizontalTextPosition(SwingConstants.RIGHT);
		this.creditLimitTypeLbl.setIcon(this.acctView.getMDGUI().getImages().getIcon(SELECTOR));
		this.creditLimitTypeLbl.addMouseListener(this);
		listPanel.add(this.creditLimitTypeLbl, GridC.getc().xy(2, 0).wx(0.2F).fillx().east());

		listPanel.add(this.balTypeLabel, GridC.getc().xy(3, 0).wx(0.2F).fillx().east());
		
		this.currentRow++;	
	}
	
	@Override
	protected void setHeaderLabels(CurrencyType base,  DebtAmountWrapper amountWrapper)
	{
		super.setHeaderLabels(base, amountWrapper);
//		if (this.ccAccountView ==null) this.ccAccountView = (CreditCardAccountView) acctView;
		this.creditLimitTypeLbl.setText(getCreditLimitType().getMenuName()); 
	}
	

	@Override
	protected JLabel getAccountTypeSpecificLabel()
	{
		return getCreditLimitType().getTotal(this,getRoot());
	}


	private void showCreditLimitTypePopup()
	{
		JPopupMenu btMenu = new JPopupMenu();
				
		for (CreditLimitType type: CreditLimitType.values())
		{
			CreditCardLimitMenuAction action = new CreditCardLimitMenuAction(type, this);
			JMenuItem option = new JMenuItem(action);
			
			if (type.ordinal() == getCreditLimitType().ordinal())
			{
				option.setSelected(true);
			}

			btMenu.add(option);
		}
		
		btMenu.show(this.creditLimitTypeLbl, 0, this.headerLabel.getHeight());
	}


	@Override
	public void mousePressed(MouseEvent evt)
	{
		Util.logConsole(true, "Mouse: mousePressed...." + evt.getSource());
		if (evt.getSource() == this.balTypeLabel)
		{
			showBalanceTypePopup();
			return;
		}
		
		if (evt.getSource() == this.creditLimitTypeLbl) 
		{
			showCreditLimitTypePopup();
		}
	}
	
	/**
	 * @return the ccAccountView
	 */
	public CreditCardAccountView getCcAccountView()
	{
		return ccAccountView;
	}
	
	@Override
	public String getSubAcctExpansionKey()
	{
        Util.logConsole(true, "^^ CCVP.getSubAcctExpansionKey() returning: " + Main.EXPAND_SUBS_KEY);
		return Main.EXPAND_SUBS_KEY;
	}

	@Override
	protected void showBalanceTypePopup() {

		Util.logConsole(true, "Inside: CCVP.showBalanceTypePopup() - Super'ing....");
		super.showBalanceTypePopup();
		if (this.getCcAccountView() != null) {
			this.getCcAccountView().extnContext.creditCardReportDispose();
//			this.getCcAccountView().extnContext.creditCardReportRefresh();
		}
	}

	/**
	 * @return the creditLimitType
	 */
	public CreditLimitType getCreditLimitType()
	{
		return this.creditLimitType;
	}

	
	/**
	 * @param creditLimitType the creditLimitType to set
	 */
	public void setCreditLimitType(CreditLimitType creditLimitType)
	{
		this.creditLimitType = creditLimitType;
	}

}
