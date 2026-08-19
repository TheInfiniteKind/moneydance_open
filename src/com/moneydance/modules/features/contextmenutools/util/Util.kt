package com.moneydance.modules.features.contextmenutools.util

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Reminder
import com.infinitekind.moneydance.model.UndoableChange
import com.infinitekind.util.AppDebug
import com.infinitekind.util.DateUtil.today
import com.moneydance.modules.features.contextmenutools.Main
import com.moneydance.modules.features.contextmenutools.Main.Companion.extensionContext
import java.awt.Color
import java.awt.Component
import java.awt.Dialog

fun String.prefixExtnID(): String { return "${Main.EXTN_ID}: $this"}

/**
 * Logs why a menu action was withheld entirely, or offered with fewer options than usual, gated
 * on either the extension's own "Enable debug messages" checkbox OR Moneydance's launch debug
 * flag. Shared by any action class that wants this exact shape (caller builds the full message,
 * source is the calling class's own display name for the log prefix).
 *
 * NOTE: CopyPasteSplits.kt has its own separate logBlockedIfDebug with a different shape (takes
 * a ParentTxn and builds richer context itself) and a different gate (debugMenuEnabled only, no
 * DEBUG) - that one is deliberately NOT unified with this one, since doing so would change its
 * existing, shipped behavior rather than just share identical logic.
 */
fun logBlockedIfDebug(source:String, message:String) {
  if (extensionContext?.debugMenuEnabled != true && !Main.DEBUG) return
  Util.logConsole(false, "$source: $message")
}

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

/**
 * Reminder.getNextOccurrences(maximumDate: Int? = null): List<Int> exists at runtime on
 * Moneydance build 5202+, but not in the earlier compile-time API jar this module builds
 * against - same situation as AbstractTxn.downloadMatchTypeCompat above. Unlike that one, this
 * fails soft (returns null) rather than throwing: callers use this for decorative "next few
 * dates" display info, not a decision-critical value, so a reflection failure (older runtime, or
 * an unexpected return type) should fall back silently to Reminder.getNextOccurance() (singular,
 * always available) rather than break the caller.
 *
 * Real signature confirmed: `fun getNextOccurrences(maximumDate: Int? = null): List<Int>`. The
 * nullable Int parameter is boxed (java.lang.Integer) at the bytecode level - reflecting with
 * Integer::class.java, not Int::class.java. The return type is always a List<Int> (boxed
 * Integer elements at runtime), never an IntArray.
 */
fun Reminder.getNextOccurrencesCompat(maximumDate:Int? = null):List<Int>? {
  return try {
    val method = this.javaClass.getMethod("getNextOccurrences", Integer::class.java)
    (method.invoke(this, maximumDate) as? List<*>)?.filterIsInstance<Int>()
  } catch (e:Exception) {
    null
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
  
  /**
   * Loads a small icon from the extension jar's classpath resources (e.g. an icon dropped into
   * src/.../contextmenutools/icons/ and built into the jar). Returns null (never throws) if the
   * resource isn't found or fails to load - callers should fall back to a text/unicode label.
   */
  @JvmStatic
  fun loadIcon(resourcePath:String):javax.swing.Icon? {
    return try {
      val cl = Main::class.java.classLoader
      val stream = cl.getResourceAsStream(resourcePath) ?: return null
      val bytes = stream.readBytes()
      val img = java.awt.Toolkit.getDefaultToolkit().createImage(bytes)
      javax.swing.ImageIcon(img)
    } catch (e:Throwable) {
      null
    }
  }
  
  /** Loads a UTF-8 text resource bundled in the extension jar, e.g. "/contextmenutools_readme.txt"
   *  at the resource root. Returns a placeholder message instead of throwing if the resource is
   *  missing or unreadable. */
  fun loadTextResource(resourcePath:String):String {
    return try {
      extensionContext?.javaClass?.getResourceAsStream(resourcePath)
        ?.bufferedReader(Charsets.UTF_8)
        ?.use { it.readText() }
      ?: "<Resource not found: $resourcePath>"
    } catch (e:Exception) {
      "<Error loading resource '$resourcePath': $e>"
    }
  }
}