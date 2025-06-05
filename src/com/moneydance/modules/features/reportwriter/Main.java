/*
 * Copyright (c) 2020, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */
package com.moneydance.modules.features.reportwriter;

import java.awt.*;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.text.SimpleDateFormat;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Date;
import java.util.List;

import javax.swing.*;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.AccountIterator;
import com.infinitekind.moneydance.model.AccountListener;
import com.infinitekind.moneydance.model.Budget;
import com.infinitekind.moneydance.model.BudgetList;
import com.infinitekind.moneydance.model.BudgetListener;
import com.infinitekind.moneydance.model.CurrencyListener;
import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.moneydance.model.InvestTxnType;
import com.infinitekind.moneydance.model.TxnUtil;
import com.infinitekind.util.CustomDateFormat;
import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBDirectoryUtils;
import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;
import com.moneydance.modules.features.reportwriter.factory.OutputCSV;
import com.moneydance.modules.features.reportwriter.factory.OutputDatabase;
import com.moneydance.modules.features.reportwriter.factory.OutputFactory;
import com.moneydance.modules.features.reportwriter.factory.OutputSpreadsheet;
import com.moneydance.modules.features.reportwriter.view.BeanSelectionRow;
import com.moneydance.modules.features.reportwriter.view.MyReport;
import com.moneydance.modules.features.reportwriter.view.ReportDataRow;
import com.moneydance.modules.features.reportwriter.view.SwingAccelerator;


/**
 * Generalized Moneydance extension to extract data
 * <p>
 * Main class to create main window
 * @author Mike Bray
 */

public class Main extends FeatureModule implements AccountListener, BudgetListener, CurrencyListener
{
	public static String minorBuildNo = "00";
	public static String databaseChanged = "20210121";

	public static CustomDateFormat cdate;
	public static DateTimeFormatter cdateFX;
	public static ZoneId zone;
	public static String datePattern;
	public static SwingAccelerator accels;
	public static Image mainIcon;
	public static MRBPreferences2 preferences;
	public static ClassLoader loader;
	public static Date now;
	public static char decimalChar;
	public static FeatureModuleContext context;
	public static AccountBook book;
	public static UserPreferences up;
	public static CurrencyType baseCurrency;
	public static MRBDebug rwDebugInst;
	public static Main extension;
	public static String buildNo;
	public static MyReport frame;
	public static Images loadedIcons;
	private Image selectedBlack = null;
	private Image selectedLight;
	private Image unselectedBlack;
	private Image unselectedLight;
	public ImageIcon selectedIcon;
	public ImageIcon unselectedIcon;
	public List<BeanSelectionRow> currencies;
	public List<BeanSelectionRow> transferTypes;
	public List<BeanSelectionRow> bankAccounts;
	public List<BeanSelectionRow> assetAccounts;
	public List<BeanSelectionRow> liabilityAccounts;
	public List<BeanSelectionRow> creditAccounts;
	public List<BeanSelectionRow> loanAccounts;
	public List<BeanSelectionRow> investmentAccounts;
	public List<BeanSelectionRow> securityAccounts;
	public List<BeanSelectionRow> incomeCategories;
	public List<BeanSelectionRow> expenseCategories;
	public List<BeanSelectionRow> tags;
	public List<BeanSelectionRow> securities;
	public List<BeanSelectionRow> budgets;

	private JFrame progressFrame;
	private JScrollPane progressScroll;
	private JTextArea progressArea;
	private String progressText;
	private String uri;
	private String command;
	private String extensionDir;

	public int SCREENWIDTH;
	public int SCREENHEIGHT;
	private int SCREENX;
	private int SCREENY;
	public static Font labelFont;
	private boolean extensionOpen = false;
	/*
	 * Called when extension is loaded<p>
	 * Need to register the feature and the URI command to be called 
	 * when the user selects the extension.
	 * 
	 * normally "showconsole"
	 */
	@Override
	public void init() {
		// the first thing we will do is register this module to be invoked
		// via the application toolbar
		extension = this;
		context = getContext();
		int iBuild = getBuild();
		buildNo = String.valueOf(iBuild);  
		mainIcon = getIcon("mrb icon2.png");
		try {
			context.registerFeature(this, "showconsole",
					mainIcon,
					getName());
			rwDebugInst = new MRBDebug();
			rwDebugInst.setExtension(Constants.EXTENSIONNAME);
			rwDebugInst.setDebugLevel(MRBDebug.INFO);
			rwDebugInst.debug(Constants.EXTENSIONNAME, "Init", MRBDebug.INFO, "Started Build "+buildNo+"."+minorBuildNo);
		}
		catch (Exception e) {
			e.printStackTrace(System.err);
		}
		up = UserPreferences.getInstance();
		datePattern = up.getSetting(UserPreferences.DATE_FORMAT);
		cdate = new CustomDateFormat(datePattern);
		cdateFX = DateTimeFormatter.ofPattern(datePattern);
		zone= ZoneId.systemDefault();
		now = new Date();
		decimalChar = up.getDecimalChar();
		loadedIcons = new Images(this);
		labelFont = UIManager.getFont("Label.font");
		/*
		 * Need to ensure Jasper Server is available in the .moneydance/fmodule/.reportwriter folder
		 * 
		 */
		if (!setReportDirectory()) {
			JOptionPane.showMessageDialog(null,"Problem loading Report Writer. Look at the Console Log for more detail");
		}
	}
	/**
	 * retrieves an image from within the .mxt file.  Must be included when the extension 
	 * is compiled
	 * @param action the name of the image to load
	 * @return 	the image		
	 */
	public Image getIcon(String resource) {
		try {
			loader = getClass().getClassLoader();
			java.io.InputStream in = 
					loader.getResourceAsStream(Constants.RESOURCES+resource);
			if (in != null) {
				ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
				byte[] buf = new byte[256];
				int n;
				while((n=in.read(buf, 0, buf.length))>=0)
					bout.write(buf, 0, n);
				return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
			}
		} catch (Throwable e) {
			rwDebugInst.debug("ReportWriter", "getIcon", MRBDebug.INFO,"Error loading image "+resource );
		}
		return null;
	}
	/*
	 * Need to capture MD calling cleanup so FX page is closed
	 */
	@Override
	public void cleanup() {
		rwDebugInst.debug("ReportWriter", "cleanup", MRBDebug.SUMMARY, "cleanup  ");
		closeConsole();
		extensionOpen= false;
	}
	@Override
	public void unload() {
		rwDebugInst.debug("ReportWriter", "unload", MRBDebug.SUMMARY, "unload  ");
    cleanup();
  }

	@Override
	public void handleEvent(String appEvent) {
		super.handleEvent(appEvent);
		rwDebugInst.debug("Main", "HandleEvent", MRBDebug.SUMMARY, "Event "+appEvent);       
		if (appEvent.compareToIgnoreCase("md:file:opening") == 0) {
			handleEventFileOpening();
		} else if (appEvent.compareToIgnoreCase("md:file:opened") == 0) {
			handleEventFileOpened();
		} else if (appEvent.compareToIgnoreCase("md:file:closing") == 0) {
			handleEventFileClosed();
		}
	}

	protected void handleEventFileOpening() {
		rwDebugInst.debug("Main","HandleEventFileOpening", MRBDebug.SUMMARY, "Opening ");
	}

	protected void handleEventFileOpened() {
		rwDebugInst.debug("Main", "HandleEventFileOpened", MRBDebug.INFO, "File Opened");
		if (!extensionOpen) {
			MRBPreferences2.forgetInstance();
			book=context.getCurrentAccountBook();
			MRBPreferences2.loadPreferences(context);
			preferences = MRBPreferences2.getInstance();		
			rwDebugInst.setDebugLevel(preferences.getInt(Constants.PROGRAMNAME+"."+Constants.DEBUGLEVEL, MRBDebug.INFO));
			String debug;
			if (rwDebugInst.getDebugLevel()==MRBDebug.INFO)
				debug = "INFO";
			else if (rwDebugInst.getDebugLevel()==MRBDebug.SUMMARY)
				debug = "SUMM";
			else if (rwDebugInst.getDebugLevel()== MRBDebug.DETAILED)
				debug = "DET";
			else
				debug = "OFF";	
			rwDebugInst.debug("ReportWriter", "HandleEventFileOpened", MRBDebug.INFO, "Debug level set to "+debug);
		}
		book.addAccountListener(this);
		book.getBudgets().addListener(this);
		book.getCurrencies().addCurrencyListener(this);
	}
	private boolean setReportDirectory() {
		File extensionData = MRBDirectoryUtils.getExtensionDataDirectory(Constants.PROGRAMNAME);
		extensionDir = extensionData.getAbsolutePath();
		boolean fileFound = false;
		boolean dbFound = false;
		String fileVersion=null;
		String fileName="";
		if (extensionData.exists()) {
			rwDebugInst.debug("Main", "setReportDirectory", MRBDebug.SUMMARY, "Extension directory found");
			String [] filenames = extensionData.list();
			for (String jarFile : filenames) {
				rwDebugInst.debug("Main", "setReportDirectory", MRBDebug.SUMMARY, "File "+jarFile);
				if (jarFile.startsWith("h2-") && jarFile.endsWith(".jar")) {
					dbFound = true;
					continue;
				}
					
				if (jarFile.endsWith(".java")) {
					File deleteFile = new File(extensionDir+"/"+jarFile);
					try {
						deleteFile.delete();
					}
					catch (Exception e) {
						e.printStackTrace();
						rwDebugInst.debug("Main", "setReportDirectory", MRBDebug.SUMMARY, "Error deleting temp file "+jarFile);
						return false;
					}
				}
					
			}
		}
		else {
			rwDebugInst.debug("Main", "setReportDirectory", MRBDebug.SUMMARY, "Extension directory not found");
			return false;
		}
		if (!dbFound) {
			InputStream stream = this.getClass().getResourceAsStream(Constants.RESOURCES+Constants.DATABASEJAR);
			String outputName = extensionDir+"/"+Constants.DATABASEJAR;
			outputName = outputName.replace(".jarsav", ".jar");
			if (stream != null) {
				try {
					Files.copy(stream, Paths.get(outputName),StandardCopyOption.REPLACE_EXISTING);
				}
				catch (IOException e) {
					e.printStackTrace();
					rwDebugInst.debug("Main", "setReportDirectory", MRBDebug.SUMMARY, "Error copying database jar file ");					
					return false;
				}
			}
				
		}
		return true;
	}

	protected void handleEventFileClosed() {
		rwDebugInst.debug("Main", "HandleEventFileClosed", MRBDebug.INFO, "Closing ");
		closeConsole();
	}
	/**
	 * Processes the uri from Moneydance.  Called by Moneydance
	 * <p>Commands:
	 * <ul>
	 * 	<li>showconsole - called when the user selects the extension
	 * <li>viewreport - View a report, must be done on AWT-Event-Queue
	 *   </ul>
	 *  @param uri		the uri from Moneydance
	 */
	@Override
	public void invoke(String urip) {
		if (book == null)
			book=context.getCurrentAccountBook();
		baseCurrency = book.getCurrencies().getBaseType();
		accels = new SwingAccelerator();
		if (preferences == null){
			MRBPreferences2.loadPreferences(context);
			preferences = MRBPreferences2.getInstance();
		}
		/*
		 * load JCheckBox icons for Unix due to customised UIManager Look and feel
		 */
		if (MRBPlatform.isUnix() || MRBPlatform.isFreeBSD()) {
			if (selectedBlack == null) {
				selectedBlack = getIcon(Constants.SELECTEDBLACKIMAGE);
				selectedLight = getIcon(Constants.SELECTEDLIGHTIMAGE);
				unselectedBlack = getIcon(Constants.UNSELECTEDBLACKIMAGE);
				unselectedLight = getIcon(Constants.UNSELECTEDLIGHTIMAGE);
				UIDefaults uiDefaults = UIManager.getDefaults();
				Color theme = uiDefaults.getColor("Panel.foreground");
				double darkness = 0;
				if (theme != null) {
					darkness = 1 - (0.299 * theme.getRed() + 0.587 * theme.getGreen()
							+ 0.114 * theme.getBlue()) / 255;
					rwDebugInst.debug("Quote Load", "Init", MRBDebug.DETAILED,
							"Panel.foreground Color " + theme.toString() + " Red " + theme.getRed()
									+ " Green " + theme.getGreen() + " Blue " + theme.getBlue()
									+ " Darkness " + darkness);
				}
				if (darkness > 0.5) {
					if (selectedBlack != null) {
						rwDebugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "selected black loaded");
						selectedIcon = new ImageIcon(
								selectedBlack.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
					if (unselectedBlack != null) {
						rwDebugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "unselected black loaded");
						unselectedIcon = new ImageIcon(
								unselectedBlack.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
				} else {
					if (selectedLight != null) {
						rwDebugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "selected light loaded");
						selectedIcon = new ImageIcon(
								selectedLight.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
					if (unselectedLight != null) {
						rwDebugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "unselected light loaded");
						unselectedIcon = new ImageIcon(
								unselectedLight.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
				}
			}
		}
		uri = urip;
		command = uri;
		int theIdx = uri.indexOf('?');
		if(theIdx>=0) {
			command = uri.substring(0, theIdx);
		}
		else {
			theIdx = uri.indexOf(':');
			if(theIdx>=0) {
				command = uri.substring(0, theIdx);
			}
		}
	     /*
		 * showConsole will be on AWT-Event-Queue, all other commands will be on the thread of the calling
		 * program, make sure all commands are processed on the AWT-Event-Queue to preserve sequence
		 */
		rwDebugInst.debug("Main","invoke",MRBDebug.SUMMARY,"Command "+ command);
		switch (command) {
		case "showconsole" :
			showConsole();
			break;
		case Constants.VIEWREPORTCMD :
			viewReport(uri);
			break;
		case Constants.SHOWHELP :
			String url =Constants.HELPURL;

			if(Desktop.isDesktopSupported()){
				Desktop desktop = Desktop.getDesktop();
				try {
					desktop.browse(new URI(url.trim()));
				} catch (IOException | URISyntaxException e) {
					e.printStackTrace();
				}
			}else{
				ProcessBuilder process = new ProcessBuilder();
				try {
					process.command("xdg-open " +url);
					process.start();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
			break;
		}
	}
	@Override
	public String getName() {
		return Constants.EXTENSIONNAME;
	}
	/**
	 * Create the GUI and show it.  For thread safety,
	 * this method should be invoked from the
	 * event dispatch thread.
	 */
	private void createAndShowGUI() {
		rwDebugInst.debug("ReportWriter", "createandShowGUI", MRBDebug.SUMMARY, "cleanup  ");
		if (extensionOpen && frame !=null) {
			frame.requestFocus();
			return;
		}
		collectData();
		book.addAccountListener(this);
		book.getBudgets().addListener(this);
		book.getCurrencies().addCurrencyListener(this);
		frame = new MyReport();
		frame.setTitle(Constants.EXTENSIONNAME+" "+buildNo+"."+minorBuildNo);
		frame.setIconImage(mainIcon);
		frame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
		//Display the window.
		frame.setLocationRelativeTo(null);
		frame.addWindowListener(new java.awt.event.WindowAdapter() {
			@Override
			public void windowClosing(java.awt.event.WindowEvent windowEvent) {
				if (JOptionPane.showConfirmDialog(frame,
						"Are you sure you want to close Report Writer?", "Close Window?", 
						JOptionPane.YES_NO_OPTION,
						JOptionPane.QUESTION_MESSAGE) == JOptionPane.YES_OPTION){
					rwDebugInst.debug("Main", "createAndShowGUI", MRBDebug.SUMMARY, "Yes");	        	
					closeConsole();
				}
			}
		});
		frame.pack();
		rwDebugInst.debug("Main",  "createAndShowGUI", MRBDebug.SUMMARY, "frame "+frame.getWidth()+"/"+frame.getHeight());
		frame.setVisible(true);
		SCREENX = preferences.getInt(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEX,0);
		SCREENY = preferences.getInt(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEY,0);
		if (SCREENX !=0 || SCREENY!=0)
			frame.setLocation(SCREENX,SCREENY);
		else
			frame.setLocationRelativeTo(null);
		frame.getContentPane().requestFocus();
		frame.addComponentListener(new ComponentListener() {
			@Override
			public void componentResized(ComponentEvent e) {

			}
	
			@Override
			public void componentMoved(ComponentEvent e) {
				Component c = (Component)e.getSource();
				Point currentLocation = c.getLocationOnScreen();
				Main.rwDebugInst.debug("Main", "createAndShowGUI", MRBDebug.SUMMARY, "Component moved "+currentLocation.x+"/"+currentLocation.y);
				Main.preferences.put(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEX, currentLocation.x);
				Main.preferences.put(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEY, currentLocation.y);
				Main.preferences.isDirty();
			}
	
			@Override
			public void componentShown(ComponentEvent e) {
			
			}
	
			@Override
			public void componentHidden(ComponentEvent e) {			
			}
		});
	}

	/**
	 * Starts the user interface for the extension
	 * 
	 * First it checks if Rhumba is present by sending a hello message to Rhumba
	 * @see #invoke(String)
	 */
	private synchronized void showConsole() {
		rwDebugInst.debug("Main", "showConsole", MRBDebug.INFO, "Show Console");
		javax.swing.SwingUtilities.invokeLater(this::createAndShowGUI);

	}
	/**
	 * Get the extension context
	 * @return FeatureModuleContext context
	 */
	public FeatureModuleContext getUnprotectedContext() {
		return getContext();
	}
	/**
	 * closes the extension - need to close the FX Panel 
	 */
	public synchronized void closeConsole() {
		rwDebugInst.debug("Main", "closeConsole", MRBDebug.DETAILED, "closing Console ");
		extensionOpen=false;
		if(frame != null){
			frame.setVisible(false);
			frame=null;
		}
		if (preferences != null) {
			MRBPreferences2.forgetInstance();
			preferences=null;
		}
		book=null;
		
	}

	/*
	 * collect the MD data required for the parameter and group panes
	 */
	private void collectData() {
		loadAccounts();
		loadBudgets();
		loadTags();
		loadCurrencies();
		InvestTxnType[] txnTypes = InvestTxnType.ALL_TXN_TYPES;
		transferTypes = new ArrayList<>();
		for (InvestTxnType type : txnTypes) {
			BeanSelectionRow row = new BeanSelectionRow(type.toString(),type.getIDString(), "Transfer Type", false);
			row.setDepth(0);
			transferTypes.add(row);
		}
	}
	private void loadBudgets(){
		budgets = new ArrayList<>();
		BudgetList budgetList = book.getBudgets();
		if (budgetList != null) {
			for (Budget budget : budgetList.getAllBudgets()) {
				BeanSelectionRow row = new BeanSelectionRow(budget.getUUID(),budget.toString(), "Budget", false);
				row.setDepth(0);
				budgets.add(row);
			}
		}

	}
	private synchronized void loadCurrencies() {
		currencies = new ArrayList<>();
		securities = new ArrayList<>();
		List<CurrencyType> currencyTable = book.getCurrencies().getAllCurrencies();
		for (CurrencyType type : currencyTable) {
			if (type.getCurrencyType()== CurrencyType.Type.CURRENCY) {
				BeanSelectionRow row = new BeanSelectionRow(type.getUUID(),type.getName()+"("+type.getIDString()+")", "Currency", false);
				row.setDepth(0);
				row.setInActive(type.getHideInUI());
				currencies.add(row);
			}
			if (type.getCurrencyType()== CurrencyType.Type.SECURITY) {
				BeanSelectionRow row = new BeanSelectionRow(type.getUUID(),type.getName()+"("+type.getIDString()+")", "Security", false);
				row.setDepth(0);
				row.setInActive(type.getHideInUI());
				securities.add(row);
			}
		}
		currencies.sort(new CompareCurrency());
		securities.sort(new CompareCurrency());
	}
	private synchronized void loadAccounts() {
		AccountIterator it = new AccountIterator(book);
		if (bankAccounts == null)
			bankAccounts = new ArrayList<>();
		else
			bankAccounts.clear();
		if (assetAccounts == null)
			assetAccounts = new ArrayList<>();
		else
			assetAccounts.clear();
		if (creditAccounts == null)
			creditAccounts = new ArrayList<>();
		else
			creditAccounts.clear();
		if (liabilityAccounts == null)
			liabilityAccounts = new ArrayList<>();
		else
			liabilityAccounts.clear();
		if (loanAccounts == null)
			loanAccounts = new ArrayList<>();
		else
			loanAccounts.clear();
		if (investmentAccounts == null)
			investmentAccounts = new ArrayList<>();
		else
			investmentAccounts.clear();
		if (securityAccounts == null)
			securityAccounts = new ArrayList<>();
		else
			securityAccounts.clear();
		if (incomeCategories == null)
			incomeCategories  = new ArrayList<>();
		else
			incomeCategories .clear();
		if (expenseCategories == null)
			expenseCategories = new ArrayList<>();
		else
			expenseCategories.clear();
		while (it.hasNext()) {
			Account acct = it.next();
			BeanSelectionRow row = new BeanSelectionRow(acct.getUUID(),acct.getAccountName(),"Account",false);
			row.setInActive(false);
			row.setSortText(acct.getFullAccountName());
			row.setDepth(0);
			switch (acct.getAccountType()) {
			case ASSET :
				row.setType("Asset");
				assetAccounts.add(row);
				break;
			case BANK :
				row.setType("Bank");
				bankAccounts.add(row);
				break;
			case CREDIT_CARD :
				row.setType("Credit Card");
				creditAccounts.add(row);
				break;
			case INVESTMENT :
				row.setType("Invest");
				investmentAccounts.add(row);
				securityAccounts.add(row);
				break;
			case LIABILITY :
				row.setType("Liability");
				liabilityAccounts.add(row);
				break;
			case LOAN :
				row.setType("Loan");
				loanAccounts.add(row);
				break;
			case INCOME:
				row.setText(acct.getIndentedName());
				row.setType("Income");
				row.setDepth(acct.getDepth());
				row.setInActive(acct.getAccountIsInactive());
				incomeCategories.add(row);
				break;
			case EXPENSE:
				row.setText(acct.getIndentedName());
				row.setType("Expense");
				row.setDepth(acct.getDepth());
				row.setInActive(acct.getAccountIsInactive());
				expenseCategories.add(row);
				break;
			case SECURITY:
				row.setText("   "+acct.getAccountName());
				row.setType("Security");
				row.setDepth(acct.getDepth());
				row.setInActive(acct.getCurrentBalance() == 0L);
				securityAccounts.add(row);
				break;
			case ROOT:
			default:
				break;
			}
		}
	}
	private void loadTags() {
		tags = new ArrayList<>();
		List<String> tagList = TxnUtil.getListOfAllUsedTransactionTags(book.getTransactionSet().getAllTxns());
		for (String tagStr : tagList) {
			tags.add(new BeanSelectionRow(tagStr,tagStr,"Tag",false));
			
		}
	}


	/*
	 * running on EDT
	 * Obtains data and writes to a h2 database
	 * Compiles the Jasper Report producing {name}.jasper
	 * Fills it with data producing {name}.jrprint
	 * Displays the report
	 * 
	 * Output files are stored in the defined reports directory
	 * A temporary file with a .java extension is created in the extension data directory
	 */
	private void viewReport(String uri)  {
		String name = uri.substring(uri.indexOf("?")+1);
		Parameters params = Parameters.getInstance();
		ReportDataRow rowEdit = new ReportDataRow();
		if (!rowEdit.loadRow(name, params)) {
			JOptionPane.showMessageDialog(null,"Report "+name+" not found");
			return;
		}
		OutputFactory output=null;
		displayProgressWindow();
		try {
			switch (rowEdit.getType()) {
			case DATABASE:
				output = new OutputDatabase(rowEdit,params);
				break;
			case SPREADSHEET :
				output = new OutputSpreadsheet(rowEdit,params);
				frame.resetData();
				output = null;
				closeProgressWindow();
				return;
			case CSV:
				output = new OutputCSV(rowEdit,params);
				frame.resetData();
				output = null;
				closeProgressWindow();
				return;
			}
		}
		catch (RWException e) {
			JOptionPane.showMessageDialog(null,e.getLocalizedMessage());	
			if (output !=null) {
				try {
					output.closeOutputFile();
				}
				catch (RWException e2) {
					JOptionPane.showMessageDialog(null,"Error closing output file "+e2.getLocalizedMessage());
				}
			}
			output = null;
			return;
		}
		closeProgressWindow();

	}
	private void displayProgressWindow() {
		progressFrame = new JFrame();
		progressText = "";
		progressArea=new JTextArea(30,70);
		progressArea.setText(progressText);
		progressScroll = new JScrollPane(progressArea);
		progressFrame.setSize(200,200);
		progressFrame.getContentPane().add(progressScroll,BorderLayout.CENTER);
		progressFrame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		progressFrame.pack();
		progressFrame.setLocationRelativeTo(null);
		progressFrame.setVisible(true);
	
	}
	public void updateProgress(String line) {
		progressArea.append(line+System.lineSeparator());
		progressArea.setCaretPosition(progressArea.getText().length() - 1);
		progressArea.update(progressArea.getGraphics());
		progressScroll.validate();
	}
	private void closeProgressWindow() {
		progressFrame.setVisible(false);
		progressFrame=null;
	}

	public void openOutput() {
		Parameters params = Parameters.getInstance();
        Desktop desktop = Desktop.getDesktop();
        File dirToOpen;
        try {
            dirToOpen = new File(params.getOutputDirectory());
            desktop.open(dirToOpen);
        } catch (IllegalArgumentException | IOException iae) {
			iae.printStackTrace();
			rwDebugInst.debug("Main","openOutput",MRBDebug.DETAILED,"Error opening Output folder - "+iae.getLocalizedMessage());
		}
	}
	/*
	 * Required Listener methods
	 */
	@Override
	public void accountModified(Account paramAccount) {
		loadAccounts();
		if (frame !=null)
			frame.resetData();
	}
	@Override
	public void accountBalanceChanged(Account paramAccount) {
		// TODO Auto-generated method stub

	}
	@Override
	public void accountDeleted(Account paramAccount1, Account paramAccount2) {
		loadAccounts();
		if (frame !=null)
			frame.resetData();
	}
	@Override
	public void accountAdded(Account paramAccount1, Account paramAccount2) {
		loadAccounts();
		if (frame !=null)
			frame.resetData();
	}
	@Override
	public void budgetListModified(BudgetList paramBudgetList) {
		loadAccounts();
		if (frame !=null)
			frame.resetData();
	}
	@Override
	public void budgetAdded(Budget paramBudget) {
		loadBudgets();
		if (frame !=null)
			frame.resetData();
	}
	@Override
	public void budgetRemoved(Budget paramBudget) {
		loadBudgets();
		if (frame !=null)
			frame.resetData();
	}
	@Override
	public void budgetModified(Budget paramBudget) {

	}

	@Override
	public void currencyTableModified(CurrencyTable arg0) {
		loadCurrencies();
		if (frame !=null)
			frame.resetData();
	}
	public static class CompareCurrency implements Comparator<BeanSelectionRow>{
		public int compare(BeanSelectionRow a, BeanSelectionRow b) {
			return a.getText().compareTo(b.getText());
		}
	}
}


