/*************************************************************************\
* Copyright (C) 2010 The Infinite Kind, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.yahooqt;

/**
 * Callback interface for editing a stock exchange record. 
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public interface IExchangeEditor {
  /**
   * Edit the given exchange to allow the user to modify the stock exchange definition.
   * @param exchange The exchange to edit.
   * @return True if it was edited, false if it was not changed (or user canceled).
   */
  boolean edit(final StockExchange exchange);
}
