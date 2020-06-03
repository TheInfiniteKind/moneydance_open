/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import javax.swing.JOptionPane;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.DateUtil;

public class BudgetData  {
	protected Main              extension;
	private static final int    INDEX_ACT_NAME    = 1;
	private Account             root              = null;
	private boolean             taxIsIncome;
	private Account             mainAccount;
	
	private Map<Integer, String>     incomeAccounts  = new HashMap<Integer, String>();
	private Map<Integer, String>     moneyAccounts   = new HashMap<Integer, String>();
	private Map<Integer, String>     expenseAccounts = new HashMap<Integer, String>();
	
	@SuppressWarnings("unchecked")
	protected Map<String, String>[]       cellTypeData    = new Map[13];
	
	@SuppressWarnings("unchecked")
	private Map<String, BudgetValue>[]    spendingData = new Map[13];
	
	@SuppressWarnings("unchecked")
	private Map<String, BudgetValue>[]    budgetData   = new Map[13];
	
	@SuppressWarnings("unchecked")
	private Map<String, BudgetValue>[]    summaryData  = new Map[13];
	
	private int     budgetYear      = Calendar.getInstance().get(Calendar.YEAR);
	private String  budgetName      = null;
    private Budget  budgetCurrent   = null;
	  
    BudgetData(Main extension){
    	this.extension = extension;
    	this.refreshPreferences();
    	root = extension.getUnprotectedContext().getRootAccount();
	}
    
    private void refreshPreferences(){
    	BudgetPreferences preferences = this.extension.getPreferences();
        if(preferences.getDefaults("taxIsIncome").indexOf("y") > -1){
        	taxIsIncome = true;
        } else {
        	taxIsIncome = false;
        }
    }
    
    public void initSummaryData(){
    	for(int i = 0; i <= 12; i++){
    		this.summaryData[i]  = new HashMap<String, BudgetValue>();
		}
    }
    
    public Account getMainAccount(){
    	return mainAccount;
    }
    
    public Map<Integer, String> getIncomeAccounts(){
    	return incomeAccounts;
    }
    
    public Map<Integer, String> getMoneyAccounts(){
    	return moneyAccounts;
    }
    
    public Map<Integer, String> getExpenseAccounts(){
    	return expenseAccounts;
    }
    
    public boolean isSummaryNull(String aName, int month){
    	if(this.summaryData[month].get(aName) == null){
    		return true;
    	} else {
    		return false;
    	}
    }
    
    public boolean isSpendingNull(String aName, int month){
    	if(this.spendingData[month].get(aName) == null){
    		return true;
    	} else {
    		return false;
    	}
    }
    
    public boolean isBudgetNull(String aName, int month){
    	if(this.budgetData[month].get(aName) == null){
    		return true;
    	} else {
    		return false;
    	}
    }
    
    public BudgetValue getSummaryValue(String aName, int month){
    	if(this.summaryData[month].get(aName) != null){
    		return this.summaryData[month].get(aName);
    	} else {
    		return new BudgetValue(this, 0);
    	}
    }
    
    public BudgetValue getSpendingValue(String aName, int month){
    	if(this.spendingData[month].get(aName) != null){
    		return this.spendingData[month].get(aName);
    	} else {
    		return new BudgetValue(this, 0);
    	}
    }
    
    public BudgetValue getSTDValue(String aName, int month){
        BudgetValue stdValue = new BudgetValue(this, 0);
        for(int i=1; i<= month; i++){
        	 if(! this.isSpendingNull(aName, i)){
        		 BudgetValue thisValue = this.getSpendingValue(aName, i);
        		 stdValue.add(thisValue);
             }
        }
        
        return stdValue;
    }
    
    public BudgetValue getBudgetValue(String aName, int month){
    	if(this.budgetData[month].get(aName) != null){
    		return this.budgetData[month].get(aName);
    	} else {
    		return new BudgetValue(this, 0);
    	}
    }
    
    public BudgetValue getBTDValue(String aName, int month){
        BudgetValue btdValue = new BudgetValue(this, 0);
        for(int i=1; i<= month; i++){
        	 if(! this.isBudgetNull(aName, i)){
        		 BudgetValue thisValue = this.getBudgetValue(aName, i);
        		 btdValue.add(thisValue);
             }
        }
        
        return btdValue;
    }

    public void saveSummaryData(String aName, int month, BudgetValue value){
    	this.summaryData[month].put(aName, value);
    }

    protected Account getRoot(){
    	return root;
    }
	
    protected BudgetList getBudgetList(){
    	return root.getBook().getBudgets();
    }
    
    protected Budget getCurrentBudget(){
    	return budgetCurrent;
    }
    
    protected String getCurrentBudgetName(){
    	return budgetName;
    }
    
    protected int getCurrentBudgetYear(){
    	return budgetYear;
    }
    
    protected void setCurrentBudget(String bName, int bYear){
  	  budgetName = bName;
  	  if(bYear == 0){
          budgetYear = getYearOfBudget(bName);
  	  } else {
  		  budgetYear = bYear;
  	  }
    }
    
    protected void setCurrentBudget(String thisBudgetName){
    	this.budgetName = thisBudgetName;
    }
    
	protected void refresh(){
		refreshPreferences();
		fetchSpendingData();
		fetchBudgetData(budgetName, budgetData);
	}
	
	protected String getCellType(String acctName, int month){
		String cellType = "null";
		
		if(cellTypeData[month].get(acctName) != null){
   			cellType = ((String) cellTypeData[month].get(acctName)).toString();
		}
		
		return cellType;
	}
	
	protected int getYearOfBudget(String bName){
		  int year = 0;
		  
		  List<Budget> budgetList = this.getBudgetList().getAllBudgets();
		  Budget b = null;
		  
		  for (int i = 0; i < budgetList.size(); i++) {
			  b = budgetList.get(i);
	          if (b.getName().equals( bName )){
	        	  if(b.getItemList().getItemCount() > 0){
	    			  BudgetItem bi = b.getItemList().getItem(0);
	    			  String startDate = String.valueOf(bi.getIntervalStartDate()); 
	    			  String startYear = startDate.substring(0, 4);
	    			  year =  Integer.valueOf(startYear).intValue();
	    		  }
	          }
		  }
		  if(year == 0){
			  year = Calendar.getInstance().get(Calendar.YEAR);
		  }
		  return year;
	}

	public void repairDates(String budgetName){

		  List<Budget> budList = this.getBudgetList().getAllBudgets();
		  Budget b = null;
		  for (int i = 0; i < budList.size(); i++) {
			  b = budList.get(i);
	          if (b.getName().equals( budgetName )){

		          for (int j = 0; j < b.getItemList().getItemCount(); j++) {
		        	  BudgetItem bi = b.getItemList().getItem(j);
			          if(bi.getIntervalStartDate() > 0){
			        	  String startDate = String.valueOf(bi.getIntervalStartDate());
			        	  String endDate   = String.valueOf(bi.getIntervalEndDate());

			        	  String start_month  = startDate.substring(4, 6);
			        	  String start_day    = startDate.substring(6, 8);
			        	  String newStartDate = budgetName + start_month + start_day;

			        	  String end_month  = endDate.substring(4, 6);
			        	  String end_day    = endDate.substring(6, 8);
			        	  String newEndDate = budgetName + end_month + end_day;

			        	  bi.setIntervalStartDate(Integer.valueOf(newStartDate));
			        	  bi.setIntervalEndDate(Integer.valueOf(newEndDate));

			          }
			      }
	          }
	      }

	}
	
	public void roundValues(){

		  List<Budget> budList = this.getBudgetList().getAllBudgets();
		  Budget b = null;
		  for (int i = 0; i < budList.size(); i++) {
			  b = budList.get(i);
	          if (b.getName().equals( budgetName )){

		          for (int j = 0; j < b.getItemList().getItemCount(); j++) {
		        	  BudgetItem bi = b.getItemList().getItem(j);
		        	  
		        	  double amount = bi.getAmount();
		        	  if(amount > 1000){
		        		  amount = Math.round((amount + 500) / 1000.0) * 1000.0;
		        	  } else {
		        		  amount = Math.round((amount + 50)/ 100.0) * 100.0;
		        	  }
		        	  bi.setAmount((long)amount);
			      }
	          }
	      }

	}
	
	protected TxnSet getTxnSet(Account acct){
		if(root.getBook().getTransactionSet() == null){
			return null;
		}
		return root.getBook().getTransactionSet().getTransactionsForAccount(acct);
	}
	
	private void fetchSpendingData(){
		  incomeAccounts  = new HashMap<Integer, String>();
		  expenseAccounts = new HashMap<Integer, String>();
		  moneyAccounts   = new HashMap<Integer, String>();

		  for(int i = 0; i <= 12; i++){
			  spendingData[i]  = new HashMap<String, BudgetValue>();
		  }

		  if( root.getBook().getTransactionSet() != null) {
			  TxnSet ts = root.getBook().getTransactionSet().getAllTxns();
			  for (int i = 0; i < ts.getSize(); i++) {
		          AbstractTxn t = (AbstractTxn)ts.getTxn(i);
		          Account txnAccount    = t.getAccount();
		          AbstractTxn to = t.getOtherTxn(0);
		          if(to == null) {
		        	  this.println("ERROR: " + txnAccount.getFullAccountName());
		        	  continue;
		          }
		          
		          Account othAccount    = to.getAccount();
		          if(txnAccount.getComment().indexOf("IGNORE") > -1) continue;
		          if(othAccount.getComment().indexOf("IGNORE") > -1 && othAccount.getAccountType() == Account.AccountType.EXPENSE) continue;
		          if(txnAccount.getComment().indexOf("MAIN") > -1){
		        	  mainAccount = txnAccount;
		        	  continue;
		          }
		          if(othAccount.getComment().indexOf("MAIN") > -1 && othAccount.getAccountType() == Account.AccountType.EXPENSE) continue;

		          Integer accNum = Integer.valueOf(txnAccount.getAccountNum());
		          String  accName = txnAccount.getFullAccountName();
		          
		          if (BudgetDateUtil.isInRange(getTxnDate(t),
		        		                 new GregorianCalendar(budgetYear, 0, 1).getTime(),
		        		                 new GregorianCalendar(budgetYear, 11, 31).getTime())) {

		        	  Account topLvlAccount = txnAccount.getParentAccount();
			          while(topLvlAccount.getParentAccount() != null){
			        	  if(topLvlAccount.getParentAccount().getFullAccountName().length() > 0){
			        		  topLvlAccount = topLvlAccount.getParentAccount();
			        	  } else {
			        		  break;
			        	  }
			          }
			          
		        	  if( txnAccount.getAccountType() == Account.AccountType.INCOME || 
		        		 ( taxIsIncome && topLvlAccount.getFullAccountName().indexOf("Tax") > -1) ){
		        		  incomeAccounts.put(accNum,accName);
		        	  } else {
		        		  if( txnAccount.getAccountType() == Account.AccountType.EXPENSE && accName.indexOf("Bank Charges") < 0){
		        	      	  expenseAccounts.put(accNum,accName);
		        	      } else {
		        	      	  moneyAccounts.put(accNum,accName);
		        	      }
		        	  }
		        	  
		        	  addTransaction(spendingData[0], t);
		        	  addTransaction(spendingData[getTxnMonth(t)], t);
		          }
			  }
		  }


	}
	
	protected int getTxnMonth(AbstractTxn t) {
		return (t.getDateInt()/100) % 100;
	}
	
	protected Date getTxnDate(AbstractTxn t) {
		return DateUtil.convertIntDateToLong(t.getDateInt());
	}
	
	protected Date getDate(int dt) {
		return DateUtil.convertIntDateToLong(dt);
	}
	
	public boolean budgetDeleteItem(String categoryName, int month){
		  Budget b = this.getCurrentBudget();
		  if(b == null) return false;

		  Vector<BudgetItem> foundBudgets = new Vector<BudgetItem>();
	      for (int j = 0; j < b.getItemList().getItemCount(); j++) {
	    	  BudgetItem bi = b.getItemList().getItem(j);
	    	  if(bi.getIntervalStartDate() > 0){
	    		  Account a = bi.getTransferAccount();

	              if(a.getFullAccountName().equalsIgnoreCase(categoryName)){
	                  String startDate = String.valueOf(bi.getIntervalStartDate());
	                  int biMonth = Integer.parseInt(startDate.substring(4, 6));

	                  if(month == biMonth){
	                	  foundBudgets.add(bi);
	                  }
	              }
	    	  }
	      }
	      
	      if(foundBudgets.size() > 1){

	    	  //TODO: Some sort of dialog is needed to resolve this situation 
	    	  JOptionPane.showMessageDialog(null,
	    			    "More then one Budget item found. Action will be ignored",
	    			    "Multiple Items",
	    			    JOptionPane.ERROR_MESSAGE);
	    	  
	    	  //We need to return true so a new item is not added
	    	  return true;
	      } else{
	    	  if(foundBudgets.size() == 1) {
	    		  b.getItemList().removeItem(foundBudgets.get(0));
	    		  
	    		  b.syncItem();
	        	  return true;
	    	  }
	      }
	      
	      return false;
	}
	
	public void budgetAddZeroItem(String categoryName, int month){
		  budgetAdd(categoryName, month, new BudgetValue(this, 0), true);
	}
	  
	public void budgetAddItem(String categoryName, int month, BudgetValue value){
		  budgetAdd(categoryName, month, value, true);
	}
	  
	public void budgetAdd(String categoryName, int month, BudgetValue value, boolean allowZero){
		  Budget b = this.getCurrentBudget();
		  if(b == null) return;

		  if(value.isEqual(0) && ! allowZero) return;

		  Account ta = getAccount(this.getRoot(), categoryName);
	      BudgetItem ti = b.createItem();

	      ti.setAccount(ta);
	      ti.setTransferAccount(ta);
	      
	      value.setValue(value.dFormat().doubleValue() * 100);
	      ti.setAmount( value.longValue() );
	      ti.setInterval(BudgetItem.INTERVAL_NO_REPEAT);

	      String monthNum = String.valueOf(month);
	      if(month < 10) monthNum = "0" + monthNum;

		  ti.setIntervalStartDate(Integer.parseInt(this.getCurrentBudgetYear() + monthNum + "01"));
		  ti.setIntervalEndDate(Integer.parseInt(this.getCurrentBudgetYear() + 
				                                 monthNum + 
				                                 String.valueOf(BudgetDateUtil.getMonthEndDay(this.getCurrentBudgetYear(), month))));
		  
		  ti.syncItem();
		  b.syncItem();

	}
	
	public boolean budgetUpdateItem(String categoryName, int month, BudgetValue dataValue){
		  Budget b = this.getCurrentBudget();
		  if(b == null) return false;

		  Vector<BudgetItem> foundBudgets = new Vector<BudgetItem>();
	      for (int j = 0; j < b.getItemList().getItemCount(); j++) {
	    	  BudgetItem bi = b.getItemList().getItem(j);
	    	  if(bi.getIntervalStartDate() > 0){
	    		  Account a = bi.getTransferAccount();

	              if(a.getFullAccountName().equalsIgnoreCase(categoryName)){
	                  String startDate = String.valueOf(bi.getIntervalStartDate());
	                  int biMonth = Integer.parseInt(startDate.substring(4, 6));

	                  if(month == biMonth){
	                	  foundBudgets.add(bi);
	                  }
	              }
	    	  }
	      }
	      
	      if(foundBudgets.size() > 1){

	    	  //TODO: Some sort of dialog is needed to resolve this situation 
	    	  JOptionPane.showMessageDialog(null,
	    			    "More then one Budget item found. Value will be ignored",
	    			    "Multiple Items",
	    			    JOptionPane.ERROR_MESSAGE);
	    	  
	    	  //We need to return true so a new item is not added
	    	  return true;
	      } else{
	    	  if(foundBudgets.size() == 1) {
	        	  BudgetValue amount = new BudgetValue(this, dataValue);
	        	  amount.multiply(100.00d);
	        	  
	        	  BudgetItem bi = foundBudgets.get(0);
	        	  bi.setAmount( amount.longValue() );
	        	  
	        	  bi.syncItem();
	        	  return true;
	    	  }
	      }

	      return false;
	  }

	  public String[] getAccounts(Account parentAcct){
		  List<String> list = new ArrayList<String>();
		  
		  List<Account> accounts = parentAcct.getSubAccounts();
		  for (int i = 0; i < accounts.size(); i++) {
			  Account acct = accounts.get(i);
			  String acctName = acct.getFullAccountName();
			  
			  boolean isIgnored  = false;
			  boolean isInTable  = true;
			  boolean isMain     = false;
			  
			  if(acct.getComment().indexOf("MAIN") > -1){
				  isMain = true;
			  } else {
				  if(acct.getComment().indexOf("IGNORE") > -1){
					  isIgnored = true;
				  } else {
					  if(this.isSpendingNull(acctName, 0)) {
						  if(this.isBudgetNull(acctName, 0)) {
			        		  isInTable = false;
			        	  } else {
			        		  isInTable = true;
			        	  }
			          } else {
			        	  isInTable = true;
			          }
				  }
			  }


			  if( (isIgnored || ! isInTable) && ! isMain){
				  list.add(acctName);
			  }
			  
			  if(acct.getSubAccountCount() > 0){
				 String[] subAccounts = getAccounts(acct);
				 for (int j = 0; j < subAccounts.length; j++) { 
					    list.add(subAccounts[j]);
				 }
			  }
		  }
		  
		  return list.toArray(new String[0]);
	}
	
	public Account getAccount(String accountName){
	      Account fa = getAccount(this.root, accountName);

		  return fa;
	}
	  
	public Account getAccount(Account parentAcct, String accountName){
	      Account fa = null;

	      List<Account> accounts = parentAcct.getSubAccounts();
		  for (int i = 0; i < accounts.size(); i++) {
			  Account acct = accounts.get(i);
			  if(acct.getFullAccountName().equalsIgnoreCase(accountName)) return acct;

			  if(acct.getSubAccountCount() > 0){
				  fa = getAccount(acct, accountName);
			  }

			  if(fa != null) break;
		  }

		  return fa;
	}
	
	public BudgetItem getBudgetItem(String accountName, int month){
		Budget b = this.getCurrentBudget();
		BudgetItem bi = null;
		
		for (int j = 0; j < b.getItemList().getItemCount(); j++) {
			   BudgetItem tbi = b.getItemList().getItem(j);
		       Account a = tbi.getTransferAccount();
		       String  aName = a.getFullAccountName();
		          
		       if(aName.equalsIgnoreCase(accountName) && tbi.getIntervalStartDate() > 0){
		              Date startDay   = new GregorianCalendar(budgetYear, month-1, 1).getTime();
			          Date endDay     = new GregorianCalendar(budgetYear, month-1, BudgetDateUtil.getMonthEndDay(budgetYear, month)).getTime();

			          Date budStartDate = BudgetDateUtil.getDateYYYYMMDD(tbi.getIntervalStartDate());
				      Date budEndDate = BudgetDateUtil.getDateYYYYMMDD(tbi.getIntervalEndDate());

				      // Is it after end day?
				      if (budStartDate == null || budStartDate.after(endDay)) continue;
				      // Is it before start day
				      if (budEndDate != null && budEndDate.before(startDay)) continue;
				      
				      if (startDay.after(budStartDate)) continue;
				      
				      bi = tbi;
				      break;
		       }
		}
		
		return bi;
	}
	
	public double fetchBudgetValue(String accountName, int month){
		BudgetItem bi = getBudgetItem(accountName, month);
		double amount = 0;
		
		if(bi != null){
			amount = bi.getAmount() / 100.00;
		}

		return amount;
	}
	
	 public void fetchBudgetData(String budgetName, Map<String, BudgetValue>[] dataMap){

		  for(int i = 0; i <= 12; i++){
			  dataMap[i]       = new HashMap<String, BudgetValue>();
			  cellTypeData[i]  = new HashMap<String, String>();
		  }

		  List<Budget> budgetList = this.getBudgetList().getAllBudgets();
		  Budget b = null;
		  for (int i = 0; i < budgetList.size(); i++) {
			  b = budgetList.get(i);
	          if (b.getName().equals( budgetName )){
	        	  budgetCurrent = b;

		          for (int j = 0; j < b.getItemList().getItemCount(); j++) {
		        	  BudgetItem bi = b.getItemList().getItem(j);
			          Account a = bi.getTransferAccount();

			          if(bi.getIntervalStartDate() > 0 && 
			        		  a.getComment().indexOf("IGNORE") == -1 &&
			        		  a.getComment().indexOf("MAIN") == -1  ){
			        	  Integer accNum = new Integer(a.getAccountNum());
			              String  accName = a.getFullAccountName();
			              
			        	  for(int month = 1; month <= 12; month++){
			        		  Date startDay   = new GregorianCalendar(budgetYear, month-1, 1).getTime();
				        	  Date endDay     = new GregorianCalendar(budgetYear, month-1, BudgetDateUtil.getMonthEndDay(budgetYear, month)).getTime();

				              BudgetValue bAmount = (getBudgetedAmount(bi, startDay, endDay, month));

				              //Yes this is a hack, but I did not want to change the return object to deal with with
				              //No budget entry exists, different than a "0" value budget entry
				              if (bAmount.isNoEntry()) continue;

				              //Value was in cents, convert to dollars
				              bAmount.divide(100.00);
				              
				              //If there is already a budget value saved, overwrite it
				              BudgetValue cAmount = new BudgetValue(this, 0);
				              BudgetValue tAmount = new BudgetValue(this, 0);
				              if (dataMap[month].get(accName) != null){
				            	  cAmount.setValue(dataMap[month].get(accName));
				              }
				              if (dataMap[0].get(accName) != null){
				            	  tAmount.setValue(dataMap[0].get(accName));
				              }
				              
				              tAmount.minus(cAmount);
				              tAmount.add(bAmount);
				              
				              dataMap[month].put(accName,bAmount);
				              
				              dataMap[0].put(accName,tAmount);
				              cellTypeData[0].put(accName, "total");
			        	  }

			        	  Account topLvlAccount = a.getParentAccount();
				          while(topLvlAccount.getParentAccount() != null){
				        	  if(topLvlAccount.getParentAccount().getFullAccountName().length() > 0){
				        		  topLvlAccount = topLvlAccount.getParentAccount();
				        	  } else {
				        		  break;
				        	  }
				          }

			              if(a.getAccountType() == Account.AccountType.INCOME || 
			            	 ( taxIsIncome && topLvlAccount.getFullAccountName().indexOf("Tax") > -1) ){
			                incomeAccounts.put(accNum,accName);
			              } else {
			                if(a.getAccountType() == Account.AccountType.EXPENSE && accName.indexOf("Bank Charges") < 0 ){
			                  expenseAccounts.put(accNum,accName);
			                } else {
			                  moneyAccounts.put(accNum,accName);
			                }
			              }

			          }
			          
			          
			          
			      }
	          }
	      }

	  }
	 
	 private BudgetValue getBudgetedAmount(BudgetItem bi, Date startDay, Date endDay, int month) {
	      Date budStartDate = BudgetDateUtil.getDateYYYYMMDD(bi.getIntervalStartDate());
	      Date budEndDate = BudgetDateUtil.getDateYYYYMMDD(bi.getIntervalEndDate());
	      Date budDt = budStartDate;

	      BudgetValue amount = new BudgetValue(this, 0);
	      // Is it after end day?
	      if (budStartDate == null || budStartDate.after(endDay)){
	    	  amount.setIsNoEntry(true);
	    	  return amount;
	      }
	      // Is it before start day
	      if (budEndDate != null && budEndDate.before(startDay)){
	    	  amount.setIsNoEntry(true);
	    	  return amount;
	      }

	      boolean done         = false;
	      boolean entryInRange = false;
	      int count = 0;
	      while (!done) {
	              // Is budget in range
	              if (BudgetDateUtil.isInRange(budDt, startDay, endDay)) {
	            	      amount.add(bi.getAmount());
	                      entryInRange = true;
	                      count++;
	              }
	              // Get next budgeted date
	              int interval = bi.getInterval();
	              if(interval > 50){
	            	  interval = interval - 50;
	              }
	              switch (interval) {
	                      case BudgetItem.INTERVAL_ANNUALLY: budDt   = BudgetDateUtil.addYears(budDt  , 1); break;
	                      case BudgetItem.INTERVAL_BI_MONTHLY: budDt = BudgetDateUtil.addMonths(budDt , 2); break;
	                      case BudgetItem.INTERVAL_BI_WEEKLY: budDt  = BudgetDateUtil.addWeeks(budDt  , 2); break;
	                      case BudgetItem.INTERVAL_DAILY:budDt       = BudgetDateUtil.addDays(budDt   , 1); break;
	                      case BudgetItem.INTERVAL_MONTHLY:budDt     = BudgetDateUtil.addMonths(budDt , 1); break;
	                      case BudgetItem.INTERVAL_SEMI_ANNUALLY: {
	                              if (BudgetDateUtil.isSameDayOfYear(budDt,budStartDate)) {
	                                      budDt = BudgetDateUtil.addDays(budDt,182);
	                              } else {
	                                      budDt = BudgetDateUtil.addDays(budDt,-182);
	                                      budDt = BudgetDateUtil.addYears(budDt, 1);
	                              }
	                              break;
	                      }
	                      case BudgetItem.INTERVAL_SEMI_MONTHLY: {
	                              if (BudgetDateUtil.isSameDayOfMonth(budDt,budStartDate)) {
	                                      budDt = BudgetDateUtil.addDays(budDt,15);
	                              } else {
	                                      budDt = BudgetDateUtil.addDays(budDt,-15);
	                                      budDt = BudgetDateUtil.addMonths(budDt, 1);
	                              }
	                              break;
	                      }
	                      case BudgetItem.INTERVAL_TRI_MONTHLY: budDt = BudgetDateUtil.addMonths(budDt , 3); break;
	                      case BudgetItem.INTERVAL_TRI_WEEKLY: budDt  = BudgetDateUtil.addWeeks(budDt  , 3); break;
	                      case BudgetItem.INTERVAL_WEEKLY: budDt      = BudgetDateUtil.addWeeks(budDt  , 1); break;
	                      default: {
	                    	  done = true;
	                      }
	              }

	              // Is it past date
	              if (budDt.after(endDay) || budDt.after(budEndDate)) {
	                      break;
	              }
	      }

	      if(! entryInRange){
	    	  amount.setIsNoEntry(true);
	    	  return amount;
	      }
	      
	      //Repair Budget Items, set as No Repeat
	      if(bi.getInterval() != BudgetItem.INTERVAL_NO_REPEAT && count == 1){
	    	  if(bi.getInterval() == BudgetItem.INTERVAL_MONTHLY){
	    		  long MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24;
	    		  long deltaDays = ( budEndDate.getTime() - budStartDate.getTime() )/ MILLISECONDS_PER_DAY;
	    		  if(deltaDays <= 31){
	    			  bi.setInterval(BudgetItem.INTERVAL_NO_REPEAT); 
	    		  }
	    	  }
	      }
	      
	      if(bi.getInterval() != BudgetItem.INTERVAL_NO_REPEAT){
	    	  int bMonth = (new Integer(String.valueOf(bi.getIntervalStartDate()).substring(4, 6))).intValue();
		      if(month > bMonth){
		    	  cellTypeData[month].put(bi.getTransferAccount().getFullAccountName(), "repeat"); 
		      } else {
		    	  cellTypeData[month].put(bi.getTransferAccount().getFullAccountName(), "origin"); 
		      }
	      } else {
	    	  String currentValue = cellTypeData[month].get(bi.getTransferAccount().getFullAccountName());
	    	  if(currentValue != null){
	    		  //System.err.println(bi.getTransferAccount().getFullAccountName() + " X-X " + month + " = " + amount);
	    		  if( ! currentValue.equalsIgnoreCase("origin") ){
	    			  cellTypeData[month].put(bi.getTransferAccount().getFullAccountName(), "single");
		    	  } 
	    	  }
	      }
	      
	      return amount;
	 }
	 
	 private void addTransaction(Map<String, BudgetValue>  txnMap, AbstractTxn t) {
		  addTransaction(txnMap, t, INDEX_ACT_NAME);
	 }

	 private void addTransaction(Map<String, BudgetValue> txnMap, AbstractTxn t, int mapIndex) {
	      if (t == null) return;

	      Account   txnAccount = t.getAccount();
	      
	      BudgetValue tValue = new BudgetValue(this, t.getValue());
	      tValue.setAccount(txnAccount);
		  
	      BudgetValue amount = new BudgetValue(this, tValue);
	      
	      amount.divide(100.00);
	      
	      BudgetValue sAmount = new BudgetValue(this, 0);

	      String  accName      = txnAccount.getFullAccountName();
	      
	      Account topLvlAccount = txnAccount.getParentAccount();
	      while(topLvlAccount.getParentAccount() != null){
	    	  if(topLvlAccount.getParentAccount().getFullAccountName().length() > 0){
	    		  topLvlAccount = topLvlAccount.getParentAccount();
	    	  } else {
	    		  break;
	    	  }
	      }

	      if (txnAccount.getAccountType() == Account.AccountType.INCOME || 
	    	  ( taxIsIncome && topLvlAccount.getFullAccountName().indexOf("Tax") > -1) ){
	    	  amount.negate();
	      }

	      if (txnMap.get(accName) != null){
	    	  sAmount.setValue(txnMap.get(accName));
	      }
	      sAmount.add(amount);
	      txnMap.put(accName,sAmount.dFormat());
	}
	 
    void println(String message){
		  java.util.Date date= new java.util.Date();
		  System.err.println(new Timestamp(date.getTime()) + " : " + message);
    }
}
