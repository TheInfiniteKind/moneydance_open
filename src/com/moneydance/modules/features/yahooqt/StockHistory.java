package com.moneydance.modules.features.yahooqt;

import java.util.Collections;
import java.util.List;

/**
* Created by IntelliJ IDEA.
* User: Kevin
* Date: Jun 16, 2010
* Time: 6:37:32 AM
* To change this template use File | Settings | File Templates.
*/
public class StockHistory {
  private String baseCurrency;
  private List<StockRecord> _records;
  private final int _errors;

  StockHistory(String baseCurrency, List<StockRecord> records, int errorCount) {
    this.baseCurrency = baseCurrency;
    _records = records;
    _errors = errorCount;
  }

  public int getErrorCount() {
    return _errors;
  }

  public String getCurrency() {
    return this.baseCurrency;
  }

  public int getRecordCount() {
    return _records ==null ? 0 : _records.size();
  }

  public StockRecord getRecord(int index) {
    return _records.get(index);
  }

  public StockRecord findMostRecentValidRecord() {
    Collections.sort(_records);
    for (int index = _records.size() - 1; index >= 0; index--) {
      StockRecord record = _records.get(index);
      if (record.closeRate != 0.0) return record;
    }
    return null;
  }
}
