/*
 *  Copyright (c) 2014, Michael Bray. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */ 
package com.moneydance.modules.features.loadsectrans;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.util.SortedSet;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.GridC;

public class GenerateWindow extends JPanel {
	private SortedSet<SecLine> setLine;
	private Account acct;
	private GenerateTable transTab;
	private GenerateTableModel transModel;
	private InvestFields investFields;
	private JPanel panTop;
	private JPanel panMid;
	private JPanel panBot;
	private JTextField txtAccount;
	private MyCheckBox select;
	private JButton btnClose;
	private JButton btnSave;
	private MoneydanceUI mdGUI;
	private com.moneydance.apps.md.controller.Main mdMain;
	private JButton helpBtn;

	private JScrollPane transScrollPane;
	private Parameters2 params;
	public GenerateWindow(SortedSet<SecLine> setLine, Account acct, Parameters2 params) {
		mdMain = com.moneydance.apps.md.controller.Main.mainObj;
		mdGUI = mdMain.getUI();
		this.setLine = setLine;
		this.acct = acct;
		this.params = params;
		transModel = new GenerateTableModel();
		transTab = new GenerateTable(transModel);
		generateTrans();
		/*
		 * Start of screen
		 * 
		 * Top Panel Account
		 */
		this.setLayout(new BorderLayout());
		panTop = new JPanel (new GridBagLayout());
		GridBagConstraints gbc_label = new GridBagConstraints();
		gbc_label.gridx = 0;
		gbc_label.gridy = 0;
		JLabel lbAccount = new JLabel("Investment Account:");
		panTop.add(lbAccount,gbc_label);
		GridBagConstraints gbc_account = new GridBagConstraints();
		gbc_account.gridx = 1;
		gbc_account.gridy = 0;
		txtAccount = new JTextField(this.acct.getAccountName());
		panTop.add(txtAccount,gbc_account);
		this.add(panTop,BorderLayout.PAGE_START);
		/*
		 * Middle Panel table
		 */
		panMid = new JPanel ();
		panMid.setLayout(new BoxLayout(panMid,BoxLayout.Y_AXIS));
		transScrollPane = new JScrollPane (transTab);
		transScrollPane.setAlignmentX(LEFT_ALIGNMENT);
		panMid.add(transScrollPane,BorderLayout.LINE_START);
		transScrollPane.setPreferredSize(new Dimension(Constants.LOADSCREENWIDTH,Constants.LOADSCREENHEIGHT));
		select = new MyCheckBox();
		select.setAlignmentX(LEFT_ALIGNMENT);
		select.addItemListener(new ItemListener() {
			@Override
			public void itemStateChanged(ItemEvent e) {
				boolean bNewValue;
				if (e.getStateChange() == ItemEvent.DESELECTED)
					bNewValue = false;
				else
					bNewValue = true;
				for (int i=0;i<transModel.getRowCount();i++)
					transModel.setValueAt(bNewValue, i, 0);
				transModel.fireTableDataChanged();
			}
		});
		panMid.add(select);
		this.add(panMid,BorderLayout.CENTER);
		
		
		/*
		 * Add Buttons
		 */
		panBot = new JPanel(new GridBagLayout());
		/*
		 * Button 1
		 */
		GridBagConstraints constraints = new GridBagConstraints();
		constraints.gridx = 0;
		constraints.gridy = 0;
		constraints.anchor = GridBagConstraints.LINE_START;
		constraints.insets = new Insets(15,15,15,15);
		btnClose = new JButton("Close");
		btnClose.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				close();
			}
		});
		panBot.add(btnClose,constraints);

		/*
		 * Button 2
		 */
		GridBagConstraints constraints2 = new GridBagConstraints();
		constraints2.gridx = constraints.gridx+1;
		constraints2.gridy = constraints.gridy;
		constraints2.insets = new Insets(15,15,15,15);
		btnSave = new JButton("SaveTransactions");
		btnSave.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				save();
				panMid.invalidate();
				panMid.validate();
			}
		});
		panBot.add(btnSave,constraints2);
		helpBtn = new JButton("Help");
		helpBtn.setToolTipText("Display help information");
		helpBtn.addActionListener(e -> {
			String url = "https://github.com/mrbray99/moneydanceproduction/wiki/Security-Transaction-Load";
			mdGUI.showInternetURL(url);
		});
		panBot.add(helpBtn, GridC.getc(constraints2.gridx+1,constraints2.gridy).west().insets(10, 10, 10, 10));
		
		this.add(panBot,BorderLayout.PAGE_END);
			
	}
	private void generateTrans() {
		for (SecLine secLine :setLine) {
			if (!secLine.getSelect())
				continue;
			FieldLine objMatch = params.matchType(secLine.getTranType());
			if (objMatch != null) {
				investFields = new InvestFields();
				investFields.hasFee = false;
				ParentTxn ptTran = new ParentTxn(Main.acctBook);
				ptTran.setAccount(acct);
				switch (Constants.TRANSTYPES[objMatch.getTranType()]) {
				case Constants.SECURITY_INCOME :
					investFields.amount= secLine.getValue();
					investFields.hasAmount = true;
					investFields.category = objMatch.getAccount();
					investFields.hasCategory=true;
					investFields.date = secLine.getDate();
					investFields.taxDate= secLine.getDate();
					investFields.txnType = InvestTxnType.MISCINC;
					investFields.security = Main.mapAccounts.get(secLine.getTicker());
					investFields.hasSecurity = true;
					investFields.payee = secLine.getDescription();
					investFields.storeFields(ptTran);
					transModel.addLine(new GenerateTransaction(Constants.PARENT,acct, secLine.getDate(),
							secLine.getValue(),"","",
							AbstractTxn.TRANSFER_TYPE_MISCINCEXP, secLine.getTranType(),ptTran.getParentTxn()));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,(Main.mapAccounts.get(secLine.getTicker())),
							secLine.getDate(),0,Main.mapAccounts.get(secLine.getTicker()).getAccountName(),"",
							AbstractTxn.TRANSFER_TYPE_MISCINCEXP, secLine.getTranType(),ptTran.getSplit(0)));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,objMatch.getAccount(), secLine.getDate(),
							secLine.getValue()*-1,
							OnlineTxn.INVEST_TXN_MISCINC+" "+Main.mapAccounts.get(secLine.getTicker()).getAccountName(),"",
							AbstractTxn.TRANSFER_TYPE_MISCINCEXP, secLine.getTranType(),ptTran.getSplit(1)));
					break;
				case Constants.SECURITY_DIVIDEND :
					investFields.amount= secLine.getValue();
					investFields.hasAmount = true;
					investFields.category = objMatch.getAccount();
					investFields.hasCategory=true;
					investFields.date = secLine.getDate();
					investFields.taxDate= secLine.getDate();
					investFields.txnType = InvestTxnType.DIVIDEND;
					investFields.security = Main.mapAccounts.get(secLine.getTicker());
					investFields.hasSecurity = true;
					investFields.payee = secLine.getDescription();
					investFields.storeFields(ptTran);
					transModel.addLine(new GenerateTransaction(Constants.PARENT,
							acct, //account
							secLine.getDate(), //date
							secLine.getValue(), // value
							"", // descr
							"",  // cheque
							AbstractTxn.TRANSFER_TYPE_DIVIDEND, // type
							secLine.getTranType(),ptTran.getParentTxn())); // reference
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,(Main.mapAccounts.get(secLine.getTicker())),
							secLine.getDate(),0,Main.mapAccounts.get(secLine.getTicker()).getAccountName(),"",AbstractTxn.TRANSFER_TYPE_DIVIDEND, secLine.getTranType(),ptTran.getSplit(0)));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,objMatch.getAccount(), secLine.getDate(),
							secLine.getValue()*-1,
							OnlineTxn.INVEST_TXN_DIVIDEND+" "+Main.mapAccounts.get(secLine.getTicker()).getAccountName(),"",
							AbstractTxn.TRANSFER_TYPE_DIVIDEND, secLine.getTranType(),ptTran.getSplit(1)));
					
					break;
				case Constants.SECURITY_COST :
					investFields.amount= secLine.getValue();
					investFields.hasAmount = true;
					investFields.category = secLine.getAccount();
					investFields.hasCategory=true;
					investFields.date = secLine.getDate();
					investFields.taxDate= secLine.getDate();
					investFields.txnType = InvestTxnType.MISCEXP;
					investFields.security = Main.mapAccounts.get(secLine.getTicker());
					investFields.hasSecurity = true;
					investFields.storeFields(ptTran);
					transModel.addLine(new GenerateTransaction(Constants.PARENT,acct, secLine.getDate(),
							secLine.getValue()*-1,"","",
							AbstractTxn.TRANSFER_TYPE_MISCINCEXP, secLine.getTranType(),ptTran.getParentTxn()));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,(Main.mapAccounts.get(secLine.getTicker())),
							secLine.getDate(),0,Main.mapAccounts.get(secLine.getTicker()).getAccountName(),"",AbstractTxn.TRANSFER_TYPE_MISCINCEXP,
							secLine.getTranType(),ptTran.getSplit(0)));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,objMatch.getAccount(), secLine.getDate(),
							secLine.getValue(),
							OnlineTxn.INVEST_TXN_MISCINC+" "+Main.mapAccounts.get(secLine.getTicker()).getAccountName(),"",
							AbstractTxn.TRANSFER_TYPE_MISCINCEXP, secLine.getTranType(),ptTran.getSplit(1)));
					break;
				case Constants.INVESTMENT_INCOME:
					investFields.amount= secLine.getValue();
					investFields.hasAmount = true;
					investFields.xfrAcct = objMatch.getAccount();
					investFields.hasXfrAcct=true;
					investFields.date = secLine.getDate();
					investFields.taxDate= secLine.getDate();
					investFields.txnType = InvestTxnType.BANK;
					investFields.payee = secLine.getDescription();
					investFields.storeFields(ptTran);
					transModel.addLine(new GenerateTransaction(Constants.PARENT,acct, secLine.getDate(),
							secLine.getValue(), secLine.getDescription(),"",AbstractTxn.TRANSFER_TYPE_BANK, secLine.getTranType(),ptTran.getParentTxn()));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,objMatch.getAccount(), secLine.getDate(),
							secLine.getValue()*-1,acct.getAccountName(),"",
							AbstractTxn.TRANSFER_TYPE_BANK, secLine.getTranType(),ptTran.getSplit(0)));
					break;
				case Constants.INVESTMENT_COST :
					investFields.amount= secLine.getValue();
					investFields.hasAmount = true;
					investFields.xfrAcct = objMatch.getAccount();
					investFields.hasXfrAcct=true;
					investFields.date = secLine.getDate();
					investFields.taxDate= secLine.getDate();
					investFields.txnType = InvestTxnType.BANK;
					investFields.payee = secLine.getDescription();
					investFields.storeFields(ptTran);
					transModel.addLine(new GenerateTransaction(Constants.PARENT,acct, secLine.getDate(),
							secLine.getValue(), secLine.getDescription(),"",
							AbstractTxn.TRANSFER_TYPE_BANK, secLine.getTranType(),ptTran.getParentTxn()));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,objMatch.getAccount(), secLine.getDate(),
							secLine.getValue()*-1,acct.getAccountName(),"",
							AbstractTxn.TRANSFER_TYPE_BANK, secLine.getTranType(),ptTran.getSplit(0)));
					break;
				case Constants.INVESTMENT_BUY:
				case Constants.INVESTMENT_SELL:
					if (Constants.TRANSTYPES[objMatch.getTranType()].equals(Constants.INVESTMENT_BUY)) {
						investFields.txnType = InvestTxnType.BUY;
						investFields.amount = -secLine.getValue();
					}
					else {
						investFields.amount = -secLine.getValue();
						investFields.txnType = InvestTxnType.SELL;
					}

					Account security = Main.mapAccounts.get(secLine.getTicker());
					if (security==null || (!security.getAccountType().equals(Account.AccountType.SECURITY))||
						security.getCurrencyType()==null)
						break;
					CurrencyType securityCurrency = security.getCurrencyType();
					investFields.hasPrice = true;
					investFields.hasSecurity=true;
					investFields.hasShares=true;
					investFields.hasAmount=true;
					investFields.hasMemo = true;
					Double unitConvert = secLine.getUnit();
					for (int i=0;i<securityCurrency.getDecimalPlaces();i++)
						unitConvert = unitConvert*10.0;
					investFields.shares = Math.round(unitConvert);
					investFields.secCurr= securityCurrency;
					investFields.date = secLine.getDate();
					investFields.taxDate = secLine.getDate();

					investFields.price=secLine.getValue()/(100.0 * secLine.getUnit());
					investFields.security = security;
					investFields.payee = secLine.getDescription();
					investFields.storeFields(ptTran);
					transModel.addLine(new GenerateTransaction(Constants.PARENT,acct, secLine.getDate(),
							secLine.getValue(), secLine.getDescription(),"",
							AbstractTxn.TRANSFER_TYPE_BUYSELL, secLine.getTranType(),ptTran.getParentTxn(),params));
					transModel.addLine(new GenerateTransaction(Constants.SPLIT,acct, secLine.getDate(),
							investFields.shares,acct.getAccountName(),"",
							AbstractTxn.TRANSFER_TYPE_BANK, secLine.getTranType(),ptTran.getSplit(0),params));
					break;
				default :
					/*
					 * not interested in transfers/card payments
					 */
				}
			}
		}
		
		
	}
	 
	 public void close() {
		this.setVisible(false);
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.dispose();

	 }
	 
	 public void save() {
		 int i = 0;
		 while (i<transModel.getRowCount()) {
			 if (transModel.getLine(i).getType() == Constants.PARENT) {
				 if ((boolean)transModel.getValueAt(i, 0)) {
					 GenerateTransaction transLine = transModel.getLine(i);	
				 	 ParentTxn ptTran = (ParentTxn)transLine.getTxn();
					 if (transLine.getInvType()!= null) ptTran.setInvestTxnType(transLine.getInvType());
				 	 SplitTxn stTran1 = (SplitTxn) ptTran.getSplit(0);
					 ptTran.setParameter(Constants.TAGGEN, transLine.getRef());
					 stTran1.setParameter(Constants.TAGGEN, transLine.getRef());
					 if (ptTran.getSplitCount() > 1) {
						 SplitTxn stTran2 = (SplitTxn) ptTran.getSplit(1);
						 stTran2.setParameter(Constants.TAGGEN, transLine.getRef());
					 }
					 ptTran.syncItem();
					 i++;
				 }
				 else
					 i++;
			 }
			 else
				 i++;
		 }
		 /*
		  * finished creating transactions:
		  *   1. check processed transactions again
		  *   2. Delete processed rows from window
		  *   3. redisplay window 
		  */
		 Main.tranSet = Main.acctBook.getTransactionSet();
		 Main.generatedTranSet = new MyTransactionSet(Main.root, acct, params,setLine);
		 for (SecLine objLine :setLine) {
			if (!objLine.getSelect())
				continue;
			objLine.setProcessed(false);
			Main.generatedTranSet.findTransaction(objLine);
		 }
		 int iRowCount = transModel.getRowCount();
		 for (int j = iRowCount -1; j>= 0; j--) {
			 int iIndex = transModel.getLine(j).getIndex();
			 if (iIndex >= 0)
				 transModel.deleteLine(iIndex);
		 }
		 transModel.fireTableDataChanged();

	 }

}
