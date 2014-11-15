/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios.selector;

import com.infinitekind.moneydance.model.DisplayableObject;
import com.moneydance.modules.features.ratios.L10NRatios;

public enum FilterSelection
  implements DisplayableObject
{
  REQUIRED(L10NRatios.REQUIRED),
  ALLOWED(L10NRatios.ALLOWED),
  DISALLOWED(L10NRatios.DISALLOWED);

  private final String _resourceKey;

  private FilterSelection(final String resourceKey) {
    _resourceKey = resourceKey;
  }

  public String getResourceKey() {
    return _resourceKey;
  }

}
