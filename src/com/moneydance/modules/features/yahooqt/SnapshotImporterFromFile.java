package com.moneydance.modules.features.yahooqt;

import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.util.CustomDateFormat;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;

/**
 * Created by IntelliJ IDEA.
 * User: Kevin
 * Date: Jun 13, 2010
 * Time: 6:46:16 AM
 * To change this template use File | Settings | File Templates.
 */
public class SnapshotImporterFromFile extends SnapshotImporter {
  private final File _file;

  /**
   * Constructor to allow input fields to be final.
   * @param fileToImport The file to read price history from.
   * @param currency     The currency whose history will be updated from the file.
   * @param dateFormat   The user-specified date format.
   * @param userDecimal  The user-specified character to use as a decimal point.
   */
  public SnapshotImporterFromFile(File fileToImport, CurrencyType currency, SimpleDateFormat dateFormat,
                          char userDecimal) {
    super(currency, dateFormat, userDecimal);
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
  protected BufferedReader getInputStream() throws IOException, DownloadException, NumberFormatException
  {
    InputStream oldIn = new FileInputStream(_file);
    return new BufferedReader(new InputStreamReader(oldIn));
  }
}
