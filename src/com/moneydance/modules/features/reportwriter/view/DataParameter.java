package com.moneydance.modules.features.reportwriter.view;

import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;

public class DataParameter {
	private SortedMap<String,String> fields;
	private String value;
	private List<String> list;

	public List<String> getList() {
		if (list != null)
			return list;
		return new ArrayList<String>();
	}

	public void setList(List<String> list) {
		this.list = list;
	}

	public String getValue() {
		return value;
	}

	public void setValue(String value) {
		this.value = value;
	}

	public SortedMap<String, String> getFields() {
		return fields;
	}

	public void setFields(SortedMap<String, String> fields) {
		this.fields = fields;
	}

	

}
