/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.*;
import com.moneydance.awt.graph.*;
import com.infinitekind.util.*;

import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Cursor;
import java.awt.Color;
import java.awt.BasicStroke;
import java.awt.Frame;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

import javax.swing.JPanel;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JTable;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JScrollPane;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableModel;

import java.util.*;
import java.util.GregorianCalendar;
import java.sql.Timestamp;
import java.text.NumberFormat;
import java.text.SimpleDateFormat;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYItemRenderer;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.chart.labels.XYToolTipGenerator;
import org.jfree.chart.axis.AxisLocation;
import org.jfree.chart.axis.NumberAxis;

public class BudgetForecast extends JDialog implements ActionListener, Runnable {
  private static final long serialVersionUID = 7904680121905462798L;
 
  private Main                extension;
  private BudgetData          data;
  
  private JPanel              mp, bigP, smaP, bp, bpl, bpr;
  private JScrollPane         tp;
  private JButton             btRefresh;
  private JComboBox <String>  cbFutuIntervals   = new JComboBox<String>();
  private JComboBox <String>  cbFutuNum         = new JComboBox<String>();
  private BudgetForecastConf  predConf          = null;
  private Date                prDate            = new Date();
  private GridBagLayout       gbl               = new GridBagLayout();
  
  @SuppressWarnings({"rawtypes" })
  private Hashtable           remindersStatus   = new Hashtable();
  private SimpleDateFormat    dateFormat        = new SimpleDateFormat("MM/dd/yy");
  private JTable              table;
  
  @SuppressWarnings("rawtypes")
  private Map[]               spendingData      = new Map[13];
  private Object[][]	      tabData;
  private static NumberFormat nf;
  private static String[]     cols              = {"","Date","Description","Amount","Balance"};
  
  
  public BudgetForecast(Main ext, BudgetForecastConf predConf) {
    super( (Frame) null, "");
    this.predConf = predConf;
    this.data = ext.getBudgetData();
    this.extension = ext;

    nf = NumberFormat.getNumberInstance();
    nf.setGroupingUsed(true);
    nf.setMinimumFractionDigits(2);
    nf.setMaximumFractionDigits(2);
	run();
  }


 @SuppressWarnings("unchecked")
public void run() {
    setTitle(predConf.extensionName);
    Vector<?> v = getTxnRemindersVect();
    for(int i=0;i<v.size();i++) {
      remindersStatus.put(v.elementAt(i), new Boolean(true));
    }
    Calendar tmp = Calendar.getInstance();
    tmp.set(Calendar.HOUR_OF_DAY, 12);
    tmp.set(Calendar.AM_PM, Calendar.AM);
    tmp.set(Calendar.MINUTE, 0);
    tmp.set(Calendar.SECOND, 0);
    tmp.set(Calendar.MILLISECOND, 0);
    tmp.add(Calendar.MONTH, BudgetForecastConf.DEF_NUM);

    predConf.cbAccounts.setSelectedIndex(0);

    btRefresh = new JButton("Refresh");
    btRefresh.addActionListener(this);
    btRefresh.setVisible(true);

    cbFutuIntervals.addItem("days");
    cbFutuIntervals.addItem("weeks");
    cbFutuIntervals.addItem("months");
    cbFutuIntervals.addItem("years");
    cbFutuIntervals.setSelectedIndex(2);
    for (int i=1;i<=BudgetForecastConf.INTERVALS;i++) cbFutuNum.addItem(String.valueOf(i));
    cbFutuNum.setSelectedIndex(0);

    predConf.cbAccounts.addActionListener(this);
    cbFutuIntervals.addActionListener(this);
    cbFutuNum.addActionListener(this);


    //Left side options
    bpl = new JPanel(gbl);
    bpl.setBorder(new EmptyBorder(0,0,5,5));
    bpl.add(btRefresh, AwtUtil.getConstraints(0,0,0,0,1,1,true,false));
    bpl.add(predConf.cbAccounts, AwtUtil.getConstraints(1,0,1,0,1,1,true,false));
    
    //Right side options
    bpr = new JPanel(gbl);
    bpr.setBorder(new EmptyBorder(0,5,5,0));
    bpr.add(new JLabel("Period: ", JLabel.RIGHT), AwtUtil.getConstraints(0,0,1,0,1,1,true,false));
    bpr.add(cbFutuNum,       AwtUtil.getConstraints(1,0,0,0,1,1,true,false));
    bpr.add(cbFutuIntervals, AwtUtil.getConstraints(2,0,1,0,1,1,true,false));
    
    //Options Pane
    bp = new JPanel(new GridLayout(1,2));
    bp.setBorder(new EmptyBorder(0,95,0,180));
    bp.add(bpl);
	bp.add(bpr);

	//Graph Pane
    bigP = new JPanel(gbl);
    bigP.setBorder(new EmptyBorder(0,0,0,25));
    
    smaP = new JPanel(gbl);
    smaP.setBorder(new EmptyBorder(0,20,0,0));
    
    //Setup Table for Transaction List
    tabData = new Object[1][5];
  	  table = new JTable(tabData,cols);
    tp = new JScrollPane(table);
    tp.setBackground(new Color(237, 237, 237));
    tp.setBorder(new EmptyBorder(0,95,0,180));
    
    //Overall Layout of panes
    mp = new JPanel(gbl);
    mp.setBorder(new EmptyBorder(0,10,10,10));
    
    
    /* For my own reference, I always forget the arguments to getConstraints
     * getConstraints(int x, int y, 
     *   float weightx, 
     *   float weighty, 
     *   int width, 
     *   int height, 
     *   boolean fillx, 
     *   boolean filly) 
     */

    getContentPane().add(mp);

    pack();
    this.setSize(1000, 1000);
    this.setResizable(false);
    
    AwtUtil.centerWindow(this);
  }

  private long getAccountBalance(Account account) {
    long realBalance = account.getCurrentBalance();

    for(int i=0; i<account.getSubAccountCount(); i++) {
      realBalance += getAccountBalance(account.getSubAccount(i));
    }
    return realBalance;
  }

  public void setWaitCursor() {
    try {
      setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
    } catch (Exception e) {}
  }

  public void setDefaultCursor() {
    try {
      setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
    } catch (Exception e) {}
  }

  public static String format( long cents )
  {
    if (cents == 0) return ("--");
    return nf.format((float)cents/100.0);
  }

  private void addRow(String type, 
		              long date, 
		              String description, 
		              long amount, 
		              long balance, ArrayList<BudgetForecastRow> rowList) {
    
	BudgetForecastRow row = new BudgetForecastRow();
    row.type = type;

    Calendar cal = Calendar.getInstance();
    cal.setTimeInMillis(date);

    if (date == 0) {
      row.date = new String("");
    } else {
      row.date = new Long(date).toString();
    }

    row.description = description;
    row.amount      = new Long(amount).toString();

    //Scan rowList for collision between transaction types
    boolean foundDuplicate = false;
    for(int i = 0; i < rowList.size(); i++){
      BudgetForecastRow data = (BudgetForecastRow) rowList.get(i);
  
  	  String txnType = data.type;
  	  long   txnDate = new Long(data.date).longValue();
  	  String txnDesc = data.description;
  	  long   txnAmnt = new Long(data.amount).longValue();

  	  Calendar txnCal = Calendar.getInstance();
  	  txnCal.setTime(new Date(txnDate));

  	  if(! txnType.equalsIgnoreCase(type)
  	     && txnDesc.equalsIgnoreCase(description)
  		 && cal.get(Calendar.MONTH) == txnCal.get(Calendar.MONTH)
  		 && cal.get(Calendar.YEAR) == txnCal.get(Calendar.YEAR)){

  		data.type = row.type+txnType;
  		data.date = row.date;
  		
  		long dataAmount = 0;
  		if(txnAmnt > 0){
  			if(txnAmnt > amount){
  				dataAmount = txnAmnt;
  			} else {
  				dataAmount = amount;
  			}
  		} else {
  			if(txnAmnt < amount){
  				dataAmount = txnAmnt;
  			} else {
  				dataAmount = amount;
  			}
  		}
  		
  		data.amount = (new Long(dataAmount)).toString();
  		
  		rowList.set(i, data);
  		foundDuplicate = true;
  	  }
    }

    if(! foundDuplicate){
    	rowList.add(row);
    }
  }

  private long findBudgetTxns(Calendar curr, long startBal, Account acct, ArrayList<BudgetForecastRow> rowList) {
	  long    balance = startBal;
	  
	  @SuppressWarnings("unchecked")
	  Map<String, BudgetValue>[] budgetData = new Map[13];
	  
	  for(int i = 0; i <= 12; i++){
		  budgetData[i]  = new HashMap<String, BudgetValue>();
	  }
	  
	  Calendar today = Calendar.getInstance();
      today.setTime(curr.getTime());

	  if(data.getRoot() == null) return balance;

	  List<Budget> budgetList = data.getBudgetList().getAllBudgets();
	  Budget b = null;
	  for (int i = 0; i < budgetList.size(); i++) {
		  b = budgetList.get(i);
          if (b.getName().equals( data.getCurrentBudgetName() )){
        	  for (int j = 0; j < b.getItemList().getItemCount(); j++) {
	        	  BudgetItem bi = b.getItemList().getItem(j);
		          Account a = bi.getTransferAccount();

		          if(bi.getIntervalStartDate() > 0){
		        	  for(int month = 1; month <= 12; month++){
		        		  if(today.get(Calendar.MONTH) + 1 > month) continue;
		        		  
		        		  Date budgetDay = new GregorianCalendar(data.getCurrentBudgetYear(), month-1, 2).getTime();
			              Calendar start = Calendar.getInstance();
			        	  start.setTime(budgetDay);
			        	  Calendar stop = Calendar.getInstance();
			      	      stop.setTime(prDate);

			      	      if (stop.before(start)) break;
			      	      
			        	  Date startDay   = new GregorianCalendar(data.getCurrentBudgetYear(), month-1, 1).getTime();
			        	  Date endDay     = new GregorianCalendar(data.getCurrentBudgetYear(), month-1, getMonthEndDay(month, data.getCurrentBudgetYear())).getTime();

			        	  String  budgetCategory = a.getFullAccountName();
			        	  BudgetValue budgetedAmount = new BudgetValue(data, 0);
			        	  
			        	  if(acct.getComment().indexOf("MAIN") > -1) {
			        		  budgetedAmount = getBudgetedAmount(bi,startDay,endDay).negateValue();
			        	  } else {
			        		  if(acct.getAccountName().equalsIgnoreCase(budgetCategory)) {
				        		  budgetedAmount = getBudgetedAmount(bi,startDay,endDay);
				        	  }
			        	  }
			        	  
			              if (budgetedAmount.isEqual(0)) continue;
			              //this.println("DEBUG (BUDGET): " + startDay + " - " + endDay + " --> " + month + " : " + budgetCategory + " -- " + budgetedAmount);

			      	      budgetData[month].put(budgetCategory,budgetedAmount);

		        	  }

		          }
		      }

          }
	  }
	  
	  for(int month = 1; month <= 12; month++){
		  Date budgetDay   = new GregorianCalendar(data.getCurrentBudgetYear(), month-1, 2).getTime();
		  Iterator<?> it = budgetData[month].entrySet().iterator();
		  while (it.hasNext()) {
		        @SuppressWarnings("rawtypes")
				Map.Entry pairs = (Map.Entry)it.next();
		        
		        String budgetCategory = pairs.getKey().toString();
		        long budgetedAmount = ((BudgetValue) budgetData[month].get(budgetCategory)).longValue(); 
		        it.remove(); 
		        
		        balance += budgetedAmount;

		        String type = "B";
		        if(spendingData[month].get(budgetCategory) != null) {
		        	  long spentAmount = 0;

		        	  if(acct.getComment().indexOf("MAIN") > -1) {
		        		  spentAmount = ((BudgetValue) spendingData[month].get(budgetCategory)).longValue();
		        	  } else {
		        		  spentAmount = -((BudgetValue) spendingData[month].get(budgetCategory)).longValue();
		        	  }
		        	  budgetedAmount += spentAmount;
		        	  balance += spentAmount;
		        	  type = "BT";
		        }
		          
		        addRow(type, BudgetDateUtil.getLngDateTime(budgetDay), budgetCategory, budgetedAmount, balance, rowList);
		  }
	  }
	  

	  return balance;
  }

  private long findFutureTxns(long startBal, Account acct, ArrayList<BudgetForecastRow> rowList) {
    AbstractTxn   txn;
    long          balance = startBal;
    int           i;

    TxnSet txns = data.getTxnSet(acct);
    if(txns == null){
    	return balance;
    }
    
    JDateField todayField = new JDateField(new CustomDateFormat("MM/dd/yyyy"));
    todayField.gotoToday();
    int today = todayField.getDateInt();
    
    for (i=0; i<txns.getSize(); i++) {
      txn = txns.getTxn(i);
      if (txn.getDateInt() > today){
    	  
        //TODO: Limit by prDate
        balance += txn.getValue();

        addRow("F", data.getTxnDate(txn).getTime(), 
        		    txn.getDescription(), txn.getValue(), balance, rowList);
      }
    }
    return balance;
  }

  private void createChart(){
	  calcPrDate();
	  
	  mp.removeAll();
	  bigP.removeAll();
	  smaP.removeAll();
	  
	  setWaitCursor();
	  
	  fetchSpendingData();
	  
	  final XYSeriesCollection datasetSmall = new XYSeriesCollection();
	  final XYSeriesCollection datasetBig   = new XYSeriesCollection();
	  
	  
	  //Split series between two charts
	  //for(int i = 0; i < predConf.getNumAccounts(); i++){
		  XYSeries dataSeries = calcPredictedRBalance(predConf.getAccount());
		  
		  BudgetPreferences prefs = extension.getPreferences();
		  String largeThreshold   = prefs.getDefaults("large");
		  if(largeThreshold == "") {
			  largeThreshold = "10000";
		  }
		  Double lValue = new Double(largeThreshold);
		  
		  if (dataSeries.getMaxY() > lValue.doubleValue()) {
			  datasetBig.addSeries(dataSeries);

		  } else {
			  datasetSmall.addSeries(dataSeries);
		  }
	  //}
	  
	  //Build charts
	  JFreeChart chartSmall = buildChart(datasetSmall, true);
	  JFreeChart chartBig = buildChart(datasetBig, false);
	  chartBig.setTitle("Large Account Balances");
	  
	  //Add charts to panel
	  bigP.add(new ChartPanel(chartBig),   AwtUtil.getConstraints(0,0,1,1,1,1,true,true));
	  smaP.add(new ChartPanel(chartSmall), AwtUtil.getConstraints(0,0,1,1,1,1,true,true));
	    
	  if(datasetBig.getSeriesCount() > 0){
		  if(datasetSmall.getSeriesCount() > 0){
			  mp.add(bigP, AwtUtil.getConstraints(0,0,1,0.2f,1,1,true,true));
			  mp.add(smaP, AwtUtil.getConstraints(0,1,1,0.6f,1,1,true,true));
			  mp.add(bp,   AwtUtil.getConstraints(0,2,1,0.0f,1,1,true,true));
			  mp.add(tp,   AwtUtil.getConstraints(0,3,1,0.2f,1,1,true,true));
		  } else {
			  mp.add(bigP, AwtUtil.getConstraints(0,0,1,0.8f,1,1,true,true));
			  mp.add(bp, AwtUtil.getConstraints(0,1,1,0.0f,1,1,true,true));
			  mp.add(tp, AwtUtil.getConstraints(0,2,1,0.2f,1,1,true,true));
		  }
	  } else {
		  if(datasetSmall.getSeriesCount() > 0){
			  mp.add(smaP, AwtUtil.getConstraints(0,0,1,0.8f,1,1,true,true));
			  mp.add(bp, AwtUtil.getConstraints(0,1,1,0.0f,1,1,true,true));
			  mp.add(tp, AwtUtil.getConstraints(0,2,1,0.2f,1,1,true,true));
		  } else {
			  mp.add(bp, AwtUtil.getConstraints(0,0,1,0.0f,1,1,true,true));
			  mp.add(tp, AwtUtil.getConstraints(0,1,1,0.2f,1,1,true,true));
		  }
	  }
	  
	  setDefaultCursor();
  }

private JFreeChart buildChart(XYSeriesCollection dataset, boolean showZero){
  final JFreeChart chart = ChartFactory.createXYStepChart(
			"Account Balances", "", "Balance", dataset, PlotOrientation.VERTICAL,
			true, true, false);
  chart.setBackgroundPaint(new Color(237, 237, 237));
  chart.removeLegend();

  final XYPlot plot = chart.getXYPlot();
  
  plot.setRangeAxisLocation(AxisLocation.BOTTOM_OR_LEFT);
  ((NumberAxis)plot.getRangeAxis()).setAutoRangeIncludesZero(false);
  ((NumberAxis)plot.getRangeAxis()).setAutoRange(true);
  
  plot.setBackgroundPaint(new Color(250, 250, 250));
  plot.setDomainGridlinePaint(Color.gray);
  plot.setDomainGridlinesVisible(true);
  plot.setRangeGridlinePaint(Color.gray);
  
  plot.setRangeZeroBaselineVisible(showZero);
  plot.setRangeZeroBaselinePaint(Color.black);
  plot.setRangeZeroBaselineStroke(new BasicStroke(2.0f));
  
  
  //Setup line renderers
  XYItemRenderer renderer;
  for(int i = 0; i < dataset.getSeriesCount(); i++){
	  renderer = plot.getRenderer();
	  renderer.setSeriesStroke(i, new BasicStroke(3.0f));
	  renderer.setSeriesToolTipGenerator(i, new XYToolTipGenerator () {
	      public String generateToolTip(XYDataset data, int series, int index) {
	        return dateFormat.format(
	        		data.getX(series,index).doubleValue()) + " " +
					format((long)(data.getY(series,index).doubleValue()*100.0));
	      }
		});
  }
  
  return chart;
}
private XYSeries calcPredictedRBalance(Account cacct) {

    ArrayList<BudgetForecastRow> rowList = new ArrayList<BudgetForecastRow>();
    ArrayList<BudgetForecastRow> txnList = new ArrayList<BudgetForecastRow>();

    long changes  = 0;
    long startingBalance = getAccountBalance(cacct); 
    long currentBalance  = startingBalance;
    
    Calendar curr = Calendar.getInstance();
	    curr.set(Calendar.HOUR_OF_DAY, 12);
	    curr.set(Calendar.AM_PM, Calendar.AM);
	    curr.set(Calendar.MINUTE, 0);
	    curr.set(Calendar.SECOND, 0);
	    curr.set(Calendar.MILLISECOND, 0);

    Calendar today = Calendar.getInstance();
    today.setTime(curr.getTime());

    addRow("S",BudgetDateUtil.getLngDateTime(Calendar.getInstance().getTime()),"Starting Balance",0,currentBalance, rowList);

    findFutureTxns(currentBalance, cacct, txnList);
    findBudgetTxns(curr, currentBalance, cacct, txnList);

    final XYSeries series = new XYSeries(cacct.getAccountName(), false, true);
    series.add(BudgetDateUtil.getLngDateTime(curr.getTime()), currentBalance/100.0);

    curr.setTime(today.getTime());

    Calendar stop = Calendar.getInstance();
	    stop.setTime(prDate);
	    stop.set(Calendar.HOUR_OF_DAY, 12);
	    stop.set(Calendar.AM_PM, Calendar.AM);
	    stop.set(Calendar.MINUTE, 0);
	    stop.set(Calendar.SECOND, 0);
	    stop.set(Calendar.MILLISECOND, 0);
    if (stop.before(curr)) return null;

    ParentTxn ptxn = null;
    SplitTxn  stxn = null;

    //Find all Reminders
    //Calendar nextDay;

    while (curr.before(stop) || curr.equals(stop)) {

        long currentTime = BudgetDateUtil.getLngDateTime(curr.getTime());
        Calendar nextDay = Calendar.getInstance();
        nextDay.setTime(curr.getTime());
        nextDay.add(Calendar.DAY_OF_MONTH, 1);

        List<Reminder> rl = predConf.rs.getRemindersOnDay(nextDay);
        for (Reminder r : rl) {
            //if ( (r.getReminderType() == Reminder.Type.typeForCode(Reminder.TXN_REMINDER_TYPE)) ) {
            //if ( ((Boolean)remindersStatus.get(r)).booleanValue() ) {

            if (r.getReminderType() == Reminder.Type.TRANSACTION) {
                ptxn = r.getTransaction();

                if (ptxn.getAccount().equals(cacct)) {
                    changes += ptxn.getValue();
                    addRow("R", currentTime, r.getDescription(), ptxn.getValue(), currentBalance + changes, txnList);
                }

                for (int i = 0; i < ptxn.getSplitCount(); i++) {
                    stxn = ptxn.getSplit(i);
                    if (stxn.getAccount().equals(cacct)) {
                        long val = CurrencyTable.convertValue(stxn.getAmount(),
                                stxn.getParentTxn().getAccount().getCurrencyType(),
                                cacct.getCurrencyType(),
                                ptxn.getDateInt());
                        changes += val;
                        addRow("R", currentTime, r.getDescription(), val, currentBalance + changes, txnList);
                    }
                }
                //}
                //}
            }
        }

        curr.add(Calendar.DAY_OF_MONTH, 1);
    }

    //Loop through all found transactions and chart by date
    curr.setTime(today.getTime());
    changes = 0;
    while(curr.before(stop) || curr.equals(stop)) {
        long currentTime = BudgetDateUtil.getLngDateTime(curr.getTime());

        Calendar nextDay = Calendar.getInstance();
        nextDay.setTime(curr.getTime());
        nextDay.add(Calendar.DAY_OF_MONTH, 1);

        //Loop through array and add all found transactions
        for(int i = 0; i < txnList.size(); i++){
          
          BudgetForecastRow data = (BudgetForecastRow) txnList.get(i);

      	  long txnDate = new Long((String) data.date).longValue();
      	  
      	  if(txnDate >= curr.getTime().getTime() && txnDate < nextDay.getTime().getTime()){
      	  	long txnAmt = new Long((String) data.amount).longValue();
      	  	String txnType = data.type;

      	  	if (! txnType.equalsIgnoreCase("B") &&
      	  		! txnType.equalsIgnoreCase("BT")){
      	  	    changes += txnAmt;
      	  		addRow(txnType, txnDate, data.description, txnAmt, currentBalance + changes, rowList);
      	  	}

      	  }
        }

        series.add(currentTime, (currentBalance + changes)/100.0);
        curr.add(Calendar.DAY_OF_MONTH, 1);
    }


    if(cacct.getAccountName().equalsIgnoreCase(predConf.getAccount().getAccountName())){
    	fillTable(startingBalance, rowList);
    }
    
    return series;
  }

  private void fillTable(long balance, ArrayList<BudgetForecastRow> rowList){

	    Collections.sort(rowList);
	    
	    tabData = new Object[rowList.size()][5];

	    for (int i=0; i<rowList.size(); i++) {
	    	BudgetForecastRow row = (BudgetForecastRow) rowList.get(i);
	    	long txnDate  = new Long((String) row.date).longValue();
		    long txnAmt   = new Long((String) row.amount).longValue();
		    balance = balance + txnAmt;
		    
	    	Object[] data = new Object[5];
	    	data[0] = row.type;
	    	data[1] = dateFormat.format(txnDate);
	    	data[2] = row.description;
	    	data[3] = format(txnAmt);
	    	data[4] = format(balance);

	        tabData[i] = data;
	    }

	    table.setModel(new DefaultTableModel(tabData,cols));


	    for (int i=0; i<5; i++) {
	      table.getColumnModel().getColumn(i).setCellRenderer(new BudgetDetailCellRenderer());
	    }
	    table.setAutoResizeMode(JTable.AUTO_RESIZE_ALL_COLUMNS);
	    table.getColumnModel().getColumn(0).setPreferredWidth(8);
	    table.getColumnModel().getColumn(1).setPreferredWidth(55);
	    table.getColumnModel().getColumn(2).setPreferredWidth(150);

	    table.repaint();
  }

    private Vector<?> getTxnRemindersVect() {
        Vector<Reminder> res = new Vector<Reminder>();
        List<Reminder> rs = predConf.rs.getAllReminders();

        for (Reminder r : rs) {
            if (r.getReminderType() == Reminder.Type.TRANSACTION) {
                res.add(r);
            }
        }
        return res;
    }

  public void actionPerformed(ActionEvent e) {
    this.refresh();
  }
  
  public void refresh(){
	  createChart();
	  validate();
	  repaint();
  }

  private void calcPrDate() {
    Calendar tmp = Calendar.getInstance();
    tmp.set(Calendar.HOUR_OF_DAY, 12);
    tmp.set(Calendar.AM_PM, Calendar.AM);
    tmp.set(Calendar.MINUTE, 0);
    tmp.set(Calendar.SECOND, 0);
    tmp.set(Calendar.MILLISECOND, 0);
    int num = cbFutuNum.getSelectedIndex()+1;
    switch(cbFutuIntervals.getSelectedIndex()) {
      case 0:
        tmp.add(Calendar.DAY_OF_MONTH, num);
        break;
      case 1:
        tmp.add(Calendar.WEEK_OF_MONTH, num);
        break;
      case 2:
    	  tmp.set(Calendar.DAY_OF_MONTH, 1 );
          tmp.add(Calendar.MONTH, num );
        break;
      case 3:
        tmp.add(Calendar.YEAR, num);
        break;
    }

    prDate.setTime(tmp.getTime().getTime());
  }

  class CurrencyLabeler implements ValueLabeler {
    private CurrencyType curr;

    CurrencyLabeler(CurrencyType ct) {
      this.curr = ct;
    }

    public String getLabelForValue(double value, int type) {
      return curr.format(Math.round(value), '.');
    }
  }

	private int getMonthEndDay(int month, int budgetYear){
		  int endDay = 31;
	      switch (month) {
		      case 1: endDay = 31; break;
		      case 2: endDay = 28; break;
		      case 3: endDay = 31; break;
		      case 4: endDay = 30; break;
		      case 5: endDay = 31; break;
		      case 6: endDay = 30; break;
		      case 7: endDay = 31; break;
		      case 8: endDay = 31; break;
		      case 9: endDay = 30; break;
		      case 10: endDay = 31; break;
		      case 11: endDay = 30; break;
		      case 12: endDay = 31; break;
		      default: endDay = 31;
		  }

	      if( (budgetYear % 4) == 0 && month == 2 ) endDay = 29;

	      return endDay;
	  }

	private BudgetValue getBudgetedAmount(BudgetItem bi, Date startDay, Date endDay) {
	      Date budStartDate = BudgetDateUtil.getDateYYYYMMDD(bi.getIntervalStartDate());
	      Date budEndDate = BudgetDateUtil.getDateYYYYMMDD(bi.getIntervalEndDate());
	      Date budDt = budStartDate;

	      // Is it after end day?
	      if (budStartDate == null || budStartDate.after(endDay)) return new BudgetValue(data, 0);
	      // Is it before start day
	      if (budEndDate != null && budEndDate.before(startDay)) return new BudgetValue(data, 0);

	      long amount = 0;
	      boolean done = false;
	      while (!done) {
	              // Is budget in range
	              if (BudgetDateUtil.isInRange(budDt, startDay, endDay)) {
	                      amount += bi.getAmount();
	              }
	              // Get next budgeted date
	              switch (bi.getInterval()) {
	                      case BudgetItem.INTERVAL_ANNUALLY: budDt = BudgetDateUtil.addYears(budDt, 1); break;
	                      case BudgetItem.INTERVAL_BI_MONTHLY: budDt = BudgetDateUtil.addMonths(budDt, 2); break;
	                      case BudgetItem.INTERVAL_BI_WEEKLY: budDt = BudgetDateUtil.addWeeks(budDt,2); break;
	                      case BudgetItem.INTERVAL_DAILY:budDt = BudgetDateUtil.addDays(budDt,1);break;
	                      case BudgetItem.INTERVAL_MONTHLY:budDt = BudgetDateUtil.addMonths(budDt,1);break;
	                      case BudgetItem.INTERVAL_SEMI_ANNUALLY: {
	                              if (BudgetDateUtil.isSameDayOfYear(budDt,budStartDate)) {
	                                      budDt = BudgetDateUtil.addDays(budDt,182);
	                              } else {
	                                      budDt = BudgetDateUtil.addDays(budDt,-182);
	                                      budDt =BudgetDateUtil.addYears(budDt, 1);
	                              }
	                              break;
	                      }
	                      case BudgetItem.INTERVAL_SEMI_MONTHLY: {
	                              if (BudgetDateUtil.isSameDayOfMonth(budDt,budStartDate)) {
	                                      budDt = BudgetDateUtil.addDays(budDt,15);
	                              } else {
	                                      budDt = BudgetDateUtil.addDays(budDt,-15);
	                                      budDt =BudgetDateUtil.addMonths(budDt, 1);
	                              }
	                              break;
	                      }
	                      case BudgetItem.INTERVAL_TRI_MONTHLY: budDt = BudgetDateUtil.addMonths(budDt, 3); break;
	                      case BudgetItem.INTERVAL_TRI_WEEKLY: budDt = BudgetDateUtil.addWeeks(budDt,3); break;
	                      case BudgetItem.INTERVAL_WEEKLY: budDt = BudgetDateUtil.addWeeks(budDt,1); break;
	                      default: done = true;
	              }

	              // Is it past date
	              if (budDt.after(endDay) || budDt.after(budEndDate)) {
	                      break;
	              }
	      }

	      return new BudgetValue(data, amount);
	}

	@SuppressWarnings("unchecked")
	private void fetchSpendingData(){
		  for(int i = 0; i <= 12; i++){
			  spendingData[i]  = new HashMap<String, BudgetValue>();
		  }

		  if(data.getRoot().getBook().getTransactionSet() != null) {
			  TxnSet ts = data.getRoot().getBook().getTransactionSet().getAllTxns();
			  for (int i = 0; i < ts.getSize(); i++) {
		          AbstractTxn t = ts.getTxn(i);
		          Account txnAccount    = t.getAccount();
		          
		          AbstractTxn ot = t.getOtherTxn(0);
		          if(ot != null){
		        	  Account othAccount    = ot.getAccount();

			          if(txnAccount.getComment().indexOf("IGNORE") > -1) continue;
			          if(othAccount.getComment().indexOf("IGNORE") > -1 && othAccount.getAccountType() == Account.AccountType.EXPENSE) continue;

			          String dt = (new Integer(t.getDateInt())).toString();
			          GregorianCalendar gc = new GregorianCalendar();
			          gc.set(Calendar.YEAR, new Integer(dt.substring(0,4)).intValue() );
			          gc.set(Calendar.MONTH, new Integer(dt.substring(4,6)).intValue() - 1 );
			          gc.set(Calendar.DAY_OF_MONTH, new Integer(dt.substring(6,8)).intValue() );
			          gc.set(Calendar.HOUR_OF_DAY,0);
			          gc.set(Calendar.MINUTE,0);
			          gc.set(Calendar.SECOND,0);
			          gc.set(Calendar.MILLISECOND,0);

			          if (BudgetDateUtil.isInRange(gc.getTime(),new GregorianCalendar(data.getCurrentBudgetYear(), 0, 1).getTime()
			        		                   ,new GregorianCalendar(data.getCurrentBudgetYear(), 11, 31).getTime())) {

			        	  Account topLvlAccount = txnAccount.getParentAccount();
				          while(topLvlAccount.getParentAccount() != null){
				        	  if(topLvlAccount.getParentAccount().getFullAccountName().length() > 0){
				        		  topLvlAccount = topLvlAccount.getParentAccount();
				        	  } else {
				        		  break;
				        	  }
				          }

			        	  addTransaction(spendingData[gc.get(Calendar.MONTH)+1], t, gc.get(Calendar.MONTH)+1);
			          }
		          }
		          
			  }
			  
		  }
		  
	  }

	private void addTransaction(Map<String, BudgetValue> txnMap, AbstractTxn t, int month) {
	      if (t == null) return;

	      Account   a         = t.getAccount();
	      BudgetValue amount  = new BudgetValue(data, t.getValue());
	      BudgetValue sAmount = new BudgetValue(data, 0);

	      String  accName = a.getFullAccountName();

	      if (txnMap.get(accName) != null){
	    	  sAmount.setValue(txnMap.get(accName));
	      }
	      sAmount.add(amount);

	      txnMap.put(accName, sAmount);
	}
	
	void println(String message){
		  java.util.Date date= new java.util.Date();
		  System.err.println(new Timestamp(date.getTime()) + " : " + message);
	}
}

