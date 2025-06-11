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

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.infinitekind.util.DateUtil;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.QuotePrice;
import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.impl.client.CloseableHttpClient;

import javax.swing.text.DateFormatter;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.List;
import java.util.TimeZone;

public class GetMDQuote extends GetQuoteTask {

    private String mdSecURL = "https://api.marketdata.app/v1/stocks/bulkcandles/D/?symbols=";
    private String mdFundURL = "https://api.marketdata.app/v1/funds/candles/D/";
    private DateTimeFormatter dFormat = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private boolean history=false;

    private List<String> volumes;
    private List<String> closes;
    private List<String> lows;
    private List<String> highs;
    Integer lastPriceDate=0;
    String tradeCurrency;
    String fromDate;
    String toDate;

    public GetMDQuote(String ticker, String tradeCurrency, QuoteListener listener, CloseableHttpClient httpClient, String tickerType, String tid) {
        super(ticker, listener, httpClient, tickerType, tid, 0, 0, Constants.QuoteSource.MARKETDATA);
        this.tradeCurrency = tradeCurrency;
        String convTicker = ticker.replace("^", "%5E");
        if (tickerType.equals(Constants.STOCKTYPE))
            url = mdSecURL + convTicker +"&dateformat=timestamp&token="+params.getMdToken();
        debugInst.debug("GetMDQuote", "GetMDQuote", MRBDebug.DETAILED, "Executing :" + url);
        lastPriceDate = -1;
    }
    public GetMDQuote(String ticker,  Constants.MDStockType stockType, String tradeCurrency, QuoteListener listener, CloseableHttpClient httpClient, String tickerType, String tid, Integer lastPriceDate, boolean history) {
        super(ticker, listener, httpClient, tickerType, tid, 0, 0, Constants.QuoteSource.MARKETDATA);
        this.tradeCurrency = tradeCurrency;
        this.history = history;
        int  historyDateInt = DateUtil.incrementDate(Main.today,0,-(params.getAmtHistory()+1),0);
        this.lastPriceDate = (lastPriceDate == null ? 0 : lastPriceDate);
        if (this.lastPriceDate < historyDateInt) {
            this.lastPriceDate = historyDateInt;
            Main.debugInst.debug("GetMDQuote", "construct", MRBDebug.DETAILED, "History date restricted to  " + lastPriceDate);
        }

        int year = this.lastPriceDate/10000;
        int month = (this.lastPriceDate-(year*10000))/100;
        int day = this.lastPriceDate- year*10000-month*100;
        LocalDate tempDate = LocalDate.of(year,month,day);
        fromDate = tempDate.format(dFormat);
        LocalDate today = LocalDate.now();
        toDate = today.format(dFormat);
       String convTicker = ticker.replace("^", "%5E");
       if (tickerType.equals(Constants.STOCKTYPE) && stockType == Constants.MDStockType.STOCK) {
            url = mdSecURL + convTicker + "&dateformat=timestamp&from="+fromDate+"&to="+toDate+"&token=" + params.getMdToken();
        }
        if (tickerType.equals(Constants.STOCKTYPE) && stockType == Constants.MDStockType.MUTUAL) {
            url = mdFundURL + convTicker + "?from="+fromDate+"&to="+toDate+"&token=" + params.getMdToken();
        }
        debugInst.debug("GetMDQuote", "GetMDQuote", MRBDebug.DETAILED, "Executing :" + url);

    }
    @Override
    synchronized public QuotePrice analyseResponse(CloseableHttpResponse response) throws IOException {

        QuotePrice quotePrice = new QuotePrice();
        quotePrice.setTicker(ticker);
        quotePrice.setCurrency(tradeCurrency);
        HttpEntity entity = response.getEntity();
        try {
            InputStream stream = entity.getContent();
            String buffer = getJsonString(stream);
            if (Main.LOG_RAW_RESPONSES) { // only when enabled AND QL DETAILED debugging then print the raw response...
              debugInst.debug("getMDQuote", "analyseResponse", MRBDebug.DETAILED, "raw entity: '" + buffer + "'");
            }
            JsonObject nodes = JsonParser.parseString(buffer).getAsJsonObject();
            try {
                parseDoc(nodes, quotePrice);
            } catch (IOException a) {
                debugInst.debug("GetMDQuote", "analyseResponse", MRBDebug.INFO, "IOException " + a.getMessage());
                throw new IOException(a);
            }
        } catch (UnsupportedOperationException e) {
            throw new IOException(e);
        } catch (MalformedURLException e) {
            throw (new IOException(e));
        } catch (ClientProtocolException e) {
            throw (new IOException(e));
        } catch (IOException e) {
            throw (new IOException(e));
        } catch (Exception e) {
            e.printStackTrace();

        }

        return quotePrice;
    }

    private String getJsonString(InputStream stream) throws IOException {
        String result = "";
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8));
            String buffer = "";
            while ((buffer = reader.readLine()) != null) {
                result += buffer;
            }
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } finally {

                }
            }
        }
        if (result.isEmpty())
            throw new IOException("Cannot find MD price data");
        return result;
    }

    private void parseDoc(JsonObject doc, QuotePrice quotePrice) throws IOException {
        Object quoteNode = null;
        Object resultNode = null;
        String timeZoneStr = "";
        Calendar tradeDateCal;
        String tradeDateStr="";
        int tradeDateInt;
        JsonArray prices=null;
        JsonArray highs=null;
        JsonArray lows=null;
        JsonArray volumes=null;
        JsonArray timestamps=null;
        int crntLine=0;
        boolean historyAvailable=false;
        double highValue;
        double lowValue;
        long volume;
        double price;
        JsonElement itemNode = doc.get("c");
        String value;
        if (itemNode != null) {
            if (itemNode.isJsonArray()){
                 prices = itemNode.getAsJsonArray();
            }
        }
        itemNode = doc.get("t");
        if (itemNode != null) {
            if (itemNode.isJsonArray()){
                timestamps = itemNode.getAsJsonArray();
            }
        }
        itemNode = doc.get("v");
        if (itemNode != null) {
            if (itemNode.isJsonArray()){
                volumes = itemNode.getAsJsonArray();
            }
        }

        itemNode = doc.get("h");
        if (itemNode != null) {
            if (itemNode.isJsonArray()){
                highs = itemNode.getAsJsonArray();
            }
        }
        itemNode = doc.get("l");
        if (itemNode != null) {
            if (itemNode.isJsonArray()){
                lows = itemNode.getAsJsonArray();
            }
        }
        if (prices !=null && !prices.isJsonNull()){
            if (prices.size()>1) {
                historyAvailable = true;
                crntLine = prices.size()-1;
            }
            else
                crntLine = 0;
        }
        try {
            quotePrice.setPrice(prices.get(crntLine).getAsDouble());
        }
        catch (ClassCastException | IllegalStateException e){
            debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid price value ");
            quotePrice.setPrice(0.0D);
        }
        try {
            quotePrice.setLowPrice(lows.get(crntLine).getAsDouble());
        }
        catch (ClassCastException | IllegalStateException e){
            debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid low price value ");
            quotePrice.setLowPrice(0.0D);
        }
        try {
            quotePrice.setHighPrice(highs.get(crntLine).getAsDouble());
        }
        catch (ClassCastException | IllegalStateException e){
            debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid high price value ");
            quotePrice.setHighPrice(0.0D);
        }
        try {
            quotePrice.setVolume(volumes.get(crntLine).getAsLong());
        }
        catch (ClassCastException | IllegalStateException e){
            debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid volume value ");
            quotePrice.setVolume(0L);
        }
        try {
            quotePrice.setTradeDate(timestamps.get(crntLine).getAsString()+"T00:00");
        }
        catch (ClassCastException | IllegalStateException e){
            debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid volume value ");
            quotePrice.setVolume(0L);
        }
        if (!history || !params.getHistory()|crntLine==0)
            return;
        crntLine -= 1;
        boolean priceFound = false;
        while(crntLine >=0){
            lowValue=0.0;
            price=0.0;
            highValue=0.0;
            volume = 0L;
            priceFound = false;
            tradeDateInt = 0;
            try {
                    volume = volumes.get(crntLine).getAsLong();
            }
            catch (ClassCastException | IllegalStateException| IndexOutOfBoundsException e){
                debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid volume value ");
                volume=0L;
            }
            try {
                 lowValue = lows.get(crntLine).getAsDouble();
            }
            catch (ClassCastException | IllegalStateException| IndexOutOfBoundsException e){
                debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid low price value ");
                lowValue=0L;
            }
            try {
                    highValue = highs.get(crntLine).getAsDouble();
            }
            catch (ClassCastException | IllegalStateException| IndexOutOfBoundsException e){
                debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid high price value ");
                lowValue=0L;
            }
            try {
                    price = prices.get(crntLine).getAsDouble();
                    priceFound = true;
                }
            catch (ClassCastException | IllegalStateException| IndexOutOfBoundsException e){
                debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid price value ");
                price=0L;
            }
            try {
                String tradeDate = timestamps.get(crntLine).getAsString();
                tradeDateStr = tradeDate+"T00:00";
                tradeDate = tradeDate.replace("-","");
                tradeDateInt= Integer.valueOf(tradeDate);

            }
            catch (ClassCastException | IllegalStateException| IndexOutOfBoundsException e){
                debugInst.debug("GetQuoteTask", "parseDoc", MRBDebug.INFO, "Invalid tarde date value ");
                price=0L;
            }

            if (priceFound) {
                QuotePrice historyPrice = new QuotePrice();
                historyPrice.setTradeDateInt(tradeDateInt);
                historyPrice.setTradeDate(tradeDateStr);
                historyPrice.setPrice(price);
                historyPrice.setHighPrice(highValue);
                historyPrice.setLowPrice(lowValue);
                historyPrice.setVolume(volume);
                quotePrice.addHistory(historyPrice.getTradeDateInt(), historyPrice.getPrice(), historyPrice.getHighPrice(),
                        historyPrice.getLowPrice(), historyPrice.getVolume());
            }
            crntLine-=1;
        }
    }

    private Calendar getLastTrade(String regularMarketTime, String exchangeTimezoneName) throws IOException {
        Calendar lastTrade = null;
        if ((regularMarketTime != null) && (exchangeTimezoneName != null)) {
            long longValue;
            try {
                longValue = Long.valueOf(regularMarketTime);
                ZonedDateTime marketZonedDateTime = getMarketZonedDateTime(longValue, exchangeTimezoneName);
                lastTrade = GregorianCalendar.from(marketZonedDateTime);
            } catch (NumberFormatException e) {
                throw new IOException("error calculating trade date");
            }
        }
        return lastTrade;
    }

    private final ZonedDateTime getMarketZonedDateTime(long regularMarketTime, String exchangeTimezoneName) {
        long epoch = regularMarketTime;
        Instant instant = Instant.ofEpochSecond(epoch);
        TimeZone timeZone = TimeZone.getTimeZone(exchangeTimezoneName);
        ZoneId zoneId = timeZone.toZoneId();
        ZonedDateTime zoneDateTime = ZonedDateTime.ofInstant(instant, zoneId);
        return zoneDateTime;
    }

}
