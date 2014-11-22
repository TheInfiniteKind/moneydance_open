package com.moneydance.modules.features.ratios;

import com.moneydance.util.StringUtils;


/**
 * <p>Defines different logic combinatorial options for tags.</p>
 *
 * @author Kevin Menningen - Mennē Software Solutions, LLC
 */
public enum TagLogic
{
  AND('a'),
  OR('o'),
  EXACT('x');

  private final char _configKey;

  private TagLogic(final char configKey) {
    _configKey = configKey;
  }

  public String getConfigKey() {
    return String.valueOf(_configKey);
  }

  public static TagLogic fromString(final String config) {
    if (StringUtils.isBlank(config)) return OR;
    char key = config.charAt(0);
    if (key == 'a') return AND;
    if (key == 'x') return EXACT;
    return OR;
  }
}


