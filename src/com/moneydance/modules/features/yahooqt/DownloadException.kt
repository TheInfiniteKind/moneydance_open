/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt

/**
 * An exception encountered while downloading data.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class DownloadException : Exception {
  val downloadInfo: DownloadInfo
  
  internal constructor(downloadInfo: DownloadInfo, reason: String?) : super(reason) {
    this.downloadInfo = downloadInfo
  }
  
  internal constructor(downloadInfo: DownloadInfo, reason: String?, cause: Throwable?) : super(reason, cause) {
    this.downloadInfo = downloadInfo
  }
}
