package com.moneydance.modules.features.filedisplay;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DecimalFormat;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.Vector;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTree;
import javax.swing.SwingUtilities;
import javax.swing.border.EmptyBorder;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeCellRenderer;
import javax.swing.tree.TreePath;
import javax.swing.tree.TreeSelectionModel;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.tiksync.SyncRecord;
import com.infinitekind.util.CustomDateFormat;
import com.moneydance.awt.GridC;

/**
 * File Detail. Creates a tree with the chosen options split into three groups
 * The first level of each group is added to the tree A Tree Selection Listener
 * is used to add entries when the user clicks on a leaf
 * 
 * */
public class DetailedFileDisplayWindow extends JPanel implements
		TreeSelectionListener {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private DateTimeFormatter format1 = DateTimeFormatter.ofPattern("yyyy-MM-dd hh:mm:ss",Locale.ENGLISH);
	private JTree tree;
	private DefaultMutableTreeNode nodeTop;
	private JScrollPane treeView;
	private int startDate;
	private int endDate;
	private boolean includeBankAccounts;
	private boolean includeInvestments;
	private boolean includeAssets;
	private boolean includeCreditCards;
	private boolean includeLiabilities;
	private boolean includeLoans;
	private boolean includeSecurities;
	private boolean includeIncomecat;
	private boolean includeExpensecat;
	private boolean includeAddressBook;
	private boolean includeBudgets;
	private boolean includeCurrencies;
	private boolean includeMemorizedItems;
	private boolean includeReminders;
	private boolean includeAllTrans;
	private boolean includeTransbyAccounts;
	private enum ViewType {ACCOUNT, ADDRESS, BUDGET, MEMORIZED, REMINDER, CURRENCY, SECURITY}
	private ViewType enumCurrentView;
	private Reminder objCrntReminder;
	private Account lastAcct = null;
	private CurrencyType baseCurr;
	private JScrollPane detailpane = null;
	private JPanel panTrans;
	private JFrame transFrm;
	private JFrame singleTransFrm;
	private JPanel panSingleTrans;
	MyTable detailtable = null;
	DefaultTableModel detailmodel = null;
	MyTranTable trantable = null;
	JTable tabTran = null;
	TransactionSet txnSet;
	TxnSet tsTrans;
	private AccountBook objAcctBook;
	private Map<Account.AccountType, List<Account>> accounts;

	private JButton closeButton;
	private JButton closeTranButton;
	private static final int MINSCROLLPANE = 300;
	private static final int SCROLLPANEDEPTH = 400;


	/*
	 * Each node on the tree has a user object of myNodeObject This contains a
	 * structure ID which is in the format gtex g is the group, i.e. Accounts
	 * (1), Categories (2) or Extras (3) t is the type, i.e. type of account,
	 * category or extra e is the particular entry, i.e. Bank Account, Expense
	 * category x is only used for budget items ACCOUNT_INCREMENT is added to
	 * the NODE entry to give the ACCOUNT entry BUDGET_INCREMENT is added to a
	 * Budget Entry to give the item
	 */

	public static final int BANK_NODE = 1100;
	public static final int BANK_ACCOUNT = 1110;
	public static final int INVESTMENT_NODE = 1200;
	public static final int INVESTMENT_ACCOUNT = 1210;
	public static final int LIABILITY_NODE = 1300;
	public static final int LIABILITY_ACCOUNT = 1310;
	public static final int ASSET_NODE = 1400;
	public static final int ASSET_ACCOUNT = 1410;
	public static final int LOAN_NODE = 1500;
	public static final int LOAN_ACCOUNT = 1510;
	public static final int EXPENSE_NODE = 2100;
	public static final int EXPENSE_ACCOUNT = 2110;
	public static final int INCOME_NODE = 2200;
	public static final int INCOME_ACCOUNT = 2210;
	public static final int CREDIT_CARD_NODE = 1700;
	public static final int CREDIT_CARD_ACCOUNT = 1710;
	public static final int ACCOUNTS_NODE = 1000;
	public static final int CATEGORIES_NODE = 2000;
	public static final int EXTRAS_NODE = 3000;
	public static final int EXTRAS_ADDRESS_NODE = 3100;
	public static final int EXTRAS_BUDGET_NODE = 3300;
	public static final int EXTRAS_CURRENCY_NODE = 3400;
	public static final int EXTRAS_MEMORIZED_NODE = 3500;
	public static final int EXTRAS_REMINDER_NODE = 3600;
	public static final int EXTRAS_SECURITY_NODE = 3700;
	public static final int EXTRAS_ADDRESS_ENTRY = 3110;
	public static final int EXTRAS_BUDGET_ENTRY = 3310;
	public static final int EXTRAS_CURRENCY_ENTRY = 3410;
	public static final int EXTRAS_SECURITY_ENTRY = 3710;
	public static final int EXTRAS_MEMORIZED_GRAPH_ENTRY = 3510;
	public static final int EXTRAS_MEMORIZED_REPORT_ENTRY = 3520;
	public static final int EXTRAS_REMINDER_ENTRY = 3610;
	public static final int ACCOUNT_INCREMENT = 10;
	public static final int BUDGET_INCREMENT = 1;
	public static final int CURRENCY_INCREMENT = 1;
	public static final int SECURITY_INCREMENT = 1;
	/*
	 * Name of table columns
	 */
	public static final String[] columnNames = { "Field", "Value" };
	public static final String[] transcolumns = { "ID", "Old ID", "Account",
			"Description", "Date", "Value", "Type", "P//S", "Cheque", "Status" };
	/*
	 * Table to link tree nodes back to Moneydance account type
	 */
	private static final Map<Integer, Account.AccountType> nodetypes;
	static {
		nodetypes = new HashMap<>();
		nodetypes.put(BANK_NODE, Account.AccountType.BANK);
		nodetypes.put(INVESTMENT_NODE, Account.AccountType.INVESTMENT);
		nodetypes.put(LIABILITY_NODE, Account.AccountType.LIABILITY);
		nodetypes.put(ASSET_NODE, Account.AccountType.ASSET);
		nodetypes.put(LOAN_NODE, Account.AccountType.LOAN);
		nodetypes.put(CREDIT_CARD_NODE, Account.AccountType.CREDIT_CARD);
		nodetypes.put(EXPENSE_NODE, Account.AccountType.EXPENSE);
		nodetypes.put(INCOME_NODE, Account.AccountType.INCOME);
		nodetypes.put(BANK_ACCOUNT, Account.AccountType.BANK);
		nodetypes.put(INVESTMENT_ACCOUNT, Account.AccountType.INVESTMENT);
		nodetypes.put(LIABILITY_ACCOUNT, Account.AccountType.LIABILITY);
		nodetypes.put(ASSET_ACCOUNT, Account.AccountType.ASSET);
		nodetypes.put(LOAN_ACCOUNT, Account.AccountType.LOAN);
		nodetypes.put(CREDIT_CARD_ACCOUNT, Account.AccountType.CREDIT_CARD);
		nodetypes.put(INCOME_ACCOUNT, Account.AccountType.INCOME);
		nodetypes.put(EXPENSE_ACCOUNT, Account.AccountType.EXPENSE);
		nodetypes.put(ACCOUNTS_NODE, null);
		nodetypes.put(CATEGORIES_NODE, null);
		nodetypes.put(EXTRAS_NODE, null);
	}
	/*
	 * Table to link Moneydance account types to a string
	 */
	private static final Map<Account.AccountType, String> accounttypes;
	static {
		accounttypes = new HashMap<>();
		accounttypes.put(Account.AccountType.BANK, "Bank");
		accounttypes.put(Account.AccountType.INVESTMENT, "Investment");
		accounttypes.put(Account.AccountType.LIABILITY, "Liability");
		accounttypes.put(Account.AccountType.ASSET, "Asset");
		accounttypes.put(Account.AccountType.LOAN, "Loan");
		accounttypes.put(Account.AccountType.SECURITY, "Security");
		accounttypes.put(Account.AccountType.CREDIT_CARD, "Credit Card");
	}
	/*
	 * Table to link budget intervals to a string
	 */
	private static final Map<Integer, String> intervaltypes;
	static {
		intervaltypes = new HashMap<>();
		intervaltypes.put(BudgetItem.INTERVAL_ANNUALLY, "Annually");
		intervaltypes.put(BudgetItem.INTERVAL_BI_MONTHLY, "Bi-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_BI_WEEKLY, "Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_DAILY, "Daily");
		intervaltypes.put(BudgetItem.INTERVAL_MONTHLY, "Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_NO_REPEAT, "No Repeat");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_ANNUALLY, "Once Annually ");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_BI_MONTHLY,
				"Once Bi-Monthly");
		intervaltypes
				.put(BudgetItem.INTERVAL_ONCE_BI_WEEKLY, "Once Bi-Weekly ");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_MONTHLY, "Once Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_SEMI_ANNUALLY,
				"Once Semi-Annually");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_SEMI_MONTHLY,
				"Once Semi-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_TRI_MONTHLY,
				"Once Tri-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_TRI_WEEKLY,
				"Once Tri-Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_ONCE_WEEKLY, "Once Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_SEMI_ANNUALLY, "Semi-Annually");
		intervaltypes.put(BudgetItem.INTERVAL_SEMI_MONTHLY, "Semi-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_TRI_MONTHLY, "Tri-Monthly");
		intervaltypes.put(BudgetItem.INTERVAL_TRI_WEEKLY, "Tri-Weekly");
		intervaltypes.put(BudgetItem.INTERVAL_WEEKLY, "Weekly");
	}

	// -------------------------------------------
	// Private Classes
	// -------------------------------------------
	/**
	 */
	public DetailedFileDisplayWindow(
			boolean includeBankAccounts, boolean includeInvestments,
			boolean includeAssets, boolean includeCreditCards,
			boolean includeLiabilities, boolean includeLoans,
			boolean includeSecurities, boolean includeIncomecat,
			boolean includeExpensecat, boolean includeAddressBook,
			boolean includeBudgets, boolean includeCurrencies,
			boolean includeMemorizedItems, boolean includeReminders,
			boolean includeAllTrans,
			boolean includeTransbyAccounts, int txtStartDate,
			int txtEndDate) {
		super(new GridBagLayout());
		this.includeBankAccounts = includeBankAccounts;
		this.includeInvestments = includeInvestments;
		this.includeAssets = includeAssets;
		this.includeCreditCards = includeCreditCards;
		this.includeLiabilities = includeLiabilities;
		this.includeLoans = includeLoans;
		this.includeSecurities = includeSecurities;
		this.includeIncomecat = includeIncomecat;
		this.includeExpensecat = includeExpensecat;
		this.includeAddressBook = includeAddressBook;
		this.includeBudgets = includeBudgets;
		this.includeCurrencies = includeCurrencies;
		this.includeMemorizedItems = includeMemorizedItems;
		this.includeReminders = includeReminders;
		this.includeAllTrans = includeAllTrans;
		this.includeTransbyAccounts = includeTransbyAccounts;
		this.startDate = txtStartDate;
		this.endDate = txtEndDate;
		this.setBorder(new EmptyBorder(5, 5, 5, 5));
		objAcctBook = Main.context.getCurrentAccountBook();
		baseCurr = objAcctBook.getCurrencies().getBaseType();

		// Create the nodes.
		nodeTop = new DefaultMutableTreeNode("Moneydance File");
		createNodes(nodeTop);

		// Create a tree that allows one selection at a time.
		tree = new JTree(nodeTop);
		tree.getSelectionModel().setSelectionMode(
				TreeSelectionModel.SINGLE_TREE_SELECTION);
		DefaultTreeCellRenderer renderer = (DefaultTreeCellRenderer)tree.getCellRenderer();
		if (Main.openIcon !=null)renderer.setOpenIcon(new ImageIcon(Main.openIcon));
		if (Main.closeIcon !=null)renderer.setClosedIcon(new ImageIcon(Main.closeIcon));
		if (Main.leafIcon !=null)renderer.setLeafIcon(new ImageIcon(Main.leafIcon));
		// Listen for when the selection changes.
		tree.addTreeSelectionListener(this);

		// Create the scroll pane and add the tree to it.
		treeView = new JScrollPane();
		treeView.getViewport().add(tree);
		treeView.getViewport().setPreferredSize(new Dimension(MINSCROLLPANE, SCROLLPANEDEPTH));
		tree.setMinimumSize(new Dimension(MINSCROLLPANE, SCROLLPANEDEPTH));
		this.add(treeView, GridC.getc(0, 0).fillx().colspan(4));
		// Create the detail table and pane, then hide
		detailtable = new MyTable(new DefaultTableModel(columnNames, 0));
		detailmodel = (DefaultTableModel) detailtable.getModel();
		detailpane = new JScrollPane(detailtable);
		detailpane.setPreferredSize(new Dimension(650, SCROLLPANEDEPTH));
		this.add(detailpane, GridC.getc(5, 0).fillx());

	}

	public void reset(boolean includeBankAccounts,
			boolean includeInvestments, boolean includeAssets,
			boolean includeCreditCards, boolean includeLiabilities,
			boolean includeLoans, boolean includeSecurities,
			boolean includeIncomecat, boolean includeExpensecat,
			boolean includeAddressBook, boolean includeBudgets,
			boolean includeCurrencies, boolean includeMemorizedItems,
			boolean includeReminders, boolean includeNoTrans,
			boolean includeAllTrans, boolean includeTransbyAccounts,
			int txtStartDate, int txtEndDate) {
		this.includeBankAccounts = includeBankAccounts;
		this.includeInvestments = includeInvestments;
		this.includeAssets = includeAssets;
		this.includeCreditCards = includeCreditCards;
		this.includeLiabilities = includeLiabilities;
		this.includeLoans = includeLoans;
		this.includeSecurities = includeSecurities;
		this.includeIncomecat = includeIncomecat;
		this.includeExpensecat = includeExpensecat;
		this.includeAddressBook = includeAddressBook;
		this.includeBudgets = includeBudgets;
		this.includeCurrencies = includeCurrencies;
		this.includeMemorizedItems = includeMemorizedItems;
		this.includeReminders = includeReminders;
		this.includeAllTrans = includeAllTrans;
		this.includeTransbyAccounts = includeTransbyAccounts;
		this.startDate = txtStartDate;
		this.endDate = txtEndDate;
		treeView.remove(tree);
		nodeTop = new DefaultMutableTreeNode("Moneydance File");
		createNodes(nodeTop);

		// Create a tree that allows one selection at a time.
		tree = new JTree(nodeTop);
		tree.getSelectionModel().setSelectionMode(
				TreeSelectionModel.SINGLE_TREE_SELECTION);
		DefaultTreeCellRenderer renderer = (DefaultTreeCellRenderer)tree.getCellRenderer();
		renderer.setOpenIcon(new ImageIcon(Main.openIcon));
		renderer.setClosedIcon(new ImageIcon(Main.closeIcon));
		renderer.setLeafIcon(new ImageIcon(Main.leafIcon));

		// Listen for when the selection changes.
		tree.addTreeSelectionListener(this);
		treeView.getViewport().add(tree);
		treeView.getViewport().setPreferredSize(new Dimension(MINSCROLLPANE, SCROLLPANEDEPTH));
		treeView.getViewport().setMinimumSize(new Dimension(MINSCROLLPANE, SCROLLPANEDEPTH));
		treeView.repaint();
	}

	/** Required by TreeSelectionListener interface. */
	@Override
	public void valueChanged(TreeSelectionEvent e) {
		DefaultMutableTreeNode dataitem;
		Integer nodeid;
		String nodepattern;
		DefaultMutableTreeNode node = (DefaultMutableTreeNode) tree
				.getLastSelectedPathComponent();

		if (node == null)
			return;
//		treeView.setPreferredSize(new Dimension(MINSCROLLPANE + node.getLevel()
//				* LEVELSCROLLPANE, SCROLLPANEDEPTH));
		Object nodeInfo = node.getUserObject();
		lastAcct = null;
		if (node.isLeaf()) {
			// not expanded
			myNodeObject userobj = (myNodeObject) nodeInfo;
			if (userobj != null) {
				nodeid = userobj.getnodetype();
				nodepattern = nodeid.toString();
				/*
				 * Is the node clicked on an Account (1x0x) or a Category (2x0x)
				 */
				if (nodepattern.matches("[1-2]\\d0\\d")) {
					/*
					 * Add first level of accounts to tree
					 */
					List<Account> listAccts = accounts.get(nodetypes
							.get(nodeid));
					if (listAccts == null)
						return;
					for (int i = 0; i < listAccts.size(); i++) {
						myNodeObject mynode;
						if (listAccts.get(i) == null)
							mynode = new myNodeObject(nodeid
									+ ACCOUNT_INCREMENT, "Missing Name");
						else
							mynode = new myNodeObject(nodeid
									+ ACCOUNT_INCREMENT, listAccts.get(i)
									.getAccountName());
						mynode.setaccount(listAccts.get(i));
						dataitem = new DefaultMutableTreeNode(mynode);
						node.add(dataitem);
					}
					JTree tree = (JTree) e.getSource();
					TreePath path = tree.getSelectionPath();
					tree.expandPath(path);
				}
				/*
				 * Is the node clicked on a specific account (1x1x) or category
				 * (2x1x)
				 */
				if (nodepattern.matches("[1-2]\\d1\\d")) {
					displayaccount(userobj, nodeid, node, e);
				}
				/*
				 * Is the node clicked on an Extra (3x0x)
				 */
				if (nodepattern.matches("3\\d00")) {
					displayextrasentries(userobj, nodeid, node, e);
				}
				/*
				 * Is the node clicked on a specific Extra entry (3x1x or 3x2x)
				 */
				if (nodepattern.matches("3\\d[1-2]0")) {
					displayextras(userobj, nodeid, node, e);

				}
				/*
				 * Is the node clicked on a budget item (33x1)
				 */

				if (nodepattern.matches("33\\d1")) {
					displaybudgetitem(userobj, nodeid, node, e);
				}
				/*
				 * Is the node clicked on a currency item (34x1) or security
				 * item (37x1)
				 */

				if (nodepattern.matches("34\\d1")) {
					displaycurrencyitem(userobj, nodeid, node, e);
				}
				if (nodepattern.matches("37\\d1")) {
					displaycurrencyitem(userobj, nodeid, node, e);
				}
			}
		} else {
			myNodeObject userobj = (myNodeObject) nodeInfo;
			if (userobj != null) {
				nodeid = userobj.getnodetype();
				if (nodeid == EXTRAS_BUDGET_ENTRY) {
					displayextras(userobj, nodeid, node, e);
				}
				if (nodeid == EXTRAS_CURRENCY_ENTRY) {
					displayextras(userobj, nodeid, node, e);
				}
				if (nodeid == EXTRAS_SECURITY_ENTRY) {
					displayextras(userobj, nodeid, node, e);
				}
			}
			// already expanded
		}
	}

	/*
	 * adds the data from a specific account to the table
	 */
	private void displayaccount(myNodeObject userobj, Integer nodeid,
			DefaultMutableTreeNode node, TreeSelectionEvent e) {
		DefaultMutableTreeNode dataitem;
		detailmodel.setRowCount(0);
		enumCurrentView = ViewType.ACCOUNT;
		Account acct = userobj.getaccount();
		lastAcct = acct;
		Vector<String> vname = new Vector<>();
		vname.add("Name");
		vname.add(acct.getAccountName() + " ");
		detailmodel.addRow(vname);
		Vector<String> vfname = new Vector<>();
		vfname.add("Full Account Name");
		vfname.add(acct.getFullAccountName() + " ");
		detailmodel.addRow(vfname);
		Vector<String> viname = new Vector<>();
		viname.add("Indented Account Name");
		viname.add(acct.getIndentedName() + " ");
		detailmodel.addRow(viname);
		Vector<String> vdepth = new Vector<>();
		vdepth.add("Depth");
		vdepth.add(acct.getDepth() + " ");
		detailmodel.addRow(vdepth);
		Vector<String> vtype = new Vector<>();
		vtype.add("Type");
		try {
			vtype.add(accounttypes.get(acct.getAccountType()) + " ");
		}
		catch (Exception etype) {
			vtype.add("No Account Type");			
		}
		detailmodel.addRow(vtype);
		Vector<String> vinactive = new Vector<>();
		vinactive.add("Inactive");
		vinactive.add(acct.getAccountIsInactive() + " ");
		detailmodel.addRow(vinactive);
		Vector<String> vcurrency = new Vector<>();
		vcurrency.add("Currency Type");
		CurrencyType ctype = acct.getCurrencyType();
		if (ctype == null)
	        ctype = baseCurr;
		vcurrency.add(ctype + " ");
		detailmodel.addRow(vcurrency);
		Vector<String> vbalance = new Vector<>();
		vbalance.add("Balance");
		vbalance.add(ctype.formatFancy(acct.getBalance(), '.') + " ");
		detailmodel.addRow(vbalance);
		Vector<String> vclbalance = new Vector<>();
		vclbalance.add("Cleared Balance");
		vclbalance.add(ctype.formatFancy(acct.getClearedBalance(), '.') + " ");
		detailmodel.addRow(vclbalance);
		Vector<String> vcnbalance = new Vector<>();
		vcnbalance.add("Confirmed Balance");
		vcnbalance
				.add(ctype.formatFancy(acct.getConfirmedBalance(), '.') + " ");
		detailmodel.addRow(vcnbalance);
		Vector<String> vcubalance = new Vector<>();
		vcubalance.add("Current Balance");
		vcubalance.add(ctype.formatFancy(acct.getCurrentBalance(), '.') + " ");
		detailmodel.addRow(vcubalance);
		Vector<String> vdate = new Vector<>();
		vdate.add("Creation Date");
		CustomDateFormat cdate = new CustomDateFormat("DD/MM/YYYY");
		vdate.add(cdate.format(acct.getCreationDateInt()) + " ");
		detailmodel.addRow(vdate);
		Vector<String> vcattype = new Vector<>();
		vcattype.add("Default Category");
		try {
			vcattype.add(acct.getDefaultCategory().getAccountName() + " ");
		} catch (Exception ecattype) {
			vcattype.add("None");
		}
		detailmodel.addRow(vcattype);
		Vector<String> vbankfi = new Vector<>();
		vbankfi.add("OFX Connection Bank");
		vbankfi.add(acct.getBankingFI() + " ");
		detailmodel.addRow(vbankfi);
		Vector<String> vbillpayfi = new Vector<>();
		vbillpayfi.add("OFX Bill to Bank");
		vbillpayfi.add(acct.getBillPayFI() + " ");
		detailmodel.addRow(vbillpayfi);
		Vector<String> vcomment = new Vector<>();
		vcomment.add("Comment");
		vcomment.add(acct.getComment() + " ");
		detailmodel.addRow(vcomment);
		Vector<String> vhide = new Vector<>();
		vhide.add("Hide on Home Page");
		vhide.add(acct.getHideOnHomePage() + " ");
		detailmodel.addRow(vhide);
		Vector<String> vofxacct = new Vector<>();
		vofxacct.add("OFX Account Key");
		vofxacct.add(acct.getOFXAccountKey() + " ");
		detailmodel.addRow(vofxacct);
		Vector<String> vofxmsg = new Vector<>();
		vofxmsg.add("OFX Message Type");
		vofxmsg.add(acct.getOFXAccountMsgType() + " ");
		detailmodel.addRow(vofxmsg);
		Vector<String> vofxacctnum = new Vector<>();
		vofxacctnum.add("OFX Account Number");
		vofxacctnum.add(acct.getOFXAccountNumber() + " ");
		detailmodel.addRow(vofxacctnum);
		Vector<String> vofxaccttype = new Vector<>();
		vofxaccttype.add("OFX Account Type");
		vofxaccttype.add(acct.getOFXAccountType() + " ");
		detailmodel.addRow(vofxaccttype);
		Vector<String> vofxbank = new Vector<>();
		vofxbank.add("OFX Bank ID");
		vofxbank.add(acct.getOFXBankID() + " ");
		detailmodel.addRow(vofxbank);
		Vector<String> vofxbillpayacct = new Vector<>();
		vofxbillpayacct.add("OFX Bill Pay Bank Account");
		vofxbillpayacct.add(acct.getOFXBillPayAccountNumber() + " ");
		detailmodel.addRow(vofxbillpayacct);
		Vector<String> vofxbillpayaccttype = new Vector<>();
		vofxbillpayaccttype.add("OFX Bill Pay Bank Account tYPE");
		vofxbillpayaccttype.add(acct.getOFXBillPayAccountType() + " ");
		detailmodel.addRow(vofxbillpayaccttype);
		Vector<String> vrecbal = new Vector<>();
		vrecbal.add("Recursive Balance");
		vrecbal.add(ctype.formatFancy(acct.getRecursiveBalance(), '.') + " ");
		detailmodel.addRow(vrecbal);
		Vector<String> vreccbal = new Vector<>();
		vreccbal.add("Recursive Cleared Balance");
		vreccbal.add(ctype.formatFancy(acct.getRecursiveClearedBalance(), '.')
				+ " ");
		detailmodel.addRow(vreccbal);
		Vector<String> vreccubal = new Vector<>();
		vreccubal.add("Recursive Current Balance");
		vreccubal.add(ctype.formatFancy(acct.getRecursiveCurrentBalance(), '.')
				+ " ");
		detailmodel.addRow(vreccubal);
		Vector<String> vrecrbal = new Vector<>();
		vrecrbal.add("Recursive Reconciling Balance");
		vrecrbal.add(ctype.formatFancy(acct.getRecursiveReconcilingBalance(),
				'.') + " ");
		detailmodel.addRow(vrecrbal);
		Vector<String> vrecsbal = new Vector<>();
		vrecsbal.add("Recursive Start Balance");
		vrecsbal.add(ctype.formatFancy(acct.getRecursiveStartBalance(), '.')
				+ " ");
		detailmodel.addRow(vrecsbal);
		Vector<String> vrecubal = new Vector<>();
		vrecubal.add("Recursive User Balance");
		vrecubal.add(ctype.formatFancy(acct.getRecursiveUserBalance(), '.')
				+ " ");
		detailmodel.addRow(vrecubal);
		Vector<String> vrecucbal = new Vector<>();
		vrecucbal.add("Recursive User Cleared Balance");
		vrecucbal.add(ctype.formatFancy(acct.getRecursiveUserClearedBalance(),
				'.') + " ");
		detailmodel.addRow(vrecucbal);
		Vector<String> vrecucubal = new Vector<>();
		vrecucubal.add("Recursive User Current Balance");
		vrecucubal.add(ctype.formatFancy(acct.getRecursiveUserCurrentBalance(),
				'.') + " ");
		detailmodel.addRow(vrecucubal);
		Vector<String> vrecurbal = new Vector<>();
		vrecurbal.add("Recursive User Reconciling Balance");
		vrecurbal.add(ctype.formatFancy(
				acct.getRecursiveUserReconcilingBalance(), '.')
				+ " ");
		detailmodel.addRow(vrecurbal);
		Vector<String> vrecusbal = new Vector<>();
		vrecusbal.add("Recursive User Start Balance");
		vrecusbal.add(ctype.formatFancy(acct.getRecursiveUserStartBalance(),
				'.') + " ");
		detailmodel.addRow(vrecusbal);
		Vector<String> vstartbal = new Vector<>();
		vstartbal.add("Start  Balance");
		vstartbal.add(ctype.formatFancy(acct.getStartBalance(), '.') + " ");
		detailmodel.addRow(vstartbal);
		Vector<String> vubal = new Vector<>();
		vubal.add("User Balance");
		vubal.add(ctype.formatFancy(acct.getUserBalance(), '.') + " ");
		detailmodel.addRow(vubal);
		Vector<String> vucbal = new Vector<>();
		vucbal.add("User Cleared Balance");
		vucbal.add(ctype.formatFancy(acct.getUserClearedBalance(), '.') + " ");
		detailmodel.addRow(vucbal);
		Vector<String> vucubal = new Vector<>();
		vucubal.add("User Current Balance");
		vucubal.add(ctype.formatFancy(acct.getUserCurrentBalance(), '.') + " ");
		detailmodel.addRow(vucubal);
		Vector<String> vurbal = new Vector<>();
		vurbal.add("User Reconciling Balance");
		vurbal.add(ctype.formatFancy(acct.getUserReconcilingBalance(), '.')
				+ " ");
		detailmodel.addRow(vurbal);
		Vector<String> vusbal = new Vector<>();
		vusbal.add("User Start Balance");
		vusbal.add(ctype.formatFancy(acct.getUserStartBalance(), '.') + " ");
		detailmodel.addRow(vusbal);
		Iterator<String> enAcct = acct.getParameterKeys().iterator();
		if (enAcct != null) {
			while (enAcct.hasNext()) {
				String strParm = enAcct.next();
				Vector<String> vusparm = new Vector<>();
				vusparm.add("Parm: "+strParm);
				vusparm.add(checkParameter(acct.getParameter(strParm)));
				detailmodel.addRow(vusparm);
			}

		}
		/*
		 * determine if there are any subaccounts, add them to the tree
		 */
		int nosubaccts = acct.getSubAccountCount();
		if (nosubaccts > 0) {
			for (int i = 0; i < nosubaccts; i++) {
				myNodeObject mynode = new myNodeObject(nodeid, acct
						.getSubAccount(i).getAccountName());
				mynode.setaccount(acct.getSubAccount(i));
				dataitem = new DefaultMutableTreeNode(mynode);
				node.add(dataitem);
			}
			/*
			 * expand the tree at the clicked leaf just in case there are
			 * sub-accounts
			 */
			JTree tree = (JTree) e.getSource();
			TreePath path = tree.getSelectionPath();
			tree.expandPath(path);
		}
		/*
		 * tell the table that it has changed
		 */
		detailmodel.fireTableDataChanged();
	}

	/*
	 * add the entries for the selected extra to the tree, this can be called
	 * whether it is a leaf or not so need to check so not adding twice
	 */
	private void displayextrasentries(myNodeObject userobj, Integer nodeid,
			DefaultMutableTreeNode node, TreeSelectionEvent e) {
		DefaultMutableTreeNode dataitem;
		@SuppressWarnings("unused")
		Account root = Main.context.getRootAccount();
		String nodepattern = nodeid.toString();
		/*
		 * determine which extra has been selected (3x00)
		 */
		switch (nodepattern.charAt(1)) {
		case '1':
			// list addresses
			AddressBook lab = objAcctBook.getAddresses();
			List<AddressBookEntry> listAddresses = lab.getAllEntries();
			int labc = listAddresses.size();
			if (labc > 0) {
				for (int i = 0; i < labc; i++) {
					myNodeObject mynode = new myNodeObject(
							EXTRAS_ADDRESS_ENTRY, listAddresses.get(i)
									.getName());
					mynode.setobject(listAddresses.get(i));
					dataitem = new DefaultMutableTreeNode(mynode);
					node.add(dataitem);
				}
			}
			break;
		/*
		 * case '2' : // list account books List<AccountBook> lac =
		 * AccountBookModel.getAccountBooks(); int lacc = lac.size(); if (lacc >
		 * 0) { for (int i=0;i<lacc;i++) { myNodeObject mynode = new
		 * myNodeObject (EXTRAS_ACCOUNT_ENTRY,lac.get(i).getName());
		 * mynode.setobject(lac.get(i)); dataitem = new
		 * DefaultMutableTreeNode(mynode); node.add(dataitem); } } break;
		 */
		case '3':
			// list budgets
			BudgetList lb = objAcctBook.getBudgets();
			List<Budget> listBudget = lb.getAllBudgets();
			int lbc = listBudget.size();
			if (lbc > 0) {
				for (int i = 0; i < lbc; i++) {
					myNodeObject mynode = new myNodeObject(EXTRAS_BUDGET_ENTRY,
							listBudget.get(i).getName());
					mynode.setobject(listBudget.get(i));
					dataitem = new DefaultMutableTreeNode(mynode);
					node.add(dataitem);
				}
			}
			break;
		case '4':
			// list currencies
			CurrencyTable lct = objAcctBook.getCurrencies();
			List<CurrencyType> listCurrBase = lct.getAllCurrencies();
			List<CurrencyType> listCurr = new ArrayList<CurrencyType>(listCurrBase);
			listCurr.sort((CurrencyType a1,CurrencyType a2)-> a1.getName().compareToIgnoreCase(a2.getName()));
			long lctc = lct.getCurrencyCount();
			if (node.isLeaf()) {
				if (lctc > 0) {
					for (int i = 0; i < lctc; i++) {
						if (listCurr.get(i).getCurrencyType() == CurrencyType.Type.CURRENCY) {
							myNodeObject mynode = new myNodeObject(
									EXTRAS_CURRENCY_ENTRY, listCurr.get(i)
											.getName());
							mynode.setobject(listCurr.get(i));
							dataitem = new DefaultMutableTreeNode(mynode);
							node.add(dataitem);
						}
					}
				}
			}
			break;
		case '5':
			// list memorized items
			ReportSpecManager lm = objAcctBook.getMemorizedItems();
			List<ReportSpec> lmgraphsBase = lm.getMemorizedGraphs();
			List<ReportSpec> lmgraphs =  new ArrayList<ReportSpec>(lmgraphsBase);
			lmgraphs.sort((ReportSpec a1,ReportSpec a2)-> a1.getName().compareToIgnoreCase(a2.getName()));
			List<ReportSpec> lmreportsBase = lm.getMemorizedReports();
			List<ReportSpec> lmreports =  new ArrayList<ReportSpec>(lmreportsBase);
			lmreports.sort((ReportSpec a1,ReportSpec a2)-> a1.getName().compareToIgnoreCase(a2.getName()));
			/*
			 * two types of memorized items, Graphs and Reports
			 */
			int lmcgraphs = lmgraphs.size();
			int lmcreports = lmreports.size();
			if (lmcgraphs > 0) {
				/*
				 * add graphs to the tree
				 */
				for (int i = 0; i < lmcgraphs; i++) {
					if (lmgraphs.get(i).isMemorized()) {
						myNodeObject mynode = new myNodeObject(
								EXTRAS_MEMORIZED_GRAPH_ENTRY,"(Graph) "+ lmgraphs.get(i)
										.getName());
						mynode.setobject(lmgraphs.get(i));
						dataitem = new DefaultMutableTreeNode(mynode);
						node.add(dataitem);
					}
				}
			}
			if (lmcreports > 0) {
				/*
				 * add reports to the tree
				 */
				for (int i = 0; i < lmcreports; i++) {
					if (lmreports.get(i).isMemorized()) {
						myNodeObject mynode = new myNodeObject(
								EXTRAS_MEMORIZED_REPORT_ENTRY, "(Report) "+lmreports.get(i)
										.getName());
						mynode.setobject(lmreports.get(i));
						dataitem = new DefaultMutableTreeNode(mynode);
						node.add(dataitem);
					}
				}
			}
			break;
		case '6':
			// list reminders
			ReminderSet ls = objAcctBook.getReminders();
			List<Reminder> listRem = ls.getAllReminders();
			long lsc = listRem.size();
			if (lsc > 0) {
				for (int i = 0; i < lsc; i++) {
					myNodeObject mynode = new myNodeObject(
							EXTRAS_REMINDER_ENTRY, listRem.get(i)
									.getDescription());
					mynode.setobject(listRem.get(i));
					dataitem = new DefaultMutableTreeNode(mynode);
					node.add(dataitem);
				}
			}

			break;
		case '7':
			// list securities
			CurrencyTable lcts = objAcctBook.getCurrencies();
			List<CurrencyType> listCurrsBase = lcts.getAllCurrencies();
			List<CurrencyType> listCurrs = new ArrayList<CurrencyType>(listCurrsBase);
			listCurrs.sort((CurrencyType a1,CurrencyType a2)-> a1.getName().compareToIgnoreCase(a2.getName()));
			long lctcs = lcts.getCurrencyCount();
			if (node.isLeaf()) {
				if (lctcs > 0) {
					for (int i = 0; i < lctcs; i++) {
						if (listCurrs.get(i).getCurrencyType() == CurrencyType.Type.SECURITY) {
							myNodeObject mynode = new myNodeObject(
									EXTRAS_CURRENCY_ENTRY, listCurrs.get(i)
											.getName());
							mynode.setobject(listCurrs.get(i));
							dataitem = new DefaultMutableTreeNode(mynode);
							node.add(dataitem);
						}
					}
				}
			}

			break;
		}
		/*
		 * expand the tree at the clicked leaf just in case there are
		 * sub-accounts
		 */
		JTree tree = (JTree) e.getSource();
		TreePath path = tree.getSelectionPath();
		tree.expandPath(path);
		detailmodel.fireTableDataChanged();
	}

	/*
	 * display the details of an extra when it is clicked
	 */
	private void displayextras(myNodeObject userobj, Integer nodeid,
			DefaultMutableTreeNode node, TreeSelectionEvent e) {
		DefaultMutableTreeNode dataitem;
		CustomDateFormat cdate = new CustomDateFormat("DD/MM/YYYY");
		detailmodel.setRowCount(0);
		String nodepattern = nodeid.toString();
		switch (nodepattern.charAt(1)) {
		case '1':
			// display address
			enumCurrentView = ViewType.ADDRESS;
			AddressBookEntry lab = (AddressBookEntry) userobj.getobject();
			Vector<String> vadname = new Vector<>();
			vadname.add("Name");
			vadname.add(lab.getName() + " ");
			detailmodel.addRow(vadname);
			Vector<String> vadadd = new Vector<>();
			vadadd.add("Address");
			vadadd.add(lab.getAddress() + " ");
			detailmodel.addRow(vadadd);
			Vector<String> vademail = new Vector<>();
			vademail.add("Email Address");
			vademail.add(lab.getEmailAddress() + " ");
			detailmodel.addRow(vademail);
			Vector<String> vadphone = new Vector<>();
			vadphone.add("Phone Number");
			vadphone.add(lab.getPhoneNumber() + " ");
			detailmodel.addRow(vadphone);
			Vector<String> vadsync = new Vector<>();
			vadsync.add("Sync Item Type");
			vadsync.add(lab.getSyncItemType() + " ");
			detailmodel.addRow(vadsync);

			break;
		case '3':
			// display budget data
			enumCurrentView = ViewType.BUDGET;
			Budget lb = (Budget) userobj.getobject();
			Vector<String> vbname = new Vector<>();
			vbname.add("Name");
			vbname.add(lb.getName() + " ");
			detailmodel.addRow(vbname);
			Vector<String> vbsync = new Vector<>();
			vbsync.add("Sync Item Type");
			vbsync.add(lb.getSyncItemType() + " ");
			detailmodel.addRow(vbsync);
			Vector<String> vbcnt = new Vector<>();
			vbcnt.add("Item Count");
			vbcnt.add(lb.getAllItems().size() + " ");
			detailmodel.addRow(vbcnt);
			Vector<String> vbper = new Vector<>();
			vbper.add("Period Type");
			if (lb.getPeriodType() == null)
				vbper.add("Not defined");
			else
				vbper.add(lb.getPeriodType().toString() + "("
						+ lb.getPeriodType().getOrder() + ") ");
			detailmodel.addRow(vbper);
			Vector<String> vbkey = new Vector<>();
			vbkey.add("Key");
			vbkey.add(lb.getKey() + " ");
			detailmodel.addRow(vbkey);
			Vector<String> vbns = new Vector<>();
			vbns.add("New Style");
			vbns.add(lb.isNewStyle() + " ");
			detailmodel.addRow(vbns);

			// list budget items (only if not already added - isLeaf)
			if (node.isLeaf()) {
				List<BudgetItem> listItems = lb.getAllItems();
				int lbc = listItems.size();
				if (lbc > 0) {
					for (int i = 0; i < lbc; i++) {
						String strName = "[" + i + "] ";
						BudgetItem objItem = listItems.get(i);
						Account objAcct = objItem.getTransferAccount();
						strName = strName + objAcct == null ? " " : objAcct
								.getAccountName() + " ";
						strName = strName
								+ cdate.format(objItem.getIntervalStartDate());
						myNodeObject mynode = new myNodeObject(
								EXTRAS_BUDGET_ENTRY + BUDGET_INCREMENT, strName);
						mynode.setobject(listItems.get(i));
						dataitem = new DefaultMutableTreeNode(mynode);
						node.add(dataitem);
					}
				}
				/*
				 * expand the tree at the clicked leaf just in case there are
				 * sub-accounts
				 */
				JTree tree = (JTree) e.getSource();
				TreePath path = tree.getSelectionPath();
				tree.expandPath(path);
			}
			break;
		case '4':
		case '7':
			// display currency
			enumCurrentView = ViewType.CURRENCY;
			CurrencyType lct = (CurrencyType) userobj.getobject();
			Vector<String> vctname = new Vector<>();
			vctname.add("Name");
			vctname.add(lct.getName() + " ");
			detailmodel.addRow(vctname);
			Vector<String> vctpref = new Vector<>();
			vctpref.add("Prefix");
			vctpref.add(lct.getPrefix() + " ");
			detailmodel.addRow(vctpref);
			Vector<String> vctsuff = new Vector<>();
			vctsuff.add("Suffix");
			vctsuff.add(lct.getSuffix() + " ");
			detailmodel.addRow(vctsuff);
			Vector<String> vctdp = new Vector<>();
			vctdp.add("Decimal Places");
			vctdp.add(lct.getDecimalPlaces() + " ");
			detailmodel.addRow(vctdp);
			Vector<String> vctraw = new Vector<>();
			vctraw.add("Rate");
			vctraw.add(new DecimalFormat("#").format(lct.getRate(baseCurr)) + " ");
			detailmodel.addRow(vctraw);
			Vector<String> vcttick = new Vector<>();
			vcttick.add("Ticker Symbol");
			vcttick.add(lct.getTickerSymbol() + " ");
			detailmodel.addRow(vcttick);
			Vector<String> vctID = new Vector<>();
			vctID.add("ID");
			vctID.add(lct.getIDString() + " ");
			detailmodel.addRow(vctID);
			Vector<String> vcthide = new Vector<>();
			vcthide.add("Hide in UI");
			vcthide.add(lct.getHideInUI() + " ");
			detailmodel.addRow(vcthide);
			Vector<String> vcteffd = new Vector<>();
			vcteffd.add("Effective Date");
			vcteffd.add(cdate.format(lct.getEffectiveDateInt()) + " ");
			detailmodel.addRow(vcteffd);
			Vector<String> vctsync = new Vector<>();
			vctsync.add("Sync Item Type");
			vctsync.add(lct.getSyncItemType() + " ");
			detailmodel.addRow(vctsync);
			Vector<String> vctctype = new Vector<>();
			vctctype.add("Currency Type");
			vctctype.add(lct.getCurrencyType().toString() + " ");
			detailmodel.addRow(vctctype);
			if(lct.getCurrencyType()== CurrencyType.Type.SECURITY) {
				Vector<String> vctcurr = new Vector<>();
				vctcurr.add("Security Currency");
				vctcurr.add(lct.getParameter("relative_to_currid") + " ");
				detailmodel.addRow(vctcurr);
			}
			Iterator<String> ctAcct = lct.getParameterKeys().iterator();
			if (ctAcct != null) {
				while (ctAcct.hasNext()) {
					String strParm = ctAcct.next();
					Vector<String> vusparm = new Vector<>();
					vusparm.add("Parm: "+strParm);
					vusparm.add(checkParameter(lct.getParameter(strParm)));
					detailmodel.addRow(vusparm);
				}

			}
			/*
			 * TagSet tsTags = lct.getTags(); if (tsTags != null)
			 * if(tsTags.getTagCount() > 0) { for (int
			 * iTag=0;iTag<tsTags.getTagCount();iTag++) { Vector<String> vcttag
			 * = new Vector<>();
			 * vcttag.add("Tag : "+tsTags.getTagAt(iTag).getKey());
			 * vcttag.add(tsTags.getTagAt(iTag).getValue());
			 * detailmodel.addRow(vcttag); } }
			 */
			// list currency snap shot items (only if not already added -
			// isLeaf)
			if (node.isLeaf()) {
				List<CurrencySnapshot> listCSS = lct.getSnapshots();
				int lctc = listCSS.size();
				int lctstart;
				if (lctc > 10)
					lctstart = lctc - 10;
				else
					lctstart = 0;
				if (lctc > 0) {
					for (int i = lctc - 1; i >= lctstart; i--) {
						myNodeObject mynode;
						String strName = "[" + i + "] ";
						CurrencySnapshot objSS = listCSS.get(i);
						strName = strName + cdate.format(objSS.getDateInt());

						if (nodepattern.charAt(1) == '4')
							mynode = new myNodeObject(EXTRAS_CURRENCY_ENTRY
									+ CURRENCY_INCREMENT, strName);
						else
							mynode = new myNodeObject(EXTRAS_SECURITY_ENTRY
									+ SECURITY_INCREMENT, strName);
						mynode.setobject(listCSS.get(i));
						dataitem = new DefaultMutableTreeNode(mynode);
						node.add(dataitem);
					}
				}
				/*
				 * expand the tree at the clicked leaf just in case there are
				 * sub-accounts
				 */
				JTree tree = (JTree) e.getSource();
				TreePath path = tree.getSelectionPath();
				tree.expandPath(path);
			}
			break;
		case '5':
			// display memorized item
			enumCurrentView = ViewType.MEMORIZED;
			ReportSpec stitem = (ReportSpec) userobj.getobject();
			ReportSpec.ReportGenerator objrepgen = stitem.getReportGenerator();
			SyncRecord srParms = stitem.getReportParameters();
			Vector<String> vmname = new Vector<>();
			vmname.add("Name");
			vmname.add(stitem.getName());
			detailmodel.addRow(vmname);
			Vector<String> vmsync = new Vector<>();
			vmsync.add("Sync Item Type");
			vmsync.add(stitem.getSyncItemType() + " ");
			detailmodel.addRow(vmsync);
			Vector<String> vmmem = new Vector<>();
			vmmem.add("Is memorized");
			vmmem.add(stitem.isMemorized() ? "true" : "false");
			detailmodel.addRow(vmmem);
			Vector<String> vmgid = new Vector<>();
			vmgid.add("Generator ID");
			vmgid.add(objrepgen.getLongID());
			detailmodel.addRow(vmgid);
			Vector<String> vmgrt = new Vector<>();
			vmgrt.add("Report Type");
			vmgrt.add(objrepgen.getReportType().asString());
			detailmodel.addRow(vmgrt);

			Set<String> setKeys = srParms.keySet();
			String[] keys = setKeys.toArray(new String[setKeys.size()]);

			for (String keyitem : keys) {
				Vector<String> vm = new Vector<>();
				vm.add(keyitem);
				vm.add(srParms.getString(keyitem, "unknown") + " ");
				detailmodel.addRow(vm);
			}
			break;
		case '6':
			// display reminder
			enumCurrentView = ViewType.REMINDER;
			Reminder lrobj = (Reminder) userobj.getobject();
			objCrntReminder = lrobj;
			Vector<String> vrid = new Vector<>();
			vrid.add("ID");
			vrid.add(lrobj.getUUID());
			detailmodel.addRow(vrid);
			Vector<String> vrname = new Vector<>();
			vrname.add("Name");
			vrname.add(lrobj.toString() + " ");
			detailmodel.addRow(vrname);
			Vector<String> vrdesc = new Vector<>();
			vrdesc.add("Description");
			vrdesc.add(lrobj.getDescription() + " ");
			detailmodel.addRow(vrdesc);
			Vector<String> vridt = new Vector<>();
			vridt.add("Initial Date");
			vridt.add(cdate.format(lrobj.getInitialDateInt()) + " ");
			detailmodel.addRow(vridt);
			Vector<String> vrldt = new Vector<>();
			vrldt.add("Last Date");
			vrldt.add(cdate.format(lrobj.getLastDateInt()) + " ");
			detailmodel.addRow(vrldt);
			Vector<String> vrrt = new Vector<>();
			vrrt.add("Reminder Type");
			vrrt.add(lrobj.getReminderType() + " ");
			detailmodel.addRow(vrrt);
			Vector<String> vrrd = new Vector<>();
			vrrd.add("Repeat Daily");
			vrrd.add(lrobj.getRepeatDaily() + " ");
			detailmodel.addRow(vrrd);
			Vector<String> vrrm = new Vector<>();
			vrrm.add("Repeat Monthly");
			int[] irm = lrobj.getRepeatMonthly();
			if (irm.length > 0) {
				vrrm.add(irm.length + " entries");
				detailmodel.addRow(vrrm);
				for (int i=0;i<irm.length  && i < 10;i++) {
					Vector<String> vrrmi = new Vector<>();
					vrrmi.add ("Repeat Month item " + i);
					vrrmi.add(irm[i] + " ");
					detailmodel.addRow(vrrmi);
				}
			}
			else {
				vrrm.add("0 ");
				detailmodel.addRow(vrrm);
			}
			Vector<String> vrrmm = new Vector<>();
			vrrmm.add("Repeat Monthly Modifier");
			vrrmm.add(lrobj.getRepeatMonthlyModifier() + " ");
			detailmodel.addRow(vrrmm);
			Vector<String> vrrwd = new Vector<>();
			vrrwd.add("Repeat Weekly Days");
			irm = lrobj.getRepeatWeeklyDays();
			if (irm.length > 0) {
				vrrwd.add(irm.length + " entries");
				detailmodel.addRow(vrrwd);
				for (int i=0;i<irm.length  && i < 10;i++) {
					Vector<String> vrrwdi = new Vector<>();
					vrrwdi.add ("Repeat Weekly item " + i);
					vrrwdi.add(irm[i] + " ");
					detailmodel.addRow(vrrwdi);
				}
			}
			else {
				vrrwd.add("0 ");
				detailmodel.addRow(vrrwd);
			}
			Vector<String> vrrwm = new Vector<>();
			vrrwm.add("Repeat Weekly Modifier");
			vrrwm.add(lrobj.getRepeatWeeklyModifier() + " ");
			detailmodel.addRow(vrrwm);
			Vector<String> vrry = new Vector<>();
			vrry.add("Repeat Yearly");
			vrry.add(lrobj.getRepeatYearly() + " ");
			detailmodel.addRow(vrry);
			Vector<String> vrTran = new Vector<>();
			ParentTxn vrtxn = lrobj.getTransaction();
			vrTran.add("Transaction");
			if (vrtxn == null) {
				vrTran.add("No");
				detailmodel.addRow(vrTran);
			}
			else {
				CurrencyType ctype = null;
				CurrencyTable ctab = objAcctBook.getCurrencies();
				CurrencyType ctgbp = ctab.getCurrencyByIDString("GBP");
				Vector<String> vecid = new Vector<>();
				vecid.add("Tran: ID");
				vecid.add(vrtxn.getUUID());
				Vector<String> vecacct = new Vector<>();
				vecacct.add("Tran: Account");

				if (vrtxn.getAccount() == null) {
					vecacct.add("None");
					ctype = ctgbp;
				} else {
					vecacct.add(vrtxn.getAccount().getAccountName());
					ctype = vrtxn.getAccount().getCurrencyType();
				}
				detailmodel.addRow(vecacct);
				Vector<String> vecdesc = new Vector<>();
				vecdesc.add("Tran: Description");
				vecdesc.add(vrtxn.getDescription());
				detailmodel.addRow(vecdesc);
				Vector<String> vecdate = new Vector<>();
				vecdate.add("Tran: Date");
				vecdate.add(cdate.format(vrtxn.getDateInt()));
				detailmodel.addRow(vecdate);
				Vector<String> vecvalue = new Vector<>();
				vecvalue.add("Tran: Value");
				vecvalue.add(ctype.formatFancy(vrtxn.getValue(), '.'));
				detailmodel.addRow(vecvalue);
				Vector<String> vecttype = new Vector<>();
				vecttype.add("Tran: Transfer Type");
				vecttype.add(vrtxn.getTransferType());
				detailmodel.addRow(vecttype);
				Vector<String> vecps = new Vector<>();
				vecps.add("Tran: Parent/Split");
				vecps.add("Parent");
				detailmodel.addRow(vecps);
				Vector<String> veccheque = new Vector<>();
				veccheque.add("Tran: Cheque");

				veccheque.add(vrtxn.getCheckNumber());
				detailmodel.addRow(veccheque);
				Vector<String> vecstatus = new Vector<>();
				vecstatus.add("Tran: Status");
				vecstatus.add(String.valueOf(vrtxn.getClearedStatus()));
				detailmodel.addRow(vecstatus);
				SyncRecord srTran = vrtxn.getTags();
				if (srTran != null) {
					Set<String> setKeysrmt = srTran.keySet();
					String[] keysrmt = setKeysrmt.toArray(new String[setKeysrmt.size()]);

					for (String keyitem : keysrmt) {
						Vector<String> vm = new Vector<>();
						vm.add("Tran: Tag:" + keyitem);
						vm.add(srTran.getString(keyitem, "unknown") + " ");
						detailmodel.addRow(vm);
					}
				}
				List<String> listKeywords = vrtxn.getKeywords();
				if (listKeywords != null) {
					for (String item : listKeywords) {
						Vector<String> vmkw = new Vector<>();
						vmkw.add("Keyword:");
						vmkw.add(item);
						detailmodel.addRow(vmkw);
					}

				}
			}
			SyncRecord srTranrm = lrobj.getTags();
			if (srTranrm != null) {
				Set<String> setKeysrm = srTranrm.keySet();
				String[] keysrm = setKeysrm.toArray(new String[setKeysrm.size()]);

				for (String keyitem : keysrm) {
					Vector<String> vm = new Vector<>();
					vm.add("Tag:" + keyitem);
					vm.add(srTranrm.getString(keyitem, "unknown") + " ");
					detailmodel.addRow(vm);
				}
			}
			int iParms = lrobj.getParameterCount();
			if (iParms > 0) {
				Set<String> setKeysrm = lrobj.getParameterKeys();
				String[] keysrm = setKeysrm.toArray(new String[setKeysrm.size()]);
				for (String keyitem : keysrm) {
					Vector<String> vp = new Vector<>();
					vp.add("Parm:" + keyitem);
					vp.add(lrobj.getParameter(keyitem, "unknown") + " ");
					detailmodel.addRow(vp);
				}
			}
			break;
		}
		/*
		 * tell the table that it has changed
		 */
		detailmodel.fireTableDataChanged();
	}

	/*
	 * displays a single budget item
	 */
	private void displaybudgetitem(myNodeObject userobj, Integer nodeid,
			DefaultMutableTreeNode node, TreeSelectionEvent e) {
		CustomDateFormat cdate = new CustomDateFormat("DD/MM/YYYY");
		detailmodel.setRowCount(0);
		BudgetItem bitem = (BudgetItem) userobj.getobject();
		CurrencyType tctype = (bitem.getTransferAccount() == null) ? null
				: bitem.getTransferAccount().getCurrencyType();
		Vector<String> vbiacct = new Vector<>();
		vbiacct.add("Account Name");
		vbiacct.add((bitem.getAccount() == null) ? "unknown" : bitem
				.getAccount().getAccountName() + " ");
		detailmodel.addRow(vbiacct);
		Vector<String> vbiamt = new Vector<>();
		vbiamt.add("Amount");
		vbiamt.add(((tctype == null) ? String.valueOf(bitem.getAmount())
				: tctype.formatFancy(bitem.getAmount(), '.')) + " ");
		detailmodel.addRow(vbiamt);
		Vector<String> vbicur = new Vector<>();
		vbicur.add("Currency");
		vbicur.add(bitem.getCurrency() + " ");
		detailmodel.addRow(vbicur);
		Vector<String> vbiint = new Vector<>();
		vbiint.add("Interval");
		vbiint.add(intervaltypes.get(bitem.getInterval()) + "("
				+ bitem.getInterval() + ")");
		detailmodel.addRow(vbiint);
		Vector<String> vbiintsd = new Vector<>();
		vbiintsd.add("Interval Start Date");
		vbiintsd.add(cdate.format(bitem.getIntervalStartDate()));
		detailmodel.addRow(vbiintsd);
		Vector<String> vbiinted = new Vector<>();
		vbiinted.add("Interval End Date");
		vbiinted.add(cdate.format(bitem.getIntervalEndDate()));
		detailmodel.addRow(vbiinted);
		Vector<String> vbitacct = new Vector<>();
		vbitacct.add("Transfer Accout Name");
		vbitacct.add((bitem.getTransferAccount() == null) ? "unknown" : bitem
				.getTransferAccount().getAccountName() + " ");
		detailmodel.addRow(vbitacct);
		Vector<String> vbiinc = new Vector<>();
		vbiinc.add("Is Income");
		vbiinc.add(bitem.isIncome() + " ");
		detailmodel.addRow(vbiinc);
		Vector<String> vbisync = new Vector<>();
		vbisync.add("Sync Item Type");
		vbisync.add(bitem.getSyncItemType() + " ");
		detailmodel.addRow(vbisync);
		detailmodel.fireTableDataChanged();
	}

	/*
	 * displays a single currency item
	 */
	private void displaycurrencyitem(myNodeObject userobj, Integer nodeid,
			DefaultMutableTreeNode node, TreeSelectionEvent e) {
		CustomDateFormat cdate = new CustomDateFormat("DD/MM/YYYY");
		detailmodel.setRowCount(0);
		CurrencySnapshot ctitem = (CurrencySnapshot) userobj.getobject();
		Vector<String> vbiacct = new Vector<>();
		vbiacct.add("Date");
		vbiacct.add(cdate.format(ctitem.getDateInt()));
		detailmodel.addRow(vbiacct);
		Vector<String> vbudhamt = new Vector<>();
		vbudhamt.add("User Daily High");
		vbudhamt.add(String.valueOf(ctitem.getDailyHigh()));
		detailmodel.addRow(vbudhamt);
		Vector<String> vbudlamt = new Vector<>();
		vbudlamt.add("User Daily Low");
		vbudlamt.add(String.valueOf(ctitem.getDailyLow()));
		detailmodel.addRow(vbudlamt);
		Vector<String> vburamt = new Vector<>();
		vburamt.add("User Rate");
		vburamt.add(String.valueOf(ctitem.getRate()));
		detailmodel.addRow(vburamt);
		detailmodel.fireTableDataChanged();
		Iterator<String> ctAcct = ctitem.getParameterKeys().iterator();
		if (ctAcct != null) {
			while (ctAcct.hasNext()) {
				String strParm = ctAcct.next();
				Vector<String> vusparm = new Vector<>();
				vusparm.add("Parm: "+strParm);
				vusparm.add(checkParameter(ctitem.getParameter(strParm)));
				detailmodel.addRow(vusparm);
			}

		}


	}

	public void viewTrans() {
		CustomDateFormat cdate = new CustomDateFormat("DD/MM/YYYY");
		transFrm = new JFrame("Moneydance Transactions");
		panTrans = new JPanel(new BorderLayout());
		final JPanel panTop = new JPanel(new GridBagLayout());
		final JPanel panMid = new JPanel();
		final JPanel panBot = new JPanel(new GridBagLayout());
		GridBagConstraints con = new GridBagConstraints();
		CurrencyType ctype = null;
		CurrencyTable ctab = objAcctBook.getCurrencies();
		CurrencyType ctgbp = ctab.getCurrencyByIDString("GBP");
		panTrans.setBorder(new EmptyBorder(5, 5, 5, 5));
		trantable = new MyTranTable(new DefaultTableModel(transcolumns, 0),
				this);
		trantable.setAutoCreateRowSorter(true);
		DefaultTableModel tranmodel = (DefaultTableModel) trantable.getModel();
		JScrollPane pscroll = new JScrollPane(trantable);
		pscroll.setPreferredSize(new Dimension(1000, 600));
		con.gridx = 0;
		con.gridy = 0;
		JLabel txtstart = new JLabel("Start Date : ");
		panTop.add(txtstart, con);
		con.gridx = 1;
		JLabel stdate = new JLabel(cdate.format(startDate));
		panTop.add(stdate, con);
		con.gridx = 2;
		JLabel txtend = new JLabel(" End Date : ");
		panTop.add(txtend, con);
		con.gridx = 3;
		JLabel endate = new JLabel(cdate.format(endDate));
		panTop.add(endate, con);
		panTrans.add(panTop, BorderLayout.PAGE_START);
		panMid.add(pscroll);
		panTrans.add(panMid, BorderLayout.CENTER);
		if (enumCurrentView == ViewType.REMINDER && objCrntReminder != null &&
				objCrntReminder.getReminderType() == Reminder.Type.TRANSACTION){
			AbstractTxn txn = objCrntReminder.getTransaction();
			Vector<String> vec = new Vector<>();
			vec.add(txn.getUUID());
			vec.add(new DecimalFormat("#").format(txn.getOldTxnID()) + " ");
			if (txn.getAccount() == null) {
				vec.add("None");
				ctype = ctgbp;
			} else {
				vec.add(txn.getAccount().getAccountName());
				ctype = txn.getAccount().getCurrencyType();
			}
			vec.add(txn.getDescription());
			vec.add(cdate.format(txn.getDateInt()));
			vec.add(ctype.formatFancy(txn.getValue(), '.'));
			vec.add(txn.getTransferType());
			if (txn instanceof ParentTxn)
				vec.add("P");
			else
				vec.add("S");
			vec.add(txn.getCheckNumber());
			vec.add(String.valueOf(txn.getClearedStatus()));
			tranmodel.addRow(vec);
			for (int i = 0; i<txn.getOtherTxnCount();i++){
				AbstractTxn txn2 = txn.getOtherTxn(i);
				vec = new Vector<>();
				vec.add(txn2.getUUID());
				vec.add(new DecimalFormat("#").format(txn2.getOldTxnID()) + " ");
				if (txn2.getAccount() == null) {
					vec.add("None");
					ctype = ctgbp;
				} else {
					vec.add(txn2.getAccount().getAccountName());
					ctype = txn2.getAccount().getCurrencyType();
				}
				vec.add(txn2.getDescription());
				vec.add(cdate.format(txn2.getDateInt()));
				vec.add(ctype.formatFancy(txn2.getValue(), '.'));
				vec.add(txn2.getTransferType());
				if (txn instanceof ParentTxn)
					vec.add("P");
				else
					vec.add("S");
				vec.add(txn2.getCheckNumber());
				vec.add(String.valueOf(txn2.getClearedStatus()));
				tranmodel.addRow(vec);
			}			
		}
		else {
		txnSet = objAcctBook.getTransactionSet();
			if (this.includeAllTrans)
				tsTrans = txnSet.getAllTxns();
			else {
				if (this.includeTransbyAccounts) {
					if (lastAcct == null)
						return;
					if (!(lastAcct instanceof Account))
						return;
					tsTrans = txnSet.getTransactionsForAccount(lastAcct);
				} else
					return;
			}
			for (int i = 0; i < tsTrans.getSize(); i++) {
				AbstractTxn txn = tsTrans.getTxn(i);
				if (txn.getDateInt() < this.startDate
						|| txn.getDateInt() > this.endDate)
					continue;
				Vector<String> vec = new Vector<>();
				vec.add(txn.getUUID());
				vec.add(new DecimalFormat("#").format(txn.getOldTxnID()) + " ");
				if (txn.getAccount() == null) {
					vec.add("None");
					ctype = ctgbp;
				} else {
					vec.add(txn.getAccount().getAccountName());
					ctype = txn.getAccount().getCurrencyType();
				}
				vec.add(txn.getDescription());
				vec.add(cdate.format(txn.getDateInt()));
				vec.add(ctype.formatFancy(txn.getValue(), '.'));
				vec.add(txn.getTransferType());
				if (txn instanceof ParentTxn)
					vec.add("P");
				else
					vec.add("S");
				vec.add(txn.getCheckNumber());
				vec.add(String.valueOf(txn.getClearedStatus()));
				tranmodel.addRow(vec);
			}
		}
		tranmodel.fireTableDataChanged();
		con.gridy = 2;
		con.gridwidth = 1;
		con.gridx = 0;
		closeButton = new JButton("Close");
		closeButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				closetran();
			}
		});
		panBot.add(closeButton, con);
		panTrans.add(panBot, BorderLayout.PAGE_END);
		// Display the window.
		transFrm.add(panTrans);
		transFrm.pack();
		transFrm.setVisible(true);

	}

	/*
	 * display an individual transaction
	 */
	public void displayTransaction(int iRow) {
		CustomDateFormat cdate = new CustomDateFormat("DD/MM/YYYY");
		singleTransFrm = new JFrame("Transaction Detail");
		panSingleTrans = new JPanel(new BorderLayout());
		CurrencyType ctype = null;
		CurrencyTable ctab = objAcctBook.getCurrencies();
		CurrencyType ctgbp = ctab.getCurrencyByIDString("GBP");
		panSingleTrans.setBorder(new EmptyBorder(5, 5, 5, 5));
		tabTran = new JTable(new DefaultTableModel(columnNames, 0));
		tabTran.setAutoCreateRowSorter(true);
		DefaultTableModel modTran = (DefaultTableModel) tabTran.getModel();
		JScrollPane pscroll = new JScrollPane(tabTran);
		/*
		 * find transaction
		 */
		String strTxnID = (String) (trantable.getValueAt(iRow, 0));
		AbstractTxn txn = tsTrans.getTxnByID(strTxnID);
		Vector<String> vecid = new Vector<>();
		vecid.add("ID");
		vecid.add(txn.getUUID());
		Vector<String> vecoid = new Vector<>();
		vecoid.add("Old ID");
		vecoid.add(new DecimalFormat("#").format(txn.getOldTxnID()) + " ");
		modTran.addRow(vecoid);
		Vector<String> vecacct = new Vector<>();
		vecacct.add("Account");
		if (txn.getAccount() == null) {
			vecacct.add("None");
			ctype = ctgbp;
		} else {
			vecacct.add(txn.getAccount().getAccountName());
			ctype = txn.getAccount().getCurrencyType();
		}
		modTran.addRow(vecacct);
		Vector<String> vecdesc = new Vector<>();
		vecdesc.add("Description");
		vecdesc.add(txn.getDescription());
		modTran.addRow(vecdesc);
		Vector<String> vecdate = new Vector<>();
		vecdate.add("Date");
		vecdate.add(cdate.format(txn.getDateInt()));
		modTran.addRow(vecdate);
		Vector<String> vecvalue = new Vector<>();
		vecvalue.add("Value");
		vecvalue.add(ctype.formatFancy(txn.getValue(), '.'));
		modTran.addRow(vecvalue);
		Vector<String> vecttype = new Vector<>();
		vecttype.add("Transfer Type");
		vecttype.add(txn.getTransferType());
		modTran.addRow(vecttype);
		Vector<String> vecps = new Vector<>();
		vecps.add("Parent/Split");
		if (txn instanceof ParentTxn)
			vecps.add("Parent");
		else
			vecps.add("Split");
		modTran.addRow(vecps);
		Vector<String> veccheque = new Vector<>();
		veccheque.add("Cheque");

		veccheque.add(txn.getCheckNumber());
		modTran.addRow(veccheque);
		Vector<String> vecstatus = new Vector<>();
		vecstatus.add("Status");
		vecstatus.add(String.valueOf(txn.getClearedStatus()));
		modTran.addRow(vecstatus);
		Vector<String> vecotc = new Vector<>();
		vecotc.add("Num other trans");
		vecotc.add(String.valueOf(txn.getOtherTxnCount()));
		modTran.addRow(vecotc);
		SyncRecord srTran = txn.getTags();
		if (srTran != null) {
			Set<String> setKeys = srTran.keySet();
			String[] keys = setKeys.toArray(new String[setKeys.size()]);

			for (String keyitem : keys) {
				Vector<String> vm = new Vector<>();
				vm.add("Tag:" + keyitem);
				vm.add(srTran.getString(keyitem, "unknown") + " ");
				modTran.addRow(vm);
			}
		}
		List<String> listKeywords = txn.getKeywords();
		if (listKeywords != null) {
			for (String item : listKeywords) {
				Vector<String> vmkw = new Vector<>();
				vmkw.add("Keyword:");
				vmkw.add(item);
				modTran.addRow(vmkw);
			}

		}
		modTran.fireTableDataChanged();
		panSingleTrans.add(pscroll, BorderLayout.CENTER);
		closeTranButton = new JButton("Close");
		closeTranButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				closesingletran();
			}
		});
		closeTranButton.setMaximumSize(new Dimension(40, 20));
		panSingleTrans.add(closeTranButton, BorderLayout.PAGE_END);
		// Display the window.
		singleTransFrm.add(panSingleTrans);
		singleTransFrm.pack();
		singleTransFrm.setVisible(true);

	}

	protected void closetran() {
		if (panSingleTrans != null)	
			panSingleTrans.setVisible(false);
		if (singleTransFrm != null)
			singleTransFrm.dispose();
		if (panTrans != null)	
			panTrans.setVisible(false);
		if (transFrm != null)
			transFrm.dispose();
	}

	protected void closesingletran() {
		if (panSingleTrans != null)	
			panSingleTrans.setVisible(false);
		if (singleTransFrm != null)
			singleTransFrm.dispose();
	}

	/** Close Window */
	protected void close() {
		if (panTrans != null)
			closetran();
		this.setVisible(false);
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.dispose();
	}

	/*
	 * Create the original tree nodes based on choices made
	 */
	private void createNodes(DefaultMutableTreeNode top) {
		DefaultMutableTreeNode datatype = null;
		DefaultMutableTreeNode dataitem = null;
		int noaccounts;
		accounts = new HashMap<Account.AccountType, List<Account>>();
		loadbaseaccounts();
		datatype = new DefaultMutableTreeNode(new myNodeObject(ACCOUNTS_NODE,
				"Accounts"));
		top.add(datatype);
		if (this.includeBankAccounts) {
			List<Account> l = accounts.get(Account.AccountType.BANK);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
				dataitem = new DefaultMutableTreeNode(new myNodeObject(BANK_NODE,
					"Banks(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		if (this.includeInvestments) {
			List<Account> l = accounts.get(Account.AccountType.INVESTMENT);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
			dataitem = new DefaultMutableTreeNode(new myNodeObject(
					INVESTMENT_NODE, "Investments(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		if (this.includeAssets) {
			List<Account> l = accounts.get(Account.AccountType.ASSET);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
				dataitem = new DefaultMutableTreeNode(new myNodeObject(ASSET_NODE,
					"Assets(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		if (this.includeCreditCards) {
			List<Account> l = accounts.get(Account.AccountType.CREDIT_CARD);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
				dataitem = new DefaultMutableTreeNode(new myNodeObject(
					CREDIT_CARD_NODE, "Credit Cards(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		if (this.includeLiabilities) {
			List<Account> l = accounts.get(Account.AccountType.LIABILITY);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
				dataitem = new DefaultMutableTreeNode(new myNodeObject(
					LIABILITY_NODE, "Liabilities(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		if (this.includeLoans) {
			List<Account> l = accounts.get(Account.AccountType.LOAN);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
			dataitem = new DefaultMutableTreeNode(new myNodeObject(LOAN_NODE,
					"Loans(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		datatype = new DefaultMutableTreeNode(new myNodeObject(CATEGORIES_NODE,
				"Categories"));
		top.add(datatype);
		if (this.includeIncomecat) {
			List<Account> l = accounts.get(Account.AccountType.INCOME);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
				dataitem = new DefaultMutableTreeNode(new myNodeObject(INCOME_NODE,
					"Income(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		if (this.includeExpensecat) {
			List<Account> l = accounts.get(Account.AccountType.EXPENSE);
			if (l == null)
				noaccounts = 0;
			else {
				noaccounts = l.size();
				l.sort((Account a1, Account a2) -> a1.getAccountName().compareToIgnoreCase(a2.getAccountName()));
			}
				dataitem = new DefaultMutableTreeNode(new myNodeObject(
					EXPENSE_NODE, "Expense(" + noaccounts + ")"));
			datatype.add(dataitem);
		}
		datatype = new DefaultMutableTreeNode(new myNodeObject(EXTRAS_NODE,
				"Extras"));
		top.add(datatype);
		if (this.includeAddressBook) {
			AddressBook lab = objAcctBook.getAddresses();
			List<AddressBookEntry> listABE = lab.getAllEntries();
			if (listABE == null)
				noaccounts=0;
			else
				noaccounts=listABE.size();
				dataitem = new DefaultMutableTreeNode(new myNodeObject(
					EXTRAS_ADDRESS_NODE, "Addresses Book(" +noaccounts
							+ ")"));
			datatype.add(dataitem);
		}
		if (this.includeBudgets) {
			BudgetList lab = objAcctBook.getBudgets();
			if (lab==null)
				noaccounts=0;
			else
				noaccounts=lab.getAllBudgets().size();
			dataitem = new DefaultMutableTreeNode(new myNodeObject(
					EXTRAS_BUDGET_NODE, "Budgets(" + noaccounts
							+ ")"));
			datatype.add(dataitem);
		}
		if (this.includeCurrencies) {
			CurrencyTable lc = objAcctBook.getCurrencies();
			dataitem = new DefaultMutableTreeNode(new myNodeObject(
					EXTRAS_CURRENCY_NODE, "Currencies"
							+ getCurrencyCount(lc, CurrencyType.Type.CURRENCY)));
			datatype.add(dataitem);
		}
		if (this.includeSecurities) {
			CurrencyTable lc = objAcctBook.getCurrencies();
			dataitem = new DefaultMutableTreeNode(new myNodeObject(
					EXTRAS_SECURITY_NODE, "Securities"
							+ getCurrencyCount(lc, CurrencyType.Type.SECURITY)));
			datatype.add(dataitem);
		}
		if (this.includeMemorizedItems) {
			ReportSpecManager lm = objAcctBook.getMemorizedItems();
			int lmi = lm.getMemorizedGraphs().size()
					+ lm.getMemorizedReports().size();
			dataitem = new DefaultMutableTreeNode(new myNodeObject(
					EXTRAS_MEMORIZED_NODE, "Memorized Items(" + lmi + ")"));
			datatype.add(dataitem);
		}
		if (this.includeReminders) {
			ReminderSet ls = objAcctBook.getReminders();
			dataitem = new DefaultMutableTreeNode(new myNodeObject(
					EXTRAS_REMINDER_NODE, "Reminders("
							+ ls.getAllReminders().size() + ")"));
			datatype.add(dataitem);
		}
	}

	/*
	 * loads the top level accounts for adding to the tree
	 */
	private void loadbaseaccounts() {
		Account.AccountType accounttype;
		Account root = Main.context.getRootAccount();
		int sz = root.getSubAccountCount();
		for (int i = 0; i < sz; i++) {
			Account acct = root.getSubAccount(i);
			accounttype = acct.getAccountType();
			List<Account> l = accounts.get(accounttype);
			if (l == null)
				accounts.put(accounttype, l = new ArrayList<Account>());
			l.add(acct);
		}

	}

	/*
	 * count the type of currencies/securities
	 */
	private String getCurrencyCount(CurrencyTable ctEntries,
			CurrencyType.Type ctType) {
		List<CurrencyType> arrTypes = ctEntries.getAllCurrencies();
		int iCount = 0;
		for (int i = 0; i < ctEntries.getCurrencyCount(); i++) {
			if (arrTypes.get(i).getCurrencyType() == ctType)
				iCount++;
		}
		return "(" + iCount + ")";
	}
	private String checkParameter(String param) {
		try {
			Long paramValue = Long.decode(param);
			if (paramValue < 39600000L)
				return param;
			if (paramValue>10445284800000L)
				return param;
			LocalDateTime time = LocalDateTime.ofInstant(Instant.ofEpochMilli(paramValue), ZoneId.systemDefault());
			return param+" - "+ format1.format(time);
		}
		catch (NumberFormatException e) {
		}
		return param;
	}
}
