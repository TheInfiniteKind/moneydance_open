/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.text.NumberFormat;
import java.util.Calendar;
import java.util.Collections;
import java.util.Comparator;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
//import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.File;
import java.util.Date;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

import javax.swing.Box;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JEditorPane;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.border.EmptyBorder;

import javax.xml.transform.*;  
import javax.xml.transform.dom.DOMSource;  
import javax.xml.transform.stream.StreamResult; 

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.apache.xerces.dom.DocumentImpl;
import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPReply;
import org.apache.commons.net.ftp.FTP;

import com.moneydance.awt.AwtUtil;

public class BudgetReportWindow extends JFrame {
	    private static final long serialVersionUID = 1L;
	    private Main        extension;
	    private boolean     taxIsIncome;
	    private BudgetData  data;
		private JEditorPane txtReport;
		private JEditorPane pntReport;
        private JButton     printButton;
        private JButton     publishButton;
        private JButton     closeButton;
        private JComboBox   reportPeriod;
        private JComboBox   reportYear;


        private String[] periodList;        
        // -------------------------------------------
        public BudgetReportWindow(Main ext) {
            super("MoneyPie Report");
            this.extension   = ext;
            this.data        = ext.getBudgetData();
            this.taxIsIncome = ext.getWindow().isTaxIncome();
            
            JPanel p = new JPanel(new GridBagLayout());
            p.setBorder(new EmptyBorder(10,10,10,10));

            // Text Area
            periodList = new String[] {
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December"
             };
            reportPeriod = new JComboBox(periodList);
            
            Calendar cal = Calendar.getInstance();
            reportPeriod.setSelectedIndex(cal.get(Calendar.MONTH));

            reportPeriod.addActionListener(new ActionListener() {
            	public void actionPerformed(ActionEvent e) {
            		updateReport();
                }
            });
            p.add(reportPeriod, AwtUtil.getConstraints(0,0,0,0,2,1,true,false));

            String[] yearList = new String[] {
            		"Expense",
            		"Income",
            		"Accounts"
             };
            
            reportYear = new JComboBox(yearList);
            reportYear.setSelectedIndex(0);
            reportYear.addActionListener(new ActionListener() {
            	public void actionPerformed(ActionEvent e) {
            		updateReport();
                }
            });
            p.add(reportYear, AwtUtil.getConstraints(2,0,0,0,2,1,true,false));

            pntReport = new JEditorPane();
            pntReport.setEditable(false);
            pntReport.setContentType("text/html");

            txtReport = new JEditorPane();
            txtReport.setEditable(false);
            txtReport.setContentType("text/html");
            updateReport();

            GridBagConstraints c = new GridBagConstraints();
            c.gridx=0;
            c.gridy=1;
            c.weightx=1;
            c.weighty=1;
            c.gridwidth=4;
            c.gridheight=1;
            c.fill=GridBagConstraints.BOTH;
            c.ipady = 480;
            p.add(new JScrollPane(txtReport),c);
            p.add(Box.createVerticalStrut(8), AwtUtil.getConstraints(0,3,0,0,1,1,false,false));
            printButton = new JButton("Print");
            printButton.addActionListener(new ActionListener() {
                        public void actionPerformed(ActionEvent e) {
                                print();
                        }
                });
            p.add(printButton, AwtUtil.getConstraints(0,4,1,0,1,1,false,true));

            publishButton = new JButton("Publish");
            publishButton.addActionListener(new ActionListener() {
                        public void actionPerformed(ActionEvent e) {
                        	try{
                                publish();
                        	}
                        	catch (Exception ee) {
                        		ee.printStackTrace();
                        	}

                        }
                });
            p.add(publishButton, AwtUtil.getConstraints(1,4,1,0,1,1,false,true));

            BudgetPreferences prefs = extension.getPreferences();
            String ftpHost            = prefs.getPublishDetails("ftpHost");
            if(ftpHost.length() < 1){
            	publishButton.setEnabled(false);
            }

            closeButton = new JButton("Close");
            closeButton.addActionListener(new ActionListener() {
                        public void actionPerformed(ActionEvent e) {
                                close();
                        }
                });
            p.add(closeButton, AwtUtil.getConstraints(2,4,1,0,1,1,false,true));

            getContentPane().add(p);

            setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            enableEvents(WindowEvent.WINDOW_CLOSING);

            setSize(1050, 800);
            AwtUtil.centerWindow(this);
        }

        public void updateReport(){
        	txtReport.setText(getReportStr());
        }
        
        private String getReportStr() {
        	StringBuffer sb = new StringBuffer();

        	sb.append("<HTML>");
        	sb.append("<HEAD>");
        	sb.append("<STYLE TYPE='text/css'>");
        	sb.append("body      {font-family : 'Times New Roman', Times, serif; }");
        	sb.append("body      {font-size: 11px; }");
        	sb.append("H2        {text-align:left; color:black;}");
        	sb.append("TABLE     {border: 1px solid #666666; }");
        	sb.append("TD        {border: 1px solid #666666; }");
        	sb.append("TD.head   {text-align:center; color:black; font-weight:bold; background-color:#c0c0c0}");
        	sb.append("TD.label  {text-align:left;   color:black; white-space:nowrap;}");
        	sb.append("TD.data   {text-align:right;  color:black;}");
        	sb.append("TD.diff   {text-align:right;  color:black; background-color:#c0c0c0}");
        	sb.append("TD.tl     {text-align:left;   color:black; font-weight:bold; background-color:#c0c0c0}");
        	sb.append("TD.total  {text-align:right;  color:black; font-weight:bold; background-color:#c0c0c0}");

        	sb.append("</STYLE>");
        	sb.append("</HEAD>");
        	sb.append("<BODY>");

        	String title = "";
        	if(reportYear.getSelectedIndex() == 0){
        		title = "Expenses";
        		sb.append(generateTables(title, data.getExpenseAccounts(), true));
        	}
        	if(reportYear.getSelectedIndex() == 1){
        		title = "Income";
        		sb.append(generateTables(title, data.getIncomeAccounts(), true));
        	}
        	if(reportYear.getSelectedIndex() == 2){
        		title = "Accounts";
        		sb.append(generateTables(title, data.getMoneyAccounts(), true));
        	}
        	
        	sb.append("</BODY>");
        	sb.append("</HTML>");

        	String month = periodList[reportPeriod.getSelectedIndex()];
        	this.setTitle("Report: " + title + " - " + month);
            return sb.toString();

        }

        private String generateTableCell(String cellClass, 
        								 BudgetValue cellValueB,
        								 BudgetValue cellValueA,
        								 BudgetValue cellValueD){
        	NumberFormat nf = NumberFormat.getNumberInstance();
            nf.setGroupingUsed(true);
            nf.setMinimumFractionDigits(2);
            nf.setMaximumFractionDigits(2);
            
        	String redColor   = "#ff3333";
           	String blackColor = "#000000";
           	
           	String cellColor = blackColor;
           	if(cellValueD.doubleValue() < 0){
           		cellColor = redColor;
           	}

           	StringBuffer sb = new StringBuffer();
           	
            sb.append("<TD class='"+cellClass+"'><FONT color='"+cellColor+"'>" + cellValueB.toString() + "</FONT></TD>");
            sb.append("<TD class='"+cellClass+"'><FONT color='"+cellColor+"'>" + cellValueA.toString() + "</FONT></TD>");
            sb.append("<TD class='total'><FONT color='"+cellColor+"'>" + cellValueD.toString() + "</FONT></TD>");
            
            return sb.toString();
        }
        
        @SuppressWarnings("rawtypes")
		private String generateTables(String label, Map accounts, boolean showSubTotals){
        	StringBuffer sb = new StringBuffer();
           	int reportIndex = reportPeriod.getSelectedIndex() + 1;

	  	    String topAccountName = "";
	  	    String lastTop        = "";
	  	    BudgetValue sectionTotalValue  = new BudgetValue(data, 0);
	  	    BudgetValue sectionTotalBudget = new BudgetValue(data, 0);
	  	    BudgetValue sectionTotalDiff   = new BudgetValue(data, 0);
	  	    BudgetValue sectionYTDValue    = new BudgetValue(data, 0);
	  	    BudgetValue sectionYTDBudget   = new BudgetValue(data, 0);
	  	    BudgetValue sectionYTDDiff     = new BudgetValue(data, 0);
	  	    BudgetValue sectionYearValue   = new BudgetValue(data, 0);
	  	    BudgetValue sectionYearBudget  = new BudgetValue(data, 0);
	  	    BudgetValue sectionYearDiff    = new BudgetValue(data, 0);
	  	    
	  	    BudgetValue totalValue         = new BudgetValue(data, 0);
	  	    BudgetValue totalBudget        = new BudgetValue(data, 0);
	  	    BudgetValue totalDiff          = new BudgetValue(data, 0);
	  	    BudgetValue totalYTDValue      = new BudgetValue(data, 0);
	  	    BudgetValue totalYTDBudget     = new BudgetValue(data, 0);
	  	    BudgetValue totalYTDDiff       = new BudgetValue(data, 0);
	  	    BudgetValue totalYearValue     = new BudgetValue(data, 0);
	  	    BudgetValue totalYearBudget    = new BudgetValue(data, 0);
	  	    BudgetValue totalYearDiff      = new BudgetValue(data, 0);


	  	    sb.append("<H2>"+label+"</H2>");

        	Iterator<?> k = sortByValue(accounts).keySet().iterator();
    	    while (k.hasNext()) {
    	      Integer acctNum = (Integer) k.next();
    	      String acctName = (String) accounts.get(acctNum);

    	      if(acctName.indexOf(":") > -1){
    	    	  topAccountName = acctName.substring(0, acctName.indexOf(":"));
    	      } else {
    	    	  topAccountName = acctName;
    	      }

    	      if(! showSubTotals) topAccountName = label;
    	      
    	      if(! topAccountName.equalsIgnoreCase(lastTop)){
    	    	  if(! lastTop.equals("")){
    	    		  sb.append("<TR>");
    	    	      sb.append("<TD class='tl'>Total</TD>");
    	    	      sb.append(generateTableCell("total", sectionTotalBudget, sectionTotalValue, sectionTotalDiff));
    	    	      sb.append(generateTableCell("total", sectionYTDBudget, sectionYTDValue, sectionYTDDiff));
    	    	      sb.append(generateTableCell("total", sectionYearBudget, sectionYearValue, sectionYearDiff));
    	    	      sb.append("</TR>");

    	    		  sb.append("</TABLE>");
    	    		  sb.append("<BR/><BR/>");

    	    		  
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

    	    	  sb.append("<TABLE width='90%' border='1'>");
    	    	  sb.append("<TR>");
    	    	  sb.append("<TD class='head' width='200'>&nbsp;</TD>");
    	    	  sb.append("<TD class='head' width='200' colspan='3' align='center'>"+reportPeriod.getSelectedItem().toString()+"</TD>");
    	    	  sb.append("<TD class='head' width='200' colspan='3' align='center'>YTD</TD>");
    	    	  sb.append("<TD class='head' width='200' colspan='3' align='center'>Year Total</TD>");
    	    	  sb.append("</TR>");

    	          sb.append("<TR>");
    		  	  sb.append("<TD class='head' width='200'>"+topAccountName+"</TD>");
    		  	  sb.append("<TD class='head' width='50'>Budgeted</TD>");
    		  	  sb.append("<TD class='head' width='50'>Actual</TD>");
    		  	  sb.append("<TD class='head' width='50'>Remaining</TD>");

    		      sb.append("<TD class='head' width='50'>Budgeted</TD>");
    		      sb.append("<TD class='head' width='50'>Actual</TD>");
    		  	  sb.append("<TD class='head' width='50'>Remaining</TD>");
    		  	 
    		  	  sb.append("<TD class='head' width='50'>Budgeted</TD>");
  		          sb.append("<TD class='head' width='50'>Actual</TD>");
  		  	      sb.append("<TD class='head' width='50'>Remaining</TD>");
  		  	  
    		  	  sb.append("</TR>");

    	      }
    	      
    	      
    	      
    	      
    	      //Month
    	      BudgetValue actualValue = new BudgetValue(data, 0);
    	      if(! data.isSpendingNull(acctName, reportIndex)){
    	    	  actualValue = data.getSpendingValue(acctName, reportIndex);
    	      }

    	      BudgetValue budgetValue = new BudgetValue(data, 0);
    	      if(! data.isBudgetNull(acctName, reportIndex)){
    	    	  budgetValue = data.getBudgetValue(acctName, reportIndex);
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
    	      BudgetValue ytdActual = data.getSTDValue(acctName, reportIndex);
    	      BudgetValue ytdBudget = data.getBTDValue(acctName, reportIndex);
    	      
    	      BudgetValue diffValue = new BudgetValue(data, budgetValue);
    	      diffValue.minus(actualValue);
    	      
    	      BudgetValue ytdDiff   = new BudgetValue(data, ytdBudget);
    	      ytdDiff.minus(ytdActual);
    	      
    	      BudgetValue diffYear = new BudgetValue(data, budgetYear);
    	      diffYear.minus(actualYear);

    	      acctName = acctName.substring(acctName.indexOf(":")+1);

    	      sb.append("<TR>");
    	      sb.append("<TD class='label'>" + acctName + "</TD>");
    	      sb.append(generateTableCell("data", budgetValue, actualValue, diffValue));
    	      sb.append(generateTableCell("data", ytdBudget, ytdActual, ytdDiff));
    	      sb.append(generateTableCell("data", budgetYear, actualYear, diffYear));
    	      sb.append("</TR>");

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

    	    sb.append("<TR>");
    	    sb.append("<TD class='tl'>Total</TD>");
    	    sb.append(generateTableCell("total", sectionTotalBudget, sectionTotalValue, sectionTotalDiff));
  	        sb.append(generateTableCell("total", sectionYTDBudget, sectionYTDValue, sectionYTDDiff));
  	        sb.append(generateTableCell("total", sectionYearBudget, sectionYearValue, sectionYearDiff));
  	        sb.append("</TR>");

  	        totalValue.add(sectionTotalValue);
	  	    totalBudget.add(sectionTotalBudget);
	  	    totalDiff.add(sectionTotalDiff);
	  	    
	  	    totalYTDValue.add(sectionYTDValue);
	  	    totalYTDBudget.add(sectionYTDBudget);
	  	    totalYTDDiff.add(sectionYTDDiff);
	  	    
	  	    totalYearValue.add(sectionYearValue);
	  	    totalYearBudget.add(sectionYearBudget);
	  	    totalYearDiff.add(sectionYearDiff);
	  	    
  	        sb.append("<TR>");
  	      	sb.append("<TD class='tl'>Grand Total</TD>");
  	      	sb.append(generateTableCell("total", totalBudget, totalValue, totalDiff));
  	        sb.append(generateTableCell("total", totalYTDBudget, totalYTDValue, totalYTDDiff));
  	      	sb.append(generateTableCell("total", totalYearBudget, totalYearValue, totalYearDiff));
	        sb.append("</TR>");
	        
    	    sb.append("</TABLE>");
    	    sb.append("<BR/><BR/>");
    	    

        	return sb.toString();
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

        /**
         * Print Report
         */
        protected void print() {
        	BudgetDocumentRenderer dr = new BudgetDocumentRenderer();
                pntReport.setText(txtReport.getText().replaceFirst("11px", "8px"));
                dr.print(pntReport);
        }

        private String getDateTime() {
            DateFormat dateFormat = new SimpleDateFormat("MMM-dd-yyyy");
            Date date = new Date();
            return dateFormat.format(date);
        }

        /**
         * Publish Report
         */
        protected void publish() throws Exception {
        	Document xmldoc= new DocumentImpl();
        	String period = reportPeriod.getSelectedItem().toString();

        	Element root = xmldoc.createElement("Budget");
        	root.setAttributeNS(null, "title", period);
        	root.setAttributeNS(null, "date", getDateTime());

        	Element iCat = getXMLReportSectionNode(xmldoc, "Income", data.getIncomeAccounts(), true);
        	iCat.setAttributeNS(null, "title", "Income");
        	root.appendChild(iCat);

        	Element eCat = getXMLReportSectionNode(xmldoc, "Expense", data.getExpenseAccounts(), true);
        	eCat.setAttributeNS(null, "title", "Expense");
        	root.appendChild(eCat);

        	Element aCat = getXMLReportSectionNode(xmldoc, "Accounts", data.getMoneyAccounts(), true);
        	aCat.setAttributeNS(null, "title", "Accounts");
        	root.appendChild(aCat);

        	xmldoc.appendChild(root);

    	    //Write XML out to Disk
        	BudgetPreferences prefs = extension.getPreferences();
        	String tmpPath          = prefs.getPublishDetails("tmpPath");
        	if(tmpPath.length() < 1){
        		tmpPath = "/tmp";
        	}
        	String xmlFileName = tmpPath+"/"+period+".xml";

        	
        	TransformerFactory tranFactory = TransformerFactory.newInstance();  
        	Transformer aTransformer = tranFactory.newTransformer();  
        	Source src = new DOMSource(xmldoc);  
        	Result dest = new StreamResult(new File(xmlFileName));  
        	aTransformer.transform(src, dest); 
        	
        	ftpReport(xmlFileName);

        }

        @SuppressWarnings("rawtypes")
		protected Element getXMLReportSectionNode(Document xmldoc, String label, Map accounts, boolean showSubTotals) throws Exception {
        	int reportIndex = reportPeriod.getSelectedIndex() + 1;

	  	    String topAccountName          = "";
	  	    String lastTop                 = "";
	  	    BudgetValue sectionTotalValue  = new BudgetValue(data, 0);
	  	    BudgetValue sectionTotalBudget = new BudgetValue(data, 0);
	  	    BudgetValue sectionTotalDiff   = new BudgetValue(data, 0);
	  	    int    sectionCount            = 0;


            Element eCat = xmldoc.createElementNS(null, label);
            Element eSummary = xmldoc.createElementNS(null, "summary");


        	Iterator<?> k = sortByValue(accounts).keySet().iterator();
    	    while (k.hasNext()) {
    	      Integer acctNum = (Integer) k.next();
    	      String acctName = (String) accounts.get(acctNum);

    	      if(acctName.indexOf(":") > -1){
    	    	  topAccountName = acctName.substring(0, acctName.indexOf(":"));
    	      } else {
    	    	  topAccountName = acctName;
    	      }
    	      if(! showSubTotals) topAccountName = label;

    	      if(! topAccountName.equalsIgnoreCase(lastTop)){
    	    	  if(! lastTop.equals("")){

    	    		  eSummary.setAttributeNS(null, "name", lastTop);
    	    		  eSummary.setAttributeNS(null, "title", lastTop);
    	    		  if(sectionCount > 1){
    	    			  eSummary.setAttributeNS(null, "href", label+"_"+lastTop.replaceAll(" ", "_"));
    	    		  }
    	    		  eSummary.setAttributeNS(null, "budget", sectionTotalBudget.toString());
    	    		  eSummary.setAttributeNS(null, "actual", sectionTotalValue.toString());
    	    		  eSummary.setAttributeNS(null, "remaining", sectionTotalDiff.toString());
    	          	  eCat.appendChild(eSummary);

    	          	  eSummary = xmldoc.createElementNS(null, "summary");

    	    		  sectionTotalValue.setValue(0);
    	  	  	      sectionTotalBudget.setValue(0);
    	  	  	      sectionTotalDiff.setValue(0);
    	  	  	      sectionCount = 0;
    	    	  }

    	      }

    	      BudgetValue actualValue = new BudgetValue(data, 0);
    	      if(! data.isSpendingNull(acctName, reportIndex)){
    	    	  actualValue = data.getSpendingValue(acctName, reportIndex);
    	      }

    	      BudgetValue budgetValue = new BudgetValue(data, 0);
    	      if(! data.isBudgetNull(acctName, reportIndex)){
    	    	  budgetValue = data.getBudgetValue(acctName, reportIndex);
    	      }

    	      BudgetValue budgetYear = new BudgetValue(data, 0);
    	      if(! data.isBudgetNull(acctName, 0)){
    	    	  budgetYear = data.getBudgetValue(acctName, 0);
    	      }

    	      if(taxIsIncome && topAccountName.indexOf("Taxes") > -1){
    	    	  budgetValue.negate();
    	    	  budgetYear.negate();
    	      }
    	      
    	      BudgetValue diffValue = new BudgetValue(data, budgetValue);
    	      diffValue.minus(actualValue);

    	      if(taxIsIncome && topAccountName.indexOf("Taxes") > -1){
    	    	  diffValue.negate();
    	      }

    	      acctName = acctName.substring(acctName.indexOf(":")+1);

    	      Element eItem = xmldoc.createElementNS(null, "summary");
    	      eItem.setAttributeNS(null, "name", acctName);
    	      eItem.setAttributeNS(null, "budget", budgetValue.toString());
    	      eItem.setAttributeNS(null, "actual", actualValue.toString());
    	      eItem.setAttributeNS(null, "remaining", diffValue.toString());
    	      eSummary.appendChild(eItem);
    	      sectionCount++;

    	      sectionTotalValue.add(actualValue);
    	      sectionTotalBudget.add(budgetValue);
    	      sectionTotalDiff.add(diffValue);

    	      if(showSubTotals) lastTop = topAccountName;
    	      if(! showSubTotals) lastTop = label;

    	    }

    	    eSummary.setAttributeNS(null, "name", topAccountName);
    	    eSummary.setAttributeNS(null, "title", topAccountName);
    	    if(sectionCount > 1){
    	    	eSummary.setAttributeNS(null, "href", label+"_"+topAccountName.replaceAll(" ", "_"));
    	    }
  		    eSummary.setAttributeNS(null, "budget", sectionTotalBudget.toString());
  		    eSummary.setAttributeNS(null, "actual", sectionTotalValue.toString());
  		    eSummary.setAttributeNS(null, "remaining", sectionTotalDiff.toString());
        	eCat.appendChild(eSummary);

        	return eCat;
        }

        protected void ftpReport(String fileToTransmit) {
            try {
            	BudgetPreferences prefs = extension.getPreferences();
                String ftpHost            = prefs.getPublishDetails("ftpHost");
                String ftpUserName        = prefs.getPublishDetails("ftpUserName");
                String ftpPassword        = prefs.getPublishDetails("ftpPassword");
                String ftpRemoteDirectory = prefs.getPublishDetails("ftpRemoteDirectory");

                //TODO: Append Year to remote Path
                //TODO: Create remote path if it does not exist
                
                //Create a Jakarta Commons Net FTP Client object
                FTPClient ftp = new FTPClient();

                //A datatype to store responses from the FTP server
                int reply;

                //Connect to the server
                //
                ftp.connect(ftpHost);

                // After connection attempt, you should check the reply code to verify
                // success.
                //
                reply = ftp.getReplyCode();
                if(!FTPReply.isPositiveCompletion(reply)) {
                    try {
                        ftp.disconnect();
                    } catch (Exception e) {
                        System.err.println("Unable to disconnect from FTP server " +
                                           "after server refused connection. "+e.toString());
                    }
                    throw new Exception ("FTP server refused connection.");
                }
                System.err.println("Connected to " + ftpHost + ". "+ftp.getReplyString());

                //Try to login
                if (!ftp.login(ftpUserName, ftpPassword)) {
                    throw new Exception ("Unable to login to FTP server " +
                                         "using username "+ftpUserName+" " +
                                         "and password "+ftpPassword);
                }

                System.err.println(ftp.getReplyString());
                System.err.println("Remote system is " + ftp.getSystemName());

                //
                //Set our file transfer mode to either ASCII or Binary
                //
                //ftp.setFileType(FTP.ASCII_FILE_TYPE);
                ftp.setFileType(FTP.BINARY_FILE_TYPE);

                //
                //Change the remote directory
                //
                if (ftpRemoteDirectory != null && ftpRemoteDirectory.trim().length() > 0) {
                    System.err.println("Changing to FTP remote dir: " + ftpRemoteDirectory);
                    ftp.changeWorkingDirectory(ftpRemoteDirectory);
                    reply = ftp.getReplyCode();

                    if(!FTPReply.isPositiveCompletion(reply)) {
                        throw new Exception ("Unable to change working directory " +
                                             "to:"+ftpRemoteDirectory);
                    }
                }

                //
                //Get the file that we will transfer and send it.
                //
                File f = new File(fileToTransmit);
                System.err.println("Storing file as remote filename: " + f.getName());
                boolean retValue = ftp.storeFile(f.getName(), new FileInputStream(f));
                if (!retValue) {
                  throw new Exception ("Storing of remote file failed. ftp.storeFile()" +
                                       " returned false.");
                }

                //
                //Disconnect from the FTP server
                //
                try {
                    //ftp.logout();
                    ftp.disconnect();
                } catch (Exception exc) {
                    System.err.println("Unable to disconnect from FTP server. " + exc.toString());
                }

                //f.delete();

            } catch (Exception e) {
                System.err.println("Error: "+e.toString());
            }

            System.err.println("Process Complete.");
        }
        
        /** Close Window */
        protected void close() {
                this.setVisible(false);
                this.dispose();
        }
}
