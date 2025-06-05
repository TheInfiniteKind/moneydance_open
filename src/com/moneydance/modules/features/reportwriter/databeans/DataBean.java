/*
 * Copyright (c) 2021, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.reportwriter.databeans;

import java.lang.reflect.Field;
import java.sql.Date;
import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;
import com.moneydance.modules.features.reportwriter.view.DataParameter;
import com.moneydance.modules.features.reportwriter.view.SelectionDataRow;

public abstract class DataBean {
	protected String tableName;
	protected String shortName;
	protected String parmsName;
	protected SelectionDataRow selection;
	protected SortedMap<String, DataParameter> selParams;
	protected DataParameter dataParams;
	protected List<String> selFields;
	protected String screenTitle;
	private List<BEANFIELDTYPE> columnTypes;

	public void setSelection(SelectionDataRow selection) {
		this.selection = selection;
		if (selection != null)
			selParams = selection.getParameters();
		else
			selParams = new TreeMap<String, DataParameter>();
		dataParams = selParams.get(parmsName);
		if (dataParams == null)
			dataParams = new DataParameter();
		selFields = dataParams.getList();
		if (selFields.isEmpty())
			selFields = null;
	}

	public void populateData() {
	}

	public String createTable() {
		StringBuilder bld = new StringBuilder("Create table " + tableName + " (");
		Field[] fields = this.getClass().getDeclaredFields();
		boolean firstentry = true;
		for (Field field : fields) {
			if (!field.isAnnotationPresent(ColumnName.class)) // not database field
				continue;
			ColumnName name = field.getAnnotation(ColumnName.class);
			if (firstentry)
				firstentry = false;
			else
				bld.append(",");
			bld.append(name.value());
			FieldType type = field.getAnnotation(FieldType.class);
			switch (type.value()) {
			case STRING:
				bld.append(" Varchar(1024)");
				break;
			case BOOLEAN:
				bld.append(" Boolean");
				break;
			case DATEINT:
				bld.append(" Date");
				break;
			case INTEGER:
				bld.append(" SmallInt");
				break;
			case LONG:
				bld.append(" BigInt");
				break;
			case MONEY:
				bld.append(" Decimal(19,4)");
				break;
			case DOUBLE:
			case PERCENT:
				bld.append(" Double");
				break;
			default:
				break;

			}
		}
		bld.append(")");
		return bld.toString();
	}

	public String[] createHeaderArray() {

		List<String> columns = new ArrayList<String>();
		columnTypes = new ArrayList<BEANFIELDTYPE>();
		Field[] fields = this.getClass().getDeclaredFields();
		for (Field field : fields) {
			if (!field.isAnnotationPresent(ColumnName.class)) // not database field
				continue;
			ColumnName name = field.getAnnotation(ColumnName.class);
			if (selFields != null && !selFields.contains(name.value())) // fields selected and not present
				continue;
			columns.add(name.value());
			FieldType type = field.getAnnotation(FieldType.class);
			columnTypes.add((BEANFIELDTYPE) type.value());
		}
		String[] array = new String[columns.size()];
		return columns.toArray(array);
	}

	public String[] createStringArray() {
		List<String> columns = new ArrayList<String>();
		Field[] fields = this.getClass().getDeclaredFields();
		for (Field field : fields) {
			if (!field.isAnnotationPresent(ColumnName.class)) // not database field
				continue;
			ColumnName name = field.getAnnotation(ColumnName.class);
			if (selFields != null && !selFields.contains(name.value())) // fields selected and not present
				continue;
			FieldType type = field.getAnnotation(FieldType.class);
			switch (type.value()) {
			case STRING:
				try {
					if (field.get(this) == null || ((String) field.get(this)).equals(Constants.MISSINGSTRING))
						columns.add("");
					else
						columns.add((String) field.get(this));
				} catch (IllegalAccessException e) {
					columns.add("");
				}
				break;
			case BOOLEAN:
				try {
					columns.add(String.valueOf(field.getBoolean(this)));
				} catch (IllegalAccessException e) {
					columns.add("False");
				}
				break;
			case DATEINT:
				try {
					if (field.get(this) == null || ((Date) field.get(this)) == Constants.MISSINGDATE)
						columns.add("");
					else
						columns.add(((Date) field.get(this)).toString());
				} catch (IllegalAccessException e) {
					columns.add("");
				}
				break;
			case INTEGER:
				try {
					if (field.get(this) == null || field.getInt(this) == Constants.MISSINGINT)
						columns.add("");
					else
						columns.add(String.valueOf(field.getInt(this)));
				} catch (IllegalAccessException e) {
					columns.add("");
				}
				break;
			case LONG:
				try {
					if (field.get(this) == null || field.getLong(this) == Constants.MISSINGLONG)
						columns.add("");
					else
						columns.add(String.valueOf(field.getLong(this)));
				} catch (IllegalAccessException e) {
					columns.add("0L");
				}
				break;
			case MONEY:
				try {
					if (field.get(this) == null || field.getLong(this) == Constants.MISSINGLONG)
						columns.add("0.0");
					else {
						Double amt = ((Long) field.getLong(this)).doubleValue() / 100.0;
						columns.add(amt.toString());
					}
				} catch (IllegalAccessException e) {
					columns.add("0.0");
				}
				break;
			case DOUBLE:
			case PERCENT:
				try {
					if (field.get(this) == null || field.getDouble(this) == Constants.MISSINGDOUBLE)
						columns.add("0.0");
					else
						columns.add(String.valueOf(field.getDouble(this)));
				} catch (IllegalAccessException e) {
					columns.add("0.0");
				}
				break;
			default:
				break;

			}
		}
		String[] array = new String[columns.size()];
		return columns.toArray(array);
	}

	public BEANFIELDTYPE[] getColumnTypes() {
		BEANFIELDTYPE[] types = new BEANFIELDTYPE[columnTypes.size()];
		return columnTypes.toArray(types);
	}

	public String createSQL() {
		StringBuilder bld = new StringBuilder("Insert into " + tableName + " (");
		Field[] fields = this.getClass().getDeclaredFields();
		boolean firstentry = true;
		for (Field field : fields) {
			if (!field.isAnnotationPresent(ColumnName.class)) // not database field
				continue;
			ColumnName name = field.getAnnotation(ColumnName.class);
			if (selFields != null && !selFields.contains(name.value())) // fields selected and not present
				continue;
			if (firstentry)
				firstentry = false;
			else
				bld.append(",");
			bld.append(name.value());
		}
		firstentry = true;
		bld.append(") values(");
		for (Field field : fields) {
			if (!field.isAnnotationPresent(ColumnName.class)) // not database field
				continue;
			ColumnName name = field.getAnnotation(ColumnName.class);
			if (selFields != null && !selFields.contains(name.value())) // fields selected and not present
				continue;
			if (firstentry)
				firstentry = false;
			else
				bld.append(",");
			FieldType type = field.getAnnotation(FieldType.class);
			switch (type.value()) {
			case STRING:
				bld.append("'");
				try {
					String tempStr = (String) field.get(this);
					if (tempStr != null && !tempStr.equals(Constants.MISSINGSTRING))
						tempStr = tempStr.replace("'", "''");
					else
						tempStr = "";
					bld.append(tempStr);
				} catch (IllegalAccessException e) {
					bld.append("Error");
				}
				bld.append("'");
				break;
			case BOOLEAN:
				try {
					bld.append(field.getBoolean(this));
				} catch (IllegalAccessException e) {
					bld.append("False");
				}
				break;
			case DATEINT:
				try {
					if ((Date) field.get(this) != Constants.MISSINGDATE) {
						bld.append("Date '");
						bld.append(((Date) field.get(this)).toString());
						bld.append("'");
					} else
						bld.append("NULL");
				} catch (IllegalAccessException e) {
					bld.append("0000-01-01");
					bld.append("'");
				}
				break;
			case INTEGER:
				try {
					if (field.getInt(this) != Constants.MISSINGINT)
						bld.append(field.getInt(this));
					else
						bld.append(0);
				} catch (IllegalAccessException e) {
					bld.append(0);
				}
				break;
			case LONG:
				try {
					if (field.getLong(this) != Constants.MISSINGLONG)
						bld.append(field.getLong(this));
					else
						bld.append(0L);
				} catch (IllegalAccessException e) {
					bld.append(0L);
				}
				break;
			case MONEY:
				try {
					if (field.getLong(this) != Constants.MISSINGLONG) {
						Double amt = ((Long) field.getLong(this)).doubleValue() / 100.0;
						bld.append(amt.toString());
					} else
						bld.append("0.0");
				} catch (IllegalAccessException e) {
					bld.append("0.0");
				}
				break;
			case DOUBLE:
			case PERCENT:
				try {
					if (field.getDouble(this) != Constants.MISSINGDOUBLE)
						bld.append(field.getDouble(this));
					else
						bld.append(0.0);
				} catch (IllegalAccessException e) {
					bld.append(0.0);
				}
				break;
			default:
				break;

			}

		}
		bld.append(")");
		return bld.toString();
	}

	public String setString(String value) {
		if (value == null)
			return Constants.MISSINGSTRING;
		else
			return value;
	}

	public Long setMoney(Long value) {
		if (value == null)
			return Constants.MISSINGLONG;
		else
			return value;
	}

	public Double setDouble(Double value) {
		if (value == null)
			return Constants.MISSINGDOUBLE;
		else
			return value;
	}

	public Boolean setBoolean(Boolean value) {
		if (value == null)
			return false;
		else
			return value;
	}

	public Integer setInt(Integer value) {
		if (value == null)
			return Constants.MISSINGINT;
		else
			return value;
	}

	public Long setLong(Long value) {
		if (value == null)
			return Constants.MISSINGLONG;
		else
			return value;
	}

	public Date setDate(Date value) {
		if (value == null)
			return Constants.MISSINGDATE;
		else
			return value;
	}

	public String getTableName() {
		return tableName;
	}

	public String getShortTableName() {
		return shortName;
	}

	public String getScreenTitle() {
		return screenTitle;
	}

}
