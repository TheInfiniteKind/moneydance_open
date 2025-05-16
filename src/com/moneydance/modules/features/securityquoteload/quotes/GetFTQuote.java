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
import java.io.InputStream;
import java.net.MalformedURLException;
import java.text.NumberFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Date;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.impl.client.CloseableHttpClient;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.QuotePrice;
import com.moneydance.modules.features.securityquoteload.ScanDate;

public class GetFTQuote extends GetQuoteTask {
	private MRBDebug debugInst = Main.debugInst;
	private String ftSecURL = "https://markets.ft.com/data/equities/tearsheet/summary?";
	private String ftCurrURL = "https://markets.ft.com/data/currencies/tearsheet/summary?";
	public GetFTQuote(String tickerp, QuoteListener listenerp, CloseableHttpClient httpClientp,String tickerTypep,String tidp) {
		super(tickerp, listenerp, httpClientp,tickerTypep,tidp);
		if (tickerType == Constants.STOCKTYPE)
			url = ftSecURL+"s="+ticker;
		if (tickerType == Constants.CURRENCYTYPE)
			url = ftCurrURL+"s="+ticker;
	}
	@Override
	synchronized public QuotePrice analyseResponse(CloseableHttpResponse response) throws IOException {
		QuotePrice quotePrice = new QuotePrice();
		HttpEntity entity = response.getEntity();
		try {
			InputStream stream = entity.getContent();
			Document doc = Jsoup.parse(stream, "UTF-8", "http://localhost");
			try {
				parseDoc(doc, quotePrice);
			}
			catch (IOException a) {
				debugInst.debug("GetQuoteTask","analyseResponse",MRBDebug.INFO,"IOException "+a.getMessage());
				throw new IOException(a);
			}
		}
		catch (UnsupportedOperationException e) {
			throw new IOException(e);
		}
		catch (MalformedURLException e) {
			throw (new IOException (e));
		} catch (ClientProtocolException e) {
			throw (new IOException (e));
		} catch (IOException e) {
			throw (new IOException (e));
		} 

		finally {

		}		

		return quotePrice;
	}
	private void parseDoc(Document doc, QuotePrice quotePrice) throws IOException {
		String query = null;
		Element crntLoc = null;
		try {
			query = "div.mod-tearsheet-overview__header";
			crntLoc = doc.selectFirst(query);
			if (crntLoc == null) {
				throw new IOException("Cannot find " + query);
			}
			query = "h1";
			Elements items = crntLoc.select(query);
			if (items == null) {
				throw new IOException("Cannot find " + query);
			}
			Element item = items.get(0);
			if (item == null) {
				throw new IOException("Cannot find first <li>");
			}
	
			query = "div.mod-tearsheet-overview__quote";
			crntLoc = doc.selectFirst(query);
			if (crntLoc == null) {
				throw new IOException("Cannot find " + query);
			}
	
			findPrice(crntLoc,quotePrice);
			findDate(crntLoc,quotePrice);
	
			return;
		} catch (IOException e) {
			throw new IOException("Cannot parse response for symbol=" + ticker+" " + e.getMessage(),e);
		}
	}

	private void findPrice(Element topDiv, QuotePrice quotePrice) throws IOException {
		String cssQuery;
		cssQuery = "li";
		Elements items = topDiv.select(cssQuery);
		if (items == null) {
			throw new IOException("Cannot find " + cssQuery);
		}
	
		for (Element item : items) {
			// <span class="mod-ui-data-list__label">Price (ccc)</span>
			String cssQueryLabel = "span.mod-ui-data-list__label";
			Element label = item.selectFirst(cssQueryLabel);
			if (label == null) {
				throw new IOException("Cannot find " + cssQueryLabel);
			}
			String labelText = label.text();
	
			// <span class="mod-ui-data-list__value">price</span>
			String cssQueryValue = "span.mod-ui-data-list__value";
			Element value = item.selectFirst(cssQueryValue);
			if (value == null) {
				throw new IOException("Cannot find " + cssQueryValue);
			}
			String valueText = value.text();
	
			if (labelText != null) {
				labelText = labelText.trim();
				if (labelText.startsWith("Price")) {
					setPriceAndCurrency(labelText, valueText, quotePrice);
				}
			}
			if (labelText !=null)
			{
				labelText = labelText.trim();
				if (labelText.startsWith("Shares traded")) {
					setVolume(labelText, valueText, quotePrice);
				}
			}
		}
	}
		
	private void setPriceAndCurrency(String labelText, String valueText, QuotePrice quotePrice) {
		// Price (USD)
		String patternString = "\\((.*)\\)";
		Pattern pattern = Pattern.compile(patternString);
		Matcher matcher = pattern.matcher(labelText);
		String currency = null;
		while (matcher.find()) {
			if (currency != null) {
				continue;
			}
			currency = matcher.group(1);
			quotePrice.setCurrency(currency);
		}
	
		if (valueText != null) {
			valueText = valueText.trim();
			Number price = null;
			try {
				// FT price is ALWAYS in English format
				Locale locale = Locale.ENGLISH;
				NumberFormat format = NumberFormat.getInstance(locale);
				// format.setGroupingUsed(false);
				debugInst.debug("GetFTPrices","setPriceAndCurrency",MRBDebug.DETAILED,"Price found "+valueText);
				price = format.parse(valueText);
			} catch (ParseException e) {
			}
			if (price != null) {
				quotePrice.setPrice(price.doubleValue());
			}
		}
	}
	private void setVolume(String labelText, String valueText, QuotePrice quotePrice) {
		Integer multi=1;
		String number=valueText;
		if (valueText.endsWith("k")) {
			multi = 1000;
			number = valueText.substring(0,valueText.length()-1);
		}
		if (valueText.endsWith("m")) {
			multi = 1000000;
			number = valueText.substring(0,valueText.length()-1);
		}
		Double tradeVolume;
		try {
			tradeVolume = Double.parseDouble(number);
		}
		catch (NullPointerException | NumberFormatException e) {
			tradeVolume = 0.0d;
		}
		Long tradeVolumeLong = Math.round(tradeVolume * multi);
		quotePrice.setVolume(tradeVolumeLong);
	}
	private void findDate(Element topDiv, QuotePrice quotePrice) throws IOException {
		String cssQuery;
		ScanDate scanD = new ScanDate();
		ZonedDateTime date;
		cssQuery = "div.mod-disclaimer";
		SimpleDateFormat simpleFormat = new SimpleDateFormat("MMM dd yyyy");
		Elements dateElement = topDiv.select(cssQuery);
		if (dateElement == null) {
			date=ZonedDateTime.now(ZoneOffset.UTC);
		}
		else {
			String dateText = dateElement.text();
			int asof = dateText.indexOf("as of ");
			if (asof < 0) {
				date = ZonedDateTime.now(ZoneOffset.UTC);
			} else {
				asof += 6;   // length 'as of '
				String dateString = dateText.substring(asof);
	/*			String monthStr = dateString.substring(0,3);
				String dayStr = dateString.substring(4,6);
				String yearStr = dateString.substring(7,11); */
				try {
					date = scanD.parseString(dateString);
				} catch (IOException e) {
					throw new IOException("Trade Date parse error " + e.getMessage());
				}
			}
		}
		quotePrice.setTradeDate(date.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ssZ")));
	}
}
