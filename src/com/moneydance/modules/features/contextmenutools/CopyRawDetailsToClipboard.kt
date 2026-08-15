package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.Budget
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.moneydance.model.MoneydanceSyncableItem
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.Reminder
import com.infinitekind.moneydance.model.ReportSpec
import com.infinitekind.moneydance.model.SplitTxn
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.TextViewerDialog
import com.moneydance.modules.features.contextmenutools.util.Util
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.awt.event.ActionListener
import javax.swing.Action

@Suppress("PrivatePropertyName")

/**
 * Adds two context-menu actions that work on any selection of one or more MoneydanceSyncableItem
 * objects (transactions, accounts, reminders, budgets, currencies, report specs, etc.) in any
 * context - no type, account-type, or context-type restriction:
 *
 * - "Copy Raw Details to Clipboard" - concatenates each selected item's raw detail block and
 *   copies it to the system clipboard. Confirms first if more than 10 items are selected.
 * - "Show Raw Details" - same concatenated text, shown in a read-only window instead, with its
 *   own "Copy to Clipboard" button. Never touches the clipboard on open, so it doesn't clobber
 *   whatever the user currently has copied - only the explicit button does.
 *
 * Both actions are independently toggleable (see copyEnabled/showEnabled) and share the same
 * underlying text-building logic (buildCombinedText), so the two are always in sync.
 *
 * Reads directly from menuContext.items (the raw, unfiltered selection MDActionContext exposes -
 * confirmed List<Any> in ContextActions.kt), not the narrower listAccts/listTxns views other
 * actions use, then filters to MoneydanceSyncableItem - confirmed to be the common base every
 * real selectable model type extends (Account, AbstractTxn, Budget, CurrencyType, Reminder,
 * ReportSpec). Confirmed every real MDActionContext construction site in the codebase already
 * populates items with real resolved model objects, never UI tree-node wrappers - so no
 * unwrapping is needed here.
 *
 * Menu labels include the selection count and type, e.g. "Copy Raw Details to Clipboard (3
 * Account objects)" or "...(2 multi-type objects)" when the selection mixes types.
 *
 * DETAIL BLOCK FORMAT: each item gets "--- {header} ---" followed by its syncInfo dump wrapped
 * in { }, 2-space indented inside the braces. The header line varies by type (see buildHeader) -
 * the body itself never varies by type, only which header precedes it. SplitTxn is a special
 * case: after its own header+dump block, its ParentTxn's full header+dump block is appended
 * immediately after, indented 5 spaces, so a split's parent context is always visible without
 * needing to separately select the parent.
 *
 * @param copyEnabled Whether "Copy Raw Details to Clipboard" should be offered. Read once by the
 * caller (Main.getActionsForContext) from user preferences - this class does not read
 * preferences itself. Defaults to true only for standalone use/testing; Main.kt supplies the
 * real (default-off) preference value.
 * @param showEnabled Whether "Show Raw Details" should be offered. Same sourcing as copyEnabled.
 */
class CopyRawDetailsToClipboard(
  private val copyEnabled:Boolean = true,
  private val showEnabled:Boolean = true
):ContextMenuAction {

  private val string_copy_raw_details_template = "Copy Raw Details to Clipboard ({num} {what} {noun})"
  private val string_show_raw_details_template = "Show Raw Details ({num} {what} {noun})"
  private val string_copy_raw_confirm = "Are you sure you want to copy {num} objects to clipboard?"
  private val string_show_raw_confirm = "Are you sure you want to view {num} objects?"
  private val string_copy_to_clipboard_button = "Copy to Clipboard"
  private val string_multi_type = "multi-type"

  private val dialog_show_raw_size = ".gui.show_raw_details.size"
  private val dialog_show_raw_locn = ".gui.show_raw_details.loc"

  private val CONFIRM_THRESHOLD = 10

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    val items = menuContext.items.filterIsInstance<MoneydanceSyncableItem>()
    if (items.isEmpty()) return emptyList()

    val actions = mutableListOf<Action>()
    
    if (showEnabled) {
      actions += addAction(label = buildMenuLabel(string_show_raw_details_template, items), cmd = "show_raw_details") {
        showRawDetails(menuContext, items)
      }
    }
    
    if (copyEnabled) {
      actions += addAction(label = buildMenuLabel(string_copy_raw_details_template, items), cmd = "copy_raw_details_to_clipboard") {
        copyRawDetails(items)
      }
    }

    return actions
  }

  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }

  private fun buildMenuLabel(template:String, items:List<MoneydanceSyncableItem>):String {
    val distinctTypes = items.map { it.javaClass.simpleName }.distinct()
    val what = if (distinctTypes.size == 1) distinctTypes.first() else string_multi_type
    val noun = if (items.size == 1) "object" else "objects"
    return template
      .replace("{num}", items.size.toString())
      .replace("{what}", what)
      .replace("{noun}", noun)
  }

  /**
   * Per-type header line (no braces, no dump - just the "--- {this} ---" content). Account/full
   * account names are wrapped in single quotes throughout. SplitTxn deliberately does NOT
   * include its parent's details inline anymore - that's handled by recursion in buildItemBlock,
   * appended as its own indented block instead.
   */
  private fun buildHeader(item:MoneydanceSyncableItem, dec:Char):String {
    val typeName = item.javaClass.simpleName
    val dateFmt = mdGUI.preferences.shortDateFormatter

    return when (item) {
      is ParentTxn -> {
        val acctName = item.account.fullAccountName
        val currId = item.account.currencyType.getIDString()
        val valueStr = item.account.currencyType.formatFancy(item.value, dec)
        "$typeName: ${dateFmt.format(item.dateInt)}, ${item.description}, '$acctName', $currId, $valueStr, ${item.splitCount} splits"
      }
      is SplitTxn -> {
        val acctName = item.account.fullAccountName
        val currId = item.account.currencyType.getIDString()
        val valueStr = item.account.currencyType.formatFancy(item.value, dec)
        "$typeName: ${dateFmt.format(item.dateInt)}, ${item.description}, '$acctName', $currId, $valueStr"
      }
      is Account -> {
        "$typeName: '${item.fullAccountName}', ${item.getAccountType()}, ${item.currencyType.getIDString()}"
      }
      is Reminder -> {
        val txn = item.transaction
        "$typeName: ${item.description}, '${txn.account.fullAccountName}', ${txn.account.currencyType.formatFancy(txn.value, dec)}, ${txn.splitCount} splits"
      }
      is Budget -> {
        "$typeName: ${item.name}"
      }
      is CurrencyType -> {
        val tickerSuffix = if (item.currencyType == CurrencyType.Type.SECURITY) ", ticker=${item.getTickerSymbol()}" else ""
        "$typeName: ${item.getName()}, ${item.getIDString()}, ${item.currencyType}$tickerSuffix"
      }
      is ReportSpec -> {
        "$typeName: ${item.name}, ${item.reportGenerator}, ${item.reportGenerator?.reportType}"
      }
      else -> "$typeName: $item"
    }
  }

  /** Wraps a raw multiline dump in { }, each original line indented 2 spaces inside. */
  private fun wrapDump(rawDump:String):String {
    val lines = rawDump.trimEnd('\n').split("\n")
    return buildString {
      append("{\n")
      for (line in lines) append("  $line\n")
      append("}\n")
    }
  }

  /** Indents every line of an already-built block by the given number of spaces. */
  private fun indentBlock(block:String, spaces:Int):String {
    val pad = " ".repeat(spaces)
    return block.trimEnd('\n').split("\n").joinToString("\n") { "$pad$it" } + "\n"
  }

  /**
   * Builds one item's full "--- header ---" + brace-wrapped-dump block. For SplitTxn only, the
   * same block for its ParentTxn is appended immediately after, indented 5 spaces - this does
   * not recurse further, since a ParentTxn passed back into this function never re-enters the
   * SplitTxn branch.
   */
  private fun buildItemBlock(item:MoneydanceSyncableItem, dec:Char):String {
    val header = "--- ${buildHeader(item, dec)} ---\n"
    val dump = try {
      wrapDump(item.syncInfo.toMultilineHumanReadableString())
    } catch (e:Exception) {
      Util.logConsole("CopyRawDetailsToClipboard: failed to read syncInfo for $item: $e")
      "{\n  <failed to read details: $e>\n}\n"
    }

    var block = header + dump

    if (item is SplitTxn) {
      val parentBlock = buildItemBlock(item.parentTxn, dec)
      block += indentBlock(parentBlock, 5)
    }

    return block
  }

  private fun buildCombinedText(items:List<MoneydanceSyncableItem>):String {
    val dec = mdGUI.preferences.decimalChar
    return buildString {
      for (item in items) {
        append(buildItemBlock(item, dec))
        append("\n")
      }
    }
  }

  private fun copyRawDetails(items:List<MoneydanceSyncableItem>) {
    if (items.size > CONFIRM_THRESHOLD) {
      val msg = string_copy_raw_confirm.replace("{num}", items.size.toString())
      if (!mdGUI.askQuestion(msg)) return
    }

    val combined = buildCombinedText(items)

    try {
      Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(combined), null)
      Util.logConsole(true, "CopyRawDetailsToClipboard: copied ${items.size} item(s) to clipboard")
    } catch (e:Exception) {
      Util.logConsole("CopyRawDetailsToClipboard: failed to copy to clipboard: $e")
    }
  }

  /**
   * No confirmation threshold here (unlike copyRawDetails) - showing a large read-only window
   * doesn't touch/overwrite anything, so the "are you sure" prompt (which exists specifically to
   * protect the clipboard) doesn't apply.
   */
  private fun showRawDetails(menuContext:MDActionContext, items:List<MoneydanceSyncableItem>) {
    if (items.size > CONFIRM_THRESHOLD) {
      val msg = string_show_raw_confirm.replace("{num}", items.size.toString())
      if (!mdGUI.askQuestion(msg)) return
    }

    val combined = buildCombinedText(items)
    val title = buildMenuLabel(string_show_raw_details_template, items)

    val win = TextViewerDialog(
      mdGUI, menuContext.component, title, combined, string_copy_to_clipboard_button,
      sizeKey = Main.EXTN_ID + dialog_show_raw_size,
      locationKey = Main.EXTN_ID + dialog_show_raw_locn
    )
    win.isVisible = true

    Util.logConsole(true, "CopyRawDetailsToClipboard: showed raw details for ${items.size} item(s)")
  }

}