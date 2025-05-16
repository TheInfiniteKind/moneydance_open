/*
 * Copyright (c) 2018, Michael Bray.  All rights reserved.
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
 * 
 */
package com.moneydance.modules.features.securityquoteload;

import java.util.ArrayList;
import java.util.TreeMap;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.view.CurTable;
import com.moneydance.modules.features.securityquoteload.view.CurTableModel;
import com.moneydance.modules.features.securityquoteload.view.SecTable;
import com.moneydance.modules.features.securityquoteload.view.SecTableModel;

public class AutomaticRun extends MainPriceWindow{

		public AutomaticRun (Main mainp, int runtype)
		{
			super(mainp,runtype);
			Main.debugInst.debug("AutomaticRun", "AutomaticRun", MRBDebug.DETAILED,
					"Started");
			errorsFound = false;
			errorTickers = new ArrayList<>();
			main = mainp;
			params =Parameters.getParameters();
			/*
			 * set up internal tables
			 */
			securitiesTable = new TreeMap<> ();
			currenciesTable = new TreeMap<> ();
			volumes = new TreeMap<>();
			pseudoCurrencies = params.getPseudoCurrencies();
			/*
			 * Load base accounts and currencies
			 */
			accountSources = params.getSavedAccounts();
			loadAccounts(Main.context.getRootAccount());
			baseCurrency = Main.context.getCurrentAccountBook()
					.getCurrencies()
					.getBaseType();
			baseCurrencyID = baseCurrency.getIDString();
			if(params.getCurrency() || params.getZero()){
				loadCurrencies(Main.context.getCurrentAccountBook());
			}
			secPricesModel = new SecTableModel (params,	securitiesTable, this);
			secPricesDisplayTab = new SecTable (params,secPricesModel);
			curRatesModel = new CurTableModel(params, currenciesTable, this);
			curPricesDisplayTab = new CurTable(params, curRatesModel);
			Main.debugInst.debug("AutomaticRun", "AutomaticRun", MRBDebug.DETAILED, "get Prices");
			boolean tempProcessCurrency = false;
			boolean tempProcessSecurity = false;
			switch (runtype){
				case Constants.SECAUTORUN :
					tempProcessCurrency = false;
					tempProcessSecurity = true;
					break;
				case Constants.CURAUTORUN :
					tempProcessCurrency = true;
					tempProcessSecurity = false;
					break;
				case Constants.BOTHAUTORUN :
					tempProcessCurrency = true;
					tempProcessSecurity = true;
					break;
				case Constants.STANDALONERUN:	
					tempProcessCurrency = true;
					tempProcessSecurity = true;
					break;
			}
			Main.autoRunning=true;
			Main.secondRunRequired = false;
			if (tempProcessCurrency) {
				processCurrency=true;
				processSecurity = false;
				if (tempProcessSecurity)
					Main.secondRunRequired=true;
				getPrices();
			}
			else {
				if (tempProcessSecurity) {
					processCurrency=false;
					processSecurity = true;
					getPrices();
				}
			}

		}
		public void secondRun() {
			processCurrency=false;
			processSecurity = true;
			Main.secondRunRequired=false;
			getPrices();
		}

}
