package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.Util
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.awt.event.ActionListener
import javax.swing.Action

@Suppress("PrivatePropertyName")

/**
 * Adds a "Copy Raw Details to Clipboard" context-menu action that works on any selection of one
 * or more transactions (ParentTxn or SplitTxn), in any context - no account-type or context-type
 * restriction. Concatenates each selected item's raw syncInfo dump into a single clipboard entry.
 *
 * If more than 10 items are selected, confirms with the user first before copying.
 *
 * @param enabled Whether this menu action should be offered. Read once by the caller
 * (Main.getActionsForContext) from user preferences, alongside every other menu-enabled flag -
 * this class does not read preferences itself. Defaults to true only for standalone use/testing;
 * Main.kt supplies the real (default-off) preference value.
 */
class CopyRawDetailsToClipboard(
  private val enabled:Boolean = true
):ContextMenuAction {
  
  private val string_copy_raw_details = "Copy Raw Details to Clipboard"
  private val string_copy_raw_confirm = "Are you sure you want to copy {num} transactions to clipboard?"

  private val CONFIRM_THRESHOLD = 10

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (!enabled) return emptyList()
    if (listTxns.isEmpty()) return emptyList()

    return listOf(
      addAction(label = string_copy_raw_details, cmd = "copy_raw_details_to_clipboard") {
        copyRawDetails(listTxns)
      }
    )
  }

  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }

  private fun copyRawDetails(txns:List<AbstractTxn>) {
    if (txns.size > CONFIRM_THRESHOLD) {
      val msg = string_copy_raw_confirm.replace("{num}", txns.size.toString())
      if (!mdGUI.askQuestion(msg)) return
    }

    val dec = mdGUI.preferences.decimalChar

    val combined = buildString {
      for (txn in txns) {
        val typeName = txn.javaClass.simpleName
        val acctName = txn.account.fullAccountName
        val formattedValue = txn.account.currencyType.formatFancy(txn.value, dec)
        append("--- $typeName: $acctName, ${txn.dateInt}, $formattedValue ---\n")
        try {
          append(txn.syncInfo.toMultilineHumanReadableString())
        } catch (e:Exception) {
          Util.logConsole("CopyRawDetailsToClipboard: failed to read syncInfo for $txn: $e")
          append("<failed to read details: $e>\n")
        }
        append("\n")
      }
    }

    try {
      Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(combined), null)
      Util.logConsole(true, "CopyRawDetailsToClipboard: copied ${txns.size} item(s) to clipboard")
    } catch (e:Exception) {
      Util.logConsole("CopyRawDetailsToClipboard: failed to copy to clipboard: $e")
    }
  }

}