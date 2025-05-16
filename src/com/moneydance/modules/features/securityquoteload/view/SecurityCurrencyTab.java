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
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;
import com.moneydance.modules.features.securityquoteload.MainPriceWindow;

public class SecurityCurrencyTab extends DisplayTab {
	private SecTable securityTable=null;
	private CurTable currencyTable=null;
	private JScrollPane scrollPane = new JScrollPane(); ;
	private JScrollPane scrollPane2= new JScrollPane();;
	private JLabel securities=new JLabel("Securities");
	private JLabel currencies=new JLabel("Exchange Rates");
	private JSplitPane splits;
	private JPanel topPane = new JPanel(new GridBagLayout());
	private JPanel botPane = new JPanel(new GridBagLayout());
	private Double splitPercent=0.0;

	public SecurityCurrencyTab(Parameters params, Main main, MainPriceWindow controller) {
		super(params, main, controller);
		splits=new JSplitPane(JSplitPane.VERTICAL_SPLIT,topPane,botPane);
		this.setViewportView(splits);
		topPane.add(securities,GridC.getc(0,0).west().insets(2,0,2,0));
		topPane.add(scrollPane,GridC.getc(0,1).colspan(3).wxy((float)1.0, (float)1.0).fillboth().insets(0,0,2,0));
		botPane.add(currencies,GridC.getc(0,0).insets(2,0,2,0));
		botPane.add(scrollPane2,GridC.getc(0,1).colspan(3).wxy((float)1.0, (float)1.0).fillboth().insets(0,0,2,0));
		splitPercent = Main.preferences.getDouble(Constants.PROGRAMNAME+"."+Constants.SPLITPERCENT, 0.5);
		splits.addPropertyChangeListener(JSplitPane.DIVIDER_LOCATION_PROPERTY, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent pce) {
				JSplitPane tempSplit = (JSplitPane)pce.getSource();
			    int location=Integer.valueOf(pce.getNewValue().toString());
			    Double percentT = Double.valueOf(location)/Double.valueOf(tempSplit.getHeight());
			    Main.preferences.put(Constants.PROGRAMNAME+"."+Constants.SPLITPERCENT, percentT);
			    Main.preferences.isDirty();
			}
		});
		if (splitPercent < 0.0 || splitPercent > 1.0)
			splitPercent = 0.5;
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
			@Override
			public void run() {
				splits.setDividerLocation(splitPercent);
			}
		});
	}
	public void setTables (SecTable securityTable, CurTable currencyTable) {
		this.securityTable = securityTable;
		this.currencyTable = currencyTable;
		scrollPane.setViewportView(this.securityTable);
		scrollPane2.setViewportView(this.currencyTable);
	}
}
