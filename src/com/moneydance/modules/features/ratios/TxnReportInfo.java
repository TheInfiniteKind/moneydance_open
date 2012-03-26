/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

/**
 * A holder class for computed transaction info. This class is immutable.
 */
class TxnReportInfo {
  final long convertedValue;
  final boolean isSourceRequired;
  final boolean isTargetRequired;

  TxnReportInfo(final long value,
                final boolean sourceRequired,
                final boolean targetRequired) {
    convertedValue = value;
    isSourceRequired = sourceRequired;
    isTargetRequired = targetRequired;
  }
}
