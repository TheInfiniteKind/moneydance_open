package com.moneydance.modules.features.securityquoteload.view;

import java.awt.GridBagLayout;

import javax.swing.JPanel;
import javax.swing.JScrollPane;

import com.moneydance.awt.GridC;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.MainPriceWindow;
import com.moneydance.modules.features.securityquoteload.Parameters;

public class SecurityTab extends DisplayTab {
		private SecTable securityTable=null;
		private JScrollPane scrollPane = new JScrollPane();

		public SecurityTab(Parameters params, Main main, MainPriceWindow controller) {
			super(params, main, controller);
			mainPanel = new JPanel(new GridBagLayout());
			mainPanel.add(scrollPane,GridC.getc(0,0).colspan(3).wxy((float)1.0,(float)1.0).fillboth().insets(10,0,10,0));
			this.setViewportView(mainPanel);
		}
		public void setSecurityTable (SecTable securityTable) {
			this.securityTable = securityTable;
			scrollPane.setViewportView(this.securityTable);
		}
		public void removeButtons(JPanel buttonsPanel) {
			mainPanel.remove(buttonsPanel);
		}
		public void setButtons(JPanel buttonsPanel) {
			mainPanel.add(buttonsPanel,GridC.getc(0,1).colspan(3).insets(10,0,10,0));
		}
}
