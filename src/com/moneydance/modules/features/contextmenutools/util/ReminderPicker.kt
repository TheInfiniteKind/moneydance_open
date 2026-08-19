package com.moneydance.modules.features.contextmenutools.util

import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.Reminder
import com.infinitekind.util.DateUtil
import com.infinitekind.util.DateUtil.today
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.awt.GridC
import java.awt.BorderLayout
import java.awt.Component
import java.awt.GridBagLayout
import java.awt.event.MouseAdapter
import java.awt.event.MouseEvent
import javax.swing.DefaultListModel
import javax.swing.JLabel
import javax.swing.JList
import javax.swing.JPanel
import javax.swing.JScrollPane
import javax.swing.ListCellRenderer
import javax.swing.ListSelectionModel
import javax.swing.border.EmptyBorder
import kotlin.math.abs

/**
 * Renders a Reminder in a JList picker: description (with an EXPIRED suffix when applicable),
 * account total, and either a per-split percentage breakdown or a plain split count depending on
 * showSplitPercentages. Percentages assume all splits share the account's currency - set
 * showSplitPercentages = false for candidate lists that may include differing per-split
 * currencies, where a percent-of-total figure would be misleading.
 */
class ReminderPickerRenderer(
  private val mdGUI:MoneydanceGUI,
  private val showSplitPercentages:Boolean = true
):JPanel(GridBagLayout()), ListCellRenderer<Reminder> {
  private val label = JLabel()
  private val subLabel = JLabel()
  private val dateLabel = JLabel()
  private val colors = mdGUI.colors
  
  init {
    add(label, GridC.getc(0, 0).wx(1f).fillboth())
    add(subLabel, GridC.getc(0, 1).wx(1f).fillboth().leftInset(10))
    add(dateLabel, GridC.getc(0, 2).wx(1f).fillboth().leftInset(10))
    border = EmptyBorder(4, 6, 4, 4)
  }
  
  override fun getListCellRendererComponent(list:JList<out Reminder>, value:Reminder, index:Int, isSelected:Boolean, cellHasFocus:Boolean):Component {
    isOpaque = true
    background = if (isSelected) colors.sidebarSelectedBG else colors.listBackground
    
    val templateTxn = value.transaction
    val dec = mdGUI.preferences.decimalChar
    val totalStr = templateTxn.account.currencyType.formatFancy(templateTxn.value, dec)
    
    val expiredSuffix = if (value.isInactiveOrExpired()) " (EXPIRED)" else ""
    label.text = value.description + expiredSuffix
    label.foreground = if (isSelected) colors.sidebarSelectedFG else colors.defaultTextForeground
    
    val subLabelText =
      if (showSplitPercentages) {
        val total = templateTxn.value
        val percents = templateTxn.allSplits.map { split ->
          val pct = if (total != 0L) -split.value.toDouble() / total.toDouble() * 100.0 else 0.0
          String.format("%.0f%%", pct)
        }
        "$totalStr (splits: ${percents.joinToString(", ")})"
      } else {
        "$totalStr (${templateTxn.allSplits.size} splits)"
      }
    subLabel.text = subLabelText
    subLabel.foreground = if (isSelected) colors.sidebarSelectedFG else colors.secondaryTextFG
    subLabel.font = mdGUI.fonts.mini
    
    dateLabel.text = "Upcoming: ${upcomingDatesStr(mdGUI, value)}"
    dateLabel.foreground = if (isSelected) colors.sidebarSelectedFG else colors.secondaryTextFG
    dateLabel.font = mdGUI.fonts.mini
    
    return this
  }
}

/** 0 if the two values share a sign (or either is zero), else 1 - used so a same-sign candidate
 *  always outranks an opposite-sign one regardless of raw magnitude difference. */
private fun signPenalty(a:Long, b:Long):Int {
  if (a == 0L || b == 0L) return 0
  return if ((a < 0) == (b < 0)) 0 else 1
}

/**
 * How far candidate is from reference, in 10-point percentage bands (0 = within 10%, 1 = within
 * 20%, 2 = within 30%, etc.) rather than exact pennies. Exact-penny distance almost never ties
 * between two candidates, which would starve the split-count/category tiebreakers below of any
 * real ties to resolve - banding groups "close enough" candidates together so those tiebreakers
 * actually get used.
 */
private fun valueBand(candidateValue:Long, referenceValue:Long):Int {
  if (referenceValue == 0L) return if (candidateValue == 0L) 0 else Int.MAX_VALUE
  val percentOff = abs(candidateValue - referenceValue) * 100 / abs(referenceValue)
  return (percentOff / 10).toInt()
}

/**
 * 0 if referenceTxn's own ID matches Moneydance's auto-commit convention for this candidate
 * ("{reminderUUID}.{referenceTxn's date}" - see ReminderSet.autoCommitReminder), else 1. An
 * identity match always outranks every other relevance signal below, regardless of value/split
 * count/category - it's proof the transaction really was committed from this reminder, not a
 * heuristic guess.
 */
private fun uuidDatePenalty(referenceTxn:ParentTxn, candidate:Reminder):Int =
  if (referenceTxn.UUID == "${candidate.UUID}.${referenceTxn.dateInt}") 0 else 1

/** Count of distinct split-target accounts the two transactions have in common. */
private fun categoryOverlap(a:ParentTxn, b:ParentTxn):Int {
  val aAccounts = a.allSplits.map { it.account }.toSet()
  val bAccounts = b.allSplits.map { it.account }.toSet()
  return aAccounts.intersect(bAccounts).size
}

/** Next 3 scheduled dates (or fewer), formatted for display. Bound is 1 year + 1 day forward,
 *  same as Moneydance's own reminder detail panel. getNextOccurrencesCompat may return null on
 *  an older runtime (reflection unavailable) - falls back to the always-available singular
 *  getNextOccurance for a single date in that case. */
fun upcomingDatesStr(mdGUI:MoneydanceGUI, reminder:Reminder):String {
  val dateFmt = mdGUI.preferences.shortDateFormatter
  val searchBound = DateUtil.incrementDate(today, 1, 0, 1)
  val nextDates = reminder.getNextOccurrencesCompat(searchBound)?.take(3)
    ?: reminder.getNextOccurance(searchBound).let { if (it != 0) listOf(it) else emptyList() }
  return if (nextDates.isEmpty()) "None scheduled" else nextDates.joinToString(", ") { dateFmt.format(it) }
}

/**
 * Shows a modal reminder picker and returns the chosen Reminder, or null if cancelled.
 * See ReminderPickerRenderer's kdoc above for the showSplitPercentages rationale.
 *
 * @param referenceTxn When provided, candidates are sorted by relevance to this transaction:
 * UUID.date identity match first (see uuidDatePenalty), then value band (same-sign candidates
 * always before opposite-sign ones, then nearest 10%-wide value band), then nearest split count,
 * then most shared split-target accounts, then alphabetically by description as the final
 * tiebreak. When null (the default), candidates are sorted alphabetically only, with no
 * relevance ranking.
 */
fun pickReminder(
  mdGUI:MoneydanceGUI,
  parentComponent:Component?,
  title:String,
  candidates:List<Reminder>,
  sizeKey:String,
  locationKey:String,
  showSplitPercentages:Boolean = true,
  referenceTxn:ParentTxn? = null
):Reminder? {
  val listModel = DefaultListModel<Reminder>()
  val sorted =
    if (referenceTxn != null) {
      candidates.sortedWith(
        compareBy<Reminder> { uuidDatePenalty(referenceTxn, it) }
          .thenBy { signPenalty(it.transaction.value, referenceTxn.value) }
          .thenBy { valueBand(it.transaction.value, referenceTxn.value) }
          .thenBy { abs(it.transaction.allSplits.size - referenceTxn.allSplits.size) }
          .thenByDescending { categoryOverlap(it.transaction, referenceTxn) }
          .thenBy(String.CASE_INSENSITIVE_ORDER) { it.description }
      )
    } else {
      candidates.sortedWith(compareBy(String.CASE_INSENSITIVE_ORDER) { it.description })
    }
  sorted.forEach { listModel.addElement(it) }
  
  val list = JList(listModel)
  list.cellRenderer = ReminderPickerRenderer(mdGUI, showSplitPercentages)
  list.selectionMode = ListSelectionModel.SINGLE_SELECTION
  list.selectedIndex = 0
  
  val scrollPane = JScrollPane(list, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_NEVER)
  val panel = JPanel(BorderLayout())
  panel.border = EmptyBorder(16, 16, 16, 16)
  panel.add(scrollPane, BorderLayout.CENTER)
  
  val win = SizedOKButtonWindow(
    mdGUI, parentComponent, title, OKButtonPanel.QUESTION_OK_CANCEL, focusComponent = list,
    sizeKey = sizeKey,
    locationKey = locationKey
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
  if (result != OKButtonPanel.ANSWER_OK) return null
  
  return list.selectedValue
}