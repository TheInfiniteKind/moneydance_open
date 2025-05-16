package com.moneydance.modules.features.mrbutil;

import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class 	MRBDebug {
	private int iLevel = 1;
	public  static final int  OFF = 0;
	public  static final int INFO = 1;
	public  static final int SUMMARY = 2;
	public static int DETAILED = 3;
	private DateTimeFormatter dtf =DateTimeFormatter.ofPattern("HH:mm:ss"); 
	private String extensionName = "";
	private Boolean appdebugFound;
	private Class<?> appDebug;
	private Class<?> appLogger;
	private Field fieldALL;
	private Method appDebugAll;
	private Object appLoggerInstance;
	public MRBDebug(){
			try {
				appDebug= Class.forName("com.infinitekind.util.AppDebug");
				fieldALL= appDebug.getDeclaredField("ALL");
				fieldALL.setAccessible(true);
				appLoggerInstance = fieldALL.get(appDebug);
				appLogger = appLoggerInstance.getClass();
				appDebugAll = appLogger.getMethod("log", String.class);  // new for MD2024.3(517x)...
				appdebugFound = true;
			}
			catch (ClassNotFoundException|NoSuchMethodException|NoSuchFieldException|IllegalAccessException e){
				appdebugFound=false;
			}
	}
	public int getDebugLevel () {
		return iLevel;
	}
	public void setDebugLevel (int iLevelp) {
		iLevel = iLevelp;
	}
	public void setExtension (String strExtensionp) {
		extensionName = strExtensionp;
	}

	public  synchronized  void debug (String strClass, String strMethod,int iLevelp, String strMessage) {
		if (iLevel != OFF && iLevelp <= iLevel) {
			final String type;
			switch (iLevelp) {
			case INFO:
				type = "INFO";
				break;
			case SUMMARY:
				type = "SUMM";
				break;
			default :
				type = "DET";
			}
			if (javax.swing.SwingUtilities.isEventDispatchThread())
				debugMessage(type,Thread.currentThread().getName(),strClass,strMethod,strMessage);
			else {
				final String thread = Thread.currentThread().getName();
				javax.swing.SwingUtilities.invokeLater(new Runnable() {
					@Override
					public void run() {
						debugMessage(type, thread, strClass, strMethod, strMessage);
					}
				});
			}
		}
	}	
	public synchronized  void debugMessage (String type, String thread,String strClass, String strMethod, String strMessage) {
		if (appdebugFound){
			try {
				appDebugAll.invoke(appLoggerInstance,extensionName + ">"+type+"-"+thread+"("+strClass+","+strMethod+ ") " +strMessage);
				return;
			}
			catch (IllegalAccessException | InvocationTargetException e){

			}
		}
		LocalTime now= LocalTime.now();
		System.err.println(extensionName + ">"+type+":"+now.format(dtf)+"-"+thread+"("+strClass+","+strMethod+ ") " +strMessage);
	}
}
