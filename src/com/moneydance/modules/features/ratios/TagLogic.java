package com.moneydance.modules.features.ratios;

import com.infinitekind.util.StringUtils;

/**
 * Defines different logic combinatorial options for tags.
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
    char key = config.trim().charAt(0);
    if (key == 'a') return AND;
    if (key == 'x') return EXACT;
    return OR;
  }
}

