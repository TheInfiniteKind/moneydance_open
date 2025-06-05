/*
 *  Copyright (c) 2014, 2016, Michael Bray. All rights reserved.
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

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.event.ItemEvent;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

import com.infinitekind.moneydance.model.Account;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;

public class loadPricesWindow extends JPanel implements TableListener {
    private SortedSet<SecLine> setLine;
    private Account acct;
    private MyTableModel pricesModel;
    private MyTable pricesTab;
    private GenerateWindow generateWindow;
    private Parameters2 params;
    JScrollPane spPrices;
    JPanel bottomPane;
    JPanel topPane;
    JPanel middlePane;
    JButton btnClose;
    JButton btnGenerate;
    JCheckBox select;
    JTextField accountName;
	private MoneydanceUI mdGUI;
	private com.moneydance.apps.md.controller.Main mdMain;
	private JButton helpBtn;

	public loadPricesWindow(JTextField txtFileName,Account acctp, Parameters2 objParmsp) {
		mdMain = com.moneydance.apps.md.controller.Main.mainObj;
		mdGUI = mdMain.getUI();
		setLine = new TreeSet<>(new SecLineCompare());
		acct = acctp;
		params = objParmsp;
		
		loadFile (txtFileName);
		pricesModel = new MyTableModel (setLine, Main.mapAccounts);
		pricesTab = new MyTable (pricesModel);
		/*
		 * Start of screen
		 * 
		 * Top Panel Account
		 */
		this.setLayout(new BorderLayout());
		topPane = new JPanel (new GridBagLayout());
		int x=0;
		int y=0;
		JLabel accountLbl = new JLabel("Investment Account:");
		topPane.add(accountLbl,GridC.getc(x,y));
		x++;
		accountName = new JTextField(acct.getAccountName());
		topPane.add(accountName,GridC.getc(x,y));
		this.add(topPane,BorderLayout.PAGE_START);
		/*
		 * Middle Panel table
		 */
		middlePane = new JPanel ();
		middlePane.setLayout(new BoxLayout(middlePane,BoxLayout.Y_AXIS));
		spPrices = new JScrollPane (pricesTab);
		spPrices.setAlignmentX(LEFT_ALIGNMENT);
		middlePane.add(spPrices,BorderLayout.LINE_START);
		spPrices.setPreferredSize(new Dimension(Constants.LOADSCREENWIDTH,Constants.LOADSCREENHEIGHT));
		select = new JCheckBox();
		select.setAlignmentX(LEFT_ALIGNMENT);
		select.addItemListener(e -> {
            boolean bNewValue;
            bNewValue = e.getStateChange() != ItemEvent.DESELECTED;
            for (int i=0;i<pricesModel.getRowCount();i++)
                pricesModel.setValueAt(bNewValue, i, 0);
            pricesModel.fireTableDataChanged();
        });
		middlePane.add(select);
		this.add(middlePane,BorderLayout.CENTER);
		/*
		 * Add Buttons
		 */
		bottomPane = new JPanel(new GridBagLayout());
		/*
		 * Button 1
		 */
		x=0;
		y=0;
		btnClose = new JButton("Close");
		btnClose.addActionListener(e -> close());
		bottomPane.add(btnClose,GridC.getc(x,y).west().insets(15,15,15,15));

		/*
		 * Button 2
		 */
		x++;
		btnGenerate = new JButton("Generate Transactions");
		btnGenerate.addActionListener(e -> generate());
		bottomPane.add(btnGenerate,GridC.getc(x++,y).insets(15,15,15,15));
		helpBtn = new JButton("Help");
		helpBtn.setToolTipText("Display help information");
		helpBtn.addActionListener(e -> {
			String url = "https://github.com/mrbray99/moneydanceproduction/wiki/Security-Transaction-Load";
			mdGUI.showInternetURL(url);
		});
		bottomPane.add(helpBtn, GridC.getc(x, y).west().insets(10, 10, 10, 10));
		this.add(bottomPane,BorderLayout.PAGE_END);
		

	}

	 /*
	  * try to load selected file
	  */
	 private void loadFile(JTextField fileName) {
			String exchange;
			String ticker;
		 	Main.generatedTranSet = new MyTransactionSet(Main.root, acct,params,setLine);
		 	Main.generatedTranSet.addListener(this);
			try {
				FileReader frPrices = new FileReader(fileName.getText());
				BufferedReader brPrices = new BufferedReader(frPrices);
				/*
				 * Get the headers
				 */
				String inputLine = brPrices.readLine();
				String [] inputColumns = inputLine.split(",");
				int dateColumn = 0;
				int transTypeColumn = 0;
				int descColumn = 0;
				int tickerColumn = 0;
				int valueColumn = 0;
				int unitColumn =0;
				long lAmount;
				double unitAmount;
				for (int i=0;i<inputColumns.length;i++) {
					if (inputColumns[i].equals(params.getDate()))
						dateColumn = i;
					if (inputColumns[i].equals(params.getReference()))
						transTypeColumn = i;
					if (inputColumns[i].equals(params.getDesc()))
						descColumn = i;
					if (inputColumns[i].equals(params.getTicker()))
						tickerColumn = i;
					if (inputColumns[i].equals(params.getValue()))
						valueColumn = i;
					if (inputColumns[i].equals(params.getUnitsField()))
						unitColumn = i;
				}
				while ((inputLine = brPrices.readLine())!= null) {
					inputColumns = splitString(inputLine);
					/*
					 * Amount is in pence, change to GBP
					 * 
					 * First check to see if amount had commas
					 */
					if (inputColumns[valueColumn].startsWith("\"")) {
						String amountString = inputColumns[valueColumn].substring(1);
						if (inputColumns[valueColumn+1].endsWith("\"")) {
							amountString += inputColumns[valueColumn+1].substring(0,inputColumns[valueColumn+1].length()-1);
						}
						else {
							amountString += inputColumns[valueColumn+1];
							amountString += inputColumns[valueColumn+2].substring(0,inputColumns[valueColumn+2].length()-1);
						}
						inputColumns[valueColumn] = amountString;
					}
					String settleDate = inputColumns[dateColumn].strip();
					if (settleDate.contains("00:00"))
						settleDate=settleDate.substring(0,settleDate.indexOf (" "));
					JDateField jdtSettle = new JDateField (Main.cdate); 
					jdtSettle.setDate(jdtSettle.getDateFromString(settleDate));
					int iPoint = inputColumns[valueColumn].indexOf('.');
					if ( iPoint != -1) {
						String tempStr = inputColumns[valueColumn].substring(0,iPoint);
						String decimalPoint = inputColumns[valueColumn].substring(iPoint+1);
                        tempStr = switch (decimalPoint.length()) {
                            case 1 -> tempStr + decimalPoint + "0";
                            case 2 -> tempStr + decimalPoint;
                            default -> tempStr + decimalPoint.substring(0, 2);
                        };
						lAmount = Long.parseLong(tempStr);
					}
					else
						lAmount = Long.parseLong(inputColumns[valueColumn]+"00");
					if (lAmount == 0L)
						continue;
					if (params.getExch()) {
						ticker = inputColumns[tickerColumn];
						int iPeriod = ticker.indexOf('.');
						if (iPeriod > -1) {
							inputColumns[tickerColumn] = ticker.substring(0,iPeriod-1);
							exchange = ticker.substring(iPeriod+1);
						}
						else {
							iPeriod = ticker.indexOf(':');
							if (iPeriod > -1) {
								inputColumns[tickerColumn] = ticker.substring(0,iPeriod-1);
								exchange = ticker.substring(iPeriod+1);
							}
						}
							
					}
					else {
						ticker = inputColumns[tickerColumn];
						int iPeriod = ticker.indexOf('.');
						if (iPeriod > -1) {
							exchange = ticker.substring(iPeriod+1);
						}
						else {
							iPeriod = ticker.indexOf(':');
							if (iPeriod > -1) {
								exchange = ticker.substring(iPeriod+1);
							}
						}						
					}
					if(unitColumn < 0 || inputColumns[unitColumn]==null ||inputColumns[unitColumn].isEmpty())
						unitAmount = 0.0;
					else {
						try {
							unitAmount = Double.parseDouble(inputColumns[unitColumn]);
						}
						catch (NumberFormatException e){
							unitAmount=0.0;
						}
					}
					SecLine objLine = new SecLine(jdtSettle.getDateInt(),inputColumns[transTypeColumn],
							inputColumns[descColumn],inputColumns[tickerColumn]," ",lAmount,Main.mapAccounts.get(inputColumns[tickerColumn]),unitAmount);
//					objLine.setValid(true);
					if (!params.isDefined(inputColumns[transTypeColumn]))
						objLine.setValid(false);
					else
						if (params.requiresTicker(inputColumns[transTypeColumn]) &&
							objLine.getTicker().equals(Constants.NOTICKER))
							objLine.setValid(false);
					Main.generatedTranSet.findTransaction(objLine);
					setLine.add(objLine);
				}
				brPrices.close();
			}
			catch (FileNotFoundException e) {
				JFrame fTemp = new JFrame();
				JOptionPane.showMessageDialog(fTemp,"File "+fileName+" not Found");
				close();
			}
			catch (IOException e) {
				JFrame fTemp = new JFrame();
				JOptionPane.showMessageDialog(fTemp,"I//O Error whilst reading "+fileName);
				close();
				
			}
			
	 }
	 
	 public void close() {
		this.setVisible(false);
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.dispose();

	 }
	 private void generate() {
	      //Create and set up the window.
	      JFrame frame = new JFrame(" Load Security Prices - Build "+Main.buildStr);
	      frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
	      generateWindow = new GenerateWindow(setLine,acct,params);
	      frame.getContentPane().add(generateWindow);

	      //Display the window.
	      frame.pack();
	      frame.setLocationRelativeTo(null);
	      frame.setVisible(true);
	 }
	  /*
	   * Utility method to split a string containing both " and ,
	   */
	  
	  private String[] splitString(String strInput) {
		  List<String> listParts = new ArrayList<>();
		  int i=0;
		  StringBuilder strPart = new StringBuilder();
		  boolean bString = false;
		  while(i<strInput.length()) {
			switch (strInput.substring(i, i+1)) {
			case "\"" :
                bString = !bString;
				break;
			case "," :
				if (!bString) {
					listParts.add(strPart.toString());
					strPart = new StringBuilder();
				}
				break;
			default :
				strPart.append(strInput.substring(i, i + 1));
			}
			i++;
		  }
		  listParts.add(strPart.toString());
		  String[] arrString = new String[listParts.size()];
		  return listParts.toArray(arrString);
	  }
	@Override
	public void tableChanged () {
		pricesModel.fireTableDataChanged();
		middlePane.revalidate();
	}
}
