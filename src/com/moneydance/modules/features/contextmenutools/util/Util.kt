package com.moneydance.modules.features.contextmenutools.util

import com.infinitekind.util.AppDebug
import com.infinitekind.util.DateUtil.today
import com.moneydance.modules.features.contextmenutools.Main
import java.awt.Color
import java.awt.Graphics
import java.awt.Graphics2D
import java.awt.RenderingHints
import java.lang.reflect.Modifier

fun String.prefixExtnID(): String { return "${Main.EXTN_ID}: $this"}

object Util {

  @JvmField var APPDEBUG_ENABLED = false
  
  @JvmStatic fun logConsole(message: String) {
    logConsole(false, message)
  }
  
  @JvmStatic fun logConsole(objMessage: Any) {
    logConsole(false, objMessage.toString())
  }
  
  @JvmStatic fun logConsole(onlyWhenDebug: Boolean, message: String) {
    if (onlyWhenDebug && !Main.DEBUG) return
    if (APPDEBUG_ENABLED) {
      AppDebug.ALL.log(message.prefixExtnID())
    } else {
      System.err.println(message.prefixExtnID())
    }
  }
  
  @JvmStatic fun logTerminal(message: String) {
    logTerminal(true, message)
  }
  
  @JvmStatic fun logTerminal(objMessage: Any) {
    logTerminal(true, objMessage.toString())
  }
  
  @JvmStatic fun logTerminal(onlyWhenDebug: Boolean, message: String) {
    if (onlyWhenDebug && !Main.DEBUG) return
    println(message.prefixExtnID())
  }
  
  val positiveGreen: Color
    get() = Main.mdGUI.colors.budgetHealthyColor
  
  val blue: Color
    get() = Main.mdGUI.colors.reportBlueFG
  val red: Color
    get() = Main.mdGUI.colors.negativeBalFG
  
  val defaultFGColor: Color
    get() = Main.mdGUI.colors.defaultTextForeground
  
  data class TIKDate(val year: Int, val month: Int, val day: Int)
  val Int.extractDate: TIKDate get() = TIKDate(year=this/10000, month = (this/100)%100, day = this%100)

  // the signature changed after MD2024.4(5253) to add @JvmStatic - prevent runtime compatibility issues....
  @JvmStatic val Int?.validYYYYMMDD:Int?
    get() = this?.takeIf { it > 10000000 && it < 40000000 }
  
  // the signature changed after MD2024.4(5253) to add @JvmStatic - prevent runtime compatibility issues....
  @JvmStatic val Int?.nullIfToday:Int?
    get() = this?.takeIf { it != today }
  
  // the signature changed after MD2024.4(5253) to add @JvmStatic - prevent runtime compatibility issues....
  @JvmStatic val String?.nullIfBlank: String?
    get() = if (isNullOrBlank()) null else this
  
  // the signature changed after MD2024.4(5253) to add @JvmStatic - prevent runtime compatibility issues....
  @JvmStatic val String?.blankIfNull: String
    get() = if (isNullOrBlank()) "" else this

}
