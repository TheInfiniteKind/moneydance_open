package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.moneydance.model.ParentTxn
import com.infinitekind.moneydance.model.Reminder
import com.infinitekind.moneydance.model.UndoableChange
import com.infinitekind.tiksync.SyncableItem
import com.infinitekind.util.DateUtil
import com.infinitekind.util.DateUtil.calculateDaysBetween
import com.infinitekind.util.labelify
import com.infinitekind.util.unellipsify
import com.moneydance.apps.md.controller.MDActionContext
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.apps.md.view.gui.ReminderTxnEditPanel
import com.moneydance.awt.AwtUtil
import com.moneydance.awt.GridC
import com.moneydance.modules.features.contextmenutools.Main.Companion.EXTN_ID
import com.moneydance.modules.features.contextmenutools.Main.Companion.mdGUI
import com.moneydance.modules.features.contextmenutools.util.RemUtility
import com.moneydance.modules.features.contextmenutools.util.SizedOKButtonWindow
import com.moneydance.modules.features.contextmenutools.util.isInactiveOrExpired
import com.moneydance.modules.features.contextmenutools.util.logBlockedIfDebug
import com.moneydance.modules.features.contextmenutools.util.setNameCompat
import java.awt.BorderLayout
import java.awt.Component
import java.awt.Dialog
import java.awt.Dimension
import java.awt.GridBagLayout
import java.awt.Insets
import java.awt.event.ActionEvent
import java.awt.event.KeyEvent
import java.awt.event.MouseAdapter
import java.awt.event.MouseEvent
import javax.swing.AbstractAction
import javax.swing.Action
import javax.swing.JButton
import javax.swing.JComboBox
import javax.swing.JComponent
import javax.swing.JLabel
import javax.swing.JOptionPane
import javax.swing.JPanel
import javax.swing.JScrollPane
import javax.swing.JTable
import javax.swing.KeyStroke
import javax.swing.ListSelectionModel
import javax.swing.SwingConstants
import javax.swing.SwingUtilities
import javax.swing.border.CompoundBorder
import javax.swing.border.EmptyBorder
import javax.swing.table.AbstractTableModel
import javax.swing.table.DefaultTableCellRenderer
import javax.swing.table.TableCellRenderer

/**
 * Sidebar Reminders right-click: lists one reminder's upcoming occurrences with their one-off instances,
 * and lets the user edit, delete or clear them. Offered only for exactly one reminder sent, a transaction
 * reminder on a bank or credit card account, not a loan reminder, not inactive or expired, on builds with
 * one-off instances.
 *
 * Rows are the upcoming occurrences plus any one-offs left behind (scheduled on or before the last recorded
 * date, which Moneydance still posts), ordered by one-off date, or scheduled date where there is none.
 * Edits are held in the window by scheduled date until Save, which checks every one-off's date against its
 * occurrence's window, writes only the changed dates and records one undo step on the reminder.
 * One-offs not shown in the table are never touched, except by Clear all.
 *
 * KNOWN ISSUES:
 * - "Waiting" can show when nothing will wait: when the earlier unrecorded occurrences fall within the
 *   reminder's auto-commit days, Moneydance posts them and the one-off in the same run.
 * - Moneydance's own reminder editor clears all one-offs whenever the reminder is saved there.
 *
 * @author Stuart Beesley - November 2026
 */
class EditReminderOneOffInstances:ContextMenuAction {

  private val string_menu = "Edit Reminder One-off Instances"

  override fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action> {
    if (!RemUtility.isDeferredRemindersBuild) return emptyList()
    if (menuContext.items.size != 1) {
      logBlockedIfDebug(string_menu, "Not exactly one reminder selected (${menuContext.items.size})")
      return emptyList()
    }
    val reminder = menuContext.items.first() as? Reminder ?: return emptyList()
    blockedReason(reminder)?.let {
      logBlockedIfDebug(string_menu, "'${reminder.description}': $it")
      return emptyList()
    }

    val action = MDAction.make(string_menu).command("edit_reminder_one_off_instances").callback { showOneOffInstances(menuContext, reminder) }
    return listOf(action)
  }

  private fun isEligible(reminder:Reminder):Boolean = blockedReason(reminder) == null

  private fun blockedReason(reminder:Reminder):String? = when {
    reminder.getReminderType() != Reminder.Type.TRANSACTION -> "Not a transaction reminder"
    reminder.isLoanReminder -> "Loan reminder"
    reminder.transaction.account.getAccountType() !in setOf(Account.AccountType.BANK, Account.AccountType.CREDIT_CARD) ->
      "Account type not eligible for account '${reminder.transaction.account.fullAccountName}' (${reminder.transaction.account.getAccountType()})"
    reminder.isInactiveOrExpired() -> "Reminder is expired or inactive"
    else -> null
  }

  private fun showOneOffInstances(menuContext:MDActionContext, reminder:Reminder) {
    // re-validate at click time
    if (!isEligible(reminder)) return
    val frame = AwtUtil.getFrame(menuContext.component) ?: mdGUI.firstMainFrame ?: return
    OneOffInstancesWindow(mdGUI, frame, reminder).showWindow()
  }
}

private class OneOffInstancesWindow(mdGUI:MoneydanceGUI, frame:java.awt.Frame, private val reminder:Reminder)
  :SizedOKButtonWindow(mdGUI, frame, string_title.replace("{desc}", reminder.description), OKButtonPanel.QUESTION_OK_CANCEL,
                       sizeKey = EXTN_ID + dialog_reminder_one_offs_size, locationKey = EXTN_ID + dialog_reminder_one_offs_locn) {

  private companion object {
    private val string_title = "Edit Reminder One-off Instances - {desc}"
    private val dialog_reminder_one_offs_size = ".gui.reminder_one_offs.size"
    private val dialog_reminder_one_offs_locn = ".gui.reminder_one_offs.loc"
  }

  private val string_occurrences = "Occurrences"
  private val string_to_date = "to {date}"
  private val string_no_date = "-"
  private val string_unsaved_marker = "* {date}"
  private val string_overdue = "Overdue"
  private val string_waiting = "Waiting"
  private val string_left_behind = "Left behind"
  private val string_more_occurrences = "... more occurrences exist"
  private val string_more_one_offs = "{num} more one-offs exist: {dates}"
  private val string_more_one_offs_etc = "{dates}, …"
  private val string_list_separator = ", "
  private val string_more_separator = "    "
  private val string_dates_outside = "These one-off dates are outside their occurrence's window:\n{dates}"
  private val string_days_later = "+{num}"
  private val string_date_failure = "{scheduled}: {date} - {limits}"
  private val string_col_scheduled = "Scheduled"
  private val string_col_one_off_date = "One-off date"
  private val string_col_days_moved = "Days moved"
  private val string_col_new_amount = "New amount"
  private val string_col_changed = "Changed"
  private val string_col_status = "Status"
  private val string_changed_account = "account"
  private val string_changed_splits = "splits"
  private val string_changed_currency = "currency"
  private val string_changed_description = "description"
  private val string_changed_memo = "memo"
  private val string_changed_tags = "tags"
  private val string_changed_check_number = "check number"
  private val string_fix = "Fix"
  private val string_save_anyway = "Save anyway"
  private val string_edit = "Edit"
  private val string_delete = "Delete"
  private val string_clear_all = "Clear all"
  private val string_discard_changes = "Unsaved changes will be discarded. Continue?"
  private val string_undo_name = "Edit Reminder one-off instances"
  private val string_reminder = "Reminder"
  private val string_account = "Account"
  private val string_base_amount = "Base amount"
  private val string_last_recorded = "Last recorded"
  private val string_end_date = "End date"
  private val string_frequency = "Frequency"
  private val string_on_days = "on {days}"
  private val string_last_day = "last day"
  private val string_suffix_st = "st"
  private val string_suffix_nd = "nd"
  private val string_suffix_rd = "rd"
  private val string_suffix_th = "th"
  private val string_txn_description = "Transaction description"
  private val string_category = "Category"
  private val string_auto_commit = "Auto-commit"
  private val string_auto_commit_no = "No"
  private val string_auto_commit_yes_days = "Yes, {num} days before"

  private val periodChoices = arrayOf(6, 12, 24, 36, 60)
  private val defaultPeriods = 12
  private val maxMoreDates = 6

  private val dateFmt = mdGUI.preferences.shortDateFormatter
  private val dec = mdGUI.preferences.decimalChar
  private val baseTxn = reminder.transaction
  private val baseCurrency = baseTxn.account.currencyType
  private val ackDate = reminder.dateAcknowledgedInt
  private val today = DateUtil.strippedDateInt
  private val waitingLimit = DateUtil.incrementDate(today, 0, 0, maxOf(reminder.autoCommitDays, 0))
  private val allOccurrences:List<Int> = reminder.getNextOccurrences(if (reminder.lastDateInt > 0) reminder.lastDateInt else 20991231)
  
  /** Fixed when the window opens, so a left-behind row stays after its one-off is deleted. */
  private val leftBehindDates:List<Int> = RemUtility.deferredDates(reminder).filter { it <= ackDate }

  /** Unsaved edits by scheduled date; a null value means the one-off is to be removed. */
  private val pending = mutableMapOf<Int, ParentTxn?>()
  private var clearAllPressed = false

  /** Scheduled dates, one per row; set by rebuild(). */
  private var rowDates:List<Int> = emptyList()

  private val periodsCombo = JComboBox(periodChoices).apply { selectedItem = defaultPeriods }
  private val toDateLabel = JLabel()
  private val moreLabel = JLabel()
  private val model = OneOffTableModel()
  private val table = JTable(model)
  private val content = JPanel(BorderLayout())

  private val colDaysMoved = 2
  private val colNewAmount = 3
  private val colEdit = 6
  private val colDelete = 7
  private val columnWidths = intArrayOf(90, 90, 70, 110, 240, 90, 70, 70)

  private val keyEditRow = "edit_one_off_row"
  private val keyDeleteRow = "delete_one_off_row"

  init {
    table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
    table.tableHeader.reorderingAllowed = false
    val buttonRenderer = ButtonCellRenderer()
    table.columnModel.getColumn(colEdit).cellRenderer = buttonRenderer
    table.columnModel.getColumn(colDelete).cellRenderer = buttonRenderer
    table.rowHeight = maxOf(table.rowHeight, buttonRenderer.preferredHeight)
    table.addMouseListener(object:MouseAdapter() {
      override fun mouseClicked(e:MouseEvent) {
        if (!SwingUtilities.isLeftMouseButton(e)) return
        val row = table.rowAtPoint(e.point)
        val col = table.columnAtPoint(e.point)
        if (row < 0) return
        when {
          col == colEdit -> if (e.clickCount == 1) editRow(row)
          col == colDelete -> if (e.clickCount == 1) deleteRow(row)
          e.clickCount == 2 -> editRow(row)
        }
      }
    })
    val tableKeys = table.getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT)
    tableKeys.put(KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, 0), keyEditRow)
    tableKeys.put(KeyStroke.getKeyStroke(KeyEvent.VK_DELETE, 0), keyDeleteRow)
    tableKeys.put(KeyStroke.getKeyStroke(KeyEvent.VK_BACK_SPACE, 0), keyDeleteRow)
    table.actionMap.put(keyEditRow, object:AbstractAction() {
      override fun actionPerformed(e:ActionEvent) { if (table.selectedRow >= 0) editRow(table.selectedRow) }
    })
    table.actionMap.put(keyDeleteRow, object:AbstractAction() {
      override fun actionPerformed(e:ActionEvent) { if (table.selectedRow >= 0) deleteRow(table.selectedRow) }
    })

    val rightColumns = listOf(colDaysMoved, colNewAmount)
    val lafHeaderRenderer = table.tableHeader.defaultRenderer
    // cell text starts and ends where the heading text does
    val headerInsets = (lafHeaderRenderer.getTableCellRendererComponent(table, "", false, false, -1, 0) as? JComponent)?.insets ?: Insets(0, 6, 0, 6)
    val leftAligned = PaddedCellRenderer(SwingConstants.LEADING, headerInsets)
    val rightAligned = PaddedCellRenderer(SwingConstants.RIGHT, headerInsets)
    (0 until table.columnCount).filter { it != colEdit && it != colDelete }.forEach {
      table.columnModel.getColumn(it).cellRenderer = if (it in rightColumns) rightAligned else leftAligned
    }
    // headings aligned as their cells; the look and feel's header renderer is shared by all columns, so set every time
    val lafHeaderAlignment = (lafHeaderRenderer as? JLabel)?.horizontalAlignment ?: SwingConstants.LEADING
    table.tableHeader.defaultRenderer = TableCellRenderer { t, value, isSelected, hasFocus, row, column ->
      lafHeaderRenderer.getTableCellRendererComponent(t, value, isSelected, hasFocus, row, column).also {
        (it as? JLabel)?.horizontalAlignment = if (t.convertColumnIndexToModel(column) in rightColumns) SwingConstants.RIGHT else lafHeaderAlignment
      }
    }
    // each column at least as wide as its heading
    val headerRenderer = table.tableHeader.defaultRenderer
    columnWidths.forEachIndexed { i, width ->
      val column = table.columnModel.getColumn(i)
      val headerWidth = headerRenderer.getTableCellRendererComponent(table, column.headerValue, false, false, -1, i).preferredSize.width + 12
      column.minWidth = headerWidth
      column.preferredWidth = maxOf(width, headerWidth)
    }
    val tableWidth = (0 until table.columnCount).sumOf { table.columnModel.getColumn(it).preferredWidth }

    periodsCombo.addActionListener { rebuild() }

    val header = JPanel(GridBagLayout())
    header.border = EmptyBorder(12, 16, 8, 16)
    var y = 0
    // label/value pairs across one row; a single pair's value spans the row
    fun addHeaderRow(vararg pairs:Pair<String, String>) {
      pairs.forEachIndexed { i, (label, value) ->
        header.add(JLabel(label.labelify), GridC.getc(i * 2, y).west().insets(1, if (i == 0) 0 else 24, 1, 8))
        val valueConstraints = GridC.getc(i * 2 + 1, y).west().insets(1, 0, 1, 0)
        header.add(JLabel(value), if (pairs.size == 1) valueConstraints.colspan(6) else valueConstraints)
      }
      y++
    }
    addHeaderRow(string_reminder to reminder.description)
    if (baseTxn.description != reminder.description) addHeaderRow(string_txn_description to baseTxn.description)
    addHeaderRow(string_account to baseTxn.account.fullAccountName)
    addHeaderRow(string_category to categoryDescription())
    addHeaderRow(string_base_amount to fmtAmount(baseTxn.value), string_last_recorded to fmtDate(ackDate), string_end_date to fmtDate(reminder.lastDateInt))
    addHeaderRow(string_frequency to frequencyDescription(reminder), string_auto_commit to autoCommitDescription(reminder))
    header.add(JPanel(), GridC.getc(6, y++).wx(1f))
    val periodsPanel = JPanel(GridBagLayout())
    periodsPanel.add(JLabel(string_occurrences.labelify), GridC.getc(0, 0).west().insets(0, 0, 0, 6))
    periodsPanel.add(periodsCombo, GridC.getc(1, 0).west().insets(0, 0, 0, 8))
    periodsPanel.add(toDateLabel, GridC.getc(2, 0).west())
    header.add(periodsPanel, GridC.getc(0, y++).colspan(7).west().insets(8, 0, 0, 0))

    val scrollPane = JScrollPane(table)
    scrollPane.verticalScrollBar.unitIncrement = 16
    scrollPane.preferredSize = Dimension(maxOf(950, tableWidth + 20), 260)

    moreLabel.border = EmptyBorder(6, 16, 0, 16)

    content.add(header, BorderLayout.NORTH)
    content.add(scrollPane, BorderLayout.CENTER)
    content.add(moreLabel, BorderLayout.SOUTH)

    buttonPanel.setOKAction(MDAction.make(buttonPanel.okButton.text).command("save_one_off_instances").callback { save() })
    buttonPanel.setExtraButtons(arrayOf(JButton(string_clear_all).apply { addActionListener { clearAll() } }))

    rebuild()
    if (table.rowCount > 0) table.setRowSelectionInterval(0, 0)
  }

  fun showWindow() {
    showDialog(content)
  }

  override fun isNowVisible() {
    table.requestFocusInWindow()
  }

  private fun fmtDate(date:Int):String = if (date > 0) dateFmt.format(date) else string_no_date
  private fun fmtAmount(value:Long, currency:CurrencyType = baseCurrency):String = currency.formatFancy(value, dec)

  /** autoCommitDays below 0 means auto-commit is off. */
  private fun autoCommitDescription(r:Reminder):String =
    if (r.autoCommitDays < 0) string_auto_commit_no else string_auto_commit_yes_days.replace("{num}", r.autoCommitDays.toString())

  /** As core's Reminder Details report frequency (ReminderDetailsReport buildFrequencyText), using core's
   *  strings where it has them. */
  private fun frequencyDescription(r:Reminder):String {
    val strings = mdGUI.strings
    val parts = mutableListOf<String>()
    fun withDetail(base:String, modifier:String, days:String) {
      val detail = listOfNotNull(modifier.ifBlank { null }, days.ifBlank { null }?.let { string_on_days.replace("{days}", it) })
        .joinToString(string_list_separator)
      parts += if (detail.isBlank()) base else "$base ($detail)"
    }
    if (r.repeatYearly) parts += strings.r_annually
    val monthlyDays = r.repeatMonthly?.filter { it > 0 }.orEmpty()
    if (monthlyDays.isNotEmpty()) {
      val modifier = when (r.repeatMonthlyModifier) {
        Reminder.MONTHLY_EVERY_OTHER -> strings.r_m_every_other
        Reminder.MONTHLY_EVERY_THIRD -> strings.r_m_every_third
        Reminder.MONTHLY_EVERY_FOURTH -> strings.r_m_every_fourth
        Reminder.MONTHLY_EVERY_SIXTH -> strings.r_m_every_sixth
        else -> ""
      }
      withDetail(strings.r_monthly, modifier, monthlyDays.joinToString(string_list_separator) { monthDayText(it) })
    }
    val weeklyDays = r.repeatWeeklyDays?.filter { it > 0 }.orEmpty()
    if (weeklyDays.isNotEmpty()) {
      val modifier = when (r.repeatWeeklyModifier) {
        Reminder.WEEKLY_EVERY_FIRST -> strings.r_w_first
        Reminder.WEEKLY_EVERY_SECOND -> strings.r_w_second
        Reminder.WEEKLY_EVERY_THIRD -> strings.r_w_third
        Reminder.WEEKLY_EVERY_FOURTH -> strings.r_w_fourth
        Reminder.WEEKLY_EVERY_FIFTH -> strings.r_w_fifth
        Reminder.WEEKLY_EVERY_LAST -> strings.r_w_last
        else -> ""
      }.unellipsify
      // repeatWeeklyDays holds Calendar.DAY_OF_WEEK values (1 = Sunday)
      val weekdays = java.text.DateFormatSymbols.getInstance().weekdays
      withDetail(strings.r_weekly, modifier, weeklyDays.joinToString(string_list_separator) { weekdays.getOrNull(it) ?: it.toString() })
    }
    if (r.repeatDaily > 0) parts += if (r.repeatDaily > 1) "${strings.r_daily} (${r.repeatDaily} ${strings.r_e_2})" else strings.r_daily
    return if (parts.isEmpty()) string_no_date else parts.joinToString(string_list_separator).lowercase()
  }

  private fun monthDayText(day:Int):String {
    if (day == Reminder.LAST_DAY_OF_MONTH) return string_last_day
    val suffix = if (day in 4..20 || day in 24..30) string_suffix_th
                 else listOf(string_suffix_st, string_suffix_nd, string_suffix_rd)[day % 10 - 1]
    return "$day$suffix"
  }

  /** The category, with its currency when it differs from the account's; "n splits" (core's text) when there are several. */
  private fun categoryDescription():String {
    val strings = mdGUI.strings
    if (baseTxn.splitCount > 1) return "${strings.split_label1}${baseTxn.splitCount}${strings.split_label2}"
    val category = (0 until baseTxn.splitCount).firstNotNullOfOrNull { baseTxn.getSplit(it)?.account } ?: return string_no_date
    val currency = category.currencyType
    return if (currency != baseCurrency) "${category.fullAccountName} (${currency.getIDString()})" else category.fullAccountName
  }

  private val periods:Int get() = periodsCombo.selectedItem as? Int ?: defaultPeriods
  private val periodDates:List<Int> get() = allOccurrences.take(periods)

  private fun storedOneOff(scheduled:Int):ParentTxn? = if (clearAllPressed) null else RemUtility.deferredTxn(reminder, scheduled)

  private fun effectiveOneOff(scheduled:Int):ParentTxn? = if (pending.containsKey(scheduled)) pending[scheduled] else storedOneOff(scheduled)

  private fun isChanged(scheduled:Int):Boolean =
    pending.containsKey(scheduled) || (clearAllPressed && RemUtility.deferredTxn(reminder, scheduled) != null)

  private val isDirty:Boolean get() = pending.isNotEmpty() || (clearAllPressed && RemUtility.deferredDates(reminder).isNotEmpty())

  private fun rebuild() {
    val selectedDate = rowDates.getOrNull(table.selectedRow)
    val shownPeriods = periodDates
    toDateLabel.text = if (shownPeriods.isEmpty()) "" else string_to_date.replace("{date}", fmtDate(shownPeriods.last()))
    rowDates = (shownPeriods + leftBehindDates).distinct()
      .sortedWith(compareBy({ effectiveOneOff(it)?.dateInt ?: it }, { it }))

    val effectiveOneOffDates = (RemUtility.deferredDates(reminder) + pending.keys).distinct()
      .filter { it > ackDate && it !in rowDates && effectiveOneOff(it) != null }.sorted()
    val moreText = mutableListOf<String>()
    if (allOccurrences.size > shownPeriods.size) moreText += string_more_occurrences
    if (effectiveOneOffDates.isNotEmpty()) {
      val shown = effectiveOneOffDates.take(maxMoreDates).joinToString(string_list_separator) { fmtDate(effectiveOneOff(it)?.dateInt ?: it) }
      val dates = if (effectiveOneOffDates.size > maxMoreDates) string_more_one_offs_etc.replace("{dates}", shown) else shown
      moreText += string_more_one_offs.replace("{num}", effectiveOneOffDates.size.toString()).replace("{dates}", dates)
    }
    moreLabel.text = moreText.joinToString(string_more_separator)

    model.fireTableDataChanged()
    val row = selectedDate?.let { rowDates.indexOf(it) } ?: -1
    if (row >= 0) table.setRowSelectionInterval(row, row)
  }

  /** The window a one-off's date must fall in: on or after the reminder's start date, after the previous
   *  occurrence (or the last recorded date) and before the next one (or on or before the end date). It must
   *  also stay after the previous row's date and before the next row's, one-offs included, so the one-offs
   *  post in schedule order. A left-behind one-off only has to keep that order, and be before the next
   *  upcoming occurrence. */
  private fun bounds(scheduled:Int):DateBounds? {
    val rows = leftBehindDates + allOccurrences
    val row = rows.indexOf(scheduled)
    if (row < 0) return null
    fun effectiveDate(date:Int) = effectiveOneOff(date)?.dateInt ?: date
    val index = allOccurrences.indexOf(scheduled)
    val previous = rows.getOrNull(row - 1)?.let { effectiveDate(it) } ?: 0
    val next = rows.getOrNull(row + 1)
    val occurrenceLower = if (index > 0) allOccurrences[index - 1] else if (index == 0) ackDate else 0
    val lowerExclusive = maxOf(previous, occurrenceLower)
    val upperExclusive = when {
      next == null -> 0
      next in allOccurrences -> minOf(next, effectiveDate(next))
      else -> effectiveDate(next)
    }
    val upperInclusive = if (index >= 0 && next == null) reminder.lastDateInt else 0
    return DateBounds(reminder.initialDateInt, lowerExclusive, upperExclusive, upperInclusive)
  }

  /** What Moneydance will do with the row; mirrors core's rule that a one-off due for posting (on or before
   *  today plus the reminder's auto-commit days) waits while an earlier normal occurrence is still to be
   *  recorded, using the window's unsaved edits. */
  private fun status(scheduled:Int):OccurrenceStatus {
    val oneOff = effectiveOneOff(scheduled)
    val date = oneOff?.dateInt ?: scheduled
    return when {
      scheduled <= ackDate -> if (oneOff != null) OccurrenceStatus.LEFT_BEHIND else OccurrenceStatus.RECORDED
      oneOff != null && date <= waitingLimit && allOccurrences.any { it < scheduled && effectiveOneOff(it) == null } -> OccurrenceStatus.WAITING
      date < today -> OccurrenceStatus.OVERDUE
      else -> OccurrenceStatus.UPCOMING
    }
  }

  private fun statusText(status:OccurrenceStatus):String = when (status) {
    OccurrenceStatus.OVERDUE -> string_overdue
    OccurrenceStatus.WAITING -> string_waiting
    OccurrenceStatus.LEFT_BEHIND -> string_left_behind
    OccurrenceStatus.UPCOMING, OccurrenceStatus.RECORDED -> ""
  }

  private fun clearAll() {
    clearAllPressed = true
    pending.clear()
    rebuild()
  }

  private fun deleteRow(row:Int) {
    val scheduled = rowDates.getOrNull(row) ?: return
    if (effectiveOneOff(scheduled) == null) return
    if (storedOneOff(scheduled) == null) pending.remove(scheduled) else pending[scheduled] = null
    rebuild()
  }

  private fun editRow(row:Int) {
    val scheduled = rowDates.getOrNull(row) ?: return

    val current = effectiveOneOff(scheduled)
    val source = current ?: reminder.transaction
    val txn = source.duplicateAsNew()
    if (current == null) txn.dateInt = scheduled
    txn.setParameter(SyncableItem.ITEM_KEY_ID, "${reminder.UUID}.$scheduled")
    txn.oldTxnID = -1

    val popup = OneOffEditWindow(mdGUI, this, scheduled, txn, bounds(scheduled))
    popup.showWindow()
    val edited = popup.result ?: return

    // OK on a row with a one-off is always a change; on a row without one, only a new date, amount or other change makes one
    if (current == null && edited.dateInt == scheduled && edited.value == baseTxn.value && changesFromBase(edited).isEmpty()) return
    pending[scheduled] = edited
    rebuild()
  }


  private fun save() {
    if (!isDirty) {
      goAwayNow()
      return
    }
    if (!confirmDates()) return
    val change = UndoableChange()
    change.beginModification(reminder)
    if (clearAllPressed) RemUtility.clearAllOneOffs(reminder)
    for ((scheduled, txn) in pending) RemUtility.setDeferredTxn(reminder, scheduled, txn)
    change.finishModification(reminder)
    change.setNameCompat(string_undo_name)
    mdGUI.undoManager?.recordChange(change)
    SwingUtilities.invokeLater { mdGUI.autocommitReminders() }
    goAwayNow()
  }

  /** Checks every one-off that will exist after Save, shown or not; true to go ahead with the save. */
  private fun confirmDates():Boolean {
    val storedDates = if (clearAllPressed) emptyList() else RemUtility.deferredDates(reminder)
    val failures = (storedDates + pending.keys).distinct().sorted().mapNotNull { scheduled ->
      val oneOff = effectiveOneOff(scheduled) ?: return@mapNotNull null
      val dateBounds = bounds(scheduled) ?: return@mapNotNull null
      if (dateBounds.allows(oneOff.dateInt)) null
      else string_date_failure.replace("{scheduled}", fmtDate(scheduled)).replace("{date}", fmtDate(oneOff.dateInt))
        .replace("{limits}", dateBounds.describe(::fmtDate))
    }
    if (failures.isEmpty()) return true
    val options = arrayOf(string_fix, string_save_anyway)
    val choice = JOptionPane.showOptionDialog(this, string_dates_outside.replace("{dates}", failures.joinToString("\n")), title,
                                              JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE, null, options, string_fix)
    return choice == 1
  }

  override fun goingAway():Boolean {
    if (!isDirty) return true
    return mdGUI.askQuestion(this, title, string_discard_changes)
  }

  private inner class OneOffTableModel:AbstractTableModel() {
    private val columns = listOf(string_col_scheduled, string_col_one_off_date, string_col_days_moved, string_col_new_amount,
                                 string_col_changed, string_col_status, "", "")

    override fun getRowCount():Int = rowDates.size
    override fun getColumnCount():Int = columns.size
    override fun getColumnName(column:Int):String = columns[column]
    override fun isCellEditable(rowIndex:Int, columnIndex:Int):Boolean = false

    override fun getValueAt(rowIndex:Int, columnIndex:Int):Any {
      val scheduled = rowDates[rowIndex]
      val oneOff = effectiveOneOff(scheduled)
      val oneOffCurrency = oneOff?.account?.currencyType ?: baseCurrency
      return when (columnIndex) {
        0 -> if (isChanged(scheduled)) string_unsaved_marker.replace("{date}", fmtDate(scheduled)) else fmtDate(scheduled)
        1 -> if (oneOff == null) "" else fmtDate(oneOff.dateInt)
        2 -> if (oneOff == null) "" else calculateDaysBetween(scheduled, oneOff.dateInt).let { if (it > 0) string_days_later.replace("{num}", it.toString()) else it.toString() }
        colNewAmount -> if (oneOff == null || (oneOff.value == baseTxn.value && oneOffCurrency == baseCurrency)) "" else fmtAmount(oneOff.value, oneOffCurrency)
        4 -> if (oneOff == null) "" else changesFromBase(oneOff).joinToString(string_list_separator)
        5 -> statusText(status(scheduled))
        colEdit -> string_edit
        colDelete -> string_delete
        else -> ""
      }
    }
  }

  /** What differs from the reminder's own transaction, other than the date and the total amount. */
  private fun changesFromBase(txn:ParentTxn):List<String> {
    fun splits(t:ParentTxn) = (0 until t.splitCount).mapNotNull { t.getSplit(it) }
    // split amounts and descriptions count only when there is more than one split: a single split's amount is the
    // new amount, and Moneydance's editor sets a single split's description to the payee
    val multiSplit = txn.splitCount > 1 || baseTxn.splitCount > 1
    fun splitKeys(t:ParentTxn) = splits(t).map { listOf(it.account.UUID, if (multiSplit) it.description else "", if (multiSplit) it.value.toString() else "") }
                                          .sortedBy { it.joinToString("\u0000") }
    fun currencies(t:ParentTxn) = (listOf(t.account) + splits(t).map { it.account }).map { it.currencyType }.toSet()
    fun tags(t:ParentTxn) = (listOf(t.keywords.sorted()) + splits(t).map { it.keywords.sorted() })
                              .filter { it.isNotEmpty() }.sortedBy { it.joinToString("\u0000") }
    val changes = mutableListOf<String>()
    if (txn.account != baseTxn.account) changes += string_changed_account
    if (splitKeys(txn) != splitKeys(baseTxn)) changes += string_changed_splits
    if (currencies(txn) != currencies(baseTxn)) changes += string_changed_currency
    if (txn.description != baseTxn.description) changes += string_changed_description
    if (txn.memo != baseTxn.memo) changes += string_changed_memo
    if (tags(txn) != tags(baseTxn)) changes += string_changed_tags
    if (txn.checkNumber != baseTxn.checkNumber) changes += string_changed_check_number
    return changes
  }

  /** Text cells with space either side, so adjacent columns don't run together. */
  private class PaddedCellRenderer(alignment:Int, private val textInsets:Insets):DefaultTableCellRenderer() {
    init { horizontalAlignment = alignment }
    override fun getTableCellRendererComponent(table:JTable, value:Any?, isSelected:Boolean, hasFocus:Boolean, row:Int, column:Int):Component {
      super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column)
      val base = border?.getBorderInsets(this) ?: Insets(0, 0, 0, 0)
      border = CompoundBorder(border, EmptyBorder(0, maxOf(0, textInsets.left - base.left), 0, maxOf(0, textInsets.right - base.right)))
      return this
    }
  }

  private inner class ButtonCellRenderer:TableCellRenderer {
    private val button = JButton()
    val preferredHeight:Int get() = JButton(string_delete).preferredSize.height
    override fun getTableCellRendererComponent(table:JTable, value:Any?, isSelected:Boolean, hasFocus:Boolean, row:Int, column:Int):Component {
      button.text = value?.toString() ?: ""
      button.isEnabled = column != colDelete || rowDates.getOrNull(row)?.let { effectiveOneOff(it) } != null
      return button
    }
  }
}

private enum class OccurrenceStatus { OVERDUE, UPCOMING, WAITING, LEFT_BEHIND, RECORDED }

/** An occurrence's date window; a zero limit means none. */
private class DateBounds(private val lowerInclusive:Int, private val lowerExclusive:Int, private val upperExclusive:Int,
                         private val upperInclusive:Int) {
  private val string_date_must_be = "The date must be {limits}."
  private val string_on_or_after = "on or after {date}"
  private val string_after = "after {date}"
  private val string_before = "before {date}"
  private val string_on_or_before = "on or before {date}"
  private val string_and = " and "

  fun allows(date:Int):Boolean =
    !(lowerInclusive > 0 && date < lowerInclusive) &&
    !(lowerExclusive > 0 && date <= lowerExclusive) &&
    !(upperExclusive > 0 && date >= upperExclusive) &&
    !(upperInclusive > 0 && date > upperInclusive)

  fun describe(fmtDate:(Int) -> String):String {
    val limits = mutableListOf<String>()
    if (lowerInclusive > lowerExclusive) limits += string_on_or_after.replace("{date}", fmtDate(lowerInclusive))
    else if (lowerExclusive > 0) limits += string_after.replace("{date}", fmtDate(lowerExclusive))
    if (upperExclusive > 0) limits += string_before.replace("{date}", fmtDate(upperExclusive))
    else if (upperInclusive > 0) limits += string_on_or_before.replace("{date}", fmtDate(upperInclusive))
    return string_date_must_be.replace("{limits}", limits.joinToString(string_and))
  }
}

/**
 * Edits one occurrence in Moneydance's own reminder transaction panel. Nothing is saved here: OK hands the
 * edited, never-synced transaction back to the one-off window. The date window is checked only when the date
 * was changed.
 */
private class OneOffEditWindow(mdGUI:MoneydanceGUI, owner:Dialog, private val scheduled:Int, txn:ParentTxn,
                               private val dateBounds:DateBounds?)
  :SizedOKButtonWindow(mdGUI, owner, string_title, OKButtonPanel.QUESTION_OK_CANCEL) {

  private companion object {
    private val string_title = "Edit Reminder One-off Instances - Edit One-off"
  }

  private val string_scheduled = "Scheduled date: {date}"

  private val dateFmt = mdGUI.preferences.shortDateFormatter
  private val txnPanel = ReminderTxnEditPanel(mdGUI, txn.book, true)

  /** The transaction as loaded, to tell whether the date was changed. */
  private val before:ParentTxn
  var result:ParentTxn? = null
    private set

  private val mainPanel = JPanel(GridBagLayout())

  init {
    txnPanel.populateFields(txn, txn.dateInt)
    before = txn.duplicate()

    mainPanel.add(JLabel(string_scheduled.replace("{date}", dateFmt.format(scheduled))), GridC.getc(0, 0).west().insets(10, 12, 0, 12))
    mainPanel.add(txnPanel, GridC.getc(0, 1).wx(1f).wy(1f).fillboth())

    val okAction = MDAction.make(buttonPanel.okButton.text).command("ok_one_off_edit").callback { ok() }
    buttonPanel.setOKAction(okAction)

    txnPanel.setRecordAction(okAction)
    rootPane.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW)
      .put(KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, MoneydanceGUI.ACCELERATOR_MASK_EX), okAction.command)
    rootPane.actionMap.put(okAction.command, okAction)

    setEscapeKeyCancels(true)
  }

  fun showWindow() {
    showDialog(mainPanel)
  }

  private fun ok() {
    val saved = txnPanel.saveTransactionWithModifier(null, null) ?: return
    val edited = saved.parentTxn
    val date = edited.dateInt
    if (dateBounds != null && date != before.dateInt && !dateBounds.allows(date)) {
      mdGUI.showErrorMessage(this, dateBounds.describe { dateFmt.format(it) })
      return
    }
    result = edited
    goAwayNow()
  }

  override fun goneAway() {
    txnPanel.goneAway()
  }
}
