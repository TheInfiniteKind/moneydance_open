/*
  * Copyright (c) 2014, Michael Bray. All rights reserved.
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
 */ 
package com.moneydance.modules.features.budgetgen;
/*
 * Table Model for Add Accounts window, sets column 0 to editable and Check Box
 */
import java.util.ArrayList;
import java.util.List;

import javax.swing.table.DefaultTableModel;

public class AddAccountsModel extends DefaultTableModel {
	private List<Boolean> listSelect = new ArrayList<>();
	private List<String> listCategory = new ArrayList<>();
	public AddAccountsModel() {
		super();
	}
	@Override
	public int getColumnCount() {
			return 2;
	}
	@Override
	public int getRowCount() {
		return (listSelect==null?0:listSelect.size());
	}
	public Class getColumnClass(int c){
		if (c == 0)
			return Boolean.class;
		return String.class;
	}
	@Override
	public String getColumnName(int c) {
		if (c == 0)
			return "Select";
		return "Category";
	}
	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {
		if (columnIndex == 0)
			return listSelect.get(rowIndex);
		return listCategory.get(rowIndex);
	}
	@Override
    public boolean isCellEditable(int row, int col) {
        return col == 0;
    }
	@Override
	public void setValueAt(Object value, int row, int col){
		if (col == 0)
			listSelect.set(row,(Boolean) value);
		else
			listCategory.set(row,(String) value);
	}
	public void setRows(String[] arrAccounts){
		listSelect.clear();
		listCategory.clear();
        for (String arrAccount : arrAccounts) {
            listSelect.add(false);
            listCategory.add(arrAccount);
        }
		fireTableDataChanged();
	}

}
