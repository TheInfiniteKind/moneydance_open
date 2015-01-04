/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import javax.swing.JTable;

public class BudgetPopupListener extends MouseAdapter {
	 private BudgetPopup popupMenu;
	 
	 BudgetPopupListener(BudgetPopup popupMenu){
		 this.popupMenu  = popupMenu;
	 }
	 
	 public void mouseClicked(MouseEvent e) {
		 Object source = e.getSource();

		 if(source instanceof JTable){
			 if(e.getButton() == MouseEvent.BUTTON1){

			 }
		 }
	 }
	 
	 public void mousePressed(MouseEvent e) {
		 if (e.isPopupTrigger()) {
			 showPopup(e);
         } else {
        	 Object source = e.getSource();
        	 
        	 BudgetTable table = (BudgetTable) source;
    		 int row = table.rowAtPoint( e.getPoint() );
        	 int col = table.columnAtPoint( e.getPoint() );
        	
        	 if(table.isBalloonVisible() ){
        		 //if(row == table.getBalloonRow() && col == table.getBalloonCol()){
        			 table.hideBalloon();
        		 //} else {
        		 //	 showBalloon(table, row, col);
        		 //}
        	 } else {
        		 showBalloon(table, row, col);
        	 }
        	 table.hideEditBalloon();
         }
     }

     public void mouseReleased(MouseEvent e) {
    	 if (e.isPopupTrigger()) {
			 showPopup(e);
         }
     }

     private void showBalloon(BudgetTable table, int row, int col) {
    	 if(row == -1 || col == -1) return;
    	 table.setBallonCell(row, col);
     }
     
     private void showPopup(MouseEvent e) {
    	 
    	Object source = e.getSource();
    	
    	if(source instanceof BudgetTable){
    		BudgetTable table = (BudgetTable) source;
    		int row = table.rowAtPoint( e.getPoint() );
        	int col = table.columnAtPoint( e.getPoint() );
        	
        	table.hideBalloon();
        	table.hideEditBalloon();
        	        	
        	if(row == -1 || col == -1) return;
        	
        	table.setEditCell(row, col);
        	popupMenu.setRowCol(table, row, col);        	        
        	
        	if(e.getButton() == MouseEvent.BUTTON2){
            	//Middle MB
            	if(e.getID() == MouseEvent.MOUSE_PRESSED){
            		popupMenu.setRowCol(table, row, col);
            	}
            	if(e.getID() == MouseEvent.MOUSE_RELEASED){
            		popupMenu.setEndDate(col);
            	}
            }
        	
    	} else {
    		popupMenu.setRowCol(null, -1, -1);
    	}
    	
    	
        if (e.isPopupTrigger()) {  
            popupMenu.showMenu(e.getComponent(), e.getX(), e.getY());
        }
        
     }
}
