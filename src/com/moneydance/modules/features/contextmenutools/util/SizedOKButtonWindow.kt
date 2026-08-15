package com.moneydance.modules.features.contextmenutools.util

import com.moneydance.apps.md.view.gui.MoneydanceGUI
import com.moneydance.apps.md.view.gui.OKButtonWindow
import java.awt.Component
import java.awt.Dimension
import javax.swing.JComponent

/**
 * OKButtonWindow.setInputPanel() forces the window to a hardcoded 500x500 via adjustWindow()
 * (whose maxSize parameter is dead code, never used in its implementation). That call happens
 * inside showDialog(), before setVisible(true) - so overriding here and re-packing corrects the
 * size before the window is ever painted, eliminating the visible size "jump" otherwise seen
 * when a second pack+resize is done afterward in a windowOpened listener (the previous common
 * workaround, used in several places in this codebase before this class existed).
 *
 * Also supports remembering the window's last size/location across uses, via the same
 * SecondaryDialog.setRememberSizeLocationKeys() mechanism used elsewhere in Moneydance - pass
 * sizeKey/locationKey to enable it for a given dialog. Omit both to just get correct one-shot
 * sizing with no persisted position.
 *
 * Also enforces a minimum window size (the larger of the content's own preferred size, or a
 * fixed floor) so a user who has shrunk a remembered size in a previous session can't end up
 * with a dialog too small to show its own content.
 *
 * @param focusComponent Component to request focus on once the window is shown (e.g. a text
 * field or list that should be ready for keyboard input immediately). Optional.
 * @param sizeKey Preferences key for remembering window size. Optional - omit to not persist.
 * @param locationKey Preferences key for remembering window location. Optional - omit to not persist.
 */
class SizedOKButtonWindow(
  mdGUI:MoneydanceGUI,
  private val parentComponent:Component?,
  title:String,
  buttonSet:Int,
  private val focusComponent:JComponent? = null,
  sizeKey:String? = null,
  locationKey:String? = null
):OKButtonWindow(mdGUI, parentComponent, title, null, buttonSet) {
  
  companion object {
    private val MIN_DIALOG_SIZE = Dimension(380, 280)
  }
  
  init {
    this.name = com.moneydance.modules.features.contextmenutools.Main.EXTN_ID
    if (sizeKey != null || locationKey != null) {
      setRememberSizeLocationKeys(sizeKey, locationKey)
    }
  }
  
  override fun setInputPanel(component:JComponent) {
    super.setInputPanel(component)
    pack()
    
    // enforce a floor so a shrunk-and-remembered size (or any future resize) can never go below
    // what's actually usable, regardless of this particular dialog's own content size.
    minimumSize = Dimension(
      maxOf(preferredSize.width, MIN_DIALOG_SIZE.width),
      maxOf(preferredSize.height, MIN_DIALOG_SIZE.height)
    )
    
    // only center on the parent when there's no saved position to fall back to (i.e. we're still
    // at whatever undersized default the window started at) - setVisible() will apply a saved
    // size/location afterward via SecondaryDialog's own loadSizeAndLocation(), and centering here
    // unconditionally would fight with that on every subsequent open.
    if (size.width < preferredSize.width || size.height < preferredSize.height) {
      setLocationRelativeTo(parentComponent)
    }
  }
  
  override fun isNowVisible() {
    focusComponent?.requestFocusInWindow() ?: super.isNowVisible()
  }
}