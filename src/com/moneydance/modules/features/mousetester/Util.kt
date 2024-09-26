package com.moneydance.modules.features.mousetester

import java.awt.Color

object Util {
  fun logConsole(message: String) {
    logConsole(false, message)
  }
  
  fun logConsole(objMessage: Any) {
    logConsole(false, objMessage.toString())
  }
  
  fun logConsole(onlyWhenDebug: Boolean, message: String) {
    if (onlyWhenDebug && !Main.DEBUG) return
    System.err.println("${Main.EXTN_ID}: $message")
  }
  
  fun logConsoleAppend(appendSequence: String?) {
    System.err.append(appendSequence)
  }
  
  fun logTerminal(message: String) {
    logTerminal(true, message)
  }
  
  fun logTerminal(objMessage: Any) {
    logTerminal(true, objMessage.toString())
  }
  
  fun logTerminal(onlyWhenDebug: Boolean, message: String) {
    if (onlyWhenDebug && !Main.DEBUG) return
    println("${Main.EXTN_ID}: $message")
  }
  
  val positiveGreen: Color
    get() = Main.mdGUI.colors.budgetHealthyColor
  
  val blue: Color
    get() = Main.mdGUI.colors.reportBlueFG
  val red: Color
    get() = Main.mdGUI.colors.negativeBalFG
  
  val defaultFGColor: Color
    get() = Main.mdGUI.colors.defaultTextForeground
}
