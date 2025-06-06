package com.moneydance.modules.features.securityhistoryload;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagLayout;
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
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextField;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.CurrencySnapshot;
import com.infinitekind.moneydance.model.CurrencyTable;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;

public class loadPricesWindow extends JFrame {
    private SortedMap<String, Double> mapPrices;
    private SortedMap<String, Double> mapHigh;
    private SortedMap<String, Double> mapLow;
    private SortedMap<String, Long> mapVolume;
    private SortedMap<String, Double> mapCurrent;
    private SortedMap<String, Integer> mapDates;
    private SortedMap<String, DummyAccount> mapAccounts;
    private SortedMap<String, CurrencyType> mapCurrencies;
    private MyTableModel pricesModel;
    private MyTable pricesTable;
    private CurrencyType baseCurrency;
    private String baseCurrencyID;
    private String baseCurrencyPrefix;
    private String baseCurrencySuffix;
    private MRBDebug debugInst = Main.debugInst;
    /*
     * Preferences and window sizes
     */
    private JPanel panScreen;
    private MRBPreferences2 preferences;
    public int iFRAMEWIDTH = Constants.FRAMEWIDTH;
    public int iFRAMEDEPTH = Constants.FRAMEHEIGHT;

    JScrollPane pricesScroll;
    JPanel panBot;
    JPanel panTop;
    JPanel panMid;
    JButton closeBtn;
    JButton saveBtn;
    NewParameters params;
    JDateField asOfDate;
    JCheckBox selectCB;
    String delimiter;

    public loadPricesWindow(JTextField txtFileName, NewParameters params, String delimiter) {
        this.params = params;
        this.delimiter = delimiter;
        MRBPreferences2.loadPreferences(Main.context);
        preferences = MRBPreferences2.getInstance();
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
        mapPrices = new TreeMap<String, Double>();
        mapHigh = new TreeMap<String, Double>();
        mapLow = new TreeMap<String, Double>();
        mapVolume = new TreeMap<String, Long>();
        mapCurrent = new TreeMap<String, Double>();
        mapDates = new TreeMap<String, Integer>();
        mapAccounts = new TreeMap<String, DummyAccount>();
        mapCurrencies = new TreeMap<String, CurrencyType>();
        loadAccounts(Main.context.getRootAccount());
        baseCurrency = Main.context.getCurrentAccountBook()
                .getCurrencies()
                .getBaseType();
        baseCurrencyID = baseCurrency.getIDString();
        baseCurrencyPrefix = baseCurrency.getPrefix();
        if (baseCurrencyPrefix.equals("$"))
            baseCurrencyPrefix = "\\$";
        baseCurrencySuffix = baseCurrency.getSuffix();
        if (params.getProcessCurrencies() || params.getIncludeZero()) {
            loadCurrencies(Main.context.getCurrentAccountBook());
        }
        try {
            loadFile(txtFileName);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Error when loading file - " + e.getLocalizedMessage());
            e.printStackTrace();
        }
        pricesModel = new MyTableModel(params, mapPrices, mapHigh, mapLow, mapVolume, mapCurrent, mapDates, mapAccounts, mapCurrencies);
        pricesTable = new MyTable(pricesModel);
        /*
         * Start of screen
         *
         * Top Panel date
         */
        panScreen.setLayout(new BorderLayout());
        /*
         * Top panel removed
         * Middle Panel table
         */
        panMid = new JPanel(new BorderLayout());
        pricesScroll = new JScrollPane(pricesTable);
        panMid.add(pricesScroll, BorderLayout.CENTER);
    		selectCB = new JCheckBox("Click to toggle de/select all lines");
        selectCB.setAlignmentX(LEFT_ALIGNMENT);
    		selectCB.setToolTipText("Click to toggle de/select all lines");
        selectCB.addItemListener(new ItemListener() {
            @Override
            public void itemStateChanged(ItemEvent e) {
                boolean bNewValue;
                if (e.getStateChange() == ItemEvent.DESELECTED)
                    bNewValue = false;
                else
                    bNewValue = true;
                for (int i = 0; i < pricesModel.getRowCount(); i++) {
                    if ((String) pricesModel.getValueAt(i, 5) != "0.0")
                        pricesModel.setValueAt(bNewValue, i, 0);
                }
                pricesModel.fireTableDataChanged();
            }
        });
        panMid.add(selectCB, BorderLayout.PAGE_END);
        panScreen.add(panMid, BorderLayout.CENTER);
        /*
         * Add  Buttons
         */
        panBot = new JPanel(new GridBagLayout());

        /*
         * Button 1
         */

        closeBtn = new JButton("Close");
        closeBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                close();
            }
        });
        panBot.add(closeBtn, GridC.getc(0,1).insets(15, 15, 15, 15).west());

        /*
         * Button 2
         */
        saveBtn = new JButton("Save Selected Values");
        saveBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                save();
            }
        });
        panBot.add(saveBtn, GridC.getc(1,1).insets(15, 15, 15, 15));

        panScreen.add(panBot, BorderLayout.PAGE_END);
        getContentPane().setPreferredSize(
                new Dimension(iFRAMEWIDTH, iFRAMEDEPTH));
        this.pack();


    }

    /*
     * Create 3 tables of current rate, date rate set and account object
     * all keyed by ticker symbol
     */
    private void loadAccounts(Account parentAcct) {
        int sz = parentAcct.getSubAccountCount();
        for (int i = 0; i < sz; i++) {
            Account acct = parentAcct.getSubAccount(i);
            if (acct.getAccountType() == Account.AccountType.SECURITY) {
                if ((acct.getCurrentBalance() != 0L) || (params.getIncludeZero())) {
                    CurrencyType ctTicker = acct.getCurrencyType();
                    /*
                     * Get last price entry
                     */
                    if (ctTicker != null) {
                        if (!ctTicker.getTickerSymbol().equals("")) {
                            List<CurrencySnapshot> listSnap = ctTicker.getSnapshots();
                            String strTicker = ctTicker.getTickerSymbol();
                            debugInst.debug("loadPricesWindow", "loadAccounts", MRBDebug.DETAILED, "Ticker before " + strTicker);
                            if (params.getIgnoreCase())
                                strTicker = strTicker.toUpperCase();
                            debugInst.debug("loadPricesWindow", "loadAccounts", MRBDebug.DETAILED, "Ticker after " + strTicker);
                            int iSnapIndex = listSnap.size() - 1;
                            DummyAccount dacct = new DummyAccount();
                            dacct.setAccount(acct);
                            dacct.setCurrencyType(ctTicker);
                            dacct.setAccountName(acct.getAccountName());
                            if (iSnapIndex < 0) {
                                mapCurrent.put(strTicker, 1.0);
                                mapDates.put(strTicker, 0);
                                mapAccounts.put(strTicker, dacct);
                            } else {
                                CurrencySnapshot ctssLast = listSnap.get(iSnapIndex);
                                if (ctssLast != null) {
                                    mapCurrent.put(strTicker, 1.0 / ctssLast.getRate());
                                }
                                mapDates.put(strTicker, ctssLast.getDateInt());
                                mapAccounts.put(strTicker, dacct);
                            }
                        }
                    }
                }
            }
            loadAccounts(acct);
        }
    }

    /*
     * Load the currencies and add to Securities
     */
    private void loadCurrencies(AccountBook book) {
        CurrencyTable ctTable = book.getCurrencies();
        Iterator<CurrencyType> typesIter = ctTable.iterator();
        while (typesIter.hasNext()) {
            CurrencyType currType = typesIter.next();
            if (currType.getCurrencyType() == CurrencyType.Type.SECURITY && params.getIncludeZero()) {
                if (!currType.getTickerSymbol().equals("") && !currType.getHideInUI()) {
                    List<CurrencySnapshot> listSnap = currType.getSnapshots();
                    String ticker = currType.getTickerSymbol();
                    if (params.getIgnoreCase())
                        ticker = ticker.toUpperCase();
                    int iSnapIndex = listSnap.size() - 1;
                    if (!mapAccounts.containsKey(ticker)) {
                        DummyAccount dummyAcct = new DummyAccount();
                        dummyAcct.setAccount(null);
                        dummyAcct.setCurrencyType(currType);
                        dummyAcct.setAccountName(currType.getName());
                        if (iSnapIndex < 0) {
                            mapCurrent.put(ticker, 1.0);
                            mapDates.put(ticker, 0);
                            mapAccounts.put(ticker, dummyAcct);
                        } else {
                            CurrencySnapshot ctssLast = listSnap.get(iSnapIndex);
                            if (ctssLast != null) {
                                mapCurrent.put(ticker, 1.0 / ctssLast.getRate());
                            }
                            mapDates.put(ticker, ctssLast.getDateInt());
                            mapAccounts.put(ticker, dummyAcct);
                        }
                    }
                }

            } else {

                if (!currType.getHideInUI() && currType != baseCurrency && currType.getCurrencyType() == CurrencyType.Type.CURRENCY) {
                    List<CurrencySnapshot> listSnap = currType.getSnapshots();
                    int snapIndex = listSnap.size() - 1;
                    if (snapIndex < 0) {
                        mapCurrent.put(Constants.CURRENCYID + currType.getIDString(), 1.0);
                        mapDates.put(Constants.CURRENCYID + currType.getIDString(), 0);
                        mapCurrencies.put(Constants.CURRENCYID + currType.getIDString(), currType);
                    } else {
                        CurrencySnapshot ctssLast = listSnap.get(snapIndex);
                        if (ctssLast == null)
                            mapCurrent.put(Constants.CURRENCYID + currType.getIDString(), 1.0);
                        else
                            mapCurrent.put(Constants.CURRENCYID + currType.getIDString(), ctssLast.getRate());
                        mapDates.put(Constants.CURRENCYID + currType.getIDString(), ctssLast.getDateInt());
                        mapCurrencies.put(Constants.CURRENCYID + currType.getIDString(), currType);
                    }
                }
            }
        }
    }

    /*
     * try to load selected file
     */
    private void loadFile(JTextField txtFileName) {
        int tickerFld = 0;
        int priceFld = 0;
        int highFld = 0;
        int lowFld = 0;
        int volumeFld = 0;
        int dateFld = 0;
        int maxChar = params.getMaxChar();
        String exchangeName;
        String ticker = "";
        String currencyID = "xxx";
        boolean isCurrency;
        List<String> listPrefix = params.getListPrefixes();
        try {

            FileReader frPrices = new FileReader(txtFileName.getText());
            BufferedReader brPrices = new BufferedReader(frPrices);
            /*
             * Get the headers
             */
            String line = brPrices.readLine().replaceAll("\"", "");
            String[] columns;
            switch (delimiter) {
                case Constants.COMMA -> {
                    columns = line.split(",");
                }
                case Constants.TAB -> {
                    columns = line.split("\\t");
                }
                case Constants.SEMICOLON -> {
                    columns = line.split(";");
                }
                case Constants.COLON -> {
                    columns = line.split(":");
                }
                default -> {
                    columns = line.split(",");
                }
            }
            for (int i = 0; i < columns.length; i++) {
                if (columns[i].equals(params.getTickerFld()))
                    tickerFld = i;
                if (columns[i].equals(params.getPriceFld()))
                    priceFld = i;
                if (columns[i].equals(params.getHighFld()))
                    highFld = i;
                if (columns[i].equals(params.getLowFld()))
                    lowFld = i;
                if (columns[i].equals(params.getVolumeFld()))
                    volumeFld = i;
                if (columns[i].equals(params.getDateFld()))
                    dateFld = i;
            }
            while ((line = brPrices.readLine()) != null) {
                isCurrency = false;
                try {
                    columns = splitString(line, delimiter);
                    /*
                     * Check for currency
                     */
                    if (params.getProcessCurrencies() &&
                            columns[tickerFld].length() > 2 &&
                            columns[tickerFld].substring(columns[tickerFld].length() - 2).equals(Constants.CURRENCYTICKER)) {
                        /*
                         * found currency
                         */
                        if (!columns[tickerFld].substring(0, 3).equals(baseCurrencyID)) {
                            debugInst.debug("loadPricesWindow", "loadFile", MRBDebug.INFO, "Not base Currency " + columns[tickerFld]);
                            throw new EmptyLine("not base currency");
                        }
                        currencyID = columns[tickerFld].substring(3, columns[tickerFld].length() - 2);
                        ticker = Constants.CURRENCYID + currencyID;
                        exchangeName = "";
                        isCurrency = true;
                    } else {
                        exchangeName = "";
                        String strAllTicker = columns[tickerFld];
                        debugInst.debug("loadPricesWindow", "loadFile", MRBDebug.DETAILED, "Ticker read " + strAllTicker);
                        if (params.getIgnoreCase())
                            strAllTicker = strAllTicker.toUpperCase();
                        debugInst.debug("loadPricesWindow", "loadFile", MRBDebug.DETAILED, "Ticker after " + strAllTicker);
                        if (params.getRemoveExch()) {
                            int iPeriod = strAllTicker.indexOf('.');
                            if (iPeriod > -1) {
                                ticker = strAllTicker.substring(0, iPeriod);
                                exchangeName = strAllTicker.substring(iPeriod + 1);
                            } else {
                                iPeriod = strAllTicker.indexOf(':');
                                if (iPeriod > -1) {
                                    ticker = strAllTicker.substring(0, iPeriod);
                                    exchangeName = strAllTicker.substring(iPeriod + 1);
                                } else {
                                    ticker = strAllTicker;
                                    exchangeName = "";
                                }
                            }

                        } else {
                            ticker = strAllTicker;
                            int iPeriod = ticker.indexOf('.');
                            if (iPeriod > -1) {
                                exchangeName = ticker.substring(iPeriod + 1);
                            } else {
                                iPeriod = ticker.indexOf(':');
                                if (iPeriod > -1) {
                                    exchangeName = ticker.substring(iPeriod + 1);
                                }
                            }
                        }
                        /*
                         * Now remove any prefix (if present)
                         */
                        for (String strPrefix : listPrefix) {
                            if (ticker.length() > strPrefix.length())
                                if (strPrefix.equals(ticker.substring(0, strPrefix.length()))) {
                                    ticker = ticker.substring(strPrefix.length());
                                }
                        }
                        /*
                         * If Max Characters specified shrink ticker to length
                         */
                        if (maxChar > 0)
                            if (ticker.length() > maxChar)
                                ticker = ticker.substring(0, maxChar);
                    }
                    /*
                     * Check to find ticker
                     */
                    if (isCurrency) {
                        if (!mapCurrencies.containsKey(ticker)) {
                            debugInst.debug("loadPricesWindow", "loadFile", MRBDebug.INFO, "Unknown Currency " + columns[tickerFld]);
                            throw new EmptyLine("Unknown currency");
                        }
                    } else {
                        debugInst.debug("loadPricesWindow", "loadFile", MRBDebug.DETAILED, "Ticker matched " + ticker);
                        if (!mapAccounts.containsKey(ticker)) {
                            debugInst.debug("loadPricesWindow", "loadFile", MRBDebug.INFO, "Unknown Ticker " + columns[tickerFld]);
                            throw new EmptyLine("Unknown ticker");
                        }
                    }
                    debugInst.debug("loadPricesWindow", "loadFile", MRBDebug.DETAILED, "Ticker found " + ticker);
                    /*
                     * Get Date to include in key
                     */
                    int tempDate = Main.customDateFormat.parseInt(columns[dateFld]);
                    TickerDate tempTickerDate = new TickerDate(ticker, tempDate);
                    String tickerDateStr = tempTickerDate.toString();
                    /*
                     * Amount maybe different to Moneydance, use multiplier
                     */
                    String priceStr;
                    try {
                        priceStr = stripCurrency(columns[priceFld]);
                        double dAmount = 0;
                        if (isCurrency)
                            dAmount = Double.parseDouble(priceStr);
                        else
                            dAmount = Double.parseDouble(priceStr) * Math.pow(10D, params.getMultiplier(exchangeName));
                        mapPrices.put(tickerDateStr, dAmount);
                    } catch (NumberFormatException e) {
                        // do nothing line is invalid
                    }
                    if (!params.getHighFld().equals(NewParameters.doNotLoad)) {
                        try {
                            priceStr = stripCurrency(columns[highFld]);
                            double dAmount = 0;
                            if (isCurrency)
                                dAmount = Double.parseDouble(priceStr);
                            else
                                dAmount = Double.parseDouble(priceStr) * Math.pow(10D, params.getMultiplier(exchangeName));
                            mapHigh.put(tickerDateStr, dAmount);
                        } catch (NumberFormatException e) {
                            // do nothing line is invalid
                        }
                    }
                    if (!params.getLowFld().equals(NewParameters.doNotLoad)) {
                        try {
                            priceStr = stripCurrency(columns[lowFld]);
                            double dAmount = 0;
                            if (isCurrency)
                                dAmount = Double.parseDouble(priceStr);
                            else
                                dAmount = Double.parseDouble(priceStr) * Math.pow(10D, params.getMultiplier(exchangeName));
                            mapLow.put(tickerDateStr, dAmount);
                        } catch (NumberFormatException e) {
                            // do nothing line is invalid
                        }
                    }
                    if (!params.getVolumeFld().equals(NewParameters.doNotLoad)) {
                        try {
                            Long lAmount = 0L;
                            lAmount = Long.parseLong(columns[volumeFld]);
                            mapVolume.put(tickerDateStr, lAmount);
                        } catch (NumberFormatException e) {
                            // do nothing line is invalid
                        }
                    }
                } catch (EmptyLine e) {
                    // do nothing, ignore empty lines
                }


            }
            brPrices.close();
        } catch (FileNotFoundException e) {
            JOptionPane.showMessageDialog(null, "File " + txtFileName + " not Found");
            close();
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "I/O Error whilst reading " + txtFileName);
            close();

        }

    }

    private String stripCurrency(String priceStr) {
        String priceTemp = priceStr;
        priceTemp = priceTemp.replaceFirst("^" + baseCurrencyPrefix, "");
        int index = priceTemp.indexOf(baseCurrencySuffix);
        if (index > 0)
            priceTemp = priceTemp.substring(0, index);
        return priceTemp;
    }

    public void close() {
        panScreen.setVisible(false);
        this.dispose();

    }

    private void save() {
        int iRows = pricesModel.getRowCount();
        boolean bUpdated = false;
        int iRowCount = 0;
        for (int i = 0; i < iRows; i++) {
            if (pricesModel.updateLine(i)) {
                bUpdated = true;
                iRowCount++;
            }
        }
        if (bUpdated) {
            JOptionPane.showMessageDialog(null, iRowCount + " prices updated");
            /*
             * Clear current account data and reload before redisplaying
             * the table
             */
            mapCurrent.clear();
            mapDates.clear();
            mapAccounts.clear();
            mapCurrencies.clear();
            loadAccounts(Main.context.getRootAccount());
            if (params.getProcessCurrencies() || params.getIncludeZero())
                loadCurrencies(Main.context.getCurrentAccountBook());
            pricesModel.ResetData(mapPrices, mapHigh, mapLow, mapVolume, mapCurrent, mapDates, mapAccounts, mapCurrencies);
            pricesModel.fireTableDataChanged();
            selectCB.setSelected(false);
            panScreen.revalidate();
        }
    }
    /*
     * Utility method to split a string containing both " and ,  will throw EmptyLine
     * if line contains no data
     */

    private String[] splitString(String strInput, String delimiter) throws EmptyLine {
        List<String> listParts = new ArrayList<String>();
        int i = 0;
        String strPart = "";
        char delimiterChar = switch (delimiter) {
            case Constants.COMMA -> ',';
            case Constants.TAB -> '\t';
            case Constants.SEMICOLON -> ';';
            case Constants.COLON -> ':';
            default -> ',';
        };
        boolean bString = false;
        while (i < strInput.length()) {
            char charAtI = strInput.charAt(i);
            if (charAtI == '\\') {
                if (bString) {
                    bString = false;
                } else
                    bString = true;
            } else if (charAtI == delimiterChar) {
                if (!bString) {
                    listParts.add(strPart);
                    strPart = "";
                }
            } else
                strPart += charAtI;
            i++;
        }
        if (i < 2)
            throw new EmptyLine("");
        listParts.add(strPart);
        String[] arrString = new String[listParts.size()];
        return listParts.toArray(arrString);
    }

    /*
     * preferences
     */
    private void setPreferences() {
        iFRAMEWIDTH = preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEWIDTH, Constants.FRAMEWIDTH);
        iFRAMEDEPTH = preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEDEPTH, Constants.FRAMEHEIGHT);
    }

    private void updatePreferences(Dimension objDim) {
        preferences.put(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEWIDTH, objDim.width);
        preferences.put(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEDEPTH, objDim.height);
        preferences.isDirty();
    }
}
