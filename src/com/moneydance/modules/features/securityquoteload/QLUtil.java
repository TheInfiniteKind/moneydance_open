package com.moneydance.modules.features.securityquoteload;

public class QLUtil {

  public static boolean isCrypto(String ticker) {
    if (ticker == null) return false;
    return ticker.contains("-");
  }
}
