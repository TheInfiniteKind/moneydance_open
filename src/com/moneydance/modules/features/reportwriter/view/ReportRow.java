package com.moneydance.modules.features.reportwriter.view;

import java.io.File;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Main;

public class ReportRow {
	private String name;
	private String fileName;
	private String template;
	private String selection; 
	private String data;
	private String created;
	private String lastUsed;
	private Integer type;
	public ReportRow() {
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getFileName() {
		return fileName;
	}
	public void setFileName(String fileName) {
		this.fileName = fileName;
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
	public String getData() {
		return data;
	}
	public void setData(String data) {
		this.data = data;
	}
	public String getCreated() {
		return created;
	}
	public void setCreated(String created) {
		this.created = created;
	}
	public String getLastUsed() {
		return lastUsed;
	}
	public void setLastUsed(String lastUsed) {
		this.lastUsed = lastUsed;
	}
	public Integer getType() {
		return type;
	}
	public void setType (Integer type) {
		this.type = type; 
	}

	public void delete() {
		Main.rwDebugInst.debug("ReportRow", "delete", MRBDebug.SUMMARY, "Delete "+fileName);
		File file = new File(fileName);
		if (file.delete())
			Main.rwDebugInst.debug("SelectionRow", "delete", MRBDebug.SUMMARY, "Deleted "+fileName);
		else
			Main.rwDebugInst.debug("SelectionRow", "delete", MRBDebug.SUMMARY, "Delete failed "+fileName);

	}
}
