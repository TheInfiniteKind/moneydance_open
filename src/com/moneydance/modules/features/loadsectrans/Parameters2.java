package com.moneydance.modules.features.loadsectrans;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import com.google.gson.*;

import com.google.gson.stream.JsonReader;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;

public class Parameters2 {
	/*
	 * Static and transient fields are not stored 
	 */
	private AccountBook curAcctBook;
	private File curFolder;
	private JsonReader curInFile;
	private FileOutputStream curOutFile;
	private String fileName;
	private Gson gson;
	private Parameters parameters;
	private ParametersFile parametersFile;
	/*
     * The following fields are stored in a ParametersFile object using Json
     */

	private String ticker;
	private String value;
	private String dateField;
	private String reference;
	private String desc;
	private String unitsField;
	private boolean stripExch;
	private List<FieldLine> fieldLines;
	public Parameters2() {
		/*
		 * determine if file already exists
		 */
		curAcctBook = Main.context.getRootAccount().getBook();
		curFolder = curAcctBook.getRootFolder();
		fileName = curFolder.getAbsolutePath()+"\\SecureTranLoad.bpam2";
		gson = new Gson();
		try {
			FileReader input = new FileReader(fileName);
			curInFile = new JsonReader(input);
			/*
			 * file exists, copy temporary object to this object
			 */
			parametersFile = (ParametersFile)  gson.fromJson(curInFile, ParametersFile.class);
			if (parametersFile != null) {
				this.ticker = parametersFile.getTicker();
				this.value = parametersFile.getValue();
				this.dateField = parametersFile.getDateField();
				this.reference = parametersFile.getReference();
				this.desc = parametersFile.getDesc();
				this.stripExch = parametersFile.isStripExch();
				this.fieldLines = parametersFile.getFieldLines();
				this.unitsField = parametersFile.getUnit();
			}
			input.close();
		}
		catch (JsonSyntaxException | IOException e) {
			/*
			 * file does not exist, try old file			 */
			parameters = new Parameters();
			if (parameters != null){
				this.ticker = parameters.getTicker();
				this.value = parameters.getValue();
				this.dateField = parameters.getDate();
				this.reference = parameters.getReference();
				this.desc = parameters.getDesc();
				this.stripExch = parameters.getExch();
				this.fieldLines = parameters.getLines();
				return;
			}
			fieldLines = new ArrayList<FieldLine>();
			/*
			 * create the file
			 */
			save();
		}		
	}
	public String getTicker() {
		return ticker;
	}
	public String getValue() {
		return value;
	}
	public String getDate() {
		return dateField;
	}
	public String getReference() {
		return reference;
	}
	public String getDesc() {
		return desc;
	}
	public boolean getExch() {
		return stripExch;
	}
	public void setTicker(String ticker) {
		this.ticker = ticker;
	}
	public void setValue(String value) {
		this.value = value;
	}
	public void setDate(String dateField) {
		this.dateField = dateField;
	}
	public void setReference(String reference) {
		this.reference = reference;
	}
	public void setDesc(String desc) {
		this.desc = desc;
	}
	public void setExch(boolean stripExch) {
		this.stripExch = stripExch;
	}

	public String getUnitsField() {
		return unitsField;
	}

	public void setUnitsField(String unitsField) {
		this.unitsField = unitsField;
	}

	public void addField(String strType, String strAcctName, Account acct, int iTranType) {
		FieldLine objLine = new FieldLine(strType, strAcctName, acct, iTranType);
		if (fieldLines == null)
			fieldLines = new ArrayList<FieldLine>();
		fieldLines.add(objLine);
	}

	public void updateAccount(String strType, String strAcctName, Account acct){
		for (FieldLine objLine : fieldLines) {
			if (objLine.getType().equals(strType)) {
				objLine.setAccount(strAcctName,acct);
			}	
		}
	}

	public void updateTransType(String strType,int iTranType){
		for (FieldLine objLine : fieldLines) {
			if (objLine.getType().equals(strType)) {
				objLine.setTranType(iTranType);
			}	
		}
	}


	public void deleteField(String strType){
		for (FieldLine objLine : fieldLines) {
			if (objLine.getType().equals(strType)) {
				fieldLines.remove(objLine);
				break;
			}
		}
	}
	public List<FieldLine> getLines() {
		if (fieldLines == null)
			fieldLines = new ArrayList<>();
		return fieldLines;
	}
	
	public void save() {
		/*
		 * Save the parameters into the specified file
		 */
		try {
			parametersFile = new ParametersFile();
			parametersFile.setTicker(ticker);
			parametersFile.setValue(value);
			parametersFile.setDateField(dateField);
			parametersFile.setReference(reference);
			parametersFile.setDesc(desc);
			parametersFile.setStripExch(stripExch);
			parametersFile.setFieldLines(fieldLines);
			parametersFile.setUnit(unitsField);
			FileWriter output = new FileWriter(fileName);
			gson.toJson(parametersFile, output);
			output.close();
		}
		catch(JsonIOException |IOException i)
		{
			i.printStackTrace();
		}
	}
	public boolean isDefined(String strType){
		for (FieldLine objLine: fieldLines) {
			if (objLine.getType().equals(strType))
				return true;			
		}
		return false;
	}
	public boolean requiresTicker(String strType) {
		for (FieldLine objLine: fieldLines) {
			if (objLine.getType().equals(strType)) {
				switch (Constants.TRANSTYPES[objLine.getTranType()]) {
				case Constants.SECURITY_COST:
				case Constants.SECURITY_DIVIDEND:
				case Constants.SECURITY_INCOME:
				case Constants.INVESTMENT_BUY:
				case Constants.INVESTMENT_SELL:
					return true;
				default : 
					return false;
				}
			}
		}
		return false;					
	}
	public FieldLine matchType(String strType){
		for (FieldLine objLine: fieldLines) {
			if (objLine.getType().equals(strType))
				return objLine;			
		}
		return null;
	}}
