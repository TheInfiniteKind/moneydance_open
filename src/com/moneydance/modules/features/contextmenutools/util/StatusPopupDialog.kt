package com.moneydance.modules.features.contextmenutools.util

import com.moneydance.apps.md.view.gui.MDImages
import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.OKButtonListener
import com.moneydance.apps.md.view.gui.OKButtonPanel
import com.moneydance.apps.md.view.gui.SecondaryDialog
import com.moneydance.awt.AwtUtil
import com.moneydance.modules.features.contextmenutools.Main
import java.awt.BorderLayout
import java.awt.Component
import java.awt.event.WindowAdapter
import java.awt.event.WindowEvent
import javax.swing.JLabel
import javax.swing.JOptionPane
import javax.swing.JPanel
import javax.swing.JScrollPane
import javax.swing.JTextArea
import javax.swing.SwingUtilities
import javax.swing.UIManager
import javax.swing.border.EmptyBorder

enum class DialogResult { OK, CANCEL }

class StatusPopupDialog(mdGUI:MoneydanceGUI,
                        parent:Component?,
                        title:String,
                        status:String? = null,
                        message:String,
                        modal:Boolean,
                        showCancel:Boolean = false,
                        maxHeight:Int? = null,
                        messageType:Int = JOptionPane.PLAIN_MESSAGE,
                        dlgName:String? = null)
  :SecondaryDialog(mdGUI, AwtUtil.getFrame(parent), title, modal), OKButtonListener {

  private val isModal = modal
  private val statusLabel = JLabel()
  private val messageArea = JTextArea()
  private var result = DialogResult.CANCEL

  init {

    dlgName?.let { this.name = it } // set the internal name - normally module name...

    defaultCloseOperation = DO_NOTHING_ON_CLOSE
    setEscapeKeyCancels(true)
    
    try { setIconImage(MDImages.getImage(MDImages.DIALOG)) } catch (_:Exception) { }
    
    // status label
    status?.let {
      statusLabel.text = it
      statusLabel.border = EmptyBorder(0, 0, 8, 0)
    }

    // message area
    messageArea.text = if (message.endsWith("\n")) message else "$message\n"
    messageArea.isEditable = false
    messageArea.lineWrap = false
    messageArea.wrapStyleWord = false
    messageArea.isOpaque = false
    messageArea.border = null

    try {
      val monoFont = Main.mdGUI.fonts.code
      messageArea.font = monoFont
    } catch (_:Exception) {}

    val scrollPane = JScrollPane(messageArea, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

    val content = JPanel(BorderLayout(0, 8)).apply {
      border = EmptyBorder(12, 12, 12, 12)
      if (statusLabel.text.isNotEmpty()) add(statusLabel, BorderLayout.NORTH)
      add(scrollPane, BorderLayout.CENTER)
    }

    val severityIcon =
      when (messageType) {
        JOptionPane.ERROR_MESSAGE -> UIManager.getIcon("OptionPane.errorIcon")
        JOptionPane.INFORMATION_MESSAGE -> UIManager.getIcon("OptionPane.informationIcon")
        JOptionPane.WARNING_MESSAGE -> UIManager.getIcon("OptionPane.warningIcon")
        JOptionPane.QUESTION_MESSAGE -> UIManager.getIcon("OptionPane.questionIcon")
        else -> null
      }

    val mainPanel =
      if (severityIcon != null) {
        JPanel(BorderLayout()).apply {
          add(JLabel(severityIcon).apply {
            border = EmptyBorder(0, 0, 0, 12)
            verticalAlignment = JLabel.TOP
          }, BorderLayout.WEST)
          add(content, BorderLayout.CENTER)
        }
      } else {
        content
      }

    if (isModal || showCancel) {
      val buttonPanel = OKButtonPanel(mdGUI, this, if (showCancel) OKButtonPanel.QUESTION_OK_CANCEL else OKButtonPanel.QUESTION_OK)
      content.add(buttonPanel, BorderLayout.SOUTH)
    }

    contentPane.layout = BorderLayout()
    contentPane.add(mainPanel, BorderLayout.CENTER)

    addWindowListener(object:WindowAdapter() {
      override fun windowClosing(e:WindowEvent) {
        result = DialogResult.CANCEL
        goAway()
      }
    })

    pack()

    maxHeight?.let {
      if (height > it) setSize(width, it)
    }

    setLocationRelativeTo(parent)
  }

  override fun goneAway() {}
  
  override fun buttonPressed(answerCode:Int) {
    result =
      if (answerCode == OKButtonPanel.ANSWER_OK) DialogResult.OK
      else DialogResult.CANCEL
    goAway()
  }
  
  @Suppress("UNUSED")
  fun kill() {
    val r = Runnable {
      result = DialogResult.CANCEL
      goAway()
    }
    if (SwingUtilities.isEventDispatchThread()) {
      r.run()
    } else {
      SwingUtilities.invokeLater(r)
    }
  }

  @Suppress("UNUSED")
  fun updateMessages(newTitle:String? = null,
                     newStatus:String? = null,
                     newMessage:String? = null,
                     repack:Boolean = false) {
    
    if (isModal) return

    val r = Runnable {
      newTitle?.let { title = it }
      newStatus?.let { statusLabel.text = it }
      newMessage?.let {
        messageArea.text =
          if (it.endsWith("\n")) it else "$it\n"
      }
      if (repack) pack()
    }
    
    if (SwingUtilities.isEventDispatchThread()) { r.run() } else { SwingUtilities.invokeLater(r) }
  }

  fun showDialog():DialogResult {
    if (isModal) {
      if (SwingUtilities.isEventDispatchThread()) {
        isVisible = true
      } else {
        SwingUtilities.invokeAndWait { isVisible = true }
      }
    } else {
      SwingUtilities.invokeLater { isVisible = true }
    }
    return result
  }
}
