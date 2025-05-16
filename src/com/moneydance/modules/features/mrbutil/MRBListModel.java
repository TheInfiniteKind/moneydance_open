/*
 * Copyright (c) 2014, Michael Bray. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */ 
package com.moneydance.modules.features.mrbutil;


import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;

import javax.swing.DefaultListModel;

import com.infinitekind.moneydance.model.Account.AccountType;

public class MRBListModel extends DefaultListModel<String> {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private List<MRBMyEntry> lines;
	private SortedMap<String,MRBListItem> accounts;
	private int type;
	private AccountType [] acctType;
	private String [] acctTypeCodes;
	private String [] acctTypeNames;



	public MRBListModel (SortedMap<String,MRBListItem> mapAccountsp, int iTypep){
		super();
			accounts = mapAccountsp;
			type = iTypep;
			lines = new ArrayList<MRBMyEntry>();
			acctType = AccountType.values();
			acctTypeCodes = new String[acctType.length];
			acctTypeNames = new String[acctType.length];
			for (int i=0; i< acctType.length;i++) {
				acctTypeCodes[i] = "acct_type"+acctType[i].code()+"s";
				acctTypeNames[i] = acctTypeCodes[i].toString();
			}
			update(accounts);
	}
	@Override
	public int getSize() {
		return lines.size();
	}

	
	@Override
	public String getElementAt(int index) {
		if (lines.get(index).getValue() == null){
			return lines.get(index).getKey();
		}
		return "   "+lines.get(index).getKey();
	}
	public MRBMyEntry getEntry(int index){
		return lines.get(index);
	}
	
	public void add(String strName,MRBListItem liData) {
		addElement(strName);
		lines.add(new MRBMyEntry(strName,liData));
	}
	
	public void update(SortedMap<String,MRBListItem> mapAccountsp){
		accounts = mapAccountsp;
		removeAllElements();
		lines.clear();
		String strLastType = "";
		for (String strKey : accounts.keySet()) {
			MRBListItem liTemp = accounts.get(strKey);
			String strType = getATName(liTemp.getType());
			if (liTemp.isSelected()  && type == MRBConstants.SPT_SELECT){
				if (!strType.equals(strLastType)) {
					add(strType,null);
					strLastType = strType;
				}
				add(liTemp.getName(),liTemp);
			}
			else {
				if (!liTemp.isSelected()  && type == MRBConstants.SPT_MISSING) {
					if (!strType.equals(strLastType)) {
						add(strType,null);
						strLastType = strType;
					}
					add(liTemp.getName(),liTemp);
				}

			}
		}
		this.fireContentsChanged(this, 0, this.size()-1);
	}
	 private String getATName (AccountType atLookup){
		 for (int i=0;i<acctType.length;i++){
			 if (acctType[i].equals(atLookup)){
				 return acctTypeNames[i];
			 }
		 }
		 return "Not Found";
	 }

}


