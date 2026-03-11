package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.util.labelify
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.apps.md.view.gui.OKButtonWindow
import com.moneydance.apps.md.view.gui.txnreg.TxnRegister
import com.moneydance.awt.GridC
import com.moneydance.awt.JDateField
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.Util
import java.awt.Dimension
import java.awt.GridBagLayout
import java.awt.event.ActionListener
import java.awt.event.WindowAdapter
import java.awt.event.WindowEvent
import javax.swing.Action
import javax.swing.JLabel
import javax.swing.JPanel
import javax.swing.border.EmptyBorder
import kotlin.math.abs
import kotlin.math.max

@Suppress("DuplicatedCode", "PrivatePropertyName")

class JumpToDate:ContextMenuAction {
  
  private val string_jump_to_date = "Jump to date in register"
  private val string_jump_enter_date = "Enter date to jump to"
  private val string_jump_date_label = "Date"
  
  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    val actions = mutableListOf<Action>()
    
    if (listTxns.size != 1) return actions
    
    val txn = listTxns.first()
    val acctType = txn.account.getAccountType()
    if (acctType == Account.AccountType.ROOT || acctType == Account.AccountType.SECURITY) return actions
    
    val jumpAction = addAction(label = string_jump_to_date, cmd = "jump_to_date")
    { jumpToDate(menuContext = menuContext, txn = txn) }
    actions.add(jumpAction)
    
    return actions
  }
  
  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }
  
  private fun jumpToDate(menuContext:MDActionContext, txn:AbstractTxn) {
    val txnRegister = (menuContext.component as? TxnRegister) ?: return
    
    val dateField = JDateField(mdGUI.preferences.shortDateFormatter).also {
      it.dateInt = txn.dateInt  // default to selected txn's date
    }
    
    val panel = JPanel(GridBagLayout()).also {
      it.border = EmptyBorder(16, 16, 16, 16)
      it.add(JLabel(string_jump_date_label.labelify), GridC.getc().xy(0, 0).label())
      it.add(dateField, GridC.getc().xy(1, 0).field())
    }
    
    val win = OKButtonWindow(mdGUI, menuContext.component, string_jump_enter_date, null, OKButtonPanel.QUESTION_OK_CANCEL)
    win.setEscapeKeyCancels(true)
    
    win.window.addWindowListener(object:WindowAdapter() {
      override fun windowOpened(e:WindowEvent) {
        win.pack()
        val preferredWidth = max(250, win.preferredSize.width)
        val preferredHeight = max(100, win.preferredSize.height)
        mdGUI.adjustWindow(win, Util.getComponentDialog(win), Dimension(preferredWidth, preferredHeight), null, null)
        dateField.requestFocusInWindow()
      }
    })
    
    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return
    val targetDate = dateField.dateInt
    if (targetDate <= 0) return
    
    val allTxns = txnRegister.primaryList.txns
    if (allTxns.isEmpty()) return
    
    val exactMatches = allTxns.filter { it.dateInt == targetDate }
    if (exactMatches.isNotEmpty()) {
      txnRegister.setSelectedTransactions(exactMatches.toTypedArray())
      txnRegister.ensureTxnIsVisible(exactMatches.first())
    } else {
      val nearest = allTxns.minByOrNull { abs(it.dateInt - targetDate) } ?: return
      txnRegister.setSelectedTransactions(arrayOf(nearest))
      txnRegister.ensureTxnIsVisible(nearest)
    }
  }
  
}