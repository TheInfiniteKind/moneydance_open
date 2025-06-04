 package com.moneydance.modules.features.securitypriceload;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.io.*;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;

import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.modules.features.mrbutil.HelpMenu;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPlatform;

public class FileSelectWindow extends JPanel implements ActionListener{
	  private static final long serialVersionUID = 1L;
	  private JTextField txtFileName;
	  private JComboBox<Integer> cbMultiplier;
	  private JFileChooser objFileChooser;
	  private File fSecurities;
	  private loadPricesWindow objLoadWindow;
	  private JComboBox<String> cbTicker;
	  private JCheckBox chbZero;
	  private JCheckBox chbExch;
	  private JCheckBox chbCase;
	  private JCheckBox chbCurrency;
	  private JComboBox<String> cbPrice;
	  private JComboBox<String> cbHigh;
	  private JComboBox<String> cbLow;
	  private JComboBox<String> cbVolume;
	  private JComboBox<String> cbMaxChar;
	  private JComboBox<Integer> cbDecimal;
	  private JPanel panMult;
	  private JPanel panPrefix;
	  private JButton btnAdd;
	  private Parameters objParms;
	  private List<ExchangeLine> listLines;
	  private List<String> listPrefixes;

	  private String[] arColumns;
	  private String strLastFile;
	  private Map<Object,String> mapCombos;
	  private Map<Object,String> mapDelete;
	  private Map<Object,String> mapPrefixes;
	  private Map<Object,String> mapPrefDelete;
	  private MRBDebug objDebug = Main.debugInst;
	  private HelpMenu hmMenu;
	  private JMenuItem miOnline = new JMenuItem("Online Help");
	  private JMenu mDebug = new JMenu("Turn Debug on/off");
	  private JRadioButtonMenuItem rbOff;
	  private JRadioButtonMenuItem rbInfo;
	  private JRadioButtonMenuItem rbSumm;
	  private JRadioButtonMenuItem rbDet;
	private MoneydanceUI mdGUI;
	private com.moneydance.apps.md.controller.Main mdMain;
	public FileSelectWindow() throws HeadlessException {
		mdMain = com.moneydance.apps.md.controller.Main.mainObj;
		mdGUI = mdMain.getUI();
		GridBagLayout gbl_panel = new GridBagLayout();
		this.setLayout(gbl_panel);
		hmMenu = new HelpMenu ("Help");
		hmMenu.add(miOnline);	
		miOnline.addActionListener(this);
		hmMenu.add(mDebug);
		ButtonGroup group = new ButtonGroup();
		rbOff = new JRadioButtonMenuItem("Off");
		if (objDebug.getDebugLevel() == MRBDebug.OFF)
			rbOff.setSelected(true);
		rbOff.setMnemonic(KeyEvent.VK_R);
		rbOff.addActionListener(this);
		group.add(rbOff);
		mDebug.add(rbOff);
		rbInfo = new JRadioButtonMenuItem("Information");
		if (objDebug.getDebugLevel() == MRBDebug.INFO)
			rbInfo.setSelected(true);
		rbInfo.setMnemonic(KeyEvent.VK_R);
		rbInfo.addActionListener(this);
		group.add(rbInfo);
		mDebug.add(rbInfo);
		rbSumm = new JRadioButtonMenuItem("Summary");
		if (objDebug.getDebugLevel() == MRBDebug.SUMMARY)
			rbSumm.setSelected(true);
		rbSumm.setMnemonic(KeyEvent.VK_R);
		rbSumm.addActionListener(this);
		group.add(rbSumm);
		mDebug.add(rbSumm);
		rbDet = new JRadioButtonMenuItem("Detailed");
		if (objDebug.getDebugLevel() == MRBDebug.DETAILED)
			rbDet.setSelected(true);
		rbDet.setMnemonic(KeyEvent.VK_R);
		rbDet.addActionListener(this);
		group.add(rbDet);
		mDebug.add(rbDet);
		int iGridy = 0;
		objParms = new Parameters();
		strLastFile = objParms.getLastFile();
		GridBagConstraints gbc_hmMenu = new GridBagConstraints();
		gbc_hmMenu.insets = new Insets(10, 10, 10, 10);
		gbc_hmMenu.gridx = 5;
		gbc_hmMenu.gridy = iGridy;
		this.add(hmMenu, gbc_hmMenu);
		iGridy++;
		JLabel lblFileName = new JLabel("File Name(*) : ");
		GridBagConstraints gbc_lblFileName = new GridBagConstraints();
		gbc_lblFileName.insets = new Insets(10, 10, 10, 10);
		gbc_lblFileName.gridx = 0;
		gbc_lblFileName.gridy = iGridy;
		this.add(lblFileName, gbc_lblFileName);
		
		txtFileName = new JTextField();
		GridBagConstraints gbc_txtFileName = new GridBagConstraints();
		gbc_txtFileName.insets = new Insets(10, 10, 10, 10);
		gbc_txtFileName.gridx = 1;
		gbc_txtFileName.gridy = iGridy;
		gbc_txtFileName.gridwidth=3;
		txtFileName.setColumns(50);
		txtFileName.setText(strLastFile);
		objDebug.debug("FileSelectWindow", "FileSelectWindow", MRBDebug.DETAILED, "Last File set "+txtFileName.getText());
		this.add(txtFileName, gbc_txtFileName);
				
		JButton btnLoadfile = new JButton("Load File");
		GridBagConstraints gbc_btnLoadfile = new GridBagConstraints();
		btnLoadfile.setToolTipText("Click on this button to open the file specifed");
		gbc_btnLoadfile.insets = new Insets(10, 10, 10, 10);
		gbc_btnLoadfile.gridx = 4;
		gbc_btnLoadfile.gridy = iGridy;
		this.add(btnLoadfile, gbc_btnLoadfile);
		btnLoadfile.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				loadFile();
			}
		});
		JButton btnChoose = new JButton();
		Image img = getIcon("Search-Folder-icon.jpg");
		if (img == null)
			btnChoose.setText("Choose File");
		else
			btnChoose.setIcon(new ImageIcon(img));
		GridBagConstraints gbc_btnChoose = new GridBagConstraints();
		btnChoose.setToolTipText("Click on this button to open the File Explorer");
		gbc_btnChoose.insets = new Insets(10, 10, 10, 10);
		gbc_btnChoose.gridx = 5;
		gbc_btnChoose.gridy = iGridy;
		this.add(btnChoose, gbc_btnChoose);
		btnChoose.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				chooseFile();
			}
		});
		iGridy++;
		JLabel lblLTicker = new JLabel("Select Ticker Field(*)");		
		GridBagConstraints gbc_lblLTicker = new GridBagConstraints();
		gbc_lblLTicker.insets = new Insets(10, 10, 10, 10);
		gbc_lblLTicker.gridx = 0;
		gbc_lblLTicker.gridy = iGridy;
		this.add(lblLTicker, gbc_lblLTicker);	
		cbTicker = new JComboBox<String>();
		cbTicker.setToolTipText("Required: Select the field that contains the Ticker");
		GridBagConstraints gbc_cbLTicker = new GridBagConstraints();
		gbc_cbLTicker.insets = new Insets(10, 10, 10, 10);
		gbc_cbLTicker.gridx = 1;
		gbc_cbLTicker.gridy = iGridy;
		gbc_cbLTicker.anchor = GridBagConstraints.LINE_START;
		cbTicker.addItem("Please Select a Field");
		cbTicker.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<String> cbTick = (JComboBox<String>) e.getSource();
				objParms.setTicker((String)cbTick.getSelectedItem());
			}
		});
		this.add(cbTicker, gbc_cbLTicker);	
		JLabel lblLExch = new JLabel("Remove Exchange from Ticker?");
		GridBagConstraints gbc_cbLExch = new GridBagConstraints();
		gbc_cbLExch.insets = new Insets(10, 10, 10,0);
		gbc_cbLExch.gridx =2;
		gbc_cbLExch.gridy = iGridy;
		gbc_cbLExch.anchor = GridBagConstraints.LINE_END;
		this.add(lblLExch, gbc_cbLExch );	
		chbExch = new JCheckBox();
		chbExch.setToolTipText("Selecting this box will remove from the Ticker any letters after : or .");
		GridBagConstraints gbc_chbExch = new GridBagConstraints();
		gbc_chbExch.insets = new Insets(10, 0, 10, 10);
		gbc_chbExch.gridx = 3;
		gbc_chbExch.gridy = iGridy;
		gbc_chbExch.anchor = GridBagConstraints.LINE_START;
		chbExch.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox chbExchT = (JCheckBox) e.getSource();
				objParms.setExch(chbExchT.isSelected());
			}
		});
		iGridy++;
		this.add(chbExch, gbc_chbExch);	
		JLabel lblLPrice = new JLabel("Select Price Field");		
		GridBagConstraints gbc_lblLPrice = new GridBagConstraints();
		gbc_lblLPrice.insets = new Insets(10, 10, 10, 10);
		gbc_lblLPrice.gridx =0;
		gbc_lblLPrice.gridy = iGridy;
		this.add(lblLPrice, gbc_lblLPrice);	
		cbPrice = new JComboBox<String>();
		cbPrice.setToolTipText("Required: Select the field that contains the new Price");
		GridBagConstraints gbc_cbLPrice = new GridBagConstraints();
		gbc_cbLPrice.insets = new Insets(10, 10, 10, 10);
		gbc_cbLPrice.gridx = 1;
		gbc_cbLPrice.gridy = iGridy;
		gbc_cbLPrice.anchor = GridBagConstraints.LINE_START;
		cbPrice.addItem("Please Select a Field");
		cbPrice.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<String> cbPric = (JComboBox<String>) e.getSource();
				objParms.setPrice((String)cbPric.getSelectedItem());
			}
		});
		this.add(cbPrice, gbc_cbLPrice);
		JLabel lblLZero = new JLabel("Include zero accounts?");
		GridBagConstraints gbc_cbLZero = new GridBagConstraints();
		gbc_cbLZero.insets = new Insets(10, 10, 10,0);
		gbc_cbLZero.gridx =2;
		gbc_cbLZero.gridy = iGridy;
		gbc_cbLZero.anchor = GridBagConstraints.LINE_END;
		this.add(lblLZero, gbc_cbLZero );	
		chbZero = new JCheckBox();
		chbZero.setToolTipText("Selecting this box will include Securities that do not have any holdings");
		GridBagConstraints gbc_chbZero = new GridBagConstraints();
		gbc_chbZero.insets = new Insets(10, 0, 10, 10);
		gbc_chbZero.gridx = 3;
		gbc_chbZero.gridy = iGridy;
		gbc_chbZero.anchor = GridBagConstraints.LINE_START;
		chbZero.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox chbZeroT = (JCheckBox) e.getSource();
				objParms.setZero(chbZeroT.isSelected());
			}
		});
		iGridy++;
		this.add(chbZero, gbc_chbZero);
		JLabel lblLHigh = new JLabel("Select High Field");		
		GridBagConstraints gbc_lblLHigh = new GridBagConstraints();
		gbc_lblLHigh.insets = new Insets(10, 10, 10, 10);
		gbc_lblLHigh.gridx =0;
		gbc_lblLHigh.gridy =iGridy;
		this.add(lblLHigh, gbc_lblLHigh);	
		cbHigh = new JComboBox<String>();
		cbHigh.setToolTipText("Select the field that contains the High price for the day");
		GridBagConstraints gbc_cbLHigh = new GridBagConstraints();
		gbc_cbLHigh.insets = new Insets(10, 10, 10, 10);
		gbc_cbLHigh.gridx = 1;
		gbc_cbLHigh.gridy = iGridy;
		gbc_cbLHigh.anchor = GridBagConstraints.LINE_START;
		cbHigh.addItem(Parameters.strDoNotLoad);
		cbHigh.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<String> cbHighp = (JComboBox<String>) e.getSource();
				objParms.setHigh((String)cbHighp.getSelectedItem());
			}
		});
		this.add(cbHigh, gbc_cbLHigh);
		JLabel lblCurrency = new JLabel("Process Currencies");
		GridBagConstraints gbc_cbCurrency = new GridBagConstraints();
		gbc_cbCurrency.insets = new Insets(10, 10, 10,0);
		gbc_cbCurrency.gridx =2;
		gbc_cbCurrency.gridy = iGridy;
		gbc_cbCurrency.anchor = GridBagConstraints.LINE_END;
		this.add(lblCurrency, gbc_cbCurrency );	
		chbCurrency = new JCheckBox();
		chbCurrency.setToolTipText("Selecting this box will include Currencies");
		GridBagConstraints gbc_chbCurrency = new GridBagConstraints();
		gbc_chbCurrency.insets = new Insets(10, 0, 10, 10);
		gbc_chbCurrency.gridx = 3;
		gbc_chbCurrency.gridy = iGridy;
		gbc_chbCurrency.anchor = GridBagConstraints.LINE_START;
		chbCurrency.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox chbCurrencyT = (JCheckBox) e.getSource();
				objParms.setCurrency(chbCurrencyT.isSelected());
			}
		});
		this.add(chbCurrency, gbc_chbCurrency);
		iGridy++;
		JLabel lblLLow = new JLabel("Select Low Field");		
		GridBagConstraints gbc_lblLLow = new GridBagConstraints();
		gbc_lblLLow.insets = new Insets(10, 10, 10, 10);
		gbc_lblLLow.gridx =0;
		gbc_lblLLow.gridy =iGridy;
		this.add(lblLLow, gbc_lblLLow);	
		cbLow = new JComboBox<String>();
		cbLow.setToolTipText("Select the field that contains the Low price for the day");
		GridBagConstraints gbc_cbLLow = new GridBagConstraints();
		gbc_cbLLow.insets = new Insets(10, 10, 10, 10);
		gbc_cbLLow.gridx = 1;
		gbc_cbLLow.gridy = iGridy;
		gbc_cbLLow.anchor = GridBagConstraints.LINE_START;
		cbLow.addItem(Parameters.strDoNotLoad);
		cbLow.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<String> cbLowp = (JComboBox<String>) e.getSource();
				objParms.setLow((String)cbLowp.getSelectedItem());
			}
		});
		this.add(cbLow, gbc_cbLLow);
		JLabel lblCase = new JLabel("Ignore Ticker Case");
		GridBagConstraints gbc_cbCase = new GridBagConstraints();
		gbc_cbCase.insets = new Insets(10, 10, 10,0);
		gbc_cbCase.gridx =2;
		gbc_cbCase.gridy = iGridy;
		gbc_cbCase.anchor = GridBagConstraints.LINE_END;
		this.add(lblCase, gbc_cbCase );	
		chbCase = new JCheckBox();
		chbCase.setToolTipText("Selecting this box will ignore the case of the Ticker when matching");
		GridBagConstraints gbc_chbCase = new GridBagConstraints();
		gbc_chbCase.insets = new Insets(10, 0, 10, 10);
		gbc_chbCase.gridx = 3;
		gbc_chbCase.gridy = iGridy;
		gbc_chbCase.anchor = GridBagConstraints.LINE_START;
		chbCase.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				JCheckBox chbCurrencyT = (JCheckBox) e.getSource();
				objParms.setCase(chbCurrencyT.isSelected());
			}
		});
		this.add(chbCase, gbc_chbCase);
		iGridy++;
		JLabel lblLVolume = new JLabel("Select Volume Field");		
		GridBagConstraints gbc_lblLVolume = new GridBagConstraints();
		gbc_lblLVolume.insets = new Insets(10, 10, 10, 10);
		gbc_lblLVolume.gridx =0;
		gbc_lblLVolume.gridy = iGridy;
		this.add(lblLVolume, gbc_lblLVolume);	
		cbVolume = new JComboBox<String>();
		cbVolume.setToolTipText("Select the field that contains the Daily Volume");
		GridBagConstraints gbc_cbLVolume = new GridBagConstraints();
		gbc_cbLVolume.insets = new Insets(10, 10, 10, 10);
		gbc_cbLVolume.gridx = 1;
		gbc_cbLVolume.gridy = iGridy;
		gbc_cbLVolume.anchor = GridBagConstraints.LINE_START;
		cbVolume.addItem(Parameters.strDoNotLoad);
		cbVolume.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<String> cbVolumep = (JComboBox<String>) e.getSource();
				objParms.setVolume((String)cbVolumep.getSelectedItem());
			}
		});
		this.add(cbVolume, gbc_cbLVolume);
		JLabel lblDecimal = new JLabel("Decimal Digits");
		GridBagConstraints gbc_lblLDecimal = new GridBagConstraints();
		gbc_lblLDecimal.insets = new Insets(10, 10, 10, 10);
		gbc_lblLDecimal.gridx =2;
		gbc_lblLDecimal.gridy = iGridy;
		gbc_lblLDecimal.anchor = GridBagConstraints.LINE_END;
		this.add(lblDecimal, gbc_lblLDecimal );	
		cbDecimal = new JComboBox<Integer>(Parameters.arDecimal);
		cbDecimal.setToolTipText("By default the prices are shown to 4dp. You can select 5,6,7 or 8 dp to display");
		GridBagConstraints gbc_cbDecimal = new GridBagConstraints();
		gbc_cbDecimal.insets = new Insets(10, 10, 10, 10);
		gbc_cbDecimal.gridx = 3;
		gbc_cbDecimal.gridy =iGridy;
		gbc_cbDecimal.anchor = GridBagConstraints.LINE_START;
		cbDecimal.setSelectedIndex(4);
		cbDecimal.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<Integer> cbDec = (JComboBox<Integer>) e.getSource();
				objParms.setDecimal(cbDec.getSelectedIndex());
			}
		});	
		this.add(cbDecimal, gbc_cbDecimal );
		iGridy++;
		JLabel lblLMaxChar = new JLabel("Max chars in Ticker");		
		GridBagConstraints gbc_lblLMaxChar = new GridBagConstraints();
		gbc_lblLMaxChar.insets = new Insets(10, 10, 10, 10);
		gbc_lblLMaxChar.gridx =0;
		gbc_lblLMaxChar.gridy = iGridy;
		this.add(lblLMaxChar, gbc_lblLMaxChar);	
		cbMaxChar = new JComboBox<String>(Parameters.arMaximums);
		cbMaxChar.setToolTipText("By default all chars of the Ticker are matched.  You can restrict this to 5,6,7,8,or 9");
		GridBagConstraints gbc_cbLMaxChar = new GridBagConstraints();
		gbc_cbLMaxChar.insets = new Insets(10, 10, 10, 10);
		gbc_cbLMaxChar.gridx = 1;
		gbc_cbLMaxChar.gridy = iGridy;
		gbc_cbLMaxChar.anchor = GridBagConstraints.LINE_START;
		cbMaxChar.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<String> cbMaxCharp = (JComboBox<String>) e.getSource();
				if(cbMaxCharp.getSelectedIndex() > 0 )
					objParms.setMaxChar(Integer.parseInt((String)cbMaxCharp.getSelectedItem()));
				else
					objParms.setMaxChar(0);
			}
		});
		this.add(cbMaxChar, gbc_cbLMaxChar);
		iGridy++;
		JLabel lblInst1 = new JLabel("Exchanges multipliers are used when prices are held in a different denomination");
		GridBagConstraints gbc_lblInst1 = new GridBagConstraints();
		gbc_lblInst1.insets = new Insets(0,0,0,0);
		gbc_lblInst1.gridx = 0;
		gbc_lblInst1.gridy = iGridy;
		gbc_lblInst1.anchor = GridBagConstraints.WEST;
		gbc_lblInst1.gridwidth=2;
		this.add(lblInst1, gbc_lblInst1);	
		iGridy++; 
		JLabel lblInst2 = new JLabel("The Exchange is the characters at the end of the Ticker after (:) or (.)");
		GridBagConstraints gbc_lblInst2 = new GridBagConstraints();
		gbc_lblInst2.insets = new Insets(0,0,0,0);
		gbc_lblInst2.gridx =0;
		gbc_lblInst2.gridy = iGridy;
		gbc_lblInst2.anchor = GridBagConstraints.WEST;
		gbc_lblInst2.gridwidth=2;
		this.add(lblInst2, gbc_lblInst2);	
		iGridy++;
		JLabel lblInst4 = new JLabel("Exchange Multipliers and Prefixes only become visible after the file has been loaded/choosen");
		GridBagConstraints gbc_lblInst4 = new GridBagConstraints();
		gbc_lblInst4.insets = new Insets(10,0,0,0);
		gbc_lblInst4.gridx =1;
		gbc_lblInst4.gridy = iGridy;
		gbc_lblInst4.gridwidth=3;
		this.add(lblInst4, gbc_lblInst4);
		iGridy++;
		JLabel lblMultiplier = new JLabel("Select multiplier(s) for Prices");
		GridBagConstraints gbc_lblLMultiplier = new GridBagConstraints();
		gbc_lblLMultiplier.insets = new Insets(10, 10, 10, 10);
		gbc_lblLMultiplier.gridx =0;
		gbc_lblLMultiplier.gridy = iGridy;
		this.add(lblMultiplier, gbc_lblLMultiplier);	
		JLabel lblMulttxt = new JLabel("e.g: -2 = * by 0.01, +2 = * by 100");
		GridBagConstraints gbc_lblLMulttxt = new GridBagConstraints();
		gbc_lblLMulttxt.insets = new Insets(10, 10, 10, 10);
		gbc_lblLMulttxt.gridx =1;
		gbc_lblLMulttxt.gridy =iGridy;
		this.add(lblMulttxt, gbc_lblLMulttxt);	

		JLabel lblPrefixPanel = new JLabel("Enter prefixes to remove from Ticker");
		GridBagConstraints gbc_lblPrefixPanel = new GridBagConstraints();
		gbc_lblPrefixPanel.insets = new Insets(10, 10, 10, 10);
		gbc_lblPrefixPanel.gridx =3;
		gbc_lblPrefixPanel.gridy = iGridy;
		this.add(lblPrefixPanel, gbc_lblPrefixPanel);	
		iGridy++;
		JLabel lblDefault = new JLabel("Default");
		GridBagConstraints gbc_lblLDefault = new GridBagConstraints();
		gbc_lblLDefault.insets = new Insets(10, 10, 10, 10);
		gbc_lblLDefault.gridx =0;
		gbc_lblLDefault.gridy = iGridy;
		gbc_lblLDefault.anchor = GridBagConstraints.LINE_END;
		this.add(lblDefault, gbc_lblLDefault );	
		cbMultiplier = new JComboBox<Integer>(Parameters.arMultipliers);
		GridBagConstraints gbc_cbMultiplier = new GridBagConstraints();
		gbc_cbMultiplier.insets = new Insets(10, 10, 10, 10);
		gbc_cbMultiplier.gridx = 1;
		gbc_cbMultiplier.gridy = iGridy;
		gbc_cbMultiplier.anchor = GridBagConstraints.LINE_START;
		cbMultiplier.setSelectedIndex(4);
		cbMultiplier.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				@SuppressWarnings("unchecked")
				JComboBox<Integer> cbMult = (JComboBox<Integer>) e.getSource();
				objParms.setDefaultMult(cbMult.getSelectedIndex());
			}
		});	
		this.add(cbMultiplier, gbc_cbMultiplier );
		iGridy++;
		panMult = new JPanel(new GridBagLayout());
		GridBagConstraints gbc_panMult = new GridBagConstraints();
		gbc_panMult.insets = new Insets(10, 10, 10, 10);
		gbc_panMult.gridx = 0;
		gbc_panMult.gridy = iGridy;
		gbc_panMult.gridwidth=2;
		this.add(panMult,gbc_panMult);

		panPrefix = new JPanel(new GridBagLayout());
		GridBagConstraints gbc_panPrefix = new GridBagConstraints();
		gbc_panPrefix.insets = new Insets(10, 10, 10, 10);
		gbc_panPrefix.gridx = 2;
		gbc_panPrefix.gridy = iGridy;
		gbc_panPrefix.gridwidth=2;
		this.add(panPrefix,gbc_panPrefix);
		iGridy++;
		JButton btnSave = new JButton("Save Parameters");
		GridBagConstraints gbc_btnSave = new GridBagConstraints();
		gbc_btnSave.insets = new Insets(10, 10, 10, 10);
		gbc_btnSave.gridx = 1;
		gbc_btnSave.gridy = iGridy;
		this.add(btnSave, gbc_btnSave);
		btnSave.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				objParms.save();
				JOptionPane.showMessageDialog(null,"Parameters saved");
			}
		});	
		JButton btnLoad = new JButton("Load Data");
		GridBagConstraints gbc_btnLoad = new GridBagConstraints();
		gbc_btnLoad.insets = new Insets(10, 10, 10, 10);
		gbc_btnLoad.gridx = 2;
		gbc_btnLoad.gridy = iGridy;
		this.add(btnLoad, gbc_btnLoad);
		btnLoad.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				loadData();
			}
		});
		
		
		JButton btnClose = new JButton("Close");
		GridBagConstraints gbc_btnClose = new GridBagConstraints();
		gbc_btnClose.insets = new Insets(10, 10, 10, 10);
		gbc_btnClose.gridx = 3;
		gbc_btnClose.gridy = iGridy;
		this.add(btnClose, gbc_btnClose);
		btnClose.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				close();
			}
		});
	}
	private void loadFile() {
		FileReader frPrices;
		if (txtFileName.getText().equals("")) {
			JOptionPane.showMessageDialog(null,"No file name specified");
			return;
		}
		Path pathFile = Paths.get(txtFileName.getText());
	    int iNameCount = pathFile.getNameCount();
	    Path pathParent = pathFile.getName(iNameCount - 1);
	    String strDirectory = pathParent.toString();
		try {
			frPrices = new FileReader(txtFileName.getText());
			objDebug.debug("FileSelectWindow", "loadFile", MRBDebug.DETAILED,
					"saving filename :"+txtFileName.getText()+ " & directory :" + strDirectory);
			objParms.setLastFile(txtFileName.getText());
		    objParms.setDirectory(strDirectory);
		    objParms.save();
		    frPrices.close();
		}
		catch (FileNotFoundException e) {
			JOptionPane.showMessageDialog(null,"File "+txtFileName.getText()+" not Found");
			return;
		}
		catch (IOException e) {
			JOptionPane.showMessageDialog(null,"I//O Error whilst reading "+txtFileName.getText());
			return;
		}
	
		loadFields();
	}
	private void chooseFile() {
		cbTicker.removeAllItems();
		cbTicker.addItem("Please Select a Field");
		cbPrice.removeAllItems();
		cbPrice.addItem("Please Select a Field");
		cbHigh.removeAllItems();
		cbHigh.addItem(Parameters.strDoNotLoad);
		cbLow.removeAllItems();
		cbLow.addItem(Parameters.strDoNotLoad);
		cbVolume.removeAllItems();
		cbVolume.addItem(Parameters.strDoNotLoad);
		String strDirectory = objParms.getDirectory();
		String strFileName="";
		if (MRBPlatform.isOSX()) {
			JFrame parentWindow = (JFrame) SwingUtilities.getWindowAncestor(this); 
		       System.setProperty("com.apple.macos.use-file-dialog-packages", "true");
	         FileDialog fwin = new FileDialog(parentWindow, "choose_file", FileDialog.LOAD);
	         if (strDirectory != null && strDirectory != "") {
	     		objDebug.debug("FileSelectWindow", "ChooseFile1", MRBDebug.DETAILED,
	    				"Directory is:"+strDirectory);
	           fwin.setDirectory(strDirectory);
	         }
	         fwin.setVisible(true);
	   
	         strFileName =fwin.getFile();
	         if (strFileName == null)
	        	 return;
     		objDebug.debug("FileSelectWindow", "ChooseFile2", MRBDebug.DETAILED,
	     				"File Name is:"+strFileName);
	         strDirectory = fwin.getDirectory();
	         if(strDirectory == null) {
	      		objDebug.debug("FileSelectWindow", "ChooseFile3", MRBDebug.DETAILED,
	    				"Directory is null:");
	      		strDirectory = "";
	         }
	         else {
	        	 objDebug.debug("FileSelectWindow", "ChooseFile3", MRBDebug.DETAILED,
	    				"Directory is:"+strDirectory);
	        	 strFileName = strDirectory+strFileName;
	         }
     		objDebug.debug("FileSelectWindow", "ChooseFile4", MRBDebug.DETAILED,
	     				"File Name is:"+strFileName);
	   
	       }
		else {
			if (strDirectory == "" || strDirectory == null)
				objFileChooser = new JFileChooser();
			else
				objFileChooser = new JFileChooser(strDirectory);
			objFileChooser.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES);
			objFileChooser.setFileFilter(new FileNameExtensionFilter("csv","CSV"));
			int iReturn = objFileChooser.showDialog(this, "Open File");
			if (iReturn == JFileChooser.APPROVE_OPTION) {
				fSecurities = objFileChooser.getSelectedFile();
				strFileName = fSecurities.getAbsolutePath();
				strDirectory = fSecurities.getParent();
			}
		}
		if (strFileName != ""); {
			txtFileName.setText(strFileName);
			objParms.setDirectory(strDirectory);
			objDebug.debug("FileSelectWindow", "ChooseFile", MRBDebug.DETAILED,
					"saving "+strFileName+" in directory "+strDirectory);
			objParms.save();	
			loadFields();
		}
	}
	private void loadFields() {
		FileReader frPrices;
		BufferedReader brPrices;
		if (txtFileName.getText().equals("")) {
			JOptionPane.showMessageDialog(null,"Please Select a file first");
			return;
		}
		try {
			frPrices = new FileReader(txtFileName.getText());
			brPrices = new BufferedReader(frPrices);
			/*
			 * Get the headers
			 */
			String strLine = brPrices.readLine().replaceAll("\"",""); 
			arColumns = strLine.split(",");
			brPrices.close();
		}
		catch (FileNotFoundException e) {
			JOptionPane.showMessageDialog(null,"File "+txtFileName.getText()+" not Found");
			return;
		}
		catch (IOException e) {
			JOptionPane.showMessageDialog(null,"I//O Error whilst reading "+txtFileName.getText());
			return;
		}
		objParms.setLastFile(txtFileName.getText());
		objParms.save();
		int iTickerItem = 0;
		int iPriceItem = 0;
		int iHighItem = 0;
		int iLowItem = 0;
		int iVolumeItem = 0;
		for (int i=0;i<arColumns.length;i++) {
			if (arColumns[i].equals(objParms.getTicker()))
				iTickerItem = i+1;
			cbTicker.addItem(arColumns[i]);
			if (arColumns[i].equals(objParms.getPrice()))
				iPriceItem = i+1;
			cbPrice.addItem(arColumns[i]);
			if (arColumns[i].equals(objParms.getHigh()))
				iHighItem = i+1;
			cbHigh.addItem(arColumns[i]);
			if (arColumns[i].equals(objParms.getLow()))
				iLowItem = i+1;
			cbLow.addItem(arColumns[i]);
			if (arColumns[i].equals(objParms.getVolume()))
				iVolumeItem = i+1;
			cbVolume.addItem(arColumns[i]);
		}
		cbTicker.setSelectedIndex(iTickerItem);
		cbPrice.setSelectedIndex(iPriceItem);
		cbHigh.setSelectedIndex(iHighItem);
		cbLow.setSelectedIndex(iLowItem);
		cbVolume.setSelectedIndex(iVolumeItem);
		chbExch.setSelected(objParms.getExch());
		chbZero.setSelected(objParms.getZero());
		chbCurrency.setSelected(objParms.getCurrency());
		chbCase.setSelected(objParms.getCase());
		cbMultiplier.setSelectedIndex(objParms.getDefaultMult());
		cbDecimal.setSelectedIndex(objParms.getDecimal());
		if (objParms.getMaxChar() < 1)
			cbMaxChar.setSelectedIndex(0);
		else
			cbMaxChar.setSelectedIndex(objParms.getMaxChar()-5);
		listLines = objParms.getLines();
		listPrefixes = objParms.getPrefixes();
		mapCombos = new HashMap<Object,String>();
		mapDelete = new HashMap<Object,String>();
		mapPrefixes = new HashMap<Object,String>();
		mapPrefDelete = new HashMap<Object,String>();
		buildLines();
		buildPrefixes();
		chbExch.revalidate();
		chbZero.revalidate();
		chbCurrency.revalidate();
		cbTicker.revalidate();
		cbPrice.revalidate();
		cbPrice.revalidate();
		cbHigh.revalidate();
		cbLow.revalidate();
		cbVolume.revalidate();
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.pack();

	}
	private void loadData() {
		if (cbTicker.getSelectedIndex() == cbPrice.getSelectedIndex()) {
			JOptionPane.showMessageDialog(null,"Ticker and Price can not be the same field");
			return;
		}
		if (cbTicker.getSelectedIndex() == 0 ||
			cbPrice.getSelectedIndex() == 0	) {
			JOptionPane.showMessageDialog(null,"Both Ticker and Price must be selected");
			return;
		}
		if(cbHigh.getSelectedIndex() != 0 && (cbHigh.getSelectedIndex()==cbTicker.getSelectedIndex()
				||cbHigh.getSelectedIndex()==cbVolume.getSelectedIndex())) {
			JOptionPane.showMessageDialog(null,"High field can not be same as volume or ticker");
			return;
		}
		if(cbLow.getSelectedIndex() != 0 && (cbLow.getSelectedIndex()==cbTicker.getSelectedIndex()
				||cbLow.getSelectedIndex()==cbVolume.getSelectedIndex())) {
			JOptionPane.showMessageDialog(null,"Low field can not be same as volume or ticker");
			return;
		}
		if(cbVolume.getSelectedIndex() != 0 && (cbVolume.getSelectedIndex()==cbTicker.getSelectedIndex()
				||cbVolume.getSelectedIndex()==cbPrice.getSelectedIndex())) {
			JOptionPane.showMessageDialog(null,"Volume field can not be same as price or ticker");
			return;
		}
		
	      //Create and set up the window.
		  objParms.print();
		  JFrame frame= new loadPricesWindow(txtFileName, objParms);
	      frame.setTitle("Load Security Prices - Build "+Main.buildStr);
	      frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
	      frame.setVisible(true);
	      return;
	  }
	  private void addMult() {
			JPanel panInput = new JPanel(new GridBagLayout());
			JLabel lblExch = new JLabel("Enter Exchange (no .)");
			GridBagConstraints gbc_lblExch = new GridBagConstraints();
			gbc_lblExch.insets = new Insets(10, 10, 10, 10);
			gbc_lblExch.gridx = 0;
			gbc_lblExch.gridy = 0;
			panInput.add(lblExch,gbc_lblExch);
			JTextField txtExch = new JTextField();
			txtExch.setColumns(5);
			GridBagConstraints gbc_txtExch = new GridBagConstraints();
			gbc_txtExch.insets = new Insets(10, 10, 10, 10);
			gbc_txtExch.gridx = 1;
			gbc_txtExch.gridy = 0;
			panInput.add(txtExch,gbc_txtExch);
			JLabel lblMult = new JLabel("Multiplier");
			GridBagConstraints gbc_lblMult = new GridBagConstraints();
			gbc_lblMult.insets = new Insets(10, 10, 10, 10);
			gbc_lblMult.gridx = 2;
			gbc_lblMult.gridy = 0;
			panInput.add(lblMult,gbc_lblMult);
			JComboBox<Integer> cbMult = new JComboBox<Integer>(Parameters.arMultipliers);
			GridBagConstraints gbc_cbMult = new GridBagConstraints();
			gbc_cbMult.insets = new Insets(10, 10, 10, 10);
			gbc_cbMult.gridx = 3;
			gbc_cbMult.gridy = 0;
			panInput.add(cbMult,gbc_cbMult);
			while (true) {
				int iResult = JOptionPane.showConfirmDialog(null,  panInput, 
						"Enter Exchange and Multiplier", JOptionPane.OK_CANCEL_OPTION);
				if (iResult == JOptionPane.OK_OPTION){
					String strExch = txtExch.getText();
					if (strExch.equals("")) {
						JOptionPane.showMessageDialog(null, "Exchange can not be blank");
						continue;
					}
					objParms.addExchange(strExch, cbMult.getSelectedIndex());
					break;
				}
				if (iResult == JOptionPane.CANCEL_OPTION)
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
			JLabel lblExch = new JLabel("Enter Prefix)");
			GridBagConstraints gbc_lblExch = new GridBagConstraints();
			gbc_lblExch.insets = new Insets(10, 10, 10, 10);
			gbc_lblExch.gridx = 0;
			gbc_lblExch.gridy = 0;
			panInput.add(lblExch,gbc_lblExch);
			JTextField txtPrefix = new JTextField();
			txtPrefix.setColumns(5);
			GridBagConstraints gbc_txtPrefix = new GridBagConstraints();
			gbc_txtPrefix.insets = new Insets(10, 10, 10, 10);
			gbc_txtPrefix.gridx = 1;
			gbc_txtPrefix.gridy = 0;
			panInput.add(txtPrefix,gbc_txtPrefix);
			while (true) {
				int iResult = JOptionPane.showConfirmDialog(null,  panInput, 
						"Enter Prefix", JOptionPane.OK_CANCEL_OPTION);
				if (iResult == JOptionPane.OK_OPTION){
					String strPrefix = txtPrefix.getText();
					if (strPrefix.equals("")) {
						JOptionPane.showMessageDialog(null, "Prefix can not be blank");
						continue;
					}
					objParms.addPrefix(strPrefix);
					break;
				}
				if (iResult == JOptionPane.CANCEL_OPTION)
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
			int iRow = 2;
			mapCombos.clear();
			mapDelete.clear();
			for (ExchangeLine objLine : listLines) {
				JLabel lblExch = new JLabel(objLine.getExchange());
				GridBagConstraints gbc_lblExch = new GridBagConstraints();
				gbc_lblExch.insets = new Insets(10, 10, 10, 10);
				gbc_lblExch.gridx = 1;
				gbc_lblExch.gridy = iRow;
				panMult.add(lblExch, gbc_lblExch);
				JComboBox<Integer> cbMult = new JComboBox<Integer>(Parameters.arMultipliers);
				GridBagConstraints gbc_cbMultiplier = new GridBagConstraints();
				gbc_cbMultiplier.insets = new Insets(10, 10, 10, 10);
				gbc_cbMultiplier.gridx = 2;
				gbc_cbMultiplier.gridy = iRow;
				cbMult.setSelectedIndex(objLine.getMultiplier());
				mapCombos.put(cbMult,objLine.getExchange());
				cbMult.addActionListener(new ActionListener () {
					@Override
					public void actionPerformed(ActionEvent e) {
						@SuppressWarnings("unchecked")
						JComboBox<Integer> cbMultT = (JComboBox<Integer>) e.getSource();
						String strExch = mapCombos.get(cbMultT);
						objParms.updateLine(strExch, cbMultT.getSelectedIndex());
					}
				});
				panMult.add(cbMult, gbc_cbMultiplier );
				JButton btnDelete = new JButton("Delete");
				GridBagConstraints gbc_btnDelete = new GridBagConstraints();
				gbc_btnDelete.insets = new Insets(10, 10, 10, 10);
				gbc_btnDelete.gridx = 3;
				gbc_btnDelete.gridy = iRow;
				btnDelete.addActionListener(new ActionListener () {
					@Override
					public void actionPerformed(ActionEvent e) {
						deleteExchange(e);
					}
				});
				panMult.add(btnDelete,gbc_btnDelete);
				mapDelete.put(btnDelete,objLine.getExchange());
				
				iRow++;
			}
			btnAdd = new JButton("Add Exchange Multiplier");
			GridBagConstraints gbc_butAdd= new GridBagConstraints();
			gbc_butAdd.insets = new Insets(10, 10, 10, 10);
			gbc_butAdd.gridx = 0;
			gbc_butAdd.gridy = iRow;
			btnAdd.addActionListener(new ActionListener () {
				@Override
				public void actionPerformed(ActionEvent e) {
					addMult();
				}
			});
			panMult.add(btnAdd, gbc_butAdd);

	  }
	  private void buildPrefixes() {
			int iRow = 2;
			mapPrefixes.clear();
			mapPrefDelete.clear();
			for (String strPrefix : listPrefixes) {
				JLabel lblPrefix = new JLabel(strPrefix);
				GridBagConstraints gbc_lblPrefix = new GridBagConstraints();
				gbc_lblPrefix.insets = new Insets(10, 10, 10, 10);
				gbc_lblPrefix.gridx = 1;
				gbc_lblPrefix.gridy = iRow;
				panPrefix.add(lblPrefix, gbc_lblPrefix);
				JButton btnDelete = new JButton("Delete");
				GridBagConstraints gbc_btnDelete = new GridBagConstraints();
				gbc_btnDelete.insets = new Insets(10, 10, 10, 10);
				gbc_btnDelete.gridx = 2;
				gbc_btnDelete.gridy = iRow;
				btnDelete.addActionListener(new ActionListener () {
					@Override
					public void actionPerformed(ActionEvent e) {
						deletePrefix(e);
					}
				});
				panPrefix.add(btnDelete,gbc_btnDelete);
				mapPrefDelete.put(btnDelete,strPrefix);		
				iRow++;
			}
			btnAdd = new JButton("Add Prefix");
			GridBagConstraints gbc_butAdd= new GridBagConstraints();
			gbc_butAdd.insets = new Insets(10, 10, 10, 10);
			gbc_butAdd.gridx = 0;
			gbc_butAdd.gridy = iRow;
			btnAdd.addActionListener(new ActionListener () {
				@Override
				public void actionPerformed(ActionEvent e) {
					addPrefix();
				}
			});
			panPrefix.add(btnAdd, gbc_butAdd);

	  }	
	  private void deleteExchange(ActionEvent e){
			String strExch = mapDelete.get(e.getSource());
			objParms.deleteExchange(strExch);
			panMult.removeAll();
			buildLines();
			panMult.revalidate();
			JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
			topFrame.pack();
		  
	  }
	  private void deletePrefix(ActionEvent e){
			String strExch = mapPrefDelete.get(e.getSource());
			objParms.deletePrefix(strExch);
			panPrefix.removeAll();
			buildPrefixes();
			panPrefix.revalidate();
			JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
			topFrame.pack();
		  
	  }
	  private void close() {
		  this.setVisible(false);
		  if (objLoadWindow != null)
			  objLoadWindow.close();
		  JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		  topFrame.dispose();
		  
	  }
	@Override
	public void actionPerformed(ActionEvent aeMenu) {
		JMenuItem miSource = (JMenuItem)(aeMenu.getSource());
		if (miSource == miOnline) {
			String url = "http://github.com/mrbray99/moneydanceproduction/wiki/Security-Price-and-History-Load";
			mdGUI.showInternetURL(url);
		    }
		if (miSource == rbOff){
			objDebug.setDebugLevel(MRBDebug.OFF);
			rbOff.setSelected(true);
		}
		if (miSource == rbInfo){
			objDebug.setDebugLevel(MRBDebug.INFO);
			objDebug.debug("FileSelectWindow", "actionPerformed", MRBDebug.INFO, "Debug turned to Info");
			rbInfo.setSelected(true);
		}
		if (miSource == rbSumm){
			objDebug.setDebugLevel(MRBDebug.SUMMARY);
			objDebug.debug("FileSelectWindow", "actionPerformed", MRBDebug.SUMMARY, "Debug turned to Summary");
			rbSumm.setSelected(true);
		}
		if (miSource == rbDet){
			objDebug.setDebugLevel(MRBDebug.DETAILED);
			objDebug.debug("FileSelectWindow", "actionPerformed", MRBDebug.DETAILED, "Debug turned to Detailed");
			rbDet.setSelected(true);
		}


		
	}
	private Image getIcon(String icon) {
		try {
			ClassLoader cl = getClass().getClassLoader();
			java.io.InputStream in =
					cl.getResourceAsStream("/com/moneydance/modules/features/securitypriceload/" + icon);
			if (in != null) {
				ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
				byte buf[] = new byte[256];
				int n = 0;
				while ((n = in.read(buf, 0, buf.length)) >= 0)
					bout.write(buf, 0, n);
				return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
			}
		} catch (Throwable e) {
		}
		return null;
	}

}
