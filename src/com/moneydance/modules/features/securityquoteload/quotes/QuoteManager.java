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
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import com.moneydance.modules.features.securityquoteload.Parameters;
import org.apache.http.NameValuePair;
import org.apache.http.client.config.CookieSpecs;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.utils.URLEncodedUtils;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBEDTInvoke;
import com.moneydance.modules.features.securityquoteload.Constants;
import com.moneydance.modules.features.securityquoteload.Main;
import com.moneydance.modules.features.securityquoteload.QuotePrice;

public class QuoteManager implements QuoteListener {
    private Charset charSet = Charset.forName("UTF-8");
    private MRBDebug debugInst = Main.debugInst;
    private String source;
    private String tid;
    private List<String> stocks;
    private SortedMap<String, Integer> lastPriceDate;
    private SortedMap<String, String> tradeCurrencies;
    private List<String> currencies;
    private ExecutorService threadPool;
    private CloseableHttpClient httpClient;
    private int totalQuotes = 0;
    private int successful = 0;
    private int failed = 0;
    private boolean throttleRequired;
  	private Parameters params = Parameters.getParameters();

    public void getQuotes(String request) {
        stocks = new ArrayList<String>();
        lastPriceDate = new TreeMap<>();
        tradeCurrencies = new TreeMap();
        currencies = new ArrayList<String>();
        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.INFO, "URI " + request);
        URI uri = null;
        try {
            uri = new URI(request);
        } catch (URISyntaxException e) {
            debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, "URI invalid " + request);
            e.printStackTrace();
            return;
        }
        List<NameValuePair> results = URLEncodedUtils.parse(uri, charSet);
        source = "";
        String ticker = "";
        for (NameValuePair item : results) {
            switch (item.getName()) {
                case Constants.SOURCETYPE:
                    source = item.getValue();
                    break;
                case Constants.TIDCMD:
                    tid = item.getValue();
                    break;
                case Constants.STOCKTYPE:
                    ticker = item.getValue();
                    stocks.add(item.getValue());
                    break;
                case Constants.CURRENCYTYPE:
                    ticker = item.getValue();
                    currencies.add(item.getValue());
                    break;
                case Constants.LASTPRICEDATETYPE:
                    lastPriceDate.put(ticker, Integer.valueOf(item.getValue()));
                    break;
                case Constants.TRADECURRTYPE:
                    tradeCurrencies.put(ticker,item.getValue());
            }
        }
        httpClient = HttpClients.custom()
                .setDefaultRequestConfig(RequestConfig.custom()
                        .setCookieSpec(CookieSpecs.STANDARD).build())
                .build();
        List<GetQuoteTask> tasks = new ArrayList<GetQuoteTask>();
        switch (source) {
            case Constants.SOURCEFT -> {
                for (String stock : stocks) {
                    GetQuoteTask task = new GetFTQuote(stock, this, httpClient, Constants.STOCKTYPE, tid);
                    tasks.add(task);
                    totalQuotes++;
                }
                for (String currency : currencies) {
                    GetQuoteTask task = new GetFTQuote(currency, this, httpClient, Constants.CURRENCYTYPE, tid);
                    tasks.add(task);
                    totalQuotes++;
                }
                List<Future<QuotePrice>> futures = null;
                Long timeout;
                if (tasks.size() < 100)
                    timeout = 180L;
                else if (tasks.size() > 99 && tasks.size() < 200)
                    timeout = 360L;
                else
                    timeout = 480L;
                try {
                    threadPool = Executors.newFixedThreadPool(4);
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "FT Tasks invoking " + tasks.size() + " queries - Currencies: " + currencies.size() + " Securities: " + stocks.size() + " Overall thread-pool timeout: " + timeout + " seconds (with 4 pools)");
                    futures = threadPool.invokeAll(tasks, timeout, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.INFO, e.getMessage());
                }

                if (futures == null) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Failed to invokeAll");
                    return;
                }
                for (Future<QuotePrice> future : futures) {
                    if (future.isCancelled()) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "One of the tasks has timeout.");
                        continue;
                    }
                    try {
                        future.get();
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, "Task completed");
                    } catch (InterruptedException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } catch (ExecutionException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } finally {
                    }
                }
                String doneUrl = "moneydance:fmodule:" + Constants.PROGRAMNAME + ":" + Constants.DONEQUOTECMD + "?" + Constants.TIDCMD + "=" + tid;
                doneUrl += "&" + Constants.TOTALTYPE + "=" + totalQuotes;
                doneUrl += "&" + Constants.OKTYPE + "=" + successful;
                doneUrl += "&" + Constants.ERRTYPE + "=" + failed;
                MRBEDTInvoke.showURL(Main.context, doneUrl);

            }
            case Constants.SOURCEFTHIST -> {
                for (String stock : stocks) {
                    GetQuoteTask task = new GetFTHDQuote(stock, this, httpClient, Constants.STOCKTYPE, tid, lastPriceDate.get(stock));
                    tasks.add(task);
                    totalQuotes++;
                }
                for (String currency : currencies) {
                    GetQuoteTask task = new GetFTHDQuote(currency, this, httpClient, Constants.CURRENCYTYPE, tid, null);
                    tasks.add(task);
                    totalQuotes++;
                }
                /*
                 *  invoke get quotes
                 *
                 *  Timeout set depending on number of quotes:
                 *     < 100 set to 180 secs
                 *     >99 <200 set to 360 secs
                 *     >300 set to 480 secs
                 */
                List<Future<QuotePrice>> futures = null;
                Long timeout;
                if (tasks.size() < 100)
                    timeout = 180L;
                else if (tasks.size() > 99 && tasks.size() < 200)
                    timeout = 360L;
                else
                    timeout = 480L;
                try {
                    threadPool = Executors.newFixedThreadPool(4);
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "FTHD Tasks invoking " + tasks.size() + " queries - Currencies: " + currencies.size() + " Securities: " + stocks.size() + " Overall thread-pool timeout: " + timeout + " seconds (with 4 pools)");
                    futures = threadPool.invokeAll(tasks, timeout, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.INFO, e.getMessage());
                }

                if (futures == null) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "FT History Failed to invokeAll");
                    return;
                }
                for (Future<QuotePrice> future : futures) {
                    if (future.isCancelled()) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "FT History One of the tasks has timedout.");
                        continue;
                    }
                    try {
                        future.get();
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, "FT History task completed");
                    } catch (InterruptedException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } catch (ExecutionException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } finally {
                    }
                }
                String doneUrl = "moneydance:fmodule:" + Constants.PROGRAMNAME + ":" + Constants.DONEQUOTECMD + "?" + Constants.TIDCMD + "=" + tid;
                doneUrl += "&" + Constants.TOTALTYPE + "=" + totalQuotes;
                doneUrl += "&" + Constants.OKTYPE + "=" + successful;
                doneUrl += "&" + Constants.ERRTYPE + "=" + failed;
                MRBEDTInvoke.showURL(Main.context, doneUrl);
            }
            case Constants.SOURCEYAHOO -> {
                Long timeout;
                throttleRequired = Main.THROTTLE_YAHOO;
                if (throttleRequired)
                  Main.extension.setThrottleMessage();
                else
                  Main.extension.unsetThrottleMessage();
                int minThrottleMS = (throttleRequired) ? 1000 : 0;
                int maxThrottleMS = (throttleRequired) ? 2000 : 0;

                // overall timeout for the thread-pool invokeAll() is seconds...
                timeout = Math.max(180, (long) ((stocks.size() + currencies.size()) * (throttleRequired ? 3.5 : 0.25)));

                boolean onFirst = true;
                for (String stock : stocks) {
                    GetQuoteTask task = new GetYahooQuote(stock, this, httpClient, Constants.STOCKTYPE, tid, (onFirst) ? 0 : minThrottleMS, (onFirst) ? 0 : maxThrottleMS);
                    tasks.add(task);
                    totalQuotes++;
                    onFirst = false;
                }
                for (String currency : currencies) {
                    GetQuoteTask task = new GetYahooQuote(currency, this, httpClient, Constants.CURRENCYTYPE, tid, (onFirst) ? 0 : minThrottleMS, (onFirst) ? 0 : maxThrottleMS);
                    tasks.add(task);
                    totalQuotes++;
                    onFirst = false;
                }
                List<Future<QuotePrice>> futures = null;

                try {
                  threadPool = Executors.newFixedThreadPool(1);
                  debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Yahoo Tasks invoking " + tasks.size() + " queries - Currencies: " + currencies.size() + " Securities: " + stocks.size() + " Overall thread-pool timeout: " + timeout + " seconds (with 1 pool)");
                  futures = threadPool.invokeAll(tasks, timeout, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.INFO, e.getMessage());
                }

                if (futures == null) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Yahoo Failed to invokeAll");
                    return;
                }
                for (Future<QuotePrice> future : futures) {
                    if (future.isCancelled()) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Yahoo One of the tasks has timeout.");
                        continue;
                    }
                    try {
                        future.get();
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Yahoo task completed");
                    } catch (InterruptedException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } catch (ExecutionException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } finally {
                    }
                }
                String doneUrl = "moneydance:fmodule:" + Constants.PROGRAMNAME + ":" + Constants.DONEQUOTECMD + "?" + Constants.TIDCMD + "=" + tid;
                doneUrl += "&" + Constants.TOTALTYPE + "=" + totalQuotes;
                doneUrl += "&" + Constants.OKTYPE + "=" + successful;
                doneUrl += "&" + Constants.ERRTYPE + "=" + failed;
                MRBEDTInvoke.showURL(Main.context, doneUrl);
            }
            case Constants.SOURCEYAHOOHIST -> {
                Long timeout;
                throttleRequired = Main.THROTTLE_YAHOO;
                if (throttleRequired)
                  Main.extension.setThrottleMessage();
                else
                  Main.extension.unsetThrottleMessage();
                int minThrottleMS = (throttleRequired) ? 1000 : 0;
                int maxThrottleMS = (throttleRequired) ? 2000 : 0;

                // overall timeout for the thread-pool invokeAll() is seconds...
                timeout = Math.max(180, (long) ((stocks.size() + currencies.size()) * (throttleRequired ? 3.5 : 0.25)));

                boolean onFirst = true;
                for (String stock : stocks) {
                    GetQuoteTask task = new GetYahooQuote(stock, this, httpClient, Constants.STOCKTYPE, tid, lastPriceDate.get(stock), true, (onFirst) ? 0 : minThrottleMS, (onFirst) ? 0 : maxThrottleMS);
                    tasks.add(task);
                    totalQuotes++;
                    onFirst = false;
                }
                for (String currency : currencies) {
                    GetQuoteTask task = new GetYahooQuote(currency, this, httpClient, Constants.CURRENCYTYPE, tid, lastPriceDate.get(currency),true, (onFirst) ? 0 : minThrottleMS, (onFirst) ? 0 : maxThrottleMS);
                    tasks.add(task);
                    totalQuotes++;
                    onFirst = false;
                }
                List<Future<QuotePrice>> futures = null;
                try {
                  threadPool = Executors.newFixedThreadPool(1);
                  debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "YahooHD Tasks invoking " + tasks.size() + " queries - Currencies: " + currencies.size() + " Securities: " + stocks.size() + " Overall thread-pool timeout: " + timeout + " seconds (with 1 pool)");
                  futures = threadPool.invokeAll(tasks, timeout, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.INFO, e.getMessage());
                }

                if (futures == null) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Yahoo History Failed to invokeAll");
                    return;
                }
                for (Future<QuotePrice> future : futures) {
                    if (future.isCancelled()) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Yahoo History One of the tasks has timeout.");
                        continue;
                    }
                    try {
                        future.get();
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Yahoo History task completed");
                    } catch (InterruptedException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } catch (ExecutionException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } finally {
                    }
                }
                String doneUrl = "moneydance:fmodule:" + Constants.PROGRAMNAME + ":" + Constants.DONEQUOTECMD + "?" + Constants.TIDCMD + "=" + tid;
                doneUrl += "&" + Constants.TOTALTYPE + "=" + totalQuotes;
                doneUrl += "&" + Constants.OKTYPE + "=" + successful;
                doneUrl += "&" + Constants.ERRTYPE + "=" + failed;
                MRBEDTInvoke.showURL(Main.context, doneUrl);
            }
            case Constants.SOURCEALPHA -> {
                Long timeout;

              // Throttle delay (based on API plan)
              int theoreticalThrottleMS = (60000 / params.getAlphaPlan()) + 10;
              int minThrottleMS = theoreticalThrottleMS;
              int maxThrottleMS = theoreticalThrottleMS;

              // Observed latency (used only for timeout estimation)
              int observedLatencyMS = 1000;

              // Calculate timeout in seconds with 30% buffer
              double perCallDurationSec = Math.max(observedLatencyMS, theoreticalThrottleMS) / 1000.0;
              double actualDuration = (stocks.size() + currencies.size()) * perCallDurationSec;
              timeout = Math.max(180, (long) (actualDuration * 1.3));

              boolean onFirst = true;
                for (String stock : stocks) {
                    GetQuoteTask task = new GetAlphaQuoteHD(stock, tradeCurrencies.get(stock),this, httpClient, Constants.STOCKTYPE, tid,lastPriceDate.get(stock), (onFirst) ? 0 : minThrottleMS, (onFirst) ? 0 : maxThrottleMS);
                    tasks.add(task);
                    totalQuotes++;
                    onFirst = false;
                }
                for (String currency : currencies) {
                    GetQuoteTask task = new GetAlphaQuoteHD(currency, "",this, httpClient, Constants.CURRENCYTYPE, tid,lastPriceDate.get(currency), (onFirst) ? 0 : minThrottleMS, (onFirst) ? 0 : maxThrottleMS);
                    tasks.add(task);
                    totalQuotes++;
                    onFirst = false;
                }

                List<Future<QuotePrice>> futures = null;

                try {
                    threadPool = Executors.newFixedThreadPool(1);
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "AlphaVantage Tasks invoking " + tasks.size() + " queries - Currencies: " + currencies.size() + " Securities: " + stocks.size() + " Overall thread-pool timeout: " + timeout + " seconds (with 1 pool)");
                    Main.alphaVantageLimitReached=false;
                    futures = threadPool.invokeAll(tasks, timeout, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.INFO, e.getMessage());
                }

                if (futures == null) {
                    debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Alpha Failed to invokeAll");
                    return;
                }
                for (Future<QuotePrice> future : futures) {
                    if (future.isCancelled()) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Alpha One of the tasks has timeout.");
                        continue;
                    }
                    try {
                        future.get();
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.SUMMARY, "Alpha task completed");
                    } catch (InterruptedException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } catch (ExecutionException e) {
                        debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
                    } finally {
                    }
                }
                String doneUrl = "moneydance:fmodule:" + Constants.PROGRAMNAME + ":" + Constants.DONEQUOTECMD + "?" + Constants.TIDCMD + "=" + tid;
                doneUrl += "&" + Constants.TOTALTYPE + "=" + totalQuotes;
                doneUrl += "&" + Constants.OKTYPE + "=" + successful;
                doneUrl += "&" + Constants.ERRTYPE + "=" + failed;
                MRBEDTInvoke.showURL(Main.context, doneUrl);

            }
        }
        try {
            httpClient.close();
            threadPool.shutdown();
        } catch (IOException e) {
            e.printStackTrace();
            debugInst.debug("QuoteManager", "getQuotes", MRBDebug.DETAILED, e.getMessage());
        }

    }

    public void errorReturned(String tickerp) {
        failed++;
    }

    public void doneReturned(String tickerp) {
        successful++;
    }
    public void shutdown(){
        threadPool.shutdownNow();
    }
}
