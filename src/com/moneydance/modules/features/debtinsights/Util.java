package com.moneydance.modules.features.debtinsights;


import java.awt.*;

public class Util {

    public static void logConsole(String message) {
        logConsole(false, message);
    }

    public static void logConsole(Object objMessage) {
        logConsole(false, objMessage.toString());
    }

    public static void logConsole(Boolean onlyWhenDebug, String message) {
        if (onlyWhenDebug && !Main.DEBUG) return;
        System.err.println(Main.EXTN_ID + ": " + message);
    }

    public static void logConsoleAppend(String appendSequence) {
        System.err.append(appendSequence);
    }

    public static void logTerminal(String message) {
        logTerminal(true, message);
    }

    public static void logTerminal(Object objMessage) {
        logTerminal(true, objMessage.toString());
    }

    public static void logTerminal(Boolean onlyWhenDebug, String message) {
        if (onlyWhenDebug && !Main.DEBUG) return;
        System.out.println(Main.EXTN_ID + ": " + message);
    }

    public static Color getPositiveGreen() {
        return Main.getMDGUI().getColors().budgetHealthyColor;
    }

}
