package com.moneydance.modules.features.mrbutil;

import javax.swing.*;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class 	MRBDebug {
	private DebugLevel level = DebugLevel.INFO;
	public static final int  OFF = 0;
	public static final int INFO = 1;
	public static final int SUMMARY = 2;
	public static int DETAILED = 3;
	public static int DEVELOPER = 4;
	private DateTimeFormatter dtf = DateTimeFormatter.ofPattern("HH:mm:ss");
	private String extensionName = "";
	private Boolean appdebugFound;
	private Class<?> appDebug;
	private Class<?> appLogger;
	private Field fieldALL;
	private Method appDebugAll;
	private Object appLoggerInstance;

  public enum DebugLevel {
    OFF(0, "OFF"),
    INFO(1, "INFO"),
    SUMMARY(2, "SUMM"),
    DETAILED(3, "DET"),
    DEVELOPER(4, "*DEV*");
    private final int iLevel;
  	private final String shortName;

    DebugLevel(int iLevel, String shortName) {
      this.iLevel = iLevel;
      this.shortName = shortName;
    }
    public int getLevel() { return iLevel; }
    public String getShortName() { return shortName;}

    public static DebugLevel fromInt(int level) {
      for (DebugLevel dl : DebugLevel.values()) {
        if (dl.iLevel == level) return dl;
      }
      return OFF;  // or throw IllegalArgumentException if preferred
    }

    public static boolean shouldDebugMessage(DebugLevel levelTypeMessage, DebugLevel levelTypeSetting) {
      return levelTypeMessage.getLevel() <= levelTypeSetting.getLevel();
    }
  }

  public MRBDebug() {
    try {
      appDebug = Class.forName("com.infinitekind.util.AppDebug");
      fieldALL = appDebug.getDeclaredField("ALL");
      fieldALL.setAccessible(true);
      appLoggerInstance = fieldALL.get(appDebug);
      appLogger = appLoggerInstance.getClass();
      appDebugAll = appLogger.getMethod("log", String.class);  // new for MD2024.3(517x)...
      appdebugFound = true;
    } catch (ClassNotFoundException | NoSuchMethodException | NoSuchFieldException | IllegalAccessException e) {
      appdebugFound = false;
    }
  }

  public int getDebugLevel() { return getDebugLevelType().getLevel();}
	public DebugLevel getDebugLevelType() { return level; }

  @Deprecated public void setDebugLevel(int iLevelp) { setDebugLevel(DebugLevel.fromInt(iLevelp)); } // ideally use setDebugLevel(<DebugLevel>) instead...
	public void setDebugLevel(DebugLevel levelType) { level = levelType; }

	public void setExtension (String strExtensionp) {
		extensionName = strExtensionp;
	}

	public  synchronized void debug (String strClass, String strMethod, int iLevelp, String strMessage) {
    debug(strClass, strMethod, DebugLevel.fromInt(iLevelp), strMessage);
  }

  public synchronized void debug(String strClass, String strMethod, DebugLevel levelTypeMessage, String strMessage) {
    DebugLevel levelTypeSetting = getDebugLevelType();
    if (levelTypeSetting == DebugLevel.OFF) return;
    if (!DebugLevel.shouldDebugMessage(levelTypeMessage, levelTypeSetting)) return;
    debugMessage(levelTypeMessage.shortName, Thread.currentThread().getName(), strClass, strMethod, strMessage);
  }

  public synchronized  void debugMessage (String type, String thread,String strClass, String strMethod, String strMessage) {
		if (appdebugFound){
			try {
				appDebugAll.invoke(appLoggerInstance,extensionName + ">"+type+"-"+thread+"("+strClass+","+strMethod+ ") " +strMessage);
				return;
			}
			catch (IllegalAccessException | InvocationTargetException ignored){
			}
		}
    LocalTime now = LocalTime.now();
    System.err.println(extensionName + ">" + type + ":" + now.format(dtf) + "-" + thread + "(" + strClass + "," + strMethod + ") " + strMessage);
	}
}
