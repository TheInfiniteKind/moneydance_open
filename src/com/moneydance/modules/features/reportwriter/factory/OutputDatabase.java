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

import com.moneydance.modules.features.reportwriter.Database;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.DataBean;
import com.moneydance.modules.features.reportwriter.view.ReportDataRow;

public class OutputDatabase extends OutputFactory {
	private Database database;
	private String filename;
	private boolean databaseClosed = true;

	public OutputDatabase(ReportDataRow reportp, Parameters paramsp) throws RWException {
		super(reportp, paramsp);
	}

	@Override
	public boolean chooseFile(String filename) throws RWException {
		try {
			this.filename = filename;
			database = new Database(params, filename, report.getOverWrite());
			databaseClosed = false;
		} catch (RWException e) {
			throw new RWException(e.getLocalizedMessage());
		}
		return true;
	}

	@Override
	public void closeOutputFile() throws RWException {
		if (!databaseClosed) {
			database.commit();
		}
		databaseClosed = true;
	}

	@Override
	public void createRecord(DataBean bean) throws RWException {
		database.createTable(bean);
	}

	@Override
	public void closeRecordFile() throws RWException {
		database.commit();
	}

	@Override
	public void writeRecord(DataBean bean) throws RWException {
		String sql = bean.createSQL();
		database.executeUpdate(sql);
	}

	public Database getDatabase() throws RWException {
		try {
			if (databaseClosed && database == null) {
				database = new Database(params, filename, report.getOverWrite());
				databaseClosed = false;
			}
			return database;
		} catch (RWException e) {
			throw new RWException(e.getLocalizedMessage());
		}
	}

}
