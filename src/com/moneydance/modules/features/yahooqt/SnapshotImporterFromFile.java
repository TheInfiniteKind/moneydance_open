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
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;

/**
 * Imports snapshot price data from a CSV file on disk.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class SnapshotImporterFromFile extends SnapshotImporter {
  private final File _file;

  /**
   * Constructor to allow input fields to be final.
   * @param fileToImport The file to read price history from.
   * @param resources    Object to look up localized resources.
   * @param currency     The currency whose history will be updated from the file.
   * @param dateFormat   The user-specified date format.
   * @param userDecimal  The user-specified character to use as a decimal point.
   */
  public SnapshotImporterFromFile(File fileToImport, ResourceProvider resources,
                                  CurrencyType currency, SimpleDateFormat dateFormat,
                                  char userDecimal) {
    super(resources, currency, dateFormat, userDecimal);
    _file = fileToImport;
  }

  @Override
  protected void onBeginImport() {
    System.err.println("Importing history from file: "+_file.toString());
  }

  @Override
  protected void onEndImport(int errorCount) {
    System.err.println("Import complete errors found: "+errorCount);
  }

  @Override
  protected boolean isInputStreamValid() {
    return (_file == null) || !_file.canRead() || !_file.isFile();
  }

  @Override
  protected BufferedReader getInputStream()
          throws IOException, DownloadException, NumberFormatException
  {
    InputStream oldIn = new FileInputStream(_file);
    return new BufferedReader(new InputStreamReader(oldIn));
  }
}
