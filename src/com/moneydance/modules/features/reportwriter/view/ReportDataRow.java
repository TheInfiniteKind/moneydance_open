package com.moneydance.modules.features.reportwriter.view;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.gson.stream.JsonReader;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;

public class ReportDataRow {
	String name;
	Integer type;
	String template;
	String selection;
	String dataParms;
	String outputFileName;
	Boolean generate;
	Boolean overWrite;
	Boolean addDate;
	String delimiter;
	Boolean targetExcel;
	String fileName;
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public Integer getTypeInt() {
		return type;
	}
	public Constants.ReportType getType() {
		if (type == null)
			return Constants.ReportType.CSV;
		switch (type) {
		case 2-> {return Constants.ReportType.DATABASE;}
		case 3-> {return Constants.ReportType.SPREADSHEET;}
		default -> {
			return Constants.ReportType.CSV;}
		}
	}
	public void setType(Constants.ReportType typep) {
		if (typep == null) {
			type=1;
			return;
		}
		switch (typep) {
		case DATABASE -> type = 2;
		case SPREADSHEET -> type = 3;
		case CSV ->	type = 4;
		default -> type = 1;
		}
	}
	public String getTemplate() {
		return template;
	}
	public void setTemplate(String template) {
		this.template = template;
	}
	public String getSelection() {
		return selection;
	}
	public void setSelection(String selection) {
		this.selection = selection;
	}
	public String getDataParms() {
		return dataParms;
	}
	public void setDataParms(String dataParms) {
		this.dataParms = dataParms;
	}
	public String getOutputFileName() {
		if (overWrite == null)
			return "";
		return outputFileName;
	}
	public void setOutputFileName(String outputFileName) {
		this.outputFileName = outputFileName;
	}
	public Boolean getGenerate() {
		if (generate == null)
			return true;
		return generate;
	}
	public void setGenerate(Boolean generate) {
		this.generate = generate;
	}
	public Boolean getOverWrite() {
		if (overWrite == null)
			return false;
		return overWrite;
	}
	public void setOverWrite(Boolean overWrite) {
		this.overWrite = overWrite;
	}
	public Boolean getAddDate() {
		if (addDate == null)
			return false;
		return addDate;
	}
	
	
	public void setAddDate(Boolean addDate) {
		this.addDate = addDate;
	}
	public String getDelimiter() {
		if (delimiter == null)
			return ",";
		return delimiter;
	}
	public void setDelimiter(String delimiter) {
		this.delimiter = delimiter;
	}
	

	public Boolean getTargetExcel() {
		if (targetExcel == null)
			return false;
		return targetExcel;
	}
	public void setTargetExcel(Boolean targetExcel) {
		this.targetExcel = targetExcel;
	}
	public boolean loadRow(String name,Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		fileName = dir+"/"+name+Constants.REPORTEXTENSION;
		ReportDataRow row;
		try {
			JsonReader reader = new JsonReader(new FileReader(fileName));
			row = new Gson().fromJson(reader,ReportDataRow.class);
			reader.close();
			setName(row.getName());
			setType(row.getType());
			setSelection(row.getSelection());
			setTemplate(row.getTemplate());
			setDataParms(row.getDataParms());
			setOutputFileName(row.getOutputFileName());
			setOverWrite (row.getOverWrite());
			setAddDate(row.getAddDate());
			setGenerate(row.getGenerate());
			setDelimiter(row.getDelimiter());
			setTargetExcel(row.getTargetExcel());
			Main.rwDebugInst.debug("ReportDataRow", "loadRow", MRBDebug.DETAILED, "Row loaded "+name);
		}
		catch (JsonParseException e) {
			Main.rwDebugInst.debug("ReportDataRow", "loadRow", MRBDebug.DETAILED, "Parse Exception "+e.getMessage());
			return false;
		}
		catch (IOException e){
			Main.rwDebugInst.debug("ReportDataRow", "loadRow", MRBDebug.DETAILED, "IO Exception "+e.getMessage());
			return false;
		}
		return true;
	}

	public void saveRow(Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		String fileName = dir+"/"+getName()+Constants.REPORTEXTENSION;
		try {
			   FileWriter writer = new FileWriter(fileName);
			   String jsonString = new Gson().toJson(this);
			   writer.write(jsonString);
			   writer.close();	
			   Main.rwDebugInst.debug("ReportDataRow", "saveRow", MRBDebug.DETAILED, "Row Saved "+name);
          }
			 catch (IOException i) {
				 Main.rwDebugInst.debug("ReportDataRow", "saveRow", MRBDebug.DETAILED, "IO Exception "+i.getMessage());
					   i.printStackTrace();
          }
	}
	public void delete(Parameters paramsp) {
		String dir = paramsp.getDataDirectory();
		String fileName = dir+"/"+getName()+Constants.REPORTEXTENSION;
		Main.rwDebugInst.debug("ReportDataRow", "delete", MRBDebug.SUMMARY, "Delete "+fileName);
		File file = new File(fileName);
		if (file.delete())
			Main.rwDebugInst.debug("ReportDataRow", "delete", MRBDebug.SUMMARY, "Deleted "+fileName);
		else
			Main.rwDebugInst.debug("ReportDataRow", "delete", MRBDebug.SUMMARY, "Delete failed "+fileName);

	}
	public void renameRow(String newName,Parameters paramsp) {
		delete(paramsp);
		name = newName;
		saveRow(paramsp);
	}
}
