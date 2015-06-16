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
import com.moneydance.modules.features.debtinsights.AccountUtils;
import com.moneydance.modules.features.debtinsights.DebtAmountWrapper;
import com.moneydance.modules.features.debtinsights.Strings;
import com.moneydance.modules.features.debtinsights.creditcards.CreditLimitType;
import com.moneydance.modules.features.debtinsights.model.BetterCreditCardAccount;
import com.moneydance.modules.features.debtinsights.model.BetterLoanAccount;
import com.moneydance.modules.features.debtinsights.model.DebtAccount;
import com.moneydance.modules.features.debtinsights.ui.acctview.DebtAccountView;
import com.moneydance.modules.features.debtinsights.ui.acctview.HierarchyView;
import com.moneydance.modules.features.debtinsights.ui.acctview.IconToggle;
import com.moneydance.modules.features.debtinsights.ui.acctview.SortView;
import com.moneydance.modules.features.debtinsights.ui.viewpanel.DebtViewPanel;


public class DebtManagerPanel extends DebtViewPanel
{
	private MDColors colors;
	private static final CreditLimitType creditLimitType = CreditLimitType.CREDIT_LIMIT;
	private static final Account.AccountType[] acctTypes = { Account.AccountType.CREDIT_CARD,
																													 Account.AccountType.LOAN };
	

	public DebtManagerPanel(DebtAccountView ccAccountView)
	{
		super(ccAccountView, acctTypes);
		setBorder(new CompoundBorder(new BevelBorder(BevelBorder.LOWERED), 
										new EmptyBorder(12,12,12,12)));
		setBackground(colors.homePageBG);
		setOpaque(true);
		activate();
		
	}
	
	/* (non-Javadoc)
	 * @see com.moneydance.modules.features.debtinsights.CreditCardViewPanel#init()
	 */
	@Override
	protected void init()
	{
		super.init();
		this.colors = this.acctView.getMDGUI().getColors();
	}
	

	@Override
	protected void addAcctRow(Account account, String sharesStr,
	        String balanceStr, long amt )
	{
		switch(account.getAccountType()) {
			case CREDIT_CARD:
			case LOAN:
				addAcctRow(account, amt);
			default:
				return;
		}
	}
	
//	private enum COL { LABEL, CARD_NUM, PMT, PMT_FLAG, INT_PMT, AMT, AMT_FLAG, LIMIT, APR, APR_FLAG; }
	
	private void addAcctRow(Account acct, long amt)
	{
		String acctLabel = acct.getAccountName();
		
		if (this.acctView.getHierarchyView() != HierarchyView.FLATTEN 
			&& this.acctView.getAcctComparator() == null)
		{
			int indentDepth = acct.getDepth();
	
			StringBuffer sb = new StringBuffer();
			for (int i = 1; i < indentDepth; ++i)
				sb.append(THREE_SPACE);
			sb.append(acctLabel);
			if (sb.length() <= 0) sb.append(SINGLE_SPACE);
			acctLabel = sb.toString();
		}
		
		CurrencyType currency = acct.getCurrencyType();
		CurrencyType relCurr = AccountUtils.getRelCurrency(currency, acct.getParentAccount());
		long pmt = CurrencyUtil.convertValue(DebtAccount.getNextPayment(acct), currency, relCurr);
		long intPmt = CurrencyUtil.convertValue(DebtAccount.getInterestPayment(acct), currency, relCurr);
		Long limit = null;
		String cardNumber = null;
		

//		Name	Acct #	Payment		Interest Balance		Limit	APR		When
		Object[] labels = {	null, acctLabel, cardNumber, pmt, null, intPmt, amt, null, limit, 
												 DebtAccount.getAPR(acct), null };
		Map<Header, Object> valMap = getValueMap(acct, labels, currency, relCurr);
		
		
		int i=0;
		for (Header col: Header.values())
		{
			if (i == 0)
			{
				i++;
				continue;
			}
			Object label = valMap.get(col);
			if (label == null || label.toString().length() == 0) label = " ";
			
			Color bg = (this.currentRow % 2 == 0 ? this.colors.homePageAltBG : this.colors.homePageBG);
			
			JLabel jLbl = null;
			
			if (label instanceof JLabel)
			{
				jLbl = (JLabel) label;
				jLbl.setBackground(bg);
				
			}
			else
			{
				jLbl = makeJLinkLabel(label, acct, relCurr, bg, col.border);
			}
			
			
			GridC gridC = GridC.getc().xy(i++,this.currentRow).wx(1f).fillx();
			gridC =  (label instanceof String ? gridC.west() : gridC.east());

			this.listPanel.add(jLbl, gridC);
//			if (label instanceof ImageIcon)
//			{
//				jLbl.addMouseListener(new FlagListener(listPanel, jLbl, "SHOW MSG HERE"));
//			}
		}

		this.currentRow++;
	}

	private static final long days90 = 90l * 24l * 3600l * 1000l;
	
	private Map<Header, Object> getValueMap(Account acct, Object[] labels, CurrencyType currency, CurrencyType relCurr)
	{
		Map<Header, Object> map = new HashMap<Header, Object>();
		
		for (int i=0; i < labels.length; i++)
		{
			map.put(Header.values()[i], labels[i]);
		}
		
		map.put(Header.PMT_FLG, (Math.abs((Long) map.get(Header.PAYMENT)) < Math.abs((Long) map.get(Header.INTEREST)) ? Flag.RED.makeFlag("Payment is less than accruing interest") : null));
		if(acct.getAccountType()== Account.AccountType.CREDIT_CARD)
		{
			map.put(Header.LIMIT, CurrencyUtil.convertValue(BetterCreditCardAccount.getCreditLimit(acct), currency, relCurr));
			map.put(Header.ACCT_NUM, acct.getCardNumber());

			float halfLimit = -CurrencyUtil.convertValue(BetterCreditCardAccount.getCreditLimit(acct), currency, relCurr)/2;
			map.put(Header.BAL_FLG, ((Long) map.get(Header.BALANCE) < halfLimit ? Flag.YELLOW.makeFlag("Credit used is more than 50% of credit Limit") : null));

			Date changeDate = BetterCreditCardAccount.getRateChangeDate(acct);
			if (changeDate != null && changeDate.getTime() > 0)
			{
				long t = new Date().getTime();
				long cd = changeDate.getTime();
				boolean aprChange = cd > t && cd - t < days90;
				map.put(Header.APR_FLG, (aprChange ? Flag.YELLOW.makeFlag("APR will change on " + changeDate) : null));
			}
		}
		return map;
	}
	
	private JLinkLabel makeJLinkLabel(Object value, Account acct, CurrencyType relCurr, Color bg, Border border )
	{
		String valStr = value.toString();
		int align = (value instanceof String ? SwingConstants.LEFT : SwingConstants.RIGHT);
		Color fgColor = Color.black;

		if (value instanceof Long)
		{
			valStr = relCurr.formatFancy((Long) value, this.dec);
			
			if ((Long) value < 0)
			{
				fgColor = this.colors.negativeBalFG;
			}
		}
		else if (value instanceof Double || value instanceof Float)
		{
			valStr += "%";
		}
		JLinkLabel lbl = new JLinkLabel(valStr, acct, align);
		lbl.setForeground(fgColor);
		lbl.setBorder(border);
		lbl.addLinkListener(this);
		lbl.setDrawUnderline(false);
		lbl.setOpaque(true);				
		lbl.setBackground(bg);
		
		if (hasSubAccounts(acct))
		{
			Font f = lbl.getFont();
			lbl.setFont(f.deriveFont(Font.BOLD, f.getSize()+1));
		}

		return lbl;
	}
	
	private boolean hasSubAccounts(Account acct)
	{
		return acct.getSubAccountCount() > 0;
	}
	
	@Override
	protected void addLabelsToHeader()
	{
//		-  U+2796
//		+  U+2795	
//		0  U+20E0
//		String[] headers = {"\u20E0", "Name","Acct #","Payment","Interest", "Balance","Limit","APR"}; //,"When"};
//		int[] align = {SwingConstants.CENTER, SwingConstants.LEFT,SwingConstants.LEFT,SwingConstants.RIGHT,SwingConstants.RIGHT,SwingConstants.RIGHT,SwingConstants.RIGHT};
		Font font = getFont();
		font = new Font(font.getName(), Font.BOLD, font.getSize() + 2);

		Header sortHeader = (acctView.getAcctComparator() != null ? acctView.getAcctComparator().getHeader() : null);
		
		int i=0;
		for (Header header: Header.values())
		{
			IconToggle toggle = (IconToggle) header.icon;
			toggle = (toggle != null ?  toggle.getState(acctView) : null);
			String sortLbl = (toggle != null ? ((IconToggle) toggle.getNextState()).getLabel() : Strings.BLANK);
			String labelStr = header.label + sortLbl;
			
			JLabel lbl = new JLabel(labelStr, header.align);
			if (toggle != null && (header == sortHeader || !(toggle instanceof SortView)))
			{
				lbl.setIcon(toggle.getIcon());
				lbl.setHorizontalTextPosition(SwingConstants.LEADING);
			}
			lbl.setFont(font);
			lbl.setBorder(header.border);
			lbl.addMouseListener(header.getListener(lbl, header, this));
			lbl.setToolTipText(header.tooltip);
			
			listPanel.add(lbl,GridC.getc().xy(i++,0).fillx());
		}
		
		this.currentRow++;	
	}
	
	@Override
	protected void setHeaderLabels(CurrencyType baseCurr, 
									DebtAmountWrapper amountWrapper)
	{
	}
	@Override
	protected void addTotalsRow(JPanel totalPanel, CurrencyType baseCurr,
								DebtAmountWrapper totalDebt)
	{

		Font font = getFont();
		font = new Font(font.getName(), Font.BOLD, font.getSize() + 2);
		
		int i=0;
		for (Header header: Header.values())
		{
			String labelStr = getValueFor(header.totAccessor, baseCurr, totalDebt);
			
			JLabel lbl = new JLabel(labelStr, header.align);
			lbl.setFont(font);
			lbl.setBorder(header.border);
			listPanel.add(lbl,GridC.getc().xy(i++,this.currentRow).fillx());
		}
	}

	private static final Class<?>[] params = {AccountBook.class, DebtAmountWrapper.class};
	private String getValueFor(String methodName, CurrencyType baseCurr,
								DebtAmountWrapper totalDebt)
	{
		try
		{
			Method m = AccountUtils.class.getMethod(methodName, params);
			Object[] args = {getRoot(), totalDebt};
			Object o = m.invoke(null, args);
			if (o instanceof Long)
			{
				long value = (Long) o;
				return baseCurr.formatFancy(value, this.dec);
			}
			else if (o instanceof Double || o instanceof Float)
			{
				return o.toString() + "%";
			}
		}
		catch (SecurityException e)
		{
			System.err.println("Error: " + e);
		}
		catch (NoSuchMethodException e)
		{
			return methodName;
		}
		catch (IllegalArgumentException e)
		{
			System.err.println("Error: " + e);
		}
		catch (IllegalAccessException e)
		{
			System.err.println("Error: " + e);
		}
		catch (InvocationTargetException e)
		{
			System.err.println("Error: " + e);
		}
		
		return methodName;
	}

	@Override
	protected JLabel getAccountTypeSpecificLabel()
	{
		if (DebtManagerPanel.creditLimitType != null)
			return DebtManagerPanel.creditLimitType.getTotal(this, getRoot());
		
		return new JLabel(" ");
	}

	
	/**
	 * @return the creditlimittype
	 */
	public static CreditLimitType getCreditLimitType()
	{
		return creditLimitType;
	}
}
