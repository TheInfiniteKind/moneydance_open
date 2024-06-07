package com.moneydance.modules.features.ratios;
import com.infinitekind.moneydance.model.Account;
import com.moneydance.modules.features.ratios.Main;

import java.awt.*;

public class Util {

    public static void logConsole(String message) {
        logConsole(false, message);
    }

    public static void logConsole(Object objMessage) {
        logConsole(false, objMessage.toString());
    }

    public static void logConsole(Boolean onlyWhenDebug, String message) {
        if (onlyWhenDebug && !com.moneydance.modules.features.ratios.Main.DEBUG) return;
        System.err.println(com.moneydance.modules.features.ratios.Main.EXTN_ID + ": " + message);
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
        if (onlyWhenDebug && !com.moneydance.modules.features.ratios.Main.DEBUG) return;
        System.out.println(com.moneydance.modules.features.ratios.Main.EXTN_ID + ": " + message);
    }

    public static Color getPositiveGreen() {
        return Main.getMDGUI().getColors().budgetHealthyColor;
    }

    /**
     * @since 1040
     */
    public static boolean isCategory(Account account) {
        return (account.getAccountType() == Account.AccountType.EXPENSE || account.getAccountType() == Account.AccountType.INCOME);
    }

}
