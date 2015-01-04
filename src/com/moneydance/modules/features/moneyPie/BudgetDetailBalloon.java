package com.moneydance.modules.features.moneyPie;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;

import javax.swing.Box;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.UIManager;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.AwtUtil;

@SuppressWarnings("serial")
public class BudgetDetailBalloon extends BudgetBalloon {

	private JPanel sPanel;
	private JPanel dPanel;
	private int numTxn;
	String[][] records;
	
	BudgetDetailBalloon(BudgetTable table, BudgetData data){
		super(table, data);
	}
	
	public void setBalloonContent(){
		//Color fillColor       = new Color(235,235,235);
		Color fillColor       = Color.BLACK;
		Color transparentFill = new Color(fillColor.getRed(), 
                fillColor.getGreen(), 
                fillColor.getBlue(), 0);
		

		String acctName  = (String) this.getTable().getModel().getValueAt(this.getBalloonRow(), 0);
		fetchSpendingData(acctName, this.getBalloonCol());
		String[] columnNames = {"Date", "Account", "Amount"};
		
		Object tObject = this.getTable().getModel().getValueAt(this.getBalloonRow(), this.getBalloonCol());
		BudgetValue bValue = new BudgetValue(this.getData(), 0);
		if(tObject instanceof String ){
			bValue.setValue((String) tObject);
		}
		if(tObject instanceof BudgetValue ){
			bValue.setValue((BudgetValue) tObject);
		}

		if(! this.getData().isBudgetNull(acctName, this.getBalloonCol())){
			BudgetValue value = this.getData().getBudgetValue(acctName, this.getBalloonCol());
			if(! bValue.isEqual(0)){
				bValue.setValue(value);
			}
		}
		
		BudgetValue sValue = new BudgetValue(this.getData(), 0);
		if(! this.getData().isSpendingNull(acctName, this.getBalloonCol())){
			sValue.setValue(this.getData().getSpendingValue(acctName, this.getBalloonCol()));
		}
        
		BudgetValue dValue = new BudgetValue(this.getData(), bValue);
		dValue.minus(sValue);

		Font defaultFont = UIManager.getDefaults().getFont("TabbedPane.font");
		Font smallFont = new Font(defaultFont.getFontName(), Font.PLAIN, defaultFont.getSize() - 2);
		Font largeFont = new Font(defaultFont.getFontName(), Font.BOLD, defaultFont.getSize() + 5);
		
		sPanel = new JPanel(new GridBagLayout());
		sPanel.setBackground(transparentFill);
		
		JLabel diffLabel = new JLabel( dValue.toString() );
		diffLabel.setFont(largeFont);
		
		if(dValue.isNegative()){
			diffLabel.setForeground(Color.RED);
		} else {
			diffLabel.setForeground(Color.GREEN);
		}
		
		sPanel.add(diffLabel,                              AwtUtil.getConstraints(0,0,0.25f,1,1,2,true,true));
		sPanel.add(Box.createHorizontalStrut(20),          AwtUtil.getConstraints(1,0,0.25f,1,1,2,true,true));

		JLabel budgetLabel = new JLabel("Budgeted");
		budgetLabel.setFont(smallFont);
		//budgetLabel.setForeground(Color.WHITE);
		
		JLabel actualLabel = new JLabel("Actual");
		actualLabel.setFont(smallFont);
		//actualLabel.setForeground(Color.WHITE);
		
		sPanel.add(budgetLabel,                            AwtUtil.getConstraints(2,0,0.25f,1,1,1,true,true));
		sPanel.add(new JLabel( bValue.toString() ),        AwtUtil.getConstraints(4,0,0.25f,1,1,1,true,true));
		
		sPanel.add(Box.createHorizontalStrut(8),           AwtUtil.getConstraints(3,0,0.25f,1,1,2,true,true));
		
		sPanel.add(actualLabel           ,                 AwtUtil.getConstraints(2,1,0.25f,1,1,1,true,true));
		sPanel.add(new JLabel( sValue.toString() ),        AwtUtil.getConstraints(4,1,0.25f,1,1,1,true,true));
		
		sPanel.add(Box.createVerticalStrut(8),             AwtUtil.getConstraints(0,2,1,1,5,1,true,true));
		
		if(numTxn > 0){
			String text = "Transactions";
			if(numTxn == 1) text = "Transaction";
			JButton txnButton = new JButton(numTxn + " " + text);
			//txnButton.setContentAreaFilled(false);
			txnButton.setBackground(transparentFill);
			txnButton.setBorderPainted(false);
			txnButton.setForeground(Color.WHITE);
			txnButton.addActionListener(new ActionListener() {
	                public void actionPerformed(ActionEvent e) {
	                        showTransactions();
	                }
	        });
			
			GridBagConstraints c = new GridBagConstraints();
            c.gridx=0;
            c.gridy=3;
            c.weightx=1;
            c.weighty=1;
            c.gridwidth=5;
            c.gridheight=1;
            c.fill=GridBagConstraints.HORIZONTAL;
            sPanel.add(txnButton, c);
		}
		
		this.setContents(sPanel);
		
		dPanel = new JPanel(new GridBagLayout());
		dPanel.setBackground(transparentFill);
		
		JTable table = new JTable(records, columnNames);
		
		JScrollPane scrollPane = new JScrollPane(table);
		scrollPane.setPreferredSize(new Dimension(300,70));
		
		Image backImage = getImage("/com/moneydance/modules/features/moneyPie/images/arrow_left_small.gif");
		JButton backButton;
		if(backImage != null){
			ImageIcon backIcon = new ImageIcon(backImage);
			backButton = new JButton(backIcon);
		} else {
			backButton = new JButton("");
		}

		backButton.setBorderPainted(false);
		backButton.setPreferredSize(new Dimension(14, 21) );
		
		backButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
            	showSummary();
            }
        });
		
		dPanel.add(backButton,                   AwtUtil.getConstraints(0,0,1,1,1,1,false,true));
		dPanel.add(Box.createHorizontalStrut(8), AwtUtil.getConstraints(1,0,0,0,1,1,false,false));
		dPanel.add(scrollPane,                   AwtUtil.getConstraints(2,0,0,1,1,1,true,false));
		
	}
	
	private void showSummary(){
		this.setContents(sPanel);
	}
	
	private void showTransactions(){
		this.setContents(dPanel);
	}
	
	private void fetchSpendingData(String acctName, int month){
		  numTxn = 0;
		  ArrayList<String[]> spendList = new ArrayList<String[]>();

		  TxnSet ts = this.getData().getRoot().getBook().getTransactionSet().getAllTxns();
		  for (int i = 0; i < ts.getSize(); i++) {
	          AbstractTxn t = ts.getTxn(i);
	          Account txnAccount    = t.getAccount();
	          Account othAccount    = t.getOtherTxn(0).getAccount();

	          if(txnAccount.getComment().indexOf("IGNORE") > -1) continue;
	          if(othAccount.getComment().indexOf("IGNORE") > -1 && othAccount.getAccountType() == Account.AccountType.EXPENSE) continue;
	          if(! txnAccount.getFullAccountName().equalsIgnoreCase(acctName)) continue;
	          
	          String dt = (new Integer(t.getDateInt())).toString();
	          GregorianCalendar gc = new GregorianCalendar();
	          gc.set(Calendar.YEAR, new Integer(dt.substring(0,4)).intValue() );
	          gc.set(Calendar.MONTH, new Integer(dt.substring(4,6)).intValue() - 1 );
	          gc.set(Calendar.DAY_OF_MONTH, new Integer(dt.substring(6,8)).intValue() );
	          gc.set(Calendar.HOUR_OF_DAY,0);
	          gc.set(Calendar.MINUTE,0);
	          gc.set(Calendar.SECOND,0);
	          gc.set(Calendar.MILLISECOND,0);

	          //TODO: Lookup for given month
	          int lastDayOfMonth = 28;
	          
	          if (BudgetDateUtil.isInRange(gc.getTime(),
	        		  new GregorianCalendar(this.getData().getCurrentBudgetYear(), month - 1, 1).getTime(),
	        		  new GregorianCalendar(this.getData().getCurrentBudgetYear(), month - 1, lastDayOfMonth).getTime())) {

	        	  Account topLvlAccount = txnAccount.getParentAccount();
		          while(topLvlAccount.getParentAccount() != null){
		        	  if(topLvlAccount.getParentAccount().getFullAccountName().length() > 0){
		        		  topLvlAccount = topLvlAccount.getParentAccount();
		        	  } else {
		        		  break;
		        	  }
		          }

		          BudgetValue value = new BudgetValue(this.getData(), t.getValue());
		          value.divide(100.00);  

		          SimpleDateFormat formatter = new SimpleDateFormat("MM/dd/yy");
		          String[] thisRecord = {formatter.format(gc.getTime()) , 
		        		                 t.getDescription(), 
		        		                 value.toString()};
		          spendList.add(thisRecord);
		          numTxn++;
	          }
		  }
		  
		  records = new String[numTxn][3];
		  for(int i=0;i<spendList.size();i++){
			  records[numTxn-i-1] = spendList.get(i);
		  }
		  
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
