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

import java.text.SimpleDateFormat;
import java.util.Date;

import javax.swing.JOptionPane;

import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.AccountBean;
import com.moneydance.modules.features.reportwriter.databeans.AddressBean;
import com.moneydance.modules.features.reportwriter.databeans.BudgetBean;
import com.moneydance.modules.features.reportwriter.databeans.BudgetItemBean;
import com.moneydance.modules.features.reportwriter.databeans.CategoryBean;
import com.moneydance.modules.features.reportwriter.databeans.CurrencyBean;
import com.moneydance.modules.features.reportwriter.databeans.CurrencyRateBean;
import com.moneydance.modules.features.reportwriter.databeans.DataBean;
import com.moneydance.modules.features.reportwriter.databeans.InvTranBean;
import com.moneydance.modules.features.reportwriter.databeans.LotsBean;
import com.moneydance.modules.features.reportwriter.databeans.ReminderBean;
import com.moneydance.modules.features.reportwriter.databeans.SecurityBean;
import com.moneydance.modules.features.reportwriter.databeans.SecurityPriceBean;
import com.moneydance.modules.features.reportwriter.databeans.TransactionBean;
import com.moneydance.modules.features.reportwriter.view.DataDataRow;
import com.moneydance.modules.features.reportwriter.view.ReportDataRow;
import com.moneydance.modules.features.reportwriter.view.SelectionDataRow;

public abstract class OutputFactory {
	protected String fileName;
	protected String name;
	protected Parameters params;
	protected DataDataRow data;
	protected SelectionDataRow selection;
	protected ReportDataRow report;

	public OutputFactory(ReportDataRow reportp, Parameters paramsp) throws RWException {
		report = reportp;
		name = report.getName();
		params = paramsp;

		selection = new SelectionDataRow();
		if (!selection.loadRow(report.getSelection(), params)) {
			JOptionPane.showMessageDialog(null, "Selection Group file " + report.getSelection() + " not found");
			return;
		}
		data = new DataDataRow();
		if (!data.loadRow(report.getDataParms(), params)) {
			JOptionPane.showMessageDialog(null, "Data Parameters file " + report.getDataParms() + " not found");
			return;
		}
		String filename;
		String now = new SimpleDateFormat("yyyy-MM-ddHHmmss").format(new Date());
		if (report.getGenerate())
			filename = "ReportWriter" + now;
		else
			filename = report.getOutputFileName();
		if (report.getAddDate())
			filename += now;
		try {
			if (chooseFile(filename)) {
				createOutput();
				selection.touchFile();
				data.touchFile();
			}
		} catch (RWException e) {
			JOptionPane.showMessageDialog(null, "Error creating " + report.getName() + " " + e.getLocalizedMessage());
			throw e;
		}
	}

	public SelectionDataRow getSelection() {
		return selection;
	}

	public boolean chooseFile(String filename) throws RWException {
		return false;
	}

	public void createOutput() throws RWException {
		try {
			if (selection.getAccounts()) {
				AccountBean acct = new AccountBean();
				acct.setSelection(selection);
				createRecord(acct);
				Main.extension.updateProgress("Account Record Created");
				new AccountFactory(data, this);
				Main.extension.updateProgress("Account Records Output");
				closeRecordFile();
			}
			if (selection.getAddress()) {
				AddressBean addr = new AddressBean();
				addr.setSelection(selection);
				createRecord(addr);
				Main.extension.updateProgress("Address Record Created");
				new AddressFactory(data, this);
				Main.extension.updateProgress("Address Records Output");
				closeRecordFile();
			}
			if (selection.getBudgets()) {
				BudgetBean bud = new BudgetBean();
				bud.setSelection(selection);
				createRecord(bud);
				Main.extension.updateProgress("Budget Record Created");
				new BudgetFactory(data, this);
				Main.extension.updateProgress("Budget Records Output");
				closeRecordFile();
			}
			if (selection.getTransactions()) {
				TransactionBean tran = new TransactionBean();
				tran.setSelection(selection);
				createRecord(tran);
				Main.extension.updateProgress("Transaction Record Created");
				new TransactionFactory(data, this);
				Main.extension.updateProgress("Transaction Records Output");
				closeRecordFile();
			}
			if (selection.getInvTrans()) {
				InvTranBean tran = new InvTranBean();
				tran.setSelection(selection);
				;
				createRecord(tran);
				Main.extension.updateProgress("Investment Transaction Record Created");
				new InvestTranFactory(data, this);
				Main.extension.updateProgress("Investment Transaction Records Output");
				closeRecordFile();
			}
			if (selection.getLots()) {
				LotsBean tran = new LotsBean();
				tran.setSelection(selection);
				;
				createRecord(tran);
				Main.extension.updateProgress("Lots Record Created");
				new LotsFactory(data, this);
				Main.extension.updateProgress("Lots Records Output");
				closeRecordFile();
			}

			if (selection.getCurrencies()) {
				CurrencyBean cur = new CurrencyBean();
				cur.setSelection(selection);
				createRecord(cur);
				Main.extension.updateProgress("Currency Record Created");
				new CurrencyFactory(data, this);
				Main.extension.updateProgress("Currency Records Output");
				closeRecordFile();
			}
			if (selection.getSecurities()) {
				SecurityBean sec = new SecurityBean();
				sec.setSelection(selection);
				createRecord(sec);
				Main.extension.updateProgress("Security Record Created");
				new SecurityFactory(data, this);
				Main.extension.updateProgress("Security Records Output");
				closeRecordFile();
			}
			if (selection.getCategories()) {
				CategoryBean cat = new CategoryBean();
				cat.setSelection(selection);
				createRecord(cat);
				Main.extension.updateProgress("Category Record Created");
				new CategoryFactory(data, this);
				Main.extension.updateProgress("Category Records Output");
				closeRecordFile();
			}
			if (selection.getSecurityPrices()) {
				SecurityPriceBean secp = new SecurityPriceBean();
				secp.setSelection(selection);
				createRecord(secp);
				Main.extension.updateProgress("Security Price Record Created");
				new SecurityPriceFactory(data, this);
				Main.extension.updateProgress("Security Price Records Output");
				closeRecordFile();
			}
			if (selection.getCurrencyRates()) {
				CurrencyRateBean curr = new CurrencyRateBean();
				curr.setSelection(selection);
				createRecord(curr);
				Main.extension.updateProgress("Currency Rate Record Created");
				new CurrencyRateFactory(data, this);
				Main.extension.updateProgress("Currency Rate Records Output");
				closeRecordFile();
			}
			if (selection.getBudgetItems()) {
				BudgetItemBean budi = new BudgetItemBean();
				budi.setSelection(selection);
				createRecord(budi);
				Main.extension.updateProgress("Budget Item Record Created");
				new BudgetItemFactory(data, this);
				Main.extension.updateProgress("Budget Item Records Output");
				closeRecordFile();
			}
			if (selection.getReminders()) {
				ReminderBean rem = new ReminderBean();
				rem.setSelection(selection);
				createRecord(rem);
				Main.extension.updateProgress("Reminder Record Created");
				new ReminderFactory(data, this);
				Main.extension.updateProgress("Reminder Records Output");
				closeRecordFile();
			}
			closeOutputFile();
			JOptionPane.showMessageDialog(null, "Report/File " + name + " created");
		} catch (RWException e) {
			throw e;
		}
	}

	public void createRecord(DataBean bean) throws RWException {

	}

	public void writeRecord(DataBean bean) throws RWException {
	}

	public void closeOutputFile() throws RWException {

	}

	public void closeRecordFile() throws RWException {

	}

}
