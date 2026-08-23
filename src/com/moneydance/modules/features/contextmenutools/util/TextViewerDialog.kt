package com.moneydance.modules.features.contextmenutools.util

import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.SecondaryDialog
import com.moneydance.awt.AwtUtil
import java.awt.BorderLayout
import java.awt.Component
import java.awt.Dimension
import java.awt.FlowLayout
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.awt.event.ActionEvent
import java.awt.event.KeyEvent
import javax.swing.AbstractAction
import javax.swing.JButton
import javax.swing.JComponent
import javax.swing.JLabel
import javax.swing.JOptionPane
import javax.swing.JPanel
import javax.swing.JScrollPane
import javax.swing.JTextArea
import javax.swing.JTextField
import javax.swing.KeyStroke
import javax.swing.border.EmptyBorder
import javax.swing.event.AncestorEvent
import javax.swing.event.AncestorListener
import javax.swing.text.DefaultHighlighter
import kotlin.math.max
import kotlin.math.min

/**
 * Minimal read-only text viewer with "Copy to Clipboard" and "Find" buttons - no OK/Cancel pair,
 * closing is just the window's own native close control or Escape (setEscapeKeyCancels), same
 * as any normal window. Modeled on StatusPopupDialog's plain-SecondaryDialog-subclass pattern,
 * but without the modal/severity-icon/kill/updateMessages machinery that class carries for its
 * own (different) purpose.
 *
 * Find (Ctrl/Cmd+F or the Find button) opens a small Next/Previous/Cancel prompt and highlights
 * matches in the text.
 *
 * @param sizeKey Preferences key for remembering window size. Optional - omit to not persist.
 * @param locationKey Preferences key for remembering window location. Optional - omit to not persist.
 */
class TextViewerDialog(
  mdGUI:MoneydanceGUI,
  parent:Component?,
  title:String,
  text:String,
  copyButtonLabel:String,
  sizeKey:String? = null,
  locationKey:String? = null
):SecondaryDialog(mdGUI, AwtUtil.getFrame(parent), title, false) {

  companion object {
    private val MIN_DIALOG_SIZE = Dimension(420, 320)
    private const val SEARCH_ICON_PATH = "com/moneydance/apps/md/view/gui/glyphs/glyph_search.png"
  }

  private val textArea = JTextArea(10, 70)   // bounded preferred size, matching MD's own showRawItemDetails reference -
                                              // JScrollPane handles anything beyond this via scrollbars, instead of
                                              // pack() sizing the window to fit the entire (potentially huge) raw dump

  init {

    this.name = com.moneydance.modules.features.contextmenutools.Main.EXTN_ID

    setEscapeKeyCancels(true)

    textArea.text = if (text.endsWith("\n")) text else "$text\n"
    textArea.isEditable = false
    textArea.lineWrap = false
    textArea.wrapStyleWord = false
    textArea.border = EmptyBorder(10, 10, 10, 10)
    textArea.caretPosition = 0   // ensure the view opens scrolled to the START, not wherever focus/setText left it

    try {
      textArea.font = mdGUI.fonts.code
    } catch (_:Exception) { }

    val scrollPane = JScrollPane(textArea, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

    val copyButton = JButton(copyButtonLabel)
    copyButton.addActionListener {
      try {
        Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(text), null)
      } catch (_:Exception) { }
    }

    val findAction = FindAction()
    val findIcon = Util.loadIcon(SEARCH_ICON_PATH)
    val findButton = if (findIcon != null) JButton(findIcon) else JButton("\uD83D\uDD0D")
    findButton.toolTipText = mdGUI.strings().find___
    findButton.addActionListener(findAction)

    getRootPane().actionMap.put("find-text", findAction)
    getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_F, MoneydanceGUI.ACCELERATOR_MASK), "find-text")

    val buttonPanel = JPanel(BorderLayout())
    buttonPanel.border = EmptyBorder(8, 8, 8, 8)
    buttonPanel.add(findButton, BorderLayout.WEST)
    buttonPanel.add(copyButton, BorderLayout.EAST)

    val content = JPanel(BorderLayout())
    content.add(scrollPane, BorderLayout.CENTER)
    content.add(buttonPanel, BorderLayout.SOUTH)

    contentPane.layout = BorderLayout()
    contentPane.add(content, BorderLayout.CENTER)

    if (sizeKey != null || locationKey != null) {
      setRememberSizeLocationKeys(sizeKey, locationKey)
    }

    isResizable = true
    pack()

    // default to a large, screen-relative size rather than whatever the small bounded
    // JTextArea(10,70) would otherwise produce - only affects the FIRST-EVER open; if a
    // sizeKey/locationKey remembered size exists from a previous session, SecondaryDialog's own
    // loadSizeAndLocation() applies afterward (when the caller sets isVisible = true) and takes
    // over from here, respecting whatever size the user last left it at.
    val screenSize = Toolkit.getDefaultToolkit().screenSize
    val defaultWidth = (screenSize.width * 0.8).toInt()
    val defaultHeight = (screenSize.height * 0.75).toInt()
    size = Dimension(maxOf(preferredSize.width, defaultWidth), maxOf(preferredSize.height, defaultHeight))

    minimumSize = Dimension(
      maxOf(preferredSize.width, MIN_DIALOG_SIZE.width),
      maxOf(preferredSize.height, MIN_DIALOG_SIZE.height)
    )
    setLocationRelativeTo(parent)

    // belt-and-braces: scroll back to top after the window is actually shown, in case anything
    // (focus grab, layout pass) scrolls it after this point
    javax.swing.SwingUtilities.invokeLater {
      scrollPane.viewport.viewPosition = java.awt.Point(0, 0)
    }
  }

  override fun goneAway() {}

  private inner class FindAction:AbstractAction() {

    var lastSearch = ""
    var lastPosn = -1
    var previousEndPosn = -1
    var lastDirection = 0

    override fun actionPerformed(e:ActionEvent?) {

      val strings = mdGUI.strings()

      val p = JPanel(FlowLayout())
      val lbl = JLabel(strings.find___)
      val tf = JTextField(lastSearch, 20)
      p.add(lbl)
      p.add(tf)

      tf.addAncestorListener(
        object:AncestorListener {
          override fun ancestorAdded(event:AncestorEvent?) {
            val comp:JTextField = event?.component as JTextField
            comp.requestFocusInWindow()
            comp.selectAll()
            comp.removeAncestorListener(this)
          }

          override fun ancestorRemoved(event:AncestorEvent?) {}
          override fun ancestorMoved(event:AncestorEvent?) {}
        }
      )

      val searchOptions = arrayOf(strings.next, strings.previous, strings.cancel)
      val defaultDirection = searchOptions[lastDirection]
      val response = JOptionPane.showOptionDialog(this@TextViewerDialog,
                                                  p,
                                                  strings.find___,
                                                  JOptionPane.OK_CANCEL_OPTION,
                                                  JOptionPane.QUESTION_MESSAGE,
                                                  null,
                                                  searchOptions,
                                                  defaultDirection)

      var searchWhat:String? = null

      var lSwitch = false
      if (response == 0 || response == 1) {
        if (response != lastDirection) lSwitch = true
        lastDirection = response
        searchWhat = tf.getText().trim()
      }

      if (searchWhat == null || searchWhat == "") return

      val theText = textArea.getText()
      val highlighter = textArea.highlighter
      highlighter.removeAllHighlights()

      var startPos = 0
      val pos:Int
      var endPos:Int
      val direction:String
      if (response == 0) {
        direction = "[${strings.next}]"
        if (searchWhat == lastSearch) {
          startPos = lastPosn
          if (lSwitch)
            startPos += searchWhat.length + 1
        }
        lastSearch = searchWhat

        pos = theText.indexOf(searchWhat, startPos, true)

      } else {
        direction = "[${strings.previous}]"
        endPos = theText.length - 1

        if (searchWhat == lastSearch) {
          if (previousEndPosn < 0) previousEndPosn = theText.length - 1
          endPos = max(0, previousEndPosn)
          if (lSwitch) endPos = max(0, lastPosn - 1)
        }
        lastSearch = searchWhat

        pos = theText.lastIndexOf(searchWhat, endPos, true)
      }

      if (pos >= 0) {
        textArea.setCaretPosition(pos)
        highlighter.addHighlight(pos, min(pos + searchWhat.length, theText.length), DefaultHighlighter.DefaultPainter)
        if (response == 0) {
          lastPosn = pos + searchWhat.length
          previousEndPosn = theText.length - 1
        } else {
          lastPosn = pos - searchWhat.length
          previousEndPosn = pos - 1
        }
      } else {
        lastPosn = 0
        previousEndPosn = theText.length - 1
        mdGUI.showInfoMessage(this@TextViewerDialog, "Searching ${direction} text not found")
      }
    }

  }
}