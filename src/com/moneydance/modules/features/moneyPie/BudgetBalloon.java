package com.moneydance.modules.features.moneyPie;

import java.awt.Color;
import javax.swing.JLabel;

import net.java.balloontip.TablecellBalloonTip;
import net.java.balloontip.positioners.BasicBalloonTipPositioner;
import net.java.balloontip.positioners.LeftAbovePositioner;
import net.java.balloontip.styles.MinimalBalloonStyle;
import net.java.balloontip.styles.ModernBalloonStyle;

@SuppressWarnings("serial")
public class BudgetBalloon extends TablecellBalloonTip {
	
	private BudgetData data;
	private BudgetTable table;
	private int balloonRow;
	private int balloonCol;
	
	public BudgetData getData() {
		return data;
	}

	public void setData(BudgetData data) {
		this.data = data;
	}

	public BudgetTable getTable() {
		return table;
	}

	public void setTable(BudgetTable table) {
		this.table = table;
	}

	public void setBalloonRow(int balloonRow) {
		this.balloonRow = balloonRow;
	}

	public void setBalloonCol(int balloonCol) {
		this.balloonCol = balloonCol;
	}
	
	public int getBalloonRow() {
		return balloonRow;
	}

	public int getBalloonCol() {
		return balloonCol;
	}

	BudgetBalloon(BudgetTable table, BudgetData data){
		
		super(table, 
				new JLabel(""), 3, 6,
				new MinimalBalloonStyle(Color.WHITE, 8), 
				new LeftAbovePositioner(15, 10),
				null);
		
		((BasicBalloonTipPositioner)this.getPositioner()).setAttachLocation(1.5f, 0.0f);

		this.data = data;
		this.table = table;
		
		this.setBallonStyle();
	}
	
    public void setBalloonContent(){
		
	}

	private void setBallonStyle(){
		Color fillColorTop    = new Color(235,235,235);
		Color fillColorBot    = new Color(150,150,150);
		Color borderColor     = Color.BLACK;
		
		ModernBalloonStyle style = new ModernBalloonStyle(10, 10, 
			                                              fillColorTop, 
			                                              fillColorBot, 
				                                          borderColor);
		style.setBorderThickness(1);
		style.enableAntiAliasing(true);
		this.setStyle(style);
		
		this.setPadding(5);
		this.setCloseButton(this.getDefaultCloseButton(),false, false);
		this.setVisible(false);
		
	}
	
	public void setPosition(int row, int col){
		this.setCellPosition(row, col);
		this.balloonRow = row;
		this.balloonCol = col;
		
		if(row == -1 || col == -1) return;
		
		if(table.isCellEditable(row, col)){
			this.setBalloonContent();
		}
		
	}
	
}
