/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

import java.text.MessageFormat;
import java.util.concurrent.Callable;
import java.util.concurrent.CancellationException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;

/**
 * Background thread task parent that is capable of running different kinds of tasks using a stock
 * connection. Provides status updates.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public class ConnectionTask extends FutureTask<Boolean> {
  private final StockQuotesModel _model;
  private final ResourceProvider _resources;
  private final String _taskName;

  public ConnectionTask(final Callable<Boolean> task, final StockQuotesModel model,
                        final ResourceProvider resources) {
    super(task);
    _model = model;
    _resources = resources;
    _taskName = task.toString();
  }

  String getTaskName() { return _taskName; }

  @Override
  protected void done() {
    if (isCancelled()) {
      // remove the current task and signal complete
      if(Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for "+_taskName+" done, was canceled.");
      _model.downloadDone(true, _taskName, Boolean.FALSE);
      return;
    }
    Boolean result;
    try {
      result = get();
    }
    catch (InterruptedException ignore) {
      // if multiple transaction changes come in, the task may be canceled with normal
      // program flow, therefore ignore
      if(Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for "+_taskName+" done, InterruptedException");
      result = Boolean.FALSE;
    }
    catch (CancellationException ignore) {
      // if multiple transaction changes come in, the task may be canceled with normal
      // program flow, therefore ignore
      if(Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for "+_taskName+" done, CancellationException");
      result = Boolean.FALSE;
    }
    catch (ExecutionException error) {
      error.printStackTrace(System.err);
      if(Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for "+_taskName+" done, error received");
      String message = MessageFormat.format(
              _resources.getString(L10NStockQuotes.ERROR_DOWNLOADING_FMT),
              "",
              error.getLocalizedMessage());
       _model.showProgress(0.0f, message);
      result = Boolean.FALSE;
    }

    // remove the current task and signal complete
    if(Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for "+_taskName+" done, result "+result);
    _model.downloadDone(true, _taskName, result);
  }
}



