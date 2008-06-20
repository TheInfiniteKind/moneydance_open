/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.moneydance.apps.md.model.*;
import com.moneydance.apps.md.controller.*;
import com.moneydance.awt.*;
import com.moneydance.awt.graph.*;
import com.moneydance.util.*;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;
import javax.swing.border.*;
import javax.swing.table.*;
import java.io.*;
import java.util.*;
import java.net.*;
import java.text.*;

public class BalancePredicter 
  extends JDialog
  implements ActionListener, MouseMotionListener, Runnable
{
  private JPanel mp, gp, bp, bpl, bpr;
  private JButton btReminders, btBuild, btDone, btDone1;
  private JComboBox cbFutuIntervals = new JComboBox();
  private JComboBox cbFutuNum = new JComboBox();
  private JComboBox cbPastIntervals = new JComboBox();
  private JComboBox cbPastNum = new JComboBox();
  private JComboBox cbAccounts = new JComboBox();
  private JDialog manageDlg = null;
  private BalPredRGraph balRGraph = null;
  private BalPredTGraph balTGraph = null;
  private BalPredGraph balGraph = null;
  private JLabel lbBalance = new JLabel("");
  private JLabel lbFutu, lbPast;
  private Resources rr = null;
  private BalPredConf balpredConf = null;
  private Date prDate = new Date();
  private GridBagLayout gbl = new GridBagLayout();
  private Hashtable remindersStatus = new Hashtable();
  private SimpleDateFormat dateFormat;
  private DateLabeler dateLabeler;
  
  public BalancePredicter(Resources rr, BalPredConf balpredConf) {
    this.rr = rr;
    this.balpredConf = balpredConf;
    dateFormat = new SimpleDateFormat(balpredConf.dateFormatStr);
    dateLabeler = new DateLabeler(dateFormat);
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

    cbFutuIntervals.addItem(rr.getString("days"));
    cbFutuIntervals.addItem(rr.getString("weeks"));
    cbFutuIntervals.addItem(rr.getString("months"));
    cbFutuIntervals.addItem(rr.getString("years"));
    cbFutuIntervals.setSelectedIndex(2);
    for (int i=1;i<=balpredConf.INTERVALS;i++) cbFutuNum.addItem(String.valueOf(i));
    cbFutuNum.setSelectedIndex(1);
    
    cbPastIntervals.addItem(rr.getString("months"));
    cbPastIntervals.addItem(rr.getString("years"));
    cbPastIntervals.setSelectedIndex(0);
    cbPastIntervals.addActionListener(this);
    for (int i=1;i<=balpredConf.INTERVALS;i++) cbPastNum.addItem(new String(""+i));
    cbPastNum.setSelectedIndex(2);

    btReminders = new JButton(rr.getString("manage_reminders"));
    btReminders.addActionListener(this);
    btBuild = new JButton(rr.getString("build_graph"));
    btBuild.addActionListener(this);
    btDone = new JButton(rr.getString("done"));
    btDone.addActionListener(this);
    
    lbFutu = new JLabel(rr.getString("future_period"), JLabel.RIGHT);
    lbPast = new JLabel(rr.getString("past_period"), JLabel.RIGHT);

    balpredConf.cbAccounts.addActionListener(this);
    balpredConf.rbReminders.addActionListener(this);
    balpredConf.rbTransactions.addActionListener(this);

    boolean boRem = balpredConf.getBasedOn()==balpredConf.basedonReminders;
    cbPastIntervals.setVisible(!boRem);
    cbPastNum.setVisible(!boRem);
    lbPast.setVisible(!boRem);
    btReminders.setVisible(boRem);
    
    lbBalance.setText(" ");

    int yy = 0;
    bpl.add(new JLabel(rr.getString("account")+"   ", JLabel.RIGHT), 
      AwtUtil.getConstraints(0,yy,0,0,1,1,true,false));
    bpl.add(balpredConf.cbAccounts, AwtUtil.getConstraints(1,yy++,1,0,1,1,true,false));
    bpl.add(balpredConf.rbReminders, AwtUtil.getConstraints(0,yy++,1,0,2,1,true,false));
    bpl.add(balpredConf.rbTransactions, AwtUtil.getConstraints(0,yy++,1,0,2,1,true,false));
    
    yy = 0;
    bpr.add(lbFutu, AwtUtil.getConstraints(0,yy,1,0,1,1,true, false));
    bpr.add(cbFutuNum, AwtUtil.getConstraints(1,yy,0,0,1,1,true,false));
    bpr.add(cbFutuIntervals, AwtUtil.getConstraints(2,yy++,1,0,1,1,true,false));
    bpr.add(lbPast, AwtUtil.getConstraints(0,yy,1,0,1,1,true, false));
    bpr.add(cbPastNum, AwtUtil.getConstraints(1,yy,0,0,1,1,true,false));
    bpr.add(cbPastIntervals, AwtUtil.getConstraints(2,yy++,1,0,1,1,true,false));
    bpr.add(btReminders, AwtUtil.getConstraints(0,yy++,1,0,3,1,true,false));
    bpr.add(new JLabel(" "), AwtUtil.getConstraints(0,yy,1,1,3,1,true,true));

    Calendar tmp = Calendar.getInstance();
    tmp.set(Calendar.HOUR_OF_DAY, 12); 
    tmp.set(Calendar.AM_PM, Calendar.AM);
    tmp.set(Calendar.MINUTE, 0); 
    tmp.set(Calendar.SECOND, 0); 
    tmp.set(Calendar.MILLISECOND, 0);
    tmp.add(Calendar.MONTH, balpredConf.DEF_NUM);

    bp.add(bpl);
    bp.add(bpr);
    mp.add(gp, AwtUtil.getConstraints(0,0,1,1,2,1,true,true));
    mp.add(bp, AwtUtil.getConstraints(0,1,1,0,2,1,true,true));
    mp.add(btBuild, AwtUtil.getConstraints(0,2,1,0,1,1,false,false));
    mp.add(btDone, AwtUtil.getConstraints(1,2,1,0,1,1,false,false));
    getContentPane().add(mp);
    pack();
    setSize(620, 460);
    AwtUtil.centerWindow(this);
    setVisible(true);

    if (balpredConf.getBasedOn()==balpredConf.basedonReminders)
      calcPredictedRBalance();
    else calcPredictedTBalance();
    validate();
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

  public void calcPredictedRBalance() {
    calcPrDate();
    
    gp.removeAll();
    balRGraph = new BalPredRGraph(null,rr);
    balRGraph.setBackground(Color.white);
    balRGraph.addMouseMotionListener(this);
    balGraph = balRGraph;

    long currentBalance = getAccountBalance(balpredConf.getAccount());
    long changes = 0;
    Vector dataPoints = new Vector();
    Vector averagePoints = new Vector();
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
    long todayLong = curr.getTime().getTime();
    
    Calendar pastCal = Calendar.getInstance();

    // adjust the starting balance to take into account the un-applied reminders
    long firstReminderDate = todayLong;
    for(Enumeration enum=balpredConf.rs.getAllReminders(); enum.hasMoreElements();) {
      Reminder r = (Reminder)enum.nextElement();
      if(!(r instanceof TransactionReminder)) continue;
      if(!((Boolean)remindersStatus.get(r)).booleanValue()) continue;
      TransactionReminder tr = (TransactionReminder)r;
      if(Math.max(tr.getDateAcknowledged(), tr.getInitialDate())>=todayLong) continue;
      ParentTxn txn = tr.getTransaction();
      if(txn==null) continue;
      long txnValue = 0;
      if(txn.getAccount()==cacct) {
        txnValue += txn.getValue();
      }
      for(int splitNum=txn.getSplitCount()-1; splitNum>=0; splitNum--) {
        SplitTxn split = txn.getSplit(splitNum);
        if(split.getAccount()==cacct) {
          txnValue += split.getValue();
        }
      }
      if(txnValue==0) continue;

      // this transaction is overdue, and affects this account with a non-zero value.
      // adjust the starting balance by amount 'txnValue' for every overdue occurance
      currentBalance += (txnValue * tr.getPastDueDates(today).size());

      // TODO: Make this handle loan reminders (and their variable values) better
    }

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
    Calendar tmp = Calendar.getInstance();
    TxnSet txns = balpredConf.getTxnSet();
    DataPoint lastPoint = null;
    
    while(curr.before(stop) || curr.equals(stop)) {
      for(Enumeration enum = balpredConf.rs.getRemindersOnDay(curr).elements(); enum.hasMoreElements();) {
        Reminder r = (Reminder)enum.nextElement();
        if ((r.getReminderType() == Reminder.TXN_REMINDER_TYPE) && 
            ((Boolean)remindersStatus.get(r)).booleanValue()) {
          ptxn = ((TransactionReminder)r).getTransaction();
          if (ptxn.getAccount().equals(cacct)) {
            changes += ptxn.getValue();
          }
          for(int i=0; i<ptxn.getSplitCount(); i++) {
            stxn = ptxn.getSplit(i);
            if (stxn.getAccount().equals(cacct)) {
              changes +=
                CurrencyTable.convertValue(-stxn.getAmount(),
                                           stxn.getParentTxn().getAccount().getCurrencyType(),
                                           cacct.getCurrencyType(),
                                           ptxn.getDate());
            }
          }
        }
      }
      
      long currentTime = curr.getTime().getTime();
      
      // found all txns for this day, except today
      /*
      if (!curr.equals(today)) {
        for (int i=0; i<txns.getSize(); i++) {
          if (Math.abs(txns.getTxnAt(i).getDate() - currentTime)<=43200000) {
            changes += txns.getTxnAt(i).getValue();
          }
        }
      }
      */
      
      if(lastPoint!=null) {  // re-add the last point... with the new date
        dataPoints.addElement(new DataPoint(currentTime, lastPoint.balance));
      }
      lastPoint = new DataPoint(currentTime, currentBalance + changes);
      dataPoints.addElement(lastPoint);
      
      curr.add(Calendar.DAY_OF_MONTH, 1);
    }
    
    long avg;
    int width = 14;
    int numDataPoints = dataPoints.size();
    for (int i=0; i<numDataPoints; i++) {
      int count = 0;
      avg = 0;
      DataPoint dataPoint = (DataPoint)dataPoints.elementAt(i);
      for (int j=(i-width); j<=(i+width); j++) {
        count++;
        if (j<0 || j>=dataPoints.size()) {
          avg += dataPoint.balance;
        } else {
          avg += ((DataPoint)dataPoints.elementAt(j)).balance;
        }
      }
      averagePoints.addElement(new DataPoint(dataPoint.date, Math.round((1.0*avg)/count)));
    }
    
    double xvalues[] = new double[numDataPoints];
    double yvalues[] = new double[numDataPoints];
    double xvaluesA[] = new double[numDataPoints];
    double yvaluesA[] = new double[numDataPoints];
    for (int i=0; i<numDataPoints; i++) {
      DataPoint dataPoint = (DataPoint)dataPoints.elementAt(i);
      DataPoint avgPoint = (DataPoint)averagePoints.elementAt(i);
      xvalues[i] = (double)dataPoint.date;
      yvalues[i] = (double)dataPoint.balance;
      xvaluesA[i] = (double)avgPoint.date;
      yvaluesA[i] = (double)avgPoint.balance;
    }
    
    XYGraphDataSet gDataSet[] = new XYGraphDataSet[2];
    gDataSet[0] = new XYGraphDataSet(null, null, cacct, xvalues, yvalues, Color.blue);
    gDataSet[1] = new XYGraphDataSet(null, null, cacct, xvaluesA, yvaluesA, Color.black);
    balpredConf.setGraphModel(new LineGraphModel(gDataSet));
    LineGraphModel lgm = (LineGraphModel)balpredConf.getGraphModel();
    lgm.setXAxisLabeler(dateLabeler);
    lgm.setValueLabeler(new CurrencyLabeler(cacct.getCurrencyType()));
    lgm.setShowZero(false);
    lgm.setThreeD(false);
    balRGraph.setModel(lgm);
    gp.add(balRGraph, AwtUtil.getConstraints(0,0,1,1,1,1,true,true));
    gp.add(lbBalance, AwtUtil.getConstraints(0,1,1,0,1,1,false,false));
    setDefaultCursor();
  }

  public void calcPredictedTBalance() {
    calcPrDate();
    gp.removeAll();
    balTGraph = new BalPredTGraph(null,rr);
    balTGraph.setBackground(Color.white);
    balTGraph.addMouseMotionListener(this);

    Vector vDates = new Vector();
    Vector vBalancesMid = new Vector();
    Vector vBalancesTop = new Vector();
    Vector vBalancesBot = new Vector();
    long changes = 0;
    Account cacct = balpredConf.getAccount();
    int accType = cacct.getAccountType();

    Calendar curr = Calendar.getInstance();
    curr.set(Calendar.HOUR_OF_DAY, 12); 
    curr.set(Calendar.AM_PM, Calendar.AM);
    curr.set(Calendar.MINUTE, 0); 
    curr.set(Calendar.SECOND, 0); 
    curr.set(Calendar.MILLISECOND, 0);
    Calendar tmpCal = Calendar.getInstance();
    Calendar tmpCal1 = Calendar.getInstance();

    Calendar today = Calendar.getInstance();
    today.setTime(curr.getTime());
    long mind = today.getTime().getTime();
    // finding first transaction date
    TxnSet txns = balpredConf.getTxnSet();
    for (int i=0;i<txns.getSize();i++) {
      mind = Math.min(txns.getTxnAt(i).getDate(), mind);
    }
    tmpCal.setTime(new Date(mind));
    tmpCal.add(Calendar.MONTH, 3);
    if (tmpCal.getTime().after(today.getTime())) {
      gp.add(new JLabel(" "), AwtUtil.getConstraints(0,0,1,1,1,1,true,false));
      gp.add(new JLabel(rr.getString("too_short")), AwtUtil.getConstraints(0,1,0,0,1,1,false,false));
      gp.add(new JLabel(" "), AwtUtil.getConstraints(0,2,1,1,1,1,true,false));
      gp.repaint();
      return;
    }

    setWaitCursor();

    int num = cbPastNum.getSelectedIndex()+1;
    long pastMonths = num;
    switch(cbPastIntervals.getSelectedIndex()) {
      case 0:
        // we accept shorter period to be 3 months
        num = num<3 ? 3 : num;
        pastMonths = num;
        cbPastNum.setSelectedIndex(num-1);
        curr.add(Calendar.MONTH, -1*num);
        break;
      case 1:
        curr.add(Calendar.YEAR, -1*num);
        pastMonths = num*12;
        break;
    }
    tmpCal.setTime(new Date(mind));

    // moving starting date to be after first transaction
    while(tmpCal.after(curr)) {
      curr.add(Calendar.MONTH, 1);
      pastMonths--;
      if (pastMonths<=balpredConf.INTERVALS) {
        cbPastIntervals.setSelectedIndex(0);
        cbPastNum.setSelectedIndex((int)(pastMonths-1));
      }
    }
    // curr is now date we can use as starting date for predictions

    long days = (today.getTime().getTime()-curr.getTime().getTime())/86400000;

    Calendar stop = Calendar.getInstance(); // future date
    stop.setTime(prDate);
    stop.set(Calendar.HOUR_OF_DAY, 12); 
    stop.set(Calendar.AM_PM, Calendar.AM);
    stop.set(Calendar.MINUTE, 0); 
    stop.set(Calendar.SECOND, 0); 
    stop.set(Calendar.MILLISECOND, 0);
    stop.add(Calendar.DAY_OF_MONTH, 1);

    // calculate average balance for first month in past period (AF)
    tmpCal.setTime(curr.getTime());
    tmpCal.add(Calendar.MONTH, 1);
    long f1 = getAvgPeriodBalance(curr.getTime(), tmpCal.getTime());

    // calculate average balance for last month in past period (AP)
    tmpCal.setTime(today.getTime());
    tmpCal.add(Calendar.MONTH, -1);
    long f2 = getAvgPeriodBalance(tmpCal.getTime(), today.getTime());

    // calculate average monthly changes (AMCH)
    long amch = Math.round(1.0*(f2-f1)/pastMonths);
    
    // calculate average diff between real balances and averages
    long realBal[] = new long[(int)pastMonths];
    long diffBalU = 0, diffBalD = 0;
    long minb, maxb;
    tmpCal.setTime(today.getTime());
    tmpCal.add(Calendar.MONTH, -1*(int)pastMonths);
    tmpCal1.setTime(tmpCal.getTime());
    tmpCal1.add(Calendar.MONTH, 1);
    for(int i=0;i<pastMonths;i++) {
      realBal[i] = getAvgPeriodBalance(tmpCal.getTime(), tmpCal1.getTime());
      minb = getMinPeriodBalance(tmpCal.getTime(), tmpCal1.getTime());
      maxb = getMaxPeriodBalance(tmpCal.getTime(), tmpCal1.getTime());
      diffBalU = Math.max(diffBalU, Math.abs(realBal[i]-maxb));
      diffBalD = Math.max(diffBalD, Math.abs(realBal[i]-minb));
      tmpCal.add(Calendar.MONTH, 1);
      tmpCal1.add(Calendar.MONTH, 1);
    }
    //diffBal = Math.round(2.0*diffBal/pastMonths);
    long currentBalance = realBal[(int)pastMonths-1];
    long currentBalanceTop = currentBalance + diffBalU;
    long currentBalanceBot = currentBalance - diffBalD;
    
    // calculate data for future period graph
    curr.setTime(today.getTime());
    boolean kindofloan = 
      (accType==Account.ACCOUNT_TYPE_LOAN) ||
      (accType==Account.ACCOUNT_TYPE_CREDIT_CARD) ||
      (accType==Account.ACCOUNT_TYPE_LIABILITY);

    while(curr.getTime().before(stop.getTime())) {
      vDates.addElement(new Date(curr.getTime().getTime()));
      vBalancesTop.addElement(new Long(currentBalanceTop));
      vBalancesMid.addElement(new Long(currentBalance));
      vBalancesBot.addElement(new Long(currentBalanceBot));
      currentBalance += Math.round(1.0*amch/30.44);
      currentBalanceTop = currentBalance + diffBalU;
      currentBalanceBot = currentBalance - diffBalD;
      curr.add(Calendar.DAY_OF_MONTH, 1);
      if (kindofloan && currentBalance>0) break;
    }

    // calculate data for past period graph
    tmpCal.setTime(today.getTime());
    tmpCal.add(Calendar.MONTH, -1*(int)pastMonths);
    int pastDays = (int)((today.getTime().getTime()-tmpCal.getTime().getTime())/86400000);
    double xvaluesMid[] = new double[pastDays+vDates.size()];
    double yvaluesMid[] = new double[xvaluesMid.length];
    double xvaluesTop[] = new double[pastDays+vDates.size()];
    double yvaluesTop[] = new double[xvaluesTop.length];
    double xvaluesBot[] = new double[pastDays+vDates.size()];
    double yvaluesBot[] = new double[xvaluesBot.length];
    int k = 0;
    xvaluesMid[k] = (double)tmpCal.getTime().getTime();
    yvaluesMid[k] = (double)(getPastBalance(tmpCal.getTime())) / 100;
    xvaluesTop[k] = xvaluesMid[k];
    yvaluesTop[k] = yvaluesMid[k];
    xvaluesBot[k] = xvaluesMid[k];
    yvaluesBot[k] = yvaluesMid[k];
    while(tmpCal.before(today)) {
      tmpCal.add(Calendar.DAY_OF_MONTH, 1);
      k++;
      xvaluesMid[k] = (double)tmpCal.getTime().getTime();
      yvaluesMid[k] = yvaluesMid[k-1];
      for (int i=0;i<txns.getSize();i++) {
        if (txns.getTxnAt(i).getDate()==tmpCal.getTime().getTime())
          yvaluesMid[k] += (double)((txns.getTxnAt(i).getValue()) / 100);
      }
      xvaluesTop[k] = xvaluesMid[k];
      yvaluesTop[k] = yvaluesMid[k];
      xvaluesBot[k] = xvaluesMid[k];
      yvaluesBot[k] = yvaluesMid[k];
    }

    Date dates;
    Long lBal;
    for (int i=0; i<vDates.size(); i++) {
      dates = (Date)vDates.get(i);
      lBal = (Long)vBalancesTop.get(i);
      xvaluesTop[pastDays+i] = (double)(dates.getTime());
      yvaluesTop[pastDays+i] = lBal.doubleValue() / 100;
      lBal = (Long)vBalancesMid.get(i);
      xvaluesMid[pastDays+i] = (double)(dates.getTime());
      yvaluesMid[pastDays+i] = lBal.doubleValue() / 100;
      lBal = (Long)vBalancesBot.get(i);
      xvaluesBot[pastDays+i] = (double)(dates.getTime());
      yvaluesBot[pastDays+i] = lBal.doubleValue() / 100;
    }
    XYGraphDataSet gDataSet[] = new XYGraphDataSet[3];
    gDataSet[0] = new XYGraphDataSet(null, null, cacct, xvaluesTop, yvaluesTop, Color.blue);
    gDataSet[1] = new XYGraphDataSet(null, null, cacct, xvaluesBot, yvaluesBot, Color.red);
    gDataSet[2] = new XYGraphDataSet(null, null, cacct, xvaluesMid, yvaluesMid, Color.black);
    balpredConf.setGraphModel(new LineGraphModel(gDataSet));
    LineGraphModel lgm = (LineGraphModel)balpredConf.getGraphModel();
    lgm.setXAxisLabeler(dateLabeler);
    lgm.setShowZero(false);
    lgm.setXAxisType(DataSetUtilities.TYPE_DATE);
    lgm.setThreeD(false);
    balTGraph.setModel(lgm);
    balGraph = balTGraph;
    gp.add(balTGraph, AwtUtil.getConstraints(0,0,1,1,1,1,true,true));
    gp.add(lbBalance, AwtUtil.getConstraints(0,1,1,0,1,1,false,false));
    setDefaultCursor();
  }

  public void mouseMoved(MouseEvent e) {
    /*
    int x,y;
    x = e.getX();
    y = e.getY();
    if (balGraph.getModel()!=null) {
      double xScale = balGraph.getXScale();
      double yScale = balGraph.getYScale();
      if ((x < balGraph.getLeftMargin()) ||
          (y > (balGraph.getSize().height - balGraph.getBottomMargin()))) {
        return;
      }
      long date = 
        Math.round((x + xScale*balGraph.getMinX() - balGraph.getLeftMargin())/xScale);
      double balance = 
        (balGraph.getSize().height 
          - y 
          - balGraph.getBottomMargin() 
          + yScale*balGraph.getMinY()
        ) / yScale;
      lbBalance.setText(dateFormat.format(new Date(date))+"    "
        +balpredConf.getAccount().getCurrencyType().formatFancy(Math.round(balance),'.'));
    } else {
      lbBalance.setText(" ");
    }
    */
  }

  public void mouseDragged(MouseEvent e) {
    mouseMoved(e);
  }

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
      private String[] headNames = 
        new String[] {rr.getString("reminders"),rr.getString("enabled")};
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
    manageDlg = new JDialog((Frame)null, rr.getString("reminders"), true);
    JPanel tp = new JPanel(gbl);
    btDone1 = new JButton(rr.getString("done"));
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
    if (src==balpredConf.rbReminders) {
      balpredConf.rbReminders.setSelected(true);
      balpredConf.rbTransactions.setSelected(false);
    } else if (src==balpredConf.rbTransactions) {
      balpredConf.rbReminders.setSelected(false);
      balpredConf.rbTransactions.setSelected(true);
    }
    
    boolean boRem = (balpredConf.getBasedOn()==balpredConf.basedonReminders);
    cbPastIntervals.setVisible(!boRem);
    cbPastNum.setVisible(!boRem);
    lbPast.setVisible(!boRem);
    btReminders.setVisible(boRem);
    if (src==btReminders) {
      ManageReminders();
    } else if(src==balpredConf.cbAccounts) {
      int accType = balpredConf.getAccount().getAccountType();
      if (balpredConf.getAccount().getBalance()>=0 && 
        (accType==Account.ACCOUNT_TYPE_CREDIT_CARD ||
        accType==Account.ACCOUNT_TYPE_LIABILITY)) {
          btBuild.setEnabled(false);
      } else {
        btBuild.setEnabled(true);
      }
      boolean noRem = balpredConf.getReminderCount()==0;
      balpredConf.rbReminders.setEnabled(!noRem);
      if (noRem) {
        balpredConf.rbTransactions.setSelected(true);
        balpredConf.rbReminders.setSelected(false);
        cbPastIntervals.setVisible(true);
        cbPastNum.setVisible(true);
        lbPast.setVisible(true);
        btReminders.setVisible(false);
      }
    } else if(src==btBuild) {
      if (boRem) calcPredictedRBalance();
      else calcPredictedTBalance();
      validate();
      repaint();
    } else if(src==btDone) {
      setVisible(false);
    } else if(src==btDone1) {
      manageDlg.setVisible(false);
    }
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

  public long getPastBalance(Date d) {
    long bal = balpredConf.getAccount().getBalance();
    long td;
    TxnSet txns = balpredConf.getTxnSet();
    for (int i=0;i<txns.getSize();i++) {
      td = txns.getTxnAt(i).getDate();
      if (td>d.getTime()) {
        bal -= txns.getTxnAt(i).getValue();
      }
    }
    return bal;
  }

  public long getAvgPeriodBalance(Date d1, Date d2) {
    long sum = 0, changes;
    long days = (d2.getTime()-d1.getTime())/86400000;
    long bal = getPastBalance(d1);
    Calendar tmpCal = Calendar.getInstance();
    TxnSet txns = balpredConf.returnTxnSet();
    tmpCal.setTime(d1);
    for (int j=0;j<days;j++) {
      tmpCal.add(Calendar.DAY_OF_MONTH, 1);
      changes = 0;
      for (int i=0;i<txns.getSize();i++) {
        if (txns.getTxnAt(i).getDate()==tmpCal.getTime().getTime()) {
          changes += txns.getTxnAt(i).getValue();
        }
      }
      bal = bal + changes;
      sum += bal;
    }
    return Math.round(1.0*sum/days);
  }

  public long getMaxPeriodBalance(Date d1, Date d2) {
    long changes;
    long days = (d2.getTime()-d1.getTime())/86400000;
    long bal = getPastBalance(d1);
    long maxb = bal;
    Calendar tmpCal = Calendar.getInstance();
    TxnSet txns = balpredConf.returnTxnSet();
    tmpCal.setTime(d1);
    for (int j=0;j<days;j++) {
      tmpCal.add(Calendar.DAY_OF_MONTH, 1);
      changes = 0;
      for (int i=0;i<txns.getSize();i++) {
        if (txns.getTxnAt(i).getDate()==tmpCal.getTime().getTime()) {
          changes += txns.getTxnAt(i).getValue();
        }
      }
      bal = bal + changes;
      maxb = Math.max(maxb, bal);
    }
    return maxb;
  }

  public long getMinPeriodBalance(Date d1, Date d2) {
    long changes;
    long days = (d2.getTime()-d1.getTime())/86400000;
    long bal = getPastBalance(d1);
    long minb = bal;
    Calendar tmpCal = Calendar.getInstance();
    TxnSet txns = balpredConf.returnTxnSet();
    tmpCal.setTime(d1);
    for (int j=0;j<days;j++) {
      tmpCal.add(Calendar.DAY_OF_MONTH, 1);
      changes = 0;
      for (int i=0;i<txns.getSize();i++) {
        if (txns.getTxnAt(i).getDate()==tmpCal.getTime().getTime()) {
          changes += txns.getTxnAt(i).getValue();
        }
      }
      bal = bal + changes;
      minb = Math.min(minb, bal);
    }
    return minb;
  }

  class DataPoint {
    long date;
    long balance;

    DataPoint(long date, long balance) {
      this.date = date;
      this.balance = balance;
    }
  }
  
  class CurrencyLabeler
    implements ValueLabeler
  {
    private CurrencyType curr;

    CurrencyLabeler(CurrencyType ct) {
      this.curr = ct;
    }

    public String getLabelForValue(double value, int type) {
      return curr.format(Math.round(value), '.');
    }
  }
  
  class DateLabeler
    implements ValueLabeler
  {
    private DateFormat dateFormat;
    
    DateLabeler(DateFormat dateFormat) {
      this.dateFormat = dateFormat;
    }
    
    public String getLabelForValue(double value, int type) {
      return dateFormat.format(new Date(Math.round(value)));
    }
  }
  
}

