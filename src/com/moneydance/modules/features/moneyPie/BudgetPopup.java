package com.moneydance.modules.features.moneyPie;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.ButtonGroup;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JRadioButtonMenuItem;
import javax.swing.JSeparator;
import javax.swing.JTable;

import java.awt.Component;

import com.infinitekind.moneydance.model.*;

@SuppressWarnings("serial")
public class BudgetPopup extends javax.swing.JPopupMenu {

	  private BudgetWindow  main;
	  private BudgetData    data;
	  private int row;
	  private int col;
	  private BudgetItem bi;
	  private JMenu repeatMenuItem;
	  private JRadioButtonMenuItem repeatNone;
	  private JRadioButtonMenuItem repeatDailyItem;
	  private JRadioButtonMenuItem repeatWeeklyItem;
	  private JRadioButtonMenuItem repeatBiWeeklyItem;
	  private JRadioButtonMenuItem repeatTriWeeklyItem;
	  private JRadioButtonMenuItem repeatMonthlyItem;
	  private JRadioButtonMenuItem repeatBiMonthlyItem;
	  private JRadioButtonMenuItem repeatSemiMonthlyItem;
	  private JRadioButtonMenuItem repeatTriMonthlyItem;
	  private JRadioButtonMenuItem repeatSemiAnnualtem;
	  private JRadioButtonMenuItem repeatAnnualItem;
	  private JMenuItem editDatamenuItem;
	  private JMenuItem addMenuItem;
	  private JMenuItem ignoreMenuItem;
	  private JMenuItem repeatPushItem;
	  
	  private String cellType;
	  
	  BudgetPopup(BudgetWindow mainWindow){
		 this.main = mainWindow;
		 this.data = mainWindow.getData();
		 this.popupCreate();
		 this.row = -1;
		 this.col = -1;
		 cellType = "";
		 bi       = null;		 
	  }
	
	  public void showMenu(Component invoker, int x, int y){
		  /*
		  if(row < 0){
			  repeatMenuItem.setEnabled(false);
		  } else {
			  repeatMenuItem.setEnabled(true);
		  }
		  */
		  show(invoker,x, y);
	  }
	  
	  protected void setRowCol(BudgetTable table, int row, int col){
		  this.row = row;
		  this.col = col;
		  
		  setRepeatLabelText();
		  setRepeatAccess(); 
		  selectRepeat();
		  setEnabledOptions(table);
	  }
	  
	  protected int getRow(){
		  return this.row;
	  }
	  
	  protected int getCol(){
		  return this.col;
	  }
	  
	  private JTable getCurrentTable(){
		  JTable table = null;
          int i = main.getSelectedBudgetTab();
          if(i==0) table = main.getIncomeTable();
          if(i==1) table = main.getMoneyTable();
          if(i==2) table = main.getExpenseTable();
          
          return table;
	  }
	  
	  private void setEnabledOptions(BudgetTable table){
		  if(table == null){
			  editDatamenuItem.setEnabled(false);
			  repeatMenuItem.setEnabled(false);
			  addMenuItem.setEnabled(false);
			  ignoreMenuItem.setEnabled(false);
			  return;
		  }
		  
		  boolean enableOpts = false;
		  if(this.col < 13 && this.col > 0) {
			  if(table.isCellEditable(this.row, this.col)) {
				  enableOpts = true;
			  }
		  }
		  if( this.col == 0 ) {
			  if(table.isCellEditable(this.row, this.col + 1) ) {
				  enableOpts = true;
			  }
		  }
			  
		  if(enableOpts){
			  editDatamenuItem.setEnabled(true);
			  //repeatMenuItem.setEnabled(true);
			  addMenuItem.setEnabled(true);
			  ignoreMenuItem.setEnabled(true);
		  } else {
			  editDatamenuItem.setEnabled(false);
			  repeatMenuItem.setEnabled(false);
			  addMenuItem.setEnabled(false);
			  ignoreMenuItem.setEnabled(false);
		  }
	  }
	  
	  private void setRepeatAccess(){
		  JTable table = getCurrentTable();
          if(table != null){
        	  BudgetData data = main.getData();
    		  String acctName = getAccountName();
    		  
    		  cellType = "single";
    		  if(col < 0 || row < 0){
    			  repeatMenuItem.setEnabled(false);
    			  return;
    		  }
    		  
    		  if(col < 13) {
    			  if(data.cellTypeData[col] != null){
        			  if(data.cellTypeData[col].get(acctName) != null){
        				  cellType = ((String) data.cellTypeData[col].get(acctName)).toString();
        			  }
        		  }
    		  }
    		  
    		  if(! cellType.equalsIgnoreCase("repeat")){
    			  repeatMenuItem.setEnabled(true);
    		  } else {
    			  repeatMenuItem.setEnabled(false);
    		  }
          }
	  }
	  
	  private String getAccountName() {
		  String acctName;
		  
		  JTable table = getCurrentTable();
		  if(row > -1){
			  acctName = (String) table.getModel().getValueAt(row, 0);
		  } else {
			  acctName = "";
		  }
		  return acctName;
	  }
	  
	  private void selectRepeat(){
		  JTable table = getCurrentTable();
		  if(table != null){
			  if(repeatMenuItem.isEnabled()){
				  BudgetData data = main.getData();
				  String acctName = getAccountName();
				  bi = data.getBudgetItem(acctName, col);
				  
				  if(bi == null){
					return;  
				  }
				  
				  if(bi.getInterval() == BudgetItem.INTERVAL_ANNUALLY){
					  repeatAnnualItem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_BI_MONTHLY){
					  repeatBiMonthlyItem.setSelected(true);			  
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_BI_WEEKLY){
					  repeatBiWeeklyItem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_DAILY){
					  repeatDailyItem.setSelected(true);
			  	  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_MONTHLY){
					  repeatMonthlyItem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_SEMI_ANNUALLY){
					  repeatSemiAnnualtem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_SEMI_MONTHLY){
					  repeatSemiMonthlyItem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_TRI_MONTHLY){
					  repeatTriMonthlyItem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_TRI_WEEKLY){
					  repeatTriWeeklyItem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_WEEKLY){
					  repeatWeeklyItem.setSelected(true);
				  }
				  if(bi.getInterval() == BudgetItem.INTERVAL_NO_REPEAT){
					  repeatNone.setSelected(true); 
				  }

			  } else {
				  repeatNone.setSelected(true);
			  }
		  } else {
			  repeatNone.setSelected(true);
		  }

	  }
	  
	  private void setRepeatLabelText(){
		  String acctName = getAccountName();
		  repeatMenuItem.setText("Interval (" + acctName + ")");
	  }
	  
	  private void shiftStartDate(BudgetItem bi) {
		  String startDate = String.valueOf(bi.getIntervalStartDate());
		  String start_month  = startDate.substring(4, 6);
		  String start_day    = startDate.substring(6, 8);
		  
		  int month = new Integer(start_month);
		  if(month < 12){
			  month++;
			  
			  String monthNum = String.valueOf(month);
	          if(month < 10) monthNum = "0" + monthNum;
	          
	          bi.setIntervalStartDate(Integer.parseInt(data.getCurrentBudgetYear() + monthNum + start_day));
	          
	          main.displayBudget();
		  }
	  }
	  
	  protected void setEndDate(int month){
		  if(bi == null) return;
		  setEndDate(bi, month);
	  }
	  
	  private void setEndDate(BudgetItem bi, int month) {
		  BudgetData data = main.getData();

    	  String monthNum = String.valueOf(month);
          if(month < 10) monthNum = "0" + monthNum;

    	  bi.setIntervalEndDate(Integer.parseInt(data.getCurrentBudgetYear() + 
    			                                 monthNum + 
    			                                 String.valueOf(BudgetDateUtil.getMonthEndDay(data.getCurrentBudgetYear(), month))));
    	  main.displayBudget();
	  }
	  
	  private void popupCreate(){
		  JMenuItem expenseReportmenuItem  = new JMenuItem("Expense Report");
		  JMenuItem forecastReportmenuItem = new JMenuItem("Forecast");
		  JMenuItem refreshDatamenuItem    = new JMenuItem("Refresh");
		  editDatamenuItem                 = new JMenuItem("Edit");
		  repeatPushItem                   = new JMenuItem("Shift Start");
		  
		  repeatMenuItem = new JMenu("Repeat");
		  
		  repeatNone            = new JRadioButtonMenuItem("None");
		  repeatDailyItem       = new JRadioButtonMenuItem("Daily");
		  repeatWeeklyItem      = new JRadioButtonMenuItem("Weekly");
		  repeatBiWeeklyItem    = new JRadioButtonMenuItem("Bi-Weekly");
		  repeatTriWeeklyItem   = new JRadioButtonMenuItem("Tri-Weekly");
		  repeatMonthlyItem     = new JRadioButtonMenuItem("Monthly");
		  repeatBiMonthlyItem   = new JRadioButtonMenuItem("Bi-Monthly");
		  repeatSemiMonthlyItem = new JRadioButtonMenuItem("Semi-Monthly");
		  repeatTriMonthlyItem  = new JRadioButtonMenuItem("Tri-Monthly");
		  repeatSemiAnnualtem   = new JRadioButtonMenuItem("Semi-Annual");
		  repeatAnnualItem      = new JRadioButtonMenuItem("Annual");
		   
		  repeatMenuItem.add(repeatNone);
		  repeatMenuItem.add(repeatDailyItem);
		  repeatMenuItem.add(repeatWeeklyItem);
		  repeatMenuItem.add(repeatBiWeeklyItem);
		  repeatMenuItem.add(repeatTriWeeklyItem);
		  repeatMenuItem.add(repeatMonthlyItem);
		  repeatMenuItem.add(repeatBiMonthlyItem);
		  repeatMenuItem.add(repeatSemiMonthlyItem);
		  repeatMenuItem.add(repeatTriMonthlyItem);
		  repeatMenuItem.add(repeatSemiAnnualtem);
		  repeatMenuItem.add(repeatAnnualItem);
		  repeatMenuItem.add(new JSeparator());
		  repeatMenuItem.add(repeatPushItem);
		  
		  ButtonGroup rg = new ButtonGroup();
		  rg.add(repeatNone);
		  rg.add(repeatDailyItem);
		  rg.add(repeatWeeklyItem);
		  rg.add(repeatBiWeeklyItem);
		  rg.add(repeatTriWeeklyItem);
		  rg.add(repeatMonthlyItem);
		  rg.add(repeatBiMonthlyItem);
		  rg.add(repeatSemiMonthlyItem);
		  rg.add(repeatTriMonthlyItem);
		  rg.add(repeatSemiAnnualtem);
		  rg.add(repeatAnnualItem);
		    
		  repeatMenuItem.setEnabled(false);
		  
		  addMenuItem = new JMenuItem("Add Category");
		  ignoreMenuItem = new JMenuItem("Ignore Category");
		  
		  this.add(expenseReportmenuItem);
		  this.add(forecastReportmenuItem);
		  this.add(new JSeparator()); 
		  this.add(refreshDatamenuItem);
		  this.add(editDatamenuItem);
		  this.add(new JSeparator()); 
		  this.add(repeatMenuItem);
		  this.add(addMenuItem);
		  this.add(ignoreMenuItem);
		  
		  
		  repeatNone.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_NO_REPEAT);
	        	  setEndDate(col);
	          }
	      });
		  repeatDailyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_DAILY);
	        	  main.displayBudget();
	          }
	      });
		  repeatWeeklyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_WEEKLY);
	        	  main.displayBudget();
	          }
	      });
		  repeatBiWeeklyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_BI_WEEKLY);
	        	  main.displayBudget();
	          }
	      });
		  repeatTriWeeklyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_TRI_WEEKLY);
	        	  setEndDate(12);
	          }
	      });
		  repeatMonthlyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_MONTHLY);
	        	  setEndDate(12);
	          }
	      });
		  repeatBiMonthlyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_BI_MONTHLY);
	        	  setEndDate(12);
	          }
	      });
		  repeatSemiMonthlyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_SEMI_MONTHLY);
	        	  setEndDate(12);
	          }
	      });
		  repeatTriMonthlyItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_TRI_MONTHLY);
	        	  setEndDate(12);
	          }
	      });
		  repeatSemiAnnualtem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_SEMI_ANNUALLY);
	        	  setEndDate(12);
	          }
	      });
		  repeatAnnualItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  bi.setInterval(BudgetItem.INTERVAL_ANNUALLY);
	        	  setEndDate(bi, 12);
	          }
	      });
		  
		  repeatPushItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  shiftStartDate(bi);
	          }
	      });
		  
		  expenseReportmenuItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  main.getMain().showReport();
	          }
	      });
		  
		  forecastReportmenuItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  main.getMain().showForecast();
	          }
	      });
		  
		  refreshDatamenuItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  main.refresh();
	          }
	      });
		  
		  editDatamenuItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {

	        	  JTable table = getCurrentTable();
	              if(table != null){
	            	  ((BudgetTable)table).showEditBalloon();
	              }
	          }
	      });
		  
		  addMenuItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  
	          	String[] accountNames = data.getAccounts(main.getRoot());

	          	String s = (String)JOptionPane.showInputDialog(
	          	                    null,
	          	                    "Select category to add to budget",
	          	                    "Customized Dialog",
	          	                    JOptionPane.PLAIN_MESSAGE,
	          	                    null,
	          	                    accountNames,
	          	                    "");

	          	//If a string was returned, say so.
	          	if ((s != null) && (s.length() > 0)) {
	          		Account a = data.getAccount(main.getRoot(), s);
	          		if(a.getComment().indexOf("IGNORE") > -1){
	          		    //TODO: Make this non destructive
	          			a.setComment("");
	          		} else {
	          			data.budgetAddZeroItem(s, 1);
	          		}
	          		
	          		main.displayBudget();
	          	    return;
	          	}
	          	
	          }
	      });
		  
		  ignoreMenuItem.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	
	        	JTable table = getCurrentTable();
	          	if(table != null){
	          		int row = table.getSelectedRow();
	          		if(row < table.getRowCount() - 1){
	          			String acctName = getAccountName();
	                  	
	                  	Account a = data.getAccount(main.getRoot(), acctName);
	                  	
	                  	//TODO: Make this non destructive
	                  	a.setComment("IGNORE");
	                  	main.displayBudget();
	          		}
	          	}
	          	
	          }
	      });
		  
	  }
}
