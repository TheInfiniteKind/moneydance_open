package com.moneydance.modules.features.filedisplay;

import java.awt.AWTEvent;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Desktop;
import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.SwingConstants;

import com.infinitekind.util.CustomDateFormat;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;

/**
 * Window used for Account List interface
 * ------------------------------------------------------------------------
 */

public class FileDisplayWindow extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private Main extension;
	private JDateField startDateFld;
	private JDateField endDateFld;
	private JCheckBox includeBankAccounts;
	private JCheckBox includeInvestments;
	private JCheckBox includeAssets;
	private JCheckBox includeCreditCards;
	private JCheckBox includeLiabilities;
	private JCheckBox includeLoans;
	private JCheckBox includeSecurities;
	private JCheckBox includeIncomecat;
	private JCheckBox includeExpensecat;
	private JCheckBox includeAddressBook;
	private JCheckBox includeBudgets;
	private JCheckBox includeCurrencies;
	private JCheckBox includeMemorizedItems;
	private JCheckBox includeReminders;
	private JRadioButton includeNoTrans;
	private JRadioButton includeAllTrans;
	private JRadioButton includeTransbyAccounts;
	private JButton generateButton;
	private JButton closeButton;
	private JPanel panApp;
	private JButton transButton;
	private JPanel panSelect;
	private JPanel panTree;
	private JPanel panButtons;
	private DetailedFileDisplayWindow detailedWindow;
	private JButton copyright;
	private MoneydanceUI mdGUI;
	private com.moneydance.apps.md.controller.Main mdMain;
	private JButton helpBtn;

	public FileDisplayWindow(Main extensionp) {
		super("File Display - Build "+Main.buildStr);
		mdMain = com.moneydance.apps.md.controller.Main.mainObj;
		mdGUI = mdMain.getUI();
		setResizable(false);
		this.extension = extensionp;
		panApp = new JPanel(new BorderLayout());
		panSelect = new JPanel(new GridBagLayout());
		int col = 0;
		int row = 0;
		// Accounts
		JLabel lblAccountsName = new JLabel("Accounts to include:");
		panSelect.add(lblAccountsName, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Include Bank Accounts
		col++;
		JLabel lblIncBank = new JLabel("Bank Accounts");
		panSelect.add(lblIncBank, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col++;
		includeBankAccounts = new JCheckBox();
		panSelect.add(includeBankAccounts, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		col=1;
		// Include Investments Accounts
		JLabel lblIncInv = new JLabel("Investment Accounts");
		panSelect.add(lblIncInv, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col++;
		includeInvestments = new JCheckBox();
		panSelect.add(includeInvestments,GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include Assets
		col= 1;
		JLabel lblIncAsset = new JLabel("Assets");
		panSelect.add(lblIncAsset, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col++;
		includeAssets = new JCheckBox();
		panSelect.add(includeAssets, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include Credit Cards
		col = 1;
		JLabel lblIncCCard = new JLabel("Credit Cards");
		panSelect.add(lblIncCCard, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col++;
		includeCreditCards = new JCheckBox();
		panSelect.add(includeCreditCards, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include Liabilities
		col = 1;
		JLabel lblIncLiab = new JLabel("Liabilties");
		panSelect.add(lblIncLiab, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 2;
		includeLiabilities = new JCheckBox();
		panSelect.add(includeLiabilities, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Include Loans
		col  =1;
		JLabel lblIncLoan = new JLabel("Loans");
		panSelect.add(lblIncLoan,GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col= 2;
		includeLoans = new JCheckBox();
		panSelect.add(includeLoans, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Categories
		col = 0;
		JLabel lblCategoryName = new JLabel("Categories to include:");
		panSelect.add(lblCategoryName, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Include Income
		col = 1;
		JLabel lblIncInc = new JLabel("Income");
		panSelect.add(lblIncInc, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 2;
		includeIncomecat = new JCheckBox();
		panSelect.add(includeIncomecat, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include Expense
		col = 1;
		JLabel lblIncExp = new JLabel("Expenses");
		panSelect.add(lblIncExp, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 2;
		includeExpensecat = new JCheckBox();
		panSelect.add(includeExpensecat, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		// Extras
		row = 0;
		col = 3;
		JLabel lblExtrasName = new JLabel("Extras to include:");
		panSelect.add(lblExtrasName,GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Include Address Book
		col = 4;
		JLabel lblIncAddress = new JLabel("Address Book");
		panSelect.add(lblIncAddress, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 5;
		includeAddressBook = new JCheckBox();
		panSelect.add(includeAddressBook, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		/*
		 * // Include Account Book con.gridx = 4; con.gridy = row; JLabel
		 * lblIncAccountBook = new JLabel("Account Book");
		 * panSelect.add(lblIncAccountBook,con); con.gridx = 5;
		 * includeAccountBook = new JCheckBox();
		 * panSelect.add(includeAccountBook,con); row++;
		 */

		// Include Budgets
		col = 4;
		JLabel lblIncBudget = new JLabel("Budgets");
		panSelect.add(lblIncBudget, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 5;
		includeBudgets = new JCheckBox();
		panSelect.add(includeBudgets, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Include Currencies
		col = 4;
		JLabel lblIncCurrency = new JLabel("Currencies");
		panSelect.add(lblIncCurrency, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 5;
		includeCurrencies = new JCheckBox();
		panSelect.add(includeCurrencies, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Include Securities
		col = 4;
		JLabel lblIncSec = new JLabel("Securities");
		panSelect.add(lblIncSec, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 5;
		includeSecurities = new JCheckBox();
		panSelect.add(includeSecurities, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// Include Memorable items
		col = 4;
		JLabel lblIncMemory = new JLabel("Memorized Items");
		panSelect.add(lblIncMemory, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 5;
		includeMemorizedItems = new JCheckBox();
		panSelect.add(includeMemorizedItems, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include Reminders
		col = 4;
		JLabel lblIncRemind = new JLabel("Reminders");
		panSelect.add(lblIncRemind, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		col = 5;
		includeReminders = new JCheckBox();
		panSelect.add(includeReminders, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Transactions
		row = 0;
		col = 6;
		JLabel lblTransName = new JLabel("Include Transactions:");
		panSelect.add(lblTransName, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include none
		col = 7;
		includeNoTrans = new JRadioButton("None", true);
		panSelect.add(includeNoTrans, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include By File
		col= 7;
		includeAllTrans = new JRadioButton("By File");
		panSelect.add(includeAllTrans, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		// Include By Account
		col = 7;
		includeTransbyAccounts = new JRadioButton("By Account");
		panSelect.add(includeTransbyAccounts, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		ButtonGroup group = new ButtonGroup();
		group.add(includeNoTrans);
		group.add(includeAllTrans);
		group.add(includeTransbyAccounts);

		CustomDateFormat cdf = new CustomDateFormat("dd/MM/yyyy");
		// Trans Start Date
		col = 7;
		JLabel lblStartDate = new JLabel("Start Date:");
		panSelect.add(lblStartDate,GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		startDateFld = new JDateField(cdf);
		startDateFld.gotoFirstDayInMonth();
		startDateFld.decrementDate();
		startDateFld.setEditable(true);
		startDateFld.gotoFirstDayInMonth();
		startDateFld.setDisabledTextColor(Color.BLACK);
		col = 8;
		panSelect.add(startDateFld, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;

		// End Date
		col = 7;
		JLabel lblEndDate = new JLabel("End Date:");
		panSelect.add(lblEndDate, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		endDateFld = new JDateField(cdf);
		endDateFld.setDisabledTextColor(Color.BLACK);
		endDateFld.setEditable(true);
		col = 8;
		panSelect.add(endDateFld, GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		row++;
		col = 7;
		row++;
		// Buttons
		generateButton = new JButton("Generate");
		generateButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				generate();
			}
		});
		panSelect.add(generateButton,GridC.getc(col,row).fillx().west().insets(0, 0, 0, 0));
		panSelect.setPreferredSize(new Dimension(1000, 300));
		panApp.add(panSelect, BorderLayout.PAGE_START);
		/*
		 * Tree pane
		 */
		panTree = new JPanel(new BorderLayout());
		detailedWindow = new DetailedFileDisplayWindow(includeBankAccounts.isSelected(), includeInvestments.isSelected(),
				includeAssets.isSelected(), includeCreditCards.isSelected(),
				includeLiabilities.isSelected(), includeLoans.isSelected(),
				includeSecurities.isSelected(), includeIncomecat.isSelected(),
				includeExpensecat.isSelected(), includeAddressBook.isSelected(), 
				includeBudgets.isSelected(), includeCurrencies.isSelected(),
				includeMemorizedItems.isSelected(), includeReminders.isSelected(),
				includeAllTrans.isSelected(),
				includeTransbyAccounts.isSelected(), startDateFld.getDateInt(),
				endDateFld.getDateInt());
		panTree.add(detailedWindow);
		panTree.setPreferredSize(new Dimension(1000, 400));
		panTree.setMinimumSize(new Dimension(800, 300));
		panApp.add(panTree, BorderLayout.CENTER);
		/*
		 * Button pane
		 */
		col= 0;
		row = 0;
		panButtons = new JPanel(new GridBagLayout());
		copyright = new JButton("<html><a href=http://icons8.com>Icons couresy of icons8.com</a></html>");
		    copyright.setHorizontalAlignment(SwingConstants.LEFT);
		    copyright.setBorderPainted(false);
		    copyright.setOpaque(false);
		    copyright.setBackground(Color.WHITE);
			copyright.addActionListener(new ActionListener() {
				@Override
				public void actionPerformed(ActionEvent e) {
					openIcons();
				}
			});
		panButtons.add(copyright, GridC.getc(col,row).fillx().west().insets(5, 5, 5, 5));
		col++;
		closeButton = new JButton("Close");
		closeButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				FileDisplayWindow.this.extension.closeConsole();
			}
		});
		panButtons.add(closeButton, GridC.getc(col,row).fillx().west().insets(5, 5, 5, 5));
		transButton = new JButton("View Transactions");
		transButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				detailedWindow.viewTrans();
			}
		});
		col = 2;
		panButtons.add(transButton, GridC.getc(col++,row).fillx().west().insets(5, 5, 5, 5));
		helpBtn = new JButton("Help");
		helpBtn.setToolTipText("Display help information");
		helpBtn.addActionListener(e -> {
			String url = "https://github.com/mrbray99/moneydanceproduction/wiki/File-Display";
			mdGUI.showInternetURL(url);
		});
		panButtons.add(helpBtn, GridC.getc(col, row).west().insets(10, 10, 10, 10));
		panApp.add(panButtons, BorderLayout.PAGE_END);
		/*
		 * Add main panel
		 */
		setPreferredSize(new Dimension(1000, 800));
		getContentPane().add(panApp);

		setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		enableEvents(WindowEvent.WINDOW_CLOSING);

	}
	private void openIcons() {
		   if (Desktop.isDesktopSupported()) {
			      try {
			        Desktop.getDesktop().browse(new URI("http://icons8.com"));
			      } catch (IOException | URISyntaxException e) { /* TODO: error handling */ }
			    } else { /* TODO: error handling */ }
	}
	/*
	 * Display the detail based on selected options
	 */
	protected void generate() {
		// Schedule a job for the event dispatch thread:
		// creating and showing this application's GUI.
		detailedWindow.reset(includeBankAccounts.isSelected(),
				includeInvestments.isSelected(), includeAssets.isSelected(),
				includeCreditCards.isSelected(),
				includeLiabilities.isSelected(), includeLoans.isSelected(),
				includeSecurities.isSelected(), includeIncomecat.isSelected(),
				includeExpensecat.isSelected(),
				includeAddressBook.isSelected(), includeBudgets.isSelected(),
				includeCurrencies.isSelected(),
				includeMemorizedItems.isSelected(),
				includeReminders.isSelected(), includeNoTrans.isSelected(),
				includeAllTrans.isSelected(),
				includeTransbyAccounts.isSelected(), startDateFld.getDateInt(),
				endDateFld.getDateInt());
		panTree.setPreferredSize(new Dimension(1000, 400));
		panTree.setMinimumSize(new Dimension(800, 300));
		panApp.repaint();
	}

	@Override
	public final void processEvent(AWTEvent evt) {
		if (evt.getID() == WindowEvent.WINDOW_CLOSING) {
			extension.closeConsole();
			return;
		}
		if (evt.getID() == WindowEvent.WINDOW_OPENED) {
		}
		super.processEvent(evt);
	}

	void goAway() {
		if (detailedWindow != null)
			detailedWindow.close();
		setVisible(false);
		dispose();
	}
}
