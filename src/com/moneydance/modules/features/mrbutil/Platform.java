package com.moneydance.modules.features.mrbutil;

public class Platform
{
  private static final String OS = System.getProperty("os.name").toLowerCase();
  private static final String VERSION = System.getProperty("os.version").toLowerCase();
  public static double JAVA_VERSION = getVersion();

  public static boolean isWindows() {
    return OS.indexOf("win") >= 0;
  }

  public static boolean isMac()
  {
    return (OS.indexOf("mac") >= 0) && 
      (!isOSX());
  }

  public static boolean isOSX() {
    return OS.indexOf("os x") >= 0;
  }

  public static boolean isUnix() {
    return (OS.indexOf("nix") >= 0) || (OS.indexOf("nux") >= 0);
  }

  public static boolean isFreeBSD() {
    return OS.startsWith("freebsd");
  }

  public static boolean isOSXVersionAtLeast(String version) {
    return VERSION.compareToIgnoreCase(version) >= 0;
  }

  private static double getVersion() {
    String version = System.getProperty("java.version");
    int pos = 0; int count = 0;
    for (; (pos < version.length()) && (count < 2); pos++) {
      if (version.charAt(pos) == '.') count++;
    }

    version = version.substring(0, pos);
    if (version.endsWith(".")) {
      version = version.substring(0, pos - 1);
    }

    return Double.parseDouble(version);
  }
}