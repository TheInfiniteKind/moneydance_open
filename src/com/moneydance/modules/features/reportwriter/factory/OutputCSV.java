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
import java.io.OutputStreamWriter;
import java.io.PrintWriter;

import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.DataBean;
import com.moneydance.modules.features.reportwriter.view.ReportDataRow;

public class OutputCSV extends OutputFactory {
	private FileOutputStream outputfile;
	private PrintWriter writer;
	private String outputDirectory;
	private String delimiter;

	public OutputCSV(ReportDataRow report, Parameters params) throws RWException {
		super(report, params);
	}

	@Override
	public boolean chooseFile(String fileName) throws RWException {
		File directory;
		File[] files = null;
		boolean exists = false;
		this.fileName = fileName;
		outputDirectory = params.getOutputDirectory();
		directory = new File(outputDirectory);
		if (directory != null)
			files = directory.listFiles();
		for (File temp : files) {
			String[] parts = temp.getName().split("[.]");
			if (parts[0].equalsIgnoreCase(fileName) && parts[parts.length - 1].equalsIgnoreCase("csv")) {
				exists = true;
				if (report.getOverWrite())
					temp.delete();
			}
		}
		if (!report.getOverWrite() && exists)
			throw new RWException("csv files already exists");
		delimiter = report.getDelimiter();
		if (delimiter.equals("Tab"))
			delimiter = "\t";
		return true;
	}

	@Override
	public void createRecord(DataBean bean) throws RWException {
		try {
			outputfile = new FileOutputStream(
					outputDirectory + "/" + fileName + "." + bean.getShortTableName() + ".csv");
			byte[] bom = new byte[] { (byte) 0xEF, (byte) 0xBB, (byte) 0xBF };
			outputfile.write(bom);
			OutputStreamWriter osw = new OutputStreamWriter(outputfile, "UTF-8");
			writer = new PrintWriter(osw);
			if (report.getTargetExcel())
				if (delimiter != ",")
					writer.println("sep=" + delimiter);
		} catch (IOException e) {
			throw new RWException("IO Error on " + outputDirectory + "/" + fileName + ".acct.csv");
		}
		String[] fields = bean.createHeaderArray();
		String line = "";
		for (int ii = 0; ii < fields.length; ii++) {
			fields[ii] = escape(fields[ii]);
			line += fields[ii];
			if (ii < fields.length - 1)
				line += delimiter;
		}
		writer.println(line);

	}

	@Override
	public void writeRecord(DataBean bean) throws RWException {
		String[] fields = bean.createStringArray();
		String line = "";
		for (int ii = 0; ii < fields.length; ii++) {
			fields[ii] = escape(fields[ii]);
			line += fields[ii];
			if (ii < fields.length - 1)
				line += delimiter;
		}
		writer.println(line);
	}

	@Override
	public void closeRecordFile() throws RWException {
		if (writer != null) {
			writer.close();
		}
		writer = null;
	}

	private String escape(String str) {
		if (str == null)
			return null;
		if (str.contains(delimiter) || str.contains(System.lineSeparator())|| str.contains("\t"))
			return "\""+str.replace(delimiter, " ")+"\"";
		return str;
	}

}
