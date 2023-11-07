package com.moneydance.modules.features.moneyPie;

import java.awt.Color;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.Insets;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.NumberFormat;
import java.util.Calendar;
import java.util.Collections;
import java.util.Comparator;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import javax.swing.*;

import com.moneydance.apps.md.view.gui.MoneydanceLAF;

@SuppressWarnings("serial")
public class BudgetHomePageView extends JPanel {
    private Main       extension;
    private BudgetData data;
    
    private JPanel contentPanel;
    private JButton refreshButton;
    private JButton pieButton;
    private JButton castButton;
    private JButton reportButton;
    
    private Font plainFont;
	private Font boldFont;
    
	public BudgetHomePageView(Main ext){
		this.extension   = ext;
		this.refreshRefs();
		
		plainFont = getFont().deriveFont(Font.PLAIN);
    	boldFont = plainFont.deriveFont(Font.BOLD);
		
		setLayout(new GridBagLayout());
    this.setBackground(null);
    this.setOpaque(false);

		Image refreshImage = getImage("/com/moneydance/modules/features/moneyPie/images/refresh.gif");
		if(refreshImage == null){
			return;			
		}
		ImageIcon refreshIcon = new ImageIcon(refreshImage);
		refreshButton  = new JButton(refreshIcon);
		refreshButton.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        refresh();
      }
    });
		
		Image pieImage = getImage("/com/moneydance/modules/features/moneyPie/images/pie.gif");
        ImageIcon pieIcon = new ImageIcon(pieImage);
        pieButton  = new JButton(pieIcon);
        pieButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
            	openPie();
            }
        });
        
        Image reportImage = getImage("/com/moneydance/modules/features/moneyPie/images/report.gif");
        ImageIcon reportIcon = new ImageIcon(reportImage);
        reportButton  = new JButton(reportIcon);
        reportButton.addActionListener(new ActionListener() {
          public void actionPerformed(ActionEvent e) {
            openReport();
          }
        });
        
        Image castImage = getImage("/com/moneydance/modules/features/moneyPie/images/chart.gif");
        ImageIcon castIcon = new ImageIcon(castImage); 
        castButton  = new JButton(castIcon);
        castButton.addActionListener(new ActionListener() {
          public void actionPerformed(ActionEvent e) {
            openForecast();
          }
        });
        
        
		JPanel controlPanel = new JPanel(new GridBagLayout());
    controlPanel.setBackground(null);
    controlPanel.setOpaque(false);


    GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 1;
        gbc.gridy = 1;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(0, 0, 0, 0);
        gbc.weightx = 1.0;
        controlPanel.add(new JLabel(this.extension.getName() + " build " + this.extension.getBuild()), gbc);
        
        gbc.gridx = 2;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.fill = GridBagConstraints.NONE;
        gbc.weightx = 0;
        gbc.insets = new Insets(0, 0, 0, 0);
        controlPanel.add(refreshButton, gbc);
        
        gbc.gridx = 3;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.fill = GridBagConstraints.NONE;
        gbc.weightx = 0;
        gbc.insets = new Insets(0, 0, 0, 0);
        controlPanel.add(pieButton, gbc);
        
        gbc.gridx = 4;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.fill = GridBagConstraints.NONE;
        gbc.weightx = 0;
        gbc.insets = new Insets(0, 0, 0, 0);
        controlPanel.add(castButton, gbc);
        
        gbc.gridx = 5;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.fill = GridBagConstraints.NONE;
        gbc.weightx = 0;
        gbc.insets = new Insets(0, 0, 0, 0);
        controlPanel.add(reportButton, gbc);
        

        
        contentPanel = new JPanel(new GridBagLayout());
        contentPanel.setBackground(null);
        contentPanel.setOpaque(false);
        generatePanel();
        
        //Add the panel to the view
        gbc.gridx = 1;
        gbc.gridy = 1;
        gbc.fill = GridBagConstraints.NONE;
        gbc.weightx = 1;
        gbc.weighty = 1;
        gbc.fill = GridBagConstraints.BOTH;
        gbc.insets = new Insets(0, 0, 0, 0);
        add(controlPanel, gbc);
        
        gbc.gridy = 2;
        add(contentPanel, gbc);

    setBorder(BorderFactory.createCompoundBorder(MoneydanceLAF.homePageBorder,
                                                 BorderFactory.createEmptyBorder(0,12,0,12)));
  }
	
	private void refresh(){
		contentPanel.removeAll();
    	refreshRefs();
    	generatePanel();
	}
	
	private void refreshRefs(){
		this.extension.setup();
		this.data        = this.extension.getBudgetData();
	}
	
	private void generatePanel(){
        if(this.data != null){

			String budgetName = data.getCurrentBudgetName() == null ? "<NO BUDGET>" : data.getCurrentBudgetName();
        	int rowNumber = 1;
        	this.addToTable(rowNumber, budgetName + " - Year to Date", "", "", "",boldFont);
    		rowNumber++;
    		this.addBlankRow(rowNumber);
    		rowNumber++;
    		
        	this.addToTable(rowNumber, "Income", "Budgeted", "Actual", "Remaining", boldFont);
    		rowNumber++;
    		
    		Object[] rValues = new Object[4];
    		rValues = generateTable(rowNumber, "", data.getIncomeAccounts(), true);
    		rowNumber = ((Integer)rValues[0]).intValue();
    		
    		BudgetValue netBudgetd  = (BudgetValue) rValues[1];
    		BudgetValue netActual    = (BudgetValue) rValues[2];
    		BudgetValue netRemaining = (BudgetValue) rValues[3];
    		
        	this.addBlankRow(rowNumber);
    		rowNumber++;
    		
        	this.addToTable(rowNumber, "Expenses", "Budgeted", "Actual", "Remaining", boldFont);
    		rowNumber++;
    		rValues = generateTable(rowNumber, "", data.getExpenseAccounts(), true);
    		rowNumber = ((Integer)rValues[0]).intValue();
   
    		netBudgetd.minus((BudgetValue) rValues[1]);
    		netActual.minus((BudgetValue) rValues[2]);
    		netRemaining.minus((BudgetValue) rValues[3]);
    		
        	this.addBlankRow(rowNumber);
    		rowNumber++;

    		
    		this.addToTable(rowNumber, "Net", netBudgetd.toString(), 
    				netActual.toString(), 
    				"", boldFont);
    		
    		/*
        	this.addToTable(rowNumber, "Account Transfers", "Budgeted", "Actual", "Remaining", boldFont);
    		rowNumber++;
        	rowNumber = generateTable(rowNumber, "", data.getMoneyAccounts(), true);
        	this.addBlankRow(rowNumber);
    		rowNumber++;
    		*/
        }
	}
	
	private void openPie(){
		this.extension.showPie();
	}
	
	private void openReport(){
		this.extension.showReport();
	}
	
	private void openForecast(){
		this.extension.showForecast();
	}
	
	private void addBlankRow(int rowNumber){
		GridBagConstraints gbc = new GridBagConstraints();
		gbc.gridx = 1;
        gbc.gridy = rowNumber;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(0, 0, 0, 0);
        gbc.weightx = 1.0;
        gbc.gridwidth = 4;
        contentPanel.add(Box.createVerticalStrut(20), gbc);
	}
	
	private void addToTable(int rowNumber,
			                String accountName,
			                String cellValueB,
			                String cellValueA,
			                String cellValueD, Font customFont){
		
		NumberFormat nf = NumberFormat.getNumberInstance();
		nf.setGroupingUsed(true);
		nf.setMinimumFractionDigits(2);
		nf.setMaximumFractionDigits(2);

		Color thisColor;
		if(cellValueD.indexOf("-") > -1){
			thisColor = new Color(250, 60, 60);
		} else {
			thisColor = new Color(0, 0, 0);
		}
		
		JLabel l1 = new JLabel(accountName);
		JLabel l2 = new JLabel(cellValueB);
		JLabel l3 = new JLabel(cellValueA);
		JLabel l4 = new JLabel(cellValueD);
		
		l1.setForeground(thisColor);
		l2.setForeground(thisColor);
		l3.setForeground(thisColor);
		l4.setForeground(thisColor);
		
		if(customFont != null){
			l1.setFont(customFont);
			l2.setFont(customFont);
			l3.setFont(customFont);
			l4.setFont(customFont);
		}
		
		GridBagConstraints gbc = new GridBagConstraints();
		gbc.gridx = 1;
        gbc.gridy = rowNumber;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(0, 0, 0, 0);
        gbc.weightx = 1.0;
        contentPanel.add(l1, gbc);

        gbc.gridx = 2;
        gbc.anchor = GridBagConstraints.EAST;
        gbc.fill = GridBagConstraints.NONE;
        gbc.insets = new Insets(0, 5, 0, 0);
        gbc.weightx = 0;
        contentPanel.add(l2, gbc);
        
        gbc.gridx = 3;
        contentPanel.add(l3, gbc);
        
        gbc.gridx = 4;
        contentPanel.add(l4, gbc);

	}
	
	@SuppressWarnings("rawtypes")
	private Object[] generateTable(int rowNumber, String label, Map accounts, boolean showSubTotals){
		Calendar cal = Calendar.getInstance();
		int currentMonth = cal.get(Calendar.MONTH) + 1;

		String topAccountName = "";
		String lastTop        = "";
		BudgetValue sectionTotalValue  = new BudgetValue(data, 0);
		BudgetValue sectionTotalBudget = new BudgetValue(data, 0);
		BudgetValue sectionTotalDiff   = new BudgetValue(data, 0);
		BudgetValue sectionYTDValue   = new BudgetValue(data, 0);
		BudgetValue sectionYTDBudget  = new BudgetValue(data, 0);
		BudgetValue sectionYTDDiff    = new BudgetValue(data, 0);
		BudgetValue sectionYearValue   = new BudgetValue(data, 0);
		BudgetValue sectionYearBudget  = new BudgetValue(data, 0);
		BudgetValue sectionYearDiff    = new BudgetValue(data, 0);
		
		BudgetValue totalValue         = new BudgetValue(data, 0);
		BudgetValue totalBudget        = new BudgetValue(data, 0);
		BudgetValue totalDiff          = new BudgetValue(data, 0);
		BudgetValue totalYTDValue     = new BudgetValue(data, 0);
		BudgetValue totalYTDBudget    = new BudgetValue(data, 0);
		BudgetValue totalYTDDiff      = new BudgetValue(data, 0);
		BudgetValue totalYearValue     = new BudgetValue(data, 0);
		BudgetValue totalYearBudget    = new BudgetValue(data, 0);
		BudgetValue totalYearDiff      = new BudgetValue(data, 0);
		
		
		Iterator<?> k = sortByValue(accounts).keySet().iterator();
		while (k.hasNext()) {
		String acctNum = (String) k.next();
		String acctName = (String) accounts.get(acctNum);
		
		if(acctName.indexOf(":") > -1){
			topAccountName = acctName.substring(0, acctName.indexOf(":"));
		} else {
			topAccountName = acctName;
		}
		
		if(! showSubTotals) topAccountName = label;
		
		if(! topAccountName.equalsIgnoreCase(lastTop)){
			if(! lastTop.equals("")){
	
			this.addToTable(rowNumber, lastTop, sectionYTDBudget.toString(), 
													   sectionYTDValue.toString(), 
													   sectionYTDDiff.toString(), null);
			rowNumber++;
			
			totalValue.add(sectionTotalValue);
			totalBudget.add(sectionTotalBudget);
			totalDiff.add(sectionTotalDiff);
			
			totalYTDValue.add(sectionYTDValue);
			totalYTDBudget.add(sectionYTDBudget);
			totalYTDDiff.add(sectionYTDDiff);
			
			totalYearValue.add(sectionYearValue);
			totalYearBudget.add(sectionYearBudget);
			totalYearDiff.add(sectionYearDiff);
			
			sectionTotalValue.setValue(0);
			sectionTotalBudget.setValue(0);
			sectionTotalDiff.setValue(0);
			
			sectionYTDValue.setValue(0);
			sectionYTDBudget.setValue(0);
			sectionYTDDiff.setValue(0);
			
			sectionYearValue.setValue(0);
			sectionYearBudget.setValue(0);
			sectionYearDiff.setValue(0);
			
			}
		}

		
		//Month
		BudgetValue actualValue = new BudgetValue(data, 0);
		if(! data.isSpendingNull(acctName, currentMonth)){
			actualValue = data.getSpendingValue(acctName, currentMonth);
		}
		
		BudgetValue budgetValue = new BudgetValue(data, 0);
		if(! data.isBudgetNull(acctName, currentMonth)){
			budgetValue = data.getBudgetValue(acctName, currentMonth);
		}
		
		//Year
		BudgetValue actualYear = new BudgetValue(data, 0);
		if(! data.isBudgetNull(acctName, 0)){
		actualYear = data.getSpendingValue(acctName, 0);
		}
		
		BudgetValue budgetYear = new BudgetValue(data, 0);
		if(! data.isBudgetNull(acctName, 0)){
		budgetYear = data.getBudgetValue(acctName, 0);
		}
		
		//YTD		
		BudgetValue ytdActual = data.getSTDValue(acctName, currentMonth);
		BudgetValue ytdBudget = data.getBTDValue(acctName, currentMonth);
		
		BudgetValue diffValue = new BudgetValue(data, budgetValue);
		diffValue.minus(actualValue);
		
		BudgetValue ytdDiff   = new BudgetValue(data, ytdBudget);
		ytdDiff.minus(ytdActual);
		
		BudgetValue diffYear = new BudgetValue(data, budgetYear);
		diffYear.minus(actualYear);
		
		acctName = acctName.substring(acctName.indexOf(":")+1);
		
		sectionTotalValue.add(actualValue);
		sectionTotalBudget.add(budgetValue);
		sectionTotalDiff.add(diffValue);
		
		sectionYTDValue.add(ytdActual);
		sectionYTDBudget.add(ytdBudget);
		sectionYTDDiff.add(ytdDiff);
		
		sectionYearValue.add(actualYear);
		sectionYearBudget.add(budgetYear);
		sectionYearDiff.add(diffYear);
		
		if(showSubTotals) lastTop = topAccountName;
		if(! showSubTotals) lastTop = label;
		
		}
		
		
		this.addToTable(rowNumber, lastTop, sectionYTDBudget.toString(), 
				                            sectionYTDValue.toString(), 
				                            sectionYTDDiff.toString(), null);
		rowNumber++;
		
		totalValue.add(sectionTotalValue);
		totalBudget.add(sectionTotalBudget);
		totalDiff.add(sectionTotalDiff);
		
		totalYTDValue.add(sectionYTDValue);
		totalYTDBudget.add(sectionYTDBudget);
		totalYTDDiff.add(sectionYTDDiff);
		
		totalYearValue.add(sectionYearValue);
		totalYearBudget.add(sectionYearBudget);
		totalYearDiff.add(sectionYearDiff);
		
		this.addToTable(rowNumber, "", totalYTDBudget.toString(), 
				                       totalYTDValue.toString(), 
				                       totalYTDDiff.toString(), boldFont);
		rowNumber++;
		
		Object rValues[] = new Object[4];
		rValues[0] = (Object) new Integer(rowNumber);
		rValues[1] = (Object)totalYTDBudget;
		rValues[2] = (Object)totalYTDValue;
		rValues[3] = (Object)totalYTDDiff;
		
		return rValues;
	}

	@SuppressWarnings({ "unchecked", "rawtypes" })
	private static Map<Object,Object> sortByValue(Map<?,?> map) {
  	  List<?> list = new LinkedList(map.entrySet());
  	  
  	  Collections.sort(list, new Comparator() {
  		  public int compare(Object o1, Object o2) {
  			  return ((Comparable) ((Map.Entry) (o1)).getValue()).compareTo(((Map.Entry) (o2)).getValue());
  		  }
  	  });

  	  // logger.info(list);
  	  Map<Object, Object> result = new LinkedHashMap<Object, Object>();
  	  for (Iterator<?> it = list.iterator(); it.hasNext();) {
  		  Map.Entry<Object, Object> entry = (Map.Entry)it.next();
  		  result.put(entry.getKey(), entry.getValue());
  	  }
  	  return result;
    }
	
	private Image getImage(String urlName) {

        try {
            InputStream inputStream = getClass().getResourceAsStream(urlName);
            
            if (inputStream != null) {
                ByteArrayOutputStream outputStream = new ByteArrayOutputStream(1000);
                byte buffer[] = new byte[1024];
                int count;
                while ((count = inputStream.read(buffer, 0, buffer.length)) >= 0) {
                    outputStream.write(buffer, 0, count);
                }
                
                return Toolkit.getDefaultToolkit().createImage(outputStream.toByteArray());
            }
            
        } catch (IOException error) {
            error.printStackTrace();
        }
        
        return null;
        
    }
	
	
}
