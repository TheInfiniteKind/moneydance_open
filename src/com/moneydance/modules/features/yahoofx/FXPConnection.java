/************************************************************\
 *      Copyright (C) 2003 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.oanda;

import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.util.*;
import java.net.*;
import java.io.*;
import java.util.*;
import java.text.*;

/** Class used to communicate with www.oanda.com using the FXP
    exchange rate protocol. */
public class FXPConnection {
  public static final String DEFAULT_HOST = "www.oanda.com";
  public static final int DEFAULT_PORT = 5011;

  public static final String VALUE_TYPE_BID = "bid";
  public static final String VALUE_TYPE_ASK = "ask";
  public static final String VALUE_TYPE_MIN_BID = "min_bid";
  public static final String VALUE_TYPE_MIN_ASK = "min_ask";
  public static final String VALUE_TYPE_MAX_BID = "max_bid";
  public static final String VALUE_TYPE_MAX_ASK = "max_ask";
  public static final String VALUE_TYPE_FRACTILE_LOW_BID = "fractile_low_bid";
  public static final String VALUE_TYPE_FRACTILE_LOW_ASK = "fractile_low_ask";
  public static final String VALUE_TYPE_FRACTILE_HIGH_BID = "fractile_high_bid";
  public static final String VALUE_TYPE_FRACTILE_HIGH_ASK = "fractile_high_ask";
  public static final String VALUE_TYPE_NUM_TICKS = "num_ticks";

  public static final int ACCURACY_DAY = 0;
  public static final int ACCURACY_SECOND = 2;

  private static final String FXP_HEADER = "fxp/1.1";
  private static final String NEWLINE = "\r\n";
  
  private Socket socket;
  private String hostname;
  private int port;
  
  /** Create a connection to the default host and port. */
  public FXPConnection(Main main)
    throws Exception
  {
    this(main, DEFAULT_HOST, DEFAULT_PORT);
  }

  /** Create a connection to the given host on the default port */
  public FXPConnection(Main main, String hostname)
    throws Exception
  {
    this(main, hostname, DEFAULT_PORT);
  }
                                         
  
  /** Create a connection to the given host and port. */
  public FXPConnection(Main main, String hostname, int port)
    throws Exception
  {
    try {
      UserPreferences prefs =
        ((com.moneydance.apps.md.controller.Main)main.getExtContext()).getPreferences();
      if(prefs.getBoolSetting(UserPreferences.NET_USE_PROXY, false)) {
        String proxyHost = prefs.getSetting(UserPreferences.NET_PROXY_HOST, "127.0.0.1");
        int proxyPort = prefs.getIntSetting(UserPreferences.NET_PROXY_PORT, 80);
        socket = new Socket(proxyHost, proxyPort);
        socket.setSoTimeout(5000);
        OutputStream out = socket.getOutputStream();
        out.write(("CONNECT "+hostname+':'+port+" HTTP/1.0\n").getBytes("UTF8"));
        out.flush();
      } else {
        socket = new Socket(hostname, port);
        socket.setSoTimeout(5000);
      }
      
    } catch(Throwable t) {
      System.err.println("unable to connect to FXP server: "+t);
      if(t instanceof Exception) {
        throw (Exception)t;
      } else {
        throw new Exception("Error: "+t);
      }
    }
  }

  /** Read the status line and process the response code.  This
      throws an exception with the response message if the
      response was not a successful one.  */
  private void processStatusLine(Reader in)
    throws Exception
  {
    String line = readLine(in);
    if(line==null) {
      throw new Exception("Disconnected while reading response header");
    }
    line = line.trim();
    String protocolStr = StringUtils.fieldIndex(line,' ',0).trim();
    String responseCodeStr = StringUtils.fieldIndex(line,' ',1).trim();
    String responseMsgStr = StringUtils.fieldIndex(line,' ',2).trim();
    int responseCode;

    try {
      responseCode = Integer.parseInt(responseCodeStr);
    } catch (Exception e) {
      throw new Exception("Invalid response code: "+responseCodeStr+
                          " "+responseMsgStr);
    }
    if(responseCode!=200) {
      throw new Exception(String.valueOf(responseCode)+" "+responseMsgStr);
    }

    return;
  }


  /** Retrieve the rate from fromCurrency to toCurrency.
      Multiplying an amount in fromCurrency by the returned
      rate will yield a value in toCurrency at the given
      date. */
  public synchronized double[] getRates(String fromCurrency,
                                        String toCurrency,
                                        long endDate,
                                        int numDays,
                                        boolean invertDownload)
    throws Exception
  {
    OutputStreamWriter out = new OutputStreamWriter(new EchoOutputStream(socket.getOutputStream()));

    long startDate = endDate - (numDays * 86400000L);

    out.write(FXP_HEADER);
    out.write(NEWLINE);
    out.write("Query: quote");
    out.write(NEWLINE);
    out.write("QuoteCurrency: "+(invertDownload?fromCurrency:toCurrency));
    out.write(NEWLINE);
    out.write("BaseCurrency: "+(invertDownload?toCurrency:fromCurrency));
    out.write(NEWLINE);
    out.write("Date: "+StringUtils.getGMTDateStr(new Date(startDate)));
    out.write(NEWLINE);
    out.write("Timeincrement: 86400");
    out.write(NEWLINE);
    out.write("Nprices: "+numDays);
    out.write(NEWLINE);
    out.write(NEWLINE);
    out.flush();

    BufferedReader in =
      new BufferedReader(new InputStreamReader(new EchoInputStream(socket.getInputStream())));
    FXPMessage response = readResponse(in);

    double rates[] = new double[numDays];
    Enumeration lines = response.getLines();
    for(int i=0; i<numDays; i++) {
      if(!lines.hasMoreElements()) {
        rates[i] = -1.0;
      } else {
        String line = (String)lines.nextElement();
        try {
          rates[i] = StringUtils.parseDoubleWithException(line.trim(),'.');
          if(rates[i]!=0.0 && !invertDownload)
            rates[i] = 1/rates[i];
        } catch (Exception e) {
          rates[i] = -1.0;
        }
      }
    }
    return rates;
  }
  
  private FXPMessage readResponse(Reader in)
    throws Exception
  {
    processStatusLine(in);
    FXPMessage response = new FXPMessage();

    // read the response headers...
    while(true) {
      String line = readLine(in);
      line = line.trim();
      if(line.length()==0) 
        break; // end of headers
      int colIdx = line.indexOf(':');
      if(colIdx>=0) {
        response.addHeader(line.substring(0,colIdx),
                           line.substring(colIdx+1).trim());
      }
    }
    // read the body of the response...
    String lines = response.getHeader("content-lines", null);
    if (lines != null) {
      int contentLines = Integer.parseInt(lines);
      for(int i=0; i<contentLines; i++) {
        String line = readLine(in);
        if (line != null) response.addLine(line);
        else break;
      }
    }
    return response;
  }

  
  private synchronized String readLine(Reader in)
    throws IOException
  {
    StringBuffer sb = new StringBuffer();
    int ich;
    while(true) {
      ich = in.read();
      if(ich<0) { // end of the connection... clean up a bit
        close();
        throw new IOException("Disconnected");
      }

      sb.append((char)ich);      
      if(sb.toString().indexOf(NEWLINE)>=0) {
        return sb.toString();
      }
    }
  }
  
  
  private class EchoInputStream
    extends InputStream
  {
    private InputStream in;
    
    EchoInputStream(InputStream in) {
      this.in = in;
    }

    public int read()
      throws IOException
    {
      int b = in.read();
      if(b>=0) {
        if((b>=0x20 && b<=0x80) || b==10 || b==13) System.err.write(b);
        else System.err.write('?');
      }
      return b;
    }
  }
  
  private class EchoOutputStream
    extends OutputStream
  {
    private OutputStream out;
    
    EchoOutputStream(OutputStream out) {
      this.out = out;
    }

    public void write(int b)
      throws IOException
    {
      out.write(b);
      if((b>=0x20 && b<=0x80) || b==10 || b==13) System.err.write(b);
      else System.err.write('?');
    }

    public void write(byte b[])
      throws IOException
    {
      out.write(b);
      System.err.write(b);
    }

    public void write(byte b[], int offset, int len)
      throws IOException
    {
      out.write(b, offset, len);
      System.err.write(b, offset, len);
    }

    public void close()
      throws IOException
    {
      out.close();
    }

    public void flush()
      throws IOException
    {
      super.flush();
      out.flush();
    }
  }

  private class FXPMessage {
    private Hashtable headers;
    private Vector lines;

    FXPMessage() {
      headers = new Hashtable();
      lines = new Vector();
    }

    public void addHeader(String key, String val) {
      headers.put(key.toUpperCase(), val);
    }

    public String getHeader(String key, String defaultVal) {
      String val = (String)headers.get(key.toUpperCase());
      if(val==null)
        return defaultVal;
      return val;
    }

    public void addLine(String line) {
      lines.addElement(line);
    }

    public Enumeration getLines() {
      return lines.elements();
    }
  }

  public synchronized void close() {
    try {
      socket.close();
    } catch (Throwable e) {} 
    socket = null;
  }

}
