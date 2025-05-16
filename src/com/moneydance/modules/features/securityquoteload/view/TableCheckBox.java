/*
 * Copyright (c) 2023, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.securityquoteload.view;

import java.awt.Component;

import javax.swing.JTable;
import javax.swing.table.TableCellRenderer;

public class TableCheckBox implements TableCellRenderer {
	TableCellRenderer booleanRenderer;
	TableCellRenderer defaultRenderer;
	JTable table;
	enum whichTable {SEC,CUR};
	whichTable tabType=null;;
	SecTableModel secModel;
	CurTableModel curModel;
	public TableCheckBox (JTable table, TableCellRenderer booleanRenderer, TableCellRenderer defaultRenderer) {
		this.booleanRenderer = booleanRenderer;
		this.defaultRenderer = defaultRenderer;
		this.table = table;
		if (table instanceof SecTable) {
			secModel = (SecTableModel)table.getModel();
			tabType = whichTable.SEC;
		}
		if (table instanceof CurTable) {
			curModel = (CurTableModel)table.getModel();
			tabType = whichTable.CUR;
		}
		
	}
	@Override
	public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus,
			int row, int column) {
		int modRow=table.convertRowIndexToModel(row);
		switch (tabType) {
		case CUR:
			Object temp = curModel.getValueAt(modRow, 6);
			if (temp==null || (temp instanceof String && temp.equals("0.0"))||value instanceof String)
				return defaultRenderer.getTableCellRendererComponent(table, value, isSelected, hasFocus, modRow, column);
			return booleanRenderer.getTableCellRendererComponent(table, value, isSelected, hasFocus, modRow, column);
		case SEC:
			Object temp2 = secModel.getValueAt(modRow, 8);
			if (temp2==null || (temp2 instanceof String && temp2.equals("0.0"))||value instanceof String)
				return defaultRenderer.getTableCellRendererComponent(table, value, isSelected, hasFocus, modRow, column);
			return booleanRenderer.getTableCellRendererComponent(table, value, isSelected, hasFocus, modRow, column);
		default:
			break;
		
		}
		return null;
	}

}
