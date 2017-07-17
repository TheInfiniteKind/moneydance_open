/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;


import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import javax.swing.JPanel;
import javax.swing.Box;
import javax.swing.JComboBox;
import javax.swing.JTabbedPane;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.JButton;
import javax.swing.ButtonGroup;
import javax.swing.JRadioButton;
import javax.swing.JFrame;
import javax.swing.border.EmptyBorder;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.AwtUtil;

public class BudgetPreferencesWindow extends JFrame {
	    private static final long serialVersionUID = 1L;
	    private Main         extension;
	    
	    private JComboBox<String> accountMain;
	    private JComboBox<String> defaultBudget;
	    private JRadioButton yesButton;
	    private JRadioButton noButton;
	    private JTextField textThreshold;
      
        // -------------------------------------------
        public BudgetPreferencesWindow(Main ext) {
            super("MoneyPie Preferences");
            this.extension  = ext;
            
            JPanel p = new JPanel(new GridBagLayout());
            p.setBorder(new EmptyBorder(10,10,10,10));


            JTabbedPane pTabs = new JTabbedPane( );
            JPanel pDefaults = new JPanel(new GridBagLayout());
            JPanel pPublish = new JPanel(new GridBagLayout());

            JLabel labelAcct = new JLabel( "Main Account"  );
             accountMain = new JComboBox<String>();
            
            
            JLabel labelBudget = new JLabel( "Default Budget"  );
            defaultBudget = new JComboBox<String>();
            
            JLabel labelTax = new JLabel( "Group Tax w/Income"  );
            yesButton = new JRadioButton("Yes");
            noButton  = new JRadioButton("No");
            ButtonGroup group = new ButtonGroup();
            group.add(yesButton);
            group.add(noButton);
            
            JLabel labelThreshold = new JLabel( "Large Balance Threshold"  );
            textThreshold = new JTextField();
            
            JButton saveButton   = new JButton( "Save");
            JButton cancelButton = new JButton( "Cancel");
            
            //Defaults
            pDefaults.add( Box.createHorizontalStrut(5), 
		                                   AwtUtil.getConstraints(0,0,0.05f,0,1,1,true,false));
            pDefaults.add( labelAcct,      AwtUtil.getConstraints(1,0,0.2f,0,1,1,true,false));
            pDefaults.add( accountMain,    AwtUtil.getConstraints(2,0,0.7f,0,3,1,true,false));
            pDefaults.add( Box.createHorizontalStrut(5), 
                                           AwtUtil.getConstraints(4,0,0.05f,0,1,1,true,false));
            
            pDefaults.add( Box.createHorizontalStrut(5), 
                                           AwtUtil.getConstraints(0,1,0.05f,0,1,1,true,false));
            pDefaults.add( labelBudget,    AwtUtil.getConstraints(1,1,0.2f,0,1,1,true,false));
            pDefaults.add( defaultBudget,  AwtUtil.getConstraints(2,1,0.7f,0,3,1,true,false));
            pDefaults.add( Box.createHorizontalStrut(5), 
                                           AwtUtil.getConstraints(4,1,0.05f,0,1,1,true,false));
            
            pDefaults.add( Box.createHorizontalStrut(5), 
                                           AwtUtil.getConstraints(0,2,0.05f,0,1,1,true,false));
			pDefaults.add( labelTax,       AwtUtil.getConstraints(1,2,0.20f,0,1,1,true,false));
			pDefaults.add( yesButton,      AwtUtil.getConstraints(2,2,0,0,1,1,false,false));
			pDefaults.add( noButton,       AwtUtil.getConstraints(3,2,0,0,1,1,false,false));
			pDefaults.add( Box.createHorizontalStrut(5), 
                                           AwtUtil.getConstraints(4,2,0.70f,0,1,1,true,false));
			pDefaults.add( Box.createHorizontalStrut(5), 
                                           AwtUtil.getConstraints(5,2,0.05f,0,1,1,true,false));

			pDefaults.add( Box.createHorizontalStrut(5), 
                    					   AwtUtil.getConstraints(0,3,0.05f,0,1,1,true,false));
			pDefaults.add( labelThreshold, AwtUtil.getConstraints(1,3,0.2f,0,1,1,true,false));
			pDefaults.add( textThreshold,  AwtUtil.getConstraints(2,3,0.7f,0,3,1,true,false));
			pDefaults.add( Box.createHorizontalStrut(5), 
			                    		   AwtUtil.getConstraints(4,3,0.05f,0,1,1,true,false));
			
			
            pDefaults.add( Box.createVerticalStrut(5), 
                                           AwtUtil.getConstraints(0,4,1,1,6,1,true,false));
            
            
            //Publish
            
            JLabel labelLater = new JLabel( "Just reserving this space ..."  );
            
            pPublish.add( Box.createHorizontalStrut(5), 
                                          AwtUtil.getConstraints(0,0,0.05f,1,1,1,true,true));
            pPublish.add( labelLater,     AwtUtil.getConstraints(1,0,0.2f,1,1,1,true,true));
            pPublish.add( Box.createHorizontalStrut(5), 
			                              AwtUtil.getConstraints(2,0,0.05f,1,1,1,true,true));

            //Dialog layout
            pTabs.addTab("Settings",pDefaults);
            pTabs.addTab("Publish",pPublish);
            
            p.add( pTabs,        AwtUtil.getConstraints(0,0,1,1,5,1,true,true));
            
            p.add( Box.createHorizontalStrut(20), 
            		             AwtUtil.getConstraints(0,1,0.3f,0,1,1,true,false));
            p.add( saveButton,   AwtUtil.getConstraints(1,1,0.15f,0,1,1,false,false));
            p.add( Box.createHorizontalStrut(20), 
		                         AwtUtil.getConstraints(2,1,0.1f,0,1,1,true,false));
            p.add( cancelButton, AwtUtil.getConstraints(3,1,0.15f,0,1,1,false,false));
            p.add( Box.createHorizontalStrut(20), 
		                         AwtUtil.getConstraints(4,1,0.3f,0,1,1,true,false));
            
            this.loadValues();
            
            //Listeners
            cancelButton.addActionListener(new ActionListener() {
                        public void actionPerformed(ActionEvent e) {
                                close();
                        }
            });
            saveButton.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                	saveValues();
                	close();
                }
            });
            

            getContentPane().add(p);

            setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            enableEvents(WindowEvent.WINDOW_CLOSING);
            
            setSize(400, 300);
            AwtUtil.centerWindow(this);
        }

        private void loadValues(){
        	BudgetPreferences prefs = extension.getPreferences();
        	String largeThreshold   = prefs.getDefaults("large");
  		  	if(largeThreshold == "") {
  			  largeThreshold = "10000";
  		  	}
        	textThreshold.setText(largeThreshold);
	  		
	  		if(prefs.getDefaults("taxIsIncome").indexOf("y") > -1){
	  	    	yesButton.setSelected(true);
	  	    } else {
	  	    	noButton.setSelected(true);
	  	    }
	  		
	  		BudgetData data = this.extension.getBudgetData();
	  		List<Budget> budgetList = data.getBudgetList().getAllBudgets();
	  		
	  		//Sort Budgets by Name
	  		List<String> budgetNames = new ArrayList<String>();
	  		for (int i = 0; i < budgetList.size(); i++) {
	  			String thisBudget = budgetList.get(i).getName();
	  			budgetNames.add(thisBudget);
	  		}
	  		Collections.sort(budgetNames);
	  		
	  		String startingBudget = prefs.getDefaults("budget");
	  		
	  		for (int i = 0; i < budgetNames.size(); i++) {
	  		  String thisBudget = (String)budgetNames.get(i);
	  			
	  		  defaultBudget.addItem(thisBudget);
	  		  if(startingBudget.equalsIgnoreCase(thisBudget)){
	  			defaultBudget.setSelectedIndex(defaultBudget.getItemCount() - 1);
	  		  }
		  	}
	  		
	  		
	  		//Load Accounts
	  		
	  		Account mainAccount = data.getMainAccount();
	  		if(mainAccount != null){
	  			accountMain.addItem(mainAccount.getAccountName());
	  		} else {
	  			accountMain.addItem("");
	  		}
	  		
	  		accountMain.setSelectedIndex(0);
	  		
	  		Iterator<?> k = sortByValue(data.getMoneyAccounts()).keySet().iterator();
		    while (k.hasNext()) {
		      Integer acctNum = (Integer) k.next();
		      String acctName = (String) data.getMoneyAccounts().get(acctNum);
		      accountMain.addItem(acctName);
		    }
        }
        
        private void saveValues(){
        	String newAccountName   = (String)accountMain.getSelectedItem();
        	BudgetData data = this.extension.getBudgetData();
        	if(data.getMainAccount() != null){
        		if(! data.getMainAccount().getAccountName().equalsIgnoreCase(newAccountName)){
            		data.getMainAccount().setComment("");
            		data.getAccount(newAccountName).setComment("MAIN");
            	}
        	} else {
        		data.getAccount(newAccountName).setComment("MAIN");
        	}
        	

        	String defaultBudgetName = (String)defaultBudget.getSelectedItem();
        	String taxIsIncome       = "n";
        	if(yesButton.isSelected()){
        		taxIsIncome = "y";
        	}
        	if(noButton.isSelected()){
        		taxIsIncome = "n";
        	}
        	
        	String largeThreshold = textThreshold.getText();
        	
        	Hashtable<String, String>  defaultValues   = new Hashtable<String, String>();
        	defaultValues.put("budget", defaultBudgetName);
        	defaultValues.put("large", largeThreshold);
        	defaultValues.put("taxIsIncome", taxIsIncome);
        	
        	extension.getPreferences().saveDefaults(defaultValues);
        	this.extension.getWindow().refresh();
        }
        
        @SuppressWarnings({ "rawtypes", "unchecked" })
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

        /** Close Window */
        protected void close() {
                this.setVisible(false);
                this.dispose();
        }
}
