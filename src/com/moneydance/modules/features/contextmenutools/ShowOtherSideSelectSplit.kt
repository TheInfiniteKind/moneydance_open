package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.InvestFields
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.SplitTxn
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.SizedOKButtonWindow
import com.moneydance.modules.features.contextmenutools.util.Util
import java.awt.BorderLayout
import java.awt.Component
import java.awt.GridBagLayout
import java.awt.event.ActionListener
import java.awt.event.MouseAdapter
import java.awt.event.MouseEvent
import javax.swing.Action
import javax.swing.DefaultListModel
import javax.swing.JLabel
import javax.swing.JList
import javax.swing.JPanel
import javax.swing.JScrollPane
import javax.swing.ListCellRenderer
import javax.swing.ListSelectionModel
import javax.swing.border.EmptyBorder

private fun isSelectableAccountType(txn:AbstractTxn):Boolean {
  val type = txn.account.getAccountType()
  return type != Account.AccountType.SECURITY && type != Account.AccountType.ROOT
}

/**
 * Adds a context-menu action offering a picker of every "other side" of the selected
 * transaction to jump to - the parent (if a split is selected) plus every sibling split, each
 * labelled by position. This replaces Moneydance's own native "Show Other Side" auto-pick (which
 * silently jumps to the next split, or the parent if there are no more) with an explicit choice,
 * since a transaction with more than 2 splits has more than one plausible "other side."
 *
 * Only offered when the parent transaction has 2 or more splits, unless the option to include
 * single-split transactions is on.
 *
 * Candidate labelling: selecting the parent lists every split as 1, 2, 3... . Selecting a split
 * lists "Parent" plus every OTHER split, skipping the one currently selected but not renumbering
 * the rest.
 *
 * @author Stuart Beesley - August 2026
 */
@Suppress("PrivatePropertyName")
class ShowOtherSideSelectSplit(
  private val warnBeforeCategorySplit:Boolean = true,
  private val showFullAccountNames:Boolean = true,
  private val includeSingleSplitTxns:Boolean = false
):ContextMenuAction {

  private val string_show_other_side = "Show Other Side: Select Split"
  private val string_menu_with_count = "Show Other Side: Select Split ({num} Splits)"
  private val string_parent_label = "Parent"
  private val string_split_label = "Split"
  private val string_fee = "Fee"
  private val string_type_line = "Type: {value}"
  private val string_account_line = "Account: {value}"
  private val string_desc_line = "Transaction description: {value}"
  private val string_date_line = "Date: {value}"
  private val string_value_line = "Value: {value}"
  private val string_row_title = "{label}:  {title}"
  private val string_row_detail = "{acct} ({type}) — {amount}"
  private val string_acct_type_with_invest = "{type}, {invest}"
  private val string_category_warning = "This is a Category split ('{acct}'). Continue?"

  private val dialog_show_other_side_size = ".gui.show_other_side.size"
  private val dialog_show_other_side_locn = ".gui.show_other_side.loc"

  private data class SplitCandidate(val label:String, val txn:AbstractTxn, val displayTitle:String, val investType:String)

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (listTxns.size != 1) return emptyList()
    val selected = listTxns.first()
    val parent = selected.parentTxn
    if (parent.splitCount < 2 && !includeSingleSplitTxns) return emptyList()

    val action = addAction(label = string_menu_with_count.replace("{num}", parent.splitCount.toString()), cmd = "show_other_side_select_split")
    { showPicker(menuContext, selected, parent) }
    return listOf(action)
  }

  private fun addAction(label:String, cmd:String, listener:ActionListener):MDAction {
    return MDAction.make(label).command(cmd).callback(listener)
  }

  /**
   * Row title for an investment transaction's split, identifying WHICH PART of the transaction
   * this row actually is (security/fee/category/transfer), instead of repeating the parent's
   * description on every row. Not used for the parent row (see investmentSummaryTitle). Returns
   * null for a split matching none of the known roles - the caller falls back to the plain
   * description.
   */
  private fun investmentRoleTitle(txn:AbstractTxn, fields:InvestFields):String? {
    val acct = txn.account
    return when (acct) {
      fields.security -> fields.txnType.shortDescription
      fields.feeAcct -> string_fee
      fields.category -> fields.txnType.shortDescription
      fields.xfrAcct -> fields.txnType.shortDescription
      else -> null
    }
  }

  /** Overall transaction summary for the parent row itself. */
  private fun investmentSummaryTitle(fields:InvestFields):String {
    return fields.txnType.description
  }

  private fun buildCandidates(selected:AbstractTxn, parent:ParentTxn):List<SplitCandidate> {
    val fields = if (parent.account.getAccountType() == Account.AccountType.INVESTMENT) {
      try {
        InvestFields().also { it.setFieldStatus(parent) }
      } catch (e:Exception) {
        Util.logConsole("ShowOtherSideSelectSplit: failed to read InvestFields for '${parent.description}' (${parent.dateInt}): $e")
        null
      }
    } else null

    fun titleFor(txn:AbstractTxn, isParentRow:Boolean):String {
      if (fields == null) return txn.description
      return try {
        if (isParentRow) investmentSummaryTitle(fields) else (investmentRoleTitle(txn, fields) ?: txn.description)
      } catch (e:Exception) {
        Util.logConsole("ShowOtherSideSelectSplit: failed to build investment title for '${txn.description}': $e")
        txn.description
      }
    }

    // shown alongside the parent row's own account type (e.g. "INVESTMENT") - split rows never
    // get this, only the parent, since the transaction TYPE (Buy/Sell/Dividend/...) is a
    // property of the whole transaction, not any individual split's account.
    val parentInvestType = try {
      fields?.txnType?.shortDescription ?: ""
    } catch (e:Exception) {
      ""
    }

    val candidates = mutableListOf<SplitCandidate>()
    if (selected is SplitTxn) candidates.add(SplitCandidate(string_parent_label, parent, titleFor(parent, isParentRow = true), parentInvestType))
    for (i in 0 until parent.splitCount) {
      val split = parent.getSplit(i) ?: continue
      if (split === selected) continue
      candidates.add(SplitCandidate((i + 1).toString(), split, titleFor(split, isParentRow = false), ""))
    }
    return candidates
  }

  private fun showPicker(menuContext:MDActionContext, selected:AbstractTxn, parent:ParentTxn) {
    // re-validate at click time
    if (parent.splitCount < 2 && !includeSingleSplitTxns) return
    val candidates = buildCandidates(selected, parent)
    if (candidates.isEmpty()) return

    val listModel = DefaultListModel<SplitCandidate>()
    candidates.forEach { listModel.addElement(it) }

    val list = JList(listModel)
    list.cellRenderer = SplitCandidateRenderer(mdGUI, showFullAccountNames)
    list.selectionMode = ListSelectionModel.SINGLE_SELECTION

    val firstSelectableIndex = candidates.indexOfFirst { isSelectableAccountType(it.txn) }
    list.selectedIndex = firstSelectableIndex   // -1 (no selection) if every candidate is SECURITY/ROOT

    // JList has no native per-item disabling - revert any selection that lands on a
    // SECURITY/ROOT row back to the last valid one, so those rows are unselectable in practice,
    // not just visually dimmed.
    var lastValidIndex = firstSelectableIndex
    list.addListSelectionListener { e ->
      if (e.valueIsAdjusting) return@addListSelectionListener
      val idx = list.selectedIndex
      if (idx < 0) return@addListSelectionListener
      if (isSelectableAccountType(listModel.getElementAt(idx).txn)) {
        lastValidIndex = idx
      } else {
        list.selectedIndex = lastValidIndex
      }
    }

    val scrollPane = JScrollPane(list, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_NEVER)
    scrollPane.verticalScrollBar.unitIncrement = 16

    val dateFmt = mdGUI.preferences.shortDateFormatter
    val dec = mdGUI.preferences.decimalChar
    val acctNameStr = if (showFullAccountNames) selected.account.fullAccountName else selected.account.getAccountName()
    val valueStr = selected.account.currencyType.formatFancy(selected.value, dec)

    val headerPanel = JPanel(GridBagLayout())
    var hy = 0
    val selectedTypeStr = if (selected is SplitTxn) string_split_label else string_parent_label
    headerPanel.add(JLabel(string_type_line.replace("{value}", selectedTypeStr)), GridC.getc().xy(0, hy++).colspan(2).wx(1f).west())
    headerPanel.add(JLabel(string_account_line.replace("{value}", acctNameStr)), GridC.getc().xy(0, hy++).colspan(2).wx(1f).west())
    headerPanel.add(JLabel(string_desc_line.replace("{value}", selected.description)), GridC.getc().xy(0, hy++).colspan(2).wx(1f).west())
    headerPanel.add(JLabel(string_date_line.replace("{value}", dateFmt.format(selected.dateInt))), GridC.getc().xy(0, hy++).colspan(2).wx(1f).west())
    headerPanel.add(JLabel(string_value_line.replace("{value}", valueStr)), GridC.getc().xy(0, hy++).colspan(2).wx(1f).west())

    val panel = JPanel(BorderLayout(0, 8))
    panel.border = EmptyBorder(16, 16, 16, 16)
    panel.add(headerPanel, BorderLayout.NORTH)
    panel.add(scrollPane, BorderLayout.CENTER)

    val win = SizedOKButtonWindow(
      mdGUI, menuContext.component, string_show_other_side, OKButtonPanel.QUESTION_OK_CANCEL,
      focusComponent = list,
      sizeKey = Main.EXTN_ID + dialog_show_other_side_size,
      locationKey = Main.EXTN_ID + dialog_show_other_side_locn
    )
    win.setEscapeKeyCancels(true)

    list.addMouseListener(object:MouseAdapter() {
      override fun mouseClicked(e:MouseEvent) {
        if (e.clickCount == 2 && list.selectedIndex >= 0) {
          win.rootPane.defaultButton?.doClick()
        }
      }
    })

    val result = win.showDialog(panel)
    if (result != OKButtonPanel.ANSWER_OK) return

    val chosen = list.selectedValue ?: return

    if (warnBeforeCategorySplit && chosen.txn.account.getAccountType().isCategory) {
      val msg = string_category_warning.replace("{acct}", chosen.txn.account.fullAccountName)
      if (!mdGUI.askQuestion(msg)) return
    }

    mdGUI.showTxn(chosen.txn)
  }

  private inner class SplitCandidateRenderer(private val mdGUI:MoneydanceGUI, private val showFullAccountNames:Boolean):JPanel(GridBagLayout()), ListCellRenderer<SplitCandidate> {
    private val label = JLabel()
    private val subLabel = JLabel()
    private val colors = mdGUI.colors

    init {
      add(label, GridC.getc(0, 0).wx(1f).fillboth())
      add(subLabel, GridC.getc(0, 1).wx(1f).fillboth().leftInset(10))
      border = EmptyBorder(4, 6, 4, 4)
    }

    override fun getListCellRendererComponent(list:JList<out SplitCandidate>, value:SplitCandidate, index:Int, isSelected:Boolean, cellHasFocus:Boolean):Component {
      val selectable = isSelectableAccountType(value.txn)
      isOpaque = true
      background = if (isSelected && selectable) colors.sidebarSelectedBG else colors.listBackground

      val dec = mdGUI.preferences.decimalChar
      val txn = value.txn
      val amountStr = txn.account.currencyType.formatFancy(txn.value, dec)
      val acctType = txn.account.getAccountType().toString()
      val acctTypeStr = if (value.investType.isEmpty()) acctType
                        else string_acct_type_with_invest.replace("{type}", acctType).replace("{invest}", value.investType)

      label.text = string_row_title.replace("{label}", value.label).replace("{title}", value.displayTitle)
      label.foreground = when {
        !selectable -> colors.secondaryTextFG
        isSelected -> colors.sidebarSelectedFG
        else -> colors.defaultTextForeground
      }

      val acctNameStr = if (showFullAccountNames) txn.account.fullAccountName else txn.account.getAccountName()
      subLabel.text = string_row_detail.replace("{acct}", acctNameStr).replace("{type}", acctTypeStr).replace("{amount}", amountStr)
      subLabel.foreground = when {
        !selectable -> colors.secondaryTextFG
        isSelected -> colors.sidebarSelectedFG
        else -> colors.secondaryTextFG
      }
      subLabel.font = mdGUI.fonts.mini

      return this
    }
  }
}