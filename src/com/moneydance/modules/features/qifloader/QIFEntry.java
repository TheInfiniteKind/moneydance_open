package com.moneydance.modules.features.qifloader;

import com.infinitekind.moneydance.model.AbstractTxn;

public class QIFEntry {
	private boolean selected;
	private int date;
	private String description;
	private String cheque="";
	private byte cleared = AbstractTxn.STATUS_UNRECONCILED;
	private Double amount;
	private String category="";
	public QIFEntry () {
		
	}
	public boolean isSelected() {
		return selected;
	}
	public void setSelected(boolean selected) {
		this.selected = selected;
	}
	public int getDate() {
		return date;
	}
	public void setDate(int date) {
		this.date = date;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public Double getAmount() {
		return amount;
	}
	public void setAmount(Double amount) {
		this.amount = amount;
	}
	public String getCheque() {
		return cheque;
	}
	public void setCheque(String cheque) {
		this.cheque = cheque;
	}
	public byte getCleared() {
		return cleared;
	}
	public void setCleared(byte cleared) {
		this.cleared = cleared;
	}
	public String getCategory() {
		return category;
	}
	public void setCategory(String category) {
		this.category = category;
	}
	
}