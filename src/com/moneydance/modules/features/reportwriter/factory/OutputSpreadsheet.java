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
package com.moneydance.modules.features.reportwriter.factory;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.sql.Date;

import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.CreationHelper;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.view.ReportDataRow;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.DataBean;

public class OutputSpreadsheet extends OutputFactory {
	private String outputDirectory;
	private File workBookFile;
	private OutputStream fileOut;
	private Workbook workBook;
	private Sheet workSheet;
	private int rowIndex = 2;
	private BEANFIELDTYPE[] columnTypes;
	private CellStyle integerStyle;
	private CellStyle numberStyle;
	private CellStyle dateStyle;

	public OutputSpreadsheet(ReportDataRow reportp, Parameters paramsp) throws RWException {
		super(reportp, paramsp);
	}

	@Override
	public boolean chooseFile(String fileNamep) throws RWException {
		fileName = fileNamep;
		outputDirectory = params.getOutputDirectory();
		workBookFile = new File(outputDirectory + "/" + fileName + ".xlsx");

		if (workBookFile.exists()) {
			if (report.getOverWrite())
				workBookFile.delete();
			else
				throw new RWException(" csv files already exists");
		}
		workBook = new XSSFWorkbook();
		try {
			fileOut = new FileOutputStream(outputDirectory + "/" + fileName + ".xlsx");
		} catch (IOException e) {
			throw new RWException("Error creating workbook " + fileName + ".xlsx");
		}
		integerStyle = workBook.createCellStyle();
		integerStyle.setDataFormat((short) 1);
		numberStyle = workBook.createCellStyle();
		numberStyle.setDataFormat(workBook.createDataFormat().getFormat("#.#######"));
		dateStyle = workBook.createCellStyle();
		CreationHelper createHelper = workBook.getCreationHelper();
		dateStyle.setDataFormat(createHelper.createDataFormat().getFormat(Main.datePattern));
		return true;
	}

	@Override
	public void closeOutputFile() throws RWException {
		if (workBook != null) {
			try {
				try {
					workBook.write(fileOut);
				} catch (IOException e) {
					throw new RWException("Error writing workbook " + fileName + ".xlsx");
				}
				fileOut.flush();
				fileOut.close();
				workBook.close();
			} catch (IOException e) {
				throw new RWException("Error closing workbook " + fileName + ".xlsx");
			}
		}
		workBook = null;
	}

	@Override
	public void createRecord(DataBean bean) throws RWException {
		workSheet = workBook.createSheet(bean.getTableName());
		Row headerRow = workSheet.createRow(1);
		rowIndex = 2;
		String[] headFields = bean.createHeaderArray();
		columnTypes = bean.getColumnTypes();
		int index = 0;
		for (String field : headFields) {
			if (field.isEmpty())
				index++;
			else {
				Cell cell = headerRow.createCell(index++);
				cell.setCellValue(field);
			}
		}
	}

	@Override
	public void writeRecord(DataBean bean) throws RWException {
		String[] fields = bean.createStringArray();
		Row dataRow = workSheet.createRow(rowIndex++);
		int index = 0;
		for (int i = 0; i < fields.length; i++) {
			String field = fields[i];
			if (field == null || field.isEmpty())
				index++;
			else {
				Cell cell = dataRow.createCell(index++);
				setField(cell, dataRow, field, columnTypes[i]);
			}
		}
	}

	@Override
	public void closeRecordFile() throws RWException {

	}

	private void setField(Cell cell, Row dataRow, String field, BEANFIELDTYPE type) {
		try {
			switch (type) {
			case BOOLEAN:
				boolean tempBool = Boolean.valueOf(field);
				cell.setCellValue(tempBool);
				break;
			case DATEINT:
				Date tempDate = Date.valueOf(field);
				cell.setCellValue(tempDate);
				cell.setCellStyle(dateStyle);
				break;
			case INTEGER:
				int tempInt = Integer.valueOf(field);
				cell.setCellValue(tempInt);
				cell.setCellStyle(integerStyle);
				break;
			case MONEY:
			case DOUBLE:
			case PERCENT:
				double tempDouble = Double.valueOf(field);
				cell.setCellValue(tempDouble);
				cell.setCellStyle(numberStyle);
				break;
			default:
				cell.setCellValue(field);
				break;
			}
		} catch (NumberFormatException e) {
			Main.rwDebugInst.debug("OutputSpreadsheet", "setField", MRBDebug.DETAILED,
					"Number error for " + type.toString() + " - " + field);
			cell.setCellValue(field);
		}

	}
}
