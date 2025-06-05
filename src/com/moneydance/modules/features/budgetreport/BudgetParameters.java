/*
 * Copyright (c) 2014, Michael Bray. All rights reserved.
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

package com.moneydance.modules.features.budgetreport;

import java.awt.Color;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.SortedMap;
import java.util.TreeMap;

import javax.swing.JFrame;
import javax.swing.JOptionPane;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.awt.JDateField;

/*
 * Container for all parameters for the report.  Data is serialised into file
 * {filepath}/{budgetname}.bpam
 * 
 * {filepath} is file system path from AccountBook
 * {budgetname} is the internal key for the selected budget
 */
public class BudgetParameters implements java.io.Serializable {

	/*
	 * Static and transient fields are not stored
	 */
	private static final long serialVersionUID = 1L;
	private transient FeatureModuleContext conCurrentCon;
	private transient AccountBook abCurAcctBook;
	private transient Account rootAcct;
	private transient File fiCurFolder;
	private transient FileInputStream fiCurInFile;
	private transient FileOutputStream fiCurOutFile;
	private transient String strFileName;
	private transient String strFullFileName;
	private transient boolean bDirty;
	private transient SortedMap<String, AccountDetails> mapExpenseAccounts;
	private transient SortedMap<String, AccountDetails> mapExpenseMissing;
	private transient SortedMap<String, AccountDetails> mapIncomeAccounts;
	private transient SortedMap<String, AccountDetails> mapIncomeMissing;
	private transient long[] arrTotalActIncome;
	private transient long[] arrTotalActExpenses;
	private transient long[] arrTotalAct;

	/*
	 * The following fields are stored
	 */

	private int iStartDate;
	private int iEndDate;
	private boolean bRollup;
	private List<BudgetLine> listExpenseLines;
	private List<BudgetLine> listIncomeLines;
	private Color clrHeaders;
	private Color clrBudget;
	private Color clrActual;
	private Color clrPositive;
	private Color clrNegative;
	private Color clrFGPositive;
	private Color clrFGNegative;

	/*
	 * Constructor
	 */
	public BudgetParameters(FeatureModuleContext context, String strFileNamep,
			JDateField jdtFiscalStart, JDateField jdtFiscalEnd) {
		refreshData(context, strFileNamep, jdtFiscalStart, jdtFiscalEnd);
	}

	public void refreshData(FeatureModuleContext context, String strFileNamep,
			JDateField jdtFiscalStart, JDateField jdtFiscalEnd) {
		mapExpenseAccounts = new TreeMap<String, AccountDetails>();
		mapIncomeAccounts = new TreeMap<String, AccountDetails>();
		conCurrentCon = context;
		strFileName = strFileNamep;
		/*
		 * set parameters to default Start Date - Fiscal Start End Date - Fiscal
		 * End Rollup - true;
		 */
		iStartDate = jdtFiscalStart.getDateInt();
		iEndDate = jdtFiscalEnd.getDateInt();
		bRollup = true;
		/*
		 * load Expense Accounts
		 */
		rootAcct = conCurrentCon.getRootAccount();
		loadAccounts(rootAcct, mapExpenseAccounts, "", Constants.EXPENSE_SCREEN);
		loadAccounts(rootAcct, mapIncomeAccounts, "", Constants.INCOME_SCREEN);
		/*
		 * mapMissing used to hold Accounts declared in the main file
		 * but not being used by this budget. Will only have entries if new
		 * entries added to the main file or if user has deleted an Account from
		 * the budget.
		 */
		mapExpenseMissing = new TreeMap<String, AccountDetails>(
				mapExpenseAccounts);
		mapIncomeMissing = new TreeMap<String, AccountDetails>(
				mapIncomeAccounts);
		/*
		 * determine if file already exists
		 */
		abCurAcctBook = context.getCurrentAccountBook();
		fiCurFolder = abCurAcctBook.getRootFolder();
		/*
		 * File suffix is .BPEX for expenses, .BPIC for income
		 */

		strFullFileName = fiCurFolder.getAbsolutePath() + "\\" + strFileName
				+ ".bprp";

		try {
			fiCurInFile = new FileInputStream(strFullFileName);
			ObjectInputStream ois = new ObjectInputStream(fiCurInFile);
			/*
			 * file exists, copy temporary object to this object
			 */
			BudgetParameters objTemp = (BudgetParameters) ois.readObject();
			this.iStartDate = objTemp.iStartDate;
			this.iEndDate = objTemp.iEndDate;
			this.bRollup = objTemp.bRollup;
			this.listExpenseLines = objTemp.listExpenseLines;
			this.listIncomeLines = objTemp.listIncomeLines;
			if (objTemp.clrHeaders == null)
				clrHeaders = Constants.CLRHEAD;
			else
				clrHeaders = objTemp.clrHeaders;
			if (objTemp.clrActual == null)
				clrActual = Constants.CLRACTUAL;
			else
				clrActual = objTemp.clrActual;
			if (objTemp.clrBudget == null)
				clrBudget = Constants.CLRBUDGET;
			else
				clrBudget = objTemp.clrBudget;
			if (objTemp.clrPositive == null)
				clrPositive = Constants.CLRPOSITIVE;
			else
				clrPositive = objTemp.clrPositive;
			if (objTemp.clrNegative == null)
				clrNegative = Constants.CLRNEGATIVE;
			else
				clrNegative = objTemp.clrNegative;
			if (objTemp.clrFGPositive == null)
				clrFGPositive = Color.BLACK;
			else
				clrFGPositive = objTemp.clrFGPositive;
			if (objTemp.clrFGNegative == null)
				clrFGNegative = Color.RED;
			else
				clrFGNegative = objTemp.clrFGNegative;
			/*
			 * can not guarantee Account object ids are correct, go through the
			 * budget lines and set the account object ids using a map of names
			 * to object ids
			 * 
			 * Set date to force set up of internal fields
			 */
			List<BudgetLine>listLinesMissing = new ArrayList<BudgetLine>();
			for (BudgetLine objLine : listExpenseLines) {
				AccountDetails objAcct = mapExpenseAccounts.get(objLine.getCategoryIndent());
				if (objAcct == null) {
					/*
					 * line no longer exists
					 */
					listLinesMissing.add(objLine);
					continue;
				}
				objLine.setCategory(objAcct.getAccount());
				objLine.setParent(objAcct.getParent());
				mapExpenseAccounts.get(objLine.getCategoryIndent()).setLine(
						objLine);
				/*
				 * remove from the mapMissing map to leave a list of those not
				 * in budgetlines
				 */
				mapExpenseMissing.remove(objLine.getCategoryIndent());
			}
			for (BudgetLine objLine : listLinesMissing) {
				listExpenseLines.remove(objLine);
			}
			listLinesMissing.clear();
			for (BudgetLine objLine : listIncomeLines) {
				AccountDetails objAcct = mapIncomeAccounts.get(objLine.getCategoryIndent());
				if (objAcct == null) {
					/*
					 * line no longer exists
					 */
					listLinesMissing.add(objLine);
					continue;
				}
				objLine.setCategory(objAcct.getAccount());
				objLine.setParent(objAcct.getParent());
				mapIncomeAccounts.get(objLine.getCategoryIndent()).setLine(
						objLine);
				/*
				 * remove from the mapMissing map to leave a list of those not
				 * in budgetlines
				 */
				mapIncomeMissing.remove(objLine.getCategoryIndent());
			}
			for (BudgetLine objLine : listLinesMissing) {
				listIncomeLines.remove(objLine);
			}
			listLinesMissing.clear();
			/*
			 * now remove missing accounts from the selected accounts
			 */
			for (Entry<String, AccountDetails> objEntry : mapExpenseMissing
					.entrySet()) {
				mapExpenseAccounts.remove(objEntry.getKey());
			}
			for (Entry<String, AccountDetails> objEntry : mapIncomeMissing
					.entrySet()) {
				mapIncomeAccounts.remove(objEntry.getKey());
			}
			fiCurInFile.close();
		} catch (IOException | ClassNotFoundException ioException) {
			/*
			 * file does not exist
			 */
			listExpenseLines = new ArrayList<BudgetLine>();
			listIncomeLines = new ArrayList<BudgetLine>();
			/*
			 * load Expense Categories into the Budget Line by traversing the
			 * accounts
			 */
			rootAcct = conCurrentCon.getRootAccount();
			/*
			 * set colours
			 */
			clrHeaders = Constants.CLRHEAD;
			clrActual = Constants.CLRACTUAL;
			clrBudget = Constants.CLRBUDGET;
			clrPositive = Constants.CLRPOSITIVE;
			clrNegative = Constants.CLRNEGATIVE;
			clrFGPositive = Constants.CLRFGPOSITIVE;
			clrFGNegative = Constants.CLRFGNEGATIVE;

			/*
			 * traverse sorted map to get categories in ascending order,create
			 * budget lines and add to map
			 */
			for (Map.Entry<String, AccountDetails> mapEntry : mapExpenseAccounts
					.entrySet()) {
				BudgetLine objLine = new BudgetLine(Constants.CHILD_LINE,
						mapEntry.getKey(), mapEntry.getValue().getAccount());
				mapEntry.getValue().setLine(objLine);
				objLine.setParent(mapEntry.getValue().getParent());
				listExpenseLines.add(objLine);
				mapExpenseMissing.remove(objLine.getCategoryIndent());
			}
			for (Map.Entry<String, AccountDetails> mapEntry : mapIncomeAccounts
					.entrySet()) {
				BudgetLine objLine = new BudgetLine(Constants.CHILD_LINE,
						mapEntry.getKey(), mapEntry.getValue().getAccount());
				mapEntry.getValue().setLine(objLine);
				objLine.setParent(mapEntry.getValue().getParent());
				listIncomeLines.add(objLine);
				mapIncomeMissing.remove(objLine.getCategoryIndent());
			}
			/*
			 * create the file
			 */
			try {
				fiCurOutFile = new FileOutputStream(strFullFileName);
				ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
				oos.writeObject(this);
				fiCurOutFile.close();
			} catch (IOException i) {
				i.printStackTrace();
			}
		}
		/*
		 * make sure missing maps have BudgetLines
		 */
		Iterator<Entry<String, AccountDetails>> itTemp = mapIncomeMissing
				.entrySet().iterator();
		while (itTemp.hasNext()) {
			Entry<String, AccountDetails> enTemp = itTemp.next();
			BudgetLine objLineT = new BudgetLine(Constants.INCOME_SCREEN,
					enTemp.getKey(), enTemp.getValue().getAccount());
			mapIncomeMissing.get(enTemp.getKey()).setLine(objLineT);
		}
		itTemp = mapExpenseMissing.entrySet().iterator();
		while (itTemp.hasNext()) {
			Entry<String, AccountDetails> enTemp = itTemp.next();
			BudgetLine objLineT = new BudgetLine(Constants.EXPENSE_SCREEN,
					enTemp.getKey(), enTemp.getValue().getAccount());
			mapExpenseMissing.get(enTemp.getKey()).setLine(objLineT);
		}
		/*
		 * put budget lines in ascending indented name order
		 */
		resetLists();
	}

	/*
	 * Reset lists
	 */
	public void resetLists() {
		/*
		 * set the type for parents
		 */
		setParents(listExpenseLines);
		setParents(listIncomeLines);
	}

	/*
	 * Go through the budget lines and set the type. If category has a parent
	 * set parent line.
	 */
	private void setParents(List<BudgetLine> listBudgetLines) {
		BudgetLine[] objLast = new BudgetLine[10];
		int iDepth = -1;
		for (BudgetLine objLine : listBudgetLines) {
			objLine.setType(Constants.CHILD_LINE);
			if (iDepth == -1) {
				iDepth++;
				objLast[iDepth] = objLine;
				continue;
			}
			if (objLine.getCategory().getDepth() > objLast[iDepth]
					.getCategory().getDepth()) {
				objLast[iDepth].setType(Constants.PARENT_LINE);
				iDepth++;
				objLast[iDepth] = objLine;
			} else {
				if (objLine.getCategory().getDepth() == objLast[iDepth]
						.getCategory().getDepth())
					objLast[iDepth] = objLine;
				else {
					while (iDepth != -1) {
						if (objLine.getCategory().getDepth() < objLast[iDepth]
								.getCategory().getDepth())
							iDepth--;
						else
							break;
					}
					if (iDepth > -1)
						objLast[iDepth] = objLine;
				}
			}

		}
	}

	/*
	 * Create a table of category names and account objects Account name is made
	 * up of all accounts in path
	 */
	private static void loadAccounts(Account parentAcct,
			Map<String, AccountDetails> mapAccounts, String strIndentp,
			int iType) {
		int sz = parentAcct.getSubAccountCount();
		String strIndent;
		strIndent = strIndentp;
		for (int i = 0; i < sz; i++) {
			Account acct = parentAcct.getSubAccount(i);
			if ((iType == Constants.EXPENSE_SCREEN && acct.getAccountType() == Account.AccountType.EXPENSE)
					|| (iType == Constants.INCOME_SCREEN && acct
							.getAccountType() == Account.AccountType.INCOME)) {
				mapAccounts.put(
						strIndent + Constants.chSeperator
								+ acct.getAccountName(), new AccountDetails(
								acct, strIndentp));
			}
			loadAccounts(acct, mapAccounts, strIndent + Constants.chSeperator
					+ acct.getAccountName(), iType);
		}
	}

	/*
	 * add a category from missing list
	 */
	public void addIncomeLine(String strKey) {
		AccountDetails acct = mapIncomeMissing.get(strKey);
		mapIncomeAccounts.put(strKey, acct);
		bDirty = true;
	}

	public void addExpenseLine(String strKey) {
		AccountDetails acct = mapExpenseMissing.get(strKey);
		mapExpenseAccounts.put(strKey, acct);
		bDirty = true;
	}

	/*
	 * deselect a specific line, add it to mapMissing
	 */
	public void deselectExpenseLine(String strKey) {
		AccountDetails acct = mapExpenseAccounts.get(strKey);
		mapExpenseMissing.put(strKey, acct);
		bDirty = true;
	}

	public void deselectIncomeLine(String strKey) {
		AccountDetails acct = mapIncomeAccounts.get(strKey);
		mapIncomeMissing.put(strKey, acct);
		bDirty = true;
	}

	/*
	 * delete lines
	 */
	public void deleteExpenseLine(String strKey) {
		mapExpenseAccounts.remove(strKey);
	}

	public void deleteIncomeLine(String strKey) {
		mapIncomeAccounts.remove(strKey);
	}

	public void deleteExpenseMissing(String strKey) {
		mapExpenseMissing.remove(strKey);
	}

	public void deleteIncomeMissing(String strKey) {
		mapIncomeMissing.remove(strKey);
	}

	/*
	 * Return the whole data table
	 */
	public List<BudgetLine> getExpenseLines() {
		return listExpenseLines;
	}

	public List<BudgetLine> getIncomeLines() {
		return listIncomeLines;
	}

	/*
	 * determine if dirty
	 */
	public boolean isDirty() {
		if (bDirty)
			return true;
		for (BudgetLine objLine : listExpenseLines) {
			if (objLine.isDirty())
				return true;
		}
		for (BudgetLine objLine : listIncomeLines) {
			if (objLine.isDirty())
				return true;
		}
		return false;
	}

	/*
	 * reset all dirty flags
	 */
	public void resetDirty() {
		bDirty = false;
		for (BudgetLine objLine : listExpenseLines) {
			objLine.setDirty(false);
		}
		for (BudgetLine objLine : listIncomeLines) {
			objLine.setDirty(false);
		}
	}

	/*
	 * gets
	 */
	/*
	 * file name
	 */
	public String getFileName() {
		return strFileName;
	}

	/*
	 * Roll up
	 */
	public boolean getRollup() {
		return bRollup;
	}

	/*
	 * Start Date
	 */
	public int getStartDate() {
		return iStartDate;
	}

	/*
	 * End Date
	 */
	public int getEndDate() {
		return iEndDate;
	}

	/*
	 * array of missing categories
	 */
	public SortedMap<String, AccountDetails> getExpenseMissing() {
		return mapExpenseMissing;
	}

	public SortedMap<String, AccountDetails> getIncomeMissing() {
		return mapIncomeMissing;
	}

	/*
	 * array of Selected categories
	 */
	public SortedMap<String, AccountDetails> getExpenseSelect() {
		return mapExpenseAccounts;
	}

	public SortedMap<String, AccountDetails> getIncomeSelect() {
		return mapIncomeAccounts;
	}

	/*
	 * Actuals totals
	 */
	public long[] getIncomeTotals() {
		return arrTotalActIncome;
	}

	public long[] getExpensesTotals() {
		return arrTotalActExpenses;
	}

	public long[] getGrandTotals() {
		return arrTotalAct;
	}

	/*
	 * colours
	 */
	public Color getColourHeaders() {
		return clrHeaders;
	}

	public Color getColourBudget() {
		return clrBudget;
	}

	public Color getColourActual() {
		return clrActual;
	}

	public Color getColourPositive() {
		return clrPositive;
	}

	public Color getColourNegative() {
		return clrNegative;
	}

	public Color getColourFGPositive() {
		return clrFGPositive;
	}

	public Color getColourFGNegative() {
		return clrFGNegative;
	}

	/*
	 * Table sizes
	 */
	public int getExpenseLineCount() {
		return (mapExpenseAccounts == null ? 0 : mapExpenseAccounts.size());
	}

	public int getIncomeLineCount() {
		return (mapIncomeAccounts == null ? 0 : mapIncomeAccounts.size());
	}

	public int getExpenseMissingCount() {
		return (mapExpenseMissing == null ? 0 : mapExpenseMissing.size());
	}

	public int getIncomeMissingCount() {
		return (mapIncomeMissing == null ? 0 : mapIncomeMissing.size());
	}

	/*
	 * sets
	 */
	/*
	 * set dirty flag
	 */
	public void setDirty(boolean bDir) {
		bDirty = bDir;
		return;
	}

	/*
	 * Start Date
	 */
	public void setStartDate(int iStart) {
		bDirty = true;
		iStartDate = iStart;
		return;
	}

	/*
	 * End Date
	 */
	public void setEndDate(int iEnd) {
		bDirty = true;
		iEndDate = iEnd;
		return;
	}

	/*
	 * Colours
	 */
	public void setColourHeaders(Color clrParm) {
		bDirty = true;
		clrHeaders = clrParm;
	}

	public void setColourBudget(Color clrParm) {
		bDirty = true;
		clrBudget = clrParm;
	}

	public void setColourActual(Color clrParm) {
		bDirty = true;
		clrActual = clrParm;
	}

	public void setColourPositive(Color clrParm) {
		bDirty = true;
		clrPositive = clrParm;
	}

	public void setColourNegative(Color clrParm) {
		bDirty = true;
		clrNegative = clrParm;
	}

	public void setColourFGPositive(Color clrFGParm) {
		bDirty = true;
		clrFGPositive = clrFGParm;
	}

	public void setColourFGNegative(Color clrFGParm) {
		bDirty = true;
		clrFGNegative = clrFGParm;
	}

	/*
	 * Save the parameters into the specified file
	 */
	public void saveParams(String strFileNamep) {
		strFileName = strFileNamep;
		strFullFileName = fiCurFolder.getAbsolutePath() + "\\" + strFileName
				+ ".bprp";
		try {
			fiCurInFile = new FileInputStream(strFullFileName);
			JFrame fTemp = new JFrame();
			int iResult = JOptionPane.showConfirmDialog(fTemp, "File "
					+ strFileName
					+ " already exists.  Do you wish to overwrite?");
			fiCurInFile.close();
			if (iResult != JOptionPane.YES_OPTION)
				return;
		} catch (IOException i) {
		}
		listExpenseLines.clear();
		for (Entry<String, AccountDetails> objEntry : mapExpenseAccounts
				.entrySet()) {
			listExpenseLines.add(objEntry.getValue().getLine());
		}
		listIncomeLines.clear();
		for (Entry<String, AccountDetails> objEntry : mapIncomeAccounts
				.entrySet()) {
			listIncomeLines.add(objEntry.getValue().getLine());
		}
		try {
			fiCurOutFile = new FileOutputStream(strFullFileName);
			ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
			oos.writeObject(this);
			oos.close();
			fiCurOutFile.close();
		} catch (IOException i) {
			i.printStackTrace();
		}
		/*
		 * clear dirty flags
		 */
		resetDirty();

	}

	/*
	 * Generate
	 */
	public void generate(FeatureModuleContext context, DateRange[] arrPeriods) {
		int iDepth = -1;
		int iPeriods = arrPeriods.length;
		arrTotalActIncome = new long[iPeriods + 1];
		arrTotalActExpenses = new long[iPeriods + 1];
		arrTotalAct = new long[iPeriods + 1];
		for (int i = 0; i < iPeriods + 1; i++) {
			arrTotalActIncome[i] = 0;
			arrTotalActExpenses[i] = 0;
			arrTotalAct[i] = 0;
		}
		BudgetLine[] objLast = new BudgetLine[10];
		String[] strLast = new String[10];
		for (BudgetLine objLine : listIncomeLines) {
			objLine.generateLine(Constants.INCOME_SCREEN, context, arrPeriods);
			long[] arrTemp = objLine.getTotals();
			for (int i = 0; i < arrTemp.length; i++) {
				arrTotalActIncome[i] += arrTemp[i];
				arrTotalAct[i] += arrTemp[i];
			}
			if (bRollup) {
				if (iDepth == -1) {
					iDepth++;
					objLast[iDepth] = objLine;
					strLast[iDepth] = objLine.getCategoryIndent();
					continue;
				}
				while ((objLine.getCategory().getDepth() <= objLast[iDepth]
						.getCategory().getDepth()) && iDepth > -1) {
					iDepth--;
					if (iDepth < 0)
						break;
				}
				/*
				 * go back through parent hierarchy and add generated line
				 */
				if (objLine.getType() == Constants.CHILD_LINE && iDepth > -1) {
					if (objLine.getParent().equals(strLast[iDepth])) {
						int iTemp = iDepth;
						while (iTemp > -1) {
							objLast[iTemp].addChild(objLine.getTotals());
							iTemp--;
						}
					}
				}
				if (objLine.getType() == Constants.PARENT_LINE) {
					iDepth++;
					objLast[iDepth] = objLine;
					strLast[iDepth] = objLine.getCategoryIndent();
				}
			}
		}
		iDepth = -1;
		for (BudgetLine objLine : listExpenseLines) {
			objLine.generateLine(Constants.EXPENSE_SCREEN, context, arrPeriods);
			long[] arrTemp = objLine.getTotals();
			for (int i = 0; i < arrTemp.length; i++) {
				arrTotalActExpenses[i] += arrTemp[i];
				arrTotalAct[i] -= arrTemp[i];
			}
			if (bRollup) {
				if (iDepth == -1) {
					iDepth++;
					objLast[iDepth] = objLine;
					strLast[iDepth] = objLine.getCategoryIndent();
					continue;
				}
				while ((objLine.getCategory().getDepth() <= objLast[iDepth]
						.getCategory().getDepth()) && iDepth > -1) {
					iDepth--;
					if (iDepth < 0)
						break;
				}
				/*
				 * go back through parent hierarchy and add generated line
				 */
				if (objLine.getType() == Constants.CHILD_LINE && iDepth > -1) {
					if (objLine.getParent().equals(strLast[iDepth])) {
						int iTemp = iDepth;
						while (iTemp > -1) {
							objLast[iTemp].addChild(objLine.getTotals());
							iTemp--;
						}
					}
				}
				if (objLine.getType() == Constants.PARENT_LINE) {
					iDepth++;
					objLast[iDepth] = objLine;
					strLast[iDepth] = objLine.getCategoryIndent();
				}
			}
		}
	}
}
