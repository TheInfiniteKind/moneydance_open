/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

/**
 * An exception encountered while downloading data.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class DownloadException extends Exception {
  private final DownloadInfo downloadInfo;

  DownloadException(final DownloadInfo downloadInfo, final String reason) {
    super(reason);
    this.downloadInfo = downloadInfo;
  }

  DownloadException(final DownloadInfo downloadInfo, final String reason, final Throwable cause) {
    super(reason, cause);
    this.downloadInfo = downloadInfo;
  }

  public DownloadInfo getDownloadInfo() {
    return downloadInfo;
  }
}
