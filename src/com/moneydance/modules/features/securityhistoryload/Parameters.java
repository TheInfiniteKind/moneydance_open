package com.moneydance.modules.features.securityhistoryload;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import com.infinitekind.moneydance.model.AccountBook;

public class Parameters implements Serializable{
	/*
	 * Static and transient fields are not stored 
	 */
	private transient AccountBook abCurAcctBook;
	private transient File fiCurFolder;
	private transient FileInputStream fiCurInFile;
	private transient FileOutputStream fiCurOutFile;
	private transient String strFileName;
	public transient static Integer [] arMultipliers = {-4,-3,-2,-1,0,1,2,3,4};
	public transient static Integer [] arDecimal = {4,5,6,7,8};
	public transient static String [] arMaximums = {"No Limit","5","6","7","8","9"};
	public transient static String strDoNotLoad ="Do not load";
	/*
     * The following fields are stored
     */

	private String strTicker;
	private String strPrice;
	private String strHigh;
	private String strLow;
	private String strVolume;
	private String strDate;
	private int iMaxChar;
	private int iMultiplier;
	private int iDecimal;
	private boolean bExch;
	private boolean bZero;
	private boolean bCurrency;
	private boolean bCase;
	private String strDirectory;
	private String strLastFile;
	private int delimiter;
	private List<ExchangeLine> listExchangeLines;
	private List<String> listPrefixes;
	public Parameters() {
		/*
		 * determine if file already exists
		 */
		abCurAcctBook = Main.context.getCurrentAccountBook();
		fiCurFolder = abCurAcctBook.getRootFolder();
		strFileName = fiCurFolder.getAbsolutePath()+"\\SecureHistoryLoad.bpam";
		try {
			fiCurInFile = new FileInputStream(strFileName);
			ObjectInputStream ois = new ObjectInputStream(fiCurInFile);
			/*
			 * file exists, copy temporary object to this object
			 */
			Parameters objTemp = (Parameters) ois.readObject();
			this.strTicker = objTemp.strTicker;
			this.strPrice = objTemp.strPrice;
			this.bExch = objTemp.bExch;
			this.bZero = objTemp.bZero;
			this.bCurrency = objTemp.bCurrency;
			this.bCase = objTemp.bCase;
			this.iMultiplier = objTemp.iMultiplier;
			this.iDecimal = objTemp.iDecimal;
			this.strHigh = objTemp.strHigh;
			this.strLow = objTemp.strLow;
			this.strVolume = objTemp.strVolume;
			this.strDate = objTemp.strDate;
			this.iMaxChar = objTemp.iMaxChar;
			this.strDirectory = objTemp.strDirectory;
			this.strLastFile = objTemp.strLastFile;
			this.delimiter = objTemp.delimiter;
			this.listExchangeLines = objTemp.listExchangeLines;
			if (this.listExchangeLines == null)
				this.listExchangeLines = new ArrayList<ExchangeLine>();
			this.listPrefixes = objTemp.listPrefixes;
			if (this.listPrefixes == null)
				this.listPrefixes = new ArrayList<String>();
			fiCurInFile.close();
		}
		catch (IOException | ClassNotFoundException ioException) {
			/*
			 * file does not exist, initialize fields
			 */
			listExchangeLines = new ArrayList<ExchangeLine>();
			listPrefixes = new ArrayList<String>();
			strTicker = "";
			strPrice = "";
			strHigh = strDoNotLoad;
			strLow = strDoNotLoad;
			strVolume = strDoNotLoad;
			strDate = "";
			iMaxChar = 0;
			bExch = false;
			bZero = false;
			bCurrency = false;
			bCase = false;
			iMultiplier = 4;
			iDecimal = 0;
			strDirectory = "";
			strLastFile = "";
			delimiter = 0;
			/*
			 * create the file
			 */
			try {
				fiCurOutFile = new FileOutputStream(strFileName);
				ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
				oos.writeObject(this);
				fiCurOutFile.close();
			}
			catch(IOException i)
			{
				i.printStackTrace();
			}
		}		
	}
	public String getTicker() {
		return strTicker;
	}
	public String getPrice() {
		return strPrice;
	}
	public boolean getExch() {
		return bExch;
	}
	public String getHigh () {
		return strHigh;
	}
	public String getLow () {
		return strLow;
	}
	public String getVolume () {
		return strVolume;
	}
	public String getDate () {
		return strDate;
	}
	public boolean getZero () {
		return bZero;
	}
	public boolean getCurrency () {
		return bCurrency;
	}
	public boolean getCase () {
		return bCase;
	}
	public int getDefaultMult () {
		return iMultiplier;
	}
	public int getDecimal () {
		return iDecimal;
	}
	public int getMaxChar () {
		return iMaxChar;
	}
	public String getDirectory () {
		return strDirectory;
	}
	public String getLastFile () {
		return strLastFile;
	}

	public int getDelimiter() {
		return delimiter;
	}

	public List<ExchangeLine> getMultipliers() {
		return listExchangeLines;
	}
	public List<String> getPrefixes() {
		return listPrefixes;
	}
	public void setTicker(String strTickerp) {
		strTicker = strTickerp;
	}
	public void setPrice(String strPricep) {
		strPrice = strPricep;
	}
	public void setExch(boolean bExchp) {
		bExch = bExchp;
	}
	public void setHigh (String strHighp) {
		strHigh= strHighp;
	}
	public void setLow (String strLowp) {
		strLow = strLowp;
	}
	public void setVolume (String strVolumep) {
		strVolume = strVolumep;
	}
	public void setDate (String strDatep) {
		strDate = strDatep;
	}
	public void setZero (boolean bZerop) {
		bZero = bZerop;
	}
	public void setCurrency (boolean bCurrencyp) {
		bCurrency = bCurrencyp;
	}
	public void setCase (boolean bCasep) {
		bCase = bCasep;
	}
	public void setDefaultMult(int iMultiplierp){
		iMultiplier = iMultiplierp;
	}
	public void setDecimal (int iDecimalp) {
		iDecimal = iDecimalp;
	}
	public void setMaxChar(int iMaxCharp){
		iMaxChar = iMaxCharp;
	}
	public void setDirectory (String strDirectoryp){
		strDirectory = strDirectoryp;
	}
	public void setLastFile (String strLastFilep){
		strLastFile = strLastFilep;
	}

	public void setDelimiter(int delimiter) {
		this.delimiter = delimiter;
	}

	public void addExchange(String strExch, int iMultiplier) {
		ExchangeLine objLine = new ExchangeLine(strExch, iMultiplier);
		if (listExchangeLines == null)
			listExchangeLines = new ArrayList<ExchangeLine>();
		listExchangeLines.add(objLine);
	}
	public void addPrefix(String strPrefix) {
		if (listPrefixes == null)
			listPrefixes = new ArrayList<String>();
		listPrefixes.add(strPrefix);
	}
	public int getMultiplier(String strExchange) {
		int iReturn = iMultiplier;
		for (ExchangeLine objLine :listExchangeLines) {
			if (objLine.getExchange().equals(strExchange)){
				iReturn = objLine.getMultiplier();
				break;
			}
		}
		return arMultipliers[iReturn];
	}
	public void updateLine(String strExchange, int iMultiplierp){
		for (ExchangeLine objLine :listExchangeLines) {
			if (objLine.getExchange().equals(strExchange))
				objLine.setMultiplier(iMultiplierp);
		}

	}
	public void deleteExchange(String strExchange){
		for (ExchangeLine objLine :listExchangeLines) {
			if (objLine.getExchange().equals(strExchange)) {
				listExchangeLines.remove(objLine);
				break;
			}
		}

	}
	public void deletePrefix(String strPrefixp){
		for (String strPrefix :listPrefixes) {
			if (strPrefix.equals(strPrefixp)) {
				listPrefixes.remove(strPrefixp);
				break;
			}
		}

	}
	public List<ExchangeLine> getLines() {
		return listExchangeLines;
	}
	
	public void save() {
		/*
		 * Save the parameters into the specified file
		 */
		try {
			fiCurOutFile = new FileOutputStream(strFileName);
			ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
			oos.writeObject(this);
			oos.close();
			fiCurOutFile.close();
		}
		catch(IOException i)
		{
			i.printStackTrace();
		}
	}

}
