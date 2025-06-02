package  com.moneydance.modules.features.securitypriceload;

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
import com.moneydance.modules.features.mrbutil.MRBDebug;

public class Parameters implements Serializable{
	/*
	 * Static and transient fields are not stored 
	 */
	private static final long serialVersionUID = 1L;
	private transient AccountBook curAcctBook;
	private transient File curFolder;
	private transient FileInputStream curInFile;
	private transient FileOutputStream curOutFile;
	private transient String fileName;
	public transient static Integer [] arMultipliers = {-4,-3,-2,-1,0,1,2,3,4};
	public transient static Integer [] arDecimal = {4,5,6,7,8};
	public transient static String [] arMaximums = {"No Limit","5","6","7","8","9"};
	public transient static String strDoNotLoad ="Do not load";
	private transient MRBDebug debugInst = Main.debugInst;
	/*
     * The following fields are stored
     */

	private String strTicker;
	private String strPrice;
	private String strHigh;
	private String strLow;
	private String strVolume;
	private int iMaxChar;
	private int iMultiplier;
	private int iDecimal;
	private boolean bExch;
	private boolean bZero;
	private boolean bCurrency;
	private boolean bCase;
	private String strDirectory;
	private String strLastFile;
	private List<ExchangeLine> listExchangeLines;
	private List<String> listPrefixes;
	public Parameters() {
		/*
		 * determine if file already exists
		 */
		curAcctBook = Main.context.getCurrentAccountBook();
		curFolder = curAcctBook.getRootFolder();
		fileName = curFolder.getAbsolutePath()+"\\SecurePriceLoad.bpam";
		try {
			curInFile = new FileInputStream(fileName);
			ObjectInputStream ois = new ObjectInputStream(curInFile);
			/*
			 * file exists, copy temporary object to this object
			 */
			Parameters objTemp = (Parameters) ois.readObject();
			debugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Parameters found "+fileName);
			
			this.strTicker = objTemp.strTicker;
			debugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Ticker field "+strTicker);
			this.strPrice = objTemp.strPrice;
			debugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Price Field "+strPrice);
			this.bExch = objTemp.bExch;
			this.bZero = objTemp.bZero;
			this.bCurrency = objTemp.bCurrency;
			this.bCase = objTemp.bCase;
			this.iMultiplier = objTemp.iMultiplier;
			this.iDecimal = objTemp.iDecimal;
			this.strHigh = objTemp.strHigh;
			this.strLow = objTemp.strLow;
			this.strVolume = objTemp.strVolume;
			this.iMaxChar = objTemp.iMaxChar;
			this.strDirectory = objTemp.strDirectory;
			debugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Dierctory "+strDirectory);
			this.strLastFile = objTemp.strLastFile;
			debugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Last File "+strLastFile);
			this.listExchangeLines = objTemp.listExchangeLines;
			if (this.listExchangeLines == null)
				this.listExchangeLines = new ArrayList<ExchangeLine>();
			this.listPrefixes = objTemp.listPrefixes;
			if (this.listPrefixes == null)
				this.listPrefixes = new ArrayList<String>();
			curInFile.close();
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
			iMaxChar = 0;
			bExch = false;
			bZero = false;
			bCurrency = false;
			bCase = false;
			iMultiplier = 4;
			iDecimal = 0;
			strDirectory = "";
			strLastFile = "";
			/*
			 * create the file
			 */
			try {
				curOutFile = new FileOutputStream(fileName);
				ObjectOutputStream oos = new ObjectOutputStream(curOutFile);
				oos.writeObject(this);
				curOutFile.close();
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
		debugInst.debug("Parameters", "getLastFile", MRBDebug.DETAILED, "Last File "+strLastFile);
		return strLastFile;
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
		debugInst.debug("Parameters", "setLastFile", MRBDebug.DETAILED, "Last File "+strLastFilep);
		strLastFile = strLastFilep;
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
	
	@SuppressWarnings("unused")
	public void save() {
		/*
		 * Save the parameters into the specified file
		 */
		try {
			curOutFile = new FileOutputStream(fileName);
			debugInst.debug("Parameters", "save", MRBDebug.DETAILED, fileName);
			ObjectOutputStream oos = new ObjectOutputStream(curOutFile);
			if (oos == null) 
				debugInst.debug("Parameters", "save", MRBDebug.DETAILED, "no output stream");
			oos.writeObject(this);
			oos.close();
			curOutFile.close();
		}
		catch(IOException i)
		{
			i.printStackTrace();
		}
	}
	public void print() {
		debugInst.debug("Parameters","Ticker",MRBDebug.INFO,strTicker);
		debugInst.debug("Parameters","Price",MRBDebug.INFO,strPrice);
		debugInst.debug("Parameters","High",MRBDebug.INFO,strHigh);
		debugInst.debug("Parameters","Low",MRBDebug.INFO,strLow);
		debugInst.debug("Parameters","Volume",MRBDebug.INFO,strVolume);
		debugInst.debug("Parameters","Exchange",MRBDebug.INFO,bExch ? "True": "false");
		debugInst.debug("Parameters","Zero",MRBDebug.INFO,bZero ? "True": "false");
		debugInst.debug("Parameters","Currency",MRBDebug.INFO,bCurrency ? "True": "false");
		debugInst.debug("Parameters","Case",MRBDebug.INFO,bCase ? "True": "false");
	}

}
