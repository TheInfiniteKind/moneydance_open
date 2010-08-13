/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.paypalas;

import com.moneydance.apps.md.model.*;
import com.moneydance.apps.md.controller.*;
import com.moneydance.apps.md.controller.olb.*;
import com.moneydance.util.*;
import com.moneydance.awt.*;

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

public class PayPalWindow
  extends JDialog 
  implements ActionListener, DocumentListener, ListSelectionListener
{
  private Main extension;
  private WaitWindow waitWindow = null;
  private Resources rr;
  private RootAccount root = null;
  private Account ca = null;
  private JPanel mp, bp, lp, rp, idp;
  private JButton btUpdate, btExit, btExit1, btAccounts, btAdd, btRemove;
  private JButton btCancel, btAccept, btMerge, btImport;
  private JCheckBox chbNew;
  private JTextField tfUserID, tfNewUserID;
  private JPasswordField tfPassword;
  private JComboBox cbAccounts;
  private JDialog dlgAcct = null;
  private JDialog dlgTxns = null;
  private JList listAcct = new JList();
  private JTable tableTxns = null;
  private PayPalTableModel tmTxns = null;
  private ListSelectionModel lsmAcct;
  private ListSelectionModel lsmTxns;
  private DefaultListModel lmAcct = new DefaultListModel();
  private DefaultListModel lmTxns = new DefaultListModel();
  private URL paypalURL = null;
  private Hashtable cookies = new Hashtable();
  private Vector txns = null;
  private CustomDateFormat fmt = new CustomDateFormat("MM/dd/yyyy");
  private TxnSet tset = null;
  private TransactionSet ts = null;
  
  private final static String SPAYPAL = "https://www.paypal.com";
  private final static String PAYPAL = "http://www.paypal.com";
  private final static String PAYPAL_GET_MAIN = "/cgi-bin/webscr?cmd=_login-run";
  private final static String PAYPAL_POST_LOGIN = "/cgi-bin/webscr?__track=_login-run:p/gen/login:_login-submit";
  private final static String PAYPAL_GET_HISTORY = "/cgi-bin/webscr?cmd=_history";
  private final static String PAYPAL_GET_HISTORY_DOWNLOAD = "/cgi-bin/webscr?cmd=_history-download";
  private final static String PAYPAL_POST_DOWNLOAD = "/cgi-bin/webscr?__track=_history-download:p/acc/history_download:_history-download-submit";
  private final static String PAYPAL_GET_LOGOUT = "/cgi-bin/webscr?cmd=_logout";

  private final static String AGENT_HOST = "User-Agent: Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)\nHost: www.paypal.com:443\n";

  private final static int PAYPAL_DATE = 0;
  private final static int PAYPAL_NAME = 2;
  private final static int PAYPAL_TYPE = 3;
  private final static int PAYPAL_SUBJ = 5;
  private final static int PAYPAL_GROSS = 6;
  private final static int PAYPAL_FEE = 7;
  private final static int PAYPAL_NET = 8;
  private final static int PAYPAL_EMAIL = 10;
  private final static int PAYPAL_TID = 12;
  private final static int PAYPAL_ITEM = 16;
  private final static int PP_ITEMS = 27;
  
  public PayPalWindow(Main extension) {
    super((Frame)null, extension.getName(), true);

    this.extension = extension;
    
    rr = (Resources)ResourceBundle.getBundle("com.moneydance.modules.features.paypalas.Resources", Locale.getDefault());
    root = extension.getRoot();
    
    mp = new JPanel(new GridBagLayout());
    mp.setBorder(new EmptyBorder(10,10,10,10));

    btAccounts = new JButton(rr.getString("accounts"));
    btAccounts.addActionListener(this);
    btUpdate = new JButton(rr.getString("update"));
    btUpdate.addActionListener(this);
    btUpdate.setEnabled(false);
    btUpdate.registerKeyboardAction(this, "update", 
                                  KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, 0),
                                  JComponent.WHEN_IN_FOCUSED_WINDOW);
    btExit = new JButton(rr.getString("exit"));
    btExit.addActionListener(this);
    btExit.registerKeyboardAction(this, "exit", 
                                  KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
                                  JComponent.WHEN_IN_FOCUSED_WINDOW);
    btImport = new JButton(rr.getString("import"));
    btImport.addActionListener(this);
    btImport.setEnabled(false);

    chbNew = new JCheckBox(rr.getString("only_new"), true);
    tfUserID = new JTextField(5);
    tfUserID.setEnabled(false);
    tfPassword = new JPasswordField(5);
    cbAccounts = new JComboBox();
    loadPayPalAccounts(root);
    setUserID();
    loadAccounts(root);

    bp = new JPanel(new GridLayout(1,3));
    bp.add(btUpdate);
    bp.add(btImport);
    bp.add(btExit);
    bp.setBorder(new EmptyBorder(10,0,0,0));
    
    lp = new JPanel(new GridBagLayout());
    rp = new JPanel(new GridBagLayout());
    
    lp.add(new JLabel(rr.getString("userid"), JLabel.LEFT), AwtUtil.getConstraints(0,0,0,0,1,1,false,false));
    lp.add(tfUserID, AwtUtil.getConstraints(1,0,1,0,1,1,true,false));
    lp.add(new JLabel(rr.getString("password"), JLabel.LEFT), AwtUtil.getConstraints(0,1,0,0,1,1,false,false));
    lp.add(tfPassword, AwtUtil.getConstraints(1,1,1,0,1,1,true,false));
    lp.setBorder(new EmptyBorder(0,0,0,5));

    rp.add(btAccounts, AwtUtil.getConstraints(0,0,0,0,1,1,false,false));
    rp.add(cbAccounts, AwtUtil.getConstraints(1,0,1,0,1,1,true,false));
    rp.setBorder(new EmptyBorder(0,5,0,0));

    mp.add(lp, AwtUtil.getConstraints(0,0,1,0,1,1,true,false));
    mp.add(rp, AwtUtil.getConstraints(1,0,1,0,1,1,true,false));
    mp.add(new JLabel(" "), AwtUtil.getConstraints(0,1,1,1,2,1,true,true));
    mp.add(chbNew, AwtUtil.getConstraints(0,2,1,0,2,1,false,false));
    mp.add(bp, AwtUtil.getConstraints(0,3,1,0,2,1,false,false));

    getContentPane().add(mp);
    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);
    pack();
    setSize(480, 240);
    AwtUtil.centerWindow(this);
  }

  public void loadPayPalAccounts(Account acct) {
    for(int i=0; i<acct.getSubAccountCount(); i++) {
      Account subAcct = acct.getSubAccount(i);
      int acctType = subAcct.getAccountType();
      String paypalID = subAcct.getParameter("paypal_id");
      if((acctType==Account.ACCOUNT_TYPE_BANK)&&(paypalID!=null)) {
        cbAccounts.addItem(subAcct);
      }
      loadPayPalAccounts(subAcct);
    }
  }

  public void setUserID() {
    if (cbAccounts.getSelectedIndex()>=0) {
      ca = (Account)cbAccounts.getSelectedItem();
      tfUserID.setText(ca.getParameter("paypal_id"));
      btUpdate.setEnabled(true);
      btImport.setEnabled(true);
    } else {
      tfUserID.setText("");
      btUpdate.setEnabled(false);
      btImport.setEnabled(false);
    }
  }

  public void removeAllPayPalAccounts() {
    while(cbAccounts.getItemCount()>0) {
      cbAccounts.removeItemAt(0);
    }
    firePayPalAccountsChanged();
  }

  public void removeAllAccounts() {
    lmAcct.removeAllElements();
  }

  public void loadAccounts(Account acct) {
    for(int i=0; i<acct.getSubAccountCount(); i++) {
      Account subAcct = acct.getSubAccount(i);
      int acctType = subAcct.getAccountType();
      if(acctType==Account.ACCOUNT_TYPE_BANK) {
        lmAcct.addElement(subAcct);
      }
      loadAccounts(subAcct);
    }
  }

  private boolean cbContains(JComboBox cb, Object o) {
    for (int i=0; i<cb.getItemCount();i++) {
      if (cb.getItemAt(i).equals(o)) return true;
    }
    return false;
  }

  public final void processEvent(AWTEvent evt) {
    if(evt.getID()==WindowEvent.WINDOW_CLOSING) {
      extension.closePayPalWindow();
      return;
    }
    super.processEvent(evt);
  }

  private void firePayPalAccountsChanged() {
    setUserID();
  }

  private void updateBtns(Object o) {
    Object ob = listAcct.getSelectedValue();
    btAdd.setEnabled(!cbContains(cbAccounts, ob) && tfNewUserID.getText().trim().length()>0);
    btRemove.setEnabled(cbContains(cbAccounts, ob));
  }

  public void changedUpdate(DocumentEvent e) {
    Object o = e.getDocument();
    if (o.equals(tfNewUserID.getDocument())) {
      updateBtns(o);
      return;
    }
  }

  public void insertUpdate(DocumentEvent e) {
    Object o = e.getDocument();
    if (o.equals(tfNewUserID.getDocument())) {
      updateBtns(o);
      return;
    }
  }

  public void removeUpdate(DocumentEvent e) {
    Object o = e.getDocument();
    if (o.equals(tfNewUserID.getDocument())) {
      updateBtns(o);
      return;
    }
  }

  public void actionPerformed(ActionEvent e) {
    Object o = e.getSource();
    if (o.equals(btExit)) {
      extension.closePayPalWindow();
      return;
    }
    if (o.equals(cbAccounts)) {
      firePayPalAccountsChanged();
      return;
    }
    if (o.equals(btAccounts)) {
      OnAccounts();
      return;
    }
    if (o.equals(btCancel)) {
      dlgAcct.setVisible(false);
      dlgAcct = null;
      return;
    }
    if (o.equals(btAdd)) {
      if (!listAcct.isSelectionEmpty()) {
        Account a = (Account)listAcct.getSelectedValue();
        if (!cbContains(cbAccounts, a)) {
          if ((tfNewUserID != null)&&(tfNewUserID.getText().length()>0)) {
            cbAccounts.addItem(a);
            a.setParameter("paypal_id", tfNewUserID.getText());
            firePayPalAccountsChanged();
          }
        }
      }
      dlgAcct.setVisible(false);
      dlgAcct = null;
      return;
    }
    if (o.equals(btRemove)) {
      if (!listAcct.isSelectionEmpty()) {
        Account a = (Account)listAcct.getSelectedValue();
        if (cbContains(cbAccounts, a)) {
          cbAccounts.removeItem(a);
          a.setParameter("paypal_id", null);
          a.setParameter("paypal_dldate", null);
          firePayPalAccountsChanged();
        }
      }
      dlgAcct.setVisible(false);
      dlgAcct = null;
      return;
    }
    if (o.equals(btUpdate)) {
      OnUpdate(true);
      return;
    }
    if (o.equals(btImport)) {
      OnUpdate(false);
      return;
    }
    if (o.equals(btAccept)) {
      int selRow = tableTxns.getSelectedRow();
      OnAccept(selRow);
      txns.removeElementAt(selRow);
      tmTxns.fireTableRowsDeleted(selRow, selRow);
      btAccept.setEnabled(false);
      return;
    }
    if (o.equals(btMerge)) {
      for (int i=0;i<tableTxns.getRowCount();i++) OnAccept(i);
      txns.removeAllElements();
      tmTxns.fireTableDataChanged();
      btAccept.setEnabled(false);
      btMerge.setEnabled(false);
      return;
    }
    if (o.equals(btExit1)) {
      dlgTxns.setVisible(false);
      dlgTxns = null;
      return;
    }
  }

  public void valueChanged(ListSelectionEvent e) {
    ListSelectionModel lsm = (ListSelectionModel)e.getSource();
    if (lsm==lsmAcct) {
      tfNewUserID.setEnabled(true);
      Object o = listAcct.getSelectedValue();
      btAdd.setEnabled(!cbContains(cbAccounts, o) && tfNewUserID.getText().trim().length()>0);
      btRemove.setEnabled(cbContains(cbAccounts, o));
      return;
    }
    if (lsm==lsmTxns) {
      btAccept.setEnabled(true);
    }
  }

  private void OnAccept(int row) {
    CSVLine csv = (CSVLine)txns.elementAt(row);
    Calendar cal = Calendar.getInstance();
    cal.setTime(fmt.parse(csv.getStr(PAYPAL_DATE)));
    cal.set(Calendar.HOUR_OF_DAY,12);
    cal.set(Calendar.MINUTE,0);
    cal.set(Calendar.SECOND,0);
    cal.set(Calendar.MILLISECOND,0);

    ParentTxn ptxn = new ParentTxn(cal.getTime().getTime(), cal.getTime().getTime(), 
      System.currentTimeMillis(), "", ca, csv.getStr(PAYPAL_NAME), csv.getStr(PAYPAL_SUBJ), 
      -1, AbstractTxn.STATUS_CLEARED);
      
    long gross = ca.getCurrencyType().parse(csv.getStr(PAYPAL_GROSS),'.');
    long fee = ca.getCurrencyType().parse(csv.getStr(PAYPAL_FEE),'.');
    int acctType = gross<0 ? Account.ACCOUNT_TYPE_EXPENSE : Account.ACCOUNT_TYPE_INCOME;
    Account category = null;
    ParentTxn ttxn = null;

    ttxn = ts.findBestMatch(csv.getStr(PAYPAL_NAME), gross+fee, ca);
    if (ttxn == null) {
      for(Enumeration subs = root.getSubAccounts(); subs.hasMoreElements(); ) {
        Account ac = (Account)subs.nextElement();
        if (ac.getAccountType() == acctType) {
          category = ac;
          break;
        }
      }
    } else {
      category = ttxn.getSplit(0).getAccount();
      // finding exact match by date, amount and account
      AbstractTxn atxn;
      atxn = findMatch(cal.getTime().getTime(), gross+fee, ca);
      if (atxn != null) {
        // transaction already exist
        atxn.setTag("paypal_email", csv.getStr(PAYPAL_EMAIL));
        atxn.setTag("paypal_tid", csv.getStr(PAYPAL_TID));
        atxn.setTag("paypal_item", csv.getStr(PAYPAL_ITEM));
        return;
      }
    }

    ptxn.addSplit(new SplitTxn(ptxn,gross,1.0,category,"",-1,AbstractTxn.STATUS_CLEARED));
    // PayPal transactions are specific, they often containt 2 splits (second is fee) 
    // and never more than 2 splits
    if (fee != 0) {
      if (ttxn == null) {
        for(Enumeration subs = root.getSubAccounts(); subs.hasMoreElements(); ) {
          Account ac = (Account)subs.nextElement();
          if (ac.getAccountType() == Account.ACCOUNT_TYPE_EXPENSE) {
            category = ac;
            break;
          }
        }
      } else {
        category = ttxn.getSplit(ttxn.getSplitCount()-1).getAccount();
      }
      ptxn.addSplit(new SplitTxn(ptxn,fee,1.0,category,"",-1,AbstractTxn.STATUS_CLEARED));
    }
    ptxn.setTag("paypal_email", csv.getStr(PAYPAL_EMAIL));
    ptxn.setTag("paypal_tid", csv.getStr(PAYPAL_TID));
    ptxn.setTag("paypal_item", csv.getStr(PAYPAL_ITEM));
      
    ts.addNewTxn(ptxn);
  }

  private void OnAccounts() {
    if (dlgAcct==null) {
      dlgAcct = new JDialog((JFrame)null, rr.getString("select_account"), true);
      lsmAcct = listAcct.getSelectionModel();
      lsmAcct.addListSelectionListener(this);
      listAcct.setModel(lmAcct);
      JScrollPane spAcct = new JScrollPane(listAcct);
      JPanel mainPanel = new JPanel(new GridBagLayout());
      mainPanel.setBorder(new EmptyBorder(10,10,10,10));
      btAdd = new JButton(rr.getString("add"));
      btAdd.addActionListener(this);
      btAdd.setEnabled(false);
      btRemove = new JButton(rr.getString("remove"));
      btRemove.addActionListener(this);
      btRemove.setEnabled(false);
      btCancel = new JButton(rr.getString("cancel"));
      btCancel.addActionListener(this);
      btCancel.setEnabled(true);
      btCancel.registerKeyboardAction(this, "cancel",
                                      KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
                                      JComponent.WHEN_IN_FOCUSED_WINDOW);
      JTextArea ta = new JTextArea(10,3);
      ta.setText(rr.getString("if_no"));
      ta.setLineWrap(true);
      ta.setEditable(false);
      ta.setBorder(new EmptyBorder(0,0,5,0));
      ta.setBackground(btAdd.getBackground());
      mainPanel.add(ta, AwtUtil.getConstraints(0,0,1,0,2,1,true,true));
      mainPanel.add(spAcct, AwtUtil.getConstraints(0,1,1,1,1,1,true,true));
      JPanel btnp = new JPanel(new GridLayout(3,1));
      btnp.add(btAdd);
      btnp.add(btRemove);
      btnp.add(btCancel);
      btnp.setBorder(new EmptyBorder(0,10,0,0));
      mainPanel.add(btnp, AwtUtil.getConstraints(1,1,0,1,1,1,true,false));
      idp = new JPanel(new GridBagLayout());
      idp.add(new JLabel(rr.getString("paypal_id")), AwtUtil.getConstraints(0,0,0,0,1,1,false,false));
      tfNewUserID = new JTextField(10);
      tfNewUserID.getDocument().addDocumentListener(this);
      idp.add(tfNewUserID, AwtUtil.getConstraints(1,0,1,0,1,1,true,false));
      mainPanel.add(idp, AwtUtil.getConstraints(0,2,1,0,1,1,true,false));
      tfNewUserID.setEnabled(false);
      dlgAcct.getContentPane().add(mainPanel);
      dlgAcct.setSize(getSize().width, getSize().height);
      dlgAcct.setLocation(getLocation().x, getLocation().y);
      AwtUtil.centerWindow(dlgAcct);
    }
    dlgAcct.setVisible(true);
  }

  private byte[] getBytes(String str) {
    try {
      return str.getBytes("UTF8");
    } catch (Throwable t) {
      System.err.println("Error: "+t);
    }
    return str.getBytes();
  }

  private Task updateTask = new Task() {
      public void performTask() throws Exception {
        PayPalSession();
      }
    };

  private  class PPSession {
    Socket socket = null;
    InputStream in = null;
    OutputStream out = null;
    String host = "www.paypal.com";
    String line = null;
    String redirectLink = null;
    int port = 443;
    Hashtable cookies = null;
    HttpsHelper2 httpsHelper = null;
    BufferedReader rdr = null;
    Vector resp = new Vector();

    PPSession(Hashtable cookies) {
      this.cookies = cookies;
      httpsHelper = new HttpsHelper2();
      try { 
        httpsHelper.init(extension.getAppMain());
      } catch(Exception e) {}
    }

    public void storeCookie(String s) {
      int i = s.indexOf('=');
      String key = s.substring(0, i);
      if (i==-1) return;
      cookies.remove(key);
      cookies.put(key, s.substring(i+1, s.indexOf(';')));
    }

    public boolean isError() {
      String s;
      for (int i=0;i<resp.size();i++) {
        s = ((CSVLine)resp.elementAt(i)).getCSV();
        if (s.indexOf("<!-- begin error -->")>=0) return true;
      }
      return false;
    }

    public void GET(String url) {
      GET(url, false);
    }

    public void GET(String url, boolean output) {
      redirectLink = null;
      StringBuffer sb = new StringBuffer();
      boolean first = true;
      try {
        socket = httpsHelper.getSSLSocket(host, port);
        in = socket.getInputStream();
        out = socket.getOutputStream();
        String getstr = "GET "+url+" HTTP/1.1\n";
        sb.append(getstr);
        sb.append(AGENT_HOST);
        for(Enumeration cookieNames=cookies.keys(); cookieNames.hasMoreElements();) {
          Object cookieName = cookieNames.nextElement();
          if (first) {
            sb.append("Cookie: ");
            first = false;
          }
          sb.append(cookieName+"="+cookies.get(cookieName)+"; ");
        }
        if (!first) sb.append("\n"); // cookies present
        sb.append("\n");
        out.write(sb.toString().getBytes("UTF8"));
        rdr = new BufferedReader(new InputStreamReader(in, "UTF8"));
        boolean hdr = true;
        resp.clear();
        while(true) {
          line = rdr.readLine();
          if(line==null) break;
          if (line.length()==0) {
            hdr = false;
            continue;
          }
          if (!hdr) resp.addElement(new CSVLine(line));
          if (!hdr && output) System.out.println(line);
          if (line.startsWith("Location:")) {
            redirectLink = line.substring(10);
          }
          if (line.startsWith("Refresh:")) {
            redirectLink = line.substring(line.indexOf("URL=")+4);
          }
          if (line.startsWith("Set-Cookie:")) storeCookie(line.substring(12));
        }
      } catch(Exception exc) {
        exc.printStackTrace(System.out);
      } finally {
        if(socket!=null) try { socket.close(); } catch (Throwable t) {}
        if(out!=null) try { out.close(); } catch (Throwable t) {}
        if(in!=null) try { in.close(); } catch (Throwable t) {}
      }
      if (redirectLink!=null) GET(redirectLink, output);
    }

    public void POST(String url, String msg) {
      POST(url, msg, false, 0);
    }

    public void POST(String url, String msg, boolean output) {
      POST(url, msg, output, 0);
    }

    public void POST(String url, String msg, int mode) {
      POST(url, msg, false, mode);
    }

    public void POST(String url, String msg, boolean output, int mode) {
      redirectLink = null;
      StringBuffer sb = new StringBuffer();
      boolean first = true;
      try {
        socket = httpsHelper.getSSLSocket(host, port);
        in = socket.getInputStream();
        out = socket.getOutputStream();
        String getstr = "POST "+url+" HTTP/1.1\n";
        sb.append(getstr);
        sb.append(AGENT_HOST);
        sb.append("Accept-Language: en\n");
        sb.append("Accept: */*\n");
        sb.append("Content-Length: "+msg.length()+"\n");
        sb.append("Content-Type: application/x-www-form-urlencoded\n");
        sb.append("Pragma: no-cache\n");
        for(Enumeration cookieNames=cookies.keys(); cookieNames.hasMoreElements();) {
          Object cookieName = cookieNames.nextElement();
          if (first) {
            sb.append("Cookie: ");
            first = false;
          }
          sb.append(cookieName+"="+cookies.get(cookieName)+"; ");
        }
        if (!first) sb.append("\n"); // cookies present
        sb.append("\n");
        sb.append(msg);
        out.write(sb.toString().getBytes("UTF8"));
        
        rdr = new BufferedReader(new InputStreamReader(in, "UTF8"));
        boolean hdr = true;
        resp.clear();
        String prevline = null;
        while(true) {
          line = rdr.readLine();
          if(line==null) break;
          if (line.length()==0) {
            hdr = false;
            continue;
          }
          if (line.startsWith("Location:")) {
            redirectLink = line.substring(10);
          }
          if (line.startsWith("Refresh:")) {
            redirectLink = line.substring(line.indexOf("URL=")+4);
          }
          if (line.startsWith("Set-Cookie:")) storeCookie(line.substring(12));
          if (!hdr && output) System.out.println(line);
          if (!hdr) {
            if (mode==0) {
              resp.addElement(new CSVLine(line));
            } else {
              if (!line.startsWith("\"")) continue;
              if (elementsInString(line)==PP_ITEMS) {
                resp.addElement(new CSVLine(line));
              } else {
                if (prevline==null) {
                  prevline = new String(line);
                } else {
                  prevline = prevline + line;
                }
                if (elementsInString(prevline)==PP_ITEMS) {
                  resp.addElement(new CSVLine(prevline));
                  prevline = null;
                }
              }
            }
          }
        }
      } catch(Exception exc) {
        exc.printStackTrace(System.out);
      } finally {
        if(socket!=null) try { socket.close(); } catch (Throwable t) {}
        if(out!=null) try { out.close(); } catch (Throwable t) {}
        if(in!=null) try { in.close(); } catch (Throwable t) {}
      }
      if (redirectLink!=null) GET(redirectLink, output);
    }
  }

  private int elementsInString(String s) {
    int i=0, j=0, k;
    if (s==null) return 0;
    if (s.length()<2) return 0;
    while(i<s.length()) {
      k = s.indexOf("\"", i);
      if (k!=-1) {
        j++;
        i = k+1;
      } 
      else break;
    }
    return j/2;
  }

  private void PayPalSession() {
    setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
    cookies.clear();
    PPSession ss = new PPSession(cookies);

    Account ca  = (Account)cbAccounts.getSelectedItem();
    String dateRange, dldate = null;
    dldate = ca.getParameter("paypal_dldate");
    if (dldate==null) {
      dateRange = "&from_a=&from_b=&from_c=&to_a=&to_b=&to_c=&range=all";
    } else {
      if (chbNew.isSelected()) {
        Calendar today = Calendar.getInstance();
        Calendar past = Calendar.getInstance();
        past.setTime(fmt.parse(dldate));
        dateRange = 
          "&from_a="+(1+past.get(Calendar.MONTH))+
          "&from_b="+past.get(Calendar.DAY_OF_MONTH)+
          "&from_c="+past.get(Calendar.YEAR)+
          "&to_a="+(1+today.get(Calendar.MONTH))+
          "&to_b="+today.get(Calendar.DAY_OF_MONTH)+
          "&to_c="+today.get(Calendar.YEAR)+
          "&range=date";
      } else {
        dateRange = "&from_a=&from_b=&from_c=&to_a=&to_b=&to_c=&range=all";
      }
    }

    waitWindow.setLabel(rr.getString("connecting"));
    ss.GET(SPAYPAL+PAYPAL_GET_MAIN);
    String pwd = new String(tfPassword.getPassword());
    String postMsg = "cmd=_login-submit&login_email="+tfUserID.getText()+"&login_password="+pwd;
    waitWindow.setLabel(rr.getString("logging_in"));
    ss.POST(SPAYPAL+PAYPAL_POST_LOGIN, postMsg);
    if (ss.isError()) {
      setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
      JOptionPane.
        showMessageDialog(null, 
                          rr.getString("login_error"),
                          rr.getString("error"), 
                          JOptionPane.ERROR_MESSAGE);
      return;
    }
    ss.GET(SPAYPAL+PAYPAL_GET_HISTORY_DOWNLOAD);
    postMsg = "cmd=_history-download-submit&history_cache="+dateRange+"&type=excel&all_activity_comma=all_activity&submit.x=Download%20History";
    waitWindow.setLabel(rr.getString("downloading"));
    ss.POST(SPAYPAL+PAYPAL_POST_DOWNLOAD, postMsg, 1);
    if (ss.isError()) {
      setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
      JOptionPane.
        showMessageDialog(null, 
                          rr.getString("login_error"),
                          rr.getString("error"), 
                          JOptionPane.ERROR_MESSAGE);
      return;
    }
    txns = (Vector)ss.resp.clone();
    ss.resp.clear();
    waitWindow.setLabel(rr.getString("logging_out"));
    ss.GET(PAYPAL+PAYPAL_GET_LOGOUT);
    setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
  }

  private void OnUpdate(boolean online) {
    txns = null;
    if (online) {
      waitWindow = new WaitWindow(this);
      try {
        waitWindow.invokeTask(updateTask, rr.getString("initializing"));
      } catch(Throwable t) {
        setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
        JOptionPane.
          showMessageDialog(null, 
                            rr.getString("error_connect"),
                            rr.getString("error"), 
                            JOptionPane.ERROR_MESSAGE);
        return;
      }
      waitWindow = null;
    } else {
      try {
        FileDialog fch = new FileDialog(AwtUtil.getFrame(this), rr.getString("choose_file"));
        fch.setVisible(true);
        String file = fch.getFile();
        String dir = fch.getDirectory();
        if(file==null || dir==null)
          return;
        if(!dir.endsWith(File.separator))
          dir = dir+File.separator;
        BufferedReader in = new BufferedReader(new FileReader(dir+file));
        String line;
        txns = new Vector();
        while(true) {
          line = in.readLine();
          if (line==null) break;
          if(line.trim().length()<=0) continue;
          if (line.startsWith("\"")) txns.addElement(new CSVLine(line));
        }
        in.close();
      } catch(Exception exc) {}
    }
    if (txns == null) return;
    ca.setParameter("paypal_dldate", fmt.format(Calendar.getInstance()));
    ts = root.getTransactionSet();
    tset = ts.getTransactionsForAccount(ca);
    int i,j;
    String tid = null;
    AbstractTxn atxn;
    i = 0;
    boolean tid_match;
    while(true) {
      if (txns.size()==0) break;
      if (i>(txns.size()-1)) break;
      CSVLine csv = (CSVLine)txns.elementAt(i);
      if ((!csv.getStr(4).equals("Completed"))&&(!csv.getStr(4).equals("Reversed"))) {
        txns.removeElementAt(i);
        continue;
      }
      tid = csv.getStr(PAYPAL_TID);
      tid_match = false;
      for (j=0; j<tset.getSize();j++) {
        atxn = tset.getTxnAt(j);
        if (atxn.getTag("paypal_tid", ".").equals(tid)) {
          txns.removeElementAt(i);
          tid_match = true;
          break;
        }
      }
      if (!tid_match) i++;
    }

    dlgTxns = new JDialog((JFrame)null, rr.getString("select_account"), true);
    tmTxns = new PayPalTableModel();
    tableTxns = new JTable(tmTxns);
    lsmTxns = tableTxns.getSelectionModel();
    lsmTxns.addListSelectionListener(this);
    TableColumnModel colMod = tableTxns.getColumnModel();
    colMod.getColumn(0).setPreferredWidth(50);
    colMod.getColumn(1).setPreferredWidth(250);
    colMod.getColumn(2).setPreferredWidth(50);

    JScrollPane spTxns = new JScrollPane(tableTxns);
    JPanel mainPanel = new JPanel(new GridBagLayout());
    mainPanel.setBorder(new EmptyBorder(10,10,10,10));
    btAccept = new JButton(rr.getString("accept"));
    btAccept.addActionListener(this);
    btAccept.setEnabled(false);
    btMerge = new JButton(rr.getString("merge"));
    btMerge.addActionListener(this);
    btExit1 = new JButton(rr.getString("exit"));
    btExit1.addActionListener(this);
    btExit1.registerKeyboardAction(this, "cancel",
                                   KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
                                   JComponent.WHEN_IN_FOCUSED_WINDOW);
    mainPanel.add(spTxns, AwtUtil.getConstraints(0,0,1,1,1,1,true,true));

    JPanel btnp = new JPanel(new GridBagLayout());
    btnp.add(btAccept, AwtUtil.getConstraints(0,0,1,0,1,1,true,false));
    btnp.add(btMerge, AwtUtil.getConstraints(0,1,1,0,1,1,true,false));
    btnp.add(new JLabel(" "), AwtUtil.getConstraints(0,2,1,1,1,1,true,true));
    btnp.add(btExit1, AwtUtil.getConstraints(0,3,1,0,1,1,true,false));
    btnp.setBorder(new EmptyBorder(0,10,0,0));

    mainPanel.add(btnp, AwtUtil.getConstraints(1,0,0,1,1,1,true,false));
    dlgTxns.getContentPane().add(mainPanel);
    dlgTxns.setSize(getSize().width+120, getSize().height+40);
    dlgTxns.setLocation(getLocation().x-60, getLocation().y-20);
    AwtUtil.centerWindow(dlgTxns); 
    dlgTxns.setVisible(true);
  }
  
  private class CSVLine {
    String csv;
    
    CSVLine(String s) {
      this.csv = s;
    }
    
    String getStr(int num) {
      int j1 = 0, j2 = csv.indexOf("\",")+2;
      for (int i=0;i<num;i++) {
        j1 = csv.indexOf("\",", j1)+2;
        j2 = csv.indexOf("\",", j2)+2;
      }
      return csv.substring(j1+1,j2-2);
    }
    
    public String getCSV() {
      return this.csv;
    }
  }

  private static final String columns[] = { "Date", "Name", "Amount" };

  private class PayPalTableModel
    extends AbstractTableModel
  {
    
    public int getColumnCount() {
      return columns.length;
    }

    public Class getColumnClass(int column) {
      switch(column) {
        case 2: return Number.class;
        default: return String.class;
      }
    }

    public String getColumnName(int column) {
      switch(column) {
        case 0: 
        case 1: 
        case 2: return columns[column];
        default: return "";
      }
    }
    
    public synchronized int getRowCount() {
      return txns == null ? 0 : txns.size();
    }

    public Object getValueAt(int row, int column) {
      if (row>=getRowCount()) return null;
      CSVLine item = (CSVLine)txns.elementAt(row);
      switch(column) {
        case 0:
          return fmt.format(fmt.parse(item.getStr(0)));
        case 1:
          return item.getStr(2);
        case 2:
        default:
          return item.getStr(8);
      }
    }
    
    public boolean isCellEditable(int row, int column) {
      return false;
    }
  }

  private AbstractTxn findMatch(long date, long amount, Account acct) {
    if (acct == null) return null;
    synchronized(root) {
      AbstractTxn match = null;

      for(int i=tset.getSize()-1; i>=0; i--) {
        AbstractTxn txn = tset.getTxnAt(i);
        if (txn.getAccount()!=acct) continue;
        if (txn.getDate()!=date) continue;
        if (txn.getValue()!=amount) continue;
        match = txn;
      }
      return match;
    }
  }

}
