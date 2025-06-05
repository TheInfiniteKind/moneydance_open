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

package com.moneydance.modules.features.budgetgen;

import java.awt.GridBagLayout;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.prefs.Preferences;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextField;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.BudgetItem;
import com.infinitekind.moneydance.model.DateRange;
import com.infinitekind.util.DateUtil;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBInconsistencyException;

/*
 * Container for all parameters for the budget.  Data is serialised into file
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
	private transient BudgetExtend objCurBudget;
	private transient File fiCurFolder;
	private transient FileInputStream fiCurInFile;
	private transient FileOutputStream fiCurOutFile;
	private transient String strFileName;
	private transient String strFullFileName;
	private transient boolean bDirty;
    private transient SortedMap<String,AccountDetails> mapAccounts;
    private transient SortedMap<String,String> mapAcctName;
    private transient SortedMap<String,String> mapIndentName;
    private transient SortedMap<String,AccountDetails> mapMissing;
    private transient int iBudgetPer;
    private transient int iType;
    private transient int iPriorStart;
    private transient int iPriorEnd;
    private transient List<String> missing;
    /*
     * Table to link budget intervals item intervals
     */
    private static final Map<Integer, Integer> intervaltypes;
    static
    {
    		intervaltypes = new HashMap<Integer,Integer>();
		 	intervaltypes.put (Constants.PERIODANNUAL,BudgetItem.INTERVAL_ANNUALLY); 
			intervaltypes.put (Constants.PERIODWEEKLY,BudgetItem.INTERVAL_WEEKLY); 
			intervaltypes.put (Constants.PERIODBIWEEKLY,BudgetItem.INTERVAL_BI_WEEKLY); 
			intervaltypes.put (Constants.PERIODMONTHLY,BudgetItem.INTERVAL_MONTHLY); 
    }
   /*
     * The following fields are stored
     */

	private int iStartDate;
	private int iEndDate;
	private double dRPI;
	private int iDatePer;
	private List<BudgetLine> listBudgetLines;
	private boolean bManual;
	/*
	 * Constructor
	 */
	public BudgetParameters(FeatureModuleContext context, BudgetExtend objBudget,JDateField jdtFiscalStart,
			int iTypep, String strFileNamep) throws MRBInconsistencyException {

		Main.debugInst.debug("BudgetParameters","Constructor",MRBDebug.SUMMARY, "Budget Parameters Created");
        mapAccounts = new TreeMap<String,AccountDetails>();
        mapAcctName = new TreeMap<String,String>();
        mapIndentName = new TreeMap<String,String>();
		conCurrentCon = context;
		objCurBudget = objBudget;
		iType = iTypep;
		strFileName = strFileNamep;

		/*
		 * set parameters to default
		 * 	Start Date - Fiscal Year
		 *  End Date - Fiscal End
		 *  RPI - 0.0
		 *  Values Window Width - Constants.FRAMEWIDTH
		 *  Values Window Height - Constants.FRAMEDEPTH
		 *  Date Period - 0 fiscal year
		 */
		Calendar calTemp = Calendar.getInstance();
		JDateField jdtTemp = new JDateField(Main.cdate);
		iStartDate = jdtFiscalStart.getDateInt();
		calTemp.set(iStartDate/10000, iStartDate/100-iStartDate/10000*100-1, iStartDate - iStartDate/100*100);
		calTemp.add(Calendar.YEAR, 1);
		jdtTemp.setDate(calTemp.getTime());
		jdtTemp.decrementDate();
		iEndDate = jdtTemp.getDateInt();
		dRPI = 0.0;
		iBudgetPer = objCurBudget.getPeriodOrder();
		iDatePer = 0;
		bManual = false;
		/*
		 * load Expense Accounts
		 */
		rootAcct = conCurrentCon.getRootAccount();
		try {
			loadAccounts(rootAcct, mapAccounts,mapAcctName,"", iType);
		}
	    catch (MRBInconsistencyException e) {
	    	  e.printStackTrace();
        }
		/*
		 * mapMissing used to hold Expense Accounts declared in the main file but not
		 * being used by this budget.  Will only have entries if new entries added to the 
		 * main file or if user has deleted an Account from the budget.
		 */
		mapMissing = new TreeMap<String,AccountDetails>(mapAccounts);
		/*
		 * determine if file already exists
		 */
		abCurAcctBook = context.getCurrentAccountBook();
		fiCurFolder = abCurAcctBook.getRootFolder();
		/*
		 * File name comes from Select screen.  If it is blank then
		 * name is budgetname.BPEX for expenses, budgetname.BPIC for income
		 */
		if (strFileName == null || strFileName.equals("")) {
			strFileName = objCurBudget.getKey();
			saveFileName(strFileName);
		}
		if (iType == Constants.EXPENSE_SCREEN)
			strFullFileName = fiCurFolder.getAbsolutePath()+"\\"+strFileName+".bpex";
		else
			strFullFileName = fiCurFolder.getAbsolutePath()+"\\"+strFileName+".bpic";
		try {
			fiCurInFile = new FileInputStream(strFullFileName);
			ObjectInputStream ois = new ObjectInputStream(fiCurInFile);
			/*
			 * file exists, copy temporary object to this object
			 */
			Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.SUMMARY, "Parameter File "+strFullFileName + " Exists");
			BudgetParameters objTemp = (BudgetParameters) ois.readObject();
			this.iStartDate = objTemp.iStartDate;
			this.iEndDate = objTemp.iEndDate;
			this.dRPI = objTemp.dRPI;
			this.iDatePer = objTemp.iDatePer;
			this.listBudgetLines = objTemp.listBudgetLines;
			this.bManual = objTemp.bManual;
			/*
			 * can not guarantee Account object ids are correct,
			 * go through the budget lines and set the account object ids using
			 * a map of names to object ids
			 * 
			 * Set date to force set up of internal fields
			 */
			Iterator<BudgetLine> itLine = listBudgetLines.iterator();
			missing = new ArrayList<>();
			while (itLine.hasNext()) {
				BudgetLine objLine = itLine.next();
				if (mapIndentName.get(objLine.getCategoryIndent())== null) {
					missing.add("The Category "+objLine.getCategoryIndent()+" is no longer in the file.  It has been dropped.");
					itLine.remove();
					Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.SUMMARY, "Account not in file ="+objLine.getCategoryIndent());					
				}
				else {
					if (mapAccounts.get(mapIndentName.get(objLine.getCategoryIndent())) == null) {
						missing.add("Account not found="+objLine.getCategoryIndent());
						Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.DETAILED, "Account not found="+objLine.getCategoryIndent());					
						objLine.setCategory(null);
					}
					else {
						AccountDetails objDetail = mapAccounts.get(mapIndentName.get(objLine.getCategoryIndent()));
						objLine.setCategory(objDetail.getAccount());
						objLine.setStartDate(objLine.getStartDate());
						objLine.setParent(objDetail.getParent());
						objDetail.setLine(objLine);
						Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.DETAILED, "Account in parameters="+objLine.getCategoryIndent());
				    }
					/*
					 * remove from the mapMissing map to leave a list of those not in budgetlines
					 */
					mapMissing.remove(mapIndentName.get(objLine.getCategoryIndent()));
				}
			}
			if (!missing.isEmpty()) {
				String message = "The following errors have occurred when loading the parameters\n";
				for (String mess : missing) {
					message +=mess+"\n";
				}
				JFrame fTemp = new JFrame();
				JOptionPane
				.showMessageDialog(fTemp,message);
			}
			/*
			 * now remove entries that no longer exist
			 */
			for (Iterator<BudgetLine> iter = listBudgetLines.listIterator(); iter.hasNext(); ) {
			    BudgetLine a = iter.next();
			    if (a.getCategory() == null) {
			        iter.remove();
			    }
			}
			Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.DETAILED, "iStartDate="+iStartDate);
			Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.DETAILED, "iEndDate="+iEndDate);
			Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.DETAILED, "dRPI="+dRPI);
			Main.debugInst.debug("BudgetParameters","loadParameters",MRBDebug.DETAILED, "iDatePer="+iDatePer);
			fiCurInFile.close();
		}
		catch (IOException | ClassNotFoundException ioException) {
			/*
			 * file does not exist
			 */
			listBudgetLines = new ArrayList<BudgetLine>();
			/*
			 * load Categories into the Budget Line by traversing the accounts
			 */
			rootAcct = conCurrentCon.getRootAccount();

			/*
			 * traverse sorted map to get categories in ascending order,create budget lines and add
			 * to map
			 */
			for (Map.Entry<String,AccountDetails> mapEntry : mapAccounts.entrySet()){
				  String strIndentName = mapAcctName.get(mapEntry.getKey());
				  if (strIndentName == "")
					  strIndentName = mapEntry.getKey();
				  BudgetLine objLine = new BudgetLine(Constants.CHILD_LINE,strIndentName,
		    			  mapEntry.getValue().getAccount(), iStartDate,Constants.mapDatePeriod.get(iBudgetPer));
				  mapEntry.getValue().setLine(objLine);
				  objLine.setParent(mapEntry.getValue().getParent());
		    	  listBudgetLines.add(objLine);
		    	  mapMissing.remove(mapIndentName.get(objLine.getCategoryIndent()));
			}
			/*
			 * create the file
			 */
			try {
				fiCurOutFile = new FileOutputStream(strFullFileName);
				ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
				oos.writeObject(this);
				fiCurOutFile.close();
			}
			catch(IOException i)
			{
				i.printStackTrace();
			}
		}
		try {
			setPriorDates();
			/*
			 * put budget lines in ascending indented name order
			 */
			Collections.sort(listBudgetLines);
			/*
			 * set the type for parents
			 */
			setParents();
		}
		catch (MRBInconsistencyException e) {
			e.printStackTrace();
		}
	}
	/*
	 * Go through the budget lines and set the type.  If category has a parent set parent line.
	 */
	public void setParents() throws MRBInconsistencyException {
		for (BudgetLine objLine : listBudgetLines) {
			objLine.setType(Constants.CHILD_LINE);
			Account objParent = mapAccounts.get(mapIndentName.get(objLine.getCategoryIndent())).getAccount().getParentAccount();
			if (objParent != null && objParent != rootAcct) {
				while (objParent != null && objParent != rootAcct) {
					String strIndentName = mapAcctName.get(objParent.getFullAccountName());
					if (strIndentName == null || strIndentName.equals(""))
						continue;
					BudgetLine objParentLine = mapAccounts.get(objParent.getFullAccountName()).getLine();
					objParentLine.setType(Constants.PARENT_LINE);
					Account objTemp =objParent.getParentAccount();
					if (objTemp == objParent) {
						throw new MRBInconsistencyException(new Throwable("Parent equals Account "+objTemp.getFullAccountName()));
					}
					if (objTemp == null || objTemp == rootAcct)
						break;
					objParent = objTemp;
				}
			}
		}
	}

	/*
	 * Create a table of category names and account objects
	 * Account name is made up of all accounts in path
	 */
	 private void loadAccounts(Account parentAcct, Map<String, AccountDetails> mapAccounts,
			 Map<String,String> mapAcctName,String strIndentp, int iType) throws MRBInconsistencyException {
	    int sz = parentAcct.getSubAccountCount();
	    String strIndent;
	    strIndent = strIndentp;
	    for(int i=0; i<sz; i++) {
	      Account acct = parentAcct.getSubAccount(i);
	      if (mapAcctName.get(acct.getFullAccountName()) != null) {
				throw new MRBInconsistencyException(new Throwable(
						"Account name "+acct.getFullAccountName()+" already defined "));
	      }
	      if (iType == Constants.EXPENSE_SCREEN) {
		      if (acct.getAccountType() == Account.AccountType.EXPENSE) {
		    	  String strAcct = acct.getFullAccountName();
		    	  String strIndentName = strIndent + Constants.chSeperator+acct.getAccountName();
		    	  mapAccounts.put(strAcct, new AccountDetails(acct, strIndentp));
		    	  mapAcctName.put(strAcct, strIndentName);
		    	  mapIndentName.put(strIndentName, strAcct);
		      }
		      try {
		    	  loadAccounts(acct, mapAccounts,mapAcctName,strIndent + Constants.chSeperator+acct.getAccountName(), iType);
		      }
		      catch (MRBInconsistencyException e) {
		    	  e.printStackTrace();
		      }
	      }
	      else {
		      if (acct.getAccountType() == Account.AccountType.INCOME) {
		    	  String strAcct = acct.getFullAccountName();
		    	  String strIndentName = strIndent + Constants.chSeperator+acct.getAccountName();
		    	  mapAccounts.put(strAcct,new AccountDetails(acct, strIndentp));
		    	  mapAcctName.put(strAcct, strIndentName);
		    	  mapIndentName.put(strIndentName, strAcct);
		      }
		      try {
		    	  loadAccounts(acct, mapAccounts,mapAcctName,strIndent + Constants.chSeperator+acct.getAccountName(), iType);
		      }
		      catch (MRBInconsistencyException e) {
		    	  e.printStackTrace();
		      }
	      }
	    }
	 
	 }	
	 public int getLineCount() {
		return (listBudgetLines == null ? 0 :listBudgetLines.size());
	 }
	/*
	 * add a category from missing list
	 * 
	 * add to lines, remove from missing list
	 */
	public void addCategory(String strCategory) {
		if (mapMissing.containsKey(strCategory)) {
			Main.debugInst.debug("BudgetParameters","addCategory",MRBDebug.DETAILED, "Category added="+strCategory);
			AccountDetails acct = mapMissing.get(strCategory);
			mapMissing.remove(strCategory);
			BudgetLine objLine = new BudgetLine(Constants.CHILD_LINE,mapAcctName.get(strCategory),acct.getAccount(),iStartDate,Constants.mapDatePeriod.get(iBudgetPer));
			listBudgetLines.add(objLine);
			acct.setLine(objLine);
			mapAccounts.put(strCategory,acct);
			setParents();
		}
	}
	/*
	 * Return the whole data table
	 */
	public List<BudgetLine> getLines(){
		return listBudgetLines;
	}
	/*
	 * get individual line
	 */
	public BudgetLine getItem(int i) {
		return listBudgetLines.get(i);
	}
	/*
	 * determine if dirty
	 */
	public boolean isDirty() {
		if (bDirty)
			return true;
		for (BudgetLine objLine : listBudgetLines){
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
		for (BudgetLine objLine : listBudgetLines){
			objLine.setDirty(false);
		}
	
	}
	/*
	 * gets
	 * 
	 * Budget Period
	 */
	public int getPeriod() {
		return iBudgetPer;
	}
	/*
	 * Date Period
	 */
	public int getDatePeriod() {
		return iDatePer;
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
	public int getPriorStart() {
		return iPriorStart;
	}
	/*
	 * End Date
	 */
	public int getPriorEnd() {
		return iPriorEnd;
	}
	
	public int getPriorDays() {
		return DateUtil.calculateDaysBetween(iPriorStart, iPriorEnd);

	}
	/*
	 * RPI
	 */
	public double getRPI() {
		return dRPI;
	}
	/*
	 * Manual, set when user updates generated figures manually
	 */
	public boolean getManual() {
		return bManual;
	}
	/*
	 * array of missing categories
	 */
	public SortedMap<String, AccountDetails> getMissing() {
		return mapMissing;
	}
	/*
	 * sets
	 * 
	 * Budget Period
	 */
	public void setPeriod(int iPer) {
		iBudgetPer = iPer;
		return;
	}
	/*
	 * Date Period
	 */
	public void setDatePeriod (int iDatePerp){
		iDatePer = iDatePerp;
	}
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
		setPriorDates();
		return;
	}
	/*
	 * End Date
	 */
	public void setEndDate(int iEnd) {
		bDirty = true;
		iEndDate = iEnd;
		setPriorDates();
		return;
	}
	private void setPriorDates() throws MRBInconsistencyException {
		int iDays = DateUtil.calculateDaysBetween(iStartDate, iEndDate);
		int iDaystart = 0;
		Calendar calTemp = Calendar.getInstance();
		calTemp.setTime(DateUtil.convertIntDateToLong(iStartDate));
		while (iDaystart < iDays) {
			int iTemp = iDaystart;
			switch (iBudgetPer) {
			case Constants.PERIODANNUAL :
				calTemp.add(Calendar.YEAR, -1);
				iDaystart +=366;
				break;
			case Constants.PERIODBIWEEKLY :
				calTemp.add(Calendar.DAY_OF_YEAR, -14);
				iDaystart +=14;
				break;
			case Constants.PERIODWEEKLY :
				calTemp.add(Calendar.DAY_OF_YEAR, -7);
				iDaystart +=7;
				break;
			default:
				DateUtil.setToBeginningOfMonth(calTemp);
				calTemp.add(Calendar.MONTH, -1);
				iDaystart += DateUtil.calculateDaysInMonth(DateUtil.convertCalToInt(calTemp));
			}
			if (iDaystart <= iTemp) {
				throw new MRBInconsistencyException (new Throwable("Budget period inconsistent"));
			}
		}
		iPriorEnd = DateUtil.convertDateToInt(DateUtil.decrementDate(DateUtil.convertIntDateToLong(iStartDate)));
		iPriorStart = DateUtil.convertCalToInt(calTemp);
	}
	/*
	 * RPI
	 */
	public void setRPI(double dRPIp) {
		bDirty = true;
		dRPI = dRPIp;
		return;
	}
	/*
	 * Manual, set when user updates generated figures manually
	 */
	public void setManual(boolean bManualp) {
		bManual = bManualp;
	}
	/*
	 * calculation 
	 * 
	 */
	public boolean calculateAll () {
		return calculateLines("ALL");
	}

	public boolean calculateSelected () {
		return calculateLines("SELECT");
	}
	
	public boolean calculateLines(String strType) {
		boolean bActive= false;
		BudgetLine[] objLast = new BudgetLine[10];
		String[] strLast = new String[10];
		int iDepth = 0;
		boolean[] bInitialised  = new boolean[10];
		for (BudgetLine objLine : listBudgetLines) {
			if (objLine.getType() == Constants.PARENT_LINE) {
				if (objLine.getRollup()){
					iDepth++;
					objLast[iDepth] = objLine;
					strLast[iDepth] = objLine.getCategoryIndent();
					bInitialised[iDepth] = false;
				}
			}
			if (strType.equals("ALL") || objLine.getSelect()) {
				if (objLine.getAmount()!= 0) {
					objLine.calculateLine(iStartDate, iEndDate, dRPI);
					if (objLine.getParent().equals(strLast[iDepth])) {
						int iTemp = iDepth;
						while (iTemp > 0){
							if (!bInitialised[iTemp]) {
								objLast[iTemp].setAmount(0L);
								objLast[iTemp].setYear1Amt(0L);
								objLast[iTemp].setYear2Amt(0L);
								objLast[iTemp].setYear3Amt(0L);
								bInitialised[iTemp] = true;
							}
							objLast[iTemp].setYear1Amt(objLast[iTemp].getYear1Amt()+objLine.getYear1Amt());
							objLast[iTemp].setYear2Amt(objLast[iTemp].getYear2Amt()+objLine.getYear2Amt());
							objLast[iTemp].setYear3Amt(objLast[iTemp].getYear3Amt()+objLine.getYear3Amt());
							iTemp--;
						}
					}
					bActive = true;
				}
			}
		}
		return bActive;
	}
	/*
	 * delete a specific line, add it to mapMissing
	 */
	public void deleteLine(int iRow) {
		String strAccount = listBudgetLines.get(iRow).getCategoryIndent();
		AccountDetails acct = mapAccounts.get(strAccount);
		mapMissing.put(strAccount, acct);
		mapAccounts.remove(strAccount);
		listBudgetLines.remove(iRow);
		bDirty = true;
	}

	/*
	 * Save the parameters into the specified file
	 */
	public void saveParams() {
		String strFileNamep = askForFileName(strFileName);
		if (strFileNamep.equals(Constants.CANCELLED))
			return;
		if (iType == Constants.EXPENSE_SCREEN)
			strFullFileName = fiCurFolder.getAbsolutePath()+"\\"+strFileNamep+".bpex";
		else
			strFullFileName = fiCurFolder.getAbsolutePath()+"\\"+strFileNamep+".bpic";
		try {
			fiCurInFile = new FileInputStream(strFullFileName);
			JFrame fTemp = new JFrame();
			int iResult = JOptionPane
					.showConfirmDialog(fTemp,
							"File already exists.  Do you wish to overwrite?");
			fiCurInFile.close();
			if (iResult != JOptionPane.YES_OPTION) 
				return;
		}
		catch (IOException i) {}
		try {
			fiCurOutFile = new FileOutputStream(strFullFileName);
			ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
			oos.writeObject(this);
			oos.close();
			fiCurOutFile.close();
		}
		catch(IOException i)
		{
			i.printStackTrace();
		}
		/*
		 * clear dirty flags, save file name in preferences
		 */
		resetDirty();
		saveFileName(strFileNamep);
		strFileName = strFileNamep;

		
	}
	/*
	 * ask for parameters file name
	 */
	private String askForFileName(String strFileNamep) {
		String strFileName;
		JPanel panInput = new JPanel(new GridBagLayout());
		JLabel lblType = new JLabel("Enter File Name:");
		strFileName = strFileNamep;
		panInput.add(lblType, GridC.getc(0,0).insets(10, 10, 10, 10));
		JTextField txtType = new JTextField();
		txtType.setText(strFileName);
		txtType.setColumns(20);
		panInput.add(txtType, GridC.getc(1,0).insets(10, 10, 10, 10));
		while (true) {
			int iResult = JOptionPane.showConfirmDialog(null, panInput,
					"Save Parameters", JOptionPane.OK_CANCEL_OPTION);
			if (iResult == JOptionPane.OK_OPTION) {
				if (txtType.getText().equals("")) {
					JOptionPane.showMessageDialog(null,
							"File Name can not be blank");
					continue;
				}
				strFileName = txtType.getText();
				break;
			}
			if (iResult == JOptionPane.CANCEL_OPTION) {
				strFileName = Constants.CANCELLED;
				break;
			}
		}
		return strFileName;

	}	/*
	 * Generate
	 */
	public void generate(DateRange[] arrPeriods) {
		BudgetLine[] objLast = new BudgetLine[10];
		int[] arrDepth = new int[10];
		String[] strLast = new String[50];
		int iDepth = 0;
		arrDepth[0] = 0;
		boolean[] bInitialised  = new boolean[10];
		for (BudgetLine objLine : listBudgetLines) {
			while (iDepth > 0 && objLine.getCategory().getDepth() <= arrDepth[iDepth])
				iDepth--;
			if (objLine.getType() == Constants.PARENT_LINE) {
				if (objLine.getRollup()){
					iDepth++;
					objLast[iDepth] = objLine;
					strLast[iDepth] = objLine.getCategoryIndent();
					arrDepth[iDepth] = objLine.getCategory().getDepth();
					bInitialised[iDepth] = false;
				}
			}
			/*
			 * go back through parent hierarchy and add generated line
			 */
			objLine.generateLine(arrPeriods, this);
			if (objLine.getParent().equals(strLast[iDepth])) {
				int iTemp = iDepth;
				while (iTemp > 0){
					objLast[iTemp].addChild(1,bInitialised[iTemp],objLine.getYear1Array());
					objLast[iTemp].addChild(2,bInitialised[iTemp],objLine.getYear2Array());
					objLast[iTemp].addChild(3,bInitialised[iTemp],objLine.getYear3Array());
					bInitialised[iTemp] = true;
					iTemp--;
				}
			}
		}
		setManual(false);
	}
	/*
	 * update user preferences with file name
	 */
	public void saveFileName(String strFileName) {
		Preferences objRoot = Preferences.userRoot();
		Preferences objPref = objRoot.node(Constants.PREFERENCESNODE);
		objPref.put(Constants.FILENAMEPREF, strFileName);

	}
}
