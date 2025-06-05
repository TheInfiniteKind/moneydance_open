/*
 *  Copyright (c) 2014, Michael Bray. All rights reserved.
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
package com.moneydance.modules.features.loadsectrans;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;

import javax.swing.table.DefaultTableModel;


public class GenerateTableModel extends DefaultTableModel {
	private static String[] arrColumns = {"Select","P/S","Amount","Account","Description","Cheque","T Type","Date"};
	private List<GenerateTransaction> listTrans; 
	private List<Boolean> listSelect;

	public GenerateTableModel() {
		listTrans = new ArrayList<GenerateTransaction>();
		listSelect = new ArrayList<Boolean>();
	}

	@Override
	public int getRowCount() {
		if (listTrans == null)
			return 0;
		return (listTrans.size());
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	public Class getColumnClass(int c){
		return String.class;
	}

		@Override
	public int getColumnCount() {
			return 8;
	}	
	@Override
	public String getColumnName(int c) {
		return arrColumns[c];
	}
	@Override
	public Object getValueAt(int rowIndex, int columnIndex) {
		DecimalFormat dfNumbers = new DecimalFormat("#0.00");
		switch (columnIndex) {
		case 0:
			if (listTrans.get(rowIndex).getType() == Constants.PARENT)
				return listSelect.get(rowIndex);
			return  "    ";
		case 1:
			return  listTrans.get(rowIndex).getType();
		case 2:
			return dfNumbers.format(listTrans.get(rowIndex).getAmount()/100.00);
		case 3:
			return  listTrans.get(rowIndex).getAccount().getAccountName();
		case 4:
			return  listTrans.get(rowIndex).getDesc();
		case 5:
			return  listTrans.get(rowIndex).getCheque();
		case 6:
			return  listTrans.get(rowIndex).getTType();
		default:
			return  Main.cdate.format(listTrans.get(rowIndex).getDate());
			
		}
	}
	@Override
    public boolean isCellEditable(int row, int col) {
        /*
         * Only Select, amount, period, start date and RPI are editable
         * Category, Year 1, Year 2, Year 3 are not
         */
		if (col ==0)
			return true;
		else
			return false;
    }
	@Override
	public void setValueAt(Object value, int row, int col){
		/*
		 * copes with call when data is invalid
		 */
		if (value == null)
			return;
		if (col ==0)
			listSelect.set(row, (boolean) value);
	}
	
	public void addLine(GenerateTransaction objTran) {
		listTrans.add (objTran);
		listSelect.add(false);
	}
	
	public GenerateTransaction getLine(int row){
		return listTrans.get(row);
	}
	
	public void deleteLine(int row){
		listTrans.remove(row);
		return;
	}}
