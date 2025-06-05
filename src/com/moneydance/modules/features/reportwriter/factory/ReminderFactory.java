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

import java.util.List;
import java.util.SortedMap;

import com.infinitekind.moneydance.model.ParentTxn;
import com.infinitekind.moneydance.model.Reminder;
import com.infinitekind.moneydance.model.ReminderSet;
import com.infinitekind.moneydance.model.SplitTxn;
import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.databeans.ReminderBean;
import com.moneydance.modules.features.reportwriter.view.DataDataRow;
import com.moneydance.modules.features.reportwriter.view.DataParameter;

public class ReminderFactory {
	private DataDataRow dataParams;
	private ReminderSet reminders;
	private List<Reminder> selectedReminders;
	private SortedMap<String, DataParameter> map;
	private int fromDate;
	private int toDate;
	private boolean filterByDate = false;

	public ReminderFactory(DataDataRow dataParams, OutputFactory output) throws RWException {
		this.dataParams = dataParams;
		map = this.dataParams.getParameters();
		reminders = Main.book.getReminders();
		if (reminders == null)
			return;
		selectedReminders = reminders.getAllReminders();
		if (selectedReminders == null)
			return;
		if (map.containsKey(Constants.PARMSELDATES)) {
			filterByDate = true;
			if (map.containsKey(Constants.PARMFROMDATE))
				fromDate = Integer.valueOf(map.get(Constants.PARMFROMDATE).getValue());
			else
				fromDate = DateUtil.getStrippedDateInt();
			if (map.containsKey(Constants.PARMTODATE) && !map.containsKey(Constants.PARMTODAY))
				toDate = Integer.valueOf(map.get(Constants.PARMTODATE).getValue());
			else
				toDate = DateUtil.getStrippedDateInt();
		}
		for (Reminder rem : selectedReminders) {
			if (filterByDate) {
				if (rem.getInitialDateInt() > toDate)
					continue;
				if (rem.getLastDateInt() > 0 && rem.getLastDateInt() < fromDate)
					continue;
			}
			if (rem.getReminderType() == Reminder.Type.NOTE) {
				ReminderBean bean = new ReminderBean();
				bean.setSelection(output.getSelection());
				bean.setReminder(rem, null, null, 0);
				bean.populateData();
				try {
					output.writeRecord(bean);
				} catch (RWException e) {
					throw e;
				}
			} else {
				ParentTxn parent = rem.getTransaction();
				for (int idx = 0; idx < parent.getOtherTxnCount(); idx++) {
					ReminderBean bean = new ReminderBean();
					bean.setSelection(output.getSelection());
					bean.setReminder(rem, parent, (SplitTxn) parent.getOtherTxn(idx), idx);
					bean.populateData();
					try {
						output.writeRecord(bean);
					} catch (RWException e) {
						throw e;
					}

				}
			}
		}
	}
}
