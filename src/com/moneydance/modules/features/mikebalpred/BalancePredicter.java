/************************************************************\
 * Portions Copyright (C) 2008 Reilly Technologies, L.L.C.   *
\************************************************************/

package com.moneydance.modules.features.mikebalpred;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.*;
import com.moneydance.awt.graph.*;
import com.infinitekind.util.*;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.border.*;
import javax.swing.table.*;
import java.util.*;
import java.text.*;

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

//@SuppressWarnings("unchecked")
public class BalancePredicter extends JDialog
  implements ActionListener, /*MouseMotionListener,*/ Runnable
{
  private static final long serialVersionUID = 7904680121905462798L;
  private JPanel mp, gp, bp, bpl, bpr;
  private JButton btReminders, btDone, btDone1;
  private JComboBox cbFutuIntervals   = new JComboBox();
  private JComboBox cbFutuNum         = new JComboBox();
  private JDialog manageDlg           = null;
  private JLabel lbFutu;
  private BalPredConf balpredConf     = null;
  private Date prDate                 = new Date();
  private GridBagLayout gbl           = new GridBagLayout();
  private Hashtable remindersStatus   = new Hashtable();
  private SimpleDateFormat dateFormat = new SimpleDateFormat("MM/dd/yy");
  private JTextArea text              = new JTextArea();
  private JTable table;

  private Object[][]	tabData;
  private static NumberFormat nf;
  private static String[] cols        = {"","Date","Description","Amount","Balance"};
  private boolean DEBUG               = false;

  public BalancePredicter(BalPredConf balpredConf) {
    super((Frame)null, "Mike's Balance Predictor");
    this.balpredConf = balpredConf;

    nf = NumberFormat.getNumberInstance();
    nf.setGroupingUsed(true);
    nf.setMinimumFractionDigits(2);
    nf.setMaximumFractionDigits(2);
	run();
  }

  private void dd(String msg) {
    if (!DEBUG) return;
    text.append(msg+"\n");
  }


public void run() {
    setTitle(balpredConf.extensionName);
    Vector v = getTxnRemindersVect();
    for(int i=0;i<v.size();i++) {
      remindersStatus.put(v.elementAt(i), new Boolean(true));
    }
    mp = new JPanel(gbl);
    mp.setBorder(new EmptyBorder(0,0,10,0));
    gp = new JPanel(gbl);
    gp.setBorder(new CompoundBorder(new EmptyBorder(10,10,10,10), new BevelBorder(BevelBorder.LOWERED)));
    bp = new JPanel(new GridLayout(1,2));
    bpl = new JPanel(gbl);
    bpl.setBorder(new EmptyBorder(0,0,5,5));
    bpr = new JPanel(gbl);
    bpr.setBorder(new EmptyBorder(0,5,5,0));
    bp.setBorder(new EmptyBorder(0,10,10,10));

    cbFutuIntervals.addItem("days");
    cbFutuIntervals.addItem("weeks");
    cbFutuIntervals.addItem("months");
    cbFutuIntervals.addItem("years");
    cbFutuIntervals.setSelectedIndex(3);
    for (int i=1;i<=BalPredConf.INTERVALS;i++) cbFutuNum.addItem(String.valueOf(i));
    cbFutuNum.setSelectedIndex(0);

    btReminders = new JButton("Manage Reminders");
    btReminders.addActionListener(this);
    btReminders.setVisible(true);
    btDone = new JButton("Done");
    btDone.addActionListener(this);

    lbFutu = new JLabel("Future period ", JLabel.RIGHT);

    balpredConf.cbAccounts.addActionListener(this);
    cbFutuIntervals.addActionListener(this);
    cbFutuNum.addActionListener(this);

    int yy = 0;
    bpl.add(new JLabel("Account: "+"   ", JLabel.RIGHT), AwtUtil.getConstraints(0,yy,0,0,1,1,true,false));
    bpl.add(balpredConf.cbAccounts, AwtUtil.getConstraints(1,yy++,1,0,1,1,true,false));

    yy = 0;
    bpr.add(lbFutu, AwtUtil.getConstraints(0,yy,1,0,1,1,true, false));
    bpr.add(cbFutuNum, AwtUtil.getConstraints(1,yy,0,0,1,1,true,false));
    bpr.add(cbFutuIntervals, AwtUtil.getConstraints(2,yy++,1,0,1,1,true,false));
    bpr.add(btReminders, AwtUtil.getConstraints(0,yy++,1,0,3,1,false,false));
    bpr.add(new JLabel(" "), AwtUtil.getConstraints(0,yy,1,1,3,1,true,true));

    Calendar tmp = Calendar.getInstance();
    tmp.set(Calendar.HOUR_OF_DAY, 12);
    tmp.set(Calendar.AM_PM, Calendar.AM);
    tmp.set(Calendar.MINUTE, 0);
    tmp.set(Calendar.SECOND, 0);
    tmp.set(Calendar.MILLISECOND, 0);
    tmp.add(Calendar.MONTH, BalPredConf.DEF_NUM);

    text.setEditable(false);

    tabData = new Object[1][5];
		table = new JTable(tabData,cols);

    JScrollPane tablePane = new JScrollPane(table);
    tablePane.setBorder(new CompoundBorder(new EmptyBorder(10,0,10,10), new BevelBorder(BevelBorder.LOWERED)));


    bp.add(bpl);
	bp.add(bpr);           	// xy, weight, wh, fill
    mp.add(gp, AwtUtil.getConstraints(0,0,1,1,2,1,true,true));
    mp.add(bp, AwtUtil.getConstraints(0,1,1,0,2,1,true,true));
    if (DEBUG)    mp.add(new JScrollPane(text),  AwtUtil.getConstraints(2,1,5,0,1,3,true,true));
		          mp.add(tablePane, AwtUtil.getConstraints(2,0,5,1,1,1,true,true));
                  mp.add(btDone, AwtUtil.getConstraints(1,2,1,0,1,1,false,false));
    getContentPane().add(mp);
    pack();
    setSize(1200, 800);
    AwtUtil.centerWindow(this);
    setVisible(true);

    calcPredictedRBalance();
    validate();
  }

  private long getAccountBalance(Account account) {
    long realBalance = account.getCurrentBalance();
	//  long realBalance = account.getBalance();

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

  private void addRow(String type, long date, String description, long amount, long balance, ArrayList rowList) {
    Object[] row = new Object[5];   // {"Date","Description","Amount","Balance"};

    row[0]=type;
    if (date == 0) {
      row[1] = new String("");
    } else {
      row[1] = new Long(date).toString();
    }

    row[2]=description;
    row[3]=new Long(amount).toString();
    row[4]=format(balance);

    rowList.add(row);
  }

  private long findOverdueTxns(Calendar curr, long startBal, Account acct, ArrayList rowList){
	long          balance = startBal;
	Calendar today = Calendar.getInstance();
             today.setTime(curr.getTime());
	long todayLong = curr.getTime().getTime();
	dd("todayLong = "+todayLong);


	// adjust the starting balance to take into account the un-applied reminders
	    //long firstReminderDate = todayLong;
	    for(Enumeration en=balpredConf.rs.getAllReminders(); en.hasMoreElements();) {
	      Reminder r = (Reminder)en.nextElement();
	      if(!(r instanceof TransactionReminder)) continue;
	      if(!((Boolean)remindersStatus.get(r)).booleanValue()) continue;
	      TransactionReminder tr = (TransactionReminder)r;
	      if(Math.max(tr.getDateAcknowledged(), tr.getInitialDate())>=todayLong) continue;
	      ParentTxn txn = tr.getTransaction();
	      if(txn==null) continue;
	      long txnValue = 0;
	      if(txn.getAccount()==acct) {
	        txnValue += txn.getValue();
	      }
	      for(int splitNum=txn.getSplitCount()-1; splitNum>=0; splitNum--) {
	        SplitTxn split = txn.getSplit(splitNum);
	        if(split.getAccount()==acct) {
	          txnValue += split.getValue();
	        }
	      }
	      if(txnValue==0) continue;

	      // this transaction is overdue, and affects this account with a non-zero value.
	      // adjust the starting balance by amount 'txnValue' for every overdue occurance

	      Vector overdueDates = tr.getPastDueDates(today);

	      long delta =  (txnValue * tr.getPastDueDates(today).size());
	      if (delta == 0) continue;

	      dd("found overdue Reminder.");
	      dd("   delta = "+delta);

	      dd("  "+overdueDates.size()+" overdue dates.");
	      for (int i = 0; i<overdueDates.size(); i++) {
	    	  balance += txnValue;
	        addRow("O", ((Date) overdueDates.get(i)).getTime(), tr.getDescription(), txnValue,balance, rowList);
	      }

	      dd("   currentBalance = "+balance);
	    }

	    return balance;
  }

  private long findFutureTxns(long startBal, Account acct, ArrayList rowList) {
    AbstractTxn   txn;
    long          balance = startBal;
    int           i;

    dd("\nadding future transactions.");
    TxnSet txns = balpredConf.getTxnSet();      // root.getTransactionSet().getTransactionsForAccount(acct);

    JDateField todayField = new JDateField(new CustomDateFormat("MM/dd/yyyy"));
    todayField.gotoToday();
    int today = todayField.getDateInt();

    dd("today is "+today);
    dd("account has "+txns.getSize()+" transactions.");
    for (i=0; i<txns.getSize(); i++)
    {
      txn = txns.getTxn(i);
      if (txn.getDateInt() > today)
      {
        balance += txn.getValue();
        addRow("F", txn.getDate(), txn.getDescription(), txn.getValue(), balance, rowList);
        dd("adding "+txn.getDateInt()+txn.getDescription());
      }
    }
    return balance;
  }

  public void calcPredictedRBalance() {
    dd("Starting calcPredictedRBalance");
    calcPrDate();

    ArrayList rowList = new ArrayList();
    ArrayList txnList = new ArrayList();

    gp.removeAll();

    long currentBalance = getAccountBalance(balpredConf.getAccount());
    dd("currentBalance = "+currentBalance);
    long changes = 0;
    Account cacct = balpredConf.getAccount();

    setWaitCursor();

    Calendar curr = Calendar.getInstance();
	    curr.set(Calendar.HOUR_OF_DAY, 12);
	    curr.set(Calendar.AM_PM, Calendar.AM);
	    curr.set(Calendar.MINUTE, 0);
	    curr.set(Calendar.SECOND, 0);
	    curr.set(Calendar.MILLISECOND, 0);

    Calendar today = Calendar.getInstance();
    today.setTime(curr.getTime());

    addRow("S",Calendar.getInstance().getTime().getTime(),"Starting Balance",0,currentBalance, rowList);

    findFutureTxns(currentBalance, cacct, txnList);
    findOverdueTxns(curr, currentBalance, cacct, txnList);

    curr.setTime(today.getTime());

    Calendar stop = Calendar.getInstance();
	    stop.setTime(prDate);
	    stop.set(Calendar.HOUR_OF_DAY, 12);
	    stop.set(Calendar.AM_PM, Calendar.AM);
	    stop.set(Calendar.MINUTE, 0);
	    stop.set(Calendar.SECOND, 0);
	    stop.set(Calendar.MILLISECOND, 0);
    if (stop.before(curr)) return;

    ParentTxn ptxn = null;
    SplitTxn  stxn = null;

	final XYSeries series = new XYSeries("Balance", false, true);

    series.add(curr.getTime().getTime(), currentBalance/100.0);

    while(curr.before(stop) || curr.equals(stop)) {
      long currentTime = curr.getTime().getTime();

      Calendar nextDay = Calendar.getInstance();
      nextDay.setTime(curr.getTime());
      nextDay.add(Calendar.DAY_OF_MONTH, 1);

      //Loop through array and add all found transactions
      for(int i = 0; i < txnList.size(); i++){
    	  Object[] data = (Object[]) txnList.get(i);

    	  long txnDate = new Long((String) data[1]).longValue();

    	  if(txnDate >= curr.getTime().getTime() && txnDate < nextDay.getTime().getTime()){
    	  	long txnAmt = new Long((String) data[3]).longValue();
    	  	changes += txnAmt;
    	  	addRow((String) data[0], txnDate, (String) data[2], txnAmt, currentBalance + changes, rowList);
    	  }

      }

      for(Enumeration en = balpredConf.rs.getRemindersOnDay(curr).elements(); en.hasMoreElements();) {
        Reminder r = (Reminder)en.nextElement();
        if ((r.getReminderType() == Reminder.TXN_REMINDER_TYPE) && ((Boolean)remindersStatus.get(r)).booleanValue()) {
          ptxn = ((TransactionReminder)r).getTransaction();
          if (ptxn.getAccount().equals(cacct)) {
            changes += ptxn.getValue();
			dd("RM(p): "+dateFormat.format(currentTime)+" "+r.getDescription()+" "+format(ptxn.getValue()));
            addRow("R", currentTime, r.getDescription(), ptxn.getValue(), currentBalance + changes, rowList);
          }
          for(int i=0; i<ptxn.getSplitCount(); i++) {
            stxn = ptxn.getSplit(i);
            if (stxn.getAccount().equals(cacct)) {
                long val = CurrencyTable.convertValue(-stxn.getAmount(),
                                                      stxn.getParentTxn().getAccount().getCurrencyType(),
                                                      cacct.getCurrencyType(),
                                                      ptxn.getDate());
                changes += val;
                dd("RM(s): "+dateFormat.format(currentTime)+" "+r.getDescription()+" "+format(val));
                addRow("R", currentTime, r.getDescription(), val, currentBalance + changes, rowList);
            }
          }
        }
      }
	  series.add(currentTime, (currentBalance + changes)/100.0);

      curr.add(Calendar.DAY_OF_MONTH, 1);
    }

    tabData = new Object[rowList.size()][5];

    for (int i=0; i<rowList.size(); i++) {
      Object[] data = (Object[]) rowList.get(i);
      long txnDate  = new Long((String) data[1]).longValue();
      long txnAmt   = new Long((String) data[3]).longValue();

      data[1] = dateFormat.format(txnDate);
      data[3] = format(txnAmt);

      tabData[i] = data;
    }

    table.setModel(new DefaultTableModel(tabData,cols));


    for (int i=0; i<5; i++) {
      table.getColumnModel().getColumn(i).setCellRenderer(new DetailCellRenderer());
    }
    table.setAutoResizeMode(JTable.AUTO_RESIZE_ALL_COLUMNS);
    table.getColumnModel().getColumn(0).setPreferredWidth(8);
    table.getColumnModel().getColumn(1).setPreferredWidth(55);
    table.getColumnModel().getColumn(2).setPreferredWidth(150);

    table.repaint();

    gp.add(createChartPanel(series),  AwtUtil.getConstraints(0,0,1,1,1,1,true,true));
    setDefaultCursor();
  }

//   public void mouseMoved(MouseEvent e) {
//     /*
//     int x,y;
//     x = e.getX();
//     y = e.getY();
//     if (balGraph.getModel()!=null) {
//       double xScale = balGraph.getXScale();
//       double yScale = balGraph.getYScale();
//       if ((x < balGraph.getLeftMargin()) ||
//           (y > (balGraph.getSize().height - balGraph.getBottomMargin()))) {
//         return;
//       }
//       long date =
//         Math.round((x + xScale*balGraph.getMinX() - balGraph.getLeftMargin())/xScale);
//       double balance =
//         (balGraph.getSize().height
//           - y
//           - balGraph.getBottomMargin()
//           + yScale*balGraph.getMinY()
//         ) / yScale;
//       lbBalance.setText(dateFormat.format(new Date(date))+"    "
//         +balpredConf.getAccount().getCurrencyType().formatFancy(Math.round(balance),'.'));
//     } else {
//       lbBalance.setText(" ");
//     }
//     */
//   }
//
//   public void mouseDragged(MouseEvent e) {
//     mouseMoved(e);
//   }

  private Vector getTxnRemindersVect() {
    Vector v = balpredConf.rs.getAllRemindersVect();
    Vector res = new Vector();
    for(int i=0;i<v.size();i++) {
      Reminder r  = (Reminder)v.elementAt(i);
      if (r.getReminderType()==Reminder.TXN_REMINDER_TYPE) res.add(r);
    }
    return res;
  }

  private void ManageReminders() {
    class RemindersTableModel extends AbstractTableModel {
	  private static final long serialVersionUID = 1L;
	  private String[] headNames = new String[] {"Reminders","Enabled"};
      private Object[][] data = null;
      private int tsize = getTxnRemindersVect().size();
      private Reminder r = null;
      RemindersTableModel() {
        data = new Object[tsize][2];
        Vector v = getTxnRemindersVect();
        for (int i=0;i<tsize;i++) {
          r = (Reminder)v.elementAt(i);
          data[i][0] = r;
          data[i][1] = remindersStatus.get(r);
        }
      }
      public int getColumnCount() { return 2; }
      public int getRowCount() { return tsize;}
      public String getColumnName(int col) {
        return headNames[col];
      }
      public boolean isCellEditable(int row, int col) {
        return (col==1);
      }
      public Object getValueAt(int row, int col) {
        return data[row][col];
      }
      public void setValueAt(Object value, int row, int col) {
        if (col==1) {
          data[row][1] = value;
          Reminder r  = (Reminder)data[row][0];
          remindersStatus.remove(r);
          remindersStatus.put(r, value);
        }
        fireTableCellUpdated(row, col);
      }
      public Class getColumnClass(int col) {
        return data[0][col].getClass();
      }
    };

    JTable reminders = new JTable(new RemindersTableModel());
    reminders.getColumnModel().getColumn(0).setPreferredWidth(200);
    reminders.getColumnModel().getColumn(1).setPreferredWidth(50);
    reminders.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
    reminders.setCellSelectionEnabled(true);
    JScrollPane scrollpane = new JScrollPane(reminders);
    manageDlg = new JDialog((Frame)null, "Reminders", true);
    JPanel tp = new JPanel(gbl);
    btDone1 = new JButton("Done");
    btDone1.addActionListener(this);
    tp.add(scrollpane, AwtUtil.getConstraints(0,0,1,1,1,1,true,true));
    tp.add(new JLabel(" "), AwtUtil.getConstraints(0,1,1,0,1,1,false,false));
    tp.add(btDone1, AwtUtil.getConstraints(0,2,1,0,1,1,false,false));
    tp.add(new JLabel(" "), AwtUtil.getConstraints(0,3,1,0,1,1,false,false));
    manageDlg.getContentPane().add(tp);
    manageDlg.setSize(320,300);
    AwtUtil.centerWindow(manageDlg);
    manageDlg.setVisible(true);
  }

  public void actionPerformed(ActionEvent e) {
    Object src = e.getSource();
    btReminders.setVisible(true);
    if (src==btReminders) {
      ManageReminders();
      return;      // so we don't recalculate and display everything
    }
    else if(src==balpredConf.cbAccounts) {
      boolean noRem = balpredConf.getReminderCount()==0;
      if (noRem) {
        btReminders.setVisible(false);
      }
    }
    else if(src==btDone) {
      setVisible(false);
      return;       // so we don't recalculate and display everything
    }
    else if(src==btDone1) {
      manageDlg.setVisible(false);
    }
    calcPredictedRBalance();
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
        tmp.add(Calendar.MONTH, num);
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

	private ChartPanel createChartPanel(XYSeries s1) {
		final XYSeriesCollection dataset = new XYSeriesCollection();
		dataset.addSeries(s1);

		final JFreeChart chart = ChartFactory.createXYStepChart(
				"Predicted Balance", "Time", "Balance", dataset, PlotOrientation.VERTICAL,
				false, true, false);   // legend, tooltips, urls;

		chart.setBackgroundPaint(new Color(216, 216, 216));
		final XYPlot plot = chart.getXYPlot();
		XYItemRenderer renderer = plot.getRenderer();
		renderer.setSeriesStroke(0, new BasicStroke(2.0f));
		dd("The class of renderer is " + renderer.getClass().getName());
		renderer.setSeriesToolTipGenerator(0, new XYToolTipGenerator () {
	      public String generateToolTip(XYDataset data, int series, int index) {
	        return dateFormat.format(data.getX(series,index).doubleValue())+" "
							+format((long)(data.getY(series,index).doubleValue()*100.0));
	      }
		});

		ChartPanel cp = new ChartPanel(chart);
		return cp;
	}

}

