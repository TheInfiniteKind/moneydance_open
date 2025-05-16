package com.moneydance.modules.features.mrbutil;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.io.ByteArrayOutputStream;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Vector;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.RowSorter;
import javax.swing.SortOrder;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableModel;
import javax.swing.table.TableRowSorter;

import com.infinitekind.moneydance.model.AbstractTxn;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.AccountUtil;
import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.ParentTxn;
import com.infinitekind.moneydance.model.TransactionSet;
import com.infinitekind.moneydance.model.Txn;
import com.infinitekind.moneydance.model.TxnSearch;
import com.infinitekind.moneydance.model.TxnSet;
import com.infinitekind.tiksync.SyncRecord;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.awt.GridC;
import com.infinitekind.util.CustomDateFormat;
/**
 *  Creates a view over specific transactions
 * @author Mike Bray
 *
 */
public class MRBViewTransactions implements TxnSearch {
	private MRBTranTable trantable;
	MRBTranModel tranmodel;
	private boolean bAllTrans;
	private AccountBook objAcctBook;
	private TransactionSet  txnSet;
    private TxnSet tsTrans;
    private Account objAcct;
	private int iStartDate;
	private int iEndDate;
	private boolean bRollup;
	/*
	 * Preferences
	 */
	private MRBPreferences2 preferences;
	private int iSCREENWIDTH = MRBConstants.TRANSCREENWIDTH;
	private int iSCREENDEPTH = MRBConstants.TRANSCREENDEPTH;
	private int iSCROLLDEPTH;
	private int iSCROLLWIDTH;
	private int iTOPDEPTH = 50;
	private int iBOTDEPTH= 50;

	/*
	 * screen components
	 */
	private JFrame frmTrans;
	private JPanel pTrans;
	private JFrame frmSingleTrans;
	private JPanel pSingleTrans;
	private JPanel panTop;
	private JPanel panMid;
	private JPanel panBot;	
	CustomDateFormat cdate;
	UserPreferences up;
	JScrollPane pscroll;
	private JButton closeButton;
	JTable tabTran = null;
	private JButton closeTranButton;
	public static final String[] columnNames = {"Field","Value"};
	private Image imgIcon;
    /*
     * Table to link Moneydance transaction types to a string
     */
    private static final Map<String, String> txnTypes;
    static
    {
    	txnTypes = new HashMap<String, String>();
    	txnTypes.put(AbstractTxn.TRANSFER_TYPE_BANK,"Bank Xfr");
    	txnTypes.put(AbstractTxn.TRANSFER_TYPE_BUYSELL,"Buy/Sell");
    	txnTypes.put(AbstractTxn.TRANSFER_TYPE_BUYSELLXFR,"Buy/Sell Xfr");
    	txnTypes.put(AbstractTxn.TRANSFER_TYPE_DIVIDEND,"Dividend");
    	txnTypes.put(AbstractTxn.TRANSFER_TYPE_DIVIDENDXFR,"Dividend Xfr");
    	txnTypes.put(AbstractTxn.TRANSFER_TYPE_MISCINCEXP,"Misc Exp/Inc");
    	txnTypes.put(AbstractTxn.TRANSFER_TYPE_SHORTCOVER,"Short Cover");
    }
    /*
     * Table to link Moneydance transaction status to a string
     */
    private static final Map<AbstractTxn.ClearedStatus, String> txnStatus;
    static
    {
    	txnStatus = new HashMap<AbstractTxn.ClearedStatus, String>();
    	txnStatus.put(AbstractTxn.ClearedStatus.CLEARED,"Cleared");
    	txnStatus.put(AbstractTxn.ClearedStatus.RECONCILING,"Reconciling");
    	txnStatus.put(AbstractTxn.ClearedStatus.UNRECONCILED,"Unreconciled");
    }
    /**
     * Creates the window of transactions
     * 
     * @param bAllTransp Set to false to display only one side of the transaction, true to display both sides
     * @param objAcctBookp The current Moneydance Account Book
     * @param objAcctp The account you wish to display transactions for
     * @param bRollupp Set to true to display all transactions of descendants of the account
     * @param iStartDatep Start date of the period in which to display transactions
     * @param iEndDatep End date of the period in which to display transactions
     */
    public MRBViewTransactions(boolean bAllTransp, AccountBook objAcctBookp, Account objAcctp, boolean bRollupp, int iStartDatep, int iEndDatep) {
    	bAllTrans = bAllTransp;
    	objAcctBook = objAcctBookp;
    	objAcct = objAcctp;
    	iStartDate = iStartDatep;
    	iEndDate = iEndDatep;
    	bRollup = bRollupp;
   	    UserPreferences up = UserPreferences.getInstance();
  	    String strDateFormat = up.getSetting(UserPreferences.DATE_FORMAT);
  	    CustomDateFormat cdate = new CustomDateFormat(strDateFormat);
  	    imgIcon = getIcon("/com/moneydance/modules/features/mrbutil/mrb icon2.png");
  	    preferences = MRBPreferences2.getInstance();
  	    /*
  	     * set up panels
  	     */
		frmTrans = new JFrame("Moneydance Transactions");
    	pTrans = new JPanel(new BorderLayout());
    	panTop = new JPanel(new GridBagLayout());
    	panMid = new JPanel();
    	panBot = new JPanel(new GridBagLayout());
		pTrans.addComponentListener(new ComponentListener() {

			@Override
			public void componentResized(ComponentEvent arg0) {
				JPanel panScreen = (JPanel) arg0.getSource();
				Dimension objDimension = panScreen.getSize();
				updatePreferences(objDimension);
			}

			@Override
			public void componentShown(ComponentEvent arg0) {
				// not needed
			}

			@Override
			public void componentHidden(ComponentEvent e) {
				// not needed
			}

			@Override
			public void componentMoved(ComponentEvent e) {
				// not needed
			}

		});
		setPreferences(); // set the screen sizes
    	CurrencyType ctype = null;
    	CurrencyTable ctab = objAcctBook.getCurrencies();
    	CurrencyType ctgbp = ctab.getCurrencyByIDString("GBP");
    	pTrans.setBorder(new EmptyBorder(5,5,5,5));
    	/*
    	 * set up table
    	 * Create sorter for model to sort on date (column 3)
    	 */
        trantable = new MRBTranTable(new MRBTranModel(),this);
        TableRowSorter<TableModel> objSorter = new TableRowSorter<>(trantable.getModel());
        trantable.setRowSorter(objSorter);
        List<RowSorter.SortKey> sortKeys = new ArrayList<>();     
        sortKeys.add(new RowSorter.SortKey(2, SortOrder.ASCENDING));        
        objSorter.setSortKeys(sortKeys);
        objSorter.sort();
        tranmodel = (MRBTranModel) trantable.getModel();
    	pscroll = new JScrollPane(trantable);
    	int x=0;
    	int y=0;
    	JLabel txtstart = new JLabel("Start Date : ");
    	panTop.add (txtstart,GridC.getc(x, y));
    	x++;
    	JLabel stdate = new JLabel(cdate.format(iStartDate));
    	panTop.add(stdate,GridC.getc(x, y));
    	x++;
    	JLabel txtend = new JLabel(" End Date : ");
    	panTop.add (txtend,GridC.getc(x, y));
    	x++;
    	JLabel endate = new JLabel(cdate.format(iEndDate));
    	panTop.add(endate,GridC.getc(x, y));
    	pTrans.add(panTop,BorderLayout.PAGE_START);
    	panMid.add(pscroll);
    	pTrans.add(panMid,BorderLayout.CENTER);
    	txnSet = objAcctBook.getTransactionSet();
   		tsTrans = txnSet.getTransactions(this);
   		AccountUtil.sortTransactions(tsTrans, AccountUtil.DATE_ENTERED);
    	for (int i=0;i<tsTrans.getSize();i++) {
    		AbstractTxn txn = tsTrans.getTxn(i);
    		String[] arrRow = new String[9];
    		if (txn.getAccount() == null) {
    			arrRow[0] = "None";
    			ctype = ctgbp;
    		}
    		else {
    			arrRow[0] = txn.getAccount().getAccountName();
    			ctype = txn.getAccount().getCurrencyType();
    		}
    		arrRow[1] = txn.getDescription();
    		arrRow[2] = cdate.format(txn.getDateInt());
    		arrRow[3] = ctype.formatFancy(txn.getValue(),'.');
    		arrRow[4] = txnTypes.get(txn.getTransferType());
    		if (txn instanceof ParentTxn)
    			arrRow[5] = "P";
    		else
    			arrRow[5] = "S";
    		arrRow[6] = txn.getCheckNumber();
    		arrRow[7] = txnStatus.get(txn.getClearedStatus());
    		arrRow[8] = txn.getUUID();
      		tranmodel.addRow(arrRow);
    	}
    	tranmodel.fireTableDataChanged();
        y = 2;
	    x = 0;
	    closeButton = new JButton("Close");
	    closeButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
		    	closetran();
			}
		});
	    panBot.add(closeButton, GridC.getc(x, y));
	    pTrans.add(panBot,BorderLayout.PAGE_END);
    	pTrans.setPreferredSize(new Dimension(iSCREENWIDTH,iSCREENDEPTH));
    	panTop.setPreferredSize(new Dimension(iSCREENWIDTH,iTOPDEPTH));
    	panMid.setPreferredSize(new Dimension (iSCREENWIDTH,iSCROLLDEPTH));
    	pscroll.setPreferredSize(new Dimension(iSCROLLWIDTH,iSCROLLDEPTH));
    	panBot.setPreferredSize(new Dimension(iSCREENWIDTH, iBOTDEPTH));
    	//Display the window.
    	frmTrans.setTitle("Transactions");
    	if (imgIcon != null)
    		frmTrans.setIconImage(imgIcon);
    	frmTrans.add(pTrans);
    	frmTrans.pack();
    	frmTrans.setVisible(true);

    }
    /*
     * display an individual transaction
     */
    public void displayTransaction(int iRow) {
    	up = UserPreferences.getInstance();
    	String strDateFormat = up.getSetting(UserPreferences.DATE_FORMAT);
    	cdate = new CustomDateFormat(strDateFormat);
		frmSingleTrans = new JFrame("Transaction Detail");
		pSingleTrans = new JPanel(new BorderLayout());
       	CurrencyType ctype = null;
    	CurrencyTable ctab = objAcctBook.getCurrencies();
    	CurrencyType ctgbp = ctab.getCurrencyByIDString("GBP");
    	pSingleTrans.setBorder(new EmptyBorder(5,5,5,5));
        tabTran = new JTable(new DefaultTableModel(columnNames,0));
        tabTran.setAutoCreateRowSorter(true);
        DefaultTableModel modTran = (DefaultTableModel) tabTran.getModel();
    	JScrollPane pscroll = new JScrollPane(tabTran);
    	/*
    	 * find transaction
    	 */
    	String strTxnID = tranmodel.getUUID(iRow);
		AbstractTxn txn = tsTrans.getTxnByID(strTxnID);
    	Vector<String> vecid = new Vector<String>();
		vecid.add("ID");
		vecid.add(txn.getUUID());
    	Vector<String> vecoid = new Vector<String>();
		vecoid.add("Old ID");
		vecoid.add(new DecimalFormat("#").format(txn.getOldTxnID())+" ");
		modTran.addRow(vecoid);
		Vector<String> vecacct = new Vector<String>();
		vecacct.add("Account");
		
		if (txn.getAccount() == null) {
			vecacct.add("None");
			ctype = ctgbp;
		}
		else {
			vecacct.add(txn.getAccount().getAccountName());
			ctype = txn.getAccount().getCurrencyType();
		}
		modTran.addRow(vecacct);
		Vector<String> vecdesc = new Vector<String>();
		vecdesc.add("Description");
		vecdesc.add(txn.getDescription());
		modTran.addRow(vecdesc);
		Vector<String> vecdate = new Vector<String>();
		vecdate.add("Date");
		vecdate.add(cdate.format(txn.getDateInt()));
		modTran.addRow(vecdate);
		Vector<String> vecvalue = new Vector<String>();
		vecvalue.add("Value");
		vecvalue.add(ctype.formatFancy(txn.getValue(),'.'));
		modTran.addRow(vecvalue);
		Vector<String> vecttype = new Vector<String>();
		vecttype.add("Transfer Type");
		vecttype.add(txn.getTransferType());
		modTran.addRow(vecttype);
		Vector<String> vecps = new Vector<String>();
		vecps.add("Parent/Split");
		if (txn instanceof ParentTxn)
			vecps.add("Parent");
		else
			vecps.add("Split");
		modTran.addRow(vecps);
		Vector<String> veccheque = new Vector<String>();
		veccheque.add("Cheque");

		veccheque.add(txn.getCheckNumber());
		modTran.addRow(veccheque);
		Vector<String> vecstatus = new Vector<String>();
		vecstatus.add("Status");
   		vecstatus.add(String.valueOf(txn.getClearedStatus()));
		modTran.addRow(vecstatus);
		Vector<String> vecotc = new Vector<String>();
		vecotc.add("Num other trans");
   		vecotc.add(String.valueOf(txn.getOtherTxnCount()));
		modTran.addRow(vecotc);
		SyncRecord srTran = txn.getTags();
		if (srTran != null) {
        	Set<String> setKeys =srTran.keySet();
        	String [] keys =setKeys.toArray(new String[setKeys.size()]);
	
        	for (String keyitem : keys) {
        		Vector<String> vm = new Vector<String>();   
        		vm.add("Tag:" + keyitem);
        		vm.add(srTran.getString(keyitem,"unknown")+" ");
        		modTran.addRow(vm);
			}
		}
		List<String> listKeywords = txn.getKeywords();
		if (listKeywords != null) {
        	for (String item : listKeywords) {
        		Vector<String> vmkw = new Vector<String>();   
        		vmkw.add("Keyword:");
        		vmkw.add(item);
        		modTran.addRow(vmkw);
			}
			
		}
    	modTran.fireTableDataChanged();
     	pSingleTrans.add(pscroll,BorderLayout.CENTER);
	    closeTranButton = new JButton("Close");
	    closeTranButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
		    	closesingletran();
			}
		});
	    closeTranButton.setMaximumSize(new Dimension(40,20));
	    pSingleTrans.add(closeTranButton,BorderLayout.PAGE_END);
    	//Display the window.
	   	frmSingleTrans.setTitle("Transaction");
    	if (imgIcon != null)
    		frmSingleTrans.setIconImage(imgIcon);
    	frmSingleTrans.add(pSingleTrans);
    	frmSingleTrans.pack();
    	frmSingleTrans.setVisible(true);

   	
    }
	public void closetran() {
		if (pSingleTrans != null)	
			pSingleTrans.setVisible(false);
		if (frmSingleTrans != null)
			frmSingleTrans.dispose();
		if (pTrans != null)	
			pTrans.setVisible(false);
		if (frmTrans != null)
			frmTrans.dispose();
	}

	protected void closesingletran() {
		if (pSingleTrans != null)	
			pSingleTrans.setVisible(false);
		if (frmSingleTrans != null)
			frmSingleTrans.dispose();
	}
    @Override
	public boolean matches(Txn txn) {
		if (txn.getDateInt()< iStartDate || txn.getDateInt() > iEndDate)
			return false;
		if (bAllTrans){
			if (!((txn.getAccount() == objAcct) || (bRollup && objAcct.isAncestorOf(txn.getAccount())))) {
				int iTrans = txn.getOtherTxnCount();
				boolean bFound = false;
				for (int iOtherTxn = 0;iOtherTxn <iTrans;iOtherTxn++) {
					AbstractTxn txnOther = txn.getOtherTxn(iOtherTxn);
					if ((txnOther.getAccount() == objAcct) || (bRollup && objAcct.isAncestorOf(txnOther.getAccount())))
						bFound = true;
				}
				if (!bFound)
					return false;
			}
		}
		else {
			if ((txn.getAccount() == objAcct) || (bRollup && objAcct.isAncestorOf(txn.getAccount()))) {}
			else
				return false;
		}

    	return true;
    }
    @Override
	public boolean matchesAll() {
    	return false;
    }
	/*
	 * preferences
	 */
	private void setPreferences() {
		iSCREENWIDTH = preferences.getInt(MRBConstants.PROGRAMNAME+"."+MRBConstants.TRANSWIDTH,MRBConstants.TRANSCREENWIDTH);
		iSCREENDEPTH = preferences.getInt(MRBConstants.PROGRAMNAME+"."+MRBConstants.TRANSDEPTH,MRBConstants.TRANSCREENDEPTH);
		iSCROLLDEPTH = iSCREENDEPTH - iTOPDEPTH - iBOTDEPTH-50;
		iSCROLLWIDTH = iSCREENWIDTH -30;
	}

	private void updatePreferences(Dimension objDim) {
		preferences.put(MRBConstants.PROGRAMNAME+"."+MRBConstants.TRANSWIDTH, objDim.width);
		preferences.put(MRBConstants.PROGRAMNAME+"."+MRBConstants.TRANSDEPTH, objDim.height);
		setPreferences();
		preferences.isDirty();
    	pTrans.setPreferredSize(new Dimension(iSCREENWIDTH,iSCREENDEPTH));
    	panTop.setPreferredSize(new Dimension(iSCREENWIDTH,iTOPDEPTH));
    	panMid.setPreferredSize(new Dimension (iSCREENWIDTH,iSCROLLDEPTH));
    	pscroll.setPreferredSize(new Dimension(iSCROLLWIDTH,iSCROLLDEPTH));
    	panBot.setPreferredSize(new Dimension(iSCREENWIDTH, iBOTDEPTH));
		pTrans.revalidate();
	}
	/*
	 * Load the generic icon
	 */

	private Image getIcon(String action) {
		try {
			ClassLoader cl = getClass().getClassLoader();
			java.io.InputStream in = cl
					.getResourceAsStream(action);
			if (in != null) {
				ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
				byte buf[] = new byte[256];
				int n = 0;
				while ((n = in.read(buf, 0, buf.length)) >= 0)
					bout.write(buf, 0, n);
				return Toolkit.getDefaultToolkit().createImage(
						bout.toByteArray());
			}
		} catch (Throwable e) {
		}
		return null;
	}

}
