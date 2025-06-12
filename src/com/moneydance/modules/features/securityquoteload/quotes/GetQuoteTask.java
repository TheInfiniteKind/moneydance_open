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
import java.util.Arrays;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

import org.apache.http.HttpStatus;
import org.apache.http.StatusLine;
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
  Constants.QuoteSource quoteSource;

	public GetQuoteTask(String ticker, QuoteListener listener, CloseableHttpClient httpClient,String tickerType,String tid) {
		super(ticker,listener, httpClient,tickerType,tid);
    this.throttleDelayMinMS = 0;
    this.throttleDelayMaxMS = 0;
    this.quoteSource = null;
	}

  public GetQuoteTask(String ticker, QuoteListener listener, CloseableHttpClient httpClient, String tickerType, String tid, int throttleDelayMinMS, int throttleDelayMaxMS, Constants.QuoteSource quoteSource) {
    super(ticker, listener, httpClient, tickerType, tid);
    this.throttleDelayMinMS = throttleDelayMinMS;
    this.throttleDelayMaxMS = throttleDelayMaxMS;
    this.quoteSource = quoteSource;
  }

	@Override
	public QuotePrice call() throws Exception {

    if (quoteSource == null) {
      debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "LOGIC ERROR: quoteSource cannot be null");
      sendError();
    }

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

      String ua;
      if (!params.getUaParam().isEmpty()) {
        // if user specified a fixed user agent then always use that
        ua = params.getUaParam();
      } else {
        if (quoteSource == null) {
          // should never happen, so just use a single/fixed default common user agent
          ua = UserAgent.getDefaultCommonUserAgent();
        } else {
          // obtain a user agent that's 'friendly' to the source server...
          ua = switch (quoteSource) {
            case FT, FTHD -> UserAgent.getRandomCommonUserAgent();
            case YAHOO, YAHOOHD -> UserAgent.getTimeBasedUserAgent();
            default -> UserAgent.getDefaultCommonUserAgent();
          };
        }
      }

      if (quoteSource == Constants.QuoteSource.MARKETDATA || quoteSource == Constants.QuoteSource.MARKETDATAHD || quoteSource == Constants.QuoteSource.MARKETDATAMU) {
        httpGet.addHeader("Accept", "application/json");
        httpGet.addHeader("Authorization", "Bearer " + params.getMdToken()); // putting the token here hides it from most logs...
        ua = "n/a";
      } else if (quoteSource == Constants.QuoteSource.ALPHAVAN) {
        // Alpha Vantage seems to require no headers...
        httpGet.addHeader("Accept", "application/json");
        ua = "n/a";
      } else {
  			httpGet.addHeader("Accept-Language","en");
        httpGet.addHeader("User-Agent", ua);
      }

      if (debugInst.getDebugLevelType() == MRBDebug.DebugLevel.DEVELOPER) {  // we wrap this inside the if in the absence of a lazy-like feature
        debugInst.debug("GetQuoteTask", "call", MRBDebug.DebugLevel.DEVELOPER, ">>> sending headers for: " + ticker + " " + Arrays.toString(httpGet.getAllHeaders()));
      }

			response = httpClient.execute(httpGet);
      StatusLine statusLine = response.getStatusLine();
      int statusCode = statusLine.getStatusCode();
      String statusReason = statusLine.getReasonPhrase();
			debugInst.debug("GetQuoteTask", "call", MRBDebug.DebugLevel.DETAILED, "Return stats for: " + ticker + " statusCode: " + statusCode + " reason: '" + statusReason + "' (source: '" + quoteSource + "' user-agent: '" + ua + "')");

      if (debugInst.getDebugLevelType() == MRBDebug.DebugLevel.DEVELOPER) {  // we wrap this inside the if in the absence of a lazy-like feature
  			debugInst.debug("GetQuoteTask", "call", MRBDebug.DebugLevel.DEVELOPER, "<<< returned headers for: " + ticker + " " + Arrays.toString(response.getAllHeaders()));
      }

			if (statusCode == HttpStatus.SC_OK || statusCode == HttpStatus.SC_NON_AUTHORITATIVE_INFORMATION) {
				try {
					quotePrice = analyseResponse(response);
					String doneUrl ="moneydance:fmodule:" + Constants.PROGRAMNAME + ":"+Constants.LOADPRICECMD+"?"+Constants.TIDCMD+"="+tid+"&";
          if (tickerType.equalsIgnoreCase(Constants.STOCKTYPE))
            doneUrl += Constants.STOCKTYPE;
          else
            doneUrl += Constants.CURRENCYTYPE;
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
							if (tickerType.equalsIgnoreCase(Constants.STOCKTYPE))
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
					debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "error analysing reply: " + e.getMessage());
					sendError();
				}
			}
			else {
				debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "error code: " + statusCode + " reason: '" + statusReason + "' (source: '" + quoteSource + "' user-agent: '"+ua+"')");
        if (statusCode == Constants.RATE_LIMITED) {
  				debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "RATE LIMITED - Removing from user-agents list (for this session)...");
          UserAgent.removeInvalidUserAgent(ua);  // only really has any effect when using random/rotating user agents...
        }
				sendError();
			}
		} catch (URISyntaxException e) {
			debugInst.debug("getQuoteTask", "call", MRBDebug.INFO, "URI invalid: " + url);
			sendError();
		}
			catch (ClientProtocolException e2) {
				debugInst.debug("GetQuoteTask", "call", MRBDebug.INFO, "server returned protocol error for: " + ticker);
				sendError();
			}
		catch (Exception e3) {
			debugInst.debug("getQuoteTask", "call", MRBDebug.INFO, "General Error: " + e3.getMessage());
			e3.printStackTrace();
			sendError();
		}
		if (response != null)
			response.close();
		return quotePrice;
	}
	private void sendError() {
		String errorUrl ="moneydance:fmodule:" + Constants.PROGRAMNAME + ":"+Constants.ERRORQUOTECMD+"?"+Constants.TIDCMD+"="+tid+"&";
		if (tickerType.equalsIgnoreCase(Constants.STOCKTYPE))
			errorUrl+=Constants.STOCKTYPE;
		else
			errorUrl+=Constants.CURRENCYTYPE;
		errorUrl += "="+ticker;
		Main.context.showURL(errorUrl);
		listener.errorReturned(ticker);

		
	}

}
