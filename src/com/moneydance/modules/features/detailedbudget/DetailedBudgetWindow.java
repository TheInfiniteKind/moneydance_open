package com.moneydance.modules.features.detailedbudget;

import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.swing.Box;
import javax.swing.JButton;
import javax.swing.JEditorPane;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.WindowConstants;
import javax.swing.border.EmptyBorder;
import javax.swing.filechooser.FileFilter;

import com.moneydance.apps.md.controller.Util;
import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.AwtUtil;

/** Detailed Budget.
 * Can include subtotals per week, month, year.
 * With subtotals it will always show Actual Amount. You can
 * include the budgeted Amount with that, and the difference.
 * Does NOT give budgeted amount for an item if not in
 * the budgeted period (ie does not do what MoneyDance Budget report, 
 * add per year and divide per period).
 * */
public class DetailedBudgetWindow extends JFrame {
	private static final long serialVersionUID = 1L;
	private Main extension;
	private Budget budget;
	private String budgetPeriod;
	private Date startDate;
	private Date endDate;
	private String subTotalBy;
	private boolean budgetWithSubtotal;
	private boolean diffWithSubtotal;
	private boolean showAllAccounts;
	private boolean subtotalsForParentCategories;
	
	private JEditorPane txtReport;
	private JButton printButton;
	private JButton saveButton;
	private JButton closeButton;

	/** Categories to show in report*/
	private List<Account> categories = null;
	
	public static final DecimalFormat CURR_FMT = new DecimalFormat("#,##0");
	public static final DecimalFormat CENTS_FMT = new DecimalFormat("00");
	public static final SimpleDateFormat DT_FMT = new SimpleDateFormat("yyyy-MM-dd");
	
	public static final int START_DAY_OF_WEEK = Calendar.MONDAY;
	
	public static final int INCOME_ACCOUNTS = 0;
	public static final int EXPENSE_ACCOUNTS = 1;
	public static final int DIFF_ACCOUNTS = 2; // Income - Expense
	
	// -------------------------------------------
	
	/**
	 * Detailed Budget Report
	 * @param budget
	 * @param budgetPeriod
	 * @param startDate
	 * @param endDate
	 * @param subTotalBy
	 * @param budgetWithSubtotal
	 * @param diffWithSubtotal
	 */
	public DetailedBudgetWindow(Main extension, Budget budget, String budgetPeriod,
			Date startDate, Date endDate, String subTotalBy,
			boolean budgetWithSubtotal, boolean diffWithSubtotal,
			boolean showAllAccounts,
			boolean subtotalsForParentCategories) {
	    super("Detailed Budget");
//	    System.out.println("Detailed Budget");
	    this.extension = extension;
	    this.budget = budget;
	    this.budgetPeriod = budgetPeriod;
	    this.startDate = startDate;
	    this.endDate = endDate;
	    this.subTotalBy = subTotalBy;
	    this.budgetWithSubtotal = budgetWithSubtotal;
	    this.diffWithSubtotal = diffWithSubtotal;
	    this.showAllAccounts = showAllAccounts;
	    this.subtotalsForParentCategories = subtotalsForParentCategories;

	    // Get a list of all categories
		categories = getCategories();

	    JPanel p = new JPanel(new GridBagLayout());
	    p.setBorder(new EmptyBorder(10,10,10,10));

	    // Text Area
	    txtReport = new JEditorPane();
	    txtReport.setEditable(false);
	    txtReport.setContentType("text/html");
	    txtReport.setText(getReportStr());
	    p.add(new JScrollPane(txtReport), AwtUtil.getConstraints(0,0,1,1,4,1,true,true));
	    p.add(Box.createVerticalStrut(8), AwtUtil.getConstraints(0,2,0,0,1,1,false,false));
	    printButton = new JButton("Print");
	    printButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				print();
			}
		});
	    p.add(printButton, AwtUtil.getConstraints(0,3,1,0,1,1,false,true));
	    saveButton = new JButton("Save");
	    saveButton.addActionListener(new ActionListener() {
	    	public void actionPerformed(ActionEvent e) {
	    		save();
	    	}
	    });
	    p.add(saveButton, AwtUtil.getConstraints(1,3,1,0,1,1,false,true));
	    closeButton = new JButton("Close");
	    closeButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				close();
			}
		});
	    p.add(closeButton, AwtUtil.getConstraints(2,3,1,0,1,1,false,true));
	    
	    getContentPane().add(p);

	    setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
	    enableEvents(WindowEvent.WINDOW_CLOSING);

	    setSize(600, 500);
	    AwtUtil.centerWindow(this);

//		System.out.println("Done Init DB.");
	}

	/**
	 * Print Report
	 */
	protected void print() {
		DocumentRenderer dr = new DocumentRenderer();
		dr.print(txtReport);
	}

	/** Get the Report based on parameters given.
	 * Will be as HTML format. */
	private String getReportStr() {
//		System.out.println("getReportStr");
		StringBuffer sb = new StringBuffer();
		// Start
		sb.append("<HTML>");
		// Heading
		sb.append("<font size=5><strong>Detailed Budget Report</strong></font><br><br>");
		sb.append("<font size=4><strong>").append(getBudgetPeriodStr());
		sb.append("</strong></font><br>");
		if (!subTotalBy.equals("None")) {
			sb.append("<font size=4><strong>");
			sb.append("Subtotal by ").append(subTotalBy);
			sb.append("</strong></font><br>");
		}
		SimpleDateFormat pdf = new SimpleDateFormat("d MMM yyyy");
		sb.append("Date: <strong>").append(pdf.format(new Date())).append("</strong><br>");
		sb.append("Budget: <strong>").append(budget==null ? "ALL" : budget.getName()).append("</strong><br>");
		sb.append("Period: <strong>").append(pdf.format(startDate)).
			append("</strong> to <strong>").append(pdf.format(endDate)).append("</strong><br><br>");
		// Body
		
		// Get Subtotal times
		List<DetailedBudgetColumn> columns = getDetailedBudgetColumns(startDate,endDate);
		
		// Fill Actual and Budgeted Amounts for each column
		for (Iterator<DetailedBudgetColumn> iterator = columns.iterator(); iterator.hasNext();) {
			DetailedBudgetColumn col = iterator.next();
			
			// Map of int (account number) to DetailedBudgetItem
			col.detIncomeItems =  getDetailedBudgetItems(col.startDay, col.endDay, INCOME_ACCOUNTS);
			col.detExpenseItems =  getDetailedBudgetItems(col.startDay, col.endDay, EXPENSE_ACCOUNTS);
		}
		
		// Number of table columns in subtotals
		int numSubTotalCols = getNumSubtotalsColumns();
		
		sb.append("<table border=\"1\">\n");
		// First line of header
		sb.append("<tr><td align=\"center\"><strong>Item</strong></td>");
		if (columns.size() > 1) {
			for (Iterator<DetailedBudgetColumn> iterator = columns.iterator(); iterator.hasNext();) {
				DetailedBudgetColumn col = iterator.next();
				sb.append("<td align=\"center\" colspan="+numSubTotalCols+"><strong>"+DT_FMT.format(col.startDay)+
						" - "+DT_FMT.format(col.endDay)+"</strong></td>");
			}
			int lastSpan = 3;
			sb.append("<td align=\"center\" colspan="+lastSpan+"><strong>TOTAL</strong></td>");
			sb.append("</tr>\n");
			// Second line of header
			sb.append("<tr><td>&nbsp</td>\n");
			if (columns.size() > 1) {
				for (Iterator<DetailedBudgetColumn> iterator = columns.iterator(); iterator.hasNext();) {
					/*DetailedBudgetColumn col = (DetailedBudgetColumn) */iterator.next();
					if (budgetWithSubtotal || columns.size() == 1) {
						sb.append("<td align=\"center\"><strong>Budget</strong></td>");
					}
					sb.append("<td align=\"center\"><strong>Actual</strong></td>");
					if (diffWithSubtotal || columns.size() == 1) {
						sb.append("<td align=\"center\"><strong>Diff</strong></td>");
					}
				}
			}
		}
		
		sb.append("<td align=\"center\"><strong>Budget</strong></td>");
		sb.append("<td align=\"center\"><strong>Actual</strong></td>");
		sb.append("<td align=\"center\"><strong>Diff</strong></td>");
		sb.append("</tr>\n");

		sb.append(getCategoriesHTML(columns,INCOME_ACCOUNTS));
		if (subtotalsForParentCategories) {
			sb.append("<tr><td colspan="+getNumTableColumns(columns)+">&nbsp;</td></tr>\n");
		}
		sb.append(getCategoriesHTML(columns,EXPENSE_ACCOUNTS));
		sb.append("<tr><td colspan="+getNumTableColumns(columns)+">&nbsp;</td></tr>\n");
		
		sb.append(getCategoriesTotalHTML(columns,INCOME_ACCOUNTS));
		sb.append(getCategoriesTotalHTML(columns,EXPENSE_ACCOUNTS));
		sb.append(getCategoriesTotalHTML(columns,DIFF_ACCOUNTS));
		
		sb.append("</table>");
		
		// End
		sb.append("</HTML>");
//		System.out.println("Done getReportStr.");
		return sb.toString();
	}
	
	private String getBudgetPeriodStr() {
		Date now = startDate;
		SimpleDateFormat MONTH_DF = new SimpleDateFormat("MMMM yyyy");
		SimpleDateFormat YEAR_DF = new SimpleDateFormat("yyyy");
		if (budgetPeriod.equals("Month to Date")) return MONTH_DF.format(now) + " to Date";
		if (budgetPeriod.equals("Quarter to Date")) return YEAR_DF.format(now) + " Quarter " + DateUtil.getQuarterNum(now) + " to Date";
		if (budgetPeriod.equals("Year to Date")) return YEAR_DF.format(now) + " to Date";
		if (budgetPeriod.equals("This Month")) return MONTH_DF.format(now);
		if (budgetPeriod.equals("This Quarter")) return YEAR_DF.format(now) + " Quarter " + DateUtil.getQuarterNum(now);
		if (budgetPeriod.equals("This Year")) return YEAR_DF.format(now);
		if (budgetPeriod.equals("Last Month")) return MONTH_DF.format(now);
		if (budgetPeriod.equals("Last Quarter")) return YEAR_DF.format(now) + " Quarter " + DateUtil.getQuarterNum(now);
		if (budgetPeriod.equals("Last Year")) return YEAR_DF.format(now);
		if (budgetPeriod.equals("Custom")) return "Custom";
		
		return "";
	}

	/**
	 * Number of Report Columns for each subtotal
	 * @return
	 */
	public int getNumSubtotalsColumns() {
		int numSubTotalCols = 1;
		if (budgetWithSubtotal) numSubTotalCols++;
		if (diffWithSubtotal) numSubTotalCols++;
		return numSubTotalCols;
	}
	
	/**
	 * Total number of columns for report row
	 * @param columns
	 * @return
	 */
	public int getNumTableColumns(List<DetailedBudgetColumn> columns) {
		int i = 4;
		if (columns.size() > 1) {
			i += getNumSubtotalsColumns() * columns.size();
		}
		if (subtotalsForParentCategories) i++;

		return i;
	}

	/** Categories HTML for Income or Expenses */
	public String getCategoriesHTML(List<DetailedBudgetColumn> columns, int type) {
		StringBuffer sbo = new StringBuffer();
		sbo.append("<tr><td colspan="+getNumTableColumns(columns)+"><strong>");
		if (type == INCOME_ACCOUNTS)
			sbo.append("INCOME");
		else if (type == EXPENSE_ACCOUNTS)
			sbo.append("EXPENSE");
		sbo.append("</strong></td></tr>");
		
		// Categories
		Account lastParentAccount = null;
		// Array of longs for subtotals
		Map<Integer, Long> parentSubtotalMap = new HashMap<Integer, Long>();
		Map<Integer, Long> lastParentSubtotalMap = new HashMap<Integer, Long>();
		boolean lastParentHasValues = false;
		for (Iterator<Account> iterator = categories.iterator(); iterator.hasNext();) {
			int parentSubPtr = 0;
			Account account = iterator.next();
			StringBuffer sb = new StringBuffer();
			StringBuffer sbBefore = new StringBuffer();
			if (account == null)
				continue;
			// Only accept income or expense accounts
			if (type == INCOME_ACCOUNTS && account.getAccountType() != Account.AccountType.INCOME) continue;
			else if (type == EXPENSE_ACCOUNTS && account.getAccountType() != Account.AccountType.EXPENSE) continue;
//			System.out.println("  account="+account.getAccountName()+" "+account);
			
			// Do we add Parent Account row?
			int indent = 0;
			if (subtotalsForParentCategories) {
				indent = account.getDepth() - 1;

				Account parentAccount = account.getParentAtDepth(0);
				if (lastParentAccount != null && !lastParentAccount.equals(parentAccount) && lastParentHasValues) {
					lastParentSubtotalMap = parentSubtotalMap;
					parentSubtotalMap = new HashMap<Integer, Long>();
					lastParentHasValues = false;
				}
			}

			Integer accNum = new Integer(account.getAccountNum());
			// Account Name
			sb.append("<tr><td"+getIndentStyle(indent)+">");
			sb.append(getAccountName(account));
			sb.append("</td>");
			
			// Columns
			long totalActual = 0;
			long totalBudget = 0;
			for (Iterator<DetailedBudgetColumn> iterator2 = columns.iterator(); iterator2.hasNext();) {
				DetailedBudgetColumn col = iterator2.next();
				DetailedBudgetItem item = null;
				if (type == INCOME_ACCOUNTS) item = col.detIncomeItems.get(accNum);
				else if (type == EXPENSE_ACCOUNTS) item = col.detExpenseItems.get(accNum);
				long actual = 0;
				long budget = 0;
				if (item != null) {
					actual = item.actualAmount;
					budget = item.budgetAmount;
				}
//				System.out.println(" -- item="+item+" actual="+actual+" budget="+budget);
				
				
				if (budgetWithSubtotal || columns.size() == 1) {
					sb.append("<td align=\"right\">").append(getCurrencyStr(budget,null)).append("</td>");
					addSubtotal(parentSubtotalMap,budget,parentSubPtr++);
				}
				sb.append("<td align=\"right\">").append(getCurrencyStr(actual,col.endDay)).append("</td>");
				addSubtotal(parentSubtotalMap,actual,parentSubPtr++);
				if (diffWithSubtotal || columns.size() == 1) {
					long diff = budget - actual;
					if (type == INCOME_ACCOUNTS) {
						diff = actual - budget;
					}
					sb.append("<td align=\"right\">").append(getCurrencyStr(diff,col.endDay)).append("</td>");
					addSubtotal(parentSubtotalMap,diff,parentSubPtr++);
				}
				totalActual += actual;
				totalBudget += budget;
			}
			
			// If more than 1 column add a total column
			if (columns.size() > 1) {
				sb.append("<td align=\"right\">").append(getCurrencyStr(totalBudget,null)).append("</td>");
				addSubtotal(parentSubtotalMap,totalBudget,parentSubPtr++);
				sb.append("<td align=\"right\">").append(getCurrencyStr(totalActual,null)).append("</td>");
				addSubtotal(parentSubtotalMap,totalActual,parentSubPtr++);
				long diff = totalBudget - totalActual;
				if (type == INCOME_ACCOUNTS) {
					diff = totalActual - totalBudget;
				}
				sb.append("<td align=\"right\">").append(getCurrencyStr(diff,null)).append("</td>");
				addSubtotal(parentSubtotalMap,diff,parentSubPtr++);
			}
			sb.append("</tr>\n");
			
			// Do we show all accounts, even if all 0?
			if (showAllAccounts || totalActual != 0 || totalBudget != 0) {
				lastParentHasValues = true;
				if (subtotalsForParentCategories) {
					Account parentAccount = account.getParentAtDepth(0);
//					System.out.println("  parentAccount="+parentAccount.getAccountName()+" last="+lastParentAccount+" account="+account);
					if (lastParentAccount == null || !lastParentAccount.equals(parentAccount)) {
						// Add subtotal of previous parent account
						if (lastParentAccount != null) {
							addParentCategorySubtotalRow(sbBefore,lastParentSubtotalMap);
//							System.out.println("  sbBefore1="+sbBefore.toString());
							addBlankRow(sbBefore,columns);
						}
						
						// Add heading of current parent account
						addParentHeading(sbBefore,parentAccount,columns);
//						System.out.println("  sbBefore2 ="+sbBefore.toString());
						
						lastParentAccount = parentAccount;
					}
				}
				
				sbo.append(sbBefore);
				sbo.append(sb);
			}
		}
		// Last subtotal
		if (subtotalsForParentCategories) {
			if (lastParentAccount != null) {
				addParentCategorySubtotalRow(sbo,parentSubtotalMap);
			}
		}
	
		return sbo.toString();
	}

	private String getIndentStyle(int indent) {
		if (indent <= 0) return "";
		return " style=\"padding-left:20px;\"";
	}
	
	private void addSubtotal(Map<Integer, Long> subtotalMap, long value, int index) {
		long val = 0;
		if (subtotalMap.get(new Integer(index)) != null) {
			val = subtotalMap.get(new Integer(index)).longValue();
		}
		val += value;
		subtotalMap.put(new Integer(index),new Long(val));
	}
	
	/** Parent Category with Subtotals row for Parent Category */
	private void addParentCategorySubtotalRow(StringBuffer sb, Map<Integer, Long> subtotalMap) {
		sb.append("<tr><td><strong>Subtotal</strong></td>");

		for (int i = 0; i < subtotalMap.size(); i++) {
			long val = subtotalMap.get(new Integer(i)).longValue();
			sb.append("<td align=\"right\"><strong>"+getCurrencyStr(val,null)+"</strong></td>");
		}
		
//		sb.append("<td>&nbsp;</td>");
		sb.append("</tr>");
	}

	/** Parent Category with Subtotals row for Parent Category */
	private void addParentHeading(StringBuffer sb, Account account, List<DetailedBudgetColumn> columns) {
		sb.append("<tr><td colspan="+getNumTableColumns(columns)+"><strong>"+getAccountName(account)+"</strong></td></tr>");
	}
	
	/** Blank row */
	private void addBlankRow(StringBuffer sb, List<DetailedBudgetColumn> columns) {
		sb.append("<tr><td colspan="+getNumTableColumns(columns)+">&nbsp;</td></tr>");
	}
	
	/** Categories HTML for TOTAL of Income or Expenses */
	public String getCategoriesTotalHTML(List<DetailedBudgetColumn> columns, int type) {
		StringBuffer sb = new StringBuffer();
		// TOTALS
		sb.append("<tr><td><strong>");
		if (type == INCOME_ACCOUNTS) sb.append("TOTAL INCOME");
		else if (type == EXPENSE_ACCOUNTS) sb.append("TOTAL EXPENSE");
		else if (type == DIFF_ACCOUNTS) sb.append("TOTAL DIFF");
		sb.append("</strong></td>");
		
		// Columns
		long totalActual = 0;
		long totalBudget = 0;
		for (Iterator<DetailedBudgetColumn> iterator2 = columns.iterator(); iterator2.hasNext();) {
			DetailedBudgetColumn col = iterator2.next();
			long actual = 0;
			long budget = 0;
			if (type == INCOME_ACCOUNTS) {
				actual = col.getTotalIncomeActualAmount();
				budget = col.getTotalIncomeBudgetAmount();
			}
			else if (type == EXPENSE_ACCOUNTS) {
				actual = col.getTotalExpenseActualAmount();
				budget = col.getTotalExpenseBudgetAmount();
			}
			else if (type == DIFF_ACCOUNTS) {
				actual = col.getTotalIncomeActualAmount() - col.getTotalExpenseActualAmount();
				budget = col.getTotalIncomeBudgetAmount() - col.getTotalExpenseBudgetAmount();
			}
			
			if (budgetWithSubtotal || columns.size() == 1) {
				sb.append("<td align=\"right\"><strong>").append(getCurrencyStr(budget,null)).append("</strong></td>");
			}
			sb.append("<td align=\"right\"><strong>").append(getCurrencyStr(actual,col.endDay)).append("</strong></td>");
			if (diffWithSubtotal || columns.size() == 1) {
				sb.append("<td align=\"right\"><strong>").append(getCurrencyStr(budget - actual,col.endDay)).append("</strong></td>");
			}
			totalActual += actual;
			totalBudget += budget;
		}
		
		// If more than 1 column add a total column
		if (columns.size() > 1) {
			sb.append("<td align=\"right\"><strong>").append(getCurrencyStr(totalBudget,null)).append("</strong></td>");
			sb.append("<td align=\"right\"><strong>").append(getCurrencyStr(totalActual,null)).append("</strong></td>");
			sb.append("<td align=\"right\"><strong>").append(getCurrencyStr(totalBudget - totalActual,null)).append("</strong></td>");
		}
		sb.append("</tr>\n");
		
		return sb.toString();
	}
	
	/**
	 * Get a DetailedBudgetColumn object which contains all Actual and Budgeted Values
	 * for a given time period.
	 * @param startDay Start Day of Period
	 * @param endDay End Day of Period
	 * @return
	 */
	private List<DetailedBudgetColumn> getDetailedBudgetColumns(Date startDay, Date endDay) {
		List<DetailedBudgetColumn> columns = new ArrayList<DetailedBudgetColumn>();
		
		Date sd = startDay;

		// No Subtotals
		if (subTotalBy == null || subTotalBy.equals("None")) {
			DetailedBudgetColumn col = new DetailedBudgetColumn(startDay,endDay);
			columns.add(col);
		} 
		// Want subtotals
		else  {
			boolean done = false;
			while (!done) {
				Date e2 = null;
				if (subTotalBy.equals("Week")) {
					e2 = DateUtil.getEndOfWeek(sd,START_DAY_OF_WEEK);
				}
				else if (subTotalBy.equals("Month")) {
					e2 = DateUtil.getEndOfMonth(sd);
				}
				else if (subTotalBy.equals("Year")) {
					e2 = DateUtil.getEndOfYear(sd);
				} 
				else {
					// Shouldnt get here
					break;
				}
				// Have we reached the end
				if (DateUtil.isInSameDayOrAfter(e2, endDay)) {
					DetailedBudgetColumn col = new DetailedBudgetColumn(sd,endDay);
					columns.add(col);
					break;
				}
				// Next day
				DetailedBudgetColumn col = new DetailedBudgetColumn(sd,e2);
				columns.add(col);
				sd = DateUtil.setTimeZero(DateUtil.addDays(e2, 1));
			}
		}

		return columns;
	}

	/**
	 * Name of the account (Category)
	 * @param account
	 * @return
	 */
	private String getAccountName(Account account) {
		if (account == null) return "";
		StringBuffer sb = new StringBuffer();
		String[] names = account.getAllAccountNames();
		for (int i = 0; i < names.length; i++) {
			if (subtotalsForParentCategories) {
				if (i > 1) sb.append(":");
				if (i > 0 || names.length == 1) sb.append(names[i]);
			} else {
				if (i > 0) sb.append(":");
				sb.append(names[i]);
			}
		}
		
		return sb.toString();
	}

	private String getFullAccountName(Account account) {
		if (account == null) return "";
		StringBuffer sb = new StringBuffer();
		String[] names = account.getAllAccountNames();
		for (int i = 0; i < names.length; i++) {
			if (i > 0) sb.append(":");
			sb.append(names[i]);
		}
		
		return sb.toString();
	}
	
	/** Return amount as dollars and cents in HTML format. 
	 * If date in future return empty space.*/
	public String getCurrencyStr(long amount, Date dt) {
		StringBuffer sb = new StringBuffer();
		if (dt != null && dt.after(new Date()) && amount == 0) {
			return "&nbsp;";
		}
		if (amount < 0) sb.append("<font color=\"red\">");
		sb.append(CURR_FMT.format(amount/100)).append(".").append(CENTS_FMT.format(Math.abs(amount%100)));
		if (amount < 0) sb.append("</font>");
		return sb.toString();
	}
	
	/**
	 * Get a the budgeted and actual amounts for the period given.
	 * @param type Either INCOME_ACCOUNTS(0) or EXPENSE_ACCOUNTS(1)
	 * @return Map of int (account number) to DetailedBudgetItem
	 */
	private Map<String, DetailedBudgetItem> getDetailedBudgetItems(Date startDay, Date endDay, int type) {
//		System.out.println("getDetailedBudgetItems type="+type);
		Map<String, DetailedBudgetItem> txnMap = new HashMap<String, DetailedBudgetItem>();
		
		TransactionSet txSet = extension.getUnprotectedContext().getCurrentAccountBook().getTransactionSet();
		
		// Loop through all transactions
		for (AbstractTxn t : txSet) {
			if (t == null) continue;
//			System.out.println("..txn="+t.getAccount().getAccountName()+" => "+t.getAccount().getClass().getName());
			// Only accept income or expense accounts
			if (type == INCOME_ACCOUNTS && t.getAccount().getAccountType() != Account.AccountType.INCOME) continue;
			else if (type == EXPENSE_ACCOUNTS && t.getAccount().getAccountType() != Account.AccountType.EXPENSE) continue;
			
			// Is this transaction in the range?
			int intStartDay = Util.convertDateToInt(startDay);
			int intEndDay   = Util.convertDateToInt(endDay);
			int dt = t.getDateInt();
			if (intStartDay <= dt && dt <= intEndDay) {
//				System.out.println("    in date range t="+t+" class="+t.getClass().getName());
				addTransaction(txnMap, t);
			}
		}

		// Loop through all budgeted items
		// If more than one budget has the same Category budgeted, it
		// will sum them.
		BudgetList budList = extension.getUnprotectedContext().getCurrentAccountBook().getBudgets();
		for (Budget b : budList.getAllBudgets()) {
			for (BudgetItem bi : b.getAllItems()) {
				Account a = bi.getTransferAccount();

				// Only accept income or expense accounts
				if (type == INCOME_ACCOUNTS && a.getAccountType() != Account.AccountType.INCOME) continue;
				else if (type == EXPENSE_ACCOUNTS && a.getAccountType() != Account.AccountType.EXPENSE) continue;
				
				// Is the budget item scheduled for the given time period
				long budgetedAmount = getBudgetedAmount(bi.getIntervalStartDate(),
														bi.getIntervalEndDate(),
														bi.getInterval(),
														bi.getAmount(), 
														Util.convertDateToInt(startDay), 
														Util.convertDateToInt(endDay));
				if (budgetedAmount == 0) continue;
				
				DetailedBudgetItem item = txnMap.get(a.getUUID());
				if (item == null) {
					item = new DetailedBudgetItem(a.getUUID(), budgetedAmount, 0);
					txnMap.put(a.getUUID(), item);
				} else {
					item.budgetAmount += budgetedAmount;
				}
			}
		}
		
		return txnMap;
	}
	
	static class IntervalInfo 
	{
		public IntervalInfo(int y, int m, int d, boolean p) 
		{
			years = y;
			months = m;
			days = d;
			prorate = p;
		}
		public int years;
		public int months;
		public int days;
		public boolean prorate;
		
		@Override
		public String toString()
		{
			return "" + years + ", " + months + ", " + days + ", " + prorate;
		}
	}
	
	static private Map<Integer, IntervalInfo> intervalMap = null;
	
	static private void buildIntervalMap() 
	{
		intervalMap = new HashMap<Integer, IntervalInfo>();
		
		intervalMap.put(BudgetItem.INTERVAL_NO_REPEAT, new IntervalInfo(3000, 0, 0, false));
		intervalMap.put(BudgetItem.INTERVAL_ANNUALLY, new IntervalInfo(1, 0, 0, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_ANNUALLY, new IntervalInfo(1, 0, 0, false));
		intervalMap.put(BudgetItem.INTERVAL_SEMI_ANNUALLY, new IntervalInfo(0, 6, 0, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_SEMI_ANNUALLY, new IntervalInfo(0, 6, 0, false));
		intervalMap.put(BudgetItem.INTERVAL_TRI_MONTHLY, new IntervalInfo(0, 3, 0, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_TRI_MONTHLY, new IntervalInfo(0, 3, 0, false));
		intervalMap.put(BudgetItem.INTERVAL_MONTHLY, new IntervalInfo(0, 1, 0, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_MONTHLY, new IntervalInfo(0, 1, 0, false));
		intervalMap.put(BudgetItem.INTERVAL_SEMI_MONTHLY, new IntervalInfo(0, 1, 0, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_SEMI_MONTHLY, new IntervalInfo(0, 1, 0, false));
		intervalMap.put(BudgetItem.INTERVAL_TRI_WEEKLY, new IntervalInfo(0, 0, 21, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_TRI_WEEKLY, new IntervalInfo(0, 0, 21, true));
		intervalMap.put(BudgetItem.INTERVAL_BI_WEEKLY, new IntervalInfo(0, 0, 14, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_BI_WEEKLY, new IntervalInfo(0, 0, 14, true));
		intervalMap.put(BudgetItem.INTERVAL_WEEKLY, new IntervalInfo(0, 0, 7, true));
		intervalMap.put(BudgetItem.INTERVAL_ONCE_WEEKLY, new IntervalInfo(0, 0, 7, false));
	}

	/**
	 * What is the budgeted amount for the given time period
	 * @param budStart Budget start date
	 * @param budEnd Budget end date
	 * @param interval Budget interval type
	 * @param intervalAmount Budget amount per interval
	 * @param repStart Report start date
	 * @param repEnd Report end date
	 * @return
	 */
	static long getBudgetedAmount(int budStart, int budEnd, 
								  int interval, long intervalAmount, 
								  int repStart, int repEnd) 
	{
		repEnd = Util.incrementDate(repEnd);
		budEnd = Util.incrementDate(budEnd);

		if (intervalMap == null)
			buildIntervalMap();
				
		int perStart = budStart;
		int perEnd = perStart;

		// Do the report period and budget period overlap?
		if (budStart > repEnd || budEnd < repStart)
			return 0;

		// Special handling for INTERVAL_DAILY (very easy case)
		if (interval == BudgetItem.INTERVAL_DAILY)
		{
			perStart = Math.max(perStart, repStart);
			perEnd = Math.min(budEnd, repEnd);
			
			return intervalAmount * (Util.calculateDaysBetween(perStart, perEnd));
		}
		
		IntervalInfo i = intervalMap.get(new Integer(interval));
		
		long amount = 0;
		while (perEnd < repEnd) 
		{
			// budDt is the beginning of one budget period.  Find the
			// end of the period.
			perStart = perEnd;
			perEnd = Util.incrementDate(perStart, i.years, i.months, i.days);
			
			if (perEnd <= repStart)
				continue;
			if (perStart > budEnd)
				break;

			// Determine if we have a partial period, and what the
			// start and end dates are.
			int calcStartDt = perStart, calcEndDt = perEnd;
			boolean partial = false;
			
			if (calcStartDt < repStart) 
			{
				calcStartDt = repStart;
				partial = true;
			}
			if (calcEndDt > repEnd)
			{
				calcEndDt = repEnd;
				partial = true;
			}
			if (calcEndDt > budEnd)
			{
				calcEndDt = budEnd;
				partial = true;
			}
			
			int periodLen = Util.calculateDaysBetween(perStart, perEnd);
			int calcLen   = Util.calculateDaysBetween(calcStartDt, calcEndDt);

			// Special handling for semi-monthly:
			if (interval == BudgetItem.INTERVAL_SEMI_MONTHLY ||
				interval == BudgetItem.INTERVAL_ONCE_SEMI_MONTHLY)
			{
				if (!partial)
					amount += intervalAmount * 2;
				else if (i.prorate)
					amount += (intervalAmount * 20 * calcLen / periodLen + 5) / 10;
				else
				{
					if (calcStartDt == perStart)
						amount += intervalAmount;
					int endFirst = Util.incrementDate(calcStartDt, 0, 0, 
													  periodLen / 2);
					if (endFirst < calcEndDt)
						amount += intervalAmount;
				}
				continue;
			}

			if (!partial || (!i.prorate && calcStartDt == perStart))
				amount += intervalAmount;
			else if (i.prorate)
				amount += (10 * intervalAmount * calcLen / periodLen + 5) / 10;
		}
		
		return amount;
	}

	/**
	 * Add a transaction to the Map
	 * @param txnMap
	 * @param t
	 */
	private void addTransaction(Map<String, DetailedBudgetItem> txnMap, AbstractTxn t) {
		if (t == null) return;

		// Get txn account
		Account a = t.getAccount();
		long amount = t.getValue();
		if ( t.getAccount().getAccountType() == Account.AccountType.INCOME) amount = -amount;
		// Get current actual amount
		DetailedBudgetItem item = txnMap.get(a.getUUID());
		if (item == null) {
			item = new DetailedBudgetItem(a.getUUID(), 0, amount);
			txnMap.put(a.getUUID(), item);
		} else {
			item.actualAmount += amount;
		}
	}

	/** Get all categories (A category is actually an Account object) based on 
	 * Budget selected */
	private List<Account> getCategories() {
		List<Account> categoryList = new ArrayList<Account>();
		
		// Do we get all the categories?
		if (budget!=null) {
			// Get only specified budget
      BudgetList budList = extension.getUnprotectedContext().getCurrentAccountBook().getBudgets();
      
      for (BudgetItem bi : budget.getAllItems()) {
        addCategoryAndSubcategories(categoryList, bi.getTransferAccount());
      }
      
      sortCategories(categoryList);
      return categoryList;
      
		}
		// Get all categories
		try {
			for (Account a : extension.getUnprotectedContext().getCurrentAccountBook().getRootAccount().getSubAccounts()) {
				addCategoryAndSubcategories(categoryList, a);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		sortCategories(categoryList);
		return categoryList;
	}
	
	private void sortCategories(List<Account> categoryList) {
		Collections.sort(categoryList,new Comparator<Account>() {
			public int compare(Account arg0, Account arg1) {
				return getFullAccountName(arg0).compareTo(getFullAccountName(arg1));
			}
		});

	}

	/** Add an account to the list if it isnt there already */
	private void addCategoryAndSubcategories(List<Account> categoryList, Account account) {
		if (account == null) return;
    
    // If it's a category and not in the list, add it
    switch(account.getAccountType()) {
      case INCOME:
      case EXPENSE:
        if (!categoryList.contains(account)) {
          categoryList.add(account);
        }
        break;
    }
    
    for (Account suba : account.getSubAccounts()) {
      addCategoryAndSubcategories(categoryList, suba);
		}
		
	}

	/** Save the Report */
	protected void save() {
		//Create a file chooser
		JFileChooser fc = new JFileChooser();
		File defFile = new File(getBudgetPeriodStr()+".html");
		fc.setSelectedFile(defFile);
		fc.setFileFilter(new FileFilter() {
			@Override
			public String getDescription() {
				return "HTML Files";
			}
		
			@Override
			public boolean accept(File f) {
				if (f.getName().toLowerCase().endsWith("html")) return true;
				return false;
			}
		});
		
		//In response to a button click:
		int returnVal = fc.showSaveDialog(this);
		
		if (returnVal == JFileChooser.APPROVE_OPTION) {
            File file = fc.getSelectedFile();
            
            try {
                BufferedWriter out = new BufferedWriter(new FileWriter(file));
                out.write(txtReport.getText());
                out.close();
            } catch (IOException e) {
            	// TODO(divegeek) Figure out what's appropriate here.
            }
        }
	}

	/** Close Window */
	protected void close() {
		this.setVisible(false);
		this.dispose();
	}
	
	/**
	 * Budget Item contains account (category) and actual, budget amounts for time period. 
	 */
	class DetailedBudgetItem {
		String accountID = null;
		long budgetAmount = 0;
		long actualAmount = 0;
		
		public DetailedBudgetItem(String accountID, long budgetAmount, long actualAmount) {
			this.accountID = accountID;
			this.budgetAmount = budgetAmount;
			this.actualAmount = actualAmount;
		}
	}

	/** Represents a subtotal column in the report including all income and
	 * expense categories.
	 * @author rolf
	 *
	 */ 
	class DetailedBudgetColumn {
		Date startDay = null;
		Date endDay = null;
		// Map of account (int) to DetailedBudgetItem for income accounts
		Map<String, DetailedBudgetItem> detIncomeItems = null;
		// Map of account (int) to DetailedBudgetItem for expense accounts
		Map<String, DetailedBudgetItem> detExpenseItems = null;
		
		public DetailedBudgetColumn(Date startDay, Date endDay) {
			this.startDay = startDay;
			this.endDay = endDay;
		}
		
		/** Total Budget amount for Income Accounts */
		public long getTotalIncomeBudgetAmount() {
			long total = 0;
			for (Iterator<Account> iterator = categories.iterator(); iterator.hasNext();) {
				Account account = iterator.next();
				Integer accNum = new Integer(account.getAccountNum());

				DetailedBudgetItem item = detIncomeItems.get(accNum);
				if (item != null) total += item.budgetAmount;
			}
			return total;
		}
		
		/** Total Actual amount for Income Accounts */
		public long getTotalIncomeActualAmount() {
			long total = 0;
			for (Iterator<Account> iterator = categories.iterator(); iterator.hasNext();) {
				Account account = iterator.next();
				Integer accNum = new Integer(account.getAccountNum());

				DetailedBudgetItem item = detIncomeItems.get(accNum);
				if (item != null) total += item.actualAmount;
			}
			return total;
		}
		
		/** Total Budget amount for Expense Accounts */
		public long getTotalExpenseBudgetAmount() {
			long total = 0;
			for (Iterator<Account> iterator = categories.iterator(); iterator.hasNext();) {
				Account account = iterator.next();
				Integer accNum = new Integer(account.getAccountNum());

				DetailedBudgetItem item = detExpenseItems.get(accNum);
				if (item != null) total += item.budgetAmount;
			}
			return total;
		}
		
		/** Total Actual amount for Expense Accounts */
		public long getTotalExpenseActualAmount() {
			long total = 0;
			for (Iterator<Account> iterator = categories.iterator(); iterator.hasNext();) {
				Account account = iterator.next();
				Integer accNum = new Integer(account.getAccountNum());

				DetailedBudgetItem item = detExpenseItems.get(accNum);
				if (item != null) total += item.actualAmount;
			}
			return total;
		}
		
	}
}

// Local Variables:
// tab-width: 4
// End: