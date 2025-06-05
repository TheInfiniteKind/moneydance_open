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
package com.moneydance.modules.features.reportwriter;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Serializable;
import java.nio.file.Files;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.concurrent.TimeUnit;

import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.gson.stream.JsonReader;
import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.view.DataDataRow;
import com.moneydance.modules.features.reportwriter.view.DataRow;
import com.moneydance.modules.features.reportwriter.view.ReportDataRow;
import com.moneydance.modules.features.reportwriter.view.ReportRow;
import com.moneydance.modules.features.reportwriter.view.SelectionRow;

public class Parameters implements Serializable{
	private AccountBook curAcctBook;
	private File curFolder;
	private String fileName;
	private NewParameters newParams;
	private Boolean introScreen;
	private String dataDirectory;
	private String outputDirectory;
	private List<SelectionRow> selectionList;
	private List<DataRow> dataList;
	private List<ReportRow> reportList;
	private static Parameters thisObj;
	public Parameters() {
		curAcctBook = Main.context.getCurrentAccountBook();
		curFolder = curAcctBook.getRootFolder();
		thisObj = this;
		/*
		 * Determine if the new file exists
		 */
		fileName = curFolder.getAbsolutePath()+"\\"+Constants.DEFAULTPARAMETERFILE+Constants.PARMEXTENSION;
		try {
			JsonReader reader = new JsonReader(new FileReader(fileName));
			newParams = new Gson().fromJson(reader,NewParameters.class);
			reader.close();
			Main.rwDebugInst.debug("Parameters", "Parameters", MRBDebug.SUMMARY, "File found "+fileName);

		}
		catch (JsonParseException e) {
			Main.rwDebugInst.debug("Parameters", "Parameters", MRBDebug.DETAILED, "Parse Exception "+e.getMessage());
		}
		catch (IOException e){
			/*
			 * file does not exist, initialize fields
			 */
			newParams = new  NewParameters();
			newParams.setDataDirectory(Constants.NODIRECTORY);
			newParams.setReportDirectory(Constants.NODIRECTORY);
			newParams.setOutputDirectory(Constants.NODIRECTORY);
			newParams.setIntroScreen(true);
			/*
			 * create the file
			 */
			try {
			   FileWriter writer = new FileWriter(fileName);
			   String jsonString = new Gson().toJson(newParams);
			   writer.write(jsonString);
			   writer.close();
			   Main.rwDebugInst.debug("Parameters", "Parameters", MRBDebug.SUMMARY, "File created "+fileName);

             }
			 catch (IOException i) {
					   i.printStackTrace();
             }
		}
		dataDirectory = newParams.getDataDirectory();
		outputDirectory = newParams.getOutputDirectory();
		introScreen = newParams.getIntroScreen();
		dataList = new ArrayList<>();
		selectionList = new ArrayList<>();
		reportList = new ArrayList<>();
		setDataTemplates();
	}
	public static Parameters getInstance() {
		return thisObj;
	}
	public void setDataTemplates() {
		Main.rwDebugInst.debug("Parameters", "setDataTemplates", MRBDebug.SUMMARY, "Data Directory "+dataDirectory);
		if (dataDirectory == null || dataDirectory.equals(Constants.NODIRECTORY))
			return;
		dataList.clear();
		reportList.clear();
		selectionList.clear();
		File folder = new File(dataDirectory);
		File [] files = folder.listFiles();
		if (files != null && files.length > 0) {
			Arrays.sort(files);
            for (File file : files) {
                if (file.isFile()) {
                    String fileName = file.getName();
                    Main.rwDebugInst.debug("Parameters", "setDataTemplates", MRBDebug.SUMMARY, "Processing " + fileName);
                    if (fileName.toLowerCase().endsWith(Constants.DATAEXTENSION)) {
                        DataRow newRow = new DataRow();
                        newRow.setName(fileName.substring(0, fileName.lastIndexOf(".")));
                        newRow.setFileName(file.getAbsolutePath());
                        DataDataRow dataRow = new DataDataRow();
                        dataRow.loadRow(newRow.getName(), this);
                        BasicFileAttributes atts;
                        try {
                            atts = Files.readAttributes(file.toPath(), BasicFileAttributes.class);
                            newRow.setLastModified(Main.cdate.format(new Date(atts.lastModifiedTime().to(TimeUnit.MILLISECONDS))));
                            newRow.setCreated(Main.cdate.format(new Date(atts.creationTime().to(TimeUnit.MILLISECONDS))));
                            newRow.setLastUsed(Main.cdate.format(new Date(atts.lastAccessTime().to(TimeUnit.MILLISECONDS))));
                        } catch (IOException e) {
                            newRow.setLastModified("");
                            newRow.setCreated("");
                            newRow.setLastUsed("");
                        }
                        dataList.add(newRow);
                    }
                    if (fileName.toLowerCase().endsWith(Constants.SELEXTENSION)) {
                        SelectionRow newRow = new SelectionRow();
                        newRow.setName(fileName.substring(0, fileName.lastIndexOf(".")));
                        newRow.setFileName(file.getAbsolutePath());
                        BasicFileAttributes atts;
                        try {
                            atts = Files.readAttributes(file.toPath(), BasicFileAttributes.class);
                            newRow.setLastModified(Main.cdate.format(new Date(atts.lastModifiedTime().to(TimeUnit.MILLISECONDS))));
                            newRow.setCreated(Main.cdate.format(new Date(atts.creationTime().to(TimeUnit.MILLISECONDS))));
                            newRow.setLastUsed(Main.cdate.format(new Date(atts.lastAccessTime().to(TimeUnit.MILLISECONDS))));
                        } catch (IOException e) {
                            newRow.setLastModified("");
                            newRow.setCreated("");
                            newRow.setLastUsed("");
                        }
                        selectionList.add(newRow);
                    }
                    if (fileName.toLowerCase().endsWith(Constants.REPORTEXTENSION)) {
                        ReportRow newRow = new ReportRow();
                        newRow.setName(fileName.substring(0, fileName.lastIndexOf(".")));
                        newRow.setFileName(file.getAbsolutePath());
                        ReportDataRow dataRow = new ReportDataRow();
                        if (!dataRow.loadRow(newRow.getName(), this)) {
                            Main.rwDebugInst.debug("Parameters", "setReportTemplates", MRBDebug.SUMMARY, "Processing " + fileName);
                            OptionMessage.displayErrorMessage("Could not load data for data row " + newRow.getName());
                            continue;
                        }
                        newRow.setTemplate(dataRow.getTemplate());
                        newRow.setSelection(dataRow.getSelection());
                        newRow.setData(dataRow.getDataParms());
                        newRow.setType(switch (dataRow.getType()) {
                            case DATABASE -> 2;
                            case SPREADSHEET -> 3;
                            case CSV -> 4;
                        });
                        newRow.setLastUsed(Main.cdate.format(new Date(file.lastModified())));
                        reportList.add(newRow);
                    }
                }
            }
		}
		else
			dataDirectory = Constants.NODIRECTORY;
	}

	public String getDataDirectory() {
		return dataDirectory;
	}

	public void setDataDirectory(String dataDirectory) {
		this.dataDirectory = dataDirectory;
	}

	public List<SelectionRow> getSelectionList() {
		return selectionList;
	}

	public String getOutputDirectory() {
		return outputDirectory;
	}
	public void setOutputDirectory(String outputDirectory) {
		this.outputDirectory = outputDirectory;
	}
	public void addSelectionRow(SelectionRow row) {
		for (SelectionRow tempRow : selectionList) {
			if (tempRow.getName().equalsIgnoreCase(row.getName())) {
				tempRow.setLastModified(row.getLastModified());
				tempRow.setLastUsed(row.getLastUsed());
				tempRow.setCreated(row.getCreated());
				tempRow.setFileName(row.getFileName());
				return;
			}
		}
		selectionList.add(row);
	}

	public void updateSelectionRow(SelectionRow row) {
		for (SelectionRow tempRow : selectionList) {
			if (tempRow.getName().equalsIgnoreCase(row.getName())) {
				tempRow.setLastModified(row.getLastModified());
				tempRow.setLastUsed(row.getLastUsed());
				tempRow.setCreated(row.getCreated());
				tempRow.setFileName(row.getFileName());
				return;
			}
		}
	}
	public void removeSelectionRow(SelectionRow row) {
		selectionList.remove(row);
	}

	public List<DataRow> getDataList() {
		return dataList;
	}

	public void addDataRow(DataRow row) {
		for (DataRow tempRow : dataList) {
			if (tempRow.getName().equalsIgnoreCase(row.getName())) {
				tempRow.setLastModified(row.getLastModified());
				tempRow.setLastUsed(row.getLastUsed());
				tempRow.setCreated(row.getCreated());
				tempRow.setFileName(row.getFileName());
				return;
			}
		}
		dataList.add(row);
	}

	public void updateDataRow(DataRow row) {
		for (DataRow tempRow : dataList) {
			if (tempRow.getName().equalsIgnoreCase(row.getName())) {
				tempRow.setLastModified(row.getLastModified());
				tempRow.setLastUsed(row.getLastUsed());
				tempRow.setCreated(row.getCreated());
				tempRow.setFileName(row.getFileName());
				return;
			}
		}
	}
	public void removeDataRow(DataRow row) {
		dataList.remove(row);
	}
	
	public List<ReportRow> getReportList() {
		return reportList;
	}

	public void addReportRow(ReportRow row) {
		for (ReportRow tempRow : reportList) {
			if (tempRow.getName().equalsIgnoreCase(row.getName())) {
				tempRow.setLastUsed(row.getLastUsed());
				tempRow.setCreated(row.getCreated());
				tempRow.setFileName(row.getFileName());
				tempRow.setTemplate(row.getTemplate());
				tempRow.setSelection(row.getSelection());
				tempRow.setData(row.getData());
				tempRow.setType(row.getType());
				return;
			}
		}
		reportList.add(row);
	}

	public void updateReportRow(ReportRow row) {
		for (ReportRow tempRow : reportList) {
			if (tempRow.getName().equalsIgnoreCase(row.getName())) {
				tempRow.setLastUsed(row.getLastUsed());
				tempRow.setCreated(row.getCreated());
				tempRow.setFileName(row.getFileName());
				tempRow.setTemplate(row.getTemplate());
				tempRow.setSelection(row.getSelection());
				tempRow.setData(row.getData());
				tempRow.setType(row.getType());
				return;
			}
		}
	}
	public void removeReportRow(ReportRow row) {
		reportList.remove(row);
	}
	/*
	 * Save
	 */
	public void save() {

		/*
		 * create the file
		 */
		newParams.setDataDirectory(dataDirectory);
		newParams.setOutputDirectory(outputDirectory);
		newParams.setIntroScreen(introScreen);

		try {
			   FileWriter writer2 = new FileWriter(fileName);
			   String jsonString = new Gson().toJson(newParams);
			   Main.rwDebugInst.debug("Parameters","save",MRBDebug.SUMMARY,"Json string "+jsonString);
			   writer2.write(jsonString);
			   writer2.close();			  
          } catch (IOException i) {
					   i.printStackTrace();
	
          }
	}
	public boolean checkDataGroup(String groupName) {
		for (ReportRow row : reportList) {
			if (row.getData()!=null && row.getData().equals(groupName))
				return true;
		}
		return false;
	}
	public Boolean getIntroScreen() {
		if (introScreen == null)
			introScreen=true;
		return introScreen;
	}
	public void setIntroScreen(Boolean introScreen) {
		this.introScreen = introScreen;
	}
	

}
