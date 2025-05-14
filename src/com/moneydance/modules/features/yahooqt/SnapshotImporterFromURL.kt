/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.moneydance.modules.features.yahooqt.DownloadException
import com.moneydance.modules.features.yahooqt.SQUtil.isBlank
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL
import java.text.MessageFormat
import java.text.SimpleDateFormat
import java.util.*

/**
 * Imports snapshot price data from a URL, assumes CSV format is returned.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class SnapshotImporterFromURL
/**
 * Constructor to allow input fields to be final.
 * @param url          The URL to read the data from.
 * @param cookie       The name of the cookie, or null if non exists.
 * @param resources    Object to look up localized resources.
 * @param downloadInfo Information about the currency or security to be updated
 * @param dateFormat   The user-specified date format.
 * @param timeZone     Time zone to use when parsing downloaded time values.
 * @param userDecimal  The user-specified character to use as a decimal point.
 */(private val _urlString: String, private val _cookieString: String?, resources: ResourceProvider,
    downloadInfo: DownloadInfo,
    dateFormat: SimpleDateFormat, timeZone: TimeZone?, userDecimal: Char) : SnapshotImporter(resources, downloadInfo, dateFormat, timeZone, userDecimal) {
  override fun onBeginImport() {
    QER_DLOG.log { "Importing history from URL: $_urlString" }
  }
  
  override fun onEndImport(errorCount: Int) {
    if (errorCount != 0) QER_DLOG.log { "Import complete errors found: $errorCount" }
  }
  
  override val isInputStreamValid: Boolean
    get() = (!isBlank(_urlString))
  
  @get:Throws(IOException::class, DownloadException::class, NumberFormatException::class)
  override val inputStream: BufferedReader
    get() {
      val url = URI(_urlString).toURL()
      val urlConn = url.openConnection() as HttpURLConnection
      if (_cookieString != null) {
        urlConn.setRequestProperty("Cookie", _cookieString)
      }
      var respCode = 0
      var errorText: String? = null
      var error = true
      try {
        respCode = urlConn.responseCode
        error = false
      } catch (e: IOException) {
        errorText = _resources.getString(L10NStockQuotes.IMPORT_ERROR_COMM)
      } catch (e: NumberFormatException) {
        errorText = _resources.getString(L10NStockQuotes.IMPORT_ERROR_NUMBER)
      } catch (ex: Exception) {
        errorText = ex.message
      }
      if (error) {
        val responseMessage = urlConn.responseMessage
        val message = MessageFormat.format(
          _resources.getString(L10NStockQuotes.IMPORT_ERROR_URL_FMT), errorText, responseMessage
        )
        throw DownloadException(downloadInfo, message)
      }
      if (respCode < 200 || respCode >= 300) {
        val responseMessage = urlConn.responseMessage
        val message = MessageFormat.format(
          _resources.getString(L10NStockQuotes.IMPORT_ERROR_URL_CODE_FMT),
          respCode, responseMessage
        )
        throw DownloadException(downloadInfo, message)
      }
      return BufferedReader(InputStreamReader(urlConn.inputStream, "UTF8"))
    }
}