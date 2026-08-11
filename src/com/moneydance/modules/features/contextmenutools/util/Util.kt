package com.moneydance.modules.features.contextmenutools.util

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.UndoableChange
import com.infinitekind.util.AppDebug
import com.infinitekind.util.DateUtil.today
import com.moneydance.modules.features.contextmenutools.Main
import java.awt.Color
import java.awt.Component
import java.awt.Dialog

fun String.prefixExtnID(): String { return "${Main.EXTN_ID}: $this"}

/**
 * UndoableChange.name became a public var in MD2026. For compatibility with pre-2026 builds,
 * try the setName() method first, then fall back to reflection on the private field. Silently
 * does nothing if neither exists (older/unexpected builds).
 */
fun UndoableChange.setNameCompat(name:String) {
  val clazz = this.javaClass
  val setOk = runCatching {
    val m = clazz.getMethod("setName", String::class.java)
    m.invoke(this, name)
  }.isSuccess
  if (!setOk) {
    runCatching {
      val f = clazz.getDeclaredField("name")
      f.isAccessible = true
      f.set(this, name)
    }
  }
}

/**
 * AbstractTxn.downloadMatchType / DownloadMatchType exist at runtime on MD2024.4, but not in
 * the earlier compile-time API jar this module builds against. Reflect both the getter and the
 * NO_MATCH constants, without a compile-time reference to the missing type.
 */
fun AbstractTxn.downloadMatchTypeCompat():Any {
  return try {
    this.javaClass.getMethod("getDownloadMatchType").invoke(this)
    ?: throw IllegalStateException("downloadMatchType reflection returned null for $this")
  } catch (e:Exception) {
    throw IllegalStateException("Failed to reflect AbstractTxn.downloadMatchType via reflection", e)
  }
}

val noMatchConstantCompat:Any by lazy {
  try {
    val enumClass = Class.forName("com.infinitekind.moneydance.model.AbstractTxn\$DownloadMatchType")
    enumClass.getField("NO_MATCH").get(null)
    ?: throw IllegalStateException("NO_MATCH field reflection returned null")
  } catch (e:Exception) {
    throw IllegalStateException("Failed to reflect AbstractTxn.DownloadMatchType.NO_MATCH via reflection", e)
  }
}

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
  
  @JvmStatic
  fun getComponentDialog(component: Component?): Dialog? {
    var c = component ?: return null
    while(true) {
      if (c is Dialog) { return c }
      c = c.parent ?: return null
    }
  }
}
