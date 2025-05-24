/*
 *  Copyright (c) 2020, Michael Bray and Hung Le.  All rights reserved.
 *  
 *  NOTE: this module contains original work by Mike Bray and Hung Le, no breach of copyright is intended and no 
 *  benefit has been gained from the use of this work
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
package com.moneydance.modules.features.securityquoteload.quotes;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

import org.apache.http.HttpStatus;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.HistoryPrice;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.Parameters;
import com.moneydance.modules.features.securityquoteload.QuotePrice;

public class GetQuoteTask extends QuoteTask<QuotePrice> {
	Parameters params = Parameters.getParameters();
  int throttleDelayMinMS;
  int throttleDelayMaxMS;

	public GetQuoteTask(String ticker, QuoteListener listener, CloseableHttpClient httpClient,String tickerType,String tid) {
		super(ticker,listener, httpClient,tickerType,tid);
    this.throttleDelayMinMS = 0;
    this.throttleDelayMaxMS = 0;
	}

  public GetQuoteTask(String ticker, QuoteListener listener, CloseableHttpClient httpClient, String tickerType, String tid, int throttleDelayMinMS, int throttleDelayMaxMS) {
    super(ticker, listener, httpClient, tickerType, tid);
    this.throttleDelayMinMS = throttleDelayMinMS;
    this.throttleDelayMaxMS = throttleDelayMaxMS;
  }

	@Override
	public QuotePrice call() throws Exception {
		QuotePrice quotePrice = null;
		CloseableHttpResponse response = null;
		if (ticker.isBlank()) {
			debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "Invalid Ticker "+rawTicker);
			sendError();
		}
			
		URI uri=null;
		try {
			uri= new URI(url.trim());
			debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "Processing  "+ticker+" URI:"+uri.toASCIIString() + "(throttle delay/sleep per call - min: " + (throttleDelayMinMS/1000.0) + " max: " + (throttleDelayMaxMS/1000.0) + ")");
      if (throttleDelayMinMS > 0) {
        try {
          if (throttleDelayMaxMS > throttleDelayMinMS) {
            TimeUnit.MILLISECONDS.sleep(ThreadLocalRandom.current().nextInt(throttleDelayMinMS, throttleDelayMaxMS+1)); // randomized delay between min and max milli-seconds
          } else {
            TimeUnit.MILLISECONDS.sleep(throttleDelayMinMS);
          }
        } catch (InterruptedException e) {
          debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "The task for ticker: '" + ticker + "' has been cancelled during its throttle / sleep... quitting this task");
          Thread.currentThread().interrupt(); // restore interrupt status
          return quotePrice;
        }
      }
			HttpGet httpGet = new HttpGet(uri);
			httpGet.addHeader("Accept-Language","en");
			//httpGet.addHeader("User-Agent","Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36");
      String ua = params.getUaParam().isEmpty() ? UserAgent.getAgent() : params.getUaParam();
      httpGet.addHeader("User-Agent", ua);

			response = httpClient.execute(httpGet);
			quotePrice=null; 
			debugInst.debug("GetQuoteTask", "call", MRBDebug.DETAILED, "Return stats for  "+ticker+" "+response.getStatusLine().getStatusCode() + " (user-agent: '" + ua + "')");
			if (response.getStatusLine().getStatusCode() == HttpStatus.SC_OK || response.getStatusLine().getStatusCode() == HttpStatus.SC_NON_AUTHORITATIVE_INFORMATION) {
				try {
					quotePrice = analyseResponse(response);
					String doneUrl ="moneydance:fmodule:" + Constants.PROGRAMNAME + ":"+Constants.LOADPRICECMD+"?"+Constants.TIDCMD+"="+tid+"&";
					if (tickerType == Constants.STOCKTYPE)
						doneUrl+=Constants.STOCKTYPE;
					else
						doneUrl+=Constants.CURRENCYTYPE;
					doneUrl += "="+ticker+"&p="+String.format("%.8f",quotePrice.getPrice());
					doneUrl += "&"+Constants.TRADEDATETYPE+"="+quotePrice.getTradeDate();
					doneUrl += "&"+Constants.TRADECURRTYPE+"="+quotePrice.getCurrency();
					if (quotePrice.getHighPrice()!= 0.0)
						doneUrl += "&"+Constants.HIGHTYPE+"="+quotePrice.getHighPrice();
					if (quotePrice.getLowPrice()!= 0.0)
						doneUrl += "&"+Constants.LOWTYPE+"="+quotePrice.getLowPrice();
					doneUrl += "&"+Constants.VOLUMETYPE+"="+quotePrice.getVolume();
					Main.context.showURL(doneUrl);
					if (!quotePrice.getHistory().isEmpty()) {
						for (HistoryPrice history : quotePrice.getHistory()) {
							doneUrl ="moneydance:fmodule:" + Constants.PROGRAMNAME + ":"+Constants.LOADHISTORYCMD+"?"+Constants.TIDCMD+"="+tid+"&";
							if (tickerType == Constants.STOCKTYPE)
								doneUrl+=Constants.STOCKTYPE;
							else
								doneUrl+=Constants.CURRENCYTYPE;
							doneUrl += "="+ticker+"&p="+String.format("%.8f",history.getPrice());
							if (history.getHighPrice()!= 0.0)
								doneUrl += "&"+Constants.HIGHTYPE+"="+history.getHighPrice();
							if (history.getLowPrice()!= 0.0)
								doneUrl += "&"+Constants.LOWTYPE+"="+history.getLowPrice();
							doneUrl += "&"+Constants.TRADEDATETYPE+"="+history.getDate();
							doneUrl += "&"+Constants.TRADECURRTYPE+"="+quotePrice.getCurrency();
							if (params.getAddVolume() && quotePrice.getVolume() > 0L)
								doneUrl += "&"+Constants.VOLUMETYPE+"="+history.getVolume();
							Main.context.showURL(doneUrl);
				
						}
					}
					listener.doneReturned(ticker);
				}
				catch (IOException e) {
					debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "error analysing reply "+e.getMessage());
					sendError();
				}
			}
			else {
				debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "error returned "+response.getStatusLine().getStatusCode() + " (user-agent: '"+ua+"')");
        if (response.getStatusLine().getStatusCode() == Constants.RATE_LIMITED) {
  				debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "RATE LIMITED - Removing from user-agents list (for this session)...");
          UserAgent.removeInvalidAgent(ua);
        }
				sendError();
			}
		} catch (URISyntaxException e) {
			debugInst.debug("getQuoteTask", "call", MRBDebug.INFO, "URI invalid "+url);
			sendError();
		}
			catch (ClientProtocolException e2) {
				debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "server returned protocol error for "+ticker);
				sendError();
			}
		catch (Exception e3) {
			debugInst.debug("getQuoteTask", "call", MRBDebug.INFO, "General Error  - "+e3.getMessage());
			e3.printStackTrace();
			sendError();
		}
		if (response != null)
			response.close();
		return quotePrice;
	}
	private void sendError() {
		String errorUrl ="moneydance:fmodule:" + Constants.PROGRAMNAME + ":"+Constants.ERRORQUOTECMD+"?"+Constants.TIDCMD+"="+tid+"&";
		if (tickerType == Constants.STOCKTYPE)
			errorUrl+=Constants.STOCKTYPE;
		else
			errorUrl+=Constants.CURRENCYTYPE;
		errorUrl += "="+ticker;
		Main.context.showURL(errorUrl);
		listener.errorReturned(ticker);

		
	}

}
