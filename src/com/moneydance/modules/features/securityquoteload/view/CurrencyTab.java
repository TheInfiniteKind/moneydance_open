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

import java.awt.GridBagLayout;

import javax.swing.JPanel;
import javax.swing.JScrollPane;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;
import com.moneydance.modules.features.securityquoteload.MainPriceWindow;

public class CurrencyTab extends DisplayTab {
	private CurTable currencyTable;
	private JScrollPane scrollPane = new JScrollPane();
	public CurrencyTab(Parameters params,Main main, MainPriceWindow controller) {
		super(params, main, controller);
		mainPanel = new JPanel(new GridBagLayout());
		mainPanel.setLayout(new GridBagLayout());
		this.setViewportView(mainPanel);
		mainPanel.add(scrollPane,GridC.getc(0,0).colspan(3).wxy((float)1.0,(float)1.0).fillboth().insets(10,0,5,0));
	}
	public void setCurrencyTable(CurTable currencyTable) {
		this.currencyTable = currencyTable;
		scrollPane.setViewportView(this.currencyTable);
	}
	public void removeButtons(JPanel buttonsPanel) {
		mainPanel.remove(buttonsPanel);
	}
	public void setButtons(JPanel buttonsPanel) {
		mainPanel.add(buttonsPanel,GridC.getc(0,1).colspan(3).wxy((float)1.0,(float)1.0).fillboth().insets(10,0,10,0));
	}
}
