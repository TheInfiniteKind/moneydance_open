/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br></br>
 * [
 * http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)<br></br>
 * \ */
package com.moneydance.modules.features.yahooqt

import java.text.MessageFormat
import java.util.concurrent.Callable
import java.util.concurrent.CancellationException
import java.util.concurrent.ExecutionException
import java.util.concurrent.FutureTask

/**
 * Background thread task parent that is capable of running different kinds of tasks using a stock
 * connection. Provides status updates.
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
class ConnectionTask(task: Callable<Boolean?>, private val _model: StockQuotesModel,
                     private val _resources: ResourceProvider) : FutureTask<Boolean?>(task) {
  val taskName: String = task.toString()
  
  override fun done() {
    if (isCancelled) {
      // remove the current task and signal complete
      if (Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for " + taskName + " done, was canceled.")
      _model.downloadDone(true, taskName, java.lang.Boolean.FALSE)
      return
    }
    var result: Boolean?
    try {
      result = get()
    } catch (ignore: InterruptedException) {
      // if multiple transaction changes come in, the task may be canceled with normal
      // program flow, therefore ignore
      if (Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for " + taskName + " done, InterruptedException")
      result = java.lang.Boolean.FALSE
    } catch (ignore: CancellationException) {
      // if multiple transaction changes come in, the task may be canceled with normal
      // program flow, therefore ignore
      if (Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for " + taskName + " done, CancellationException")
      result = java.lang.Boolean.FALSE
    } catch (error: ExecutionException) {
      error.printStackTrace(System.err)
      if (Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for " + taskName + " done, error received")
      val message = MessageFormat.format(
        _resources.getString(L10NStockQuotes.ERROR_DOWNLOADING_FMT),
        "",
        error.localizedMessage
      )
      _model.showProgress(0.0f, message)
      result = java.lang.Boolean.FALSE
    }
    
    // remove the current task and signal complete
    if (Main.DEBUG_YAHOOQT) System.err.println("ConnectionTask for " + taskName + " done, result " + result)
    _model.downloadDone(true, taskName, result)
  }
}



