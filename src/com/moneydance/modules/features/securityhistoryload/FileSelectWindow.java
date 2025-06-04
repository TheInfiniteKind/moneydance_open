package com.moneydance.modules.features.securityhistoryload;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;

import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.HelpMenu;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPlatform;


public class FileSelectWindow extends JPanel implements ActionListener {
    private JTextField fileNameFld;
    private JComboBox<Integer> multiplier;
    private JFileChooser fileChooser;
    private File inputFile;
    private loadPricesWindow loadWindow;
    private JComboBox<String> tickerFld;
    private JComboBox<String> delimiters;
    private JCheckBox includeZero;
    private JCheckBox removeExch;
    private JCheckBox ignoreCase;
    private JCheckBox includeCurrency;
    private JComboBox<String> priceFld;
    private JComboBox<String> highFld;
    private JComboBox<String> lowFld;
    private JComboBox<String> volumeFld;
    private JComboBox<String> dateFld;
    private JComboBox<String> tickerMaxChar;
    private JComboBox<Integer> decimalChars;
    private JPanel panMult;
    private JPanel panPrefix;
    private JButton addBtn;
    private NewParameters parms;
    private List<ExchangeLine> listLines;
    private List<String> listPrefixes;

    private String[] columns;
    private String lastFileName;
    private Map<Object, String> mapCombos;
    private Map<Object, String> mapDelete;
    private Map<Object, String> mapPrefixes;
    private Map<Object, String> mapPrefDelete;
    private MRBDebug debugInst = Main.debugInst;
    private HelpMenu helpMenu;
    private JMenuItem onlineMenu = new JMenuItem("Online Help");
    private JMenu debugMenu = new JMenu("Turn Debug on/off");
    private JRadioButtonMenuItem debugOff;
    private JRadioButtonMenuItem debugInfo;
    private JRadioButtonMenuItem debugSumm;
    private JRadioButtonMenuItem debugDet;
    private MoneydanceUI mdGUI;
    private com.moneydance.apps.md.controller.Main mdMain;

    public FileSelectWindow() throws HeadlessException {
        mdMain = com.moneydance.apps.md.controller.Main.mainObj;
        mdGUI = mdMain.getUI();
        GridBagLayout gbl_panel = new GridBagLayout();
        this.setLayout(gbl_panel);
        helpMenu = new HelpMenu("Help");
        helpMenu.add(onlineMenu);
        onlineMenu.addActionListener(this);
        helpMenu.add(debugMenu);
        ButtonGroup group = new ButtonGroup();
        debugOff = new JRadioButtonMenuItem("Off");
        if (debugInst.getDebugLevel() == MRBDebug.OFF)
            debugOff.setSelected(true);
        debugOff.setMnemonic(KeyEvent.VK_R);
        debugOff.addActionListener(this);
        group.add(debugOff);
        debugMenu.add(debugOff);
        debugInfo = new JRadioButtonMenuItem("Information");
        if (debugInst.getDebugLevel() == MRBDebug.INFO)
            debugInfo.setSelected(true);
        debugInfo.setMnemonic(KeyEvent.VK_R);
        debugInfo.addActionListener(this);
        group.add(debugInfo);
        debugMenu.add(debugInfo);
        debugSumm = new JRadioButtonMenuItem("Summary");
        if (debugInst.getDebugLevel() == MRBDebug.SUMMARY)
            debugSumm.setSelected(true);
        debugSumm.setMnemonic(KeyEvent.VK_R);
        debugSumm.addActionListener(this);
        group.add(debugSumm);
        debugMenu.add(debugSumm);
        debugDet = new JRadioButtonMenuItem("Detailed");
        if (debugInst.getDebugLevel() == MRBDebug.DETAILED)
            debugDet.setSelected(true);
        debugDet.setMnemonic(KeyEvent.VK_R);
        debugDet.addActionListener(this);
        group.add(debugDet);
        debugMenu.add(debugDet);
        int gridy = 0;
        parms = new NewParameters();
        parms.init();
        lastFileName = parms.getLastFile();
        this.add(helpMenu, GridC.getc(5,gridy).insets(5, 10, 5, 10));
        gridy++;
        JLabel delimiterLbl = new JLabel("Choose Delimiter");
        this.add(delimiterLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        delimiters = new JComboBox<>(Constants.DELIMITERS);
        delimiters.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> delimiter = (JComboBox<String>) e.getSource();
                parms.setDelimiter(delimiter.getSelectedIndex());
            }
        });
        this.add(delimiters, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        if (parms.getDelimiter()>= Constants.DELIMITERS.length)
            parms.setDelimiter(0);
        delimiters.setSelectedIndex(parms.getDelimiter());
        gridy++;
        JLabel lblFileName = new JLabel("File Name : ");
        this.add(lblFileName, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());

        fileNameFld = new JTextField();
        fileNameFld.setColumns(50);
        fileNameFld.setText(lastFileName);
        this.add(fileNameFld, GridC.getc(1, gridy).insets(5, 10, 5, 10).colspan(3).fillx().west());

        JButton loadFileBtn = new JButton("Load File");
        loadFileBtn.setToolTipText("Click on this button to open the file specifed");
        this.add(loadFileBtn, GridC.getc(4,gridy).insets(5, 10, 5, 10));
        loadFileBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                loadFile();
            }
        });
        JButton chooseBtn = new JButton();
        Image icon = Main.extension.getIcon("Search-Folder-icon.jpg");
        if (icon !=null)
            chooseBtn.setIcon(new ImageIcon(icon));
        else chooseBtn.setText("Choose File");
        chooseBtn.setToolTipText("Click on this button to open the File Explorer");
        this.add(chooseBtn, GridC.getc(5,gridy).insets(5, 10, 5, 10));
        chooseBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                chooseFile();
            }
        });
        gridy++;
        JLabel tickerLbl = new JLabel("Select Ticker Field");
        this.add(tickerLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        tickerFld = new JComboBox<String>();
        tickerFld.setToolTipText("Required: Select the field that contains the Ticker");

        tickerFld.addItem("Please Select a Field");
        tickerFld.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> cbTick = (JComboBox<String>) e.getSource();
                parms.setTickerFld((String) cbTick.getSelectedItem());
            }
        });
        this.add(tickerFld, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        JLabel lblLExch = new JLabel("Remove Exchange from Ticker?");
        this.add(lblLExch, GridC.getc(2,gridy).insets(5, 0, 5, 10).east());
        removeExch = new JCheckBox();
        removeExch.setToolTipText("Selecting this box will remove from the Ticker any letters after : or .");
        removeExch.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JCheckBox chbExchT = (JCheckBox) e.getSource();
                parms.setRemoveExch(chbExchT.isSelected());
            }
        });
        this.add(removeExch, GridC.getc(3,gridy).insets(5, 0, 5, 10).west());
        gridy++;
        JLabel dateLbl = new JLabel("Select Date Field");
        this.add(dateLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        dateFld = new JComboBox<String>();
        dateFld.setToolTipText("Required: Select the field that contains the Date");
        dateFld.addItem("Please Select a Field");
        dateFld.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> cbDate = (JComboBox<String>) e.getSource();
                parms.setDateFld((String) cbDate.getSelectedItem());
            }
        });
        this.add(dateFld, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        gridy++;
        JLabel priceLbl = new JLabel("Select Price Field");
        this.add(priceLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        priceFld = new JComboBox<String>();
        priceFld.setToolTipText("Required: Select the field that contains the new Price");
        priceFld.addItem("Please Select a Field");
        priceFld.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> cbPric = (JComboBox<String>) e.getSource();
                parms.setPriceFld((String) cbPric.getSelectedItem());
            }
        });
        this.add(priceFld, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        JLabel zeroLbl = new JLabel("Include zero accounts?");
        this.add(zeroLbl, GridC.getc(2,gridy).insets(5, 0, 5, 10).east());
        includeZero = new JCheckBox();
        includeZero.setToolTipText("Selecting this box will include Securities that do not have any holdings");
        includeZero.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JCheckBox chbZeroT = (JCheckBox) e.getSource();
                parms.setIncludeZero(chbZeroT.isSelected());
            }
        });
        this.add(includeZero, GridC.getc(3,gridy).insets(5, 10, 5, 10).west());
        gridy++;
        JLabel highLbl = new JLabel("Select High Field");
        this.add(highLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        highFld = new JComboBox<String>();
        highFld.setToolTipText("Select the field that contains the High price for the day");
        highFld.addItem(NewParameters.doNotLoad);
        highFld.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> cbHighp = (JComboBox<String>) e.getSource();
                parms.setHighFld((String) cbHighp.getSelectedItem());
            }
        });
        this.add(highFld, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        JLabel currencyLbl = new JLabel("Process Currencies");
        this.add(currencyLbl, GridC.getc(2,gridy).insets(5, 0, 5, 10).east());
        includeCurrency = new JCheckBox();
        includeCurrency.setToolTipText("Selecting this box will include Currencies");
        includeCurrency.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JCheckBox chbCurrencyT = (JCheckBox) e.getSource();
                parms.setProcessCurrencies(chbCurrencyT.isSelected());
            }
        });
        this.add(includeCurrency, GridC.getc(3,gridy).insets(5, 10, 5, 10).west());
        gridy++;
        JLabel lowLbl = new JLabel("Select Low Field");
        this.add(lowLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        lowFld = new JComboBox<String>();
        lowFld.setToolTipText("Select the field that contains the Low price for the day");
        lowFld.addItem(NewParameters.doNotLoad);
        lowFld.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> cbLowp = (JComboBox<String>) e.getSource();
                parms.setLowFld((String) cbLowp.getSelectedItem());
            }
        });
        this.add(lowFld,GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        JLabel caseLbl = new JLabel("Ignore Ticker Case");
        this.add(caseLbl, GridC.getc(2,gridy).insets(5, 0, 5, 10).east());
        ignoreCase = new JCheckBox();
        ignoreCase.setToolTipText("Selecting this box will ignore the case of the Ticker when matching");
        ignoreCase.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JCheckBox chbCurrencyT = (JCheckBox) e.getSource();
                parms.setIgnoreCase(chbCurrencyT.isSelected());
            }
        });
        this.add(ignoreCase, GridC.getc(3,gridy).insets(5, 10, 5, 10).west());
        gridy++;
        JLabel volumeLbl = new JLabel("Select Volume Field");
        this.add(volumeLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        volumeFld = new JComboBox<String>();
        volumeFld.setToolTipText("Select the field that contains the Daily Volume");
        volumeFld.addItem(NewParameters.doNotLoad);
        volumeFld.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> cbVolumep = (JComboBox<String>) e.getSource();
                parms.setVolumeFld((String) cbVolumep.getSelectedItem());
            }
        });
        this.add(volumeFld, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        JLabel decimalLbl = new JLabel("Decimal Digits");
        this.add(decimalLbl, GridC.getc(2,gridy).insets(5, 0, 5, 10).east());
        decimalChars = new JComboBox<Integer>(NewParameters.decimalList);
        decimalChars.setToolTipText("By default the prices are shown to 4dp. You can select 5,6,7 or 8 dp to display");
        decimalChars.setSelectedIndex(4);
        decimalChars.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<Integer> cbDec = (JComboBox<Integer>) e.getSource();
                parms.setDecimal(cbDec.getSelectedIndex());
            }
        });
        this.add(decimalChars, GridC.getc(3,gridy).insets(5, 10, 5, 10).west());
        gridy++;
        JLabel maxCharLbl = new JLabel("Max chars in Ticker");
        this.add(maxCharLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        tickerMaxChar = new JComboBox<String>(NewParameters.maximums);
        tickerMaxChar.setToolTipText("By default all chars of the Ticker are matched.  You can restrict this to 5,6,7,8,or 9");
         tickerMaxChar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<String> cbMaxCharp = (JComboBox<String>) e.getSource();
                if (cbMaxCharp.getSelectedIndex() > 0)
                    parms.setMaxChar(Integer.parseInt((String) cbMaxCharp.getSelectedItem()));
                else
                    parms.setMaxChar(0);
            }
        });
        this.add(tickerMaxChar, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        gridy++;
        JLabel inst1Lbl = new JLabel("Exchanges multipliers are used when prices are held in a different denomination");
        this.add(inst1Lbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).colspan(2).west());

        gridy++;
        JLabel inst2Lbl = new JLabel("The Exchange is the characters at the end of the Ticker after (:) or (.)");
        this.add(inst2Lbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).colspan(2).west());
        gridy++;
        JLabel inst4Lbl = new JLabel("Exchange Multipliers and Prefixes only become visible after the file has been loaded/choosen");
        this.add(inst4Lbl, GridC.getc(1,gridy).insets(5, 10, 5, 10).colspan(3).west());
        gridy++;
        JLabel multiplierLbl = new JLabel("Select multiplier(s) for Prices");
        this.add(multiplierLbl, GridC.getc(0,gridy).insets(5, 10, 5, 10).west());
        JLabel lblMulttxt = new JLabel("e.g: -2 = * by 0.01, +2 = * by 100");
        this.add(lblMulttxt, GridC.getc(1,gridy).insets(5, 10, 5, 10));

        JLabel prefixPanelLbl = new JLabel("Enter prefixes to remove from Ticker");
        this.add(prefixPanelLbl, GridC.getc(3,gridy).insets(5, 10, 5, 10));
        gridy++;
        JLabel defaultLbl = new JLabel("Default");
        this.add(defaultLbl, GridC.getc(0,gridy).insets(5, 0, 5, 10).east());
        multiplier = new JComboBox<Integer>(NewParameters.multipliersList);
        multiplier.setSelectedIndex(4);
        multiplier.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                @SuppressWarnings("unchecked")
                JComboBox<Integer> cbMult = (JComboBox<Integer>) e.getSource();
                parms.setDefaultMultiplier(cbMult.getSelectedIndex());
            }
        });
        this.add(multiplier, GridC.getc(1,gridy).insets(5, 10, 5, 10).west());
        gridy++;
        panMult = new JPanel(new GridBagLayout());
        this.add(panMult, GridC.getc(0,gridy).insets(5, 10, 5, 10).colspan(2));

        panPrefix = new JPanel(new GridBagLayout());
        this.add(panPrefix, GridC.getc(2,gridy).insets(5, 10, 5, 10).colspan(2));
        gridy++;
        JButton saveBtn = new JButton("Save NewParameters");
        this.add(saveBtn, GridC.getc(1,gridy).insets(5, 10, 5, 10));
        saveBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                parms.save();
                JOptionPane.showMessageDialog(null, "NewParameters saved");
            }
        });
        JButton loadBtn = new JButton("Load Data");
        this.add(loadBtn,GridC.getc(2,gridy).insets(5, 10, 5, 10) );
        loadBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                loadData();
            }
        });


        JButton closeBtn = new JButton("Close");
        this.add(closeBtn, GridC.getc(3,gridy).insets(5, 10, 5, 10));
        closeBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                close();
            }
        });
    }

    private void loadFile() {
        FileReader pricesReader;
        if (fileNameFld.getText().isBlank()) {
            JOptionPane.showMessageDialog(null, "No file name specified");
            return;
        }
        Path filePath = Paths.get(fileNameFld.getText());
        int nameCount = filePath.getNameCount();
        Path parentPath = filePath.getName(nameCount - 1);
        String directory = parentPath.toString();
        try {
            pricesReader = new FileReader(fileNameFld.getText());
            parms.setLastFile(fileNameFld.getText());
            parms.setDirectoryName(directory);
            parms.save();
            pricesReader.close();
        } catch (FileNotFoundException e) {
            JOptionPane.showMessageDialog(null, "File " + fileNameFld.getText() + " not Found");
            return;
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "I//O Error whilst reading " + fileNameFld.getText());
            return;
        }

        loadFields();
        JOptionPane.showMessageDialog(null,"File Loaded");
    }

    private void chooseFile() {
        tickerFld.removeAllItems();
        tickerFld.addItem("Please Select a Field");
        dateFld.removeAllItems();
        dateFld.addItem("Please Select a Field");
        priceFld.removeAllItems();
        priceFld.addItem("Please Select a Field");
        highFld.removeAllItems();
        highFld.addItem(NewParameters.doNotLoad);
        lowFld.removeAllItems();
        lowFld.addItem(NewParameters.doNotLoad);
        volumeFld.removeAllItems();
        volumeFld.addItem(NewParameters.doNotLoad);
        String directory = parms.getDirectoryName();
        String fileName = "";
        if (MRBPlatform.isOSX()) {
            JFrame parentWindow = (JFrame) SwingUtilities.getWindowAncestor(this);
            System.setProperty("com.apple.macos.use-file-dialog-packages", "true");
            FileDialog winDialog = new FileDialog(parentWindow, "choose_file", FileDialog.LOAD);
            if (directory != null && !directory.isBlank()) {
                debugInst.debug("FileSelectWindow", "ChooseFile1", MRBDebug.DETAILED,
                        "Directory is:" + directory);
                winDialog.setDirectory(directory);
            }
            winDialog.setVisible(true);

            fileName = winDialog.getFile();
            if (fileName == null)
                return;
            debugInst.debug("FileSelectWindow", "ChooseFile2", MRBDebug.DETAILED,
                    "File Name is:" + fileName);
            directory = winDialog.getDirectory();
            if (directory == null) {
                debugInst.debug("FileSelectWindow", "ChooseFile3", MRBDebug.DETAILED,
                        "Directory is null:");
                directory = "";
            } else {
                debugInst.debug("FileSelectWindow", "ChooseFile3", MRBDebug.DETAILED,
                        "Directory is:" + directory);
                fileName = directory + fileName;
            }
            debugInst.debug("FileSelectWindow", "ChooseFile4", MRBDebug.DETAILED,
                    "File Name is:" + fileName);

        } else {
            if (Objects.equals(directory, "") || directory == null)
                fileChooser = new JFileChooser();
            else
                fileChooser = new JFileChooser(directory);
            fileChooser.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES);
            fileChooser.setFileFilter(new FileNameExtensionFilter("csv", "CSV"));
            int returnCode = fileChooser.showDialog(this, "Open File");
            if (returnCode == JFileChooser.APPROVE_OPTION) {
                inputFile = fileChooser.getSelectedFile();
                fileName = inputFile.getAbsolutePath();
                directory = inputFile.getParent();
            }
        }
        if (!fileName.isBlank()) ;
        {
            fileNameFld.setText(fileName);
            parms.setDirectoryName(directory);
            parms.save();
            loadFields();
        }
    }

    private void loadFields() {
        FileReader pricesReader;
        BufferedReader pricesBufferedReader;
        if (fileNameFld.getText().isBlank()) {
            JOptionPane.showMessageDialog(null, "Please Select a file first");
            return;
        }
        try {
            pricesReader = new FileReader(fileNameFld.getText());
            pricesBufferedReader = new BufferedReader(pricesReader);
            /*
             * Get the headers
             */
            String line = pricesBufferedReader.readLine().replaceAll("\"", "");
            switch ((String)delimiters.getSelectedItem()){
                case Constants.COMMA -> {columns = line.split(",");}
                case Constants.TAB -> {columns = line.split("\\t");}
                case Constants.SEMICOLON -> {columns = line.split(";");}
                case Constants.COLON -> {columns = line.split(":");}
                default -> {columns = line.split(",");}
            }
            pricesBufferedReader.close();
        } catch (FileNotFoundException e) {
            JOptionPane.showMessageDialog(null, "File " + fileNameFld.getText() + " not Found");
            return;
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "I//O Error whilst reading " + fileNameFld.getText());
            return;
        }
        parms.setLastFile(fileNameFld.getText());
        parms.save();
        int iTickerItem = 0;
        int iPriceItem = 0;
        int iHighItem = 0;
        int iLowItem = 0;
        int iVolumeItem = 0;
        int iDateItem = 0;
        for (int i = 0; i < columns.length; i++) {
            if (columns[i].equals(parms.getTickerFld()))
                iTickerItem = i + 1;
            tickerFld.addItem(columns[i]);
            if (columns[i].equals(parms.getPriceFld()))
                iPriceItem = i + 1;
            priceFld.addItem(columns[i]);
            if (columns[i].equals(parms.getHighFld()))
                iHighItem = i + 1;
            highFld.addItem(columns[i]);
            if (columns[i].equals(parms.getLowFld()))
                iLowItem = i + 1;
            lowFld.addItem(columns[i]);
            if (columns[i].equals(parms.getVolumeFld()))
                iVolumeItem = i + 1;
            volumeFld.addItem(columns[i]);
            if (columns[i].equals(parms.getDateFld()))
                iDateItem = i + 1;
            dateFld.addItem(columns[i]);
        }
        tickerFld.setSelectedIndex(iTickerItem);
        priceFld.setSelectedIndex(iPriceItem);
        highFld.setSelectedIndex(iHighItem);
        lowFld.setSelectedIndex(iLowItem);
        volumeFld.setSelectedIndex(iVolumeItem);
        dateFld.setSelectedIndex(iDateItem);
        removeExch.setSelected(parms.getRemoveExch());
        includeZero.setSelected(parms.getIncludeZero());
        includeCurrency.setSelected(parms.getProcessCurrencies());
        ignoreCase.setSelected(parms.getIgnoreCase());
        multiplier.setSelectedIndex(parms.getDefaultMultiplier());
        if (parms.getMaxChar() < 1)
            tickerMaxChar.setSelectedIndex(0);
        else
            tickerMaxChar.setSelectedIndex(parms.getMaxChar() - 5);
        listLines = parms.getListExchangeLines();
        listPrefixes = parms.getListPrefixes();
        mapCombos = new HashMap<Object, String>();
        mapDelete = new HashMap<Object, String>();
        mapPrefixes = new HashMap<Object, String>();
        mapPrefDelete = new HashMap<Object, String>();
        buildLines();
        buildPrefixes();
        removeExch.revalidate();
        includeZero.revalidate();
        includeCurrency.revalidate();
        tickerFld.revalidate();
        priceFld.revalidate();
        priceFld.revalidate();
        highFld.revalidate();
        lowFld.revalidate();
        volumeFld.revalidate();
        dateFld.revalidate();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();

    }

    private void loadData() {
        if (tickerFld.getSelectedIndex() == priceFld.getSelectedIndex()) {
            JOptionPane.showMessageDialog(null, "Ticker and Price can not be the same field");
            return;
        }
        if (tickerFld.getSelectedIndex() == 0 ||
                priceFld.getSelectedIndex() == 0 ||
                dateFld.getSelectedIndex() == 0) {
            JOptionPane.showMessageDialog(null, "Ticker, Date and Price must be selected");
            return;
        }
        if (highFld.getSelectedIndex() != 0 && (highFld.getSelectedIndex() == tickerFld.getSelectedIndex()
                || highFld.getSelectedIndex() == volumeFld.getSelectedIndex())) {
            JOptionPane.showMessageDialog(null, "High field can not be same as volume or ticker");
            return;
        }
        if (lowFld.getSelectedIndex() != 0 && (lowFld.getSelectedIndex() == tickerFld.getSelectedIndex()
                || lowFld.getSelectedIndex() == volumeFld.getSelectedIndex())) {
            JOptionPane.showMessageDialog(null, "Low field can not be same as volume or ticker");
            return;
        }
        if (volumeFld.getSelectedIndex() != 0 && (volumeFld.getSelectedIndex() == tickerFld.getSelectedIndex()
                || volumeFld.getSelectedIndex() == priceFld.getSelectedIndex())) {
            JOptionPane.showMessageDialog(null, "Volume field can not be same as price or ticker");
            return;
        }

        //Create and set up the window.
        JFrame frame = new loadPricesWindow(fileNameFld, parms,(String)delimiters.getSelectedItem());
        frame.setTitle("Load Security History - Build " + Main.buildStr);
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        frame.setVisible(true);
        return;
    }

    private void addMult() {
        JPanel panInput = new JPanel(new GridBagLayout());
        JLabel exchLbl = new JLabel("Enter Exchange (no .)");
        panInput.add(exchLbl, GridC.getc(0,0).insets(5, 10, 5, 10));
        JTextField exchFld = new JTextField();
        exchFld.setColumns(5);
        panInput.add(exchFld, GridC.getc(1,0).insets(5, 10, 5, 10));
        JLabel multLbl = new JLabel("Multiplier");
        panInput.add(multLbl, GridC.getc(2,0).insets(5, 10, 5, 10));
        JComboBox<Integer> multCombo = new JComboBox<Integer>(NewParameters.multipliersList);
        multCombo.setSelectedIndex(NewParameters.multipliersListDefaultIdx);
        panInput.add(multCombo, GridC.getc(3,0).insets(5, 10, 5, 10));
        while (true) {
            int result = JOptionPane.showConfirmDialog(null, panInput,
                    "Enter Exchange and Multiplier", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                String exch = exchFld.getText();
                if (exch.isBlank()) {
                    JOptionPane.showMessageDialog(null, "Exchange can not be blank");
                    continue;
                }
                parms.addExchange(exch, multCombo.getSelectedIndex());
                break;
            }
            if (result == JOptionPane.CANCEL_OPTION)
                break;
        }
        panMult.removeAll();
        buildLines();
        panMult.revalidate();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();
        return;

    }

    private void addPrefix() {
        JPanel panInput = new JPanel(new GridBagLayout());
        JLabel exchLbl = new JLabel("Enter Prefix)");
        panInput.add(exchLbl, GridC.getc(0,0).insets(5, 10, 5, 10));
        JTextField prefixFld = new JTextField();
        prefixFld.setColumns(5);
        panInput.add(prefixFld, GridC.getc(0,1).insets(5, 10, 5, 10));
        while (true) {
            int result = JOptionPane.showConfirmDialog(null, panInput,
                    "Enter Prefix", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                String strPrefix = prefixFld.getText();
                if (strPrefix.isBlank()) {
                    JOptionPane.showMessageDialog(null, "Prefix can not be blank");
                    continue;
                }
                parms.addPrefix(strPrefix);
                break;
            }
            if (result == JOptionPane.CANCEL_OPTION)
                break;
        }
        panPrefix.removeAll();
        buildPrefixes();
        panPrefix.revalidate();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();
        return;

    }

    private void buildLines() {
        int row = 2;
        mapCombos.clear();
        mapDelete.clear();
        for (ExchangeLine objLine : listLines) {
            JLabel exchLbl = new JLabel(objLine.getExchange());
            panMult.add(exchLbl, GridC.getc(1,row).insets(5, 10, 5, 10));
            JComboBox<Integer> multCombo = new JComboBox<Integer>(NewParameters.multipliersList);
            multCombo.setSelectedIndex(objLine.getMultiplier());
            mapCombos.put(multCombo, objLine.getExchange());
            multCombo.addActionListener(new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    @SuppressWarnings("unchecked")
                    JComboBox<Integer> multTCombo = (JComboBox<Integer>) e.getSource();
                    String exch = mapCombos.get(multTCombo);
                    parms.updateLine(exch, multTCombo.getSelectedIndex());
                }
            });
            panMult.add(multCombo, GridC.getc(2,row).insets(5, 10, 5, 10));
            JButton deleteBtn = new JButton("Delete");
            deleteBtn.addActionListener(new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    deleteExchange(e);
                }
            });
            panMult.add(deleteBtn, GridC.getc(3,row).insets(5, 10, 5, 10));
            mapDelete.put(deleteBtn, objLine.getExchange());

            row++;
        }
        addBtn = new JButton("Add Exchange Multiplier");
        addBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                addMult();
            }
        });
        panMult.add(addBtn,GridC.getc(0,row).insets(5, 10, 5, 10));

    }

    private void buildPrefixes() {
      int row = 2;
        mapPrefixes.clear();
        mapPrefDelete.clear();
        for (String prefix : listPrefixes) {
            JLabel prefixLbl = new JLabel(prefix);
            panPrefix.add(prefixLbl, GridC.getc(1,row).insets(5, 10, 5, 10));
            JButton deleteBtn = new JButton("Delete");
            deleteBtn.addActionListener(new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    deletePrefix(e);
                }
            });
            panPrefix.add(deleteBtn, GridC.getc(2,row).insets(5, 10, 5, 10));
            mapPrefDelete.put(deleteBtn, prefix);
            row++;
        }
        addBtn = new JButton("Add Prefix");
        addBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                addPrefix();
            }
        });
        panPrefix.add(addBtn, GridC.getc(0,row).insets(5, 10, 5, 10));

    }

    private void deleteExchange(ActionEvent e) {
        String exch = mapDelete.get(e.getSource());
        parms.deleteExchange(exch);
        panMult.removeAll();
        buildLines();
        panMult.revalidate();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();

    }

    private void deletePrefix(ActionEvent e) {
        String prefix = mapPrefDelete.get(e.getSource());
        parms.deletePrefix(prefix);
        panPrefix.removeAll();
        buildPrefixes();
        panPrefix.revalidate();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();

    }

    private void close() {
        this.setVisible(false);
        if (loadWindow != null)
            loadWindow.close();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.dispose();

    }

    @Override
    public void actionPerformed(ActionEvent aeMenu) {
        JMenuItem miSource = (JMenuItem) (aeMenu.getSource());
        if (miSource == onlineMenu) {
            String url = "http://github.com/mrbray99/moneydanceproduction/wiki/Security-Price-and-History-Load";
            mdGUI.showInternetURL(url);
        }
        if (miSource == debugOff) {
            debugInst.setDebugLevel(MRBDebug.OFF);
            debugOff.setSelected(true);
        }
        if (miSource == debugInfo) {
            debugInst.setDebugLevel(MRBDebug.INFO);
            debugInst.debug("FileSelectWindow", "actionPerformed", MRBDebug.INFO, "Debug turned to Info");
            debugInfo.setSelected(true);
        }
        if (miSource == debugSumm) {
            debugInst.setDebugLevel(MRBDebug.SUMMARY);
            debugInst.debug("FileSelectWindow", "actionPerformed", MRBDebug.SUMMARY, "Debug turned to Summary");
            debugSumm.setSelected(true);
        }
        if (miSource == debugDet) {
            debugInst.setDebugLevel(MRBDebug.DETAILED);
            debugInst.debug("FileSelectWindow", "actionPerformed", MRBDebug.DETAILED, "Debug turned to Detailed");
            debugDet.setSelected(true);
        }


    }
}
