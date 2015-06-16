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

import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import javax.swing.SwingConstants;
import javax.swing.border.Border;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.modules.features.debtinsights.DebtAmountWrapper;
import com.moneydance.modules.features.debtinsights.creditcards.CreditCardLimitMenuAction;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.ui.acctview.CreditCardAccountView;
import com.moneydance.modules.features.debtinsights.ui.acctview.DebtAccountView;

public class CreditCardViewPanel extends DebtViewPanel
{
//	private static final Logger log = LoggerFactory.getLogger(CreditCardViewPanel.class);
	protected JLabel 	creditLimitTypeLbl;
	protected JLabel creditTotalLbl;
	private CreditLimitType creditLimitType; // = CreditLimitType.CREDIT_LIMIT;
	

	protected CreditCardAccountView ccAccountView;

	protected static final Border[] borders = {	DebtViewPanel.nameBorder,
																							 DebtViewPanel.amountBorder,
																							 DebtViewPanel.amountBorder};
	
	public CreditCardViewPanel(DebtAccountView ccAccountView,
	        				Account.AccountType... acctTypes)
	{
		super(ccAccountView);
	}

	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.BetterViewPanel#activate()
	 */
	@Override
	protected void init()
	{
		super.init();
		this.ccAccountView = (CreditCardAccountView) this.acctView;
//		if (getCreditLimitType() == null) setCreditLimitType(CreditLimitType.CREDIT_LIMIT);

		setCreditLimitType(CreditLimitType.fromInt(	prefs
													.getIntSetting (this.ccAccountView.creditLimitTypePref, 
																	CreditLimitType.CREDIT_LIMIT.ordinal())));
		
//		setCreditLimitType((prefType != null ?  prefType : CreditLimitType.CREDIT_LIMIT));
	}

	@Override
	protected void addAcctRow(Account account, String sharesStr,
	        					String balanceStr, long amt)
	{
    //BetterCreditCardAccount acct = new BetterCreditCardAccount(account);
		String acctLabel = account.getAccountName();
		int indentDepth = account.getDepth();

		StringBuffer sb = new StringBuffer();
		for (int i = 1; i < indentDepth; ++i)
			sb.append(THREE_SPACE);
		sb.append(acctLabel);
		if (sb.length() <= 0) sb.append(SINGLE_SPACE);
		acctLabel = sb.toString();

		JLinkLabel nameLbl = new JLinkLabel(acctLabel, account, SwingConstants.LEFT);
		
		JComponent creditLimitDisplay = getCreditLimitType().getDisplayComponent(this, account, amt);
		
		JLinkLabel balanceLbl = new JLinkLabel(balanceStr, account, SwingConstants.RIGHT);

		JComponent[] labels = {nameLbl, creditLimitDisplay, balanceLbl};
		
		if (amt < 0L)
		{
			Color negFGColor = this.acctView.getMDGUI().getColors().negativeBalFG;
			balanceLbl.setForeground(negFGColor);
		}

		for (int i=0; i < labels.length; i++)
		{
			if (labels[i] == null) continue;
			
			if (labels[i] instanceof JLinkLabel)
			{
				((JLinkLabel) labels[i]).addLinkListener(this);
				((JLinkLabel) labels[i]).setDrawUnderline(false);
			}
			if (this.currentRow % 2 == 0)
			{
				Color bg = this.acctView.getMDGUI().getColors().homePageAltBG;
				labels[i].setOpaque(true);				
				labels[i].setBackground(bg);
			}
			labels[i].setBorder(borders[i]);
			
			GridC gridC = GridC.getc().xy(i+1,this.currentRow);
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
		Font font = getFont();
		font = new Font(font.getName(), 1, font.getSize() + 2);

		this.creditLimitTypeLbl = new JLabel(" ", SwingConstants.RIGHT);
		this.creditLimitTypeLbl.setFont(font);
		this.creditLimitTypeLbl.setHorizontalTextPosition(SwingConstants.LEADING);
		this.creditLimitTypeLbl.setIcon(this.acctView.getMDGUI()
				.getImages()
				.getIcon(SELECTOR));
		this.creditLimitTypeLbl.addMouseListener(this);

		listPanel.add(this.headerLabel, 
				GridC.getc().xy(0, 0).wx(0.6F).colspan(2).west());
		listPanel.add(this.creditLimitTypeLbl, GridC.getc().xy(2, 0).wx(0.2F).fillx().east());
		listPanel.add(this.balTypeLabel, GridC.getc().xy(3, 0).wx(0.2F).fillx().east());
		
		this.currentRow++;	
	}
	
	@Override
	protected void setHeaderLabels(CurrencyType baseCurr, 
									DebtAmountWrapper amountWrapper)
	{
		super.setHeaderLabels(baseCurr, amountWrapper);
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
		return "gui_expand_subaccts";
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
