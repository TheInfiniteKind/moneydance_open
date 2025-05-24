package com.moneydance.modules.features.securityquoteload.quotes;

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

import javax.swing.*;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.InvocationTargetException;
import java.net.MalformedURLException;
import java.nio.charset.StandardCharsets;
import java.time.*;
import java.util.*;

public class GetAlphaQuoteHD extends GetQuoteTask{
    private String alphaSecURL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=";
    private String alphaCurURL = "https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=";
    private Integer lastPriceDate;
    private int historyDateInt;
    private String convTicker;
    private String tradeCurrency;

    public GetAlphaQuoteHD(String ticker, String tradeCurrency, QuoteListener listener, CloseableHttpClient httpClient, String tickerType, String tid,Integer lastPriceDate, int throttleDelayMinMS, int throttleDelayMaxMS) {
        super(ticker, listener, httpClient, tickerType, tid, throttleDelayMinMS, throttleDelayMaxMS);
        this.tradeCurrency = tradeCurrency;
        int  historyDateInt = DateUtil.incrementDate(Main.today,0,-(params.getAmtHistory()+1),0);
        this.lastPriceDate = (lastPriceDate == null ? 0 : lastPriceDate);
        if (this.lastPriceDate < historyDateInt) {
            this.lastPriceDate = historyDateInt;
            Main.debugInst.debug("GetAlphaQuote", "construct", MRBDebug.DETAILED, "History date restricted to  " + lastPriceDate);
        }
        convTicker = ticker.replace("^", "%5E");
        if (tickerType.equals(Constants.STOCKTYPE))
            url = alphaSecURL + convTicker + "&apikey="+params.getAlphaAPIKey();
        if (tickerType.equals(Constants.CURRENCYTYPE)) {
            String baseCur = convTicker.substring(convTicker.indexOf("/")+1);
            String fromCur = convTicker.substring(0,convTicker.indexOf("/"));
            url = alphaCurURL + fromCur+"&to_symbol="+baseCur+"&apikey="+params.getAlphaAPIKey();
        }
        Main.debugInst.debug("GetAlphaQuote", "GetAlphaQuote", MRBDebug.DETAILED, "Executing :" + url);

    }
    @Override
    public QuotePrice analyseResponse(CloseableHttpResponse response) throws IOException {
        QuotePrice quotePrice = new QuotePrice();
        quotePrice.setTicker(ticker);
        quotePrice.setCurrency(tradeCurrency);
        HttpEntity entity = response.getEntity();
        try {
            InputStream stream = entity.getContent();
            String buffer = getJsonString(stream);
            JsonObject nodes = JsonParser.parseString(buffer).getAsJsonObject();
            try {
                parseDoc(nodes, quotePrice);
            }
            catch (IOException a) {
                Main.debugInst.debug("GetAlphaQuote","analyseResponse", MRBDebug.INFO,"IOException "+a.getMessage());
                throw new IOException(a);
            }
        }
        catch (UnsupportedOperationException e) {
            throw new IOException(e);
        }
        catch (MalformedURLException e) {
            Main.debugInst.debug("GetAlphaQuote","analyseResponse", MRBDebug.INFO,"MalformedURLException "+e.getMessage());
            throw (new IOException (e));
        } catch (ClientProtocolException e) {
            Main.debugInst.debug("GetAlphaQuote","analyseResponse", MRBDebug.INFO,"ClientProtocolException "+e.getMessage());
            throw (new IOException (e));
        } catch (IOException e) {
            Main.debugInst.debug("GetAlphaQuote","analyseResponse", MRBDebug.INFO,"IOException "+e.getMessage());
            throw (new IOException (e));
        } catch (Exception e){
            Main.debugInst.debug("GetAlphaQuote","analyseResponse", MRBDebug.INFO,"Exception "+e.getMessage());
            throw (new IOException (e));
        }

        finally {

        }

        return quotePrice;
    }
    private String getJsonString(InputStream stream) throws IOException {
        StringBuilder result = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            String buffer;
            while ((buffer = reader.readLine()) != null) {
                result.append(buffer);
            }
        }
        if (result.toString().isEmpty())
            throw new IOException("Cannot find Alpha price data");
        return result.toString();
    }

    private void parseDoc(JsonObject doc, QuotePrice quotePrice) throws IOException{
        Set<Map.Entry<String, JsonElement>> entrySet;
        Set<Map.Entry<String, JsonElement>> members;
        JsonElement quoteNode = null;
        JsonElement resultNode = null;
        JsonObject values;
        boolean priceFound = false;
        String timeZoneStr = "";
        Calendar tradeDateCal;
        String tradeDateStr = "";
        double highValue;
        double lowValue;
        long volume;
        double price;
        quoteNode = doc.get("Information");
        if (quoteNode!=null){
            String message = quoteNode.getAsString();
            if (!Main.alphaVantageLimitReached) {
                Main.alphaVantageLimitReached = true;
                try {
                    SwingUtilities.invokeAndWait(new Runnable() {

                        @Override
                        public void run() {
                            JOptionPane.showMessageDialog(null, "Alpha Vantage returned: " + message);
                        }
                    });
                } catch (InterruptedException | InvocationTargetException e) {
                    throw new IOException("Alpha Vantage error");
                }
            }
            throw new IOException("Alpha Vantage error");
        }
        quoteNode = doc.get("Meta Data");
        if (quoteNode==null || quoteNode.isJsonNull())
            throw new IOException("Cannot parse response for " + ticker);
        entrySet = ((JsonObject)quoteNode).entrySet();
        for (Map.Entry<String, JsonElement>entry:entrySet){
            String key = entry.getKey();
            if (key.substring(0,2).equals("5."))
                timeZoneStr = entry.getValue().getAsString();
        }
        if (tickerType.equals(Constants.STOCKTYPE))
            quoteNode = doc.get("Time Series (Daily)");
        else
            quoteNode = doc.get("Time Series FX (Daily)");
        if (quoteNode == null || !(quoteNode instanceof JsonObject))
            throw new IOException("Cannot parse response for " + ticker);
        entrySet = ((JsonObject)quoteNode).entrySet();

        boolean isValue;

        for (Map.Entry<String, JsonElement> entry:entrySet){
            String key = entry.getKey();
            values= entry.getValue().getAsJsonObject();
            members = values.entrySet();
            int date = getIntDate(key);
            if (!priceFound) {
                fillValues(members, quotePrice);
                quotePrice.setTradeDateInt(date);
                quotePrice.setTradeDate(date+"T00:00");
                quotePrice.setTicker(ticker);
                quotePrice.setCurrency(tradeCurrency);
                priceFound = true;
            }
            else {
                if (date < lastPriceDate || !params.getHistory())
                    return;
                QuotePrice historyPrice = new QuotePrice();
                historyPrice.setTicker(ticker);
                historyPrice.setCurrency(tradeCurrency);
                historyPrice.setTradeDateInt(date);
                historyPrice.setTradeDate(date+"T00:00");
                fillValues(members, historyPrice);
                quotePrice.addHistory(historyPrice.getTradeDateInt(), historyPrice.getPrice(), historyPrice.getHighPrice(),
                        historyPrice.getLowPrice(), historyPrice.getVolume());
            }
        }

    }
    private int getIntDate(String dateStr){
        Integer year;
        Integer month;
        Integer day;
        if (dateStr.length() <10)
            return 0;
        try {
            year = Integer.parseUnsignedInt(dateStr.substring(0, 4));
            month = Integer.parseUnsignedInt(dateStr.substring(5, 7));
            day = Integer.parseUnsignedInt(dateStr.substring(8));
        } catch (NumberFormatException e){ return 0;}
        return year*10000+month*100+day;
    }
    private void fillValues(Set<Map.Entry<String, JsonElement>> members, QuotePrice quotePrice){
        for (Map.Entry<String, JsonElement> entry : members){
            String test = entry.getKey().substring(0,1);
            switch (entry.getKey().substring(0,2)){
                case "2." -> {
                    quotePrice.setHighPrice(entry.getValue().getAsDouble());
                }
                case "3." -> {
                    quotePrice.setLowPrice(entry.getValue().getAsDouble());

                }
                case "4." -> {
                    quotePrice.setPrice(entry.getValue().getAsDouble());
                }
                case "5." -> {
                    quotePrice.setVolume(entry.getValue().getAsLong());
                }
            }
        }
    }
}
