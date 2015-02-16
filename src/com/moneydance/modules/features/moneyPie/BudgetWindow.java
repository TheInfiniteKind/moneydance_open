/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/

package com.moneydance.modules.features.moneyPie;

import com.moneydance.awt.AwtUtil;
import com.infinitekind.moneydance.model.*;

import java.util.List;
import java.awt.EventQueue;
import java.awt.GridBagLayout;
import java.awt.AWTEvent;
import java.awt.event.WindowEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.Component;

import javax.swing.event.ChangeEvent;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.TableColumnModelEvent;
import javax.swing.event.TableColumnModelListener;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import javax.swing.event.TableModelListener;
import javax.swing.event.TableModelEvent;
import javax.swing.table.TableModel;
import javax.swing.JTable;
import javax.swing.JFrame;
import javax.swing.JTabbedPane;
import javax.swing.JPanel;
import javax.swing.Box;
import javax.swing.JScrollPane;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableModel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JRadioButtonMenuItem;
import javax.swing.ButtonGroup;
import javax.swing.JSeparator;
import javax.swing.JOptionPane;

import java.awt.event.MouseListener;
import java.util.Calendar;
import java.util.Comparator;
import java.util.Map;
import java.util.LinkedList;
import java.util.LinkedHashMap;
import java.util.Iterator;
import java.util.Collections;
import java.sql.Timestamp;

/** Window used for Account List interface
  ------------------------------------------------------------------------
*/

//@SuppressWarnings("unchecked")
public class BudgetWindow extends JFrame implements ActionListener, TableModelListener, TableColumnModelListener {
  private Main                extension;
  private BudgetData          data;
  
  private static final long   serialVersionUID  = 1L;
  private static final int    WINDOW_WIDTH      = 1360;
  private static final int    WINDOW_HEIGHT     = 700;

  public  static final int    INCOME_ACCOUNTS   = 0;
  public  static final int    EXPENSE_ACCOUNTS  = 1;
  public  static final int    DIFF_ACCOUNTS     = 2; // Income - Expense
  
  private String              defaultBudget;
  private boolean             taxIsIncome;
  private TableColumnModel    summaryColModel;
  private DefaultTableModel   incomeModel;
  private DefaultTableModel   moneyModel;
  private DefaultTableModel   expenseModel;
  private DefaultTableModel   summaryModel;

  private JPanel              mainPanel;
  private JTabbedPane         tableTabs;
  private BudgetTable         incomeTable;
  private BudgetTable         moneyTable;
  private BudgetTable         expenseTable;
  private BudgetTable         summaryTable;

  private BudgetPopup popupMenu;
  private JMenu       viewMenu;
  private JMenu       helpMenu;
  private JMenu       pieMenu;
  private ButtonGroup budgetGroup;
  private JMenuItem   aboutAction;
  private JMenuItem   prefAction;
  private JMenuItem   editBudgetAction;
  private JMenuItem   copyBudgetAction;
  private JMenuItem   renameBudgetAction;
  private JMenuItem   removeBudgetAction;
  private JMenuItem   newBudgetAction;
  private JMenuItem   repairAction;
  private JMenuItem   roundAction;
  private JMenuItem   showForecastAction;
  private JMenuItem   showReportAction;
  private JMenuItem   refreshAction;

  private String[] columnNames = {"Category",
						          "Jan",
						          "Feb",
						          "Mar",
						          "Apr",
						          "May",
						          "Jun",
						          "Jul",
						          "Aug",
						          "Sep",
						          "Oct",
						          "Nov",
						          "Dec",
						          "Total"};


  public BudgetWindow(Main extension) {
    super(extension.getName() + " Console");
    this.extension = extension;
    this.data      = extension.getBudgetData();
    this.updatePrefs();
    
    popupMenu = new BudgetPopup(this);
    
    summaryModel = new DefaultTableModel();
    summaryTable = tableCreate(summaryModel, popupMenu);

    incomeModel = new DefaultTableModel();
    incomeModel.addTableModelListener(this);
    incomeTable = tableCreate(incomeModel, popupMenu);

    expenseModel = new DefaultTableModel();
    expenseModel.addTableModelListener(this);
    expenseTable = tableCreate(expenseModel, popupMenu);

    moneyModel = new DefaultTableModel();
    moneyModel.addTableModelListener(this);
    moneyTable = tableCreate(moneyModel, popupMenu);

    summaryColModel = summaryTable.getColumnModel();
    incomeTable.setColumnModel(summaryColModel);
    expenseTable.setColumnModel(summaryColModel);
    moneyTable.setColumnModel(summaryColModel);
    summaryColModel.addColumnModelListener(this);

    JMenuBar menuBar = new JMenuBar();
    pieMenu = new JMenu("MoneyPie");
    viewMenu = new JMenu("View");
    helpMenu = new JMenu("Help");
    
    menuBar.add(pieMenu);
    menuBar.add(viewMenu);
    menuBar.add(helpMenu);
    
    prefAction         = new JMenuItem("Preferences");
    aboutAction        = new JMenuItem("About");
    editBudgetAction   = new JMenuItem("Open Budget List");
    newBudgetAction    = new JMenuItem("New");
    copyBudgetAction   = new JMenuItem("Copy");
    renameBudgetAction = new JMenuItem("Rename");
    removeBudgetAction = new JMenuItem("Delete");
    repairAction       = new JMenuItem("Repair");
    roundAction        = new JMenuItem("Round Budget Values");
    refreshAction      = new JMenuItem("Refresh Data");
    showForecastAction = new JMenuItem("Forecast");
    showReportAction   = new JMenuItem("Expense Report");

    pieMenu.add(aboutAction);
    pieMenu.add(new JSeparator()); 
    pieMenu.add(prefAction);
    pieMenu.add(new JSeparator()); 
    pieMenu.add(editBudgetAction);
    pieMenu.add(new JSeparator()); 
    pieMenu.add(newBudgetAction);
    pieMenu.add(copyBudgetAction);
    pieMenu.add(removeBudgetAction);
    pieMenu.add(renameBudgetAction);
    pieMenu.add(new JSeparator()); 
    pieMenu.add(repairAction);
    //pieMenu.add(roundAction);
    
    viewMenu.add(showReportAction);
    viewMenu.add(showForecastAction);
    viewMenu.add(new JSeparator()); 
    viewMenu.add(refreshAction);
    viewMenu.add(new JSeparator()); 
    
    prefAction.addActionListener(this);
    aboutAction.addActionListener(this);
    editBudgetAction.addActionListener(this);
    newBudgetAction.addActionListener(this);
    copyBudgetAction.addActionListener(this);
    renameBudgetAction.addActionListener(this);
    removeBudgetAction.addActionListener(this);
    repairAction.addActionListener(this);
    roundAction.addActionListener(this);
    showForecastAction.addActionListener(this);
    refreshAction.addActionListener(this);
    showReportAction.addActionListener(this);
    
    setJMenuBar(menuBar);
    
    mainPanel = new JPanel(new GridBagLayout());
    mainPanel.setBorder(new EmptyBorder(10,10,10,10));

    List<Budget> budgetList = data.getBudgetList().getAllBudgets();
    
    budgetGroup = new ButtonGroup();
	Budget b = null;

    boolean defaultFound = false;
	for (int i = 0; i < budgetList.size(); i++) {
		  b = budgetList.get(i);
		  if(data.getYearOfBudget(b.getName()) > 0){
			  this.addBudget(b.getName());
			  if(b.getName().equalsIgnoreCase(defaultBudget)){
				  defaultFound = true;
			  }
		  }
	}
	
	if(defaultFound){
		for (int i = 0; i < viewMenu.getMenuComponentCount(); i++) {
			 Component vComponent = viewMenu.getMenuComponent(i);
			 if (vComponent instanceof JMenuItem){
				 JMenuItem vItem = (JMenuItem) vComponent;
				 if(vItem.getText().equalsIgnoreCase(defaultBudget)){
					 setCurrentBudget(defaultBudget, 0);
					 vItem.setSelected(true);
					 break;
				 }
			 }
		 }
	}
	
	
	/* For my own reference, I always forget the arguments to getConstraints
     * getConstraints(int x, int y, 
     *   float weightx, 
     *   float weighty, 
     *   int width, 
     *   int height, 
     *   boolean fillx, 
     *   boolean filly) 
     */

    tableTabs = new JTabbedPane();

    tableTabs.addTab( "Income",   null, new JScrollPane( incomeTable ) );
    tableTabs.addTab( "Accounts", null, new JScrollPane( moneyTable ) );
    tableTabs.addTab( "Expense",  null, new JScrollPane( expenseTable ) );

    mainPanel.add(new JScrollPane(summaryTable), AwtUtil.getConstraints(0,0,1,0.1f,1,1,true,true));
    mainPanel.add(Box.createVerticalStrut(8),    AwtUtil.getConstraints(0,1,0,0,1,1,false,false));
    mainPanel.add(new JScrollPane(tableTabs),    AwtUtil.getConstraints(0,2,1,0.9f,1,1,true,true));
	
    getContentPane().add(mainPanel);

    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);

    displayBudget();

    //new PrintStream(new ConsoleStream());

    setSize(WINDOW_WIDTH, WINDOW_HEIGHT);
    AwtUtil.centerWindow(this);

  }
  
  protected Main getMain(){
	 return extension;
  }
  
  protected boolean isTaxIncome(){
	  return taxIsIncome;
  }
  
  protected void refresh(){
	data.refresh();
	this.updatePrefs();
	tablePaint();
  }
  
  private void updatePrefs(){
		BudgetPreferences prefs = extension.getPreferences();
	    defaultBudget    = prefs.getDefaults("budget");

	    if(prefs.getDefaults("taxIsIncome").indexOf("y") > -1){
	    	taxIsIncome = true;
	    } else {
	    	taxIsIncome = false;
	    }
  }
  
  protected Account getRoot(){
		return data.getRoot();  
  }
  
  protected BudgetTable getIncomeTable(){
	  return incomeTable;
  }
  
  protected BudgetTable getExpenseTable(){
	  return expenseTable;
  }
  
  protected BudgetTable getMoneyTable(){
	  return moneyTable;
  }
  
  protected int getSelectedBudgetTab(){
	  return tableTabs.getSelectedIndex();
  }
  
  protected BudgetData getData(){
	  return data;
  }
  
  private void setCurrentBudget(String bName, int bYear){
	  data.setCurrentBudget(bName, bYear);
	  this.setTitle(extension.getName()+" : " + data.getCurrentBudgetName() 
			                   + " (" + data.getCurrentBudgetYear() + ") " );
  }
  
  private void addBudget(String bName){
	  JMenuItem budgetItem = new JRadioButtonMenuItem(bName);
	  budgetGroup.add(budgetItem);
	  viewMenu.add(budgetItem);
	  
	  int bYear = data.getYearOfBudget(bName);
	  if( bYear == data.getCurrentBudgetYear() ){
		  budgetItem.setSelected(true);
		  setCurrentBudget(bName, bYear);
	  }
	  
	  budgetItem.addActionListener(new ActionListener() {
          public void actionPerformed(ActionEvent evt) {
          	JMenuItem src = (JMenuItem) evt.getSource();
          	String bName = src.getText();
          	
          	int bYear = data.getYearOfBudget(bName);
  			if(bYear > 0){
  				setCurrentBudget(bName, bYear);
  				displayBudget();
  			}
          }
      });  
  }
  
  private void removeBudget(String bName){
	 //Remove the budget
	 for (int i = 0; i < viewMenu.getMenuComponentCount(); i++) {
		 Component vComponent = viewMenu.getMenuComponent(i);
		 if (vComponent instanceof JMenuItem){
			 JMenuItem vItem = (JMenuItem) vComponent;
			 if(vItem.getText().equalsIgnoreCase(bName)){
				 viewMenu.remove(vItem);
				 budgetGroup.remove(vItem);
				 break;
			 }
		 }
		 
	 }
  }
  
  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    
    if(src==aboutAction){
    	Runnable runner = new Runnable()
		{
			public void run()
			{
				BudgetSplash window = new BudgetSplash(extension.getName(), extension.getBuild());
				window.setVisible( true );
			}
		};
		EventQueue.invokeLater( runner );
    }
    
    
    if(src==prefAction){
    	BudgetPreferencesWindow win = new BudgetPreferencesWindow(this.extension);
        win.setVisible(true);
    }
    
    if(src==editBudgetAction){
    	extension.getUnprotectedContext().showURL("moneydance:showbudgets");
    }
    
    if(src==newBudgetAction){

    	String s = (String)JOptionPane.showInputDialog(
    	                    null,
    	                    "Name for new budget",
    	                    "Budget",
    	                    JOptionPane.PLAIN_MESSAGE);

    	if ((s != null) && (s.length() > 0)) {
    		BudgetList budgetList = data.getBudgetList();
        	Budget b = new Budget(data.getRoot().getBook());
    		b.setName(s);
    		budgetList.addBudget(b);
        	this.addBudget(b.getName());
        	
        	setCurrentBudget(b.getName(), Calendar.getInstance().get(Calendar.YEAR));
      	    displayBudget();
    	}
    }
    
    if(src==copyBudgetAction){
    	String s = (String)JOptionPane.showInputDialog(
                null,
                "Name for new budget",
                "Budget",
                JOptionPane.PLAIN_MESSAGE);
    	
    	if ((s != null) && (s.length() > 0)) {
    		List<Budget> budgetList = data.getBudgetList().getAllBudgets();
      	    Budget b = null;
      	    for (int i = 0; i < budgetList.size(); i++) {
      		  b = budgetList.get(i);
              if (b.getName().equals( data.getCurrentBudgetName() )){
            	  
            	  Budget cBudget = b.duplicateAsNew("New");
            	  cBudget.setName(s);
            	  data.getBudgetList().addBudget(cBudget);
            	  
            	  this.addBudget(cBudget.getName());
            	  
            	  setCurrentBudget(cBudget.getName(), data.getCurrentBudgetYear() );
            	  displayBudget();
            	  
            	  break;
              }
      	    }
    	}
    	
    }
    
    if(src==removeBudgetAction){
    	List<Budget> budgetList = data.getBudgetList().getAllBudgets();
  	    Budget b = null;
  	    for (int i = 0; i < budgetList.size(); i++) {
  		  b = budgetList.get(i);
          if (b.getName().equals( data.getCurrentBudgetName() )){
        	  this.removeBudget(b.getName());
        	  data.getBudgetList().removeBudget(b);
        	  break;
          }
  	    }
  	    
  	    budgetList = data.getBudgetList().getAllBudgets();
  	    if(budgetList.size() > 0){
  	    	b = budgetList.get(0);
  	    	setCurrentBudget(b.getName(), 0);
  	    }
  	    
  	    for (int i = 0; i < viewMenu.getMenuComponentCount(); i++) {
			 Component vComponent = viewMenu.getMenuComponent(i);
			 if (vComponent instanceof JMenuItem){
				 JMenuItem vItem = (JMenuItem) vComponent;
				 String bName = vItem.getText();
				 
				 if(bName.equalsIgnoreCase(data.getCurrentBudgetName()) ){
					 vItem.setSelected(true);
					 displayBudget();
					 break;
				 }
			 }
		 }
    }
    
    if(src==renameBudgetAction){
    	List<Budget> budgetList = data.getBudgetList().getAllBudgets();
  	    Budget b = null;
  	    for (int i = 0; i < budgetList.size(); i++) {
  		  b = budgetList.get(i);
          if (b.getName().equals( data.getCurrentBudgetName() )){
        	  String s = (String)JOptionPane.showInputDialog(
                      null,
                      "New name for budget: " + b.getName(),
                      "Budget",
                      JOptionPane.PLAIN_MESSAGE);
        	  if ((s != null) && (s.length() > 0)) {
        		  this.removeBudget(b.getName());
            	  b.setName(s);
            	  this.addBudget(b.getName());

            	  setCurrentBudget(b.getName(), data.getCurrentBudgetYear() );
            	  displayBudget();
        	  }
        	  
        	  break;
          }
  	    }
    }
    
    if(src==showReportAction){
    	this.extension.showReport();
    }

    if(src==refreshAction){
    	this.refresh();
    }

    if(src==repairAction){
    	//TODO user input
    	String s = (String)JOptionPane.showInputDialog(
                null,
                "Convert budget values to what year?",
                "Budget Year",
                JOptionPane.PLAIN_MESSAGE);
    	
    	if ((s != null) && (s.length() > 0)) {
    		data.repairDates( s );
    	}    	
    	this.refresh();
    }
    
    if(src==roundAction){
    	data.roundValues();
    	this.refresh();
    }

    if(src==showForecastAction){
    	this.extension.showForecast();
    }

  }

  protected void displayBudget(){
	  this.refresh();
  	  setEditAllowed(true);
  }

  private void setEditAllowed(boolean isEditable){
	  summaryTable.setEditable(false);
  	  incomeTable.setEditable(isEditable);
  	  moneyTable.setEditable(isEditable);
  	  expenseTable.setEditable(isEditable);
  }

  private BudgetTable tableCreate(DefaultTableModel tableModel, BudgetPopup popupMenu){
	  for (int col = 0; col < columnNames.length; col++) {
		  tableModel.addColumn(columnNames[col]);
      }

	  BudgetTable table = new BudgetTable(this, tableModel, data);
	  table.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_INTERVAL_SELECTION);
	  TableColumn column = null;
	  for (int i = 0; i < columnNames.length; i++) {
	      column = table.getColumnModel().getColumn(i);

	      if (i == 0) {
	          column.setPreferredWidth(215);
	      } else {
	    	  if(i == 13) {
	    		  column.setPreferredWidth(100);
	    	  } else {
	    		  column.setPreferredWidth(83);
	    	  }
	      }
	  }

	  if(popupMenu !=  null){
		  MouseListener popupListener = new BudgetPopupListener(popupMenu);
		  table.addMouseListener(popupListener);
		  table.getTableHeader().addMouseListener(popupListener);
	  }

	  table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
	  table.getTableHeader().setReorderingAllowed(false);

	  return table;
  }

  public void tableChanged(TableModelEvent e) {
      int row = e.getFirstRow();
      int column = e.getColumn();
      TableModel model = (TableModel)e.getSource();

      if(row > -1 && column > -1) {
        BudgetValue dValue = (BudgetValue) model.getValueAt(row, column);
        String categoryName = (String) model.getValueAt(row, 0);
        Account ba = data.getAccount(data.getRoot(), categoryName);
        String  accName = ba.getFullAccountName();

        if(! data.isBudgetNull(accName, column)){
        	BudgetValue cValue = data.getBudgetValue(accName, column);

	        if(! dValue.isNoEntry() ){
		        if(cValue.isEqual(dValue)){
		        	//this.println("No Change: " + columnName + "," + categoryName +":" + amount +"->"+data +"\n");
		        } else {
		        	if(! data.budgetUpdateItem(categoryName, column, dValue)){
			        	data.budgetAddItem(categoryName, column, dValue);
			        }
		        	
		        	displayBudget();
		        }
	        } else {
	        	data.budgetDelteItem(categoryName, column);
	        	displayBudget();
	        }

        } else {
        	if(! dValue.isNoEntry() ){
        		data.budgetAddItem(categoryName, column, dValue);
        	} else {
        		data.budgetDelteItem(categoryName, column);
        	}
        	displayBudget();
        }

      }

  }

  public void columnAdded(TableColumnModelEvent e) {
      
  }

  public void columnMarginChanged(ChangeEvent e) {

  }

  public void columnMoved(TableColumnModelEvent e) {
      
  }

  public void columnRemoved(TableColumnModelEvent e) {
      
  }

  public void columnSelectionChanged(ListSelectionEvent e) {
      
  }
    
  private void tableClear(DefaultTableModel tableModel){

	  while(tableModel.getRowCount() > 0) {
		  tableModel.removeRow(0);
      }
  }


  protected void tablePaint(){
	  if(data.getRoot() != null) {

		  for (int i = 0; i < columnNames.length; i++) {
			  summaryTable.getColumnModel().getColumn(i).setCellRenderer(null);
			  summaryTable.getColumnModel().getColumn(i).setCellEditor(null);	  
		  }
		  
		  tableClear(incomeModel);
		  tableClear(moneyModel);
		  tableClear(expenseModel);
		  tableClear(summaryModel);
  
		  data.initSummaryData();

		  addAccountToTable(data.getIncomeAccounts(),  incomeModel);
		  addAccountToTable(data.getMoneyAccounts(),   moneyModel);
		  addAccountToTable(data.getExpenseAccounts(), expenseModel);
		  
		  summaryModel.addRow( new Object[] {"Total",
				  	data.getSummaryValue("Total", 1),
				  	data.getSummaryValue("Total", 2),
				  	data.getSummaryValue("Total", 3),
				  	data.getSummaryValue("Total", 4),
				  	data.getSummaryValue("Total", 5),
				  	data.getSummaryValue("Total", 6),
				  	data.getSummaryValue("Total", 7),
				  	data.getSummaryValue("Total", 8),
				  	data.getSummaryValue("Total", 9),
				  	data.getSummaryValue("Total", 10),
				  	data.getSummaryValue("Total", 11),
				  	data.getSummaryValue("Total", 12),
				  	data.getSummaryValue("Total", 0)
	           });
		  
		  //This assumes the budget name is 2013 or 2014, etc...
		  if(data.getCurrentBudgetName() == null){
			  repairAction.setEnabled(false);
		  } else {
			  int budgetYear = Integer.parseInt(data.getCurrentBudgetName());
			  if( budgetYear == data.getCurrentBudgetYear() ) {
				  repairAction.setEnabled(false);
			  } else {
				  repairAction.setEnabled(true); 
			  }
		  }
		  
		  for (int i = 0; i < columnNames.length; i++) {
			  BudgetCellRenderer renderer = new BudgetCellRenderer(data);
			  summaryTable.getColumnModel().getColumn(i).setCellRenderer(renderer);
			  
			  BudgetCellEditor editor = new BudgetCellEditor(data);
			  summaryTable.getColumnModel().getColumn(i).setCellEditor(editor);
		  }

		  incomeTable.initBalloon();
		  expenseTable.initBalloon();
		  moneyTable.initBalloon();
		  
		  
		  //BIG FUCKING HACK
		  //for some unknown reason, balloons will not display after
		  //refreshing the table. But by some magic, selecting another
		  //tab and reselecting the the original tab and it all works as
		  //it should?? I've tried forcing everything under the sun to repaint
		  //with no success, giving up for now 
		  int index = tableTabs.getSelectedIndex();
		  if(index == tableTabs.getTabCount() - 1) {
			  tableTabs.setSelectedIndex(0);
		  } else {
			  tableTabs.setSelectedIndex(index + 1);
		  }
		  tableTabs.setSelectedIndex(index);
	  }
  }

  public void addAccountToTable(Map<Integer, String> accounts, DefaultTableModel dataModel) {
	    if(accounts.size() < 1) return;

	    //outputArea.append("Start addAccountToTable("+dataMap+")\n");

	    BudgetValue[] total = new BudgetValue[13];

	    String summaryName = "";
	    if(accounts == data.getIncomeAccounts())  summaryName = "Income";
	    if(accounts == data.getExpenseAccounts()) summaryName = "Expense";
	    if(accounts == data.getMoneyAccounts())   summaryName = "Accounts";

	    Iterator<?> k = sortByValue(accounts).keySet().iterator();
	    while (k.hasNext()) {
	      Integer acctNum = (Integer) k.next();
	      String acctName = (String) accounts.get(acctNum);

	      boolean showNegative = false;
	      if(accounts == data.getIncomeAccounts() && taxIsIncome &&
	         (acctName.indexOf("Taxes:") > -1 || acctName.indexOf("Tax:") > -1 ) ) {
	      	  showNegative = true;
	      }

	      for(int i = 0; i <= 12; i++){
	          if(total[i] == null) total[i] = new BudgetValue(data, 0);
	          
	          if(! data.isBudgetNull(acctName, i)) {
	        	  BudgetValue v = data.getBudgetValue(acctName, i);
	        	  if(showNegative){
	        		  total[i].minus(v);
	        	  } else {
	        		  total[i].add(v);
	        	  }
	          }
	      }
		          
		  dataModel.addRow( new Object[] {acctName,
				  							data.getBudgetValue(acctName, 1).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 2).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 3).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 4).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 5).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 6).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 7).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 8).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 9).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 10).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 11).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 12).sign(showNegative).toString(),
				  							data.getBudgetValue(acctName, 0).sign(showNegative).toString()
				                             });
	    }

	    dataModel.addRow( new Object[] {"Total",
	    			 ((BudgetValue) total[1]).toString(),
	    			 ((BudgetValue) total[2]).toString(),
	    			 ((BudgetValue) total[3]).toString(),
	    			 ((BudgetValue) total[4]).toString(),
	    			 ((BudgetValue) total[5]).toString(),
	    			 ((BudgetValue) total[6]).toString(),
	    			 ((BudgetValue) total[7]).toString(),
	    			 ((BudgetValue) total[8]).toString(),
	    			 ((BudgetValue) total[9]).toString(),
	    			 ((BudgetValue) total[10]).toString(),
	    			 ((BudgetValue) total[11]).toString(),
	    			 ((BudgetValue) total[12]).toString(),
	    			 ((BudgetValue) total[0]).toString()
                });



	    if(summaryName.length()> 0){
		    summaryModel.addRow( new Object[] {summaryName,
		    		 ((BudgetValue) total[1]).toString(),
	    			 ((BudgetValue) total[2]).toString(),
	    			 ((BudgetValue) total[3]).toString(),
	    			 ((BudgetValue) total[4]).toString(),
	    			 ((BudgetValue) total[5]).toString(),
	    			 ((BudgetValue) total[6]).toString(),
	    			 ((BudgetValue) total[7]).toString(),
	    			 ((BudgetValue) total[8]).toString(),
	    			 ((BudgetValue) total[9]).toString(),
	    			 ((BudgetValue) total[10]).toString(),
	    			 ((BudgetValue) total[11]).toString(),
	    			 ((BudgetValue) total[12]).toString(),
	    			 ((BudgetValue) total[0]).toString()
	           });


		     for(int i=0; i<=12; i++){
		    	  
			      BudgetValue amount = data.getSummaryValue("Total", i);
			      if(amount == null) amount = new BudgetValue(data, 0);
			      
			      BudgetValue totalAmount = new BudgetValue(data, amount);
			      
			      if(accounts == data.getIncomeAccounts()){
			    	  totalAmount.add(total[i]);
			  	  } else {
			  		  totalAmount.minus(total[i]);
			  	  }
			      data.saveSummaryData("Total", i, totalAmount);
			 }

	     }
	    
	     //outputArea.append("END addAccountToTable()\n");
  }

  @SuppressWarnings({ "rawtypes", "unchecked" })
  private static Map<Object,Object> sortByValue(Map<?,?> map) {
	  List<?> list = new LinkedList(map.entrySet());
	  
	  Collections.sort(list, new Comparator() {
		  public int compare(Object o1, Object o2) {
			  return ((Comparable) ((Map.Entry) (o1)).getValue()).compareTo(((Map.Entry) (o2)).getValue());
		  }
	  });

	  // logger.info(list);
	  Map<Object, Object> result = new LinkedHashMap<Object, Object>();
	  for (Iterator<?> it = list.iterator(); it.hasNext();) {
		  Map.Entry<Object, Object> entry = (Map.Entry)it.next();
		  result.put(entry.getKey(), entry.getValue());
	  }
	  return result;
  }

  public final void processEvent(AWTEvent evt) {
    if(evt.getID()==WindowEvent.WINDOW_CLOSING) {
      extension.closeConsole();
      return;
    }
    if(evt.getID()==WindowEvent.WINDOW_OPENED) {
    }
    super.processEvent(evt);
  }

  /*
  private class ConsoleStream extends OutputStream implements Runnable{
    public void write(int b) throws IOException {
        repaint();
    }

    public void write(byte[] b) throws IOException {
        repaint();
    }
    
    public void run() {

    }
    
  }
  */
  
  void goAway() {
    setVisible(false);
    dispose();
  }
  
  void println(String message){
	  java.util.Date date= new java.util.Date();
	  System.err.println(new Timestamp(date.getTime()) + " : " + message);
  }
}
