package com.moneydance.modules.features.mousetester

import com.infinitekind.moneydance.model.*
import com.infinitekind.util.StringUtils.isEmpty
import com.moneydance.apps.md.view.HomePageView
import com.moneydance.apps.md.view.gui.MDAction
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.MoneydanceLAF
import com.moneydance.awt.AwtUtil.isPopupTrigger
import com.moneydance.awt.CollapsibleRefresher
import com.moneydance.awt.GridC
import java.awt.Dimension
import java.awt.GridBagLayout
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.awt.event.ActionEvent
import java.awt.event.ActionListener
import java.awt.event.MouseEvent
import java.awt.event.MouseListener
import java.io.PrintWriter
import java.io.Writer
import javax.swing.*
import kotlin.math.min

class MouseTesterView : HomePageView {
  private var mdGUI: MoneydanceGUI? = null
  private var view: ViewPanel? = null
  private var active = false
  private var mouseConsoleOutputArea: JTextArea? = null
  private var consoleWriter: PrintWriter? = null
  private var iconBlue: Icon? = null
  private var iconRed: Icon? = null
  private var iconNormal: Icon? = null
  
  private fun initializeObjects() {
    if (Main.mdMain?.currentAccountBook != null && mdGUI != null) {
      Util.logConsole(true, "${Main.EXTN_ID}: initializeObjects - already initialized... ignoring...")
      return
    }
    
    if (Main.mdMain?.currentAccountBook == null && mdGUI == null) {
      Util.logConsole("${Main.EXTN_ID}: initializeObjects - dataset & gui are not available yet... ignoring...")
      return
    }
    
    // Use this to initialize stuff (only when dataset is open - assume the gui is open too)
    if (Main.mdMain?.currentAccountBook != null && mdGUI == null) {
      Util.logConsole("${Main.EXTN_ID}: initializeObjects - dataset available - grabbing the GUI & initializing objects....")
      mdGUI = Main.mdGUI
      
      val ICON_PATH = "/com/moneydance/apps/md/view/gui/glyphs/moneybot.png"
      
      iconBlue = mdGUI?.images?.getIconWithColor(ICON_PATH, Util.blue)
      iconRed = mdGUI?.images?.getIconWithColor(ICON_PATH, Util.red)
      iconNormal = mdGUI?.images?.getIconWithColor(ICON_PATH, Util.defaultFGColor)
      
      mouseConsoleOutputArea = JTextArea()
      mouseConsoleOutputArea!!.isEditable = false
      mouseConsoleOutputArea!!.font = mdGUI!!.fonts.mono
      
      consoleWriter = PrintWriter(ConsoleWriter(mouseConsoleOutputArea))
      consoleWriter!!.println(Main.EXTN_NAME + " (results)...:")
      Util.logConsole("${Main.EXTN_ID}: initializeObjects - finished initializing objects....")
      return
    }
    
    Util.logConsole("${Main.EXTN_ID}: initializeObjects - LOGIC ERROR - book: ${Main.mdMain?.currentAccountBook} GUI: $mdGUI")
  }
  
  /** Returns a unique identifier for this view.  This identifier must be unique across all identifiers for all extensions.  */
  override fun getID(): String {
    return ID
  }
  
  /** Returns a short descriptive name of this view.  */
  override fun toString(): String {
    return Main.EXTN_NAME
  }
  
  /** Returns a GUI component that provides a view of the info panel for the given data file.  */
  override fun getGUIView(book: AccountBook): JComponent {
    Util.logConsole("${Main.EXTN_ID}: getGUIView - book: '${book}' isEDT: ${SwingUtilities.isEventDispatchThread()}")
    var viewCopy = view
    if (viewCopy != null) return viewCopy
    synchronized(this) {
      initializeObjects()
      viewCopy = ViewPanel(book)
      this.view = viewCopy
      return viewCopy as ViewPanel
    }
  }
  
  /**
   * Sets the view as active or inactive.  When not active, a view
   * should not have any registered listeners with other parts of
   * the program.  This will be called when a view is added to the
   * home page, or the home page is refreshed after not being visible
   * for a while.
   */
  override fun setActive(active: Boolean) {
    Util.logConsole("${Main.EXTN_ID}: setActive - active: $active")
    this.active = active
    if (view != null) {
      if (active) {
        view!!.activate()
      } else {
        view!!.deactivate()
      }
    }
  }
  
  override fun refresh() {
    Util.logConsole("${Main.EXTN_ID}: refresh")
    if (view != null) {
      view!!.refresh()
    }
  }
  
  /** Called when the view should clean up everything.  For example, this is called when a file is closed and the GUI is reset  */
  @Synchronized
  override fun reset() {
    Util.logConsole("${Main.EXTN_ID}: reset")
    setActive(false)
    view = null
  }
  
  private class ConsoleWriter(private var textArea: JTextArea?) : Writer(), Runnable {
    private val sb = StringBuilder()
    
    override fun write(cbuf: CharArray, off: Int, len: Int) {
      if (textArea == null) return
      synchronized(sb) {
        sb.appendRange(cbuf, off, off + len)
      }
      SwingUtilities.invokeLater(this)
    }
    
    override fun flush() {
      SwingUtilities.invokeLater(this)
    }
    
    override fun close() {
      textArea = null
    }
    
    override fun run() {
      synchronized(sb) {
        if (isEmpty(sb.toString())) return
        textArea!!.append(sb.toString())
        textArea!!.caretPosition = textArea!!.document.length
        sb.setLength(0)
      }
    }
  }
  
  private inner class ViewPanel(book: AccountBook) : JPanel(GridBagLayout()),
    MouseListener, ActionListener, AccountListener, CurrencyListener {
    private var clickFlip = false
    private val book: AccountBook
    private val mouseTesterRow: JLabel
    
    fun activate() {
      book.addAccountListener(this)
      book.currencies.addCurrencyListener(this)
      refresh()
    }
    
    fun deactivate() {
      book.removeAccountListener(this)
      book.currencies.removeCurrencyListener(this)
    }
    
    private val refresher = CollapsibleRefresher { this.reallyRefresh() }
    
    init {
      Util.logConsole("${Main.EXTN_ID}: ViewPanel()")
      this.book = book
      
      border = MoneydanceLAF.homePageBorder
      isOpaque = false
      mouseTesterRow = JLabel("<<MouseTester: CLICK TEST>>")
      mouseTesterRow.icon = iconNormal
      mouseTesterRow.addMouseListener(this)
      
      add(mouseTesterRow, GridC.getc(0, 0).wx(1f).fillboth().insets(0, 14, 6, 14))
      
      val btn = JButton(
        MDAction.makeNonKeyedAction(
          mdGUI, mdGUI!!.strings().copy_to_clipboard, "copy_clipboard",
          this
        )
      )
      add(btn, GridC.getc(1, 0).wx(1f).fillboth().insets(0, 14, 6, 14))
      
      val scrollPane: JScrollPane = object : JScrollPane(mouseConsoleOutputArea) {
        override fun getPreferredSize(): Dimension {
          val psz = super.getPreferredSize()
          psz.width = min(200.0, psz.width.toDouble()).toInt()
          psz.height = 200
          return psz
        }
      }
      add(scrollPane, GridC.getc(0, 1).colspan(2).fillboth().insets(0, 14, 6, 14))
      add(Box.createVerticalStrut(100), GridC.getc(0, 1))
      if (active) {
        activate()
      }
    }
    
    fun refresh() {
      if (mdGUI!!.suspendRefreshes) return
      refresher.enqueueRefresh()
    }
    
    fun reallyRefresh() {
      if (mdGUI!!.suspendRefreshes) return
      
      // Perform intensive data processing here and update the widget...
      repaint()
    }
    
    override fun accountModified(account: Account?) {
      //refresh();
    }
    
    override fun currencyTableModified(table: CurrencyTable?) {
      //refresh();
    }
    
    override fun accountBalanceChanged(account: Account?) {
      //refresh();
    }
    
    
    override fun accountDeleted(parentAccount: Account?, deletedAccount: Account?) {
      //refresh();
    }
    
    override fun accountAdded(parentAccount: Account?, newAccount: Account?) {
      //refresh();
    }
    
    fun logMouseEvent(mouseEvent: MouseEvent) {
      val javaPopupTrig = mouseEvent.isPopupTrigger
      val moneydancePopupTrig = isPopupTrigger(mouseEvent)
      consoleWriter!!.println(
        (mouseEvent.paramString()
         + " isPopupTrigger(java): " + javaPopupTrig
         + " isPopupTrigger(MD): " + moneydancePopupTrig)
      )
      if (javaPopupTrig || moneydancePopupTrig) {
        consoleWriter!!.println("... isPopup(java): $javaPopupTrig isPopup(MD): $moneydancePopupTrig")
      }
      repaint()
    }
    
    override fun mouseClicked(e: MouseEvent) {
      clickFlip = !clickFlip
      mouseTesterRow.foreground =
        if (clickFlip) Util.red else Util.blue
      logMouseEvent(e)
    }
    
    override fun mousePressed(e: MouseEvent) {
      mouseTesterRow.icon = iconRed
      logMouseEvent(e)
    }
    
    override fun mouseReleased(e: MouseEvent) {
      mouseTesterRow.icon = iconBlue
      logMouseEvent(e)
    }
    
    override fun mouseEntered(e: MouseEvent) {
      mouseTesterRow.border =
        BorderFactory.createLineBorder(Util.red)
      logMouseEvent(e)
    }
    
    override fun mouseExited(e: MouseEvent) {
      mouseTesterRow.border = null
      logMouseEvent(e)
    }
    
    override fun actionPerformed(evt: ActionEvent) {
      if (evt.actionCommand.equals("copy_clipboard", ignoreCase = true)) {
        try {
          Toolkit.getDefaultToolkit().systemClipboard.setContents(
            StringSelection(
              mouseConsoleOutputArea!!.text
            ), null
          )
          consoleWriter!!.println("[results copied to clipboard]")
        } catch (error: Exception) {
          Util.logConsole(Main.EXTN_ID + " - Error copy contents of JTextArea to clipboard! " + error)
          consoleWriter!!.println("[ERROR copying to clipboard!$error]")
          mdGUI!!.showErrorMessage(Main.EXTN_NAME + " - ERROR copying to clipboard!?", error)
        }
      }
    }
  }
  
  companion object {
    const val ID: String = Main.EXTN_ID
  }
}









