package com.moneydance.modules.features.securityquoteload;

import java.io.Serializable;

public class AccountSourceLine implements Serializable{
	private int source;
	private String alternate;
	public AccountSourceLine(int source, String alternate) {
		this.source = source;
		this.alternate=alternate;
	}
	public int getSource() {
		return source;
	}
	public void setSource(int source) {
		this.source = source;
	}
	public String getAlternate() {
		return alternate;
	}
	public void setAlternate(String alternate) {
		this.alternate = alternate;
	}
		

}
