/*************************************************************************\
 * Copyright (C) 2015 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 \*************************************************************************/


package com.moneydance.modules.features.findandreplace;

import java.awt.EventQueue;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * This class acts as a gateway for logging, so we can turn logging on and off as needed.
 */
public final class Logger {
  private static final long NOT_USED = Long.MIN_VALUE;
  private static final long[] _enrolledThreadIds = new long[10];
  private static int _reuseThreadIndex = -1;
  private static final DateFormat _formatter = new SimpleDateFormat("MM-dd HH:mm:ss.SSS|");

  
  static {
    for (int index = 0; index < 10; index++) _enrolledThreadIds[index] = NOT_USED;
  }
  
  public static void log(final String message) {
    logError(message, null);
  }

  public static void logError(final String message, final Throwable error) {
    System.err.println(generateLogEntry(message));
    if (error != null) {
      error.printStackTrace();
    }
  }


  /**
   * Create a log message entry like this:<br/>
   * <code>handybank (M): 04-24 05:41:49.734|This is the log message passed in.</code>
   * @param message The message to log to the console.
   * @return The complete log line.
   */
  private static String generateLogEntry(final String message) {
    Date now = new Date();
    StringBuilder sb = new StringBuilder(message.length() + 34);
    sb.append("findandreplace (");
    sb.append(getThreadId());
    sb.append("): ");
    sb.append(_formatter.format(now));
    sb.append(message);
    return sb.toString();
  }

  private static char getThreadId() {
    if (EventQueue.isDispatchThread()) return 'M';
    long id = Thread.currentThread().getId();
    for (int index = 0; index < 10; index++) {
      if (_enrolledThreadIds[index] == NOT_USED) {
        _enrolledThreadIds[index] = id;
        return Character.forDigit(index, 10);
      }
      if (_enrolledThreadIds[index] == id) return Character.forDigit(index, 10);
    }
    // ten threads have been created and rolled over, reuse
    System.err.println("findandreplace-Logger: More than 10 threads created, recycling thread indexes");
    ++_reuseThreadIndex;
    if (_reuseThreadIndex > 9) _reuseThreadIndex = 0;
    _enrolledThreadIds[_reuseThreadIndex] = id;
    return Character.forDigit(_reuseThreadIndex, 10);
  }
  

  private Logger() {
    // static utilities only
  }
}
