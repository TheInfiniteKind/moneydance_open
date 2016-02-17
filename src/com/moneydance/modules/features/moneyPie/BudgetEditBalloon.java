package com.moneydance.modules.features.moneyPie;

import java.awt.Color;
import java.awt.GridBagLayout;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.GregorianCalendar;

import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;

import javax.swing.Box;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.JPanel;
import javax.swing.JComboBox;
import javax.swing.JButton;

import javax.swing.Popup;
import javax.swing.PopupFactory;

import com.infinitekind.moneydance.model.*;
import com.moneydance.awt.AwtUtil;
import com.moneydance.awt.DatePicker;

@SuppressWarnings("serial")
public class BudgetEditBalloon extends BudgetBalloon {

	private JPanel      ePanel;
	private JTextField  bText;
	private JComboBox<String> rList;
	
	private JButton     sButton;
	private JButton     eButton;
	
	private JButton     saveButton;
	private JButton     cancelButton;
	
	private boolean     rListUpdate;
	private BudgetItem  bi;
	private BudgetValue currentValue;
	private String      accountName;
	
	BudgetEditBalloon(BudgetTable table, BudgetData data){
		super(table, data);
		rListUpdate = false;
	}
	
	public void setBalloonContent(){

		this.setBudgetItem();
		this.setCurrentValue();
		
		Color fillColor       = Color.BLACK;
		Color transparentFill = new Color(fillColor.getRed(), 
                fillColor.getGreen(), 
                fillColor.getBlue(), 0);
		
		
		JLabel bLabel = new JLabel("Budget Value");
		JLabel rLabel = new JLabel("Repeat");
		JLabel sLabel = new JLabel("Start");
		JLabel eLabel = new JLabel("End");
		
		saveButton   = new JButton("Save");
		cancelButton = new JButton("Cancel");
		
		cancelButton.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  setVisible(false);
	          }
	      });
		
		saveButton.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
	        	  currentValue.setValue(bText.getText());
	        	  	
	        	  int sDate = 0;
	        	  int eDate = 0;
	        	  
	        	  if(sButton.getText().length()>0){
	        		  sDate = getIntFromDateString(sButton.getText());
	        	  }
	        	  if(eButton.getText().length()>0){
	        		  eDate = getIntFromDateString(eButton.getText());
	        	  }
	        	  
	        	  int interval = getInterval();
	        	  
	        	  if(bi == null){
	        		  getData().budgetAddItem(accountName, getBalloonCol(), currentValue);
	        		  setBudgetItem();
	        	  } else {
	        		  currentValue.multiply(100.00);
	        		  bi.setAmount(currentValue.longValue());
	        	  }

        		  
        		  if(sDate == 0 || eDate == 0){
        			  sDate = 0;
        			  eDate = 0;
        			  interval = BudgetItem.INTERVAL_NO_REPEAT;
        		  }
        		  
        		  if(eDate - sDate < 32){
        			  if(interval == BudgetItem.INTERVAL_TRI_WEEKLY ||
        			      interval == BudgetItem.INTERVAL_MONTHLY ||
        			      interval == BudgetItem.INTERVAL_BI_MONTHLY ||
        			      interval == BudgetItem.INTERVAL_TRI_MONTHLY ||
        			      interval == BudgetItem.INTERVAL_SEMI_ANNUALLY ||
        			      interval == BudgetItem.INTERVAL_ANNUALLY ){
        				  
        				  interval = BudgetItem.INTERVAL_NO_REPEAT;
        				  sDate = 0;
	        			  eDate = 0;
        			  }
        		  }
        		  
        		  bi.setInterval(interval);
        		  if(interval != BudgetItem.INTERVAL_NO_REPEAT){
        			  bi.setIntervalStartDate(sDate);
    	        	  bi.setIntervalEndDate(eDate);
        		  }

	        	  getTable().refresh();
	        	  setVisible(false);
	          }
	      });
		
		sButton = new JButton();
		this.setStartDate(sButton);
		sButton.addActionListener(new ShowPopupActionListener(this, sButton));

		eButton = new JButton();
		this.setEndDate(eButton);
		eButton.addActionListener(new ShowPopupActionListener(this, eButton));
		
		bText = new JTextField();
		bText.setText(currentValue.rawString());

		String[] repeatStrings = { "None", 
				                   "Daily", 
				                   "Weekly",
				                   "Semi-Monthly",
				                   "Bi-Weekly", 
				                   "Tri-Weekly",
				                   "Monthly",
				                   "Bi-Monthly",
				                   "Quaterly",
				                   "Semi-Annual",
				                   "Annual"
				                   };
		rList = new JComboBox <String> (repeatStrings);
		rList.setSelectedIndex(0);
		rList.addActionListener(new ActionListener() {
	          public void actionPerformed(ActionEvent evt) {
		    	  if(! rListUpdate){
		    		  String repeatValue = (String)rList.getSelectedItem();
			          	System.err.println("Set Repeat " + repeatValue + " - " + rList.getSelectedIndex());
		    	  }
	          }
	      }); 
		
		ePanel = new JPanel(new GridBagLayout());
		ePanel.setBackground(transparentFill);
		ePanel.add(bLabel,  AwtUtil.getConstraints(0,1, 1,1, 1,1, true,true));
		ePanel.add(Box.createHorizontalStrut(4), 
				            AwtUtil.getConstraints(1,1, 1,1, 1,1,true,true));
		ePanel.add(bText,   AwtUtil.getConstraints(2,1, 1,1, 2,1, true,true));
		
		ePanel.add(rLabel,  AwtUtil.getConstraints(0,3, 1,1, 1,1, true,true));
		ePanel.add(Box.createHorizontalStrut(4), 
				            AwtUtil.getConstraints(1,3, 1,1, 1,1,true,true));
		
		ePanel.add(rList,   AwtUtil.getConstraints(2,3, 1,1, 2,1, true,true));
		
		ePanel.add(sLabel,  AwtUtil.getConstraints(0,5, 1,1, 1,1, true,true));
		ePanel.add(Box.createHorizontalStrut(4), 
				            AwtUtil.getConstraints(1,5, 1,1, 1,1,true,true));
		
		ePanel.add(sButton, AwtUtil.getConstraints(2,5, 1,1, 2,1, true,true));
		
		ePanel.add(eLabel,  AwtUtil.getConstraints(0,7, 1,1, 1,1, true,true));
		ePanel.add(Box.createHorizontalStrut(4), 
				            AwtUtil.getConstraints(1,7, 1,1, 1,1,true,true));
		ePanel.add(eButton, AwtUtil.getConstraints(2,7, 1,1, 2,1, true,true));
		
		ePanel.add(cancelButton, AwtUtil.getConstraints(2,9, 1,1, 1,1, true,true));
		ePanel.add(saveButton,   AwtUtil.getConstraints(3,9, 1,1, 1,1, true,true));
		
		this.setRepeatValue();
		this.setContents(ePanel);
	}
	
	private void setAccountName() {
	  if(row > -1){
		  accountName = (String) this.getTable().getModel().getValueAt(this.getBalloonRow(), 0);
	  } else {
		  accountName = "";
	  }
	}
	
	private void setBudgetItem(){
		setAccountName();
  	  	bi = this.getData().getBudgetItem(accountName, this.getBalloonCol());
	}
	
	private void setCurrentValue(){
		double actualValue = this.getData().fetchBudgetValue(accountName, this.getBalloonCol());
		
		currentValue = new BudgetValue(this.getData(), 0);
		if(actualValue != 0){
			currentValue.setValue(actualValue);
		} else {
			String value = (String) this.getTable().getModel().getValueAt(this.getBalloonRow(), this.getBalloonCol());
			currentValue.setValue(value);
		}
	}
	
	private void setStartDate(JButton button){
		if(bi == null) return;
		Date startDate = BudgetDateUtil.getDateYYYYMMDD(bi.getIntervalStartDate());
		SimpleDateFormat formatter = new SimpleDateFormat("MM/dd/yyyy");
		button.setText(formatter.format(startDate.getTime()));
	}
	
    private void setEndDate(JButton button){
    	if(bi == null) return;
    	Date etartDate = BudgetDateUtil.getDateYYYYMMDD(bi.getIntervalEndDate());
    	SimpleDateFormat formatter = new SimpleDateFormat("MM/dd/yyyy");
		button.setText(formatter.format(etartDate.getTime()));
	}
	
    private int getIntFromDateString(String dateString){
    	  int dateInt = 0;
		  SimpleDateFormat format = new SimpleDateFormat("MM/dd/yyyy");
		  try {
				Date thisDate = format.parse(dateString);
				SimpleDateFormat formatter = new SimpleDateFormat("yyyyMMdd");
				dateInt = Integer.parseInt( formatter.format(thisDate.getTime()));
		  } catch (ParseException e1) {
				//e1.printStackTrace();
			  return 0;
		  }
		  
		  return dateInt;
    }
    
    private int getInterval(){
    	int index = rList.getSelectedIndex();
    	if(index == 0)  return BudgetItem.INTERVAL_NO_REPEAT;
    	if(index == 1)  return BudgetItem.INTERVAL_DAILY;
    	if(index == 2)  return BudgetItem.INTERVAL_WEEKLY;
    	if(index == 3)  return BudgetItem.INTERVAL_SEMI_MONTHLY;
    	if(index == 4)  return BudgetItem.INTERVAL_BI_WEEKLY;
    	if(index == 5)  return BudgetItem.INTERVAL_TRI_WEEKLY;
    	if(index == 6)  return BudgetItem.INTERVAL_MONTHLY;
    	if(index == 7)  return BudgetItem.INTERVAL_BI_MONTHLY;
    	if(index == 8)  return BudgetItem.INTERVAL_TRI_MONTHLY;
    	if(index == 9)  return BudgetItem.INTERVAL_SEMI_ANNUALLY;
    	if(index == 10) return BudgetItem.INTERVAL_ANNUALLY;

    	return BudgetItem.INTERVAL_NO_REPEAT;
    }
    
	private void setRepeatValue(){
	  rListUpdate = true;
	  rList.setSelectedIndex(0);
	  if(bi == null){
		return;  
	  }

	  if(bi.getInterval() == BudgetItem.INTERVAL_ANNUALLY){
		  rList.setSelectedIndex(10);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_SEMI_ANNUALLY){
		  rList.setSelectedIndex(9);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_TRI_MONTHLY){
		  rList.setSelectedIndex(8);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_BI_MONTHLY){
		  rList.setSelectedIndex(7);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_MONTHLY){
		  rList.setSelectedIndex(6);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_TRI_WEEKLY){
		  rList.setSelectedIndex(5);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_BI_WEEKLY){
		  rList.setSelectedIndex(4);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_SEMI_MONTHLY){
		  rList.setSelectedIndex(3);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_WEEKLY){
		  rList.setSelectedIndex(2);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_DAILY){
		  rList.setSelectedIndex(1);
	  }
	  if(bi.getInterval() == BudgetItem.INTERVAL_NO_REPEAT){
		  rList.setSelectedIndex(0);
	  }

	  rListUpdate = false;
	}
	
	
	static class ShowPopupActionListener implements ActionListener {
		private JButton component;
		private BudgetData data;
		private BudgetEditBalloon balloon;
		
		ShowPopupActionListener(BudgetEditBalloon balloon, JButton component) {
		      this.component = component;
		      this.data = balloon.getData();
		      this.balloon = balloon;
		}
		
		public synchronized void actionPerformed(ActionEvent actionEvent) {
		  int dateInt = 0;
		  String dateString = component.getText();
		  Date thisDate = new Date();
		  
		  if(dateString.length() == 0){
			  dateInt = 20120310;
			  
			  
			  thisDate   = new GregorianCalendar(data.getCurrentBudgetYear(), balloon.getBalloonCol(), 1).getTime();
		  } else {
			  SimpleDateFormat format = new SimpleDateFormat("MM/dd/yyyy");
			  try {
				thisDate = format.parse(dateString);
			} catch (ParseException e1) {
				e1.printStackTrace();
			}
			  
		  }
		  
		  SimpleDateFormat formatter = new SimpleDateFormat("yyyyMMdd");
		  dateInt = Integer.parseInt( formatter.format(thisDate.getTime()));
		  final DatePicker picker = (new UnsafeAccessor(this.data.extension.getUnprotectedContext())).getDatePicker(dateInt);
			
		  PopupFactory factory = PopupFactory.getSharedInstance();
		  int x = component.getLocationOnScreen().x;
		  int y = component.getLocationOnScreen().y;
		  
		  final Popup popup = factory.getPopup(component, picker, x, y);
		  popup.show();

		  ChangeListener hider = new ChangeListener() {
		        public void stateChanged(ChangeEvent e) {
		          popup.hide();

		          Date thisDate = BudgetDateUtil.getDateYYYYMMDD(picker.getSelectedDate());
		  		  SimpleDateFormat formatter = new SimpleDateFormat("MM/dd/yyyy");
		  		  component.setText(formatter.format(thisDate.getTime()));
		        }
		  };
		  
		    
		  ComponentListener whenHiden = new ComponentListener() {
			  public void componentHidden(ComponentEvent e) {
				  popup.hide();
			  }

			  public void componentMoved(ComponentEvent e) {

			  }

			  public void componentResized(ComponentEvent e) {
			        
			  }

			  public void componentShown(ComponentEvent e) {

			  }
		  };
		  
		  picker.setListener(hider);
		  picker.addComponentListener(whenHiden);
		  
		}
	}
	
}
