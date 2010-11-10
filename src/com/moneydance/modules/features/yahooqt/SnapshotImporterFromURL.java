/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.model.CurrencyType;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.MessageFormat;
import java.text.SimpleDateFormat;
import java.util.TimeZone;

/**
 * Imports snapshot price data from a URL, assumes CSV format is returned.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class SnapshotImporterFromURL extends SnapshotImporter {
  private final String _urlString;

  /**
   * Constructor to allow input fields to be final.
   * @param url          The URL to read the data from.
   * @param resources    Object to look up localized resources.
   * @param currency     The currency whose history will be updated from the file.
   * @param dateFormat   The user-specified date format.
   * @param timeZone     Time zone to use when parsing downloaded time values.
   * @param userDecimal  The user-specified character to use as a decimal point.
   */
  public SnapshotImporterFromURL(String url, ResourceProvider resources, CurrencyType currency,
                          SimpleDateFormat dateFormat, TimeZone timeZone, char userDecimal) {
    super(resources, currency, dateFormat, timeZone, userDecimal);
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
  protected BufferedReader getInputStream()
          throws IOException, DownloadException, NumberFormatException
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
      errorText = _resources.getString(L10NStockQuotes.IMPORT_ERROR_COMM);
    } catch (NumberFormatException e) {
      errorText = _resources.getString(L10NStockQuotes.IMPORT_ERROR_NUMBER);
    } catch (Exception ex) {
      errorText = ex.getMessage();
    }
    if (error) {
      final String responseMessage = urlConn.getResponseMessage();
      final String message = MessageFormat.format(
              _resources.getString(L10NStockQuotes.IMPORT_ERROR_URL_FMT), errorText, responseMessage);
      throw new DownloadException(_currency, message);
    }
    if(respCode<200 || respCode >= 300) {
      final String responseMessage = urlConn.getResponseMessage();
      final String message = MessageFormat.format(
              _resources.getString(L10NStockQuotes.IMPORT_ERROR_URL_CODE_FMT),
              Integer.valueOf(respCode), responseMessage);
      throw new DownloadException(_currency, message);
    }

    return new BufferedReader(new InputStreamReader(url.openStream(), "UTF8"));
  }
}