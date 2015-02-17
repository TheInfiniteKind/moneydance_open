/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;

public class BudgetTable extends JTable {
	private static final long serialVersionUID = 1L;
	private boolean editableFlag            = true;
	private BudgetDetailBalloon balloonTip  = null;
	private BudgetEditBalloon   balloonEdit = null;
	private BudgetData data;
	private BudgetWindow main;

	public boolean getScrollableTracksViewportHeight() { 
        return getPreferredSize().height < getParent().getHeight(); 
    } 
	
	BudgetTable(BudgetWindow main, DefaultTableModel tableModel, BudgetData data){
		super(tableModel);
		this.main = main;
		this.data = data;
	}
	
	public void refresh(){
		main.refresh();
	}
	
	public void initBalloon(){
		this.balloonTip  = new BudgetDetailBalloon(this, data);
		this.balloonEdit = new BudgetEditBalloon(this, data);
	}
	
	public void setBallonCell(int row, int col){
		if(balloonTip == null) return;
		
		this.repaint();
		balloonTip.setPosition(row, col);
		if(isCellEditable(row, col)){
			balloonTip.setVisible(true);
		} else {
			hideBalloon();
		}
	}
	
	public int getBalloonRow(){
		if(balloonTip == null) return -1;
		return balloonTip.getBalloonRow();
	}
	
	public int getBalloonCol(){
		if(balloonTip == null) return -1;
		return balloonTip.getBalloonCol();
	}
	
	public void showEditBalloon(){
		if(balloonEdit == null) return;
		balloonEdit.setVisible(true);
	}
	
	public void hideEditBalloon(){
		if(balloonEdit == null) return;
		balloonEdit.setVisible(false);
	}
	
	public void hideBalloon(){
		if(balloonTip == null) return;
		balloonTip.setVisible(false);
	}
	
	public boolean isBalloonVisible(){
		if(balloonTip == null) return false;
		return balloonTip.isVisible();
	}

	public boolean isCellEditable(){
		return isCellEditable(balloonTip.getBalloonRow(), balloonTip.getBalloonRow());
	}
	
    public boolean isCellEditable(int rowIndex, int colIndex) {
      if(editableFlag){
	      if(colIndex == 0 || colIndex > 12) return false;
	      if(rowIndex == this.getRowCount() - 1) return false;
      }
      return editableFlag;   //Disallow the editing of any cell
    }
    
    public void setEditable(boolean editFlag){
  	  editableFlag = editFlag;
    }
    
}
