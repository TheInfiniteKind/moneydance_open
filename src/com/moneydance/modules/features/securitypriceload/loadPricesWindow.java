package  com.moneydance.modules.features.securitypriceload;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextField;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;

public class loadPricesWindow extends JFrame {
    private SortedMap<String,Double> mapPrices;
    private SortedMap<String,Double> mapHigh;
    private SortedMap<String,Double> mapLow;
    private SortedMap<String,Long> mapVolume;
    private SortedMap<String, Double> mapCurrent;
    private SortedMap<String,Integer> mapDates; 
    private SortedMap<String,DummyAccount> mapAccounts;
    private SortedMap<String,CurrencyType> mapCurrencies;
    private MyTableModel modPrices;
    private MyTable tabPrices;
    private CurrencyType baseCurrency;
    private String baseCurrencyStr;
    private String baseCurrencyPrefix;
    private String baseCurrencySuffix;
	/*
	 * Preferences and window sizes
	 */
	private JPanel panScreen;
	private MRBPreferences2 objPreferences;
	public int iFRAMEWIDTH = Constants.FRAMEWIDTH;
	public int iFRAMEDEPTH = Constants.FRAMEHEIGHT;
    JScrollPane spPrices;
    JPanel panBot;
    JPanel panTop;
    JPanel panMid;
    JCheckBox currentCB;
    JButton closeBtn;
    JButton saveBtn;
    Parameters params;
    JDateField asOfDate;
	JCheckBox selectCB;
	public loadPricesWindow(JTextField txtFileName,Parameters objParmsp)
 {
	 	params = objParmsp;
		MRBPreferences2.loadPreferences(Main.context);
		objPreferences = MRBPreferences2.getInstance();
		/*
		 * start of screen
		 */
		panScreen = new JPanel();
		this.add(panScreen);
		panScreen.setLayout(new BorderLayout());
		panScreen.addComponentListener(new ComponentListener() {

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
		mapPrices = new TreeMap<String, Double> ();
		mapHigh = new TreeMap<String, Double> ();
		mapLow = new TreeMap<String, Double> ();
		mapVolume = new TreeMap<String, Long> ();
		mapCurrent = new TreeMap<String, Double> ();
		mapDates = new TreeMap<String, Integer> ();
		mapAccounts = new TreeMap<String, DummyAccount> ();
		mapCurrencies = new TreeMap<String, CurrencyType> ();
		loadAccounts(Main.context.getRootAccount());
		baseCurrency = Main.context.getCurrentAccountBook()
				.getCurrencies()
				.getBaseType();
		baseCurrencyStr = baseCurrency.getIDString();
		baseCurrencyPrefix = baseCurrency.getPrefix();
		if (baseCurrencyPrefix.equals("$"))
			baseCurrencyPrefix = "\\$";
		baseCurrencySuffix = baseCurrency.getSuffix();
		if(params.getCurrency() || params.getZero()){
			loadCurrencies(Main.context.getCurrentAccountBook());
		}
		loadFile (txtFileName);
		modPrices = new MyTableModel (params,mapPrices, mapHigh, mapLow, mapVolume, mapCurrent, mapDates, mapAccounts, mapCurrencies);
		tabPrices = new MyTable (modPrices);
		/*
		 * Start of screen
		 * 
		 * Top Panel date
		 */
		panScreen.setLayout(new BorderLayout());
		panTop = new JPanel (new GridBagLayout());
		GridBagConstraints gbc_label = new GridBagConstraints();
		gbc_label.gridx = 0;
		gbc_label.gridy = 0;
		JLabel lbAsOfDate = new JLabel("As of Date for new prices:");
		panTop.add(lbAsOfDate,gbc_label);
		GridBagConstraints gbc_date = new GridBagConstraints();
		gbc_date.gridx = 0;
		gbc_date.gridy = 1;
		asOfDate = new JDateField(Main.cdate);
		panTop.add(asOfDate,gbc_date);
		panScreen.add(panTop,BorderLayout.PAGE_START);
		/*
		 * Middle Panel table
		 */
		panMid = new JPanel (new BorderLayout());
		spPrices = new JScrollPane (tabPrices);
		panMid.add(spPrices,BorderLayout.CENTER);
		selectCB = new JCheckBox();
		selectCB.setAlignmentX(LEFT_ALIGNMENT);
		selectCB.addItemListener(new ItemListener() {
			@Override
			public void itemStateChanged(ItemEvent e) {
				boolean bNewValue;
				if (e.getStateChange() == ItemEvent.DESELECTED)
					bNewValue = false;
				else
					bNewValue = true;
				for (int i=0;i<modPrices.getRowCount();i++) {
					if ((String)modPrices.getValueAt(i,5) != "0.0")
						modPrices.setValueAt(bNewValue, i, 0);
				}
				modPrices.fireTableDataChanged();
			}
		});
		panMid.add(selectCB,BorderLayout.PAGE_END);
		panScreen.add(panMid,BorderLayout.CENTER);
		/*
		 * Add Current Price Check Box Buttons
		 */
		/*
		 * Check box
		 */
		panBot = new JPanel(new GridBagLayout());
		GridBagConstraints gbcCrnt = new GridBagConstraints();
		gbcCrnt.gridx = 0;
		gbcCrnt.gridy = 0;
		gbcCrnt.anchor = GridBagConstraints.LINE_START;
		gbcCrnt.insets = new Insets(15,15,15,15);
		currentCB = new JCheckBox();
		currentCB.setSelected(true);
		panBot.add(currentCB,gbcCrnt);
		GridBagConstraints gbcCrnt_label = new GridBagConstraints();
		gbcCrnt_label.gridx = 1;
		gbcCrnt_label.gridy = 0;
		JLabel lbCrnt = new JLabel("Update Current Price");
		panBot.add(lbCrnt,gbcCrnt_label);
		
		/*
		 * Button 1
		 */
		GridBagConstraints gbcbt1 = new GridBagConstraints();
		gbcbt1.gridx = 0;
		gbcbt1.gridy = 1;
		gbcbt1.anchor = GridBagConstraints.LINE_START;
		gbcbt1.insets = new Insets(15,15,15,15);
		closeBtn = new JButton("Close");
		closeBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				close();
			}
		});
		panBot.add(closeBtn,gbcbt1);

		/*
		 * Button 2
		 */
		GridBagConstraints gbcbt2 = new GridBagConstraints();
		gbcbt2.gridx = gbcbt1.gridx+1;
		gbcbt2.gridy = gbcbt1.gridy;
		gbcbt2.insets = new Insets(15,15,15,15);
		saveBtn = new JButton("Save Selected Values");
		saveBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				save();
			}
		});
		panBot.add(saveBtn,gbcbt2);
		
		panScreen.add(panBot,BorderLayout.PAGE_END);
		getContentPane().setPreferredSize(
				new Dimension(iFRAMEWIDTH, iFRAMEDEPTH));
		this.pack();


	}
	/*
	 * Create 3 tables of current rate, date rate set and account object
	 * all keyed by ticker symbol
	 */
	 private void loadAccounts(Account parentAcct) {
	    List<Account> lAccts = parentAcct.getSubAccounts();
	    for (Account acct : lAccts) {
	      if (acct.getAccountType() == Account.AccountType.SECURITY){
	    	  if((acct.getCurrentBalance() != 0L)||(params.getZero())){
	    		  CurrencyType ctTicker = acct.getCurrencyType();
		    	  /*
		    	   * Get last price entry
		    	   */
		    	  if (ctTicker != null) {
		    		  if (!ctTicker.getTickerSymbol().equals("")) {
			    			  List<CurrencySnapshot> listSnap = ctTicker.getSnapshots();
			    			  String strTicker = ctTicker.getTickerSymbol();
			    			  if (params.getCase())
			    				  strTicker = strTicker.toUpperCase();
				    		  int iSnapIndex = listSnap.size()-1;
				    		  if( ! mapAccounts.containsKey(strTicker)){
				    			  DummyAccount dacct = new DummyAccount();
				    			  dacct.setAccount(acct);
				    			  dacct.setCurrencyType(ctTicker);
				    			  dacct.setAccountName(acct.getAccountName());
					    		  if (iSnapIndex < 0) {
								    	  mapCurrent.put(strTicker,1.0);
								    	  mapDates.put(strTicker,0);
								    	  mapAccounts.put(strTicker,dacct);
						    		  }
						    		  else {
								    	  CurrencySnapshot ctssLast = listSnap.get(iSnapIndex);
								    	  if (ctssLast != null) {
									    	  mapCurrent.put(strTicker,1.0/ctssLast.getRate());
								    	  }
								    	  mapDates.put(strTicker, ctssLast.getDateInt());
								    	  mapAccounts.put(strTicker, dacct);
						    		  }
					    		  }
			    			  }
		    		  }
	    	  }
	      }
	      loadAccounts(acct);
	    }
	 }
	 /*
	  * Load the currencies and unused securities and add to Securities
	  */
	 private void loadCurrencies(AccountBook abBook){
		 CurrencyTable ctTable = abBook.getCurrencies();
		 Iterator<CurrencyType> itTypes = ctTable.iterator();
		 while(itTypes.hasNext()){
			 CurrencyType ctType = itTypes.next();
			 if (ctType.getCurrencyType() == CurrencyType.Type.SECURITY && params.getZero()){
	    		  if (!ctType.getTickerSymbol().equals("")&&!ctType.getHideInUI()) {
	    			  List<CurrencySnapshot> listSnap = ctType.getSnapshots();
	    			  String strTicker = ctType.getTickerSymbol();
	    			  if (params.getCase())
	    				  strTicker = strTicker.toUpperCase();
		    		  int iSnapIndex = listSnap.size()-1;
		    		  if( ! mapAccounts.containsKey(strTicker)){
		    			  DummyAccount dacct = new DummyAccount();
		    			  dacct.setAccount(null);
		    			  dacct.setCurrencyType(ctType);
		    			  dacct.setAccountName(ctType.getName());
			    		  if (iSnapIndex < 0) {
						    	  mapCurrent.put(strTicker,1.0);
						    	  mapDates.put(strTicker,0);
						    	  mapAccounts.put(strTicker,dacct);
				    		  }
				    		  else {
						    	  CurrencySnapshot ctssLast = listSnap.get(iSnapIndex);
						    	  if (ctssLast != null) {
							    	  mapCurrent.put(strTicker,1.0/ctssLast.getRate());
						    	  }
						    	  mapDates.put(strTicker, ctssLast.getDateInt());
						    	  mapAccounts.put(strTicker, dacct);
				    		  }
			    		  }
	    			  }

			 }
			 else {		 
				 if (ctType.getCurrencyType()== CurrencyType.Type.CURRENCY &&
						 !ctType.getHideInUI() && 
						 ctType != baseCurrency && 
						 params.getCurrency() ){
					 List<CurrencySnapshot> listSnap = ctType.getSnapshots();
					 int iSnapIndex = listSnap.size()-1;
					 if (iSnapIndex < 0) {
				    	  mapCurrent.put(Constants.CURRENCYID+ctType.getIDString(),1.0);
				    	  mapDates.put(Constants.CURRENCYID+ctType.getIDString(),0);
				    	  mapCurrencies.put(Constants.CURRENCYID+ctType.getIDString(),ctType);
					 }
					 else {
				    	  CurrencySnapshot ctssLast = listSnap.get(iSnapIndex);
				    	  if (ctssLast == null) 
					    	  mapCurrent.put(Constants.CURRENCYID+ctType.getIDString(),1.0);
					      else
					    	  mapCurrent.put(Constants.CURRENCYID+ctType.getIDString(),ctssLast.getRate());
				    	  mapDates.put(Constants.CURRENCYID+ctType.getIDString(), ctssLast.getDateInt());
				    	  mapCurrencies.put(Constants.CURRENCYID+ctType.getIDString(), ctType);
					 }
				 }
			 }
		  }		 
	 }
	 /*
	  * try to load selected file
	  */
	 private void loadFile(JTextField txtFileName) {
		 	int iTicker=0;
		 	int iPrice=0;
		 	int iHigh = 0;
		 	int iLow = 0;
		 	int iVolume = 0;
		 	int iMaxChar = params.getMaxChar();
		 	String strExchange;
			String strTicker=""; 
			boolean bCurrency;
			List<String> listPrefix = params.getPrefixes();
			try {

				FileReader frPrices = new FileReader(txtFileName.getText());
				BufferedReader brPrices = new BufferedReader(frPrices);
				/*
				 * Get the headers
				 */
				String strLine = brPrices.readLine().replaceAll("\"",""); 
				String [] arColumns = strLine.split(",");
				for (int i = 0;i<arColumns.length;i++) {
					if (arColumns[i].equals(params.getTicker()))
							iTicker = i;
					if (arColumns[i].equals(params.getPrice()))
							iPrice = i;
					if (arColumns[i].equals(params.getHigh()))
						iHigh = i;
					if (arColumns[i].equals(params.getLow()))
						iLow = i;
					if (arColumns[i].equals(params.getVolume()))
						iVolume = i;
				}
				while ((strLine = brPrices.readLine())!= null) {
					bCurrency = false;
					try {
						arColumns = splitString(strLine);
						/*
						 * Check for currency
						 */
						if (params.getCurrency()&&
								arColumns[iTicker].length()>2 &&
								arColumns[iTicker].substring(arColumns[iTicker].length()-2).equals(Constants.CURRENCYTICKER)) {
							/*
							 * found currency
							 */
							if (!arColumns[iTicker].substring(0, 3).equals(baseCurrencyStr))
								throw new EmptyLine("not base currency");
							strTicker = Constants.CURRENCYID+arColumns[iTicker].substring(3,arColumns[iTicker].length()-2);
							strExchange = "";
							bCurrency = true;
						}
						else {
							strExchange = "";
							String strAllTicker = arColumns[iTicker];
							if (params.getCase())
								strAllTicker = strAllTicker.toUpperCase();
							if (params.getExch()) {
								int iPeriod = strAllTicker.indexOf('.');
								if (iPeriod > -1) {
									strTicker = strAllTicker.substring(0,iPeriod);
									strExchange = strAllTicker.substring(iPeriod+1);
								}
								else {
									iPeriod = strAllTicker.indexOf(':');
									if (iPeriod > -1) {
										strTicker = strAllTicker.substring(0,iPeriod);
										strExchange = strAllTicker.substring(iPeriod+1);								
									}
									else {
										strTicker = strAllTicker;
										strExchange = "";
									}
								}
									
							}
							else {
								strTicker = strAllTicker;
								int iPeriod = strTicker.indexOf('.');
								if (iPeriod > -1) {
									strExchange = strTicker.substring(iPeriod+1);
								}
								else {
									iPeriod = strTicker.indexOf(':');
									if (iPeriod > -1) {
										strExchange = strTicker.substring(iPeriod+1);								
									}
								}
							}
							/*
							 * Now remove any prefix (if present)
							 */
							for (String strPrefix : listPrefix) {
								if (strTicker.length() > strPrefix.length())
									if (strPrefix.equals(strTicker.substring(0, strPrefix.length()))){
										strTicker= strTicker.substring(strPrefix.length());						
								}
							}
							/*
							 * If Max Characters specified shrink ticker to length
							 */
							if (iMaxChar > 0)
								if(strTicker.length() > iMaxChar)
									strTicker = strTicker.substring(0,iMaxChar);
						}
						/*
						 * Check to find ticker
						 */
						if (!mapCurrent.containsKey(strTicker))
							throw new EmptyLine("Unknown ticker");
						/*
						 * Amount maybe different to Moneydance, use multiplier
						 */
						String priceStr;
						try {
							priceStr = stripCurrency(arColumns[iPrice]);
							double dAmount = 0;
							if (bCurrency)
								dAmount = Double.parseDouble(priceStr);
							else
								dAmount = Double.parseDouble(priceStr)*Math.pow(10D,params.getMultiplier(strExchange));
							mapPrices.put(strTicker, dAmount);
						}
						catch (NumberFormatException e) {
							// do nothing line is invalid
						}
						if (!params.getHigh().equals(Parameters.strDoNotLoad)) {
							try {
								priceStr = stripCurrency(arColumns[iHigh]);
								double dAmount = 0;
								if (bCurrency)
									dAmount = Double.parseDouble(priceStr);
								else
									dAmount = Double.parseDouble(priceStr)*Math.pow(10D,params.getMultiplier(strExchange));
								mapHigh.put(strTicker, dAmount);
							}
							catch (NumberFormatException e) {
								// do nothing line is invalid
							}
						}
						if (!params.getLow().equals(Parameters.strDoNotLoad)) {
							try {
								priceStr = stripCurrency(arColumns[iLow]);
								double dAmount = 0;
								if (bCurrency)
									dAmount = Double.parseDouble(priceStr);
								else
									dAmount = Double.parseDouble(priceStr)*Math.pow(10D,params.getMultiplier(strExchange));
								mapLow.put(strTicker, dAmount);
							}
							catch (NumberFormatException e) {
								// do nothing line is invalid
							}
						}
						if (!params.getVolume().equals(Parameters.strDoNotLoad)) {
							try {
								Long lAmount = 0L;
								lAmount = Long.parseLong(arColumns[iVolume]);
								mapVolume.put(strTicker, lAmount);
							}
							catch (NumberFormatException e) {
								// do nothing line is invalid
							}
						}
					}
					catch (EmptyLine e){
						// do nothing, ignore empty lines
					}
					

				}
				brPrices.close();
			}
			catch (FileNotFoundException e) {
				JFrame fTemp = new JFrame();
				JOptionPane.showMessageDialog(fTemp,"File "+txtFileName+" not Found");
				close();
			}
			catch (IOException e) {
				JFrame fTemp = new JFrame();
				JOptionPane.showMessageDialog(fTemp,"I//O Error whilst reading "+txtFileName);
				close();
				
			}
			
	 }
	 private String stripCurrency(String priceStr){
		String priceTemp = priceStr;
		priceTemp = priceTemp.replaceFirst("^"+baseCurrencyPrefix,"")	;
		int index = priceTemp.indexOf(baseCurrencySuffix);
		if (index > 0)
			priceTemp = priceTemp.substring(0, index);
		return priceTemp;
	 }	 
	 public void close() {
		this.setVisible(false);
		this.dispose();
//		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
//		topFrame.dispose();

	 }
	 private void save() {
		 int iRows = modPrices.getRowCount();
		 boolean bUpdated = false;
		 int iRowCount = 0;
		 for (int i=iRows-1;i>=0;i--){
			 if(modPrices.updateLine(i,asOfDate.getDateInt(),currentCB.isSelected())) {
				 bUpdated = true;
				 iRowCount++;
			 }
		 }
		 if (bUpdated){
			JFrame fTemp = new JFrame();
			JOptionPane.showMessageDialog(fTemp,iRowCount+" prices updated");
			/*
			 * Clear current account data and reload before redisplaying
			 * the table
			 */
			mapCurrent.clear();
			mapDates.clear();
			mapAccounts.clear();
			mapCurrencies.clear();
			loadAccounts(Main.context.getRootAccount());
			if(params.getCurrency()|| params.getZero())
				loadCurrencies(Main.context.getCurrentAccountBook());
			modPrices.ResetData(mapCurrent, mapDates, mapAccounts, mapCurrencies);
			modPrices.fireTableDataChanged();			 
			this.revalidate();
		 }
	 }
	 /*
	   * Utility method to split a string containing both " and ,  will throw EmptyLine
	   * if line contains no data
	   */
	  
	  private String[] splitString(String strInput) throws EmptyLine {
		  List<String> listParts = new ArrayList<String>();
		  int i=0;
		  String strPart = "";
		  boolean bString = false;
		  while(i<strInput.length()) {
			switch (strInput.substring(i, i+1)) {
			case "\"" : 
				if (bString) {
					bString = false;
				}
				else
					bString = true;
				break;
			case "," :
				if (!bString) {
					listParts.add(strPart);
					strPart = "";
				}
				break;
			default :
				strPart += strInput.substring(i, i+1);
			}
			i++;
		  }
		  if (i<2)
			  throw new EmptyLine ("");
		  listParts.add(strPart);
		  String[] arrString = new String[listParts.size()];
		  return listParts.toArray(arrString);
	  }
		/*
		 * preferences
		 */
		private void setPreferences() {
			iFRAMEWIDTH = objPreferences.getInt(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEWIDTH,Constants.FRAMEWIDTH);
			iFRAMEDEPTH = objPreferences.getInt(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEDEPTH,Constants.FRAMEHEIGHT);
		}

		private void updatePreferences(Dimension objDim) {
			objPreferences.put(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEWIDTH, objDim.width);
			objPreferences.put(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEDEPTH, objDim.height);
			objPreferences.isDirty();
		}
}
