/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.txfexport;

import com.moneydance.apps.md.model.*;
import com.moneydance.apps.md.controller.*;
import com.moneydance.util.*;
import com.moneydance.awt.*;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;
import javax.swing.border.*;
import java.io.*;
import java.util.*;
import java.net.*;
import java.text.*;

public class TXFExport
  extends JDialog 
  implements ActionListener,
             ListSelectionListener
{
  private Main mainObject;
  private Resources rr;
  private RootAccount root;
  private JPanel mp, tp, fp, bp;
  private JPanel smp, slrp, slp, srp, sbp;
  private Vector txfVector;
  private FeatureModuleContext context;
  private JDialog setupDlg;

  private JList listAcct = new JList();
  private ListSelectionModel lsmAcct;
  private DefaultListModel lmAcct = new DefaultListModel();
  private JList listCat = new JList();
  private ListSelectionModel lsmCat;
  private DefaultListModel lmCat = new DefaultListModel();

  private JButton btSetup, btExport, btCancel, btBrowse, btDone, btClear;
  private JTextField tfFile = new JTextField(5);
  private JDateField dateStart, dateEnd;
  private JTextPanel desc, setup_desc;
  private GridBagLayout gbl = new GridBagLayout();
  private StreamTable txf = null;
  private StreamTable txfList = new StreamTable();
  private Font nf,bf,bf2;
  private InputStream in;
  
  public TXFExport(Main mainObject, FeatureModuleContext context) {
    super((Frame)null, "TXFExport", true);
    this.mainObject = mainObject;
    this.context = context;
    rr = mainObject.getResources();
    root = mainObject.getRoot();
    
    mp = new JPanel(gbl);
    mp.setBorder(new EmptyBorder(10,10,10,10));
    bf2 = new Font(mp.getFont().getFontName(), Font.BOLD, mp.getFont().getSize()+2);
    bf = new Font(mp.getFont().getFontName(), Font.BOLD, mp.getFont().getSize());
    nf = new Font(mp.getFont().getFontName(), Font.PLAIN, mp.getFont().getSize());
    
    desc = new JTextPanel(rr.getString("main_desc"));
    com.moneydance.apps.md.controller.Main ctxt =
        (com.moneydance.apps.md.controller.Main)context;
    dateStart = new JDateField(ctxt.getPreferences().getShortDateFormatter());
    dateStart.gotoFirstDayInYear();
    dateEnd = new JDateField(ctxt.getPreferences().getShortDateFormatter());
    dateEnd.gotoToday();

    btCancel = new JButton(rr.getString("cancel"));
    btCancel.addActionListener(this);
    btExport = new JButton(rr.getString("export"));
    btExport.addActionListener(this);
    btBrowse = new JButton(rr.getString("browse"));
    btBrowse.addActionListener(this);
    btSetup = new JButton(rr.getString("setup"));
    btSetup.addActionListener(this);
    
    tp = new JPanel(gbl);
    fp = new JPanel(gbl);
    bp = new JPanel(gbl);
    
    int y = 0;
    int x = 0;
    tp.add(desc, AwtUtil.getConstraints(x,y++,1,1,5,1,true,false));
    tp.add(new JLabel(rr.getString("start_date"), JLabel.RIGHT),
      AwtUtil.getConstraints(x++,y,0,0,1,1,true,false));
    tp.add(dateStart, AwtUtil.getConstraints(x++,y,0,0,1,1,true,false));
    tp.add(new JLabel(" "), AwtUtil.getConstraints(x++,y,1,0,1,1,true,false));
    tp.add(new JLabel(rr.getString("end_date"), JLabel.RIGHT),
      AwtUtil.getConstraints(x++,y,0,0,1,1,true,false));
    tp.add(dateEnd, AwtUtil.getConstraints(x++,y++,0,0,1,1,true,false));
    tp.setBorder(new EmptyBorder(0,0,5,0));
    
    y = 0;
    fp.add(new JLabel(rr.getString("export_to"), JLabel.LEFT),
      AwtUtil.getConstraints(0,y++,1,0,2,1,true,false));
    fp.add(tfFile, AwtUtil.getConstraints(0,y,1,0,1,1,true,false));
    fp.add(btBrowse, AwtUtil.getConstraints(1,y++,0,0,1,1,true,false));
    fp.setBorder(new EmptyBorder(0,0,5,0));
    
    x = 0;
    bp.add(btSetup, AwtUtil.getConstraints(x++,0,0,0,1,1,true,false));
    bp.add(btExport, AwtUtil.getConstraints(x++,0,0,0,1,1,true,false));
    bp.add(btCancel, AwtUtil.getConstraints(x++,0,0,0,1,1,true,false));
    
    y = 0;
    mp.add(tp, AwtUtil.getConstraints(0,y++,1,0,1,1,true,false));
    mp.add(fp, AwtUtil.getConstraints(0,y++,1,1,1,1,true,false));
    mp.add(bp, AwtUtil.getConstraints(0,y++,1,0,1,1,true,false));

    getContentPane().add(mp);
    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);
    try { pack(); } catch (Exception e) {}
    Dimension sz = getPreferredSize();
    setSize(sz.width+50, sz.height+30);
    AwtUtil.centerWindow(this);
  }

  private void loadAccount(Account acct) {
    for(int i=0; i<acct.getSubAccountCount(); i++) {
      Account subAcct = acct.getSubAccount(i);
      int acctType = subAcct.getAccountType();
      if((acctType==Account.ACCOUNT_TYPE_EXPENSE) || 
        (acctType==Account.ACCOUNT_TYPE_INCOME)) {
        if (subAcct.toString().length()>0) 
          lmAcct.addElement(subAcct);
      }
      loadAccount(subAcct);
    }
  }

  public final void processEvent(AWTEvent evt) {
    if(evt.getID()==WindowEvent.WINDOW_CLOSING) {
      mainObject.closeTXFExport();
      return;
    }
    super.processEvent(evt);
  }

  public void actionPerformed(ActionEvent e) {
    Object o = e.getSource();
    if (o.equals(btCancel)) {
      mainObject.closeTXFExport();
    } else if (o.equals(btBrowse)) {
      FileDialog fch = new FileDialog(AwtUtil.getFrame(this));
      fch.setFile("moneydance.txf");
      fch.setMode(FileDialog.SAVE);
      fch.setVisible(true);
      String file = fch.getFile();
      String dir = fch.getDirectory();
      if(file==null || dir==null)
        return;
      if(!dir.endsWith(File.separator))
        dir = dir+File.separator;
      tfFile.setText(dir + file);
    } else if (o.equals(btExport)) {
      doExport();
      mainObject.closeTXFExport();
    } else if (o.equals(btSetup)) {
      doSetup();
    } else if (o.equals(btDone)) {
      setupDlg.dispose();
      System.gc();
    } else if (o.equals(btClear)) {
      if (!lsmAcct.isSelectionEmpty()) {
        Account a = (Account)listAcct.getSelectedValue();
        listCat.removeSelectionInterval(0, lmCat.getSize()-1);
        a.setTaxCategory(null);
      }
    }
  }

  public void valueChanged(ListSelectionEvent e) {
    ListSelectionModel lsm = (ListSelectionModel)e.getSource();
    if (lsm==lsmAcct && !lsmAcct.isSelectionEmpty()) {
      Account a = (Account)listAcct.getSelectedValue();
      String catStr = a.getTaxCategory();
      listCat.removeSelectionInterval(0, lmCat.getSize()-1);
      if (catStr!=null) {
        TaxItem ti = null;
        for (int i=0;i<lmCat.getSize();i++) {
          ti = (TaxItem)lmCat.elementAt(i);
          if (!ti.isForm && ti.getCat().equals(catStr)) {
            listCat.setSelectedValue((TaxItem)lmCat.elementAt(0), true);
            listCat.setSelectedValue(ti, true);
            break;
          }
        }
        
      }
    } else if (lsm==lsmCat && !lsmAcct.isSelectionEmpty()) {
      Account a = (Account)listAcct.getSelectedValue();
      TaxItem ti = (TaxItem)listCat.getSelectedValue();
      if (ti!=null && !ti.isForm) a.setTaxCategory(ti.getCat());
    }
  }

  private class TaxItem {
    private String taxForm;
    private String taxCat;
    private String taxName;
    public boolean isForm;
    
    TaxItem(String form, String cat, String name, boolean b) {
      taxForm = form;
      taxCat = cat;
      taxName = name;
      isForm = b;
    }
    
    public String toString() {
      if (isForm) return taxForm;
      else return "        "+taxName;
    }
    
    public String getForm() {return taxForm;}
    public String getCat() {return taxCat;}
    public String getName() {return taxName;}
  }

  private class TaxCatCellRenderer extends JLabel implements ListCellRenderer {
    public TaxCatCellRenderer() {
      setOpaque(true);
    }
    public Component getListCellRendererComponent(
        JList list, Object o, int index, boolean isSelected, boolean cellHasFocus) {

      setText(o.toString());
      TaxItem ti = (TaxItem)o;
      if (ti.isForm) {
        setFont(bf2);
        setBackground(Color.white);
        setForeground(Color.black);
      } else {
        setFont(nf);
        setBackground(isSelected ? Color.darkGray : Color.white);
        setForeground(isSelected ? Color.white : Color.black);
      }
      return this;
    }
  }

  private class AcctCellRenderer extends JLabel implements ListCellRenderer {
    public AcctCellRenderer() {
      setOpaque(true);
    }
    public Component getListCellRendererComponent(
        JList list, Object o, int index, boolean isSelected, boolean cellHasFocus) {

      setText(o.toString());
      Account acct = (Account)o;
      if (acct.getParentAccount() == root) setFont(bf);
      else setFont(nf);
      setBackground(isSelected ? Color.darkGray : Color.white);
      setForeground(isSelected ? Color.white : Color.black);
      return this;
    }
  }

  private class AccountRecord {
    Account account;
    Vector transactions;
    AccountRecord(Account a) {
      account = a;
      transactions = new Vector();
    }
    public void addTxn(SplitTxn s) {transactions.add(s);}
    public Account getAccount() {return account;}
  }

  private class AccountRecordVector extends Vector {
    public boolean contains(Account a) {
      for (int i=0;i<size();i++) {
        if (((AccountRecord)get(i)).getAccount() == a) return true;
      }
      return false;
    }
    public Object get(Account a) {
      for (int i=0;i<size();i++) {
        if (((AccountRecord)get(i)).getAccount() == a) return get(i);
      }
      return null;
    }
  }

  private class CategoryRecord {
    String taxCategory;
    AccountRecordVector accounts;
    CategoryRecord(String cat) {
      taxCategory = cat;
      accounts = new AccountRecordVector();
    }
    public void addAccount(AccountRecord ar) {accounts.add(ar);}
    public String getTaxC() {return taxCategory;}
  }

  private class CategoryRecordVector extends Vector {
    public boolean contains(String id) {
      for (int i=0;i<size();i++) {
        if (((CategoryRecord)get(i)).getTaxC().equals(id)) return true;
      }
      return false;
    }
    public Object get(String id) {
      for (int i=0;i<size();i++) {
        if (((CategoryRecord)get(i)).getTaxC().equals(id)) return get(i);
      }
      return null;
    }
  }

  private void doSetup() {
    try {
      in = getClass().getClassLoader().getResourceAsStream("/com/moneydance/modules/features/txfexport/taxlist.tab");
      if (in == null) {
        return; // !!! add infobox later !!!
      } else {
        txfList.readFrom(in);
        in.close();
      }
    } catch(Exception exc) {
      return; // !!! add infobox later !!!
    }

    setupDlg = new JDialog((Frame)null, rr.getString("setup_title"), true);
    smp = new JPanel(gbl); // setup main panel
    smp.setBorder(new EmptyBorder(10,10,10,10));
    slrp = new JPanel(new GridLayout(1,2));
    slp = new JPanel(gbl); // setup left panel
    slp.setBorder(new EmptyBorder(0,0,0,5));
    srp = new JPanel(gbl); // setup right panel
    srp.setBorder(new EmptyBorder(0,5,0,0));
    sbp = new JPanel(gbl); // setup button panel
    sbp.setBorder(new EmptyBorder(5,0,0,0));
    
    setup_desc = new JTextPanel(rr.getString("setup_desc"));
    lsmAcct = listAcct.getSelectionModel();
    lsmAcct.addListSelectionListener(this);
    listAcct.setModel(lmAcct);
    listAcct.setCellRenderer(new AcctCellRenderer());
    lmAcct.removeAllElements();
    loadAccount(root);
    JScrollPane spAcct = new JScrollPane(listAcct);
    slp.add(new JLabel(rr.getString("category")),
      AwtUtil.getConstraints(0,0,0,0,1,1,true,false));
    slp.add(spAcct,
      AwtUtil.getConstraints(0,1,1,1,1,1,true,true));

    String[] catList = txfList.getKeyArray();
    StringUtils.sortStringArray(catList);
    lsmCat = listCat.getSelectionModel();
    lsmCat.addListSelectionListener(this);
    listCat.setModel(lmCat);
    listCat.setCellRenderer(new TaxCatCellRenderer());
    lmCat.removeAllElements();
    TaxItem ti;
    StreamTable catListTable;
    String[] subCat = null;
    int i,j;
    for (i=0;i<catList.length;i++) {
      ti = new TaxItem(catList[i], null, null, true);
      lmCat.addElement(ti);
      catListTable = new StreamTable();
      catListTable = (StreamTable)txfList.get(catList[i]);
      subCat = catListTable.getKeyArray();
      StringUtils.sortStringArray(subCat);
      for (j=0;j<subCat.length;j++) {
        ti = new TaxItem(catList[i], subCat[j], (String)catListTable.get(subCat[j]), false);
        lmCat.addElement(ti);
      }
    }
    JScrollPane spCat = new JScrollPane(listCat);
    srp.add(new JLabel(rr.getString("tax_cat")),
      AwtUtil.getConstraints(0,0,0,0,1,1,true,false));
    srp.add(spCat,
      AwtUtil.getConstraints(0,1,1,1,1,1,true,true));
    
    btDone = new JButton(rr.getString("done"));
    btDone.addActionListener(this);
    btClear = new JButton(rr.getString("clear"));
    btClear.addActionListener(this);
    sbp.add(btDone, AwtUtil.getConstraints(0,0,0,0,1,1,false,false));
    sbp.add(btClear, AwtUtil.getConstraints(1,0,0,0,1,1,false,false));
    
    slrp.add(slp);
    slrp.add(srp);

    smp.add(setup_desc, AwtUtil.getConstraints(0,0,1,0,1,1,true,false));
    smp.add(slrp, AwtUtil.getConstraints(0,1,1,1,1,1,true,true));
    smp.add(sbp, AwtUtil.getConstraints(0,2,1,0,1,1,true,false));
    
    setupDlg.getContentPane().add(smp);
    setupDlg.pack();
    setupDlg.setSize(570,400);
    AwtUtil.centerWindow(setupDlg);
    setupDlg.setVisible(true);
  }
  
  private void doExport() {
    if (tfFile.getText().trim().length()==0) {
      FileDialog fch = new FileDialog(AwtUtil.getFrame(this));
      fch.setFile("moneydance.txf");
      fch.setMode(FileDialog.SAVE);
      fch.setVisible(true);
      String file = fch.getFile();
      String dir = fch.getDirectory();
      if(file==null || dir==null)
        return;
      if(!dir.endsWith(File.separator))
        dir = dir+File.separator;
      tfFile.setText(dir + file);
    }
    CategoryRecordVector categories = new CategoryRecordVector();
    TransactionSet ts = root.getTransactionSet();
    AbstractTxn txn;
    ParentTxn ptxn;
    SplitTxn stxn;
    CategoryRecord cr;
    AccountRecord ar;
    CurrencyType curr;

    if (txf == null) {
      txf = new StreamTable();
      InputStream in;
      try {
        in = getClass().getClassLoader().getResourceAsStream("/com/moneydance/modules/features/txfexport/tax.tab");
        if (in != null) {
          txf.readFrom(in);
          in.close();
        }
      } catch(Exception exc) {
        exc.printStackTrace(System.err);
        return;
      }
    }
    
    long sd = dateStart.getDate().getTime();
    long ed = dateEnd.getDate().getTime();
    String taxc;
    for(Enumeration txns=ts.getAllTransactions(); txns.hasMoreElements();) {
      txn = (AbstractTxn)txns.nextElement();
      if (txn.getClass() == SplitTxn.class) continue;
      ptxn = txn.getParentTxn();
      Account parentAcct = ptxn.getAccount();
      if ((ptxn.getDate()<sd)||(ptxn.getDate()>ed)) continue;
      for (int i=0;i<ptxn.getSplitCount();i++) {
        stxn = ptxn.getSplit(i);
        String type = stxn.getParentTxn().getTransferType();
        if(type.equals(AbstractTxn.TRANSFER_TYPE_BUYSELL)||
           type.equals(AbstractTxn.TRANSFER_TYPE_BUYSELLXFR)) {
          taxc = "673";
        } else {
          taxc = stxn.getAccount().getTaxCategory();
        }
        if (taxc == null) continue;
        if (!categories.contains(taxc)) {
          cr = new CategoryRecord(taxc);
          categories.add(cr);
        }
        else cr = (CategoryRecord)categories.get(taxc);
        if (!cr.accounts.contains(parentAcct)) {
          ar = new AccountRecord(parentAcct);
          cr.accounts.add(ar);
        }
        else ar = (AccountRecord)cr.accounts.get(parentAcct);
        ar.transactions.add(stxn);
      }
    }
    // all split txn are now in vector categories
    try {
      FileWriter tout = new FileWriter(tfFile.getText().trim());
      tout.write("V037\n");
      tout.write("AMoneydance\n");
      Calendar cal = Calendar.getInstance();
      cal.set(Calendar.HOUR_OF_DAY, 12);
      cal.set(Calendar.MINUTE, 0);
      cal.set(Calendar.SECOND, 0);
      cal.set(Calendar.MILLISECOND, 0);
      DateFormat shortDateFormat = new SimpleDateFormat("MM/dd/yyyy");
      tout.write("D"+shortDateFormat.format(cal.getTime())+"\n");
      tout.write("^\n");
      StreamTable taxCatRecord;
      int i,j,k;
      for (i=0;i<categories.size();i++) { // for all tax categories
        cr = (CategoryRecord)categories.elementAt(i);
        taxCatRecord = (StreamTable)txf.get(cr.getTaxC());
        if (taxCatRecord==null) continue;
        int fn = taxCatRecord.getInt("form_num", 0);
        for (j=0;j<cr.accounts.size();j++) { // for all accounts
          ar = (AccountRecord)cr.accounts.elementAt(j);
          curr = ar.getAccount().getCurrencyType();
          long summary = 0;
          for (k=0;k<ar.transactions.size();k++) { // for all txns
            txn = (AbstractTxn)ar.transactions.elementAt(k);
            summary += txn.getValue();
            switch(fn) {
              case 1:
                tout.write("TD\n");
                tout.write("N"+cr.getTaxC()+"\n");
                tout.write("C1\n");
                tout.write("L"+(j+1)+"\n");
                tout.write("$"+curr.formatSemiFancy(-1*txn.getValue(),'.')+"\n");
                tout.write("X"+shortDateFormat.format(new Date(txn.getDate()))+" "+
                              ar.getAccount().toString()+" "+
                              txn.getDescription()+"\n");
                tout.write("^\n");
                break;
              case 2:
                tout.write("TD\n");
                tout.write("N"+cr.getTaxC()+"\n");
                tout.write("C1\n");
                tout.write("L"+(j+1)+"\n");
                tout.write("P"+txn.getDescription()+"\n");
                tout.write("X"+shortDateFormat.format(new Date(txn.getDate()))+" "+
                              ar.getAccount().toString()+" "+
                              txn.getDescription()+"\n");
                tout.write("^\n");
                break;
              case 3:
                tout.write("TD\n");
                tout.write("N"+cr.getTaxC()+"\n");
                tout.write("C1\n");
                tout.write("L"+(j+1)+"\n");
                tout.write("$"+curr.formatSemiFancy(-1*txn.getValue(),'.')+"\n");
                tout.write("P"+txn.getDescription()+"\n");
                tout.write("X"+shortDateFormat.format(new Date(txn.getDate()))+" "+
                              ar.getAccount().toString()+" "+
                              txn.getDescription()+"\n");
                tout.write("^\n");
                break;
              case 4:
                if (txn.getAccount().getClass() == SecurityAccount.class) {
                  Vector v = getTXFInfo(txn);
                  if (v.size()>0) {
                    for (int ii=0;ii<v.size();ii++) {
                      Long[] sr = (Long[])(v.elementAt(ii));
                      if ((sr[2].longValue()==0) || (sr[3].longValue()==0))
                        continue;
                      tout.write("TD\n");
                      tout.write("N"+cr.getTaxC()+"\n");
                      tout.write("C1\n");
                      tout.write("L"+(j+1)+"\n");
                      tout.write("P"+txn.getAccount().getAccountName()+"\n");
                      tout.write("D"+shortDateFormat.format(new Date(sr[0].longValue()))+"\n");
                      tout.write("D"+shortDateFormat.format(new Date(sr[1].longValue()))+"\n");
                      tout.write("$"+curr.formatSemiFancy(sr[2].longValue(),'.')+"\n");
                      tout.write("$"+curr.formatSemiFancy(sr[3].longValue(),'.')+"\n");
                      tout.write("X"+shortDateFormat.format(new Date(txn.getDate()))+" "+
                                    ar.getAccount().toString()+" "+
                                    txn.getDescription()+"\n");
                      tout.write("^\n");
                    }
                  }                
                }
                break;
              case 6:
                tout.write("TD\n");
                tout.write("N"+cr.getTaxC()+"\n");
                tout.write("C1\n");
                tout.write("L"+(j+1)+"\n");
                tout.write("D"+shortDateFormat.format(new Date(txn.getDate()))+"\n");
                tout.write("$"+curr.formatSemiFancy(-1*txn.getValue(),'.')+"\n");
                tout.write("P"+txn.getDescription()+"\n"); // must be state initials
                tout.write("X"+shortDateFormat.format(new Date(txn.getDate()))+" "+
                              ar.getAccount().toString()+" "+
                              txn.getDescription()+"\n");
                tout.write("^\n");
                break;
            }
          }
          if ((fn!=4)&&(fn!=5)) {
            tout.write("TS\n");
            tout.write("N"+cr.getTaxC()+"\n");
            tout.write("C1\n");
            tout.write("L"+(j+1)+"\n");
            tout.write("$"+curr.formatSemiFancy(-1*summary,'.')+"\n");
            tout.write("^\n");
          }
        }
      }
      tout.close();
    } catch(IOException exc) {
      exc.printStackTrace(System.err);
    }
  }

  private boolean calculateTXFInfo(AbstractTxn atxn){
    CurrencyType curr = atxn.getAccount().getCurrencyType();
    txfVector = new Vector();
    Long[] longTerm = new Long[4];
    Long[] shortTerm = new Long[4];
    long stBuyDate = 0;
    long ltBuyDate = 0;
    
    long numShares = -1 * TxnUtil.getSecurityPart(atxn.getParentTxn()).getValue();
    long sellDate = atxn.getDate();
    Calendar c = Calendar.getInstance();
    c.setTime(new Date(sellDate));
    c.add(Calendar.YEAR, -1);
    c.add(Calendar.DATE, -1);
    long cutOffDate = c.getTime().getTime();
    
    String type = atxn.getParentTxn().getTransferType();
    if(type.equals(AbstractTxn.TRANSFER_TYPE_BUYSELL)||
       type.equals(AbstractTxn.TRANSFER_TYPE_BUYSELLXFR)){
      SplitTxn split = TxnUtil.getSecurityPart(atxn.getParentTxn());
      if(split.getAmount() > 0){
        SecurityAccount account = (SecurityAccount)split.getAccount();
        TransactionSet tSet = account.getRootAccount().getTransactionSet();
        TxnSet txnSet = tSet.getTransactionsForAccount(account);
        AccountUtil.sortTransactions(txnSet, AccountUtil.DATE);        
        if(account.getUsesAverageCost()){
          TxnSet validTxns = new TxnSet();
          TxnSet buySet = new TxnSet();
          TxnSet sellSet = new TxnSet();
          for(int i = 0; i < txnSet.getSize(); i++){
            AbstractTxn absTxn = txnSet.getTxn(i);
            String type1 = absTxn.getParentTxn().getTransferType();
            if((type1.equals(AbstractTxn.TRANSFER_TYPE_BUYSELL))||
               (type1.equals(AbstractTxn.TRANSFER_TYPE_BUYSELLXFR))||
               (type1.equals(AbstractTxn.TRANSFER_TYPE_DIVIDEND))){
              if((absTxn.getDate() <= atxn.getDate())&&(absTxn.getTxnId()!=atxn.getTxnId())){
                validTxns.addTxn(absTxn);
              }
            }
          }
          AccountUtil.sortTransactions(validTxns, AccountUtil.DATE);
          long totalCostBasis = 0;
          long shares = 0;
          double perShareCost = 0.0;
          long splitDate = 0;
          
          for(int j = 0; j < validTxns.getSize(); j++){
            AbstractTxn absTxn = validTxns.getTxn(j);
            if(splitDate==0){
              splitDate = absTxn.getDate();
            }
            SplitTxn splitTxn = TxnUtil.getSecurityPart(absTxn.getParentTxn());
            shares = curr.adjustValueForSplits(splitDate, shares, splitTxn.getDate());
            if(splitTxn.getAmount() < 0){
              SplitTxn commission = TxnUtil.getCommissionPart(absTxn.getParentTxn());
              totalCostBasis += (-1 * splitTxn.getAmount()) + (-1 * commission.getAmount());
              shares += splitTxn.getValue();
              buySet.addTxn(absTxn);
            } else if(splitTxn.getAmount() > 0){
              if(shares != 0){
                perShareCost = (double)totalCostBasis / shares;
                long costSold = Math.round((-1*splitTxn.getValue())*perShareCost);
                totalCostBasis -= costSold;
                shares += splitTxn.getValue();
                sellSet.addTxn(absTxn);
              }
            }
            splitDate = splitTxn.getDate();
          }
          shares = curr.adjustValueForSplits(splitDate, shares, sellDate);
          
          perShareCost = (double)totalCostBasis / shares;
          long thisCostBasis = Math.round(numShares * perShareCost);
          
          long sharesSold = 0;
          for(int l = 0; l < sellSet.getSize(); l++){
            SplitTxn sellTxn = TxnUtil.getSecurityPart(sellSet.getTxn(l).getParentTxn());
            sharesSold += Math.abs(curr.adjustValueForSplits(sellTxn.getDate(),
                                                             sellTxn.getValue(), sellDate));
          }

          boolean partial = false;
          long sharesBought = 0;
          long ltShares = 0;
          long stShares = 0;
          int index = 0;
          for(int k = 0; k < buySet.getSize() && sharesSold > 0; k++){
            SplitTxn buyTxn = TxnUtil.getSecurityPart(buySet.getTxn(k).getParentTxn());
            sharesBought = curr.adjustValueForSplits(buyTxn.getDate(),
                                                     buyTxn.getValue(), sellDate);
            if(sharesBought < sharesSold){
              sharesSold -= sharesBought;
            } else if(sharesBought == sharesSold){
              sharesSold = 0;
              index = k + 1;
            } else {
              partial = true;
              sharesBought -= sharesSold;
              index = k;
              sharesSold = 0;
            }
          }
          
          if(partial){
            SplitTxn buyTxn = TxnUtil.getSecurityPart(buySet.getTxn(index).getParentTxn());
            if(sharesBought > numShares){
              if(buyTxn.getDate() < cutOffDate){
                if(buyTxn.getDate() > ltBuyDate)
                  ltBuyDate = buyTxn.getDate();
                ltShares += numShares;
              } else {
                if((buyTxn.getDate() < stBuyDate)||(stBuyDate==0))
                  stBuyDate = buyTxn.getDate();
                stShares += numShares;
              }
              numShares = 0;
            } else {
              if(buyTxn.getDate() < cutOffDate){
                if(buyTxn.getDate() > ltBuyDate)
                  ltBuyDate = buyTxn.getDate();
                ltShares += sharesBought;
              } else {
                if((buyTxn.getDate() < stBuyDate)||(stBuyDate==0))
                  stBuyDate = buyTxn.getDate();
                stShares += sharesBought;
              }
              numShares -= sharesBought;
              index++;
            }
          }
          
          for (int m = index; m < buySet.getSize() && numShares > 0; m++){
            SplitTxn buyTxn = TxnUtil.getSecurityPart(buySet.getTxn(m).getParentTxn());
            long bShares = curr.adjustValueForSplits(buyTxn.getDate(),
                                                     buyTxn.getValue(), sellDate);
            if(bShares > numShares){
              if(buyTxn.getDate() < cutOffDate){
                if(buyTxn.getDate() > ltBuyDate)
                  ltBuyDate = buyTxn.getDate();
                ltShares += numShares;
              } else {
                if((buyTxn.getDate() < stBuyDate)||(stBuyDate==0))
                  stBuyDate = buyTxn.getDate();
                stShares += numShares;
              }
              numShares = 0;
            } else {
              if(buyTxn.getDate() < cutOffDate){
                if(buyTxn.getDate() > ltBuyDate)
                  ltBuyDate = buyTxn.getDate();
                ltShares += sharesBought;
              } else {
                if((buyTxn.getDate() < stBuyDate)||(stBuyDate==0))
                  stBuyDate = buyTxn.getDate();
                stShares += sharesBought;
              }
              numShares -= sharesBought;
            }
          }
          
          double ltRate = (double)ltShares / (ltShares + stShares);
          double stRate = (double)stShares / (ltShares + stShares);
          
          longTerm[0] = new Long(ltBuyDate);
          longTerm[1] = new Long(sellDate);
          longTerm[2] = new Long(Math.round(ltRate * thisCostBasis));
          longTerm[3] = new Long(Math.round(ltRate * InvestUtil.getPerShareSalesNet(atxn)));
          txfVector.addElement(longTerm);
          
          shortTerm[0] = new Long(stBuyDate);
          shortTerm[1] = new Long(sellDate);
          shortTerm[2] = new Long(Math.round(stRate * thisCostBasis));
          shortTerm[3] = new Long(Math.round(stRate * InvestUtil.getPerShareSalesNet(atxn)));
          txfVector.addElement(shortTerm);

          return true;  
        } else {
          long ltTotal = 0;
          long stTotal = 0;
          long ltShares = 0;
          long stShares = 0;
          
          Hashtable tag = TxnUtil.parseCostBasisTag(split);
          if(tag==null) return false;
          for(Enumeration e = tag.keys(); e.hasMoreElements();){
            String txnID = (String)e.nextElement();
            SplitTxn stxn = (SplitTxn)txnSet.getTxnByID(Long.parseLong(txnID));
            long shares = Long.parseLong((String)tag.get(txnID));
            SplitTxn commission = TxnUtil.getCommissionPart(stxn.getParentTxn());
            long commFees = 0;
            if(commission!=null){
              double commRate = (double)shares/Math.abs(curr.adjustValueForSplits(stxn.getDate(),
                                                                                  stxn.getValue(),
                                                                                  sellDate));
              commFees = Math.round(commRate * Math.abs(commission.getAmount()));
            }              
            if(stxn.getDate() < cutOffDate){
              ltTotal = ltTotal + Math.round(shares / curr.adjustRateForSplits(stxn.getDate(),
                                                                               stxn.getRate(),
                                                                               sellDate))
                + commFees;
              ltShares += shares;
              ltBuyDate = stxn.getDate();
            } else {
              stTotal = stTotal + Math.round(shares / curr.adjustRateForSplits(stxn.getDate(),
                                                                               stxn.getRate(),
                                                                               sellDate))
                + commFees;
              stShares += shares;
              if((stxn.getDate() < stBuyDate)||(stBuyDate==0))
                stBuyDate = stxn.getDate();
            }
          }
          long ltRate = Math.round((1.0 * ltShares) / numShares);
          longTerm[0] = new Long(ltBuyDate);
          longTerm[1] = new Long(sellDate);
          longTerm[2] = new Long(ltTotal);
          longTerm[3] = new Long(ltRate * InvestUtil.getPerShareSalesNet(atxn));
          txfVector.addElement(longTerm);
         
          long stRate = Math.round((1.0 * stShares) / numShares);
          shortTerm[0] = new Long(stBuyDate);
          shortTerm[1] = new Long(sellDate);
          shortTerm[2] = new Long(stTotal);
          shortTerm[3] = new Long(stRate * InvestUtil.getPerShareSalesNet(atxn));
          txfVector.addElement(shortTerm);
          
          return true;
        }
      }
    }
    return false;
  }

  public Vector getTXFInfo(AbstractTxn atxn){
    if(calculateTXFInfo(atxn))
      return txfVector;
    return new Vector();
  }

}
