/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;
import java.util.SortedMap;
import java.util.TreeMap;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonParseException;
import com.google.gson.reflect.TypeToken;
import com.google.gson.stream.JsonReader;
import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.modules.features.mrbutil.MRBDebug;

public class Parameters{
	/*
	 * Static and  fields are not stored 
	 */
	private  AccountBook curAcctBook;
	private  File curFolder;
	private  String fileName;
	public  static Integer [] alphaPlans = {1200, 600, 300, 150, 75, 5};  // fastest (paid) to slowest (free)
	public  static Integer [] multipliers = {-4,-3,-2,-1,0,1,2,3,4};
	public  static String[] CURRENCYDATES = {"Trade Date","Today's Date"};
	public  static int USETRADEDATE = 0;
	public  static int USETODAYSDATE = 1;
	public  static Integer [] decimals = {2,3,4,5,6,7,8};
	public  static String [] maximums = {"No Limit","6","7","8","9"};
	private  MRBDebug debugInst = Main.debugInst;
	private  String[] secSource = {Constants.DONOTLOAD,Constants.YAHOO,Constants.FT,Constants.YAHOOHIST,Constants.FTHIST,Constants.ALPHAVAN};
	private  String[] curSource = {Constants.DONOTLOAD,Constants.YAHOO,Constants.YAHOOHIST,Constants.FT,Constants.ALPHAVAN};
	private  List<NewAccountLine>listNewAccounts;
	private SortedMap<String, NewAccountLine> savedAccounts;
	private  NewParameters newParams;
	private  ExchangeList exchanges;
	private  PseudoList pseudoList;
	private  SortedMap<String, ExchangeLine> mapExchangeLines;
	private  SortedMap<String,PseudoCurrency> pseudoCurrencies;
	private  boolean addVolume;
	private  boolean history;
	private  boolean export;
	private  boolean exportAuto;
	private  String exportFolder;
	private  boolean isDirty;
	private  boolean overridePrice;
	private  Integer displayOption;
	private  Integer amtHistory;
	private  Integer timeOfRun;
	private String alphaAPIKey;
	private String uaParam;
  private Integer alphaPlan;
	private  char[] HEX_CHARS = "0123456789abcdef".toCharArray();

	private int noDecimals;
	private int newNoDecimals;
	private boolean includeZero;
	private boolean includeCurrency;
	private int currencyDate;
	private boolean roundPrices;
	private static Parameters thisObj=null;
	public Parameters() {
		curAcctBook = Main.context.getCurrentAccountBook();
		curFolder = curAcctBook.getRootFolder();
		/*
		 * Determine if the new file exists
		 */
		boolean createNew = false;
		isDirty = false;
		switch (findFile(curFolder)) {
		case NEW2 :
			fileName = curFolder.getAbsolutePath()+"/"+Constants.PARAMETERFILE2;
			try {
				JsonReader reader = new JsonReader(new FileReader(fileName,StandardCharsets.UTF_8));
				debugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Parameters found "+fileName);
				newParams = new Gson().fromJson(reader,NewParameters.class);
					listNewAccounts = newParams.getListAccounts();
				reader.close();
			}
			catch (JsonParseException e) {
				debugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Parse Exception "+e.getMessage());
				createNew = true;
			}
			catch (IOException e){
				createNew = true;
			}
			break;
		default:
		case NONE :	
			createNew = true;
		
		}
		boolean currencyChanged = false;
		if (!createNew) {
			for (NewAccountLine line:listNewAccounts) {
				String name = line.getName();
				String hexstr = asHex(name.getBytes(StandardCharsets.UTF_8));
				if (line.isCurrency()) {
					line.setName(Constants.CURRENCYID+name.substring(3));
					continue;
				}
				if (name.length()<3)
					continue;
				if (name.substring(0, 2).equals(Constants.CURRENCYID)) {
					line.setCurrency(true);
					continue;
				}
				if ((hexstr.substring(0,1).compareTo("BB") > 0 && hexstr.substring(2,3).compareTo("BB")>0 && hexstr.substring(4,5).compareTo("BB")>0) ||
						hexstr.substring(0,6).equalsIgnoreCase("3f3f3f")){
					line.setName(Constants.CURRENCYID+name.substring(3));
					line.setCurrency(true);
					Main.debugInst.debug("Parameters","init",MRBDebug.INFO,"currency changed from "+hexstr.substring(0,6)+ " to new currency");
				}
			}
		}
		/*
		 * Column Widths name changed
		 */
		int [] columnWidths;
		columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME+".SEC."+Constants.CRNTCOLWIDTH);
		if (columnWidths.length == 0) {
			columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME+"."+Constants.CRNTCOLWIDTH);		
			if (columnWidths.length == 0)
				columnWidths = Constants.DEFAULTCOLWIDTH;
			else {
				if (columnWidths.length < Constants.NUMTABLECOLS) {
					int [] tempColWidths = Constants.DEFAULTCOLWIDTH;
					if (columnWidths.length >0)
						tempColWidths[0] = columnWidths[0];
					if (columnWidths.length >1)
						tempColWidths[1] = columnWidths[1];
					if (columnWidths.length >2)
						tempColWidths[3] = columnWidths[2];
					if (columnWidths.length >3)
						tempColWidths[4] = columnWidths[3];
					if (columnWidths.length >4)
						tempColWidths[5] = columnWidths[4];
					if (columnWidths.length >5)
						tempColWidths[6] = columnWidths[5];
					if (columnWidths.length >6)
						tempColWidths[7] = columnWidths[6];
					if (columnWidths.length >7)
						tempColWidths[8] = columnWidths[7];
					if (columnWidths.length >8)
						tempColWidths[9] = columnWidths[8];
					if (columnWidths.length >9)
						tempColWidths[10] = columnWidths[9];
					tempColWidths[11] =Constants.DEFAULTCOLWIDTH[11];
					if (columnWidths.length >11)
						tempColWidths[12] = columnWidths[10];
					if (columnWidths.length >12)
						tempColWidths[13] = columnWidths[11];
					columnWidths = tempColWidths;
				}
				Main.preferences.put(Constants.PROGRAMNAME+".SEC."+Constants.CRNTCOLWIDTH, columnWidths);
			}
		}
		columnWidths = Main.preferences.getIntArray(Constants.PROGRAMNAME+".CUR."+Constants.CRNTCOLWIDTH);
		if (columnWidths.length == 0) {
			columnWidths = Constants.DEFAULTCURCOLWIDTH;
			Main.preferences.put(Constants.PROGRAMNAME+".CUR."+Constants.CRNTCOLWIDTH, Constants.DEFAULTCURCOLWIDTH);
		}
		if (createNew) {
				/*
				 * file does not exist, initialize fields
				 */
				newParams = new  NewParameters();
				fileName = curFolder.getAbsolutePath()+"/"+Constants.PARAMETERFILE2;
			/*
			 * create the file
			 */
			try {
			   FileWriter writer = new FileWriter(fileName,StandardCharsets.UTF_8);
			   String jsonString = new Gson().toJson(newParams);
			   writer.write(jsonString);
			   writer.close();			  
             } catch (IOException i) {
				 i.printStackTrace();
	
             }
		}
		this.includeZero= newParams.isIncludeZero();
		this.includeCurrency= newParams.isIncludeCurrency();
		if(newParams.getNewNoDecimals() == -1)
			newParams.setNewNoDecimals(newParams.getNoDecimals()+4);
		this.newNoDecimals = newParams.getNewNoDecimals();
		this.noDecimals= newParams.getNewNoDecimals();
		this.listNewAccounts = newParams.getListAccounts();
		this.addVolume = newParams.isAddVolume();
		this.history = newParams.isHistory();
		this.export = newParams.isExport();
		this.exportAuto = newParams.isExportAuto();
		this.exportFolder = newParams.getExportFolder();
		this.roundPrices = newParams.isRoundPrices();
		this.overridePrice = newParams.isOverridePrice();
		this.amtHistory= newParams.getAmtHistory();
		this.displayOption=newParams.getDisplayOption();
		this.alphaAPIKey = newParams.getAlphaAPIKey();
		this.alphaPlan = newParams.getAlphaPlan();
		this.uaParam = newParams.getUaParam();

		savedAccounts = new TreeMap<>();
		buildAccounts();
		exchanges = new ExchangeList();
		exchanges.getData();
		mapExchangeLines = exchanges.getList();
		pseudoList = new PseudoList();
		pseudoList.getData();
		pseudoCurrencies = pseudoList.getList();
		if (currencyChanged)
			save();
		isDirty=false;
	}
	public static Parameters getParameters() {
		if (thisObj == null)
			thisObj = new Parameters();
		return thisObj;
	}
	public static void closeParameters() {
		thisObj = null;
	}
	public  String asHex(byte[] buf)
	{
	    char[] chars = new char[2 * buf.length];
	    for (int i = 0; i < buf.length; ++i)
	    {
	        chars[2 * i] = HEX_CHARS[(buf[i] & 0xF0) >>> 4];
	        chars[2 * i + 1] = HEX_CHARS[buf[i] & 0x0F];
	    }
	    return new String(chars);
	}
	private Constants.FILEFOUND findFile(File curFolder) {
		FileInputStream testFile;
		String fileName=curFolder.getAbsolutePath()+"/" +Constants.PARAMETERFILE2;
		try {
			testFile = new FileInputStream(fileName);
			testFile.close();
			debugInst.debug("Parameters", "findFile", MRBDebug.DETAILED, "New 2");
			return Constants.FILEFOUND.NEW2;
		}
		catch (IOException e) {
		}
		return Constants.FILEFOUND.NONE;
	}
	
    public SortedMap<String,PseudoCurrency> ReadPseudo() {
    	SortedMap<String,PseudoCurrency> configuration = new TreeMap<>();
        File file = DirectoryUtil.getCurrencyConfigurationFile();
        List<PseudoCurrency> list = new ArrayList<>();
        if (!file.exists()) {
            PseudoCurrency pCur = new PseudoCurrency();
            pCur.setPseudo("GBX");
            pCur.setMultiplier(0.01D);
            pCur.setReplacement("GBP");
            list.add(pCur);
            WritePseudo(list);
        } else {
            try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
                GsonBuilder gsonBuilder = new GsonBuilder();
                Gson gson = gsonBuilder.create();
                Type type = new TypeToken<List<PseudoCurrency>>() {}.getType();
                list = gson.fromJson(reader,type);
            } catch (IOException e) {
    			debugInst.debug("Parameters", "ReadPseudo", MRBDebug.INFO, "Problem reading pseudo currency file "+e.getMessage());       	
             }
        }
        for (PseudoCurrency curr :list){
        	configuration.put(curr.getPseudo(), curr);
        }
        return configuration;
    }

    public void WritePseudo(List<PseudoCurrency>configuration) {
        if (configuration == null) {
            return;
        }
        File file = DirectoryUtil.getCurrencyConfigurationFile();
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(file))) {
            GsonBuilder gsonBuilder = new GsonBuilder();
            gsonBuilder.setPrettyPrinting();
            Gson gson = gsonBuilder.create();
            gson.toJson(configuration, writer);
        } catch (IOException e) {
			debugInst.debug("Parameters", "WritePseudo", MRBDebug.INFO, "Problem writing pseudo currency file "+e.getMessage());       	
        }
    }

	/*
	 * Zero
	 */
	public boolean getZero () {
		return includeZero;
	}
	public void setZero (boolean bZerop) {
		includeZero = bZerop;
		isDirty=true;
	}
	/*
	 * Currency
	 */
	public boolean getCurrency () {
		return includeCurrency;
	}
	public void setCurrency (boolean includeCurrencyp) {
		includeCurrency = includeCurrencyp;
		isDirty=true;
	}
	/*
	 * add Volume figures
	 */
	public boolean getAddVolume() {
		return addVolume;
	}
	public void setAddVolume(boolean addVolumep){
		addVolume = addVolumep;
		isDirty=true;
	}
	/*
	 * include history
	 */
	public boolean getHistory() {
		return history;
	}
	public void setHistory(boolean historyp){
		history = historyp;
		isDirty=true;
	}
	public boolean isExport() {
		return export;
	}
	public void setExport(boolean export) {
		this.export = export;
		isDirty=true;
	}
	public boolean isExportAuto() {
		return exportAuto;
	}
	public void setExportAuto(boolean exportAuto) {
		this.exportAuto = exportAuto;
		isDirty=true;
	}
	public String getExportFolder() {
		return exportFolder;
	}
	public void setExportFolder(String exportFolder) {
		this.exportFolder = exportFolder;
		isDirty=true;
	}
	/*
	 * Decimal
	 */
	public int getDecimal () {
		return newNoDecimals;
	}
	public void setDecimal (int noDecimalp) {
		isDirty=true;
		newNoDecimals = noDecimalp;
	}
	/*
	 * Round Prices flag
	 */
	public boolean isRoundPrices() {
		return roundPrices;
	}
	public void setRoundPrices(boolean roundPrices) {
		this.roundPrices = roundPrices;
		isDirty=true;
	}
	/*
	 * Currency Date
	 */
	public int getCurrencyDate () {
		return currencyDate;
	}
	public void setCurrencyDate (int currencyDatep) {
		currencyDate = currencyDatep;
		isDirty=true;
	}
	/*
	 * override Price flag
	 */

	public boolean isOverridePrice() {
		return overridePrice;
	}
	public void setOverridePrice(boolean overridePrice) {
		this.overridePrice = overridePrice;
		isDirty=true;
	}
	
	public boolean getOverridePrice() {
		return overridePrice;
	}
	public Constants.CurrencyDisplay getDisplayOption() {
		if (displayOption==0)
			return Constants.CurrencyDisplay.SAME;
		return Constants.CurrencyDisplay.SEPARATE;
	}
	public void setDisplayOption(Constants.CurrencyDisplay displayOption) {
		this.displayOption = displayOption.getNum();
		isDirty=true;
	}
	public Integer getAmtHistory() {
		return amtHistory;
	}
	public void setAmtHistory(Integer amtHistory) {
		this.amtHistory = amtHistory;
		isDirty=true;
	}
	public Integer getTimeOfRun() {
		return timeOfRun;
	}
	public void setTimeOfRun(Integer timeOfRun) {
		this.timeOfRun = timeOfRun;
		isDirty=true;
	}
	public String [] getSourceArray() {
		return secSource;
	}
	public String [] getCurSourceArray() {
		return curSource;
	}
	public SortedMap<String,PseudoCurrency> getPseudoCurrencies(){
		return pseudoCurrencies;
	}
	public SortedMap<String,ExchangeLine> getExchanges(){
		return mapExchangeLines;
	}
	/*
  	 * Alpha Vantage API Key
	 */

	public String getAlphaAPIKey() {
		return alphaAPIKey;
	}

	public void setAlphaAPIKey(String alphaAPIKey) {
		this.alphaAPIKey = alphaAPIKey;
		isDirty=true;
	}
	/*
  	 * Alpha Vantage API Plan ID
	 */

	public Integer getAlphaPlan() {
    // if not set or zero then pass back the default / fastest... (plans are set highest to lowest - the free is at the end)
    return (alphaPlan == null || alphaPlan < Parameters.alphaPlans[Parameters.alphaPlans.length - 1]) ? Parameters.alphaPlans[0] : alphaPlan;
	}

	public void setAlphaPlan(Integer alphaPlan) {
		this.alphaPlan = alphaPlan;
		isDirty=true;
	}
	/*
	 * User Agent
	 */

	public String getUaParam() {
		return uaParam;
	}

	public void setUaParam(String uaParam) {
		this.uaParam = uaParam;
		isDirty=true;
	}


	/*
	 * Accounts
	 * 
	 * Only valid sources are stored.   'Do Not Load' is not stored
	 */
	private void buildAccounts() {
		if (listNewAccounts == null)
			listNewAccounts = new ArrayList<>();
		for (NewAccountLine alTemp:listNewAccounts) {
			if (alTemp.getSource()!= 0 || alTemp.getFtAlternate()!=null || alTemp.getYahooAlternate()!=null|| alTemp.getAlphaAlternate()!=null || alTemp.getExchange()!=null) {
				savedAccounts.put(alTemp.getName(),alTemp);
			}
		}
	}
	
	public List<NewAccountLine> getAccountsList() {
		return listNewAccounts;
	}
	public SortedMap<String,NewAccountLine> getSavedAccounts() {
		return savedAccounts;
	}
	public String getNewTicker(String ticker, String exchange,String alternate, int source){
		debugInst.debug("Parameters", "getNewTicker", MRBDebug.DETAILED, "Ticker: "+ticker+" Exchange: "+exchange+" alternate: "+alternate);;
		String newTicker;
		if (alternate == null || alternate.isBlank())
			newTicker = ticker;
		else
			newTicker = alternate;
		if (exchange==null|| exchange.isBlank())
			return newTicker;
		ExchangeLine line = mapExchangeLines.get(exchange);
		if (line!=  null) {
			if (source == Constants.YAHOOINDEX || source == Constants.YAHOOHISTINDEX)
				newTicker = line.getYahooPrefix()+newTicker+line.getYahooSuffix();
			if (source == Constants.FTINDEX || source ==Constants.FTHISTINDEX)
				newTicker = line.getFtPrefix()+newTicker+line.getFtSuffix();
			if (source == Constants.ALPHAINDEX)
				newTicker = line.getAlphaPrefix()+newTicker+line.getAlphaSuffix();
		}
		return newTicker;
	}
	public String getExchangeCurrency(String exchange){
		ExchangeLine line = mapExchangeLines.get(exchange);
		if (line!=  null) return line.getCurrency();
		return null;
	}
	public void setDirty(boolean dirty) {
		this.isDirty=dirty;
	}
	public boolean paramsChanged() {
		return isDirty;
	}
	public void saveAccountSources(SortedMap<String,NewAccountLine>sources) {
		NewParameters tempParams=null;
		fileName = curFolder.getAbsolutePath()+"/"+Constants.PARAMETERFILE2;
		try {
			JsonReader reader = new JsonReader(new FileReader(fileName,StandardCharsets.UTF_8));
			debugInst.debug("Parameters", "saveAccountSource", MRBDebug.DETAILED, "Parameters found "+fileName);
			tempParams = new Gson().fromJson(reader,NewParameters.class);
			listNewAccounts = newParams.getListAccounts();
			reader.close();
		}
		catch (JsonParseException e) {
			debugInst.debug("Parameters", "saveAccountSource", MRBDebug.DETAILED, "Parse Exception "+e.getMessage());
		}
		catch (IOException e2){
			debugInst.debug("Parameters", "saveAccountSource", MRBDebug.DETAILED, "Parse Exception "+e2.getMessage());
		}
		List<NewAccountLine>newList = new ArrayList<NewAccountLine>();
		for (Entry<String,NewAccountLine> entry : sources.entrySet()) {
			NewAccountLine crntLine = entry.getValue();
			NewAccountLine newLine = new NewAccountLine();
			newLine.setName(entry.getKey());
			newLine.setCurrency(crntLine.isCurrency());
			newLine.setFtAlternate(crntLine.getFtAlternate());
			newLine.setYahooAlternate(crntLine.getYahooAlternate());
			newLine.setAlphaAlternate(crntLine.getAlphaAlternate());
			newLine.setExchange(crntLine.getExchange());
			newLine.setSource(crntLine.getSource());
			newList.add(newLine);
		}
		tempParams.setListAccounts(newList);
		/*
		 * create the file
		 */
		fileName = curFolder.getAbsolutePath()+"/"+Constants.PARAMETERFILE2;
		try {
			   FileWriter writer2 = new FileWriter(fileName,StandardCharsets.UTF_8);
			   String jsonString = new Gson().toJson(tempParams);
			   writer2.write(jsonString);
			   writer2.close();			  
          } catch (IOException i) {
					   i.printStackTrace();
	
          }
	}
	/*
	 * Save and reload
	 */
	public void save() {
		/*
		 * Save the parameters into the specified file
		 */
		newParams.setIncludeCurrency(includeCurrency);
		newParams.setIncludeZero(includeZero);
		newParams.setNoDecimals(noDecimals);
		newParams.setNewNoDecimals(newNoDecimals);
		newParams.setAddVolume(addVolume);
		newParams.setHistory(history);
		newParams.setExportAuto(exportAuto);
		newParams.setExportFolder(exportFolder);
		newParams.setExport(export);
		newParams.setRoundPrices(roundPrices);
		newParams.setOverridePrice(overridePrice);
		newParams.setAmtHistory(amtHistory);
		newParams.setDisplayOption(displayOption);
		newParams.setListAccounts(listNewAccounts);
		newParams.setAlphaAPIKey(alphaAPIKey);
		newParams.setAlphaPlan(alphaPlan);
		newParams.setUaParam(uaParam);

		/*
		 * create the file
		 */
		fileName = curFolder.getAbsolutePath()+"/"+Constants.PARAMETERFILE2;
		try {
			   FileWriter writer2 = new FileWriter(fileName,StandardCharsets.UTF_8);
			   String jsonString = new Gson().toJson(newParams);
			   writer2.write(jsonString);
			   writer2.close();			  
          } catch (IOException i) {
					   i.printStackTrace();
	
          }
		isDirty = false;
	}
	public void reloadValues() {
		this.includeZero= newParams.isIncludeZero();
		this.includeCurrency= newParams.isIncludeCurrency();
		if(newParams.getNewNoDecimals() == -1)
			newParams.setNewNoDecimals(newParams.getNoDecimals()+4);
		this.newNoDecimals = newParams.getNewNoDecimals();
		this.noDecimals= newParams.getNewNoDecimals();
		this.listNewAccounts = newParams.getListAccounts();
		this.addVolume = newParams.isAddVolume();
		this.history = newParams.isHistory();
		this.export = newParams.isExport();
		this.exportAuto = newParams.isExportAuto();
		this.exportFolder = newParams.getExportFolder();
		this.roundPrices = newParams.isRoundPrices();
		this.overridePrice = newParams.isOverridePrice();
		this.amtHistory= newParams.getAmtHistory();
		this.alphaAPIKey= newParams.getAlphaAPIKey();
		this.alphaPlan= newParams.getAlphaPlan();
		this.uaParam= newParams.getUaParam();
		this.displayOption=newParams.getDisplayOption();
		isDirty=false;
	}

}
