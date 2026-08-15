package com.moneydance.modules.features.contextmenutools.util

import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.SecondaryDialog
import com.moneydance.awt.AwtUtil
import java.awt.BorderLayout
import java.awt.Component
import java.awt.Dimension
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import javax.swing.JButton
import javax.swing.JPanel
import javax.swing.JScrollPane
import javax.swing.JTextArea
import javax.swing.border.EmptyBorder

/**
 * Minimal read-only text viewer with a single "Copy to Clipboard" button - no OK/Cancel pair,
 * closing is just the window's own native close control or Escape (setEscapeKeyCancels), same
 * as any normal window. Modeled on StatusPopupDialog's plain-SecondaryDialog-subclass pattern,
 * but without the modal/severity-icon/kill/updateMessages machinery that class carries for its
 * own (different) purpose.
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
  }

  init {

    this.name = com.moneydance.modules.features.contextmenutools.Main.EXTN_ID

    setEscapeKeyCancels(true)

    val textArea = JTextArea(10, 70)   // bounded preferred size, matching MD's own showRawItemDetails reference -
                                        // JScrollPane handles anything beyond this via scrollbars, instead of
                                        // pack() sizing the window to fit the entire (potentially huge) raw dump
    textArea.text = if (text.endsWith("\n")) text else "$text\n"
    textArea.isEditable = false
    textArea.lineWrap = false
    textArea.wrapStyleWord = false
    textArea.border = EmptyBorder(10, 10, 10, 10)

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

    val buttonPanel = JPanel(BorderLayout())
    buttonPanel.border = EmptyBorder(0, 0, 8, 8)
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
    minimumSize = Dimension(
      maxOf(preferredSize.width, MIN_DIALOG_SIZE.width),
      maxOf(preferredSize.height, MIN_DIALOG_SIZE.height)
    )
    if (size.width < preferredSize.width || size.height < preferredSize.height) {
      setLocationRelativeTo(parent)
    }
  }

  override fun goneAway() {}
}