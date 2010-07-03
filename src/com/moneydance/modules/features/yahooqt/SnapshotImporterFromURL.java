package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.controller.URLUtil;
import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.util.CustomDateFormat;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

/**
 * Created by IntelliJ IDEA.
 * User: Kevin
 * Date: Jun 13, 2010
 * Time: 6:46:16 AM
 * To change this template use File | Settings | File Templates.
 */
public class SnapshotImporterFromURL extends SnapshotImporter {
  private final String _urlString;

  /**
   * Constructor to allow input fields to be final.
   * @param url          The URL to read the data from.
   * @param currency     The currency whose history will be updated from the file.
   * @param dateFormat   The user-specified date format.
   * @param userDecimal  The user-specified character to use as a decimal point.
   */
  public SnapshotImporterFromURL(String url, CurrencyType currency, SimpleDateFormat dateFormat,
                          char userDecimal) {
    super(currency, dateFormat, userDecimal);
    _urlString = url;
  }

  @Override
  protected void onBeginImport() {
    System.err.println("Importing history from URL: "+ _urlString);
  }

  @Override
  protected void onEndImport(int errorCount) {
    if (errorCount != 0) System.err.println("Import complete errors found: "+errorCount);
  }

  @Override
  protected boolean isInputStreamValid() {
    return (!SQUtil.isBlank(_urlString));
  }

  @Override
  protected BufferedReader getInputStream() throws IOException, DownloadException, NumberFormatException
  {
    URL url = new URL(_urlString);
    HttpURLConnection urlConn = (HttpURLConnection)url.openConnection();
    int respCode = 0;
    String errorText = null;
    boolean error = true;
    try {
      respCode = urlConn.getResponseCode();
      error = false;
    } catch (IOException e) {
      errorText = "Communication";
    } catch (NumberFormatException e) {
      errorText = "Invalid Data";
    } catch (Exception ex) {
      errorText = "Unknown: "+ex.getMessage();
    }
    if (error) {
      final String responseMessage = urlConn.getResponseMessage();
      final String message = "Error: "+errorText+", received response message '" + responseMessage;
      throw new DownloadException(_currency, message);
    }
    if(respCode<200 || respCode >= 300) {
      final String responseMessage = urlConn.getResponseMessage();
      final String message = "Received response code " + respCode + " and message '" +
              responseMessage + "'";
      throw new DownloadException(_currency, message);
    }

    return new BufferedReader(new InputStreamReader(url.openStream(), "UTF8"));
  }
}